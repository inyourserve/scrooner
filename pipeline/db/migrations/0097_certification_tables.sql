-- Top-1000 certification program (data-team/34), P1: output tables of the
-- invariant suite (`scrooner-certify`, pipeline/src/scrooner_pipeline/certification/).
--
-- certification_finding: one row per invariant violation found by code for a
-- company's stored value (cell, rule, both values, evidence). severity
-- 'wrong_value' blocks certification; 'review' needs a human or the Verifier.
-- The suite rewrites a company's OPEN findings on each run (delete-then-insert,
-- one transaction per chunk); rows with resolved_at set are kept as history.
--
-- company_certification: one row per company, the state ladder of data-team/34
-- (uncertified -> checks_clean -> reconciled -> verified -> certified). The
-- suite only moves a company between uncertified and checks_clean; the later
-- states are written by the reconciliation job and the Verifier.
--
-- Reads nothing, backfills nothing: the tables start empty.
create table if not exists analytics.certification_finding (
    id bigserial primary key,
    company_id bigint not null references core.company (id),
    invariant text not null
        check (invariant ~ '^I[0-9]+$'),
    severity text not null check (severity in ('wrong_value', 'review')),
    data_point_name text not null,
    period_end date,
    stored_value numeric,
    expected_or_other_value numeric,
    evidence jsonb not null default '{}'::jsonb,
    source_fact_ids bigint[] not null default '{}',
    found_at timestamptz not null default now(),
    resolved_at timestamptz,
    -- Rule-registry / run provenance (nullable, additive; amended 2026-10-22
    -- before 0097 was applied).
    rule_id text,
    rule_version integer,
    suite_version text,
    certify_run_id text,
    suite_run_at timestamptz
);

create index if not exists idx_certification_finding_company_open
    on analytics.certification_finding (company_id)
    where resolved_at is null;

create index if not exists idx_certification_finding_invariant
    on analytics.certification_finding (invariant, severity)
    where resolved_at is null;

create table if not exists analytics.company_certification (
    company_id bigint primary key references core.company (id),
    state text not null default 'uncertified'
        check (state in ('uncertified', 'checks_clean', 'reconciled', 'verified', 'certified')),
    checks_run_at timestamptz,
    open_findings integer not null default 0,
    reconciled_at timestamptz,
    verified_at timestamptz,
    certified_at timestamptz
);
