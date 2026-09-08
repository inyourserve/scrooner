// Direct Postgres access for the Next.js server application. Company pages
// serving views" directly -- no apps/backend dependency for this page,
// since a company page is a static/ISR read, not a dynamic query the
// Python Screener needs to evaluate. Values that are Decimal in Postgres
// come back as strings here (the `postgres` client's default, matching
// this project's Decimal-as-string discipline at every boundary -- see
// doc 04's correctness controls) -- never parsed to a JS float.

import postgres from "postgres";

// Company pages use one consolidated request, so each server instance needs a
// very small pool. `prepare: false` keeps this client compatible with
// Supabase's transaction pooler when the Vercel DATABASE_URL is moved to port
// 6543; it is also safe with the current session-pooler URL.
const sql = postgres(process.env.DATABASE_URL ?? "postgres://invalid:invalid@127.0.0.1:5432/scrooner", {
  max: 2,
  idle_timeout: 20,
  connect_timeout: 10,
  prepare: false,
});

// History-depth decision (2026-08-29), mirrored from pipeline/screener/
// resolve.py's own MIN_PERIOD_END: display/resolution boundary only, never
// deletes anything from core/analytics. XBRL tagging predating ~2011 is
// sparse/unreliable (27% of all core.period FY rows are pre-2015, mostly
// pre-mandatory-XBRL era, live-checked before choosing this floor), and it
// also guards the "most recent value" queries below against ever
// resolving a stale or malformed period (one real bad row found live: a
// FY period end-dated 2104-12-31) as if it were current.
const HISTORY_FLOOR = "2015-01-01";

// Upper-bound companion to HISTORY_FLOOR, added 2026-08-29 the same day
// after finding the floor alone doesn't catch a FUTURE-dated malformed
// period -- a real one exists (a SPAR Group, Inc. fact end-dated
// 2104-12-31, a genuine filer XBRL context typo in their own 2016 10-K,
// not a Scrooner bug) and 134 core.period rows total are dated more than
// a year past today (worst: 6016-06-30). Any "most recent" query sorted
// by period_end desc would let a future-dated row incorrectly win over
// real current data. +30 days (not exactly today) tolerates ordinary
// clock/timezone skew between this server and whatever wrote the row.
// Written directly as `current_date + interval '30 days'` in each query
// below (a fixed, non-parameterized SQL expression, not user input) --
// the `postgres` tagged-template client would otherwise bind a JS string
// constant as a literal VALUE, not evaluate it as SQL.

// Non-equity listing types (ETNs/ETPs, warrants, units, rights, funds,
// royalty trusts) share a real operating company's CIK/company_id as the
// SEC-registered issuer/guarantor, but are not equity in that company --
// e.g. Bank of Montreal is the real issuer behind ~30 unrelated leveraged/
// inverse ETN tickers (FNGU, GDXD, BNKU, ...), all correctly classified
// `security_type = 'ETP'` by OpenFIGI. Found live 2026-09-06, direct user
// report ("we are powering ETNs?"): ticker resolution had no security_type
// filter at all, so /stocks/fngu rendered Bank of Montreal's full equity
// company page under an ETN ticker, and typing "fngu" into search
// surfaced it as if it were a stock. Requires an alias named `l` on
// core.listing in the query it's spliced into. Mirrors pipeline's own
// PRIMARY_SECURITY_TYPES (company_master/security_type.py) -- same
// allowed set, kept in sync by hand since Python and TS can't share a
// constant directly. NULL (not yet OpenFIGI-classified) is allowed, not
// excluded -- excluding it would drop most of the population (only
// ~18% is classified so far), and an unclassified real equity company
// has never been observed resolving to a wrong page, unlike an explicit
// non-equity type.
const EQUITY_ONLY_SQL = sql`(l.security_type is null or l.security_type in ('Common Stock', 'ADR', 'REIT', 'MLP', 'Tracking Stk', 'Ltd Part'))`;

export interface CompanyIdentity {
  id: number;
  cik: string;
  company_name: string;
  sic_code: string | null;
  sic_description: string | null;
  // doc 10 Sec 12/doc 26 Sec 2.8/doc 28 (2026-08-21) -- a curated,
  // investor-friendly bucket derived from sic_code (company_master/
  // sector_bucket.py), coarser but more readable than the raw SIC
  // description. Not GICS (licensed taxonomy, already ruled out).
  sector: string | null;
  status: string;
  ticker: string | null;
  // doc 39 (2026-08-30) -- about_text is regex-extracted from the latest
  // 10-K's Item 1 Business section (single fetch, no history, per doc
  // 38's case-1 reasoning); the contact fields are from company_master/
  // contact_details.py's zero-new-fetch submissions.json parse, now at
  // 100% active-company coverage. Both null for a company not yet
  // covered by either pass -- honest null, not an error.
  about_text: string | null;
  ein: string | null;
  business_address_line1: string | null;
  business_address_city: string | null;
  business_address_state: string | null;
  business_address_zip: string | null;
  business_phone: string | null;
  website: string | null;
}

export async function getCompanyByTicker(ticker: string): Promise<CompanyIdentity | null> {
  const rows = await sql<CompanyIdentity[]>`
    select c.id, c.cik, c.company_name, c.sic_code, c.sic_description, c.sector, c.status, l.ticker
    from core.company c
    join core.listing l on l.company_id = c.id
    where lower(l.ticker) = lower(${ticker}) and ${EQUITY_ONLY_SQL}
    order by (l.effective_to is null) desc
    limit 1
  `;
  return rows[0] ?? null;
}

export interface MetricRow {
  metric_name: string;
  value: string | null;
  period_label: string;
  period_end: string;
  is_null_reason: string | null;
}

// One row per metric: the most-recent value, same TTM-preferred/latest-
// period_end rule as screener/resolve.py (doc 14 Sec 1) -- kept here as a
// direct SQL port rather than a cross-language import, since the frontend can't
// call the Python resolver. Same rule, independently expressed.
export async function getLatestMetrics(companyId: number): Promise<Record<string, MetricRow>> {
  const rows = await sql<MetricRow[]>`
    with ranked as (
      select md.metric_name, mv.value, mv.period_label, mv.period_end, mv.is_null_reason,
             row_number() over (
               partition by md.metric_name
               order by (mv.period_label = 'TTM') desc, mv.period_end desc
             ) as rn
      from analytics.metric_value mv
      join analytics.metric_definition md on md.id = mv.metric_definition_id
      where mv.company_id = ${companyId} and mv.period_end >= ${HISTORY_FLOOR} and mv.period_end <= current_date + interval '30 days'
    )
    select metric_name, value, period_label, period_end::text, is_null_reason
    from ranked where rn = 1
  `;
  return Object.fromEntries(rows.map((r) => [r.metric_name, r]));
}

export interface PublicFloatRow {
  value: string;
  period_end: string;
}

// doc 23 Stage B / doc 24 Phase 1 -- dei:EntityPublicFloat, NOT Market
// Cap. Annual (10-K cover-page snapshot as of the filer's 2nd fiscal
// quarter), excludes affiliate/insider-held shares. Queried directly
// from analytics.canonical_fact (not metric_value -- this isn't one of
// doc 02's 18 locked metrics), most recent period only, and rendered
// with an explicit label distinguishing it from the still price-vendor-
// blocked Market Cap field -- see that stage's own design note on never
// letting the two be confused.
export async function getLatestPublicFloat(companyId: number): Promise<PublicFloatRow | null> {
  const rows = await sql<PublicFloatRow[]>`
    select cf.value::text, p.end_date::text as period_end
    from analytics.canonical_fact cf
    join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
    join core.period p on p.id = cf.period_id
    where cf.company_id = ${companyId} and cc.name = 'public_float' and p.end_date >= ${HISTORY_FLOOR} and p.end_date <= current_date + interval '30 days'
    order by p.end_date desc
    limit 1
  `;
  return rows[0] ?? null;
}

// Generic latest-value-of-a-canonical-concept reader, most recent period
// only -- same query shape as getLatestPublicFloat, factored out so
// Book Value (stockholders_equity) doesn't need its own near-duplicate
// function. Not for price-dependent metrics (those are in
// analytics.metric_value via getLatestMetrics, not here).
export async function getLatestConceptValue(companyId: number, conceptName: string): Promise<string | null> {
  const rows = await sql<{ value: string }[]>`
    select cf.value::text
    from analytics.canonical_fact cf
    join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
    join core.period p on p.id = cf.period_id
    where cf.company_id = ${companyId} and cc.name = ${conceptName} and p.end_date >= ${HISTORY_FLOOR} and p.end_date <= current_date + interval '30 days'
    order by p.end_date desc
    limit 1
  `;
  return rows[0]?.value ?? null;
}

export interface LatestPriceRow {
  price: string;
  symbol: string;
  bar_timestamp: string;
  feed: string;
}

export interface PriceHistoryPoint {
  date: string;
  price: string;
}

// doc 25 -- real Alpaca price (delayed_sip, ~15min delay). RAW ingested
// price only, not a calculated metric -- Market Cap/P/E/Dividend
// Yield/etc. still need the separate, not-yet-built Mapper follow-on
// (doc 13's locked boundary: Company Master ingests price, Mapper
// calculates price-dependent metrics). Most recent price_date only --
// core.market_price_alpaca is a small daily snapshot table, not a full
// history.
export async function getLatestPrice(companyId: number): Promise<LatestPriceRow | null> {
  const rows = await sql<LatestPriceRow[]>`
    select price::text, symbol, bar_timestamp::text, feed
    from core.market_price_alpaca
    where company_id = ${companyId}
    order by price_date desc
    limit 1
  `;
  return rows[0] ?? null;
}

export interface StatementPeriod {
  fiscal_year: number;
  fiscal_period: string;
  period_end: string;
}

export interface StatementLineRow {
  label: string;
  values: (string | null)[];
}

export interface Statement {
  periods: StatementPeriod[];
  lines: StatementLineRow[];
}

// Direct SQL port of pipeline's statements/classify.py::get_statement --
// same source tables (analytics.statement_line + canonical_fact), same
// fiscal_period-is-not-null filter (doc 17 Sec 4's YTD-duplicate fix).
//
// `frequency` splits FY from quarterly periods -- found live 2026-08-17:
// a company's FY period and its Q4 period share the same end_date (Q4 is
// the fiscal year's own last quarter), so a single merged table sorted by
// end_date interleaves "FY 2025" between "Q3 2025" and "Q4 2025" with no
// stable, sensible order. Screener.in's real page (doc 17 Sec 1) never
// merges these either -- Quarterly Results is its own section, separate
// from the annual Profit & Loss/Balance Sheet/Cash Flow sections. This
// matches that structure instead of inventing a different one.
export async function getStatement(companyId: number, statement: string, frequency: "annual" | "quarterly" = "annual"): Promise<Statement> {
  const periodFilter = frequency === "annual" ? sql`p.fiscal_period = 'FY'` : sql`p.fiscal_period in ('Q1','Q2','Q3','Q4')`;
  const rows = await sql<
    { display_order: number; display_label: string; fiscal_year: number | null; fiscal_period: string | null; period_end: string | null; value: string | null }[]
  >`
    select sl.display_order, sl.display_label, p.fiscal_year, p.fiscal_period, p.end_date::text as period_end, cf.value
    from analytics.statement_line sl
    left join analytics.canonical_fact cf
      on cf.canonical_concept_id = sl.canonical_concept_id and cf.company_id = ${companyId}
    left join core.period p on p.id = cf.period_id
    where sl.statement = ${statement} and (${periodFilter} or p.id is null)
      and (p.end_date is null or (p.end_date >= ${HISTORY_FLOOR} and p.end_date <= current_date + interval '30 days'))
    order by sl.display_order, p.end_date
  `;

  const periodKey = (fy: number, fp: string, pe: string) => `${fy}|${fp}|${pe}`;
  const periodMap = new Map<string, StatementPeriod>();
  const lineMap = new Map<number, { label: string; values: Map<string, string | null> }>();

  for (const r of rows) {
    if (!lineMap.has(r.display_order)) lineMap.set(r.display_order, { label: r.display_label, values: new Map() });
    if (r.period_end && r.fiscal_year && r.fiscal_period) {
      const key = periodKey(r.fiscal_year, r.fiscal_period, r.period_end);
      periodMap.set(key, { fiscal_year: r.fiscal_year, fiscal_period: r.fiscal_period, period_end: r.period_end });
      lineMap.get(r.display_order)!.values.set(key, r.value);
    }
  }

  const periods = [...periodMap.entries()].sort((a, b) => a[1].period_end.localeCompare(b[1].period_end));
  return {
    periods: periods.map(([, p]) => p),
    lines: [...lineMap.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([, l]) => ({ label: l.label, values: periods.map(([key]) => l.values.get(key) ?? null) })),
  };
}

// Trailing N fiscal-year values for one metric, most-recent-first --
// used by the Pros/Cons checklist (doc 17 Sec 5) for multi-year rules.
export async function getMetricHistory(companyId: number, metricName: string, years: number): Promise<(string | null)[]> {
  const rows = await sql<{ value: string | null }[]>`
    select mv.value
    from analytics.metric_value mv
    join analytics.metric_definition md on md.id = mv.metric_definition_id
    where mv.company_id = ${companyId} and md.metric_name = ${metricName} and mv.period_label = 'FY'
      and mv.period_end >= ${HISTORY_FLOOR} and mv.period_end <= current_date + interval '30 days'
    order by mv.period_end desc
    limit ${years}
  `;
  return rows.map((r) => r.value);
}

export interface FilingRow {
  form: string;
  filing_date: string;
  accession_number: string;
  items: string | null;
}

// items (doc 21 / doc 24 Phase 1): SEC's own structured 8-K event
// classification (e.g. "2.02,9.01"), null for every non-8-K form.
export async function getRecentFilings(companyId: number, limit = 10): Promise<FilingRow[]> {
  return sql<FilingRow[]>`
    select form, filing_date::text, accession_number, items
    from core.filing
    where company_id = ${companyId} and filing_date is not null
    order by filing_date desc
    limit ${limit}
  `;
}

// doc 39 (2026-08-30) -- core.employee_headcount_disclosure, regex-
// extracted from the 4 most recent 10-Ks (this disclosure is confirmed
// annual-only, not repeated in 10-Qs). Deliberately NOT sourced from
// core.fact/analytics.canonical_fact: only ~3.5% of companies tag
// dei:EntityNumberOfEmployees as structured XBRL (checked live -- not
// even Apple/Microsoft/Costco do), so this table is the real coverage
// path. is_approximate reflects the filing's own "approximately" wording
// -- never silently dropped, since a layoff/growth reading should carry
// that same uncertainty forward, not present a rounded figure as exact.
export interface EmployeeHeadcountRow {
  filing_date: string;
  headcount: number;
  is_approximate: boolean;
}

// doc 37 (2026-08-31) -- core.segment_revenue, parsed from each
// company's latest 10-Q/10-K "Details" report (the standard Company
// Facts API strips dimensional/segment XBRL entirely -- doc 22). Only
// covers a handful of golden-set companies so far, not full population
// -- an empty array is expected and renders nothing, same honest-gap
// pattern as every other not-yet-scaled section on this page.
export interface SegmentRevenueRow {
  segment_name: string;
  period_type: string;
  period_end: string;
  value: string;
}

export interface InsiderTransactionRow {
  reporting_owner_name: string;
  officer_title: string | null;
  is_director: boolean;
  is_officer: boolean;
  is_ten_percent_owner: boolean;
  transaction_date: string | null;
  transaction_code: string | null;
  acquired_disposed_code: string | null;
  shares: string | null;
  price_per_share: string | null;
  shares_owned_following: string | null;
  is_10b5_1_plan: boolean | null;
  accession_number: string;
}

// doc 19 Stage 2 -- core.insider_transaction, Form 4 only (Form 3/5 out of
// scope for this pass, see ownership/insider.py's module docstring).
// is_10b5_1_plan (doc 23 Stage A / doc 24 Phase 1): null for any filing
// before the rule's 2023-04-01 effective date -- shown as "—", never
// defaulted to "discretionary."
// MVP decision 2026-08-28: collect and display 12 months only -- mirrors
// insider.py's MIN_FILING_DATE bound, no deep-history backfill for now.
export async function getRecentInsiderTransactions(companyId: number, limit = 15): Promise<InsiderTransactionRow[]> {
  return sql<InsiderTransactionRow[]>`
    select reporting_owner_name, officer_title, is_director, is_officer, is_ten_percent_owner,
           transaction_date::text, transaction_code, acquired_disposed_code,
           shares::text, price_per_share::text, shares_owned_following::text, is_10b5_1_plan, accession_number
    from core.insider_transaction
    where company_id = ${companyId}
      and transaction_date is not null
      and transaction_date >= (current_date - interval '12 months')
    order by transaction_date desc
    limit ${limit}
  `;
}

export interface BeneficialOwnershipRow {
  filer_name: string;
  schedule_type: string;
  is_amendment: boolean;
  filing_date: string | null;
  accession_number: string;
}

// doc 19 Stage 3 -- core.beneficial_ownership. Every row here already
// passed the issuer-vs-filer check at write time (ownership/beneficial_ownership.py)
// -- no re-filtering needed at read time. percent_of_class/shares_owned are
// intentionally not selected: not yet extracted (see that module's docstring),
// so surfacing them would show nulls for every real row -- filer name +
// schedule type + date is the honest slice of what's actually populated.
export async function getRecentBeneficialOwnership(companyId: number, limit = 15): Promise<BeneficialOwnershipRow[]> {
  return sql<BeneficialOwnershipRow[]>`
    select filer_name, schedule_type, is_amendment, filing_date::text, accession_number
    from core.beneficial_ownership
    where company_id = ${companyId}
    order by filing_date desc nulls last
    limit ${limit}
  `;
}

export interface InstitutionalHolderRow {
  filer_name: string;
  shares: string | null;
  value_usd: string | null;
  filing_date: string | null;
}

// insider_info.md Overview + Insider Ownership subsections --
// core.insider_ownership_summary/insider_window_summary
// (ownership/insider_summary.py). Full-population build was still in
// progress at the time this was wired in (see doc/audit/2026-08-29's
// display-rule addendum to insider_info.md) -- ownershipSummary is
// legitimately `null` for a company not yet processed, same honest-null
// discipline as every other not-yet-computed field on this page, not an
// error state.
export interface InsiderOwnershipSummaryRow {
  ownership_pct: string | null;
  shares_owned_by_insiders: string | null;
  distinct_insiders_count: number;
  is_null_reason: string | null;
}

export interface InsiderWindowSummaryRow {
  window_months: number;
  shares_bought: string;
  shares_sold: string;
  buy_dollar_volume: string;
  sell_dollar_volume: string;
  insiders_buying_count: number;
  insiders_selling_count: number;
  largest_purchase_owner_name: string | null;
  largest_purchase_date: string | null;
  largest_purchase_shares: string | null;
  largest_purchase_price: string | null;
  largest_purchase_value: string | null;
  largest_sale_owner_name: string | null;
  largest_sale_date: string | null;
  largest_sale_shares: string | null;
  largest_sale_price: string | null;
  largest_sale_value: string | null;
}

// insider_info.md Institutional Ownership subsection --
// core.institutional_ownership_summary (ownership/institutional_summary.py,
// 2-consecutive-quarter comparison). Golden-10 only as of 2026-08-29 --
// null for every other company, same honest-null contract as above;
// the stock page falls back to the older single-window
// getTopInstitutionalHolders list when this is null so every company
// still shows something.
export interface InstitutionalTopHolderRow {
  filer_name: string;
  filer_cik: string;
  shares: string;
  value_usd: string | null;
  ownership_pct: string | null;
  share_change: string | null;
  pct_change: string | null;
  status: string;
  report_period: string;
}

export interface InstitutionalOwnershipSummaryRow {
  report_period_latest: string;
  report_period_prior: string;
  total_institutional_pct: string | null;
  total_institutional_pct_prior: string | null;
  qoq_change_pct: string | null;
  total_holders: number;
  holders_increased: number;
  holders_decreased: number;
  new_positions: number;
  exited_positions: number;
  top_holders: InstitutionalTopHolderRow[];
}

// insider_info.md Mutual Fund Ownership subsection --
// core.fund_ownership_summary (ownership/mutual_fund_summary.py,
// 2-consecutive-period comparison). Golden-10 only as of 2026-08-29;
// portfolio_weight_pct/fund_family are individually honest-null per
// holder when Form N-PORT didn't report them (doc's own "when
// available" scoping for portfolio weight), not just at the summary
// level.
export interface FundTopHolderRow {
  fund_name: string;
  fund_cik: string;
  fund_family: string | null;
  shares: string;
  value_usd: string | null;
  ownership_pct: string | null;
  portfolio_weight_pct: string | null;
  share_change: string | null;
  pct_change: string | null;
  status: string;
  report_period: string;
}

export interface FundOwnershipSummaryRow {
  report_period_latest: string;
  report_period_prior: string;
  total_fund_ownership_pct: string | null;
  total_fund_ownership_pct_prior: string | null;
  change_in_pct: string | null;
  total_funds_holding: number;
  funds_increasing: number;
  funds_decreasing: number;
  new_positions: number;
  exited_positions: number;
  top_holders: FundTopHolderRow[];
}

interface RawStatementRow {
  statement: string;
  display_order: number;
  display_label: string;
  fiscal_year: number | null;
  fiscal_period: string | null;
  period_end: string | null;
  value: string | null;
}

export interface MetricHistoryPoint {
  value: string | null;
  period_end: string;
}

interface MetricHistoryRow extends MetricHistoryPoint {
  metric_name: string;
}

interface CompanyPageQueryRow {
  company: CompanyIdentity;
  metrics: MetricRow[];
  statements: RawStatementRow[];
  filings: FilingRow[];
  insider_transactions: InsiderTransactionRow[];
  beneficial_ownership: BeneficialOwnershipRow[];
  institutional_holders: InstitutionalHolderRow[];
  public_float: PublicFloatRow | null;
  latest_price: LatestPriceRow | null;
  price_history: PriceHistoryPoint[];
  book_value: string | null;
  metric_history: MetricHistoryRow[];
  peer_companies: PeerCompanyRow[];
  insider_ownership_summary: InsiderOwnershipSummaryRow | null;
  insider_window_summary: InsiderWindowSummaryRow[];
  institutional_ownership_summary: InstitutionalOwnershipSummaryRow | null;
  fund_ownership_summary: FundOwnershipSummaryRow | null;
  employee_headcount_history: EmployeeHeadcountRow[];
  segment_revenue: SegmentRevenueRow[];
}

export interface CompanyPageData {
  company: CompanyIdentity;
  metrics: Record<string, MetricRow>;
  quarterlyResults: Statement;
  incomeStatement: Statement;
  balanceSheet: Statement;
  cashFlow: Statement;
  filings: FilingRow[];
  insiderTransactions: InsiderTransactionRow[];
  beneficialOwnership: BeneficialOwnershipRow[];
  institutionalHolders: InstitutionalHolderRow[];
  publicFloat: PublicFloatRow | null;
  latestPrice: LatestPriceRow | null;
  priceHistory: PriceHistoryPoint[];
  bookValue: string | null;
  metricHistory: Record<string, (string | null)[]>;
  metricTrendHistory: Record<string, MetricHistoryPoint[]>;
  peerCompanies: PeerCompanyRow[];
  insiderOwnershipSummary: InsiderOwnershipSummaryRow | null;
  insiderWindowSummary: InsiderWindowSummaryRow[];
  institutionalSummary: InstitutionalOwnershipSummaryRow | null;
  fundSummary: FundOwnershipSummaryRow | null;
  employeeHeadcountHistory: EmployeeHeadcountRow[];
  segmentRevenue: SegmentRevenueRow[];
}

function assembleStatement(
  rows: RawStatementRow[],
  statement: string,
  frequency: "annual" | "quarterly",
): Statement {
  const matchingRows = rows.filter((row) => {
    if (row.statement !== statement) return false;
    if (row.fiscal_period === null) return true;
    return frequency === "annual"
      ? row.fiscal_period === "FY"
      : ["Q1", "Q2", "Q3", "Q4"].includes(row.fiscal_period);
  });
  const periodKey = (fy: number, fp: string, pe: string) => `${fy}|${fp}|${pe}`;
  const periodMap = new Map<string, StatementPeriod>();
  const lineMap = new Map<number, { label: string; values: Map<string, string | null> }>();

  for (const row of matchingRows) {
    if (!lineMap.has(row.display_order)) {
      lineMap.set(row.display_order, { label: row.display_label, values: new Map() });
    }
    if (row.period_end && row.fiscal_year && row.fiscal_period) {
      const key = periodKey(row.fiscal_year, row.fiscal_period, row.period_end);
      periodMap.set(key, {
        fiscal_year: row.fiscal_year,
        fiscal_period: row.fiscal_period,
        period_end: row.period_end,
      });
      lineMap.get(row.display_order)!.values.set(key, row.value);
    }
  }

  const periods = [...periodMap.entries()].sort((a, b) => a[1].period_end.localeCompare(b[1].period_end));
  return {
    periods: periods.map(([, period]) => period),
    lines: [...lineMap.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([, line]) => ({
        label: line.label,
        values: periods.map(([key]) => line.values.get(key) ?? null),
      })),
  };
}

/**
 * Fetch every public company-page section in one parameterized SQL request.
 *
 * PostgreSQL still executes the individual subqueries, but the visitor pays
 * for one connection acquisition and one network round trip instead of 16.
 * Numeric financial values are cast to text before JSON construction so this
 * keeps the project's Decimal-as-string boundary intact.
 */
export async function getCompanyPageData(ticker: string): Promise<CompanyPageData | null> {
  const rows = await sql<CompanyPageQueryRow[]>`
    with selected_company as (
      -- company_name is COALESCE'd to core.company.display_name when
      -- present -- found live 2026-09-07, direct user report: raw SEC
      -- names carry EDGAR's own disambiguation suffix ("COSTCO WHOLESALE
      -- CORP /NEW", "TUCOWS INC /PA/"), which looked broken rendered
      -- as-is. display_name (company_master/display_name.py) is a
      -- separate, non-authoritative column -- yfinance longName/
      -- shortName first, OpenFIGI name second, a deterministic suffix
      -- strip always as the guaranteed fallback -- core.company.company_name
      -- itself is untouched and remains the real SEC-filed legal name.
      -- Safe to coalesce under the same field name here: this interface
      -- has exactly one consumer (this page), never used as a join/lookup
      -- key.
      select c.id, c.cik, coalesce(c.display_name, c.company_name) as company_name,
             c.sic_code, c.sic_description,
             c.sector, c.y_sector, c.y_industry, c.status, l.ticker,
             c.about_text, c.y_about_text, c.ein, c.business_address_line1,
             c.business_address_city, c.business_address_state,
             c.business_address_zip, c.business_phone, c.website, c.y_website
      from core.company c
      join core.listing l on l.company_id = c.id
      where lower(l.ticker) = lower(${ticker}) and ${EQUITY_ONLY_SQL}
      order by (l.effective_to is null) desc
      limit 1
    ),
    peer_companies as (
      -- Peer group: exact match on core.company.y_industry (yfinance's own
      -- industry classification -- see doc 02's decision register for why
      -- this is now a stored, production field, and doc/planning/y-finance.md
      -- for the ToS tradeoff that decision knowingly accepts). Replaced a
      -- 4-tier SIC+yfinance-industry+yfinance-sector+SIC-sector cascade
      -- 2026-09-06 by explicit user direction ("use industry only") --
      -- y_industry alone already gives tighter, more correct peer groups
      -- than SIC-exact for real cases the cascade's own history names
      -- (Visa/Mastercard/PayPal/Western Union share y_industry='Credit
      -- Services' despite sharing an unrelated SIC code with Uber/Etsy;
      -- SPAC shells correctly share y_industry='Shell Companies'), so one
      -- clean tier replaces the cascade rather than layering under it.
      -- Companies with no yfinance industry data (~18% of the active
      -- population, see company_master/yfinance_industry.py) simply get
      -- an honest empty peer list -- no SIC/sector fallback guess.
      select distinct on (c.id) c.id, l.ticker, coalesce(c.display_name, c.company_name) as company_name, 'industry'::text as match_basis
      from core.company c
      join core.listing l on l.company_id = c.id
      join selected_company company on company.y_industry is not null and c.y_industry = company.y_industry
      where c.status = 'active'
        and c.id != company.id
        and l.effective_to is null
        and l.ticker is not null
        and ${EQUITY_ONLY_SQL}
      order by c.id, (l.security_type = 'Common Stock') desc nulls last
    ),
    peer_metrics as (
      select mv.company_id, md.metric_name, mv.value,
             row_number() over (
               partition by mv.company_id, md.metric_name
               order by (mv.period_label = 'TTM') desc, mv.period_end desc
             ) as rn
      from analytics.metric_value mv
      join analytics.metric_definition md on md.id = mv.metric_definition_id
      join peer_companies p on p.id = mv.company_id
      where md.metric_name in ('roe', 'roic', 'revenue_growth_3y_cagr', 'net_margin')
        and mv.value is not null
        -- Real bug found live 2026-08-29: ranking peers by raw ROIC
        -- surfaced values like 9107% and net margins like -53,774% --
        -- the well-known ROE/ROIC/margin degeneracy for a company with
        -- near-zero invested capital or revenue, not real outperformance.
        -- Bounding to +/-200% excludes the formula-degenerate cases
        -- without needing Market Cap (still 0 population-wide, blocked
        -- on the price vendor) to filter by company size instead.
        and (md.metric_name = 'revenue_growth_3y_cagr' or (mv.value >= -2.0 and mv.value <= 2.0))
    ),
    ranked_metrics as (
      select md.metric_name, mv.value::text as value, mv.period_label,
             mv.period_end::text as period_end, mv.is_null_reason,
             row_number() over (
               partition by md.metric_name
               order by (mv.period_label = 'TTM') desc, mv.period_end desc
             ) as rank
      from analytics.metric_value mv
      join analytics.metric_definition md on md.id = mv.metric_definition_id
      join selected_company company on company.id = mv.company_id
      where mv.period_end >= ${HISTORY_FLOOR} and mv.period_end <= current_date + interval '30 days'
    ),
    -- Real reporting periods (fiscal_year, fiscal_period), NOT raw
    -- core.period rows -- found live 2026-09-05, a real bug: a single
    -- real quarter/year routinely has 2+ distinct core.period rows
    -- sharing (or nearly sharing) the same end_date, one 'instant'
    -- (balance-sheet "as of") and one 'duration' (income/cash-flow
    -- "for the period"), sometimes a third stray instant row (e.g. a
    -- shares-outstanding-as-of-filing-date fact, dated days after the
    -- real quarter-end). The previous 'limit 8' on 'distinct period.id'
    -- silently counted these as separate "periods", so 8 raw-row slots
    -- covered only ~2-4 REAL quarters -- confirmed live for AAPL,
    -- whose real Q3 2026 has 3 separate period.id rows (631/714/784)
    -- for what a user experiences as one quarter. This CTE now picks 8
    -- (quarterly) / 7 (annual, matching this project's own already-
    -- decided public-page depth policy) DISTINCT REAL periods first,
    -- then annual_periods/quarterly_periods below pull in every
    -- period.id belonging to those chosen periods (both instant and
    -- duration), so assembleStatement's own per-statement-type
    -- filtering always has a complete period to draw from.
    annual_fiscal_periods as (
      select distinct fact.company_id, period.fiscal_year, period.fiscal_period
      from analytics.canonical_fact fact
      join core.period period on period.id = fact.period_id
      join selected_company company on company.id = fact.company_id
      where period.fiscal_period = 'FY' and period.end_date >= ${HISTORY_FLOOR} and period.end_date <= current_date + interval '30 days'
      order by period.fiscal_year desc
      limit 7
    ),
    quarterly_fiscal_periods_distinct as (
      select distinct fact.company_id, period.fiscal_year, period.fiscal_period
      from analytics.canonical_fact fact
      join core.period period on period.id = fact.period_id
      join selected_company company on company.id = fact.company_id
      where period.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4') and period.end_date >= ${HISTORY_FLOOR} and period.end_date <= current_date + interval '30 days'
    ),
    -- row_number() computed over the ALREADY-distinct set above --
    -- computing it directly alongside 'select distinct' would number
    -- every raw joined row (which legitimately repeats per real quarter
    -- once per underlying instant/duration period.id), making every row
    -- "distinct" by its own unique rn and defeating the dedup entirely.
    quarterly_fiscal_periods as (
      select *, row_number() over (order by fiscal_year desc, fiscal_period desc) as rn
      from quarterly_fiscal_periods_distinct
    ),
    annual_periods as (
      select distinct period.id, period.end_date
      from core.period period
      join annual_fiscal_periods afp
        on afp.company_id = period.company_id
       and afp.fiscal_year = period.fiscal_year
       and afp.fiscal_period = period.fiscal_period
    ),
    quarterly_periods as (
      select distinct period.id, period.end_date
      from core.period period
      join (select * from quarterly_fiscal_periods order by rn limit 8) qfp
        on qfp.company_id = period.company_id
       and qfp.fiscal_year = period.fiscal_year
       and qfp.fiscal_period = period.fiscal_period
    ),
    displayed_periods as (
      select id from annual_periods
      union
      select id from quarterly_periods
    ),
    statement_rows as (
      select sl.statement, sl.display_order::numeric as display_order, sl.display_label,
             p.fiscal_year, p.fiscal_period, p.end_date::text as period_end,
             cf.value::text as value
      from analytics.statement_line sl
      cross join selected_company company
      left join analytics.canonical_fact cf
        on cf.canonical_concept_id = sl.canonical_concept_id
       and cf.company_id = company.id
      left join core.period p on p.id = cf.period_id
      where sl.statement in ('income_statement', 'balance_sheet', 'cash_flow')
        and (p.id in (select id from displayed_periods) or p.id is null)
    ),
    -- EBITDA, sourced from analytics.metric_value (a computed metric, not
    -- a raw filed XBRL concept, so it has no canonical_concept_id / never
    -- appears in analytics.statement_line -- that table is Mapper's
    -- frozen boundary, per doc 04/17). Added 2026-09-08, direct user
    -- report: EBITDA -- one of the figures an equity researcher looks
    -- for first -- had no row anywhere on the page, only the EV/EBITDA
    -- and Net Debt/EBITDA *ratio* cards used it internally. calculate.py's
    -- generic engine already computes a real per-period (Q1-Q4/FY) value
    -- (verified live against AAPL before wiring this in), separate from
    -- expanded_metrics.py's own 'TTM'-labeled sum -- joining on
    -- (period_end, period_label = fiscal_period) naturally excludes the
    -- TTM row (its period_end is always today's date, never a real
    -- core.period end_date), so no separate exclusion filter is needed.
    -- display_order 5.5 places it directly under Operating Income (5),
    -- ahead of Interest Expense (6) -- standard income-statement placement.
    ebitda_rows as (
      select 'income_statement'::text as statement,
             5.5::numeric as display_order,
             'EBITDA'::text as display_label,
             p.fiscal_year, p.fiscal_period, p.end_date::text as period_end,
             mv.value::text as value
      from core.period p
      join selected_company company on company.id = p.company_id
      join analytics.metric_value mv
        on mv.company_id = p.company_id
       and mv.period_end = p.end_date
       and mv.period_label = p.fiscal_period
      join analytics.metric_definition md
        on md.id = mv.metric_definition_id and md.metric_name = 'ebitda'
      where p.id in (select id from displayed_periods)
        and mv.value is not null
    ),
    -- Free Cash Flow -- same pattern as ebitda_rows above, same day
    -- (direct user report: "verify the row of all financial table --
    -- are rows name correct? flow is correct?"). FCF was completely
    -- absent from the cash flow table despite being one of the most
    -- fundamental figures in equity research (verified live against
    -- AAPL FY2025: $98,767,000,000, exactly CFO $111,482,000,000 minus
    -- CapEx $12,715,000,000). Placed at display_order 4.5 -- directly
    -- after Capital Expenditures (4, post migration 0056's reorder),
    -- the natural derivation point, ahead of Dividends Paid (5).
    fcf_rows as (
      select 'cash_flow'::text as statement,
             4.5::numeric as display_order,
             'Free Cash Flow'::text as display_label,
             p.fiscal_year, p.fiscal_period, p.end_date::text as period_end,
             mv.value::text as value
      from core.period p
      join selected_company company on company.id = p.company_id
      join analytics.metric_value mv
        on mv.company_id = p.company_id
       and mv.period_end = p.end_date
       and mv.period_label = p.fiscal_period
      join analytics.metric_definition md
        on md.id = mv.metric_definition_id and md.metric_name = 'fcf'
      where p.id in (select id from displayed_periods)
        and mv.value is not null
    ),
    combined_statement_rows as (
      select * from statement_rows
      union all
      select * from ebitda_rows
      union all
      select * from fcf_rows
    ),
    metric_history_rows as (
      select md.metric_name, mv.value::text as value,
             mv.period_end::text as period_end,
             row_number() over (
               partition by md.metric_name order by mv.period_end desc
             ) as rank
      from analytics.metric_value mv
      join analytics.metric_definition md on md.id = mv.metric_definition_id
      join selected_company company on company.id = mv.company_id
      where md.metric_name in (
        'roe', 'roic', 'fcf', 'fcf_margin', 'revenue_growth_yoy',
        'operating_margin', 'net_margin', 'debt_to_equity',
        'net_debt_ebitda', 'share_dilution_trend'
      )
        and mv.period_label = 'FY'
        and mv.period_end >= ${HISTORY_FLOOR} and mv.period_end <= current_date + interval '30 days'
    )
    select
      jsonb_build_object(
        'id', company.id,
        'cik', company.cik,
        'company_name', company.company_name,
        'sic_code', company.sic_code,
        'sic_description', company.sic_description,
        'sector', company.sector,
        'status', company.status,
        'ticker', company.ticker,
        'about_text', coalesce(company.about_text, company.y_about_text),
        'ein', company.ein,
        'business_address_line1', company.business_address_line1,
        'business_address_city', company.business_address_city,
        'business_address_state', company.business_address_state,
        'business_address_zip', company.business_address_zip,
        'business_phone', company.business_phone,
        'website', coalesce(company.website, regexp_replace(company.y_website, '^https?://', ''))
      ) as company,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'metric_name', metric_name,
          'value', value,
          'period_label', period_label,
          'period_end', period_end,
          'is_null_reason', is_null_reason
        ) order by metric_name)
        from ranked_metrics where rank = 1
      ), '[]'::jsonb) as metrics,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'statement', statement,
          'display_order', display_order,
          'display_label', display_label,
          'fiscal_year', fiscal_year,
          'fiscal_period', fiscal_period,
          'period_end', period_end,
          'value', value
        ) order by statement, display_order, period_end)
        from combined_statement_rows
      ), '[]'::jsonb) as statements,
      coalesce((
        select jsonb_agg(to_jsonb(recent) order by recent.filing_date desc)
        from (
          select f.form, f.filing_date::text as filing_date,
                 f.accession_number, f.items
          from core.filing f
          where f.company_id = company.id and f.filing_date is not null
          order by f.filing_date desc
          limit 24
        ) recent
      ), '[]'::jsonb) as filings,
      coalesce((
        select jsonb_agg(to_jsonb(recent) order by recent.transaction_date desc)
        from (
          select it.reporting_owner_name, it.officer_title,
                 it.is_director, it.is_officer,
                 it.is_ten_percent_owner,
                 it.transaction_date::text as transaction_date,
                 it.transaction_code, it.acquired_disposed_code,
                 it.shares::text as shares,
                 it.price_per_share::text as price_per_share,
                 it.shares_owned_following::text as shares_owned_following,
                 it.is_10b5_1_plan, it.accession_number
          from core.insider_transaction it
          where it.company_id = company.id
            and it.transaction_date is not null
            and it.transaction_date >= (current_date - interval '12 months')
          order by it.transaction_date desc
          limit 15
        ) recent
      ), '[]'::jsonb) as insider_transactions,
      coalesce((
        select jsonb_agg(to_jsonb(recent) order by recent.filing_date desc nulls last)
        from (
          select ownership.filer_name, ownership.schedule_type,
                 ownership.is_amendment,
                 ownership.filing_date::text as filing_date,
                 ownership.accession_number
          from core.beneficial_ownership ownership
          where ownership.company_id = company.id
          order by ownership.filing_date desc nulls last
          limit 15
        ) recent
      ), '[]'::jsonb) as beneficial_ownership,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'filer_name', holder.filer_name,
          'shares', holder.shares,
          'value_usd', holder.value_usd,
          'filing_date', holder.filing_date
        ) order by holder.sort_shares desc nulls last)
        from (
          select dedup.filer_name, dedup.shares::text as shares,
                 dedup.value_usd::text as value_usd,
                 dedup.filing_date::text as filing_date,
                 dedup.shares as sort_shares
          from (
            select distinct on (ownership.filer_name)
                   ownership.filer_name, ownership.shares,
                   ownership.value_usd, ownership.filing_date,
                   ownership.is_amendment
            from core.institutional_ownership ownership
            where ownership.company_id = company.id
            order by ownership.filer_name, ownership.is_amendment desc,
                     ownership.filing_date desc nulls last
          ) dedup
          order by dedup.shares desc nulls last
          limit 15
        ) holder
      ), '[]'::jsonb) as institutional_holders,
      (
        select jsonb_build_object(
          'value', fact.value::text,
          'period_end', period.end_date::text
        )
        from analytics.canonical_fact fact
        join analytics.canonical_concept concept
          on concept.id = fact.canonical_concept_id
        join core.period period on period.id = fact.period_id
        where fact.company_id = company.id and concept.name = 'public_float' and period.end_date >= ${HISTORY_FLOOR} and period.end_date <= current_date + interval '30 days'
        order by period.end_date desc
        limit 1
      ) as public_float,
      (
        select jsonb_build_object(
          'price', price.price::text,
          'symbol', price.symbol,
          'bar_timestamp', price.bar_timestamp::text,
          'feed', price.feed
        )
        from core.market_price_alpaca price
        where price.company_id = company.id
        order by price.price_date desc
        limit 1
      ) as latest_price,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'date', history.price_date::text,
          'price', history.price::text
        ) order by history.price_date)
        from (
          select price_date, price
          from core.market_price_alpaca
          where company_id = company.id
          order by price_date desc
          limit 3650
        ) history
      ), '[]'::jsonb) as price_history,
      (
        select fact.value::text
        from analytics.canonical_fact fact
        join analytics.canonical_concept concept
          on concept.id = fact.canonical_concept_id
        join core.period period on period.id = fact.period_id
        where fact.company_id = company.id
          and concept.name = 'stockholders_equity'
          and period.end_date >= ${HISTORY_FLOOR} and period.end_date <= current_date + interval '30 days'
        order by period.end_date desc
        limit 1
      ) as book_value,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'metric_name', metric_name,
          'value', value,
          'period_end', period_end
        ) order by metric_name, period_end desc)
        from metric_history_rows where rank <= 3
      ), '[]'::jsonb) as metric_history,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'ticker', peer.ticker,
          'company_name', peer.company_name,
          'match_basis', peer.match_basis,
          'roe', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'roe' and rn = 1),
          'roic', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'roic' and rn = 1),
          'revenue_growth_3y_cagr', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'revenue_growth_3y_cagr' and rn = 1),
          'net_margin', (select value::text from peer_metrics where company_id = peer.id and metric_name = 'net_margin' and rn = 1)
        ) order by peer.sort_roic desc nulls last)
        from (
          -- Every industry-matched peer is shown (the listing itself is
          -- never gated on ROIC existing) -- found live 2026-09-06 that
          -- requiring a non-null ROIC hid every bank peer for JPM (ROIC
          -- isn't computed for any bank, a real formula limitation, not a
          -- matching bug), producing a confusing empty table despite real
          -- peers existing. Missing metric cells render as "--" via
          -- fmtPct's own null handling; sorting still prefers real ROIC
          -- values first, ROIC-less peers last.
          select p.id, p.ticker, p.company_name, p.match_basis,
                 (select value from peer_metrics where company_id = p.id and metric_name = 'roic' and rn = 1) as sort_roic
          from peer_companies p
          order by sort_roic desc nulls last
          limit 10
        ) peer
      ), '[]'::jsonb) as peer_companies,
      (
        select jsonb_build_object(
          'ownership_pct', s.ownership_pct::text,
          'shares_owned_by_insiders', s.shares_owned_by_insiders::text,
          'distinct_insiders_count', s.distinct_insiders_count,
          'is_null_reason', s.is_null_reason
        )
        from core.insider_ownership_summary s
        where s.company_id = company.id
      ) as insider_ownership_summary,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'window_months', w.window_months,
          'shares_bought', w.shares_bought::text,
          'shares_sold', w.shares_sold::text,
          'buy_dollar_volume', w.buy_dollar_volume::text,
          'sell_dollar_volume', w.sell_dollar_volume::text,
          'insiders_buying_count', w.insiders_buying_count,
          'insiders_selling_count', w.insiders_selling_count,
          'largest_purchase_owner_name', w.largest_purchase_owner_name,
          'largest_purchase_date', w.largest_purchase_date::text,
          'largest_purchase_shares', w.largest_purchase_shares::text,
          'largest_purchase_price', w.largest_purchase_price::text,
          'largest_purchase_value', w.largest_purchase_value::text,
          'largest_sale_owner_name', w.largest_sale_owner_name,
          'largest_sale_date', w.largest_sale_date::text,
          'largest_sale_shares', w.largest_sale_shares::text,
          'largest_sale_price', w.largest_sale_price::text,
          'largest_sale_value', w.largest_sale_value::text
        ) order by w.window_months)
        from core.insider_window_summary w
        where w.company_id = company.id
      ), '[]'::jsonb) as insider_window_summary,
      (
        select jsonb_build_object(
          'report_period_latest', ios.report_period_latest::text,
          'report_period_prior', ios.report_period_prior::text,
          'total_institutional_pct', ios.total_institutional_pct::text,
          'total_institutional_pct_prior', ios.total_institutional_pct_prior::text,
          'qoq_change_pct', ios.qoq_change_pct::text,
          'total_holders', ios.total_holders,
          'holders_increased', ios.holders_increased,
          'holders_decreased', ios.holders_decreased,
          'new_positions', ios.new_positions,
          'exited_positions', ios.exited_positions,
          'top_holders', ios.top_holders
        )
        from core.institutional_ownership_summary ios
        where ios.company_id = company.id
      ) as institutional_ownership_summary,
      (
        select jsonb_build_object(
          'report_period_latest', fos.report_period_latest::text,
          'report_period_prior', fos.report_period_prior::text,
          'total_fund_ownership_pct', fos.total_fund_ownership_pct::text,
          'total_fund_ownership_pct_prior', fos.total_fund_ownership_pct_prior::text,
          'change_in_pct', fos.change_in_pct::text,
          'total_funds_holding', fos.total_funds_holding,
          'funds_increasing', fos.funds_increasing,
          'funds_decreasing', fos.funds_decreasing,
          'new_positions', fos.new_positions,
          'exited_positions', fos.exited_positions,
          'top_holders', fos.top_holders
        )
        from core.fund_ownership_summary fos
        where fos.company_id = company.id
      ) as fund_ownership_summary,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'filing_date', h.filing_date::text,
          'headcount', h.headcount,
          'is_approximate', h.is_approximate
        ) order by h.filing_date desc)
        from core.employee_headcount_disclosure h
        where h.company_id = company.id
        limit 4
      ), '[]'::jsonb) as employee_headcount_history,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'segment_name', sr.segment_name,
          'period_type', sr.period_type,
          'period_end', sr.period_end,
          'value', sr.value::text
        ) order by sr.segment_name, sr.period_type)
        from core.segment_revenue sr
        where sr.company_id = company.id
        limit 60
      ), '[]'::jsonb) as segment_revenue
    from selected_company company
  `;

  const row = rows[0];
  if (!row) return null;

  const metricHistory: Record<string, (string | null)[]> = {};
  const metricTrendHistory: Record<string, MetricHistoryPoint[]> = {};
  for (const historyRow of row.metric_history) {
    (metricHistory[historyRow.metric_name] ??= []).push(historyRow.value);
    (metricTrendHistory[historyRow.metric_name] ??= []).push({
      value: historyRow.value,
      period_end: historyRow.period_end,
    });
  }

  return {
    company: row.company,
    metrics: Object.fromEntries(row.metrics.map((metric) => [metric.metric_name, metric])),
    quarterlyResults: assembleStatement(row.statements, "income_statement", "quarterly"),
    incomeStatement: assembleStatement(row.statements, "income_statement", "annual"),
    balanceSheet: assembleStatement(row.statements, "balance_sheet", "annual"),
    cashFlow: assembleStatement(row.statements, "cash_flow", "annual"),
    filings: row.filings,
    insiderTransactions: row.insider_transactions,
    beneficialOwnership: row.beneficial_ownership,
    institutionalHolders: row.institutional_holders,
    publicFloat: row.public_float,
    latestPrice: row.latest_price,
    priceHistory: row.price_history,
    bookValue: row.book_value,
    metricHistory,
    metricTrendHistory,
    peerCompanies: row.peer_companies,
    insiderOwnershipSummary: row.insider_ownership_summary,
    insiderWindowSummary: row.insider_window_summary,
    institutionalSummary: row.institutional_ownership_summary,
    fundSummary: row.fund_ownership_summary,
    employeeHeadcountHistory: row.employee_headcount_history,
    segmentRevenue: row.segment_revenue,
  };
}

// doc 19 Stage 4 -- core.institutional_ownership, matched by CUSIP against
// SEC's bulk Form 13F data set. Now 2 stored reporting windows per company
// (doc 19's later upgrade) -- scoped here to whichever window has the most
// recent filing_date, the single most-recent snapshot, not a blended
// multi-quarter total. Deduplicated per FILER (filer_cik, not filer_name
// text) and per FILING (accession_number, preferring an amendment over its
// original), then SUMS every row within that one chosen filing.
//
// Fixed 2026-09-05, a real, serious undercounting bug: the original query
// deduped with `distinct on (filer_name)` and kept only ONE raw row per
// filer. A single Form 13F filing can legitimately report the SAME
// security across multiple separate INFOTABLE rows for one filer
// (different investment-discretion/managed-account categories) --
// confirmed live for AAPL, "BlackRock, Inc." reports 25 separate rows, all
// under one accession_number, all is_amendment=false, summing to ~$1.1B;
// the old query kept only the single largest ($423.9M) and silently
// discarded the other 24. See pipeline's mapper/expanded_metrics.py
// (_institutional_ownership_shares) and ownership/institutional_summary.py
// (_period_holders) for the same fix applied the same day, and
// doc/learnings/form-13f-cusip-crosswalk.md for the original build.
export async function getTopInstitutionalHolders(companyId: number, limit = 15): Promise<InstitutionalHolderRow[]> {
  // dedup.shares is explicitly qualified in the ORDER BY below -- an
  // earlier, unqualified `order by shares desc` silently bound to this
  // query's own `shares::text` output column instead of the numeric
  // subquery column (Postgres prefers an unqualified SELECT-list alias
  // over a same-named FROM-clause column), sorting lexicographically
  // ("9995" > "9990000" as text) instead of numerically. Caught live:
  // AAPL's real top holder (Vanguard, ~950M shares) was appearing below
  // filers holding under 10,000 shares.
  return sql<InstitutionalHolderRow[]>`
    select max(filer_name) as filer_name, sum(shares)::text as shares, sum(value_usd)::text as value_usd, max(filing_date)::text as filing_date
    from core.institutional_ownership io
    join (
      select distinct on (filer_cik) filer_cik, accession_number
      from core.institutional_ownership
      where company_id = ${companyId}
        and source_zip = (
          select source_zip from core.institutional_ownership
          where company_id = ${companyId}
          group by source_zip
          order by max(filing_date) desc nulls last
          limit 1
        )
      order by filer_cik, is_amendment desc, filing_date desc nulls last
    ) chosen_filing
      on chosen_filing.filer_cik = io.filer_cik
     and chosen_filing.accession_number = io.accession_number
    where io.company_id = ${companyId}
    group by io.filer_cik
    order by sum(shares) desc nulls last
    limit ${limit}
  `;
}

export interface PeerCompanyRow {
  ticker: string;
  company_name: string;
  // Single tier since 2026-09-06 (by explicit user direction, replacing a
  // 4-tier SIC+yfinance cascade): exact core.company.y_industry match --
  // see peer_companies CTE in getCompanyPageData.
  match_basis: "industry";
  roe: string | null;
  roic: string | null;
  revenue_growth_3y_cagr: string | null;
  net_margin: string | null;
}

export interface ExampleScreenRow {
  ticker: string;
  company_name: string;
  roic: string;
  revenue_growth_3y_cagr: string | null;
}

export interface CompanyDirectoryRow {
  ticker: string;
  company_name: string;
  exchange: string | null;
  sector: string | null;
}

// Public company autocomplete. Only current listings for active companies are
// exposed, so every suggestion resolves to a real `/stocks/{ticker}/` page.
// The browser calls the dedicated cached endpoint only after interaction; this
// query is never part of the consolidated company-page request.
export async function searchCompanyDirectory(query: string, limit = 8): Promise<CompanyDirectoryRow[]> {
  const normalized = query.trim().replace(/\s+/g, " ").toLowerCase().slice(0, 64);
  if (!normalized) return [];

  return sql<CompanyDirectoryRow[]>`
    with candidates as (
      select distinct on (lower(l.ticker))
        l.ticker,
        coalesce(c.display_name, c.company_name) as company_name,
        l.exchange,
        c.sector
      from core.company c
      join core.listing l on l.company_id = c.id
      where c.status = 'active'
        and l.effective_to is null
        and l.ticker is not null
        and ${EQUITY_ONLY_SQL}
        and (
          starts_with(lower(l.ticker), ${normalized})
          or starts_with(lower(c.company_name), ${normalized})
          or starts_with(lower(c.display_name), ${normalized})
        )
      order by lower(l.ticker), c.company_name
    )
    select ticker, company_name, exchange, sector
    from candidates
    order by
      case
        when lower(ticker) = ${normalized} then 0
        when lower(company_name) = ${normalized} then 1
        when starts_with(lower(ticker), ${normalized}) then 2
        else 3
      end,
      length(ticker),
      ticker
    limit ${limit}
  `;
}

// Homepage shortcuts stay honest without loading the whole company directory.
// This is a small homepage-only query and never runs on company research pages.
export async function getCompaniesByTickers(tickers: string[]): Promise<CompanyDirectoryRow[]> {
  if (tickers.length === 0) return [];
  const normalized = tickers.map((ticker) => ticker.toUpperCase());
  return sql<CompanyDirectoryRow[]>`
    select distinct on (upper(l.ticker))
      l.ticker, coalesce(c.display_name, c.company_name) as company_name, l.exchange, c.sector
    from core.company c
    join core.listing l on l.company_id = c.id
    where c.status = 'active'
      and l.effective_to is null
      and upper(l.ticker) in ${sql(normalized)}
      and ${EQUITY_ONLY_SQL}
    order by upper(l.ticker), c.company_name
  `;
}

// Sector/industry collection pages (2026-09-06): /stocks/sector/{slug} and
// /stocks/industry/{slug}. `sector` is the 11-bucket SIC-derived taxonomy
// (company_master/sector_bucket.py); `y_industry` is yfinance's own,
// finer-grained classification (company_master/yfinance_industry.py) --
// two genuinely different fields, not a merge, same separation this
// project already keeps everywhere else these two sources meet.
//
// Neither is stored as a slug, so slugify() below is the one place that
// turns a real display name into a URL segment, and the same function
// must be used to match a URL slug back to its real name -- never
// duplicate this logic, or a slug and its target can silently drift.
export function slugify(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

export interface SectorSummaryRow {
  sector: string;
  slug: string;
  company_count: string;
}

export interface IndustrySummaryRow {
  y_industry: string;
  slug: string;
  company_count: string;
}

// 'Other' is deliberately excluded -- per the 2026-09-06 peer-comparison
// fix, it's a real "no real SIC on file / a legacy catch-all code" bucket,
// not an actual sector a visitor would expect to browse.
// Uses y_sector, NOT the SIC-derived core.company.sector -- found live
// 2026-09-06 (direct question: "why not use yfinance data here") that
// y_sector has zero catch-all bucket (every value is a real sector),
// while the SIC-derived version's "Other" bucket is its SECOND-LARGEST
// "sector" (1,039 companies) -- a real, known data-quality issue (SPACs/
// shells/legacy catch-all SIC codes), not something a sector browsing
// page should present as if it were a real sector. y_sector also nests
// correctly under y_industry (verified live: Semiconductors -> Technology,
// Banks - Regional -> Financial Services), so sector and industry now
// come from the same coherent taxonomy instead of two unrelated ones.
// A handful of companies have y_sector = '' (empty string, not null) --
// filtered out same as null.
// count(distinct c.id), not count(*): a company with more than one
// currently-active listing (multiple share classes, or a SPAC's common/
// unit/warrant trio -- checked live, real, common) gets one row per
// listing after the join, so count(*) silently multiplies its count.
// Found live 2026-09-06 by a direct question about the numbers: "Shell
// Companies" (mostly SPACs) showed 911 with count(*) vs. a real 327.
export async function getSectorList(): Promise<SectorSummaryRow[]> {
  const rows = await sql<{ sector: string; company_count: string }[]>`
    select c.y_sector as sector, count(distinct c.id)::text as company_count
    from core.company c
    join core.listing l on l.company_id = c.id and l.effective_to is null
    where c.status = 'active' and c.y_sector is not null and c.y_sector != ''
    group by c.y_sector
    order by c.y_sector
  `;
  return rows.map((row) => ({ ...row, slug: slugify(row.sector) }));
}

export async function getIndustryList(): Promise<IndustrySummaryRow[]> {
  const rows = await sql<{ y_industry: string; company_count: string }[]>`
    select c.y_industry, count(distinct c.id)::text as company_count
    from core.company c
    join core.listing l on l.company_id = c.id and l.effective_to is null
    where c.status = 'active' and c.y_industry is not null
    group by c.y_industry
    order by c.y_industry
  `;
  return rows.map((row) => ({ ...row, slug: slugify(row.y_industry) }));
}

// Resolves a URL slug back to the real sector/industry name by matching
// against the live list above, then returns its companies -- rather than
// trying to reverse the slug transform, which isn't guaranteed lossless
// for names with unusual punctuation.
// distinct on (c.id), not upper(l.ticker): found live 2026-09-06 (same
// pass as the count(*) fix above) that a company with more than one
// active listing -- common for SPACs (common + unit + warrant, 3 real
// tickers) -- was appearing once per ticker, i.e. the same company
// listed 2-3 times in a row as if each were a different company. Same
// "prefer Common Stock" tie-break already established for peer
// comparison above (search this file for "security_type = 'Common Stock'").
export async function getCompaniesBySectorSlug(slug: string): Promise<{ sector: string; companies: CompanyDirectoryRow[] } | null> {
  const sectors = await getSectorList();
  const match = sectors.find((row) => row.slug === slug);
  if (!match) return null;
  const companies = await sql<CompanyDirectoryRow[]>`
    with deduped as (
      select distinct on (c.id) l.ticker, coalesce(c.display_name, c.company_name) as company_name, l.exchange, c.sector
      from core.company c
      join core.listing l on l.company_id = c.id and l.effective_to is null
      where c.status = 'active' and c.y_sector = ${match.sector} and ${EQUITY_ONLY_SQL}
      order by c.id, (l.security_type = 'Common Stock') desc nulls last
    )
    select * from deduped order by company_name
  `;
  return { sector: match.sector, companies };
}

export async function getCompaniesByIndustrySlug(slug: string): Promise<{ industry: string; companies: CompanyDirectoryRow[] } | null> {
  const industries = await getIndustryList();
  const match = industries.find((row) => row.slug === slug);
  if (!match) return null;
  const companies = await sql<CompanyDirectoryRow[]>`
    with deduped as (
      select distinct on (c.id) l.ticker, coalesce(c.display_name, c.company_name) as company_name, l.exchange, c.sector
      from core.company c
      join core.listing l on l.company_id = c.id and l.effective_to is null
      where c.status = 'active' and c.y_industry = ${match.y_industry} and ${EQUITY_ONLY_SQL}
      order by c.id, (l.security_type = 'Common Stock') desc nulls last
    )
    select * from deduped order by company_name
  `;
  return { industry: match.y_industry, companies };
}

// Homepage specimen figure (design framework Sec 8.1: "a real, small
// result-table preview"). Real golden-10 data, never fabricated company
// names/values -- same "most recent, TTM-preferred" resolution rule as
// getLatestMetrics, restricted to companies with an active listing so a
// visitor who clicks through always lands on a real page. This is
// illustrative of what a screen looks like, not a recommendation --
// see doc 05's "research, not recommendation" voice rule.
export async function getExampleScreenResults(minRoic = 0.15, limit = 4): Promise<ExampleScreenRow[]> {
  return sql<ExampleScreenRow[]>`
    with ranked as (
      select c.id as company_id, mv.value,
             row_number() over (
               partition by mv.company_id
               order by (mv.period_label = 'TTM') desc, mv.period_end desc
             ) as rn
      from analytics.metric_value mv
      join analytics.metric_definition md on md.id = mv.metric_definition_id
      join core.company c on c.id = mv.company_id
      where md.metric_name = 'roic' and c.status = 'active'
    )
    select l.ticker, c.company_name, r.value::text as roic,
           (
             select mv2.value::text from analytics.metric_value mv2
             join analytics.metric_definition md2 on md2.id = mv2.metric_definition_id
             where mv2.company_id = c.id and md2.metric_name = 'revenue_growth_3y_cagr' and mv2.period_label = 'FY'
             order by mv2.period_end desc limit 1
           ) as revenue_growth_3y_cagr
    from ranked r
    join core.company c on c.id = r.company_id
    join core.listing l on l.company_id = c.id and l.effective_to is null
    where r.rn = 1 and r.value is not null and r.value > ${minRoic} and ${EQUITY_ONLY_SQL}
    order by r.value desc
    limit ${limit}
  `;
}
