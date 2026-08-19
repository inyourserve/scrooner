# Day 1 — Automated Test Foundation Evidence

> **Status:** Complete  
> **Date:** 2026-08-18  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 1

## Outcome

Scrooner now has executable offline test suites for the pipeline and backend. Before this work, both test directories collected zero tests. The default suites now collect six meaningful tests across the five required boundaries.

## Implemented

- Registered strict `unit`, `integration`, and `live` pytest markers in both Python projects.
- Added deterministic fixtures/factories for companies, filings, periods, facts, canonical facts, metric values, prices, Decimals, dates, timestamps, and UUIDs.
- Added a minimal frozen SEC Company Facts fixture carrying accession `0000320193-25-000079`.
- Added a guarded `isolated_database_url` fixture:
  - Requires explicit `SCROONER_TEST_DATABASE_URL` configuration.
  - Requires the database name to contain `test`.
  - Refuses a URL equal to `DATABASE_URL`.
  - Skips rather than falling back when no test database exists.
- Added explicit unreachable test environment values so collection of pure tests cannot load developer or production credentials.
- Added offline smoke coverage for:
  - Normalizer unit extraction/canonicalization
  - Mapper metric-definition completeness and input lineage shape
  - Screener validation, null exclusion, and ranking
  - AI Query interpretation and fail-safe ambiguity handling
  - Backend `/health` request contract
- Added `TESTING_STRATEGY.md` with commands, isolation rules, fixture guidance, and the regression-test policy.

## Verification results

### Pipeline

Command:

```bash
pipeline/.venv/bin/pytest pipeline/tests
```

Result:

```text
collected 5 items
5 passed in 0.31s
exit code: 0
```

### Backend

Command, run from `apps/backend`:

```bash
.venv/bin/pytest tests
```

Result:

```text
collected 1 item
1 passed in 0.53s
exit code: 0
```

The backend run reports one dependency deprecation warning from FastAPI's `TestClient` import path. It does not affect correctness, but it should be addressed during dependency/CI hardening rather than hidden.

### Failure-path proof

The Screener null-exclusion assertion was deliberately inverted from expecting `False` to expecting `True`. The focused pytest invocation reported one failed test and exited with code `1`. The correct assertion was then restored and the complete suite passed.

This proves a regression in a protected behavior makes the command fail non-zero.

## Day 1 Definition of Done

| Gate | Result |
|---|---|
| Pipeline and backend commands collect and run tests | PASS — 5 + 1 tests |
| Default run requires no external network | PASS — pure functions and in-process TestClient only |
| Test data cannot write production tables | PASS — no default test opens a database; guarded future DB fixture refuses ambiguous targets |
| At least five meaningful smoke tests pass | PASS — six tests across five boundaries |
| Deliberate assertion failure exits non-zero | PASS — exit code 1 observed |

## Scope boundary

Day 1 establishes the test harness; it does not claim broad regression coverage. Days 2–4 must convert the previously documented financial-period, calculation, query, and authorization bugs into comprehensive automated tests. No live SEC, Supabase, Alpaca, or production-database call was made during Day 1 verification.

