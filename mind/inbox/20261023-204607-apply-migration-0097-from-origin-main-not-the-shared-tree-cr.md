---
id: apply-migration-0097-from-origin-main-not-the-shared-tree-cr
title: Apply migration 0097 from origin/main, not the shared tree: create table if not exists makes the stale local file win silently
kind: gotcha
tags: migrations, 0097, certification
paths: pipeline/db/migrations/0097_certification_tables.sql
evidence: CODE-CHECKED
created: 2026-10-23
verified: 2026-10-23
---
The shared tree holds an older 0097 (invariant IN ('I1'..'I11'), no provenance columns). Because 0097 uses create table if not exists, applying the local file first turns the origin version into a no-op and the regex ^I[0-9]+$ and rule_id/rule_version/suite_version/certify_run_id/suite_run_at columns never land. Apply from git show origin/main:pipeline/db/migrations/0097_certification_tables.sql, then verify information_schema.columns and pg_get_constraintdef. Production migrations are manual psql (no ledger). Use set lock_timeout='5s' and retry: 0096 takes ACCESS EXCLUSIVE on company_data_point_coverage (waits behind a coverage rebuild), 0097's FKs take SHARE ROW EXCLUSIVE on core.company. Order: E0 extract, 0097, 0096, build-coverage-matrix + snapshot-coverage, E1, certify dry-run. runner.py INSERT_FINDING does not yet write the provenance columns: wire them before the first --apply.
