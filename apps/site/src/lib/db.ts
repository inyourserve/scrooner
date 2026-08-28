// Direct Postgres access for Astro (doc 04/17: "Astro... reads approved
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
const sql = postgres(import.meta.env.DATABASE_URL, {
  max: 2,
  idle_timeout: 20,
  connect_timeout: 10,
  prepare: false,
});

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
}

export async function getCompanyByTicker(ticker: string): Promise<CompanyIdentity | null> {
  const rows = await sql<CompanyIdentity[]>`
    select c.id, c.cik, c.company_name, c.sic_code, c.sic_description, c.sector, c.status, l.ticker
    from core.company c
    join core.listing l on l.company_id = c.id
    where lower(l.ticker) = lower(${ticker})
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
// direct SQL port rather than a cross-language import, since Astro can't
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
      where mv.company_id = ${companyId}
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
    where cf.company_id = ${companyId} and cc.name = 'public_float'
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
    where cf.company_id = ${companyId} and cc.name = ${conceptName}
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
export async function getRecentInsiderTransactions(companyId: number, limit = 15): Promise<InsiderTransactionRow[]> {
  return sql<InsiderTransactionRow[]>`
    select reporting_owner_name, officer_title, is_director, is_officer, is_ten_percent_owner,
           transaction_date::text, transaction_code, acquired_disposed_code,
           shares::text, price_per_share::text, shares_owned_following::text, is_10b5_1_plan, accession_number
    from core.insider_transaction
    where company_id = ${companyId} and transaction_date is not null
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

interface RawStatementRow {
  statement: string;
  display_order: number;
  display_label: string;
  fiscal_year: number | null;
  fiscal_period: string | null;
  period_end: string | null;
  value: string | null;
}

interface MetricHistoryRow {
  metric_name: string;
  value: string | null;
  period_end: string;
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
  book_value: string | null;
  metric_history: MetricHistoryRow[];
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
  bookValue: string | null;
  metricHistory: Record<string, (string | null)[]>;
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
      select c.id, c.cik, c.company_name, c.sic_code, c.sic_description,
             c.sector, c.status, l.ticker
      from core.company c
      join core.listing l on l.company_id = c.id
      where lower(l.ticker) = lower(${ticker})
      order by (l.effective_to is null) desc
      limit 1
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
    ),
    annual_periods as (
      select distinct period.id, period.end_date
      from analytics.canonical_fact fact
      join core.period period on period.id = fact.period_id
      join selected_company company on company.id = fact.company_id
      where period.fiscal_period = 'FY'
      order by period.end_date desc
      limit 8
    ),
    quarterly_periods as (
      select distinct period.id, period.end_date
      from analytics.canonical_fact fact
      join core.period period on period.id = fact.period_id
      join selected_company company on company.id = fact.company_id
      where period.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4')
      order by period.end_date desc
      limit 8
    ),
    displayed_periods as (
      select id from annual_periods
      union
      select id from quarterly_periods
    ),
    statement_rows as (
      select sl.statement, sl.display_order, sl.display_label,
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
    metric_history_rows as (
      select md.metric_name, mv.value::text as value,
             mv.period_end::text as period_end,
             row_number() over (
               partition by md.metric_name order by mv.period_end desc
             ) as rank
      from analytics.metric_value mv
      join analytics.metric_definition md on md.id = mv.metric_definition_id
      join selected_company company on company.id = mv.company_id
      where md.metric_name in ('roe', 'roic', 'fcf')
        and mv.period_label = 'FY'
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
        'ticker', company.ticker
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
        from statement_rows
      ), '[]'::jsonb) as statements,
      coalesce((
        select jsonb_agg(to_jsonb(recent) order by recent.filing_date desc)
        from (
          select f.form, f.filing_date::text as filing_date,
                 f.accession_number, f.items
          from core.filing f
          where f.company_id = company.id and f.filing_date is not null
          order by f.filing_date desc
          limit 10
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
        where fact.company_id = company.id and concept.name = 'public_float'
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
      (
        select fact.value::text
        from analytics.canonical_fact fact
        join analytics.canonical_concept concept
          on concept.id = fact.canonical_concept_id
        join core.period period on period.id = fact.period_id
        where fact.company_id = company.id
          and concept.name = 'stockholders_equity'
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
      ), '[]'::jsonb) as metric_history
    from selected_company company
  `;

  const row = rows[0];
  if (!row) return null;

  const metricHistory: Record<string, (string | null)[]> = {};
  for (const historyRow of row.metric_history) {
    (metricHistory[historyRow.metric_name] ??= []).push(historyRow.value);
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
    bookValue: row.book_value,
    metricHistory,
  };
}

// doc 19 Stage 4 -- core.institutional_ownership, matched by CUSIP against
// SEC's bulk Form 13F data set (a single recent filing window, not a
// multi-quarter trend -- see ownership/institutional.py's module
// docstring). Deduplicated per filer (preferring an amendment over its
// original, then the latest filing_date) so a manager that filed both an
// original and an amendment in this window doesn't count its position
// twice -- see doc/learnings/form-13f-cusip-crosswalk.md.
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
    select filer_name, shares::text, value_usd::text, filing_date::text
    from (
      select distinct on (filer_name) filer_name, shares, value_usd, filing_date, is_amendment
      from core.institutional_ownership
      where company_id = ${companyId}
      order by filer_name, is_amendment desc, filing_date desc nulls last
    ) dedup
    order by dedup.shares desc nulls last
    limit ${limit}
  `;
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
// exposed, so every suggestion resolves to a real `/stock/{ticker}/` page.
// The browser calls the dedicated cached endpoint only after interaction; this
// query is never part of the consolidated company-page request.
export async function searchCompanyDirectory(query: string, limit = 8): Promise<CompanyDirectoryRow[]> {
  const normalized = query.trim().replace(/\s+/g, " ").toLowerCase().slice(0, 64);
  if (!normalized) return [];

  return sql<CompanyDirectoryRow[]>`
    with candidates as (
      select distinct on (lower(l.ticker))
        l.ticker,
        c.company_name,
        l.exchange,
        c.sector
      from core.company c
      join core.listing l on l.company_id = c.id
      where c.status = 'active'
        and l.effective_to is null
        and l.ticker is not null
        and (
          starts_with(lower(l.ticker), ${normalized})
          or starts_with(lower(c.company_name), ${normalized})
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
      l.ticker, c.company_name, l.exchange, c.sector
    from core.company c
    join core.listing l on l.company_id = c.id
    where c.status = 'active'
      and l.effective_to is null
      and upper(l.ticker) in ${sql(normalized)}
    order by upper(l.ticker), c.company_name
  `;
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
    where r.rn = 1 and r.value is not null and r.value > ${minRoic}
    order by r.value desc
    limit ${limit}
  `;
}
