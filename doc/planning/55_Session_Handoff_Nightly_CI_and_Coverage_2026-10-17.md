# Session handoff: nightly CI, coverage evidence layer (2026-10-13 to 2026-10-17)

Status: handoff from the "nightly/CI watch + coverage" session. Everything below is committed and pushed to `main` unless marked otherwise. Read this instead of the old session transcript.

## 1. What was asked (original intent)

- Work down ~1000 open cockpit tickets, bigger chunks first.
- Find and fix why CI and the scheduled pipelines kept failing.
- Answer: why concept coverage is "only 86%", and extend the revenue-family explanation layer to all concepts so each concept is judged only against companies it applies to.
- Estimate (not do) a npm to pnpm move. **Not started, awaiting a founder decision.**

## 2. Shipped (commit refs)

| What | Ref | Notes |
|---|---|---|
| Filing-line evidence layer: migration 0093 `analytics.company_filing_line_evidence`, `parsers/filing_line_evidence.py`, `scrooner-map probe-filing-lines`, gap reasons in `coverage_matrix.py`, structural exclusions in `coverage_snapshot.py` denominators | earlier commits, see doc `doc/learnings/2026-10-13-applicability-probe-why-concept-coverage-is-86pct.md` | evidence, not proof; never changes `has_value` |
| Migration contiguity placeholder 0094 (`select 1;`) | a204331 | CI checks migration numbers are contiguous and end with `;` |
| Nightly coverage timeouts (matrix 30 min, tag library 15, snapshot 15, plus workflow step caps 40/20/20) | 7f4eb17 | |
| Reprocess per-stage cap `STAGE_TIMEOUT_SECS` (default 1800), hung shards killed and named, script exits 1 at the end if any stage was killed | b6aa0fc | `scripts/lib/sharded.sh`, `scripts/reprocess_recent_filers.sh`, test in `tests/unit/test_sharded_runner.py` |
| Sanity workflow: write/load statement timeouts in `timeseries_check.py` and `plausibility_check.py`, step caps (plausibility 30, period completeness 75) | 8b37cca | |
| CLAUDE.md lesson on step caps / statement_timeout / deleted cancelled-run logs | 410ccf0 | |

## 3. Results of the evidence layer (snapshot 2026-10-13, 5,213 active companies)

Average concept coverage 85.61% to 86.32%. Metric coverage unchanged (74.61%, core_v1 78.32%). Only the denominators moved, covered counts did not.

| Concept | Before | After (covered / applicable) |
|---|---|---|
| goodwill | 65.7% | 99.3% (3163/3184) |
| inventory | 53.0% | 96.7% (2552/2638) |
| research_and_development | 49.8% | 97.9% (2398/2450) |
| accounts_payable | 73.8% | 94.5% (3551/3756) |
| accounts_receivable | 71.8% | 91.0% (3455/3796) |
| operating_expenses_resolved | 85.6% | 87.8% (4123/4697) |
| gross_profit_resolved | 65.9% | 74.4% (3174/4264) |
| interest_income | 50.9% | 74.5% (2453/3294) |
| cost_of_revenue_resolved | 67.1% | 73.8% (3233/4383) |

Gap reasons now in `analytics.company_data_point_coverage`: `line_not_presented_in_filing` 13,921; `line_in_filing_not_extracted` 2,722 (the real, investigable gaps); `line_presented_combined_with_others` 911.

## 4. Open work, in priority order

1. **Check tonight's scheduled runs (nightly refresh ~17:00-21:00 UTC, sanity ~19:00 UTC).** These are the only real test of the fixes above. Look at: did a coverage snapshot get written for the new date; did `reprocess_recent_filers.sh` print `run_sharded: stage '<x>' took Ns` lines and which stage (if any) exceeded 1800 s (that is the hung stage that burned the 180-min cap on Oct 13-16). If a stage keeps timing out, investigate that stage's per-company loop for a hang (dead pooler socket, no query, no output).
2. **Sanity "Report findings" step failed on 2026-10-16** (run 38950325383) and was not investigated. Check the failed-step log.
3. **Sanity gate "REGRESSED"** on `ebitda_margin`, `peg_ratio`, `quick_ratio`, `shares_outstanding`: attributed (unverified) to stale metrics during the outage. Recheck after one fully successful refresh.
4. **Work the 2,722 `line_in_filing_not_extracted` cells**, largest concept first (interest income, cost of revenue, gross profit have the most). Each candidate tag needs a coexistence check against real companies before mapping; combined lines (for example "accounts payable and accrued") must never be mapped as plain AP.
5. **`no_line_item_filed` over-claims** for about 1 gap in 5 (sample of 40, small sample). Owner is the period-completeness lane (`sanity/period_completeness.py`); see `doc/learnings/2026-10-13-phase3-spac-pattern-does-not-generalize.md`. Phase 3 (SPAC timing classifier) is closed: the premise did not generalize.
6. Hand-offs accepted by peers, not mine: cross-tag cfo `quarter_not_derived` (scrooner-64), widening conflict-latest-filed tags (scrooner-2b).
7. Flaky frontend test `components/screener/ScreenerClient.test.tsx` ("turns supported language into verified results with one click", a focus assertion) failed once in CI; passed 4/4 locally. Not my lane; owner unknown. mypy/Ruff advisory cleanup was claimed and fixed by another session (806b0a4, 6032f91).
8. **Founder decisions pending:** npm to pnpm migration (estimate only so far); whether to start Parser 4.

## 5. Gotchas found this session (also in CLAUDE.md where durable)

- Pooler `statement_timeout` default is 2 min; any full-population scan/delete must set its own. After a dropped socket the reconnect gets a fresh 2-min default and the dead session's row locks linger, so retried deletes can time out. Use `set local statement_timeout = '10min'` inside the write.
- Logs of a cancelled GitHub Actions run return 404 (BlobNotFound). Only step timing and per-stage log lines in the script survive; keep them.
- Test a shell script the way CI calls it (relative path after `cd`), and mutation-check the test.
- `check_migrations.py` needs contiguous numbers and a trailing `;`; CI skips later steps after the first failure.
- zsh word-splitting breaks space-joined path lists; use loops or `xargs`. macOS bash 3.2 has no `mapfile` or `timeout`.
- A background `xargs -P N` wrapper is not stopped by killing its workers; kill the wrapper too.
- Several sessions share one working tree and index. Commit with `git commit -- <paths>` only, push in the same turn, and `ListAgents` before heavy DB jobs. Coordination doc: `doc/planning/53_Multi_Session_Collaboration_Plan_2026-10-13.md`.

## 6. Uncommitted work in the tree that is NOT mine

Do not commit or revert these without asking the owner: `apps/admin/` (cockpit; my payload-decoding and auto-resolve edits live there, untracked), watchlist feature (`apps/backend/routers/watchlists.py`, `apps/app/.../watchlist*`, `doc/watchlist/`), many `apps/app` UI and CSS edits, `packages/design-system/src/primitives.css`, `pipeline/.../sanity/accounting_identity.py`, `sanity/yfinance_check.py`, `jobs/sanity.py`, `mapper/expanded_concepts.py`, `ai_query/screen_templates.json`, `.github/agents/`, `doc/tag-agent/`.

## 7. Useful commands

```
# CI / scheduled run state
gh run list --limit 12 --json workflowName,status,conclusion,headSha,createdAt,event
gh run view <id> --json jobs --jq '.jobs[]|"\(.name): \(.conclusion)"'
gh api repos/inyourserve/scrooner/check-runs/<job_id>/annotations --jq '.[].message'

# Coverage
cd pipeline
uv run scrooner-map probe-filing-lines --max-minutes 20
uv run scrooner-map build-coverage-matrix      # ~15 min
uv run scrooner-map snapshot-coverage
uv run pytest tests/unit -q
```

Coverage snapshot columns: `item_type` (score/concept/metric), `item_name`, `companies_covered`, `total_active_companies`, `coverage_pct`, `snapshot_date`.
