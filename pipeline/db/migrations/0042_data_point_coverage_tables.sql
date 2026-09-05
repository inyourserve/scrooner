-- Two-table coverage system (2026-09-05), by direct request: a registry
-- of every data point (concept/metric/ownership section) and the SEC
-- XBRL tag(s) it needs, plus a per-company yes/no coverage table --
-- deliberately simple, no classification/scoring on top.
--
-- Both are derived from data this project already has (concept_mapping,
-- metric_definition_input, canonical_fact, metric_value, the ownership
-- tables) -- population scripts, not a new source of truth.

create table if not exists analytics.data_point_registry (
    id bigserial primary key,
    data_point_name text not null unique,
    data_point_type text not null check (data_point_type in ('concept', 'metric', 'ownership')),
    required_tags text[] not null default '{}',
    source_module text,
    created_at timestamptz not null default now()
);

create table if not exists analytics.company_data_point_coverage (
    id bigserial primary key,
    company_id bigint not null references core.company(id),
    data_point_name text not null references analytics.data_point_registry(data_point_name),
    has_value boolean not null,
    checked_at timestamptz not null default now(),
    unique (company_id, data_point_name)
);

create index if not exists idx_company_data_point_coverage_company on analytics.company_data_point_coverage (company_id);
create index if not exists idx_company_data_point_coverage_point on analytics.company_data_point_coverage (data_point_name, has_value);
