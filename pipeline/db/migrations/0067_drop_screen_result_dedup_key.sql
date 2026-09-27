-- Reverts migration 0064's dedup-by-content design (2026-09-20, explicit
-- founder direction: "i chose postgres for the speed, i dont want unique
-- key or whatever thing"). Measured live before changing anything: for a
-- brand-new query, each Postgres round trip to this remote instance costs
-- 0.3-1.7s on its own (network RTT dominates, not the ON CONFLICT check
-- itself) -- the old write path paid THREE separate round trips (insert
-- screen_result, executemany screen_result_item, insert user_screen_run).
-- The real fix is combining all three into one round trip via a chained
-- CTE (apps/backend/routers/screen_runs.py); the unique constraint/ON
-- CONFLICT branching added complexity without being the actual bottleneck,
-- and cross-user dedup is no longer wanted, so it goes too.
--
-- Every screen run now gets its own screen_result row again (closer to the
-- original pre-0064 shape), but keeps 0064's two-table split -- app.
-- user_screen_run is still the only per-user thing, since that separation
-- is unrelated to the dedup key itself and doc/faster-loading's original
-- "one table with stocks with reference to screen" framing still holds.

-- query_hash stays on the row (cheap, useful for debugging/telemetry) but
-- is no longer a lookup or uniqueness key, so it needs no index at all.

drop index if exists app.idx_screen_result_query_hash_dataset;
