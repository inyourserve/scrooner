---
id: actions-concurrency-groups-keep-one-pending-run-watchers-mus
title: Actions concurrency groups keep one pending run; watchers must not pgrep their own command
kind: gotcha
tags: ci, actions, watchers
evidence: CODE-CHECKED
status: active
created: 2026-11-16
verified: 2026-11-22
---
GitHub Actions concurrency (cancel-in-progress: false) keeps one running plus ONE pending run per group; a newer dispatch cancels the older pending one. Give read-only workflows their own group (standard-extract) and chain dependent dispatches after completion. Shell watcher gotcha: 'while pgrep -f X' matches the watcher's own command line when X appears in it, so it never exits; match a pattern with a digit class (e.g. 'top100_flow.sh [0-9]') or a PID.

[2026-11-22] Merged 2026-11-22: 2026-11-01 manual cell-proof run 41321371330 held heavy-db-jobs 15:28-20:31 UTC; the nightly refresh 41334234889 was cancelled with 0 jobs because the sanity cron replaced it as the single pending run. Do not dispatch multi-hour manual proof/load runs into heavy-db-jobs 12:00-22:00 UTC; resumable runs can wait.
