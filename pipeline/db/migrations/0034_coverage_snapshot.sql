-- Coverage-score tracking (doc 41, 2026-09-02). A real, persisted daily
-- history of data-point coverage -- not just a point-in-time doc -- so
-- "increase the coverage score over time" is something that can actually
-- be queried as a trend, not eyeballed from separately-dated doc entries.
--
-- One row per (snapshot_date, item_type, item_name): item_type is
-- 'concept' (one row per analytics.canonical_concept, tag-level coverage),
-- 'metric' (one row per active analytics.metric_definition, product-facing
-- coverage), or 'score' (exactly 2 rows per snapshot: avg_metric_coverage
-- and avg_concept_coverage -- see mapper/coverage_snapshot.py for the
-- formula). Reruns on the same day overwrite that day's row (unique key
-- below), so this is safe to run more than once without duplicating.

create table if not exists analytics.coverage_snapshot (
    id bigserial primary key,
    snapshot_date date not null,
    item_type text not null check (item_type in ('concept', 'metric', 'score')),
    item_name text not null,
    companies_covered integer not null,
    total_active_companies integer not null,
    coverage_pct numeric(5, 2) not null,
    created_at timestamptz not null default now(),
    unique (snapshot_date, item_type, item_name)
);

create index if not exists idx_coverage_snapshot_item on analytics.coverage_snapshot (item_type, item_name, snapshot_date);
