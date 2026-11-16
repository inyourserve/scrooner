-- 0128: company x tag x metric library on the new system (founder direction via Dhairya, 2026-11-16).
-- NOT applied: needs the founder's typed words. Rows are loaded by `scrooner-map rebuild-company-tag-library`
-- (workflow pipeline-tag-library-rebuild.yml), never by hand.
-- Number note: main ends at 0123; 0124-0127 are claimed in doc 53 (0126 and 0127 sit in pipeline/db/pending/ because
-- 0124 and 0125 are not on main), so this file also sits in pending/ and moves to migrations/ once 0124-0127 land
-- (scripts/check_migrations.py contiguity). The view needs no object from 0124-0127.
-- ROLLBACK: drop view analytics.company_tag_metric; drop table analytics.tag_library_entry;
--   drop table analytics.resolver_decision;  (nothing else references them)
--
-- Why new tables and not new columns on analytics.sec_tag_library: that table is one row per core.concept (tag only,
-- no statement, no data point) and `scrooner-map build-tag-library` runs `delete from analytics.sec_tag_library` every
-- week, which would wipe any column added here. The old tables (sec_tag_library, company_sec_tag, tag_concept_verdict,
-- company_tag_preference) are left untouched; they describe the retired concept_mapping.

-- 1. One row per (taxonomy, tag, statement, data point, role): what the tag is in the new system.
--    role = company_tag_map.decision (concept, component, excluded, combined). data_point = canonical concept base name
--    ('' for excluded). rule_ids = the company_tag_map rules that wrote it (docmap@1, docmap_fix@1, structural@1,
--    era_extend@1, ...); library_rule_id = the Tag Expert's rule in data-team/tags/rules/*.csv.
--    proven_cells / certified_cells / disagree_cells / unchecked_cells: latest cell_proof verdict per cell, counted at the
--    tag the structure selected (position_tag, fsn_stmt); certified = PROVEN cells of companies with an approver
--    certificate. deprecated_by / replaces: from the FASB taxonomy ingest (data-team/tags/taxonomy/deprecations.csv),
--    NULL while that file is not on main. known_problems: library caveats, rule notes, library-vs-map conflicts, DISAGREE.
create table if not exists analytics.tag_library_entry (
    taxonomy          text   not null,
    tag               text   not null check (btrim(tag) <> ''),
    stmt              text   not null,
    data_point        text   not null default '',
    role              text   not null check (role in ('concept', 'component', 'combined', 'excluded')),
    concept           text   not null default '',
    rule_ids          text[] not null default '{}',
    library_rule_id   text,
    library_decision  text,
    reason_class      text,
    polarity          text   check (polarity is null or polarity in ('positive', 'signed', 'raw')),
    family            text,
    deprecated_by     text,
    replaces          text,
    companies_mapped  integer not null default 0 check (companies_mapped >= 0),
    rows_mapped       integer not null default 0 check (rows_mapped >= 0),
    proven_cells      bigint  not null default 0 check (proven_cells >= 0),
    certified_cells   bigint  not null default 0 check (certified_cells >= 0),
    disagree_cells    bigint  not null default 0 check (disagree_cells >= 0),
    unchecked_cells   bigint  not null default 0 check (unchecked_cells >= 0),
    known_problems    text[]  not null default '{}',
    last_verified     date,
    content_hash      text    not null,
    built_at          timestamptz not null default now(),
    primary key (taxonomy, tag, stmt, data_point, role),
    check (certified_cells <= proven_cells)
);
create index if not exists idx_tag_library_entry_data_point on analytics.tag_library_entry (data_point, role);
create index if not exists idx_tag_library_entry_tag on analytics.tag_library_entry (tag);

comment on table analytics.tag_library_entry is
    'Tag library on the new system, rebuilt from company_tag_map, the resolver output, cell_proof and the Tag Expert files by scrooner-map rebuild-company-tag-library. Repo files are the reviewed source; this is the queryable copy.';

-- 2. The structural resolver's decision per company x data point x period (newest resolver-all110-*.csv).
--    node_tags = the tags its evidence nodes name. value is the filer-unit decimal (numeric, never float).
create table if not exists analytics.resolver_decision (
    company_id        bigint not null references core.company (id),
    cik               text   not null,
    ticker            text,
    data_point        text   not null,
    period_end        date   not null,
    grain             text   not null check (grain in ('FY', 'I')),
    decision          text   not null check (decision in ('mapped', 'component_sum', 'derived_not_printed',
                                                         'combined', 'not_presented', 'no_role')),
    node_tags         text[] not null default '{}',
    nodes             text,
    value             numeric,
    accession         text,
    column_kind       text,
    calc_check        text,
    flags             text,
    resolver_version  text,
    source_file       text   not null,
    content_hash      text   not null,
    loaded_at         timestamptz not null default now(),
    primary key (company_id, data_point, period_end, grain)
);
create index if not exists idx_resolver_decision_company_dp on analytics.resolver_decision (company_id, data_point, period_end desc);

comment on table analytics.resolver_decision is
    'Structural resolver output (data-team/tags/line_map/resolver-all110-*.csv), one row per company x data point x period; loaded by scrooner-map rebuild-company-tag-library.';

-- 3. company x tag -> data point -> metric in one query. One row per company_tag_map row x metric that takes the row's
--    data point as an input (a data point that feeds no metric keeps one row with metric_name NULL). Tagless decisions
--    (not_presented, not_in_template) are not here: they have no tag (see v_company_metric_inputs, 0126).
--    The resolver columns are the NEWEST resolver cell of that company x data point (any period); resolver_names_tag
--    says whether that cell's evidence nodes name this tag. Filter by company_id for interactive use.
create or replace view analytics.company_tag_metric as
select tm.company_id,
       tm.taxonomy, tm.tag, tm.stmt,
       tm.decision as role,
       dp.data_point,
       tm.sign, tm.era_from, tm.era_to, tm.rule_id, tm.decided_by,
       tm.evidence_adsh, tm.evidence_report, tm.evidence_line,
       rd.decision as resolver_decision,
       rd.period_end as resolver_period_end,
       rd.accession as resolver_accession,
       rd.resolver_version,
       (tm.tag = any (rd.node_tags)) as resolver_names_tag,
       md.metric_name, md.formula_version, mdi.role as metric_input_role,
       tl.polarity, tl.family, tl.proven_cells, tl.certified_cells, tl.last_verified
from analytics.company_tag_map tm
join analytics.canonical_concept cc
  on cc.id = case when tm.decision = 'component' then tm.parent_concept_id else tm.canonical_concept_id end
cross join lateral (select regexp_replace(cc.name, '_resolved$', '') as data_point) dp
left join lateral (
    select r.decision, r.period_end, r.accession, r.resolver_version, r.node_tags
    from analytics.resolver_decision r
    where r.company_id = tm.company_id and r.data_point = dp.data_point
    order by r.period_end desc, r.grain
    limit 1
) rd on true
left join (analytics.metric_definition_input mdi
           join analytics.canonical_concept ci on ci.id = mdi.canonical_concept_id
           join analytics.metric_definition md on md.id = mdi.metric_definition_id and md.status = 'active')
       on regexp_replace(ci.name, '_resolved$', '') = dp.data_point
left join analytics.tag_library_entry tl
       on tl.taxonomy = coalesce(tm.taxonomy, 'us-gaap') and tl.tag = tm.tag and tl.stmt = tm.stmt
      and tl.data_point = dp.data_point and tl.role = tm.decision
where tm.tag is not null;

comment on view analytics.company_tag_metric is
    'company x tag -> data point -> metric: company_tag_map rows with the newest resolver decision for the data point and every active metric that takes it as an input. Read-only. Filter by company_id.';
