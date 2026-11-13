-- 0126: metric lineage. "Which company uses which calculation", generated and read-only.
-- Written 2026-11-13 (work: metric calculation library). NOT applied: needs the founder's typed words.
-- Number note: main ends at 0123; 0124 (verifier_check) and 0125 (company_tag_map.dims) are claimed in doc 53 and
-- not on main yet, so this file cannot land on main before they do (scripts/check_migrations.py contiguity).
-- ROLLBACK: drop view analytics.v_company_metric_status; drop view analytics.v_company_metric_inputs;
--   alter table analytics.metric_value drop column registry_version, drop column formula_fingerprint;
--
-- 1. Two nullable columns on metric_value (metadata-only add, no rewrite): the formula fingerprint and the
--    REGISTRY_VERSION a value was computed under (scrooner_pipeline.metrics.provenance.value_stamp). Nothing writes them
--    until calculate.py is wired to stamp them; a NULL means "computed before the registry". The metric version itself is
--    already pinned by metric_definition_id -> metric_definition.formula_version.
alter table analytics.metric_value add column if not exists formula_fingerprint text;
alter table analytics.metric_value add column if not exists registry_version text;

comment on column analytics.metric_value.formula_fingerprint is
    'Hash of the formula-relevant registry fields the value was computed under (metrics.provenance.formula_fingerprint). NULL = pre-registry.';
comment on column analytics.metric_value.registry_version is
    'REGISTRY_VERSION (hash of registry/*.csv) at compute time (metrics.provenance.value_stamp). NULL = pre-registry.';

-- 2. Per company x metric x input concept: which company_tag_map rows (tag, statement, era, rule, evidence filing) feed the
--    input, and the latest proof verdict of that input cell. A "_resolved" concept has no tag-map rows of its own; it follows
--    its base concept's rows (lineage_concept). Read-only; filter by company_id.
create or replace view analytics.v_company_metric_inputs as
with inp as (
    select md.id as metric_definition_id, md.metric_name, md.formula_version, mdi.role,
           cc.id as input_concept_id, cc.name as input_concept,
           coalesce(base.id, cc.id) as lineage_concept_id, coalesce(base.name, cc.name) as lineage_concept
    from analytics.metric_definition md
    join analytics.metric_definition_input mdi on mdi.metric_definition_id = md.id
    join analytics.canonical_concept cc on cc.id = mdi.canonical_concept_id
    left join analytics.canonical_concept base on base.name = regexp_replace(cc.name, '_resolved$', '')
    where md.status = 'active'
)
select c.id as company_id, i.metric_name, i.formula_version, i.role, i.input_concept, i.lineage_concept,
       tm.id as tag_map_id, tm.decision, tm.taxonomy, tm.tag, tm.stmt, tm.sign,
       tm.era_from, tm.era_to, tm.rule_id, tm.decided_by, tm.evidence_adsh, tm.evidence_report, tm.evidence_line,
       tm.reason_class, tm.reason,
       case when tm.id is null and i.input_concept <> i.lineage_concept then 'derived_resolved_concept_no_own_map'
            when tm.id is null then 'no_company_tag_map_rows'
            else tm.decision end as feed_status,
       cp.verdict as input_proof_verdict, cp.period_end as input_proof_period_end, cp.rule_id as input_proof_rule_id
from core.company c
cross join inp i
left join analytics.company_tag_map tm
       on tm.company_id = c.id
      and ((tm.canonical_concept_id = i.lineage_concept_id and tm.decision in ('concept', 'not_presented', 'not_in_template'))
        or (tm.parent_concept_id = i.lineage_concept_id and tm.decision = 'component'))
left join lateral (
    select p.verdict, p.period_end, p.rule_id
    from analytics.cell_proof p
    where p.company_id = c.id and p.data_point_name = i.input_concept
    order by p.period_end desc, p.proved_at desc
    limit 1
) cp on true
where c.status = 'active';

comment on view analytics.v_company_metric_inputs is
    'Lineage: per company x metric x input concept, the company_tag_map rows (tag, era, rule_id, evidence filing) feeding it and the latest input proof verdict. Generated, read-only. Filter by company_id.';

-- 3. Per company x metric: computed, or the evidenced reason it is blank, or OUT of the company template.
--    Template = the company's rows at its latest effective_from <= today (company_data_point_template, 0120).
create or replace view analytics.v_company_metric_status as
select c.id as company_id, md.metric_name, md.formula_version,
       case when tpl.in_template is false then 'OUT'
            when lv.id is null then 'NO_ROW'
            when lv.value is not null then 'COMPUTED'
            else 'BLANK' end as status,
       coalesce(case when tpl.in_template is false then tpl.reason end, lv.is_null_reason) as reason,
       tpl.template, lv.period_label, lv.period_end, lv.value as latest_value,
       lv.formula_fingerprint, lv.registry_version
from core.company c
cross join analytics.metric_definition md
left join analytics.company_data_point_template tpl
       on tpl.company_id = c.id and tpl.data_point = md.metric_name
      and tpl.effective_from = (select max(x.effective_from) from analytics.company_data_point_template x
                                where x.company_id = c.id and x.effective_from <= current_date)
left join lateral (
    select v.id, v.value, v.is_null_reason, v.period_label, v.period_end, v.formula_fingerprint, v.registry_version
    from analytics.metric_value v
    where v.company_id = c.id and v.metric_definition_id = md.id
    order by v.period_end desc, v.id desc
    limit 1
) lv on true
where c.status = 'active' and md.status = 'active';

comment on view analytics.v_company_metric_status is
    'Per company x metric: COMPUTED, BLANK with the null reason, OUT of the sector template with its reason, or NO_ROW. Generated, read-only. Filter by company_id.';
