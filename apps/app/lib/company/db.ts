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
//
// idle_timeout raised 20 -> 90 (2026-09-15): the stock page now has an ISR
// cache in front of it (revalidate=900 in app/stocks/[ticker]/page.tsx), so
// most traffic never reaches this pool at all -- but a cache-miss still pays
// a full TCP+TLS+auth handshake (measured live, this dev machine to Supabase
// us-east-1: ~1.7s+) if the pool's one connection was already closed. 90s
// keeps it alive across the gaps between regenerations without holding a
// connection open indefinitely -- still well under Supabase pooler's ~15
// total-connection ceiling shared across every service (root CLAUDE.md).
const sql = postgres(process.env.DATABASE_URL ?? "postgres://invalid:invalid@127.0.0.1:5432/scrooner", {
  max: 2,
  idle_timeout: 90,
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
  // yfinance's own industry classification -- the exact field peer_companies
  // (below) joins on. Exposed here only for display (e.g. "peers share this
  // industry"), never as a lookup key from this interface.
  y_industry: string | null;
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

export interface MetricHistoryPoint {
  value: string | null;
  period_end: string;
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

// The full active-company directory (~6k rows, ~250KB), for the homepage
// search box to fetch once and match client-side with zero per-keystroke
// network/DB round trip -- the fastest a real-time search box can be,
// since the universe here is small and stable enough (changes at most
// once/day via the pipeline cron) to ship whole rather than query per
// character. Same filters/shape as searchCompanyDirectory, just without
// the prefix predicate.
export async function loadFullCompanyDirectory(): Promise<CompanyDirectoryRow[]> {
  return sql<CompanyDirectoryRow[]>`
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
    order by lower(l.ticker), c.company_name
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
    where c.status = 'active' and c.y_industry is not null and c.y_industry != ''
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
