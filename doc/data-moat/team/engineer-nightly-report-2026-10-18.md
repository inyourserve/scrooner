# Data engineer: nightly reliability report, 2026-10-18

## 1. Why the coverage snapshot stopped
Premise needs correcting: `analytics.coverage_snapshot` has rows for 10-17 (163 rows; dates present 9-29, 10-3, 10-4, 10-10..13, 10-17). The missing dates are 10-14, 10-15, 10-16. (DATA-INFERRED from one light read plus GitHub job logs, FILING-N/A.)
- Root cause for 10-14..16: `snapshot-coverage` died with `QueryCanceled: statement timeout` in `_load_concept_coverage` (coverage_snapshot.py:171) after ~2 min, the pooler default. Runs 38606067797, 38775302476, 38934758661, step "Record daily coverage snapshot" (failure, 2 min each). Same day the coverage matrix (12-14 min) and tag library (5 min) failed identically.
- Fix already in HEAD: 7f4eb17 (2026-10-17) raised statement timeouts. Run 39046403629 then wrote the 10-17 snapshot (9 min). Its matrix (30 min) and tag-library (15 min) steps and the freshness gate (`_scalar`) still hit QueryCanceled, so they are not yet reliable.
- Upstream: job 1 ("SEC filing index and reprocess") is cancelled at the 180 min job cap every night since 10-13 (step "Reprocess Normalizer + Mapper" never completes). That is the bigger reliability problem. Not changed.
- Side note: `coverage_group_snapshot rows_written=0` on 10-17 (group snapshot writes nothing); not investigated.
- Next night's proof: check `max(snapshot_date)` = 2026-10-18 after the scheduled run, and that matrix/tag steps pass with the raised timeouts while the recompute is running.

## 2. covered > total (ROE 4,818 / 4,815)
Cause: `_load_metric_coverage` counted distinct companies with a value from the whole of `analytics.metric_value`; the denominator is the `real_operating_company` population (`analytics.company_population`, 4,808 today, 4,815 on the reported day). Metric rows are never deleted when a company leaves a population, so the numerator contained companies outside the denominator. The concept path hid the same mismatch with `max(denom, covered)`. Latest snapshot (10-17) has six metrics above 100%: net_change_in_cash 100.10, ocf_to_net_income 105.68, profitable_streak_years 101.52, roa 101.83, roe 100.25, total_shareholder_yield 120.18 (3,621/3,013, capital_return_company population). Direct per-metric proof query timed out at 20s (not retried, heavy-job rule), so the "outside population" mechanism is DATA-INFERRED from code and the counts, not directly counted.
Fix: the metric numerator is now restricted to the metric's own denominator population (SQL `METRIC_COVERAGE_SQL`, EXPLAIN checked live for syntax, not executed); a warning plus floor remains for the fallback case. Concept path untouched (still floored, so a concept at 100.00% may hide the same thing; recommend the same restriction later).

## 3. Heavy-job gate (proposal, not wired)
`pipeline/src/scrooner_pipeline/db/heavy_job_guard.py`: reads `pg_stat_activity` (20s timeout), refuses if connections > 10 or another session's active query > 10 min; `--force`-style override logs a warning. Pure decision function `evaluate_gate` is unit-tested. Right now the DB shows 17 connections, so the gate would refuse. Next step: call `require_heavy_job_gate` at the top of each heavy Typer command and add `--force-heavy`; needs owner review of thresholds. No migration needed (no schema change), so no number claimed in doc 53.

## Files (uncommitted)
- pipeline/src/scrooner_pipeline/mapper/coverage_snapshot.py
- pipeline/tests/unit/test_coverage_snapshot.py
- pipeline/src/scrooner_pipeline/db/heavy_job_guard.py (new)
- pipeline/tests/unit/test_heavy_job_guard.py (new)
- doc/data-moat/team/engineer-nightly-report-2026-10-18.md
conflict_resolution.py and its test were not touched (pre-existing modifications are another change's).

## Tests
`pytest tests/unit/test_coverage_snapshot.py test_heavy_job_guard.py test_coverage_matrix.py`: 31 passed. ruff format applied; `ruff check` reports only the pre-existing import-order finding in coverage_snapshot.py (uvx ruff; project ruff/mypy not installed in .venv, mypy not run). Not run: full suite, a live snapshot with the new SQL (heavy).
