-- SEC Tag Library (2026-09-27) -- every XBRL tag we have ever stored,
-- every company that files it, and for every (company, canonical concept)
-- the exact tag behind our value. Built by mapper/tag_library.py
-- (`scrooner-map build-tag-library`), rebuilt from core.fact /
-- analytics.canonical_fact / concept_mapping -- never hand-edited.
--
-- Why: concept_tag_candidate (0050-era) only searches curated keywords
-- per concept, and coverage_matrix only says yes/no per company. Neither
-- answers "company X is missing concept Y -- which tags DOES it file?",
-- which is how every real mapping gap so far (Chevron's debt under
-- LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities,
-- Hyatt's segment-only cost of revenue) was eventually found by hand.

-- Layer 1: company x tag (every tag every company files, all companies).
create table if not exists analytics.company_sec_tag (
    company_id bigint not null references core.company(id),
    concept_id bigint not null references core.concept(id),
    fact_count integer not null,
    first_period_end date,
    last_period_end date,
    latest_value numeric,
    latest_period_type text,
    primary key (company_id, concept_id)
);
create index if not exists idx_company_sec_tag_concept on analytics.company_sec_tag (concept_id);

-- Layer 2: tag -> companies -> concepts -> metrics (one row per core.concept).
create table if not exists analytics.sec_tag_library (
    concept_id bigint primary key references core.concept(id),
    taxonomy text not null,
    tag text not null,
    company_count integer not null default 0,
    active_company_count integer not null default 0,
    fact_count bigint not null default 0,
    first_period_end date,
    last_period_end date,
    -- approved | provisional | company_preference | candidate | rejected | unmapped
    mapping_status text not null,
    mapped_concepts text[] not null default '{}',
    candidate_for_concepts text[] not null default '{}',
    feeds_metrics text[] not null default '{}',
    built_at timestamptz not null default now()
);
create index if not exists idx_sec_tag_library_status on analytics.sec_tag_library (mapping_status, active_company_count desc);

-- Layer 3: company x canonical concept -> the tag(s) actually behind our
-- latest value, or (when missing) what the company files instead.
create table if not exists analytics.company_concept_lineage (
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    has_value boolean not null,
    latest_period_end date,
    latest_value numeric,
    source_tags text[] not null default '{}',
    -- tags globally mapped (approved/provisional) to this concept that the company files in ANY period
    mapped_tags_filed text[] not null default '{}',
    -- concept_tag_candidate tags for this concept the company files -- the gap lead when has_value is false
    candidate_tags_filed text[] not null default '{}',
    gap_reason text,
    built_at timestamptz not null default now(),
    primary key (company_id, canonical_concept_id)
);
create index if not exists idx_company_concept_lineage_concept on analytics.company_concept_lineage (canonical_concept_id, has_value);

-- Metric -> company -> concept -> tag, one join away.
create or replace view analytics.metric_company_tag_lineage as
select
    md.metric_name,
    l.company_id,
    cc.name as concept_name,
    i.role as input_role,
    l.has_value as concept_has_value,
    l.latest_period_end,
    l.source_tags,
    l.gap_reason
from analytics.metric_definition md
join analytics.metric_definition_input i on i.metric_definition_id = md.id
join analytics.canonical_concept cc on cc.id = i.canonical_concept_id
join analytics.company_concept_lineage l on l.canonical_concept_id = i.canonical_concept_id;
