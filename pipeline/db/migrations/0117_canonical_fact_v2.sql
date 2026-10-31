-- canonical_fact_v2: the cell store the cohort is served from (data-team/46-canonical-fact-v2/CELL-FORMAT-v1.md).
-- One row per displayed cell; a blank is a row with value null and a reason. Loaded per company per family
-- (delete + insert), never patched. analytics.canonical_fact is untouched (temporary fallback).
-- NOT applied anywhere yet: written 2026-10-31 by scrooner-8a; the founder/Ritwik apply.
create table if not exists analytics.canonical_fact_v2 (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company (id),
    canonical_concept_id bigint not null references analytics.canonical_concept (id),
    period_id bigint not null references core.period (id),
    basis text not null default 'latest' check (basis in ('latest', 'as_filed')),
    period_grain text not null check (period_grain in ('FY', 'Q', 'I')),
    state text not null check (state in (
        'value', 'derived', 'evidenced_zero', 'undefined_by_math', 'history_horizon',
        'not_presented', 'not_in_template', 'defect')),
    value numeric,
    unit text check (unit in ('USD', 'USD/shares', 'shares', 'pure')),
    decimals integer,
    source_fact_ids bigint[] not null default '{}',
    accession text,
    tag text,
    members jsonb,
    fsn_set text,
    fsn_stmt text check (fsn_stmt in ('IS', 'BS', 'CF', 'EQ', 'CI', 'UN')),
    fsn_line integer,
    derivation jsonb,
    family text not null,
    rule_id text not null check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    rule_run_id uuid references analytics.rule_run (run_id),
    evidence_level text not null check (evidence_level in ('FILING-CHECKED', 'DATA-INFERRED')),
    reason_code text,
    reason_text text,
    defect_class text check (defect_class in (
        'vocabulary', 'composition', 'period', 'ingestion', 'resolver', 'identity',
        'evidence_pending', 'definition_pending', 'guard_hidden', 'finding_open',
        'filer_error', 'unclassified')),
    owner text check (owner in (
        'data_engineer_l1', 'data_engineer_l2', 'period_engineer', 'tag_mapper',
        'standardization_lead', 'accountant', 'sector_analyst', 'verifier',
        'triage', 'company_master')),
    root_cause_class text check (root_cause_class in (
        'vocabulary', 'composition', 'period', 'ingestion', 'resolver', 'identity',
        'evidence_pending', 'definition_pending', 'filer_error', 'unclassified')),
    input_refs jsonb not null default '{}'::jsonb,
    proof_verdict text check (proof_verdict in ('PROVEN', 'DISAGREE', 'NOT_PRESENTED', 'UNCHECKED')),
    proof_reason text,
    proof_run_id uuid,
    cell_file_sha256 text not null,
    loaded_at timestamptz not null default now(),
    check ((state in ('value', 'derived', 'evidenced_zero')) = (value is not null)),
    check (state in ('value', 'derived', 'evidenced_zero') or reason_code is not null),
    check ((state = 'defect') = (defect_class is not null and owner is not null)),
    check (state = 'defect' or (defect_class is null and owner is null and root_cause_class is null)),
    check (state <> 'derived' or derivation is not null),
    unique (company_id, canonical_concept_id, period_id, basis)
);
create index if not exists idx_canonical_fact_v2_concept on analytics.canonical_fact_v2 (canonical_concept_id);
create index if not exists idx_canonical_fact_v2_period on analytics.canonical_fact_v2 (period_id);
create index if not exists idx_canonical_fact_v2_family_company on analytics.canonical_fact_v2 (family, company_id);

-- one setting row: which store the site and the screener read
create table if not exists analytics.serving_switch (
    singleton boolean primary key default true check (singleton),
    store text not null check (store in ('v1', 'v2')),
    changed_at timestamptz not null default now(),
    changed_by text
);
insert into analytics.serving_switch (store, changed_by) values ('v1', 'migration 0117') on conflict do nothing;

-- the only relation apps/backend and the screener read: v1 rows while the switch says v1, v2 cells otherwise.
-- v2: a valued cell is served when its proof is PROVEN or UNCHECKED (founder: UNCHECKED never blanks a screen cell);
-- DISAGREE and every blank state are served as null with their reason.
create or replace view analytics.canonical_fact_served as
select cf.company_id, cf.canonical_concept_id, cf.period_id, 'latest'::text as basis,
       cf.value, cf.source_fact_ids, 'v1'::text as store,
       null::text as state, null::text as reason_code, null::text as reason_text, null::text as proof_verdict
from analytics.canonical_fact cf
where (select store from analytics.serving_switch) = 'v1'
union all
select v.company_id, v.canonical_concept_id, v.period_id, v.basis,
       case when v.state in ('value', 'derived', 'evidenced_zero')
                 and coalesce(v.proof_verdict, 'UNCHECKED') in ('PROVEN', 'UNCHECKED')
            then v.value end as value,
       v.source_fact_ids, 'v2'::text as store,
       v.state,
       case when v.proof_verdict = 'DISAGREE' then coalesce(v.proof_reason, 'proof_disagree') else v.reason_code end as reason_code,
       v.reason_text, v.proof_verdict
from analytics.canonical_fact_v2 v
where (select store from analytics.serving_switch) = 'v2';
