-- Deduplicated screen results (doc/faster-loading/fast.md, continued
-- 2026-09-12). Every user who ran a screen used to get their own
-- private copy of the computed result in app.screen_run/
-- screen_run_result -- Redis already skips recomputing an
-- already-cached query, but a second, different user asking the exact
-- same question still paid a real Postgres write of a duplicate copy.
-- Measured live before building this: ~2.1s for that write alone on a
-- 25-row result, pure overhead since the data was already known.
--
-- Split what screen_run used to do into two tables: one canonical,
-- deduplicated result shared by every user who asks the same query
-- against the same dataset generation, and one thin per-user pointer
-- that preserves "my saved screens" rerun history without duplicating
-- the actual matched-company rows.

create table if not exists app.screen_result (
    id               uuid primary key default gen_random_uuid(),
    query_hash       text not null,
    dataset_version  bigint not null,
    normalized_query jsonb not null,
    total_count      integer not null check (total_count >= 0),
    exclusions       jsonb not null default '{}'::jsonb,
    computed_at      timestamptz not null default now()
);

-- The dedup key. A second user's identical query, same dataset
-- generation, finds this row instead of computing a new one.
create unique index if not exists idx_screen_result_query_hash_dataset
    on app.screen_result (query_hash, dataset_version);

create table if not exists app.screen_result_item (
    screen_result_id uuid    not null references app.screen_result (id) on delete cascade,
    position         integer not null check (position >= 0),
    company_id       bigint  not null references core.company (id),
    result           jsonb   not null,
    primary key (screen_result_id, position),
    unique (screen_result_id, company_id)
);

-- One row per user per time they ran a query -- never a duplicate copy
-- of the matched companies, just a pointer to the shared result plus
-- whatever is genuinely per-user (the raw text they typed, when).
create table if not exists app.user_screen_run (
    id               uuid primary key default gen_random_uuid(),
    user_id          uuid not null references auth.users (id),
    screen_result_id uuid not null references app.screen_result (id),
    query_text       text not null,
    ran_at           timestamptz not null default now()
);

create index if not exists idx_user_screen_run_user_ran_at
    on app.user_screen_run (user_id, ran_at desc);

-- Backfill existing rows 1:1 (dev/test scale -- 15 rows as of this
-- migration). No retroactive deduplication: the old rows never recorded
-- their query_hash/dataset_version, so there's nothing real to dedupe
-- them against. Dedup only applies to writes made after this migration.
-- Reuses screen_run.id as BOTH the new screen_result.id (so
-- screen_run_result.run_id maps across without a lookup table) and the
-- new user_screen_run.id (so saved_screen.last_run_id's already-stored
-- values keep pointing at the right row once its FK target changes below).
insert into app.screen_result (id, query_hash, dataset_version, normalized_query, total_count, exclusions, computed_at)
select id, 'legacy:' || id::text, 0, normalized_query, total_count, exclusions, created_at
from app.screen_run;

insert into app.screen_result_item (screen_result_id, position, company_id, result)
select run_id, position, company_id, result
from app.screen_run_result;

insert into app.user_screen_run (id, user_id, screen_result_id, query_text, ran_at)
select id, user_id, id, query_text, created_at
from app.screen_run;

alter table app.saved_screen drop constraint if exists saved_screen_last_run_id_fkey;
alter table app.saved_screen add constraint saved_screen_last_run_id_fkey
    foreign key (last_run_id) references app.user_screen_run (id) on delete set null;

drop table if exists app.screen_run_result;
drop table if exists app.screen_run;
