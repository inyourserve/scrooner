-- Real bug found live 2026-08-22 launching the first full-universe
-- expansion shards (~1,270 CIKs each): every shard failed identically
-- on its very first insert with
-- "ProgramLimitExceeded: index row size 6488 exceeds btree version 4
-- maximum 2704 for index idx_collector_runs_resumable" -- a hard
-- Postgres btree page-size limit hit because params_key (the
-- comma-separated CIK list passed to --ciks, doc 08's resumability key)
-- can be many KB long for a large shard.
--
-- raw.collector_runs is a small operational bookkeeping table (one row
-- per collector invocation, 22 rows total as of this fix) -- it never
-- needed params_key indexed for query speed; a full scan of the handful
-- of rows matching (job, status) is trivially fast regardless of table
-- size. Dropping params_key from the index removes the size limit
-- entirely with zero query change needed (find_resumable_run's own
-- exact-match filter on params_key still runs correctly, just without
-- an index assist it was never actually needed for at this scale).

drop index if exists raw.idx_collector_runs_resumable;
create index if not exists idx_collector_runs_resumable on raw.collector_runs (job, status);
