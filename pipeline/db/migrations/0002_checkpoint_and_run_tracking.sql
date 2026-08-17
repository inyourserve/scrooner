-- Day 4: checkpoint/resume support. See doc/08_Scrooner_Collector_Execution_Plan.md
-- Day 4 row and doc/learnings/day-04-retry-and-resume.md for the full design
-- rationale. Additive only -- every new column is nullable, nothing here
-- changes the meaning of an existing row.

-- Idempotency key for append-only fetch rows. sec_companyfacts/sec_submissions
-- are intentionally append-only (Day 3): a genuinely new fetch pass for a
-- company that's already stored is allowed and expected (lossless history).
-- What must NOT happen is the same run's pass double-storing the same fetch
-- after a kill-and-resume. storage_path is deterministic per (cik,
-- fetched_at[, filename]) and only changes when a run gets a new fetched_at
-- -- so it's the natural idempotency key. Enforcing it as a unique
-- constraint means even a bug in the application-level checkpoint skip logic
-- can't produce a duplicate row/object; the database is the final guarantee.
alter table raw.sec_companyfacts
    add column if not exists run_id bigint references raw.collector_runs (id);
alter table raw.sec_submissions
    add column if not exists run_id bigint references raw.collector_runs (id);

create index if not exists idx_sec_companyfacts_run_id on raw.sec_companyfacts (run_id);
create index if not exists idx_sec_submissions_run_id on raw.sec_submissions (run_id);

do $$
begin
    if not exists (
        select 1 from pg_constraint where conname = 'sec_companyfacts_storage_path_key'
    ) then
        alter table raw.sec_companyfacts
            add constraint sec_companyfacts_storage_path_key unique (storage_path);
    end if;
    if not exists (
        select 1 from pg_constraint where conname = 'sec_submissions_storage_path_key'
    ) then
        alter table raw.sec_submissions
            add constraint sec_submissions_storage_path_key unique (storage_path);
    end if;
end $$;

-- Run-level checkpoint/resume state. A logical bootstrap invocation is
-- identified by (job, params_key): job is the sub-command
-- ('universe'|'companyfacts'|'submissions'|'golden'), params_key is a
-- deterministic string of that invocation's filters (only_ciks/limit). If a
-- process is killed mid-run, its raw.collector_runs row is left
-- status='running'. The next invocation with the SAME job+params_key finds
-- that row and resumes it -- same run_id, same fetched_at -- instead of
-- starting fresh and re-storing everything already done.
--
-- fetched_at is persisted (not recomputed per company) so a resumed pass
-- reuses the exact same storage_path for any company it re-touches, making
-- the unique constraint above meaningful as true belt-and-suspenders, not
-- just an accident of timing.
--
-- heartbeat_at is updated periodically during a run (not just at start) so
-- staleness can be judged by "has this row shown any sign of life
-- recently", not just "how old is started_at" -- a legitimately long full-
-- universe bootstrap shouldn't be reaped just because it's been running for
-- a while.
alter table raw.collector_runs
    add column if not exists job text;
alter table raw.collector_runs
    add column if not exists params_key text;
alter table raw.collector_runs
    add column if not exists fetched_at timestamptz;
alter table raw.collector_runs
    add column if not exists heartbeat_at timestamptz;

create index if not exists idx_collector_runs_resumable
    on raw.collector_runs (job, params_key, status);
