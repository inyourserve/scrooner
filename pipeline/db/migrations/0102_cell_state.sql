-- cell_state, thin first cut (Data Engineer lane 2; claimed in doc 53 as 0102).
-- FREEZE-REGISTER-2026-10-22 sections 1-2: one row per template cell with a
-- frozen state, a defect class and an owner, keyed by DATES (never by
-- core.period ids or fiscal labels), written under a run id so a scoreboard is
-- reproducible and rollback is a repoint of the active run.
--
-- This migration creates structure only. It reads nothing, backfills nothing and
-- changes no value in any existing table: the three tables start empty. The
-- engine that fills them (reasonless = 0 first cut, then propagation P1-P10)
-- is a later change behind a committed writer.
--
--   analytics.cell_state_run     one row per build; exactly one active run.
--   analytics.cell_state_latest  latest-period cells of a run (FY, Q, TTM, I, TP
--                                grains; v0 writes only basis 'latest').
--   analytics.cell_state_active  view: the rows of the active run (what serving
--                                and the scoreboard read).
--   analytics.defect_register    view: the active run's defect cells.
--   analytics.cell_state_k2      view: K2@2 (unclassified) and the missing-cell
--                                count, i.e. "reasonless" for the active run.
--
-- Frozen vocabularies (change only through a new register version):
--   states         value, derived, evidenced_zero, undefined_by_math,
--                  history_horizon, not_presented, not_in_template, defect
--   defect classes vocabulary, composition, period, ingestion, resolver,
--                  identity, evidence_pending, definition_pending, guard_hidden,
--                  finding_open, filer_error, unclassified
--   owners         data_engineer_l1, data_engineer_l2, period_engineer,
--                  tag_mapper, standardization_lead, accountant, sector_analyst,
--                  verifier, triage, company_master
--
-- evidence_id points at analytics.cell_evidence (migration 0100). It carries no
-- foreign key on purpose: 0100 is applied separately, and the evidence table is
-- append-only and never deleted from, so a dangling id cannot arise by cleanup.
create table if not exists analytics.cell_state_run (
    run_id bigserial primary key,
    created_at timestamptz not null default now(),
    finished_at timestamptz,
    status text not null default 'building'
        check (status in ('building', 'complete', 'failed', 'retired')),
    is_active boolean not null default false,
    data_watermark timestamptz,
    cells_expected integer,
    template_version text,
    definition_version text,
    register_version text,
    git_sha text,
    notes jsonb not null default '{}'::jsonb,
    -- only a complete run may be the active run
    check (not is_active or status = 'complete')
);

create unique index if not exists uq_cell_state_run_one_active
    on analytics.cell_state_run (is_active)
    where is_active;

create table if not exists analytics.cell_state_latest (
    run_id bigint not null
        references analytics.cell_state_run (run_id) on delete cascade,
    company_id bigint not null references core.company (id),
    data_point_name text not null,
    period_grain text not null
        check (period_grain in ('FY', 'Q', 'TTM', 'I', 'TP')),
    period_start date not null,
    period_end date not null,
    basis text not null default 'latest'
        check (basis in ('latest', 'as_filed')),
    state text not null
        check (state in (
            'value', 'derived', 'evidenced_zero', 'undefined_by_math',
            'history_horizon', 'not_presented', 'not_in_template', 'defect'
        )),
    defect_class text
        check (defect_class in (
            'vocabulary', 'composition', 'period', 'ingestion', 'resolver',
            'identity', 'evidence_pending', 'definition_pending', 'guard_hidden',
            'finding_open', 'filer_error', 'unclassified'
        )),
    owner text
        check (owner in (
            'data_engineer_l1', 'data_engineer_l2', 'period_engineer',
            'tag_mapper', 'standardization_lead', 'accountant', 'sector_analyst',
            'verifier', 'triage', 'company_master'
        )),
    rule_id text,
    evidence_id bigint,
    template_version text,
    definition_version text,
    primary key (run_id, company_id, data_point_name, period_grain,
                 period_start, period_end, basis),
    -- a defect always names its class and owner; no other state carries either
    check ((state = 'defect') = (defect_class is not null)),
    check ((state = 'defect') = (owner is not null)),
    -- instants have start = end (register section 2)
    check (period_grain <> 'I' or period_start = period_end),
    check (period_end >= period_start)
);

create index if not exists idx_cell_state_latest_state
    on analytics.cell_state_latest (run_id, state, defect_class);

create index if not exists idx_cell_state_latest_company
    on analytics.cell_state_latest (run_id, company_id);

create or replace view analytics.cell_state_active as
select s.*
from analytics.cell_state_latest s
join analytics.cell_state_run r on r.run_id = s.run_id
where r.is_active;

create or replace view analytics.defect_register as
select s.run_id, s.company_id, s.data_point_name, s.period_grain,
       s.period_start, s.period_end, s.basis, s.defect_class, s.owner,
       s.rule_id, s.evidence_id, s.template_version, s.definition_version
from analytics.cell_state_active s
where s.state = 'defect';

-- K2@2 (data-team/strategy/team/WO-REVIEW-data-triage.md): unclassified cells,
-- plus cells the run was expected to cover but did not write. reasonless is the
-- sum; the Gate C target is 0. A run that does not state cells_expected cannot
-- prove completeness, so cells_missing and reasonless are NULL (unknown), never
-- 0. With no active run the view returns no row.
create or replace view analytics.cell_state_k2 as
select r.run_id,
       r.cells_expected,
       count(s.company_id) as cells_written,
       count(*) filter (
           where s.state = 'defect' and s.defect_class = 'unclassified'
       ) as unclassified,
       case when r.cells_expected is null then null
            else greatest(r.cells_expected - count(s.company_id), 0)
       end as cells_missing,
       case when r.cells_expected is null then null
            else count(*) filter (
                     where s.state = 'defect' and s.defect_class = 'unclassified'
                 ) + greatest(r.cells_expected - count(s.company_id), 0)
       end as reasonless
from analytics.cell_state_run r
left join analytics.cell_state_latest s on s.run_id = r.run_id
where r.is_active
group by r.run_id, r.cells_expected;
