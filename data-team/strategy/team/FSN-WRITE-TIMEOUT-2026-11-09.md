# FSN write run 42561798991: why nothing was written, and the fix (2026-11-09)

For Dhairya. Branch `work/fsn/pilot-timeout-fix`.

Everything here was read-only on production: `EXPLAIN` without `ANALYZE`, with `statement_timeout = 15s`. There were no production writes and no migration.

## Cause

The pilot step timed out on every company because of one read in `select.load_company`. It fetches a company's values for its mapped tags, members included, so it has no `dim_id` filter:

```sql
where company_id = %s and tag_id = any(%s) and iprx = 0 and value is not null
```

`fsn.value` has a company index, `idx_fsn_value_series (company_id, tag_id, ddate, qtrs) where dim_id = 0`. It is partial, so this read cannot use it. The planner falls back to the unique key `(filing_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg)` with `tag_id` as the only usable condition. That walks every company's rows for the 247 mapped tags (AbbVie, company_id 2848) across 35.6M rows and 10 GB.

| | Estimated cost |
|---|---|
| Before | 846,820 |
| After | 4,692 |

That is enough to pass the pooler's statement timeout for every company: one failure about every 3 minutes, as in the logs. The cohort dry runs never saw it, because their scratch databases held one shard's companies and the walk was short there.

## Fixes

1. **The read.** It now also takes the company's own filing ids: `filing_id = any(...)`. The unique key is then used with both leading columns.
   - The rows returned are the same.
   - No index and no migration are needed.
   - The SQL is the constant `select.MEMBER_VALUES_SQL`.
   - I EXPLAINed every other `fsn.value` read in `fsn_store`. Each is bounded by `filing_id`, or by `company_id` through the partial index, including `bs_derive` on PR #6.
2. **Load (shards 4, 6, 7).** On a company failure, `load.run` called `conn.rollback()`. When the pooler had dropped the connection, that call raised itself and killed the shard.
   - It now checks `conn.closed or conn.broken`, opens a fresh connection, and retries that company once. Each company is one transaction, so a retry repeats nothing committed.
   - If the retry also fails, the company is counted in `errors` and the run goes on.
   - The batch's `rule_run` is finished on the live connection.
   - `scrooner-fsn load` tolerates the first connection's exit commit failing after the run completed.
3. **Pilot.** It has the same dead-connection handling: the company is recorded in `failed.json`, and the next one runs on a fresh connection.
4. **Workflow.** The write step skips an empty `out/cells/*/` glob instead of crashing with `FileNotFoundError`.

## Tests

`pipeline/tests/unit/test_fsn_production_scale.py` (DB-backed):

- The member-value plan uses `filing_id` in its index condition.
- `load.run` survives a backend killed mid-company. It reconnects, loads the company and finishes the rule_run.
- Without `connect`, `load.run` stops with the original error.
- `scrooner-fsn pilot` goes on after a killed backend and writes `failed.json`.

Each test fails when its fix is removed. The full pipeline suite, run the way CI runs it (Postgres 16, every migration): 2,374 passed, 1 skipped (live SEC).

## Before the next run

- The pilot connection still relies on the pooler's default statement timeout. The fix removes the slow statement. It does not set a per-session timeout: in transaction pooling a `SET` lasts only one transaction.
- The rerun loads nothing again for companies already loaded: the `input_sha256` and `loader_commit` skip applies, unless the loader commit changed.
