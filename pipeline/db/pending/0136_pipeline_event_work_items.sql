-- 0136: pipeline orchestration state (PIPELINE.md section 3, merge step M4): event log, work items, per-stage
-- checkpoints, dead letters, certify requests, served versions. Claimed in doc 53 (0135 is M5's exceptions queue).
-- NOT applied: needs the founder's typed words (doc 53, "Applying a migration").
-- Why: top100_flow dispatch and the nightly reprocess were driven by hand-typed company lists and schedules, so a crash
-- lost the list, a rerun redid finished stages, and nothing said which companies a rule change touched.
-- Idempotence: an event is unique on (cik, cause, versions_hash), so a producer that fires twice collapses to one row;
-- a work item is unique on (cik, versions_hash) once done, and at most one queued and one running item exist per company.
-- versions_hash is sha256 of the canonical JSON (sorted keys, compact separators), computed by the producer
-- (scrooner_pipeline.orchestrator.store.versions_hash); the CHECK only enforces its shape.
-- Stage numbers follow PIPELINE.md: 1 ingest, 2 know, 3 resolve, 4 prove, 5 certify, 6 serve. A worker runs them in the
-- order 1,2,3,4,6,5. Stage 5 only files a row in ops.certify_request; no table here holds a verdict, a registry row or a
-- certificate (the approver records those).
-- ROLLBACK: drop table ops.certify_request, ops.company_served_version, ops.work_dead_letter, ops.work_item_stage,
--   ops.work_item_event, ops.work_item, ops.pipeline_event;  (nothing else references them; drop schema ops only if empty)
create schema if not exists ops;

create table if not exists ops.pipeline_event (
    id           bigint generated always as identity primary key,
    -- '*' = not company-scoped; the planner expands it through the rule store's usage index (rule_version, template_change only)
    cik          text not null check (cik = '*' or cik ~ '^[0-9]{1,10}$'),
    cause        text not null check (cause in ('new_filing', 'rule_version', 'rank_change', 'template_change')),
    versions     jsonb not null check (jsonb_typeof(versions) = 'object'),
    versions_hash text not null check (versions_hash ~ '^[0-9a-f]{64}$'),
    source       text not null check (btrim(source) <> ''),
    occurred_at  timestamptz not null default now(),
    planned_at   timestamptz,
    plan_outcome text check (plan_outcome in ('queued', 'merged', 'already_done', 'no_companies', 'unscoped', 'blocked_on_ingest', 'blocked_on_resolver')),
    constraint pipeline_event_idempotent unique (cik, cause, versions_hash),
    constraint pipeline_event_star_scope check (cik <> '*' or cause in ('rule_version', 'template_change')),
    constraint pipeline_event_planned_pair check ((planned_at is null) = (plan_outcome is null))
);
create index if not exists idx_pipeline_event_unplanned on ops.pipeline_event (id) where planned_at is null;

create table if not exists ops.work_item (
    id             bigint generated always as identity primary key,
    cik            text not null check (cik ~ '^[0-9]{1,10}$'),
    from_stage     smallint not null check (from_stage between 1 and 6),
    causes         text[] not null,
    versions       jsonb not null check (jsonb_typeof(versions) = 'object'),
    versions_hash  text not null check (versions_hash ~ '^[0-9a-f]{64}$'),
    -- a dry-run item runs the stage commands without their write flags; it never counts as served
    dry_run        boolean not null default false,
    -- blocked_on_resolver: it has filings but no resolver file yet (the resolver-data-refresh batch makes it); same rule: a wait, never a dead letter.
    -- blocked_on_ingest: the company has no fsn.filing row yet (a stage 3+ item cannot run); the planner unblocks it when
    -- filings appear. It is NOT a failure and never a dead letter (scrooner-36, M6-PREP: 3,315 of ranks 1,001-5,000 have none)
    status         text not null default 'pending' check (status in ('pending', 'running', 'retry_wait', 'done', 'dead', 'blocked_on_ingest', 'blocked_on_resolver')),
    attempts       integer not null default 0 check (attempts >= 0),
    next_attempt_at timestamptz not null default now(),
    locked_by      text,
    lease_expires_at timestamptz,
    last_error     text,
    error_class    text,
    created_at     timestamptz not null default now(),
    updated_at     timestamptz not null default now(),
    finished_at    timestamptz,
    constraint work_item_running_has_lease check (status <> 'running' or (locked_by is not null and lease_expires_at is not null))
);
create unique index if not exists work_item_one_queued_per_cik on ops.work_item (cik, dry_run) where status in ('pending', 'retry_wait', 'blocked_on_ingest', 'blocked_on_resolver');
create unique index if not exists work_item_one_running_per_cik on ops.work_item (cik) where status = 'running';
create unique index if not exists work_item_done_once on ops.work_item (cik, versions_hash) where status = 'done' and not dry_run;
create index if not exists idx_work_item_claim on ops.work_item (status, next_attempt_at, id);

create table if not exists ops.work_item_event (
    work_item_id bigint not null references ops.work_item (id) on delete cascade,
    event_id     bigint not null references ops.pipeline_event (id),
    primary key (work_item_id, event_id)
);

-- One row per finished stage of a work item: the checkpoint a crashed worker resumes from. Written in the same
-- transaction as the lease extension (and, for the last stage, the item's done status and the served versions).
create table if not exists ops.work_item_stage (
    work_item_id bigint not null references ops.work_item (id) on delete cascade,
    stage        smallint not null check (stage between 1 and 6),
    stage_name   text not null,
    status       text not null check (status in ('done', 'skipped')),
    attempt      integer not null check (attempt >= 0),
    detail       jsonb not null default '{}'::jsonb,
    finished_at  timestamptz not null default now(),
    primary key (work_item_id, stage)
);

create table if not exists ops.work_dead_letter (
    id           bigint generated always as identity primary key,
    work_item_id bigint not null unique references ops.work_item (id),
    cik          text not null,
    stage        smallint check (stage between 1 and 6),
    error_class  text not null check (btrim(error_class) <> ''),
    error        text not null,
    attempts     integer not null,
    owner        text,
    created_at   timestamptz not null default now(),
    reported_at  timestamptz,
    resolved_at  timestamptz,
    resolution   text
);
create index if not exists idx_work_dead_letter_open on ops.work_dead_letter (created_at) where resolved_at is null;

-- The versions a company's cells were last produced under (the versions the worker's code and rules were at when the
-- item finished; a dry run never writes here). The daily sweep plans every company whose row differs from current.
create table if not exists ops.company_served_version (
    cik           text primary key check (cik ~ '^[0-9]{1,10}$'),
    versions      jsonb not null,
    versions_hash text not null check (versions_hash ~ '^[0-9a-f]{64}$'),
    work_item_id  bigint not null references ops.work_item (id),
    served_at     timestamptz not null default now()
);

-- Stage 5 output of a worker: a REQUEST for the approver, never a verdict. Key = ticker + coverage_sha256 + judge
-- version (PIPELINE.md stage 5), so a re-run on the same coverage files the same request once.
create table if not exists ops.certify_request (
    id              bigint generated always as identity primary key,
    work_item_id    bigint not null references ops.work_item (id),
    ticker          text not null check (btrim(ticker) <> ''),
    coverage_sha256 text not null check (coverage_sha256 ~ '^[0-9a-f]{64}$'),
    judge_version   text not null check (btrim(judge_version) <> ''),
    request_path    text,
    filed_at        timestamptz not null default now(),
    constraint certify_request_key unique (ticker, coverage_sha256, judge_version)
);

do $$
declare t text;
begin
    foreach t in array array['pipeline_event', 'work_item', 'work_item_event', 'work_item_stage', 'work_dead_letter', 'company_served_version', 'certify_request'] loop
        execute format('alter table ops.%I enable row level security', t);
    end loop;
    if exists (select 1 from pg_roles where rolname = 'anon') then
        execute 'revoke all on schema ops from anon';
        execute 'revoke all on all tables in schema ops from anon';
    end if;
    if exists (select 1 from pg_roles where rolname = 'authenticated') then
        execute 'revoke all on schema ops from authenticated';
        execute 'revoke all on all tables in schema ops from authenticated';
    end if;
end
$$;
