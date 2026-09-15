# 2026-09-12 — Deduplicated screen results: one canonical copy per query, not one per user

Prompted directly: "can we store each screen in a db table, then one table with stocks with reference to screen?" Grounded in a real measurement before building anything, per this project's own discipline.

## What was already true

By this point, `apps/backend`'s Redis layer (built 09-10/09-11) already cached the *computed* result of a screen by `query_hash` (which bakes in `dataset_version`), and a repeated identical query by the *same* user was already a ~3ms cache hit via a per-user `(user_id, query_hash, text) → run_id` pointer. That part was solved.

## What wasn't: a different user still paid a duplicate write

Measured live before proposing anything: User A asking a fresh query paid the full ~6s (real compute). User A repeating it: 3ms. **User B — a different user, asking the exact same query** — paid **2.1s**, even though the log confirmed `run_query()` was correctly skipped (Redis had the result). That 2.1s was pure overhead: writing B's own private copy of an already-known 25-row result into `app.screen_run`/`app.screen_run_result`, because every user's screen run got its own full copy of the matched-company rows in Postgres, with no sharing at the database level at all.

## The fix: split "the computed result" from "a user's reference to it"

New schema (migration `0064_deduplicated_screen_results.sql`):

- **`app.screen_result`** — one canonical row per unique `(query_hash, dataset_version)`, written once no matter how many users ask it. A unique index on that pair is the actual dedup key.
- **`app.screen_result_item`** — the matched-company rows, stored once per `screen_result`, never duplicated per user.
- **`app.user_screen_run`** — a thin per-user pointer (`user_id`, `screen_result_id`, `query_text`, `ran_at`). This is what "my saved screens" / rerun history actually needs, and it's the only thing genuinely per-user — no duplicated company data.

`app.saved_screen.last_run_id`'s foreign key was repointed from the old `screen_run` to the new `user_screen_run` (ownership/ "my screen" semantics live there, not on the shared canonical table, which has no owner at all). The old `screen_run`/`screen_run_result` tables were dropped after a 1:1 backfill (15 rows, 12,115 items — dev/test scale, no real users yet, so no retroactive deduplication of historical rows was worth the engineering cost; dedup applies to writes made from this point forward).

`create_run_from_query` now does the write as `INSERT INTO screen_result ... ON CONFLICT (query_hash, dataset_version) DO NOTHING RETURNING id` — the standard race-safe "get or create": whoever wins the insert also writes `screen_result_item`; whoever loses (the row already existed) does one cheap `SELECT` for the id and skips the item write entirely. Every caller, win or lose, still gets its own `user_screen_run` row — that part was never the expensive one.

## Honest result: real, but more modest than hoped

Verified live after the fix, same setup as before:

| Case | Before | After |
|---|---:|---:|
| First ever compute (25 rows) | 5.1–6.1s | unchanged (still real compute) |
| Same user, repeat | 3ms | unchanged (already solved) |
| **Different user, same cached query (25 rows)** | **2.1s** | **1.5–1.9s** |
| Different user, same cached query (1,802 rows) | ~2.8–3s (estimated from the 1,401-row executemany cost measured 09-10) | **2.0s** |

The win is real and unconditional — every duplicate query benefits, and it scales *up* with result-set size (the bigger the result, the more `executemany` work is now skipped entirely). But for a small, common result set it's a meaningful trim (roughly 500ms–1s), not a 10x collapse — the remaining ~1.5–2s for a "new user, warm query" is mostly the round trips that were never about duplication in the first place: `get_cached_dataset_version`, the Redis lookups, the `screen_result` conflict check, the `user_screen_run` insert, and — for a large cached result — deserializing a genuinely large JSON blob back out of Redis. None of those disappear just because the company rows are shared now.

**Named, not chased further this pass**: closing that remaining gap needs the same lever already identified 09-10 and not yet acted on — same-region deployment. Every one of those round trips costs ~270ms from this dev machine to `us-east-1`; in production, with the backend actually running near the database, the same code would likely land closer to the "3ms" end of this table for most cache hits, not because anything else changes, but because the network stops being the bottleneck.

2 new tests (`tests/test_screen_result_dedup.py`, using a fake cursor to assert the conflict/no-conflict branches actually skip/perform the item insert), full backend suite 36→38 passing, pipeline suite unaffected (no pipeline code touched), migration verified against live data (15/15 rows migrated, both existing `saved_screen.last_run_id` references still resolve).
