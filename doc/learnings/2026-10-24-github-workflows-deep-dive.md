# GitHub workflows deep dive: what each does, why it exists, what is duplicated, what we learn (2026-10-24)

Author: scrooner-7b. Read-only analysis; nothing was run, changed or committed. Evidence labels: **CODE** = read from `.github/workflows/*.yml` and the scripts they call on origin/main; **RUNS** = `gh run list/view` on 2026-10-24; **LOG** = read from a run's logs. Run counts are what `gh` returned (it lists a limited history), stated with each number.

## 1. Inventory (10 workflows)

| Workflow | Trigger | Touches prod DB? | What it does | Why it exists | Importance | Health (RUNS) |
|---|---|---|---|---|---|---|
| `pipeline-refresh.yml` | daily cron 12:23 UTC + manual | yes, heavy (3 jobs) | (1) index latest SEC filing day, reprocess Normalizer+Mapper for recently-filed companies; (2) tickers, Alpaca prices, freshness gate, filing-line evidence, coverage matrix, tag candidates, coverage snapshot; (3) recompute price-dependent metrics + screener snapshot | the only thing that keeps the product current after the one-time full-population build | CRITICAL (product freshness) | **0 successes in the last 30 runs; last green 2026-08-20** (71 runs listed) |
| `pipeline-sanity.yml` | daily cron 15:17 UTC + manual | yes, heavy | yfinance ratio cross-check, investigate/auto-fix, rendered-report parsers (revenue, cost of revenue), time-series check, metric plausibility, period completeness, yfinance statements rotation, report | external and internal correctness monitor; feeds `data_incident` | HIGH (the correctness alarm) | **no green run in the 45 runs listed (oldest 2026-09-09)** |
| `pipeline-frames-check.yml` | weekly Mon 06:05 | yes | SEC Frames self-consistency fetch, compare, report | independent source check against SEC's own aggregate | MEDIUM | green 5 weeks in a row, then **failed 2026-10-19** |
| `pipeline-tag-library.yml` | weekly Sun 23:00 + manual | yes, heavy | rebuild company x tag library, concept lineage, gap leads; list top unmapped tags for total debt | evidence base for tag mapping and gap decisions (moat input) | MEDIUM-HIGH | only run listed (2026-10-24) **failed** (exit 2) |
| `pipeline-recompute.yml` | manual only | yes, very heavy (matrix shards) | 5 phases: normalize+resolve per shard, population-wide fills, metrics per shard, screener snapshot, tag library | the "apply a rule change to everyone" tool | HIGH when a fix ships | 3 of the last 10 cancelled, 1 failed; runs 40-543 min |
| `pipeline-certify.yml` | manual only | yes (dry-run default) | run certification invariants I1-I11 shard by shard over the top-1000, upload findings | the new "is it certifiable" gate | NEW, central to the plan | **never run (0 runs)** |
| `workflow-health-check.yml` | weekly Mon 06:30 | no | for every scheduled workflow, check its last 5 runs and fail on a failure pattern | meta-alarm: "nothing paged" is not "healthy" | MEDIUM | **red every week since 2026-09-14** (it is reporting the failures above, not itself broken) |
| `live-sec-verification.yml` | weekly Mon 11:17 | no | live contract tests against the official SEC endpoints | catches SEC format/URL/User-Agent changes before the pipeline does | MEDIUM, cheap | **green 9 of 9 listed weeks**, 0-1 min |
| `ci.yml` | every push (any branch) | no (clean test Postgres) | pipeline+backend tests, Next.js lint/test/build, replay every migration on clean Postgres, backup-restore round trip, docs-link, secret scans, gitleaks, advisory format/type/audit | stops broken code, divergent schema and leaked secrets from reaching main | CRITICAL (engineering safety) | **38 of the last 100 runs failed**, across 35 branches |
| `mind.yml` | push touching `mind/**`, `CLAUDE.md`, `data-team/**` | no | mind unit tests, advisory lint | keeps the shared team memory working | LOW | green in the last 10 |

Shared control: one **concurrency group `heavy-db-jobs`** (CODE) is used by refresh, sanity, frames, tag-library, recompute and certify, so GitHub runs them one at a time. It exists because the database restarted on 2026-10-18 and 2026-10-19 when these overlapped (comment in the files). `ci`, `live-sec`, `health-check` and `mind` are outside it.

## 2. What we learn

**L1. The two daily jobs that matter have been red for weeks, so red is the baseline and a real regression is invisible.** (RUNS) Refresh: 0 successes in 30 runs, last green 2026-08-20. Sanity: no success in 45 runs back to 2026-09-09. The weekly health check has failed every Monday since 2026-09-14, correctly. A monitor that is always red carries no information; nobody can tell today's new break from the standing one.

**L2. Most of the red is a gate firing, not the work failing, and the gates are coupled to job health.** (LOG)
- Refresh, 2026-10-23 run: the freshness report shows every source `fresh` (companyfacts 1.2 h old, filing index 1.2 h, backlogs fresh) and a single alert, `unresolved_dead_letters:normalizer:3`; `--fail-on-alert` then fails the whole operational job. Three dead letters turn the entire nightly red.
- Sanity, 2026-10-23 run: the cross-check itself finished (`considered=750 critical=0 major=1810 minor=925`), yet the last step is `report --fail-on-findings`, so a normal day with 1,810 majors from the yfinance comparison is red by construction.
- Separately there are real failures: statement timeouts (`QueryCanceled` in `investigate_open_findings`, time-series, period completeness), and dropped connections (`SSL connection has been closed`, `could not receive data from server`) in refresh's reprocess and sanity's time-series write.
So one status bit mixes three different things: infrastructure failure, a data-quality gate, and an expected-nonzero findings count.

**L3. One serial queue plus long jobs means the day is spent waiting, and cron times no longer mean anything.** (CODE+RUNS)
- Refresh runs lately took 110-378 min, sanity 91-414 min (durations from created to updated, so they include time spent waiting in the group). Together they can occupy 4-13 of 24 hours; recompute (up to 543 min) and manual dispatches queue behind them.
- GitHub keeps ONE pending run per concurrency group (the files' own comment), so a newer queued run replaces an older queued one: a daily job can be silently dropped when something long is ahead of it.
- The comment "offset from refresh so they never compete" is obsolete: the group serializes them. Observed: refresh scheduled 12:23 UTC started 17:18-18:45 UTC on several days; sanity scheduled 15:17 UTC created 19:xx. Data is stale for the first hours of each day and the gap is variable.
- Root cause named in the files: the database is small (256 MB shared buffers) and restarts when jobs overlap, so serialization is a workaround for capacity, not a design.

**L4. Duplicates (same work done in more than one place).** (CODE)
1. **`build-tag-library`**: in `pipeline-recompute.yml` Phase 5 and in `pipeline-tag-library.yml` (weekly); it also used to run inside refresh until 2026-10-23, when it was moved out because it ran past its cap. Two live owners now.
2. **Screener snapshot**: `scrooner-screen build-snapshot` in recompute Phase 4 and, via `refresh_valuations.sh`, in the daily refresh. Intended (manual vs daily) but it is the same product artifact with two writers.
3. **Normalize+map stage lists**: `reprocess_recent_filers.sh` (daily, recent filers, sharded, budgeted) and `pipeline-recompute.yml` (manual, full population). Same stages, different scope and different shard code (a bash helper vs a GitHub matrix). Not wasted work, but two implementations of "run stage X sharded" that can drift.
4. **Boilerplate**: the checkout / setup-uv / setup-python / `uv sync` block repeats 3 times in refresh, 5 in recompute, plus "Require production configuration" in 4 workflows and the same company-shard selection Python snippet twice in recompute (resolve and metrics jobs).
5. **Source checkers that overlap in purpose**: Frames check (SEC aggregate), sanity yfinance ratio check, yfinance statements rotation, live SEC contract tests, plus the new certify invariants and the coverage matrix. All ask "is a stored number right?" from different angles; none replaces another, but their findings are stored in separate tables (`frames_consistency_check`, `data_sanity_check`, `statement_comparison_finding`, `period_gap`, certify findings) with `data_incident` as the only join.
6. **Health watchers**: refresh's freshness gate, the weekly health check, and sanity's report all say "something is wrong"; they overlap in signal and differ in cadence.

**L5. Cheap, green, high-value workflows are the model.** (RUNS) `live-sec-verification` (0-1 min, 9/9 green) and `mind.yml` do one narrow thing and either pass or fail cleanly, with no DB. They are the opposite of the nightlies.

**L6. CI is the safety net, and it is noisy.** (RUNS) 38 of the last 100 CI runs failed, across 35 branches; it triggers on every push to every branch (no PR trigger listed), so parallel agent branches multiply runs. The migration replay on a clean database is the check that catches live-vs-main schema divergence (CLAUDE.md says so); keep. `advisory-quality` is `continue-on-error`, so its findings never block; the repo's own notes say a green-looking tail can hide an earlier crashed step.

**L7. `pipeline-certify.yml` has never run, and it will join the same queue.** (RUNS+CODE) It is dry-run by default, runs 150 minutes max, one shard at a time, and uses the `heavy-db-jobs` group, so every certification pass competes with the nightlies for the same single lane.

**L8. Observability has known holes.** (CODE comments+LOG) Logs of cancelled runs are deleted, so per-stage timing lines are the only record; steps use `if: always()` heavily, so later steps run and fail after the first failure and the run page shows ten failed steps for one cause (the sanity run listed ten failed steps for one early failure); log lines appear under "UNKNOWN STEP" through `gh`, so step attribution needs the web UI.

## 3. Importance tiers (author's judgement, from the evidence above)
- **Must stay green daily for the product:** refresh job 1 (index + reprocess) and the freshness it produces; prices; valuations/snapshot.
- **Correctness alarm (high value, currently unusable as an alarm):** sanity, frames, certify, health check.
- **Evidence builders for the moat (can be weekly):** tag library, filing-line evidence, coverage matrix/snapshot.
- **Engineering safety (keep, reduce noise):** CI.
- **Cheap contract tests (keep as is):** live SEC verification, mind.
- **Manual power tools:** recompute, certify.

## 4. Open questions this raises (not decisions)
1. Should "job failed" and "gate fired" be separate signals? Today a gate alert and a crash both turn the same job red (L2).
2. Is the serial queue the right permanent design, or a stop-gap for database capacity (L3)? What does the daily critical path look like if only job 1 is guaranteed a slot?
3. Which of the five source checkers' results does anyone read daily? If a check's output has no consumer, it only costs queue time (L4.5).
4. Who is the single owner of the tag library and the screener snapshot (L4.1-4.2)?
5. Should certify findings use the same incident table as sanity and Frames so there is one place to look?

## 5. What this review did not do
- No run was triggered; run durations include queue time and were not split into wait vs execution.
- Only the latest failing runs were read in logs (refresh 2026-10-23, sanity 2026-10-23, tag-library 2026-10-24); older failures may have other causes.
- Runner-minute cost and secrets usage were not measured.
- `gh` returned limited history (71 refresh runs, 45 sanity runs), so "never" statements mean "in the history listed".
