-- Gate A foundation F1 (data-team/strategy/FREEZE-REGISTER-2026-10-22.md sections
-- 1, 2, 3.1, 5; WO-REVIEW-data-engineer.md section 2.4, claim in doc 53).
-- ADDITIVE ONLY. Creates empty tables, triggers and indexes. Reads nothing,
-- backfills nothing, changes no existing table. NOT to be applied by the
-- authoring session: scrooner-4d applies it in heavy slot S1 with 0096/0097
-- (lock_timeout 5s is safe: nothing here locks an existing table).
--
-- Why these tables exist (review finding F1): analytics.canonical_fact.value is
-- NOT NULL, so a guard that hides a concept cell can only delete the row, and
-- the blank is then reasonless again. The reason must live in its own store,
-- keyed by DATES (never core.period.id, so a fiscal-label repair or a period
-- rebuild cannot orphan it), scoped to a rule run, and never touched by the
-- stages that delete-then-insert canonical_fact / metric_value.
--
-- Cell key (frozen, register section 2): (company_id, data_point_name,
-- period_grain, period_start, period_end, basis). period_start = period_end
-- for instants. Fiscal labels are attributes, never part of the key.
--
-- Rule IDs (register 3.1): family.rule@N, e.g. source.periodic_form_only@1;
-- certify detectors are namespaced cert.I6.non_periodic_form@1.

-- 1. Rule-run manifest -------------------------------------------------------
-- One row per execution of a rule family (dry run, apply, rollback). Rollback
-- of a stored effect = flag off + recompute of the ciks listed here.
create table if not exists analytics.rule_run (
    run_id uuid primary key default gen_random_uuid(),
    rule_id text not null
        check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    rule_version integer not null check (rule_version >= 1),
    mode text not null check (mode in ('dry_run', 'apply', 'rollback')),
    flag_name text not null,
    flag_state text not null check (flag_state in ('off', 'on')),
    train text,
    ciks text[] not null default '{}',
    git_commit text,
    before_image_ref text,
    stats jsonb not null default '{}'::jsonb,
    started_at timestamptz not null default now(),
    finished_at timestamptz,
    check (rule_id ~ ('@' || rule_version::text || '$'))
);

create index if not exists idx_rule_run_rule on analytics.rule_run (rule_id, started_at desc);

-- 2. Blank reasons ------------------------------------------------------------
-- Why a cell has no value. Only the six non-valued states appear here (value
-- and derived cells have a value, so they need no reason). state = 'defect'
-- carries a defect class and an owner (frozen enums); every other state must
-- leave both null. root_cause_class keeps the underlying mechanism when the
-- class is guard_hidden (RULE-REGISTRY-DRAFT, proposal accepted by the Chief).
create table if not exists analytics.cell_blank_reason (
    id bigint generated always as identity primary key,
    run_id uuid not null references analytics.rule_run (run_id),
    company_id bigint not null references core.company (id),
    data_point_name text not null,
    period_grain text not null check (period_grain in ('FY', 'Q', 'TTM', 'I', 'TP')),
    period_start date not null,
    period_end date not null,
    basis text not null default 'latest' check (basis in ('latest', 'as_filed')),
    state text not null check (state in (
        'evidenced_zero', 'undefined_by_math', 'history_horizon',
        'not_presented', 'not_in_template', 'defect')),
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
    rule_id text not null
        check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    reason_code text not null check (length(reason_code) > 0),
    reason_text text,
    input_refs jsonb not null default '{}'::jsonb,
    source_fact_ids bigint[] not null default '{}',
    created_at timestamptz not null default now(),
    check (period_start <= period_end),
    check (period_grain <> 'I' or period_start = period_end),
    check ((state = 'defect') = (defect_class is not null and owner is not null)),
    check (state = 'defect' or (defect_class is null and owner is null and root_cause_class is null)),
    unique (run_id, company_id, data_point_name, period_grain, period_start, period_end, basis)
);

create index if not exists idx_cell_blank_reason_cell
    on analytics.cell_blank_reason (company_id, data_point_name, period_grain, period_end);
create index if not exists idx_cell_blank_reason_rule
    on analytics.cell_blank_reason (rule_id, run_id);

-- 3. Durable evidence ---------------------------------------------------------
-- Append-only (register section 5). Rebuilds read it and never write it. A
-- wrong row is retired by setting superseded_by exactly once; every other
-- column is immutable; DELETE and TRUNCATE are rejected by trigger.
create table if not exists analytics.cell_evidence (
    evidence_id bigint generated always as identity primary key,
    company_id bigint not null references core.company (id),
    data_point_name text not null,
    period_grain text not null check (period_grain in ('FY', 'Q', 'TTM', 'I', 'TP')),
    period_start date not null,
    period_end date not null,
    basis text not null default 'latest' check (basis in ('latest', 'as_filed')),
    state_claimed text not null check (state_claimed in (
        'value', 'derived', 'evidenced_zero', 'undefined_by_math', 'history_horizon',
        'not_presented', 'not_in_template', 'defect')),
    rule_id text not null
        check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    detector_version text,
    evidence_kind text not null check (evidence_kind in (
        'filing_check', 'detector_audit', 'verifier_sample', 'exception', 'accountant_ruling')),
    accession text,
    locator text,
    source_hash text,
    evidence_level text not null check (evidence_level in ('FILING-CHECKED', 'DATA-INFERRED')),
    recorded_by text not null check (length(recorded_by) > 0),
    recorded_at timestamptz not null default now(),
    superseded_by bigint references analytics.cell_evidence (evidence_id),
    -- sha256 of the JSONL line this row was loaded from (interim file
    -- data-team/strategy/evidence/cell_evidence.jsonl); null for direct inserts.
    import_key text unique,
    check (period_start <= period_end),
    check (period_grain <> 'I' or period_start = period_end),
    -- a filing check without an accession and a locator is not a filing check
    check (evidence_kind <> 'filing_check' or (accession is not null and locator is not null)),
    check (evidence_kind <> 'filing_check' or evidence_level = 'FILING-CHECKED'),
    check (superseded_by is null or superseded_by <> evidence_id)
);

create index if not exists idx_cell_evidence_cell
    on analytics.cell_evidence (company_id, data_point_name, period_grain, period_end)
    where superseded_by is null;
create index if not exists idx_cell_evidence_rule on analytics.cell_evidence (rule_id);

create or replace function analytics.cell_evidence_append_only()
returns trigger language plpgsql as $$
begin
    if tg_op = 'DELETE' then
        raise exception 'analytics.cell_evidence is append-only: DELETE rejected (retire a row with superseded_by)';
    end if;
    if tg_op = 'TRUNCATE' then
        raise exception 'analytics.cell_evidence is append-only: TRUNCATE rejected';
    end if;
    -- UPDATE: only superseded_by may change, only once, null -> value.
    if old.superseded_by is not null then
        raise exception 'analytics.cell_evidence row % is already superseded', old.evidence_id;
    end if;
    if new.superseded_by is null then
        raise exception 'analytics.cell_evidence is append-only: UPDATE must set superseded_by';
    end if;
    if (to_jsonb(new) - 'superseded_by') is distinct from (to_jsonb(old) - 'superseded_by') then
        raise exception 'analytics.cell_evidence is append-only: only superseded_by may change';
    end if;
    return new;
end;
$$;

drop trigger if exists trg_cell_evidence_append_only_row on analytics.cell_evidence;
create trigger trg_cell_evidence_append_only_row
    before update or delete on analytics.cell_evidence
    for each row execute function analytics.cell_evidence_append_only();

drop trigger if exists trg_cell_evidence_append_only_stmt on analytics.cell_evidence;
create trigger trg_cell_evidence_append_only_stmt
    before truncate on analytics.cell_evidence
    for each statement execute function analytics.cell_evidence_append_only();

-- 4. Registrants of a filing --------------------------------------------------
-- core.filing is unique on accession_number and its upsert never updates
-- company_id, so the first CIK normalized claims a shared (combined-filing)
-- accession forever (GATE-A-IDENTITY-REGISTRANT-CHECKS section 3c). This link
-- table records, per accession, every registrant CIK and which one is the
-- primary filer (rule entity.shared_accession_primary_filer@1: the undimensioned
-- dei:EntityCentralIndexKey, cross-checked with the first FILER block of the
-- submission header; disagreement quarantines the whole accession).
create table if not exists core.filing_registrant (
    id bigint generated always as identity primary key,
    accession_number text not null,
    registrant_cik text not null check (registrant_cik ~ '^[0-9]{10}$'),
    company_id bigint references core.company (id),
    role text not null check (role in ('primary', 'co_registrant', 'quarantined')),
    dei_default_cik text check (dei_default_cik ~ '^[0-9]{10}$'),
    header_first_filer_cik text check (header_first_filer_cik ~ '^[0-9]{10}$'),
    filer_count integer not null check (filer_count >= 1),
    quarantine_reason text,
    rule_id text not null default 'entity.shared_accession_primary_filer@1',
    determined_at timestamptz not null default now(),
    unique (accession_number, registrant_cik),
    check ((role = 'quarantined') = (quarantine_reason is not null))
);

-- exactly one primary per accession (a quarantined accession has none)
create unique index if not exists uq_filing_registrant_one_primary
    on core.filing_registrant (accession_number) where role = 'primary';
create index if not exists idx_filing_registrant_company
    on core.filing_registrant (company_id) where company_id is not null;

-- 5. Identity audit -----------------------------------------------------------
-- Every identity edit (display name, status, ticker history, name, primary
-- ticker) is one row with old value, new value and the accession that proves
-- it, so a reverse script can restore the old values exactly. DELETE is
-- rejected; the only update allowed is stamping reversed_at.
create table if not exists core.company_identity_audit (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company (id),
    field text not null check (length(field) > 0),
    old_value text,
    new_value text,
    accession text,
    locator text,
    evidence_level text not null check (evidence_level in ('FILING-CHECKED', 'DATA-INFERRED')),
    rule_id text not null
        check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    run_id uuid references analytics.rule_run (run_id),
    applied_at timestamptz not null default now(),
    reversed_at timestamptz,
    check (old_value is distinct from new_value),
    -- an applied identity edit must cite its filing
    check (evidence_level <> 'FILING-CHECKED' or (accession is not null and locator is not null))
);

create index if not exists idx_company_identity_audit_company
    on core.company_identity_audit (company_id, applied_at desc);

create or replace function core.company_identity_audit_guard()
returns trigger language plpgsql as $$
begin
    if tg_op = 'DELETE' then
        raise exception 'core.company_identity_audit is append-only: DELETE rejected';
    end if;
    if old.reversed_at is not null then
        raise exception 'core.company_identity_audit row % is already reversed', old.id;
    end if;
    if new.reversed_at is null
       or (to_jsonb(new) - 'reversed_at') is distinct from (to_jsonb(old) - 'reversed_at') then
        raise exception 'core.company_identity_audit: only reversed_at may be set';
    end if;
    return new;
end;
$$;

drop trigger if exists trg_company_identity_audit_guard on core.company_identity_audit;
create trigger trg_company_identity_audit_guard
    before update or delete on core.company_identity_audit
    for each row execute function core.company_identity_audit_guard();
