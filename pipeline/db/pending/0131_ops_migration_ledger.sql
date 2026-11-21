-- 0131: migration ledger (review-response plan P1.2, 2026-11-21).
-- Why: migrations were applied by hand; supabase_migrations.schema_migrations is stale (15 rows, max 20261003) and no
-- application ledger exists, so "is file NNNN live, and is it the same file?" had no answer in the database.
-- One row per migration file applied to this database: number, filename, sha256 of the file bytes, when, by whom.
-- The ledger row is written IN THE SAME TRANSACTION as the migration (see doc 53, "Applying a migration"), so a
-- migration is either fully applied and recorded or neither. Rows for migrations applied before this table existed are
-- proposed by `scripts/migration_ledger.py backfill` (a live read-only probe, evidence = 'probe') and inserted by a
-- reviewed statement under the founder's typed words; they are never invented by this file.
-- `python3 scripts/check_migrations.py --live` fails when repo files and this table disagree on name or hash.
-- ROLLBACK: drop table ops.migration_ledger;  (nothing references it; drop schema ops only if empty)
create schema if not exists ops;

create table if not exists ops.migration_ledger (
    number      integer     primary key check (number between 1 and 9999),
    filename    text        not null unique check (filename ~ '^[0-9]{4}_[a-z0-9_]+\.sql$'),
    sha256      text        not null check (sha256 ~ '^[0-9a-f]{64}$'),
    applied_at  timestamptz not null default now(),
    applied_by  text        not null check (btrim(applied_by) <> ''),
    -- 'transaction': row written inside the migration's own transaction (exact apply time).
    -- 'probe': backfilled from a live object probe; applied_at is the backfill time, NOT the apply time.
    evidence    text        not null default 'transaction' check (evidence in ('transaction', 'probe')),
    constraint migration_ledger_number_matches_filename check (number = substr(filename, 1, 4)::integer)
);

alter table ops.migration_ledger enable row level security;

comment on table ops.migration_ledger is
    'One row per migration file applied to this database (number, filename, sha256 of the file, applied_at, applied_by). Written in the same transaction as the migration; checked against the repo by scripts/check_migrations.py --live.';
