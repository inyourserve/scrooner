# Day 5 — CI and Repository Quality-Gate Evidence

> **Status:** Implementation complete; local gates verified. The first hosted GitHub Actions run remains pending until these changes are pushed.  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 5

## Outcome

Scrooner now has an offline default CI path for Python tests, the Astro production build, migration validation, documentation links, secret detection, and a narrow Python correctness lint. Expensive or currently debt-heavy checks are visible in a separate advisory job instead of being hidden or prematurely blocking every change.

Live access to the official SEC endpoint is isolated in a weekly/manual workflow. It cannot run without a declared SEC product/contact identity stored as the `SEC_USER_AGENT` repository secret.

## What was added

- `.github/workflows/ci.yml` — required and advisory pull-request/push checks
- `.github/workflows/live-sec-verification.yml` — scheduled/manual official SEC contract check
- `scripts/quality.sh` — one-command local equivalent for the required checks that do not need PostgreSQL or downloaded CI tools
- `scripts/check_migrations.py` — filename, duplicate-version, gap, emptiness, and file-termination checks
- `scripts/check_docs.py` — local Markdown target validation without network access
- `scripts/check_secrets.py` — fast repository-owned guard for common high-risk secret formats
- `scripts/ci/bootstrap_supabase.sql` — minimal `auth.users` stub used only when validating Supabase-targeted migrations on plain PostgreSQL
- `pipeline/tests/live/test_sec_official.py` — one opt-in contract test against the official SEC submissions endpoint

The default pipeline test configuration now excludes the `live` marker. This keeps normal local and CI test execution deterministic and credential-free.

## Required CI gates

| Job | Required behavior |
|---|---|
| Python | Install both locked environments; run 78 pipeline and 13 backend tests; compile sources; run Ruff correctness rules `E9,F63,F7,F82` |
| Site | Install from `package-lock.json`; produce the Astro server build |
| Repository integrity | Check all 15 migration identities; apply every migration to clean PostgreSQL 16; validate local documentation links; run the repository secret guard and Gitleaks |

The migration shell uses `set -euo pipefail` and `psql --set ON_ERROR_STOP=1`, so the job stops at the first failed migration.

## Advisory CI gates

The advisory job uses `continue-on-error` while the existing repository debt is measured and paid down:

- Full Ruff format check
- Mypy static analysis
- `pip-audit` over the locked pipeline dependency export
- `npm audit --omit=dev`

Full Ruff enforcement was intentionally not made required on Day 5: an initial scan reported 115 pre-existing findings. The narrow required rules catch syntax errors, undefined names, and invalid control-flow constructs without forcing a broad unrelated rewrite. Advisory status must be temporary; findings should be baselined, reduced, and promoted to required checks deliberately.

## Migration rehearsal and defect found

The first clean-PostgreSQL rehearsal exposed two problems in the test harness rather than in the production migration design:

1. Migration `0007_app_schema.sql` correctly references Supabase-owned `auth.users`, which does not exist in a plain PostgreSQL service.
2. A shell `for` loop could continue after an intermediate `psql` failure and return a false-green result if a later migration succeeded.

The CI-only bootstrap now provides the minimum external Supabase object, and the migration loop is fail-fast. A fresh database was then created in an isolated local PostgreSQL 14.15 cluster and the bootstrap plus migrations `0001` through `0015` all applied successfully with `ON_ERROR_STOP=1`. Hosted CI is configured to repeat the proof on PostgreSQL 16.

The bootstrap is not a product migration and must never be applied to Supabase production; Supabase remains the owner of its real authentication schema.

## Local verification

`./scripts/quality.sh` produced:

```text
pipeline: 79 collected, 1 live deselected, 78 passed in 0.52s
backend: 13 passed in 0.56s
migrations: 15 files, contiguous 0001-0015
documentation links: 192 local targets checked
secret patterns: 231 text files checked
Astro: server build complete
compileall: passed
```

The focused required Ruff rules were also run successfully before the final offline rehearsal. A later attempt to reacquire Ruff through `uvx` was blocked by the local sandbox's DNS restriction; GitHub Actions installs it in the network-enabled CI environment.

The live SEC test was collection-checked without making a network request:

```text
pipeline/tests/live/test_sec_official.py::test_sec_submissions_contract_for_known_filer
1 test collected
```

`git diff --check` also passed. One existing, non-blocking FastAPI `TestClient` dependency deprecation warning remains visible.

## Local commands

Run the normal required local suite:

```bash
./scripts/quality.sh
```

Run the official SEC check explicitly, with a real declared identity:

```bash
SCROONER_LIVE_SEC_USER_AGENT="Product Name contact@example.com" \
  pipeline/.venv/bin/pytest pipeline/tests/live -m live
```

Run clean-database validation through GitHub Actions, or reproduce it locally by creating an empty PostgreSQL database, applying `scripts/ci/bootstrap_supabase.sql`, and then applying every migration in filename order with `ON_ERROR_STOP=1` and a fail-fast shell.

## Day 5 Definition of Done

| Gate | Result |
|---|---|
| Supported Python and Node versions declared | PASS — Python 3.12 and Node 22 |
| Pipeline and backend tests required | PASS locally; hosted run pending push |
| Astro production build required | PASS locally; hosted run pending push |
| Migration sequence and real SQL application checked | PASS locally on isolated PostgreSQL 14.15; PostgreSQL 16 hosted run pending push |
| Broken migrations stop immediately | PASS — fail-fast shell and `ON_ERROR_STOP=1` |
| Documentation links checked | PASS |
| Secret detection present | PASS locally; Gitleaks hosted run pending push |
| Dependency audits visible | PASS as advisory gates; results pending hosted run |
| Default suite needs no production credentials or network | PASS |
| Live SEC verification isolated | PASS — weekly/manual workflow |
| Required versus advisory policy documented | PASS |

## Consultant assessment

Day 5 is complete as a repository implementation and local verification milestone. It is not yet proof that GitHub-hosted execution is green: that evidence only exists after the branch is pushed and both workflows run in the actual repository. Do not configure branch protection around these job names until the first hosted run confirms permissions, action availability, and repository-secret configuration.
