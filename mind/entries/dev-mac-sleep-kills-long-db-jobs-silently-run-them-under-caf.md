---
id: dev-mac-sleep-kills-long-db-jobs-silently-run-them-under-caf
title: Dev Mac sleep kills long DB jobs silently: run them under caffeinate -i -s
kind: gotcha
tags: mac, sleep, caffeinate, loader, pooler, ssl
paths: pipeline
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
2026-11-01: four scrooner-cells plan shards started 03:20 IST died at zero companies; logs written only on wake at 11:14 IST with 'SSL SYSCALL Operation timed out' on the first query. The Mac slept right after launch and the pooler connections were dead on wake; an earlier 02:52 drop mid-run had the same cause. 8 hours lost with no error until wake. Run any long local job under 'caffeinate -i -s <cmd>', and check pg_stat_activity for active queries rather than trusting that a job is running.

[2026-11-01] Merged from dev-mac-sleep-kills-every-long-db-job-ssl-operation-timed-ou: symptom is SSL 'Operation timed out' on wake and log lines stamped hours later; the pooler also drops idle connections after long parsing, so reconnect (db/connection.py run_write_with_reconnect) and set statement_timeout for the session.
