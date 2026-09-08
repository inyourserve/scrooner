-- P0 items from doc 45 (2026-09-08): a freshness/staleness check (a
-- genuinely new sanity DIMENSION -- not "is the value right" but "is our
-- data current") and a stock-split discontinuity check (closes a
-- previously-named, unbuilt gap -- doc 21 sec 2, "stock-split... tags
-- still raw/unmapped").
--
-- Both reuse the SAME yfinance .info() payload the Data Sanity Layer
-- already fetches -- zero additional yfinance requests for freshness
-- (info['mostRecentQuarter'] is already in that payload); the split
-- check needs exactly one new, tiny, cheap call (Ticker.splits).
--
-- Same rule as everything else built 2026-09-08: yfinance detects/
-- matches, it is never a value source. A freshness finding has no
-- "value" to fabricate in the first place (it's a date comparison); a
-- split finding, if real, points back at core.fact for the Tag
-- Investigator to trace -- never patches shares_outstanding directly
-- from yfinance's own split ratio.

create table if not exists analytics.data_freshness_check (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    our_latest_period_end date,
    yfinance_most_recent_quarter date,
    days_stale integer,
    severity text not null check (severity in ('ok', 'stale', 'unknown')),
    checked_at timestamptz not null default now(),
    unique (company_id)
);

create index if not exists idx_data_freshness_check_severity on analytics.data_freshness_check (severity) where severity <> 'ok';

create table if not exists analytics.data_split_check (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    split_date date not null,
    split_ratio numeric not null,
    our_shares_before numeric,
    our_shares_after numeric,
    implied_ratio numeric,
    severity text not null check (severity in ('ok', 'discontinuity', 'missing_data')),
    checked_at timestamptz not null default now(),
    unique (company_id, split_date)
);

create index if not exists idx_data_split_check_severity on analytics.data_split_check (severity) where severity <> 'ok';
