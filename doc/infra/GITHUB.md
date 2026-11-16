# GitHub infrastructure map

One page for every workflow: what it does, what triggers it, what it writes, and who owns it. Keep it current. A workflow that is missing from this page, or a row describing a workflow that no longer exists, is a bug.

Last full audit: [`GITHUB-INFRA-AUDIT-2026-11-16.md`](../../data-team/strategy/GITHUB-INFRA-AUDIT-2026-11-16.md).

## Rules

- Production writes run only from `workflow_dispatch` on `main`. Never from a schedule, a fork, or another branch. Only the founder dispatches them.
- Every job that touches the database shares the `manual-db-jobs` concurrency group, or checks `pipeline-refresh` itself (root `CLAUDE.md`, connection budget). Never pass a short SHA as a ref.
- A workflow lives on `main`. Branch-only workflows (`sec-reads-*`, 11-13) can't be found or reviewed.
- PR CI targets under 10 minutes. Each suite runs only when its area changes (`scripts/ci/changed_areas.py`). Python runs for `data-team/` and `doc/` changes too, because the pipeline reads those files.
- Red `main` is fixed within the hour, at the root. Never skip, disable or quarantine a test to get green.
- `workflow-health-check` keeps one open issue, "Scheduled workflow failing", while any scheduled job has a failure pattern. It closes the issue on recovery.

## Secrets

`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SEC_USER_AGENT`, plus `ALPACA_API_KEY` and `ALPACA_API_SECRET` for the refresh only. Repository variable `TOP100_COVERAGE_HOURLY` turns on the hourly export.

## Workflows

### Every push and PR

| File | What | Writes |
|---|---|---|
| `ci.yml` | `changes` job, then: Python tests on Postgres 16 with every migration applied (also lint and compile); Next.js lint, test and build; migrations, docs links and secret scans; advisory ruff, mypy and dependency audits | nothing |
| `mind.yml` | tests and lint for the shared team memory (`mind/`) | nothing |

### Scheduled

| File | When (UTC) | What | Writes |
|---|---|---|---|
| `pipeline-refresh.yml` | daily 12:23 | the nightly SEC refresh: collect, normalize, map, coverage | dev database |
| `pipeline-sanity.yml` | daily 15:17 | yfinance cross-check gate (validation only, never a stored value) | sanity tables |
| `top100-coverage-hourly.yml` | hourly :17 (opt-in var) and after every top100-flow run | rebuilds `data-team/strategy/top100-coverage*.csv` from proof verdicts, read-only session | commits the summary to `main` every hour and the full CSV daily (00:17) or on dispatch; the full CSV is also an artifact each run (90 days) |
| `workflow-health-check.yml` | daily 19:41 | judges every scheduled workflow's latest runs | the alarm issue |
| `live-sec-verification.yml` | weekly Mon 11:17 | live sec.gov contract tests | nothing |
| `pipeline-tag-library.yml` | weekly Sun 23:00 | SEC tag library rebuild (old system; review pending) | dev database |

### Manual: the current production path

| File | What | Writes |
|---|---|---|
| `top100-flow.yml` | one matrix job per company, running `scripts/top100_flow.sh`: docmap-load, structural-load, tagmap-plan, proof, era-guard, certified-guard; per-company display gate and a certification request in `approvals/requests/` | **production**; commits the requests |
| `pipeline-cells-proof.yml` | `scrooner-proof` over a company list | proof tables |
| `pipeline-fsn-extract-predecessors.yml` | FSN extract for predecessor CIKs | Supabase Storage |

### Retired 2026-11-16 (founder-approved cleanup)

These are disabled: every root job is skipped unless the repository variable `ALLOW_RETIRED_WORKFLOWS` is `'true'`. The files will be deleted from 2026-11-23, provided nothing needed them during the week.

| File | Was |
|---|---|
| `pipeline-fsn-write.yml` | old 1,000-company FSN-store production write |
| `pipeline-fsn-cohort.yml` | FSN-store cohort dry run |
| `pipeline-fsn-pilot.yml` | FSN-store pilot |
| `pipeline-cells-load.yml` and `cells-load-stage.yml` | per-family cell-file production load (superseded 11-04) |
| `pipeline-certify.yml` | old certification invariants (now top100-flow requests) |
| `bs-port-gate.yml`, `cf-port-regression-gate.yml` | old lane port gates, never passed |

### Manual, under review

`pipeline-recompute.yml` (production; full-population metric recompute, last run 10-21): Engineering to say whether the new path still needs it.

## Protecting `main` (founder approved 2026-11-16; needs the repository admin)

Why: 13 red CI runs in a row on `main` on 11-14, all from direct pushes made before CI ran. The settings below make every change land through a PR that auto-merges once CI is green.

1. Settings → General → Pull Requests: tick **Allow auto-merge** and **Automatically delete head branches**.
2. Settings → Rules → Rulesets → **New branch ruleset**:
   - Name: `main`. Enforcement: **Active**. Target branches: **Include default branch**.
   - Tick **Restrict deletions** and **Block force pushes**.
   - Tick **Require a pull request before merging**, with 0 required approvals. Agents can't approve, and Claude Approvals or CI is the gate.
   - Tick **Require status checks to pass**, then add `Detect changed areas`, `Python tests and correctness lint`, `Migrations, documentation, and secrets` and `Next.js frontend tests and production build`. A job skipped by the change filter counts as passing.
     - Leave **Require branches to be up to date** off. Many sessions land at once; with it on, every PR would need a rebase after each merge.
   - **Bypass list:** add **GitHub Actions** (app) with "Always" (or "For pull requests only" if the next item is used instead). This lets the hourly coverage commit and the top100-flow certification requests keep pushing straight to `main` with `GITHUB_TOKEN`.
     - If the app can't be added, route both through a PR: set `gh pr merge --auto`, with a bot token or a GitHub App, since `GITHUB_TOKEN` PRs don't trigger CI.
3. Agents then land work like this: `git push origin HEAD:work/<owner>/<topic>`, then `gh pr create --fill`, then `gh pr merge --auto --squash`. Nothing pushes to `main` directly any more. Update root `CLAUDE.md` ("A commit on main is pushed in the same turn") at the same time.

## Branches

Agents push `work/<owner>/<topic>` and land through a PR. Merged branches are deleted. Verifier evidence branches use `verify/<date>-<topic>`. Long-term history goes under `archive/`.

## Generated files in git

Git keeps two kinds of file: inputs the code reads (for example the resolver CSVs in `data-team/tags/line_map/`) and evidence a decision cites. Run outputs go to workflow artifacts or Supabase Storage. CI rejects any NEW file over 10 MB (`scripts/ci/check_large_files.py`) unless it is listed, with a reason, in `.github/large-files-allowlist.txt`. History is not rewritten; old blobs stay.
