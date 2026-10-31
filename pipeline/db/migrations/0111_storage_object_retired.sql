-- Storage reduction (data-team/strategy/team/STORAGE-DELETE-DRYRUN-2026-10-25.md,
-- founder-approved Rule S, 2026-10-25). Two small, append-only tables. Reads and
-- backfills nothing; both start empty.
--
-- storage_object_retired: one row per Storage object removed because an
-- identical-bytes keeper (same cik + sha256) stays in the bucket. The raw.*
-- row itself is never deleted (core.fact.raw_object_id points at it); this
-- table is the redirect: retired path -> keeper path, so collector/integrity.py
-- and any reader can still resolve the bytes. Written by the executor
-- (collector/storage_retire.py) BEFORE the object is deleted, so a crash
-- between the two steps leaves a harmless extra row, never an unresolvable path.
create table if not exists raw.storage_object_retired (
    source_table         text   not null
        check (source_table in ('raw.sec_companyfacts', 'raw.sec_submissions')),
    raw_id               bigint not null,
    cik                  text   not null,
    sha256               text   not null,
    retired_storage_path text   not null,
    keeper_raw_id        bigint not null,
    keeper_storage_path  text   not null,
    bytes                bigint,
    etag                 text,
    rule                 text   not null default 'S',
    executor_batch       text,
    retired_at           timestamptz not null default now(),
    primary key (source_table, raw_id)
);
create index if not exists idx_storage_object_retired_keeper
    on raw.storage_object_retired (source_table, keeper_raw_id);

-- sec_companyfacts_unchanged_fetch: audit row for a fetch whose payload was
-- byte-identical to the CIK's latest stored payload (collector/dedupe.py). No
-- object is uploaded and no raw.sec_companyfacts row is written for it.
create table if not exists raw.sec_companyfacts_unchanged_fetch (
    cik         text   not null,
    fetched_at  timestamptz not null,
    run_id      bigint,
    sha256      text   not null,
    kept_raw_id bigint not null references raw.sec_companyfacts (id),
    primary key (cik, fetched_at)
);
create index if not exists idx_sec_cf_unchanged_run
    on raw.sec_companyfacts_unchanged_fetch (run_id);
