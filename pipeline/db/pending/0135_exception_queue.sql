-- 0135: the single exceptions queue (PIPELINE.md section 4, merge step M5).
-- Today OPEN cells, DISAGREE proofs, census/sample FAILs, NEEDS_READ reads, drill misses and refused resolver refreshes live
-- in separate files. One row per exception, keyed by an idempotency key so a reload never duplicates; work is ranked by
-- cells_affected across all companies, grouped by root_cause_family. Standalone (no foreign keys), new schema object only.
-- Stage 5 items (CENSUS_FAIL, SAMPLE_FAIL, NEEDS_READ) are keyed by ticker + coverage_sha256 + judge version (approver review
-- 2026-11-28), so they carry judge_version; NEEDS_READ rows are owned by the approver.
-- A close needs a rule id AND a test path, or a recorded evidenced hide (hide class AND evidence). "Closing an item without a
-- rule or a test is not a close" (section 4). A reappearing closed item is reopened by the loader (reopened_count + 1).
-- ROLLBACK: drop table ops.exception_queue;

create schema if not exists ops;

create table if not exists ops.exception_queue (
    id                bigint generated always as identity primary key,
    idempotency_key   text        not null,
    kind              text        not null,
    ticker            text,
    cik               text,
    company_id        bigint,
    cell_key          text        not null,
    data_point        text,
    period_end        date,
    root_cause_family text        not null,
    owner_lane        text        not null,
    cells_affected    integer     not null default 1,
    detail            text,
    source_sha        text,
    source_path       text,
    evidence_locator  text,
    judge_version     text,
    opened_at         timestamptz not null default now(),
    last_seen_at      timestamptz not null default now(),
    reopened_count    integer     not null default 0,
    closed_at         timestamptz,
    close_rule_id     text,
    close_test_path   text,
    close_hide_class  text,
    close_evidence    text,
    closed_by         text,
    constraint exception_queue_idempotency_key_uq unique (idempotency_key),
    constraint exception_queue_key_nonblank check (btrim(idempotency_key) <> '' and btrim(cell_key) <> ''
        and btrim(root_cause_family) <> ''),
    constraint exception_queue_kind_ck check (kind in
        ('OPEN', 'DISAGREE', 'CENSUS_FAIL', 'SAMPLE_FAIL', 'NEEDS_READ', 'DRILL_MISS', 'DEAD_LETTER')),
    constraint exception_queue_owner_ck check (owner_lane in
        ('resolver', 'proof', 'verifier', 'tag_expert', 'approver', 'data_engineer')),
    constraint exception_queue_cells_ck check (cells_affected >= 1),
    -- a company-level kind names its company; a drill miss is a class of cells and may name none
    constraint exception_queue_subject_ck check (kind = 'DRILL_MISS'
        or ticker is not null or cik is not null or company_id is not null),
    constraint exception_queue_stage5_judge_ck check (kind not in ('CENSUS_FAIL', 'SAMPLE_FAIL', 'NEEDS_READ')
        or (judge_version is not null and btrim(judge_version) <> '' and source_sha is not null)),
    constraint exception_queue_needs_read_owner_ck check (kind <> 'NEEDS_READ' or owner_lane = 'approver'),
    constraint exception_queue_optional_text_nonblank check (
            (ticker is null or btrim(ticker) <> '') and (cik is null or btrim(cik) <> '')
        and (close_rule_id is null or btrim(close_rule_id) <> '') and (close_test_path is null or btrim(close_test_path) <> '')
        and (close_hide_class is null or btrim(close_hide_class) <> '') and (close_evidence is null or btrim(close_evidence) <> '')),
    -- open: no close fields. closed: a rule id with its test path, or an evidenced hide (class and evidence).
    constraint exception_queue_close_ck check (
        (closed_at is null and close_rule_id is null and close_test_path is null
            and close_hide_class is null and close_evidence is null and closed_by is null)
        or (closed_at is not null and closed_by is not null and (
                (close_rule_id is not null and close_test_path is not null)
             or (close_hide_class is not null and close_evidence is not null))))
);

create index if not exists idx_exception_queue_open_family on ops.exception_queue (root_cause_family, kind) where closed_at is null;
create index if not exists idx_exception_queue_opened_at on ops.exception_queue (opened_at);
create index if not exists idx_exception_queue_closed_at on ops.exception_queue (closed_at) where closed_at is not null;

comment on table ops.exception_queue is
    'PIPELINE.md section 4 exceptions queue (M5). Loader: certification/exception_queue.py. Idempotent on idempotency_key; a close needs rule id + test path or an evidenced hide.';
