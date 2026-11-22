---
id: a-multi-hour-manual-run-in-the-heavy-db-jobs-queue-gets-the-
title: A multi-hour manual run in the heavy-db-jobs queue gets the nightly refresh cancelled: GitHub keeps one pending run per group
kind: gotcha
tags: actions, concurrency, nightly
paths: .github/workflows/pipeline-refresh.yml, .github/workflows/pipeline-cells-proof.yml
evidence: CODE-CHECKED
status: superseded
created: 2026-11-02
verified: 2026-11-02
---
2026-11-01: manual cell-proof run 41321371330 held heavy-db-jobs 15:28-20:31 UTC; the refresh cron (fires ~17:00-18:30) queued as the pending run; the sanity cron created 19:44 replaced it, so refresh 41334234889 was cancelled with 0 jobs. Rule until the YAML changes: do not dispatch multi-hour manual proof/load runs into heavy-db-jobs between 12:00 and 22:00 UTC; resumable runs (scrooner-proof skip_proved, scrooner-cells --skip-loaded) can wait for the nightly to finish. Structural fix: own concurrency group plus a connection-headroom check for manual runs.

[2026-11-22 curator] SUPERSEDED (merged) into actions-concurrency-groups-keep-one-pending-run-watchers-mus: incident folded in
