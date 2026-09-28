-- Data truth layer (2026-09-29) -- the database, not docs, holds what we have
-- learned about every tag and every gap. Founder direction: the tag library
-- must stay current, every finding must be recorded in the DB, and it must
-- rank the biggest gaps (by tag, company, metric) so fixes are planned from
-- it. Built/refreshed by mapper/tag_library.py; read via the views below.

-- 1. Verdict per (tag, canonical concept): what we decided and why. Rows
--    from concept_mapping are mirrored automatically (source='concept_mapping');
--    investigation findings are recorded by hand or by code
--    (source='investigation'). gap_tags() never re-proposes a tag whose
--    verdict is rejected / different_concept / partial_component.
create table if not exists analytics.tag_concept_verdict (
    id bigint generated always as identity primary key,
    taxonomy text not null,
    tag text not null,
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    verdict text not null check (verdict in (
        'approved',            -- mapped, trusted
        'needs_review',        -- plausible lead, not yet coexistence-tested
        'rejected',            -- tested and wrong for this concept
        'different_concept',   -- shares vocabulary, measures something else
        'partial_component'    -- a real piece of the concept, never the whole
    )),
    reason text not null,
    evidence jsonb,
    source text not null check (source in ('concept_mapping', 'investigation')),
    decided_at timestamptz not null default now(),
    unique (taxonomy, tag, canonical_concept_id)
);

-- 2. Findings per company (and optionally per concept): bugs, filer errors,
--    legitimate absences. status tracks whether the finding is still true.
create table if not exists analytics.company_data_finding (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint references analytics.canonical_concept(id),
    finding_type text not null check (finding_type in (
        'pipeline_bug',        -- our code is wrong
        'filer_error',         -- the company's own XBRL is wrong
        'legitimate_absence',  -- the value genuinely does not exist
        'data_limit'           -- exists, but not reachable from our sources
    )),
    status text not null default 'open' check (status in ('open', 'fixed', 'wont_fix')),
    summary text not null,
    evidence jsonb,
    found_at timestamptz not null default now(),
    resolved_at timestamptz,
    -- nulls not distinct: a company-level finding (no concept) must still dedupe
    unique nulls not distinct (company_id, canonical_concept_id, summary)
);
create index if not exists idx_company_data_finding_open on analytics.company_data_finding (status, company_id);

-- 3. Best unmapped tag leads per concept, from companies missing it.
--    Rebuilt with the library (a 2M-row aggregate, too heavy for a view).
create table if not exists analytics.concept_gap_lead (
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    concept_id bigint not null references core.concept(id),
    missing_companies_filing integer not null,
    missing_market_cap numeric,
    rank integer not null,
    built_at timestamptz not null default now(),
    primary key (canonical_concept_id, concept_id)
);

-- 4. Gap ranking by concept: how many active companies lack it, how many of
--    those have a recorded reason, and how much market cap sits in the
--    unexplained part -- the order to fix things in.
create or replace view analytics.data_gap_by_concept as
with latest_mcap as (
    select distinct on (mv.company_id) mv.company_id, mv.value as market_cap
    from analytics.metric_value mv
    where mv.metric_definition_id = (select id from analytics.metric_definition where metric_name = 'market_cap')
      and mv.value is not null
    order by mv.company_id, mv.period_end desc
),
gaps as (
    select l.canonical_concept_id, l.company_id, l.has_value,
           (l.gap_reason is not null or exists (
               select 1 from analytics.company_data_finding f
               where f.company_id = l.company_id
                 and (f.canonical_concept_id = l.canonical_concept_id or f.canonical_concept_id is null)
                 and f.finding_type in ('legitimate_absence', 'data_limit', 'filer_error')
                 and f.status <> 'fixed'
           )) as explained,
           coalesce(m.market_cap, 0) as market_cap
    from analytics.company_concept_lineage l
    join core.company co on co.id = l.company_id and co.status = 'active'
    left join latest_mcap m on m.company_id = l.company_id
)
select cc.name as concept,
       count(*) as active_companies,
       count(*) filter (where not g.has_value) as missing,
       count(*) filter (where not g.has_value and g.explained) as missing_explained,
       count(*) filter (where not g.has_value and not g.explained) as missing_unexplained,
       round(100.0 * count(*) filter (where g.has_value) / nullif(count(*), 0), 1) as coverage_pct,
       sum(g.market_cap) filter (where not g.has_value and not g.explained) as unexplained_market_cap,
       (select lib.taxonomy || ':' || lib.tag from analytics.concept_gap_lead gl
          join analytics.sec_tag_library lib on lib.concept_id = gl.concept_id
         where gl.canonical_concept_id = cc.id and gl.rank = 1) as top_lead_tag,
       (select gl.missing_companies_filing from analytics.concept_gap_lead gl
         where gl.canonical_concept_id = cc.id and gl.rank = 1) as top_lead_companies
from gaps g
join analytics.canonical_concept cc on cc.id = g.canonical_concept_id
group by cc.id, cc.name;

-- 5. Gap ranking by metric: a metric is only as complete as its inputs.
create or replace view analytics.data_gap_by_metric as
select md.metric_name,
       count(distinct cov.company_id) as active_companies,
       count(distinct cov.company_id) filter (where not cov.has_value) as missing,
       count(distinct cov.company_id) filter (where not cov.has_value and cov.gap_reason is null) as missing_unexplained,
       round(100.0 * count(distinct cov.company_id) filter (where cov.has_value)
             / nullif(count(distinct cov.company_id), 0), 1) as coverage_pct,
       (select string_agg(cc.name, ', ' order by cc.name)
          from analytics.metric_definition_input i
          join analytics.canonical_concept cc on cc.id = i.canonical_concept_id
         where i.metric_definition_id = md.id) as input_concepts
from analytics.metric_definition md
join analytics.company_data_point_coverage cov on cov.data_point_name = md.metric_name
join core.company co on co.id = cov.company_id and co.status = 'active'
group by md.id, md.metric_name;

-- 6. Gap ranking by company: which companies (weighted by size) are missing
--    the most core data a user would see first.
create or replace view analytics.data_gap_by_company as
with core_concepts as (
    select id from analytics.canonical_concept where name in (
        'revenue_sanity_resolved', 'net_income_resolved', 'operating_income_resolved',
        'total_assets', 'stockholders_equity', 'cfo', 'capex', 'total_debt_resolved',
        'cash_and_equivalents', 'shares_outstanding')
)
select co.id as company_id, co.primary_ticker, coalesce(co.display_name, co.company_name) as company_name,
       (select mv.value from analytics.metric_value mv
         where mv.company_id = co.id and mv.value is not null
           and mv.metric_definition_id = (select id from analytics.metric_definition where metric_name = 'market_cap')
         order by mv.period_end desc limit 1) as market_cap,
       count(*) filter (where not l.has_value) as core_concepts_missing,
       count(*) filter (where not l.has_value and l.gap_reason is null) as core_concepts_unexplained,
       string_agg(cc.name, ', ' order by cc.name) filter (where not l.has_value) as missing_concepts,
       (select count(*) from analytics.company_data_finding f where f.company_id = co.id and f.status = 'open') as open_findings
from core.company co
join analytics.company_concept_lineage l on l.company_id = co.id and l.canonical_concept_id in (select id from core_concepts)
join analytics.canonical_concept cc on cc.id = l.canonical_concept_id
where co.status = 'active'
group by co.id;
