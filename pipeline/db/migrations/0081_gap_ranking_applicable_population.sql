-- Gap ranking fixes after the first real gap-report run (2026-09-30).
--
-- 1. Views counted every active company as "should have" every concept, so
--    BDC-only income, dividends and similar ranked first. They now count a
--    gap only for companies in the data point's applicable_population
--    (analytics.data_point_registry / analytics.company_population, built
--    by mapper/coverage_matrix.py).
-- 2. Leads ranked by lift alone were nonsense for sparse concepts
--    (AssetsCurrent "led" BDC income). Leads now carry value evidence: for
--    companies that HAVE the concept and file the candidate tag for the
--    same period, how often the two values agree (the coexistence check,
--    automated). Only evidence-backed leads are stored.

alter table analytics.concept_gap_lead
    add column if not exists coexist_pairs integer,
    add column if not exists agree_rate numeric;

drop view if exists analytics.data_gap_by_concept;
create view analytics.data_gap_by_concept as
with latest_mcap as (
    select distinct on (mv.company_id) mv.company_id, mv.value as market_cap
    from analytics.metric_value mv
    where mv.metric_definition_id = (select id from analytics.metric_definition where metric_name = 'market_cap')
      and mv.value is not null
    order by mv.company_id, mv.period_end desc
),
gaps as (
    select l.canonical_concept_id, l.company_id, l.has_value, r.applicable_population,
           (l.gap_reason is not null or exists (
               select 1 from analytics.company_data_finding f
               where f.company_id = l.company_id
                 and (f.canonical_concept_id = l.canonical_concept_id or f.canonical_concept_id is null)
                 and f.finding_type in ('legitimate_absence', 'data_limit', 'filer_error')
                 and f.status <> 'fixed'
           )) as explained,
           coalesce(m.market_cap, 0) as market_cap
    from analytics.company_concept_lineage l
    join analytics.canonical_concept cc on cc.id = l.canonical_concept_id
    join analytics.data_point_registry r on r.data_point_name = cc.name
    join analytics.company_population cp
      on cp.company_id = l.company_id and cp.population_name = r.applicable_population
    left join latest_mcap m on m.company_id = l.company_id
)
select cc.name as concept,
       g.applicable_population,
       count(*) as applicable_companies,
       count(*) filter (where not g.has_value) as missing,
       count(*) filter (where not g.has_value and g.explained) as missing_explained,
       count(*) filter (where not g.has_value and not g.explained) as missing_unexplained,
       round(100.0 * count(*) filter (where g.has_value) / nullif(count(*), 0), 1) as coverage_pct,
       sum(g.market_cap) filter (where not g.has_value and not g.explained) as unexplained_market_cap,
       (select lib.taxonomy || ':' || lib.tag from analytics.concept_gap_lead gl
          join analytics.sec_tag_library lib on lib.concept_id = gl.concept_id
         where gl.canonical_concept_id = cc.id and gl.rank = 1) as top_lead_tag,
       (select gl.missing_companies_filing from analytics.concept_gap_lead gl
         where gl.canonical_concept_id = cc.id and gl.rank = 1) as top_lead_companies,
       (select gl.agree_rate from analytics.concept_gap_lead gl
         where gl.canonical_concept_id = cc.id and gl.rank = 1) as top_lead_agree_rate
from gaps g
join analytics.canonical_concept cc on cc.id = g.canonical_concept_id
group by cc.id, cc.name, g.applicable_population;

drop view if exists analytics.data_gap_by_metric;
create view analytics.data_gap_by_metric as
select md.metric_name,
       r.applicable_population,
       count(distinct cov.company_id) as applicable_companies,
       count(distinct cov.company_id) filter (where not cov.has_value) as missing,
       count(distinct cov.company_id) filter (where not cov.has_value and cov.gap_reason is null) as missing_unexplained,
       round(100.0 * count(distinct cov.company_id) filter (where cov.has_value)
             / nullif(count(distinct cov.company_id), 0), 1) as coverage_pct,
       (select string_agg(cc.name, ', ' order by cc.name)
          from analytics.metric_definition_input i
          join analytics.canonical_concept cc on cc.id = i.canonical_concept_id
         where i.metric_definition_id = md.id) as input_concepts
from analytics.metric_definition md
join analytics.data_point_registry r on r.data_point_name = md.metric_name
join analytics.company_data_point_coverage cov on cov.data_point_name = md.metric_name
join analytics.company_population cp
  on cp.company_id = cov.company_id and cp.population_name = r.applicable_population
group by md.id, md.metric_name, r.applicable_population;
