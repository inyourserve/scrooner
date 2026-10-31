---
id: dry-run-a-multi-commit-pipeline-stage-neutralise-conn-commit
title: Dry-run a multi-commit pipeline stage: neutralise conn.commit, inspect inside the txn, then rollback
kind: howto
tags: dry-run, psycopg, testing, stages
paths: pipeline/src/scrooner_pipeline/jobs/map.py
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
Most mapper stage functions call conn.commit() internally several times, so a plain rollback at the end proves nothing. Working pattern (jobs/map.py _run_resolve_stage, 2026-10-31): open one psycopg connection, set statement_timeout, assign conn.commit = lambda: None, run the stage function(s) once or twice, query the evidence you need INSIDE the same transaction (rows that would exist, before/after snapshots keyed by (company, concept, period) to prove idempotency), then conn.rollback(). Scope writes to the companies under test so row locks stay small while peers work the same DB.
