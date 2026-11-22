---
id: ci-ran-none-of-the-db-backed-tests-until-2026-11-04-python-j
title: CI ran none of the DB-backed tests until 2026-11-04: Python job had no test DB, and tests that drop core/analytics wrecked a shared test database
kind: gotcha
tags: ci, tests, postgres
paths: .github/workflows/ci.yml, pipeline/tests/conftest.py
evidence: CODE-CHECKED
status: superseded
created: 2026-11-01
verified: 2026-11-01
---
The Python tests job set no SCROONER_TEST_DATABASE_URL, so about 107 DB-backed tests were skipped on every CI run (a CI log showed '107 skipped'); 'CI Postgres job ran the tests' was wrong, the Postgres service only lived in the migrations job. Fixed in db08874: Postgres 16 service, bootstrap + every migration, URL set, -rs to list skips. Second trap found on the first run: test_expected_period_sql, test_shared_accession_sql and test_slot_is_not_presented drop the REAL core/analytics schemas, so tests running after them skipped with 'needs the migrated schema'. isolated_database_url now creates a throwaway copy per test (create database ... template <test db>, dropped after). Local Postgres 14 cannot replay migration 0080 (NULLS NOT DISTINCT needs 15+), so verify DB tests on a branch run in CI. Never count a skip as green.

[2026-11-22 curator] RETIRED: historical, fixed 2026-11-04 (CI runs DB tests against Postgres 16, per CLAUDE.md); kept for history only
