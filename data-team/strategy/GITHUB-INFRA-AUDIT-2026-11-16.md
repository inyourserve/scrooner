# GitHub infrastructure audit, 2026-11-16

Read-only audit by the GitHub-ops cloud session (data collected 2026-11-15 ~20:40 UTC with the GitHub API and `git`). Raw run data is not committed; the numbers below cite run ids. Fixes made so far are in PR #15.

## Summary counts

- 20 workflows. 4 are healthy and in daily use, 3 are red on a schedule, 9 have had no run for a week or more, 2 have never run.
- 67 failed runs in 7 days: ci.yml 48 (23 on main), refresh 7, sanity 7, cells-proof 2, fsn-write 2, health-check 1. 433 cancelled runs (428 are ci.yml concurrency supersessions, median 68 s: expected).
- 369 remote branches: 99 merged into main, 85 more whose every commit is already in main (patch-equivalent), 185 with unique work. 164 had no commit for 7+ days.
- 2 open PRs (#4, #6), 0 open issues.
- About 323 MB packed. The largest history items are generated outputs (below).

## 1. Workflows

| Workflow | Trigger | Last 20: ok/fail/cancel | Median time | Last run | Verdict |
|---|---|---|---|---|---|
| ci.yml | push, PR | 8/0/9 (main now green) | 4 min | live | KEEP, FIX: path filter + timeouts (PR #15) |
| mind.yml | push/PR on mind, data-team | 20/0/0 | 18 s | live | KEEP |
| top100-flow.yml | dispatch (prod writes) | 3/0/1 | 34 min | 11-15 | KEEP, the production pipeline |
| top100-coverage-hourly.yml | :17 hourly, opt-in var | never ran | - | - | KEEP, confirm first run (var set 20:27Z) |
| pipeline-refresh.yml | nightly 12:23Z | 6/13/1 | 1 h 57 | 11-15 red | FIX: two root causes fixed in PR #15 |
| pipeline-sanity.yml | nightly 15:17Z | 5/14/0 | 2 h 08 | red since 10-31 | FIX: real data regression, needs an owner (see 2) |
| workflow-health-check.yml | weekly | 0/11/0 | 11 s | red always | FIX: it fails whenever any scheduled workflow ever failed, so it is a permanent alarm. Make it judge each workflow's latest run only |
| live-sec-verification.yml | weekly | 12/0/0 | 18 s | 11-09 | KEEP |
| pipeline-cells-proof.yml | dispatch | 15/3/2 | 5 min | 11-14 | KEEP while proof runs outside top100-flow; then MERGE-INTO top100-flow |
| pipeline-fsn-extract-predecessors.yml | dispatch | 3/0/1 | 4 min | 11-09 | KEEP (predecessor backfill) |
| pipeline-fsn-write.yml | dispatch (prod writes) | 5/4/1 | 22 min | 11-12 | RETIRE candidate: the old 1,000-company FSN-store write, replaced by top100-flow (founder 11-11). Founder decides |
| pipeline-fsn-cohort.yml | dispatch | 3/2/0 | 43 min | 11-10 | RETIRE candidate, same path |
| pipeline-fsn-pilot.yml | dispatch | 12/1/4 | 16 min | 11-09 | RETIRE candidate, same path |
| pipeline-cells-load.yml + cells-load-stage.yml | dispatch (prod writes) | 1/0/0 | 37 min | 11-01 | RETIRE candidate (per-family patch packages superseded 11-04) |
| pipeline-certify.yml | dispatch | 1/5/0 | 1.5 min | 10-25 | RETIRE candidate: certification now comes from top100-flow requests |
| pipeline-recompute.yml | dispatch (prod writes) | 9/4/4 | 3 h 06 | 10-21 | Ask Engineering: still needed for metric recompute after the new path writes? |
| pipeline-tag-library.yml | weekly Sun 23:00Z | 1/1/2 | 3 h 00 | 11-09 | Ask Engineering: old-system tag library; 3 h a week, mostly not green |
| bs-port-gate.yml | dispatch | 0/2/0 | 27 min | 11-02 | RETIRE: old lane gate, never passed |
| cf-port-regression-gate.yml | dispatch | 0/1/0 | 1 h 27 | 11-01 | RETIRE: old lane gate, never passed |

Also seen: runs of `sec-reads-*.yml` workflows that are not in `.github/workflows` on main (dispatched from branches, 11-13). Workflows should live on main only.

## 2. CI failures, last 7 days, by root cause

| Cause | Runs | Evidence |
|---|---|---|
| Real bug, main CI | 13 in a row on 11-14 06:13-08:41, plus 7 others | `test_fsn_new_path_guard.py:71` (new commands not classified), `test_detector_version_pin` (43565280685, 43603264737), `test_structural_loader_db.py:186` (3 runs), `test_fsn_dim_note.py:87` (43621127026), `test_proof_zstd_guard.py:88` (43440567199). All fixed by later commits; the pattern is pushing to main before CI. |
| Real bug, nightly refresh | 4 nights (11-12..15) | `incomplete placeholder: '%'` and `UniqueViolation (net_interest_income)`: fixed in PR #15 |
| Data regression, sanity gate | 7 nights | net_margin missing 842 → 2,363; gross_margin 2,117 → 2,918; operating_margin 1,272 → 1,815 (42516501636, 43634856686). Owner needed: decide whether this is the expected effect of the new-path writes (re-baseline) or a real loss |
| Flaky | 2 | `ScreenerClient.test.tsx` sort test (43230914867, 43426064178) |
| Infrastructure | 5 | refresh over its 7,000 s budget (11-08, 11-09); cells-proof connection preflight refused (2); uv download HTTP 504 (1) |
| Config | 3 | fsn-write restore missing 3 settings (fixed e3d26b9f); fsn-write dispatched with a short SHA; soupsieve 2.9.2 CVE in the advisory audit |
| Branch CI | 25 | mostly work branches (migration numbering, docs links); not opened individually |

## 3. Branches

- Safe to delete (merged into main): 99. Also cleanly deletable (all commits already in main by patch): 85. List: `git branch -r --merged origin/main` and `git cherry origin/main <branch>` with no `+` lines.
- Unique work: 185, of which most are `work/*` (187 total with that prefix), `verify/*` (65), `archive/*` (23), `review/*` (16), `land/*` (13). Plus 5 `worktree-agent-*` branches left by agent worktrees, `tmp/*` (3), `backup/*` (2).
- Proposal (founder): delete the 184 merged or patch-equivalent branches; rename kept history under `archive/`; agents push `work/<owner>/<topic>` and delete on merge. Nothing deleted by this audit.

## 4. Open PRs and issues

- PR #4 (CF gaps) and PR #6 (derived total liabilities): 663 and 686 commits behind main, one conflict each, built for the old fsn_store pilot/write path. Recommend close as superseded once owners confirm the logic is in the resolver/structural loader (derived TL is: dd7995b5).
- PR #15 (this session): refresh fix + CI path filter.
- No issues: work is tracked in markdown boards, not GitHub issues. Fine; no change proposed.

## 5. Repo sprawl (generated outputs in git)

| Path | Size now | Note |
|---|---|---|
| `data-team/tags/line_map/` | 56 MB, 180 files; `resolver-all110-*.csv` 36 MB, rewritten in 41 commits | The loader reads it, so it must be reachable by CI and the flow. Proposal: keep the latest in git, compressed (`.csv.gz`), or publish as a release asset pinned by SHA in the loader |
| `data-team/tags/exam/` | 33 MB, 1,912 files | prediction/exam evidence: keep (it proves blind-exam timing via commit time) |
| `data-team/strategy/top100-coverage.csv` | 9 MB, will be committed hourly | 24 commits/day of a 9 MB file. Proposal: hourly job commits only the summary CSV; the full CSV goes to a workflow artifact, plus a daily commit |
| `pipeline/scripts/slot_records/results/cf_da_capex_v10..v20/` | ~5.5 MB each, 11 versions | superseded dry-run outputs: move to artifacts or delete old versions (history keeps them) |
| `doc/data-moat/team/backups/split_rebase_dryrun_*.csv.gz` | 65 + 10 + 4.5 MB in history | old backups: should be storage objects, not git |
| `data-team/strategy/team/`, `strategy/data/`, `scoreboard/` | 11 + 8 + 5 MB | reports and evidence: keep |

Rule proposed: git keeps inputs the code reads and evidence a decision cites; run outputs go to workflow artifacts (90-day) or Supabase Storage; nothing over 10 MB is committed without a reason in the commit message.

## 6. Scheduled jobs

- `pipeline-refresh` (daily) and `pipeline-sanity` (daily): needed, both red; refresh fixed in PR #15, sanity needs a data owner.
- `workflow-health-check` (weekly): permanently red, gives no signal. Fix as above.
- `pipeline-tag-library` (weekly, 3 h): ask Engineering if it still feeds anything.
- `live-sec-verification` (weekly): green, useful.
- `top100-coverage-hourly`: new; watch size (section 5).

## Top 10 actions

1. Merge PR #15 (nightly refresh back to green; Next.js suite only on app changes).
2. Sanity gate: Engineering decides re-baseline vs real regression (margins missing up 1,500 since 11-08).
3. Fix workflow-health-check to judge latest runs only (PR, this session).
4. Stop red pushes to main: 13 consecutive red CI runs on 11-14. Proposal: agents push to a branch and land through a PR with auto-merge on green (branch protection change: founder).
5. Retire the old-path workflows: fsn-write, fsn-cohort, fsn-pilot, cells-load(+stage), certify, bs-port-gate, cf-port-regression-gate (founder; 3 of them can write production).
6. Delete 184 merged or patch-equivalent branches and the 5 `worktree-agent-*` branches (founder).
7. Hourly coverage: commit only the summary hourly; the 9 MB CSV as an artifact (Engineering, after its first run).
8. Close PRs #4 and #6 as superseded (owners confirm).
9. Move superseded run outputs (`cf_da_capex_v10..v19`, split-rebase backups) out of the tree; set the 10 MB commit rule (founder).
10. `doc/infra/GITHUB.md`: one map of every workflow, its owner, trigger and what it writes (this session, next).
