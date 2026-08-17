# Mapper Day 6 — Validation, Confidence States, End-to-End DoD Proof

## The bug: a delete scoped by the wrong dimension, twice

Testing the incremental-reprocessing property doc 11's Definition of Done actually names — "be re-run incrementally... without recomputing the entire golden set every time" — rather than assuming it from reading the code, exposed a real bug that had existed silently since Day 4.

`calculate.py`'s per-company write step deleted `analytics.metric_value` rows scoped only by `company_id`, then reinserted just its own 10-metric subset. Every prior day's verification checked whether *that day's own* numbers were correct; none checked what a rerun would do to a *different* stage's previously-written rows in the same shared table. Snapshotting `analytics.metric_value` row counts before and after a single-CIK `calculate` rerun (RDDT) surfaced it immediately: RDDT dropped from 243 to 143 rows — exactly Day 5's RDDT growth+TTM total (72+28=100) — while all 7 other companies stayed byte-for-byte identical. The unscoped delete had wiped Stage 3e's own prior output for that company on every Stage 3d rerun.

The first fix — scoping the delete to `metric_definition_id = any(target_ids)` — was itself incomplete, and re-running the same isolation test caught that too: RDDT came back at 215, not 243, a further 28-row gap matching exactly the TTM ROIC/ROE count. Cause: `roic` and `roe` share one `metric_definition_id` between Stage 3d's FY rows and Stage 3e's TTM rows, distinguished only by `period_label`. Scoping by metric id alone still let Stage 3d's delete reach into rows it doesn't own. The real fix added `and period_label != 'TTM'`, mirroring the opposite-direction exclusion (`and period_label = 'TTM'`) `ttm.py`'s own `compute_ttm_returns` delete already used — the two stages' deletes now partition the shared table by construction instead of by convention.

## Why this survived two full days of verification

Days 4 and 5 both did real, careful reconciliation — hand-checked margins, cross-checked TTM against FY to full decimal precision, confirmed idempotency by rerunning each stage's *own* command twice in a row and comparing totals. That idempotency check is exactly why it looked safe: rerunning `calculate` alone, twice, for the full golden set, always produced the same 2,271/1,187 split, because both runs destroyed and rebuilt the same rows in the same way — the bug is invisible unless the *other* stage's output already exists in the table at the time of the rerun, which Day 4's own idempotency check never had (Stage 3e didn't exist yet). It only became observable once both stages had run, and only if the test scoped to a company that had output from both. This is a real gap in what "verified idempotent" meant across two separate days — each stage checked its own idempotency, but nobody checked cross-stage isolation until Day 6 explicitly went looking for it.

## The generalizable lesson: shared-table ownership boundaries need explicit scoping on both sides, not implicit convention

`analytics.metric_value` is written by two different modules (`calculate.py`'s FY/quarterly rows, `ttm.py`'s growth and TTM rows) that happen to share both a table and, for `roic`/`roe`, a `metric_definition_id`. `ttm.py` already scoped its own deletes correctly on both of its write paths (`metric_definition_id = any(growth_ids)` for growth; `metric_definition_id = any([roic_id, roe_id]) and period_label = 'TTM'` for TTM returns) — `calculate.py` was the one incomplete side. Whenever two pipeline stages write into the same table under a shared foreign key, each stage's delete-then-reinsert needs to positively identify *only* the rows it owns, on every dimension another stage might also key on — not just the most obvious one (`metric_definition_id`) while missing a second, less obvious one (`period_label`) that turned out to matter for exactly two metrics out of twenty.

## Confirmed clean, not just fixed

Built `mapper/validate.py` (Stage 3f, `scrooner-map validate`) to make the checks this day needed repeatable rather than one-off: confidence-state distribution, non-authoritative-leak detection across both `analytics.canonical_fact` and `analytics.metric_value`, and `source_fact_ids` lineage integrity (every id resolves to a real `core.fact` row). Run clean against the full golden-8 after the fix: 28 approved / 3 provisional / 1 rejected confidence states (all traceable to real Day 1/2 findings, not unused schema), 0 non-authoritative leaks, 0 dangling lineage references.

Also cross-checked against `edgartools` (doc 12) as an independent second data path, not just internal reconciliation: AAPL FY2025 and FY2024 `net_margin`, computed from edgartools' independently-pulled income statement, matched `analytics.metric_value`'s stored figures to full decimal precision in both years.

## Full golden-set re-verification after the fix

Reran `calculate`, `growth`, `ttm-returns` across the full golden-8 (not just RDDT) to confirm the fix didn't change anything it shouldn't have: identical totals to Days 4–5's originals (2,271/1,187 point-in-time, 1,369/433 growth, 440/358 TTM). Total `analytics.metric_value`: 6,058 rows, matching Day 5's recorded total exactly. DB size: 58 MB (11.6% of the Supabase free-tier budget).

## Why it matters going forward

Any future pipeline stage that writes into a table another stage also writes into — which the Screener/AI-Query layers may well do over `analytics.metric_value` or a serving view of it — needs its delete/write scope checked against *every* other writer's key space, not just the primary foreign key. This is now a standing question to ask before adding a new write path to any shared table: "what dimensions do the other writers key on, and does this delete exclude all of them?" — not just "does this delete match this stage's own rows."
