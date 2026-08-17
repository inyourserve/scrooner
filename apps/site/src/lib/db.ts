// Direct Postgres access for Astro (doc 04/17: "Astro... reads approved
// serving views" directly -- no apps/backend dependency for this page,
// since a company page is a static/ISR read, not a dynamic query the
// Python Screener needs to evaluate. Values that are Decimal in Postgres
// come back as strings here (the `postgres` client's default, matching
// this project's Decimal-as-string discipline at every boundary -- see
// doc 04's correctness controls) -- never parsed to a JS float.

import postgres from "postgres";

const sql = postgres(import.meta.env.DATABASE_URL, { max: 5 });

export interface CompanyIdentity {
  id: number;
  cik: string;
  company_name: string;
  sic_code: string | null;
  sic_description: string | null;
  status: string;
  ticker: string | null;
}

export async function getCompanyByTicker(ticker: string): Promise<CompanyIdentity | null> {
  const rows = await sql<CompanyIdentity[]>`
    select c.id, c.cik, c.company_name, c.sic_code, c.sic_description, c.status, l.ticker
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
}

export async function getRecentFilings(companyId: number, limit = 10): Promise<FilingRow[]> {
  return sql<FilingRow[]>`
    select form, filing_date::text, accession_number
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
  accession_number: string;
}

// doc 19 Stage 2 -- core.insider_transaction, Form 4 only (Form 3/5 out of
// scope for this pass, see ownership/insider.py's module docstring).
export async function getRecentInsiderTransactions(companyId: number, limit = 15): Promise<InsiderTransactionRow[]> {
  return sql<InsiderTransactionRow[]>`
    select reporting_owner_name, officer_title, is_director, is_officer, is_ten_percent_owner,
           transaction_date::text, transaction_code, acquired_disposed_code,
           shares::text, price_per_share::text, shares_owned_following::text, accession_number
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
