-- Data Sanity Layer (2026-09-08, explicit user request): an independent
-- cross-check of a handful of our own computed values against yfinance
-- (Yahoo Finance), reported continuously (a daily GitHub Actions cron,
-- see .github/workflows/pipeline-sanity.yml) rather than a one-off audit.
--
-- Current-state table (ON CONFLICT (company_id, metric_name) DO UPDATE),
-- not an append-only log -- this answers "what does the sanity layer
-- think RIGHT NOW", the same "current state, not history" shape as
-- core.company.y_industry_status. checked_at drives a rotation: each run
-- picks the coldest-checked companies first, so the whole population
-- gets refreshed over several days rather than hammering yfinance daily
-- for all ~5,200 companies (yfinance has a real, tightening rate limit --
-- see company_master/yfinance_industry.py's own docstring).
create table if not exists analytics.data_sanity_check (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    metric_name text not null,
    our_value numeric,
    external_value numeric,
    external_source text not null default 'yfinance',
    pct_diff numeric,
    severity text not null,
    note text,
    checked_at timestamptz not null default now(),
    unique (company_id, metric_name)
);

create index if not exists idx_data_sanity_check_severity on analytics.data_sanity_check (severity) where severity <> 'ok';
create index if not exists idx_data_sanity_check_checked_at on analytics.data_sanity_check (checked_at);
create index if not exists idx_data_sanity_check_company on analytics.data_sanity_check (company_id);
