# Flat-AND SQL pre-filter for the Screener (2026-10-02)

Prompted directly: "design the screen system so it runs in ms... take care of all the edge cases." Builds on the same-day earlier audit (`doc/learnings/2026-10-02-create-screen-latency-audit.md`), which found and flagged but deliberately did not fix: the common "metric above X and metric below Y" query shape (`query.where is None`, the overwhelming majority of real usage) never pushed predicates into SQL at all — it fetched the entire `analytics.company_screening_snapshot` population and filtered in Python, while the less common OR/boolean-tree path (`query.where` set) already did push down and was measurably faster despite being logically more complex.

## Why this wasn't a one-line fix

The flat-AND path has a locked UX requirement the boolean-tree path already gave up: exact per-predicate `excluded_missing_data` attribution (which specific metric was missing for an excluded company — doc 14's explainability release gate). Python's existing loop is **sequential and short-circuits**: a company missing metric A is tagged `excluded_missing_data` citing only A and is never even checked against metric B, regardless of whether B would also have failed. A naive per-predicate `(col IS NULL OR comparison)` ANDed across predicates independently would **wrongly drop** a company that's missing A but has a present, failing value for B — Python's real algorithm keeps that company (tagged on A only); the naive SQL version would never fetch it at all, silently changing output.

## The fix: two independent conditions, OR'd

`query.py::_compile_flat_prefilter()` compiles:

```
(full_match) OR (any_missing)
```

- `full_match` = every non-ranked predicate's column is non-null AND passes its comparison (the real "matched" condition, no relaxation).
- `any_missing` = at least one non-ranked predicate's column is NULL (a plain `OR` across columns, independent of the other columns' values).

Any row Python's existing code would place in `matched` or `excluded_missing_data` satisfies one of these two by construction; a row that's fully dropped (present values, genuinely fails a comparison, nothing missing) satisfies neither and SQL now correctly excludes it before it's ever fetched — which is normally most of the population for a selective filter. Categorical predicates get a plain, unrelaxed `col = %s` (NULL = anything is already falsy in SQL, matching `_apply_categorical_predicates`' Python `==` exactly). Ranked predicates (`top_n`/`bottom_n`) are excluded from the pre-filter entirely — ranking needs to see every candidate the other predicates already left standing, which is exactly this query's own output.

Wired into `run_query()`: the `else` branch (non-`where` queries) now builds this pre-filter and passes it to `_select_snapshot_rows`, wrapped in the same `status != 'active' OR (status = 'active' AND (...))` trick the boolean-tree path already uses when `include_inactive` is false (so `excluded_inactive` still lists every inactive company regardless of whether it would have matched). Everything downstream of the fetch — `_apply_categorical_predicates`, the per-predicate Python filtering loop, ranking, sorting — is **completely unchanged**, now just operating on fewer rows.

## Verification

**Correctness — not assumed, proven against live data.** Ran the pre-change and post-change `run_query()` side by side against the real dev Supabase snapshot (not mocked) for 10 queries covering every structural branch: 2-predicate flat AND, single predicate, `between`, flat AND + categorical, pure ranked (no other predicate), ranked + non-ranked mixed, `include_inactive=True`, zero predicates, categorical-only, and a predicate not also used for sorting. Every one produced **byte-identical** `matched`/`excluded_missing_data`/`excluded_inactive` output:

```
flat AND, 2 predicates                   old=2.384s new=0.339s matched=200   IDENTICAL=True
flat AND, 1 predicate (pe-like)          old=0.614s new=0.597s matched=3211  IDENTICAL=True
flat AND, between                        old=0.626s new=0.592s matched=457  IDENTICAL=True
flat AND + categorical                   old=0.867s new=0.312s matched=257  IDENTICAL=True
ranked only, no other predicate          old=2.372s new=0.894s matched=20   IDENTICAL=True
ranked + non-ranked combined             old=1.737s new=1.157s matched=10   IDENTICAL=True
include_inactive true                    old=1.725s new=1.428s matched=1735 IDENTICAL=True
no predicates at all                     old=1.170s new=1.143s matched=5216 IDENTICAL=True
categorical only                         old=1.178s new=0.288s matched=205  IDENTICAL=True
sort_by not a predicate                  old=2.018s new=1.810s matched=2521 IDENTICAL=True
```

The exact case flagged in the earlier audit (2 metric predicates, the "PE below 30"-shaped query) went **2.384s → 0.339s**, a 7x improvement, with identical results. "Pure ranked, no other predicate" and "no predicates at all" correctly fall back to the original unfiltered fetch (nothing to push down) — their timing differences above are warm-cache noise from running sequentially, not a code-path change, confirmed by `_compile_flat_prefilter` returning `(None, None)` for both.

**Server-side plan is sane, not pathological** — checked via `EXPLAIN (ANALYZE, BUFFERS)` on the live snapshot table: an index scan on `(dataset_version, status)` with the relaxed OR-filter applied, 75ms execution, no sequential scan surprise.

**Offline regression tests** (`tests/unit/test_screener_complete.py`): the exact SQL shape (`_compile_flat_prefilter`'s rendered text and param order, including the `between` and categorical-prefix cases), the vacuous/pure-ranked cases correctly skipping the pre-filter, and — the one genuinely subtle case — a company missing predicate A with a present-but-failing value for B is proven to stay correctly tagged (`missing_metrics == ["A"]` only, never dropped). Full pipeline suite: 783 passing (was 726 before this session's two learnings docs' worth of changes).

## What this does and doesn't fix

`apps/backend`'s `/v1/screen` and `/v1/screen-runs` both call `scrooner_pipeline.screener.query.run_query()` directly — no backend changes needed, both benefit automatically.

Still open, not touched here (see the earlier audit doc): no deployment/region config exists for `apps/backend` at all, so every DB round trip from a non-co-located host still costs ~250-300ms regardless of how little data it now moves. This fix reduces *how much* work and data each request costs; it does not remove network latency as a floor. That remains the single biggest lever and needs a founder hosting decision.
