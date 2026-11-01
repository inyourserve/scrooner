-- Per-company sector template (founder ruling 2026-11-01, doc 02: "sector templates and 100% coverage").
-- A data point is a cell for a company only if that company's current template includes it; coverage is
-- valued cells / template cells (mapper/coverage_snapshot.py). Seeded by `scrooner-map seed-sector-templates`
-- from data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md (sector default plus company overrides).
-- A company's CURRENT template is every row at its latest effective_from <= the as-of date: each seed writes the
-- company's full set, so a field dropped in a later version disappears instead of leaving a stale row.
-- Written 2026-11-01 (work/data-engineer/sector-templates); NOT applied; applying it needs the founder's typed words.
create table if not exists analytics.company_data_point_template (
    company_id        bigint  not null references core.company (id),
    data_point        text    not null check (btrim(data_point) <> ''),
    in_template       boolean not null,
    reason            text,
    effective_from    date    not null,
    template          text    not null check (btrim(template) <> ''),
    source            text    not null check (source in ('sector_default', 'company_override')),
    template_version  text    not null check (btrim(template_version) <> ''),
    seeded_at         timestamptz not null default now(),
    primary key (company_id, data_point, effective_from),
    -- An excluded field and every company override must say why.
    constraint company_data_point_template_reason_required check (
        (in_template and source = 'sector_default') or coalesce(btrim(reason), '') <> ''
    )
);

create index if not exists idx_company_data_point_template_effective
    on analytics.company_data_point_template (company_id, effective_from);

comment on table analytics.company_data_point_template is
    'Per-company sector template (doc 02 ruling 2026-11-01). Current template = rows at the company''s latest effective_from <= as-of. Seeded only by seed-sector-templates.';
comment on column analytics.company_data_point_template.data_point is
    'canonical_concept.name or metric_definition.metric_name; the seeder rejects any other name.';
comment on column analytics.company_data_point_template.reason is
    'Required when in_template is false and for every company override.';
