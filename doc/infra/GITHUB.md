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
| `top100-coverage-hourly.yml` | hourly :17, opt-in | rebuilds `data-team/strategy/top100-coverage*.csv` from proof verdicts, read-only session | commits to `main` |
| `workflow-health-check.yml` | daily 19:41 | judges every scheduled workflow's latest runs | the alarm issue |
| `live-sec-verification.yml` | weekly Mon 11:17 | live sec.gov contract tests | nothing |
| `pipeline-tag-library.yml` | weekly Sun 23:00 | SEC tag library rebuild (old system; review pending) | dev database |

### Manual: the current production path

| File | What | Writes |
|---|---|---|
| `top100-flow.yml` | one matrix job per company, running `scripts/top100_flow.sh`: docmap-load, structural-load, tagmap-plan, proof, era-guard, certified-guard; per-company display gate and a certification request in `approvals/requests/` | **production**; commits the requests |
| `pipeline-cells-proof.yml` | `scrooner-proof` over a company list | proof tables |
| `pipeline-fsn-extract-predecessors.yml` | FSN extract for predecessor CIKs | Supabase Storage |

### Manual: the old path (retirement proposed in the 11-16 audit, founder decides)

`pipeline-fsn-write.yml` (production), `pipeline-fsn-cohort.yml`, `pipeline-fsn-pilot.yml`, `pipeline-cells-load.yml` and `cells-load-stage.yml` (production), `pipeline-certify.yml`, `pipeline-recompute.yml` (production), `bs-port-gate.yml`, `cf-port-regression-gate.yml`.

## Branches

Agents push `work/<owner>/<topic>` and land through a PR. Merged branches are deleted. Verifier evidence branches use `verify/<date>-<topic>`. Long-term history goes under `archive/`.

## Generated files in git

Git keeps two kinds of file: inputs the code reads (for example the resolver CSVs in `data-team/tags/line_map/`) and evidence a decision cites. Run outputs go to workflow artifacts or Supabase Storage. A file over 10 MB needs a reason in its commit message.
