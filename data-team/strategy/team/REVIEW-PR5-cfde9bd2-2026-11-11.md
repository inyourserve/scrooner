# Review of PR #5 at c8f2d026: commit cfde9bd2 (nightly refresh volume) and the merged guard (2026-11-11)

Reviewer: the balance-sheet lane. Requested by scrooner-8f (CI/CD session) for Dhairya.

How I checked: I read the diff and ran the tests the way CI runs them (Postgres 16): `test_operations`, `test_sharded_runner`, `test_ci_heavy_job_guard_script` and `test_heavy_job_guard`, 42 passed. I made no production reads for this review.

## The merged guard

`scripts/ci/heavy_job_guard.sh`, the eight workflow files and `test_ci_heavy_job_guard_script.py` at c8f2d026 are byte-identical to `work/ci/heavy-job-guard` d5b9ccc9, which I reviewed and tested. Nothing new to review there. `work/ci/heavy-job-guard` stays unopened, as asked.

## cfde9bd2, part 1: `reprocess_recent_filers.sh` selects only filers with work left

The SQL does what the commit says. A 10-K or 10-Q in the lookback window is selected when its accession has no `core.fact` rows yet, or when facts arrived within `FACTS_RETRY_HOURS` (48). The parameters line up with the placeholders, and the backlog branch is unchanged.

**Finding (should fix, or set the window for tonight).** Every stage, the map stages included, runs only for the selected companies (`--ciks "$CIKS"`). The 48-hour window retries a skipped night **once**. Two failed nights in a row is exactly what happened on 11-08 and 11-09, both of which ran out of budget and skipped the last map stages. After two such nights, a company whose facts landed before the first of them is never selected again. Its growth, TTM, expanded metrics, Piotroski, reconciliation and dividend-streak values stay stale until its next filing. No freshness alarm catches this per company: `mapper_backlog` watches the global maximum of `resolved_at`.

Suggested fix, smallest first:
- **(a)** For tonight's run, set `FACTS_RETRY_HOURS` to cover the time since the last refresh that finished every stage (about 96–120 hours if 11-10 also skipped stages). Selection stays bounded by the 4-day filing window.
- **(b)** Durable fix: measure the retry from the start of the last run that completed all stages, rather than from a fixed number of hours.

This does not make any value wrong. It leaves derived metrics stale, which the freshness alarm does not catch per company.

## cfde9bd2, part 2: `normalizer_backlog` from `max(core.filing.created_at)`, 5 days

Correct. `core.filing` rows are inserted by the Normalizer's identity stage (`normalizer/identity.py`), so `created_at` measures the Normalizer keeping pace, and a re-normalize does not rewrite it. The 5-day limit covers a weekend plus a Monday holiday.

Minor: a historical backfill that inserts old filings (the history tranches) also advances `max(created_at)`. That can hide a stalled daily Normalizer for up to 5 days. It is acceptable, but worth a note in the target's comment.

## Verdict

Approve, on one condition: the retry-window finding is handled before the next nightly, either by setting `FACTS_RETRY_HOURS` for tonight (a) or by the durable fix (b). The guard part is approved as is.
