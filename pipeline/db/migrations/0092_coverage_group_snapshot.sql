-- Grouped coverage history: the same daily snapshot discipline as
-- analytics.coverage_snapshot (0034), cut by company rank band (market
-- cap, revenue fallback) and by sector, so "can we launch with the top
-- 1,000-2,000 companies" is a trend that can be queried, not a one-off.
--
-- Raw lens: denominator is every active company in the group, no
-- structural-gap exclusions. metric_name '__summary__' rows carry the
-- per-group distribution (avg per-company core score, % >=90, % <60).
create table if not exists analytics.coverage_group_snapshot (
    id bigserial primary key,
    snapshot_date date not null,
    group_type text not null check (group_type in ('rank_band', 'sector_all', 'sector_top1000', 'sector_top2000')),
    group_key text not null,
    metric_name text not null,
    companies integer not null,
    covered integer not null,
    coverage_pct numeric(5, 2) not null,
    pct_ge90 numeric(5, 2),
    pct_lt60 numeric(5, 2),
    created_at timestamptz not null default now(),
    unique (snapshot_date, group_type, group_key, metric_name)
);

create index if not exists idx_coverage_group_snapshot_lookup
    on analytics.coverage_group_snapshot (group_type, group_key, metric_name, snapshot_date);
