# ADR 0001 — Screener Redis cache + AND/OR/NOT boolean-tree queries

> Per doc 05: an ADR for a consequential technical change. Supersedes two rows in the [Decision Register](../foundational/02_Scrooner_Decision_Register.md) -- "No Redis or Celery initially" (in the general locked-decisions table) and the Screener's original "AND-of-predicates only, no OR/nested boolean logic" boundary (doc 14, restated in `pipeline/CLAUDE.md`'s per-module "must not" list).

**Status:** Accepted
**Date:** 2026-09-10

## Context

`doc/faster-loading/fast.md` (a performance recommendation doc) proposed five changes to make the Screener fast: a precomputed serving table, a real SQL compiler supporting AND/OR/NOT trees, a dataset-versioned Redis cache, persisted saved-screen runs, and cursor pagination. Two of the five conflicted with decisions already locked in doc 02: "No Redis or Celery initially" (general locked-decisions table), and the Screener's boundary table restriction to simple AND-of-predicates (doc 14, `pipeline/CLAUDE.md`).

Before building anything, the actual bottleneck was measured live (not assumed from `fast.md`'s own guess): a real `ROE > 0.15` screen took **13.9s**. `EXPLAIN ANALYZE` on the exact query `screener/resolve.py` runs showed the cost was a Bitmap Heap Scan against `analytics.metric_value` (11M rows across 82 metrics) touching ~16,000 cold heap pages to pull ~205K raw rows for a single metric — rows for one `metric_definition_id` are scattered across the table's whole physical storage, not an unindexed query (`idx_metric_value_metric_definition_id` already existed). See `doc/learnings/2026-09-10-screener-performance.md` for the full investigation, including a separate finding that this dev machine's network round trip to the project's Supabase instance (`us-east-1`) costs ~270ms per query, and a fresh `psycopg.connect()` costs ~1.7s for TCP+TLS+auth alone.

Presented with the conflict, the founder explicitly chose to override both locked decisions rather than work around them (2026-09-10, in-session decision).

## Decision

1. **Redis is now a real, required production dependency of `apps/backend`** (not `pipeline`, which stays Redis-free), used exclusively for a dataset-versioned cache of `/v1/screen` and `/v1/ask` results. This supersedes doc 02's "No Redis or Celery initially" row for this one use only — it does not reopen Celery, background job queues, or any other Redis use case.
2. **The Screener's `ScreenQuery` schema now supports an optional `where: PredicateGroup` field** — an arbitrary AND/OR/NOT tree over metric and categorical predicates, compiled to a single parameterized SQL statement (`EXISTS` subqueries per metric leaf) against a new precomputed table, `analytics.company_screening_snapshot`. This supersedes doc 14's original "AND-of-predicates only" restriction. The original flat `metric_predicates`/`categorical_predicates` lists (implicit AND) still work unchanged for backward compatibility — every existing caller (`ai_query`, saved screens, doc 14b's golden-set tests) is unaffected.

## Alternatives considered

- **Postgres-only fix, no Redis** (indexing + the precomputed snapshot table alone). This was the first thing built and measured: it took the same `ROE > 0.15` screen from 13.9s to ~5.7s (dominated by this dev machine's network RTT to `us-east-1`, ~270ms × several round trips, not by any remaining query-plan inefficiency). Real, but not enough on its own to hit `fast.md`'s stated `<100ms` cached-screen budget — presented as the "keep the lock" option before the founder chose to override it.
- **Keep AND-only, defer OR/NOT indefinitely.** Rejected once the founder confirmed OR/NOT is a real, current product need, not a hypothetical one — doc 05's "evidence before expansion" principle is satisfied by that direct confirmation, not violated by building it now.

## Consequences

**Easier:** a cache-hit `/v1/screen` request now completes in **~4-8ms** (verified live against the real backend, `apps/backend/routers/screen.py`), and any query the product wants to express with OR/NOT (e.g. "ROE > 30% OR debt-to-equity < 0.1") is now expressible without a schema change. A dataset-versioned cache key (`scrooner_pipeline.screener.cache_key.compute_query_hash`) means a snapshot rebuild mints new cache entries automatically — no TTL-based invalidation logic to get wrong, matching doc 02's original caching concern even though the lock itself is superseded.

**Harder / new operational surface:** `apps/backend` now depends on a real Redis instance in production (Upstash recommended, matching `doc/reference/DOCUMENTATION.md`'s original mention) — a new managed component a solo founder must provision and monitor, the exact cost doc 02's original lock was written to avoid. Local dev now requires `brew install redis` (or equivalent) to run `apps/backend` at all. `analytics.company_screening_snapshot` is a new table that must be rebuilt (`scrooner-screen build-snapshot`) after every Mapper run or screen results silently go stale relative to `core`/`analytics` — no automated cron wires this in yet (see root `CLAUDE.md`'s existing "no scheduled reprocessing chain" gap; this is now a second job that gap needs to eventually cover).

**Foreclosed/scoped out this pass:** per-predicate `excluded_missing_data` attribution has no single well-defined meaning under OR/NOT (a company excluded by one branch may still match via another) — a `where`-tree query returns an honest `exclusion_detail` note instead of a false claim of precision, rather than forcing a semantics that doesn't fit. Same-region deployment (closing the remaining ~270ms/round-trip gap for a genuinely cold, uncached query) is named but explicitly not done here — a separate infra decision, `fast.md`'s own build-order item 6.
