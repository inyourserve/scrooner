-- yfinance Full Financial Statements system (2026-09-08, explicit user
-- request): a SEPARATE system from the Data Sanity Layer's `.info()`-based
-- ratio checks -- this one fetches yfinance's actual per-line-item
-- quarterly financial statements (income statement, balance sheet, cash
-- flow) and compares them against our own statement-table values row by
-- row, not just aggregate ratios.
--
-- Three tables, mirroring the "tag mapping" discipline concept_mapping
-- already established, just for a different source (yfinance's own row
-- labels instead of XBRL tags):
--
--   yfinance_statement_line: the raw fetched data, verbatim yfinance row
--     labels, one row per (company, statement, line item, period).
--
--   yfinance_line_item_mapping: the "tag db" equivalent -- which yfinance
--     row label corresponds to which of our own canonical concepts, with
--     the SAME approved/provisional/rejected confidence discipline
--     concept_mapping already uses. Verified live against AAPL (a
--     product company) and JPM (a bank) before seeding -- banks have NO
--     Gross Profit/Cost of Revenue/Operating Income rows at all, and
--     their "Total Revenue" is a yfinance-computed aggregate (net
--     interest income + fee income) that does NOT match our own
--     bank-specific revenue tag (gross interest income alone) -- this is
--     a REAL, sector-wide finding, not a Commerce-Bancshares-only one
--     (see doc/learnings/2026-09-08-yfinance-financials-system.md).
--
--   statement_comparison_finding: the actual per-company, per-period
--     comparison result -- our value, yfinance's value, % diff, severity.
--     Distinct from analytics.data_sanity_check (which only checks the
--     MOST RECENT period for a handful of ratios) -- this checks EVERY
--     available quarter for every mapped statement line.

create table if not exists analytics.yfinance_statement_line (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    statement_type text not null check (statement_type in ('income_statement', 'balance_sheet', 'cash_flow')),
    frequency text not null check (frequency in ('quarterly', 'annual')),
    line_item text not null,
    period_end date not null,
    value numeric,
    fetched_at timestamptz not null default now(),
    unique (company_id, statement_type, frequency, line_item, period_end)
);

create index if not exists idx_yfinance_statement_line_company on analytics.yfinance_statement_line (company_id);
create index if not exists idx_yfinance_statement_line_item on analytics.yfinance_statement_line (statement_type, line_item);

create table if not exists analytics.yfinance_line_item_mapping (
    id bigint generated always as identity primary key,
    statement_type text not null check (statement_type in ('income_statement', 'balance_sheet', 'cash_flow')),
    line_item text not null,
    canonical_concept_id bigint references analytics.canonical_concept(id),
    sign_flip boolean not null default false,
    confidence text not null default 'provisional' check (confidence in ('approved', 'provisional', 'rejected')),
    notes text,
    unique (statement_type, line_item)
);

create table if not exists analytics.statement_comparison_finding (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    period_id bigint references core.period(id),
    period_end date not null,
    our_value numeric,
    yfinance_value numeric,
    yfinance_line_item text not null,
    pct_diff numeric,
    severity text not null,
    note text,
    checked_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id, period_end)
);

create index if not exists idx_statement_comparison_finding_severity on analytics.statement_comparison_finding (severity) where severity <> 'ok';
