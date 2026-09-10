# Scrooner Screener Performance — Recommendation

**Goal:** Make Scrooner one of the fastest stock screeners available. **Problem:** a simple ROE screen currently takes ~23s because the engine reconstructs screening data from normalized filing tables on every request. **Fix:** stop computing at request time — precompute, serve from a small dedicated table, cache by dataset version.

## Architecture

```
Browser → Next.js API/BFF → Screener engine → Postgres serving table (+ Redis cache)
```

The API layer is not the bottleneck and should stay (auth, validation, query compilation, pagination). Database access stays too — but only against a small, precomputed table, never the normalized financial-data system.

## The five things to build

1. **`analytics.company_screening_snapshot`** — one row per company, every screenable *and derived* value pre-calculated: raw metrics (ROE, ROIC, P/E, D/E...) **plus** derived/relative fields your filter spec already requires — sector P/E median, 5yr valuation percentile, margin-trend flag, quality booleans (FCF > net income, margins expanding 3yr). If a filter needs computation, it must already be a column here — no exceptions, or the 23s problem just moves.
2. **SQL compiler, not string-building** — normalized criteria → parameterized SQL. Must support **AND/OR/NOT** trees (not just AND-of-ranges), since that's a stated P0/P1 requirement, not a nice-to-have.
3. **Dataset-versioned Redis cache** — `query_hash = SHA256(canonicalized criteria + sort + dataset_version)`. Critical detail: canonicalize boolean trees (e.g. sort children, fixed operator ordering) before hashing, or `A OR B` and `B OR A` miss each other and your cache hit rate quietly collapses. Cache invalidates by bumping `dataset_version`, never by TTL.
4. **Persisted saved-screen runs** — opening a saved screen reads the last run; only "Refresh" queries live. No live query on page load for saved screens.
5. **Cursor pagination** — 50 rows + opaque cursor, reading the persisted run or an indexed query. No client-side pagination of large result sets.

Keep AI/NL parsing **outside** the critical path: deterministic parser handles standard phrasing; LLM only for genuinely ambiguous queries.

## Performance budgets (p95)

| Operation | Target |
|---|---:|
| Metric catalogue | <50ms |
| Deterministic interpretation | <30ms |
| Cached screen | <100ms |
| New DB screen | <300ms |
| Next page | <100ms |
| Open saved screen | <150ms |
| Complex uncached screen | <750ms |

## ClickHouse / Elasticsearch: not now

At a few thousand to ~10K US tickers, the entire snapshot table fits comfortably in memory — Postgres will hit these targets with correct indexing alone. Add a columnar engine only if measured production queries still miss p95 after precomputation, indexing, caching, connection pooling, and same-region deployment. Introducing it earlier adds operational cost with no evidence it's needed.

## Known gaps to close before build (don't let these surface as a second 23-second problem)

- **Schema must cover derived/relative filters**, not just raw metrics — see item 1.
- **Boolean-tree canonicalization** for correct cache hits — see item 3.
- **Point-in-time / backtesting is out of scope here** but `dataset_version` should be designed so it can later map to point-in-time snapshots, since backtesting requires historical (not just latest) snapshots.
- **"Near-miss" explanations** ("would match except ROIC is 11%, needed 12%") don't fit a plain indexed WHERE-clause query — plan for it as a separate query shape, not an extension of this table.

## Build order

1. Precomputed `company_screening_snapshot` (with derived fields)
2. SQL compiler with AND/OR/NOT support
3. Dataset-versioned Redis cache (canonicalized hashing)
4. Persisted screen runs
5. Cursor pagination
6. Same-region deployment
7. Telemetry against the p95 budgets above