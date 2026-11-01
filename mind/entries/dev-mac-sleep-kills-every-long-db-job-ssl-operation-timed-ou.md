---
id: dev-mac-sleep-kills-every-long-db-job-ssl-operation-timed-ou
title: Dev Mac sleep kills every long DB job: SSL 'Operation timed out' on wake, logs stamped hours later
kind: gotcha
evidence: DATA-INFERRED
created: 2026-11-01
verified: 2026-11-01
status: superseded
---
2026-11-01: six cell-loader plan runs died with 'could not receive data from server: SSL SYSCALL error: Operation timed out'. The DB was healthy (5 backends, select 1 in 2.7s); the Mac had slept (03:20 start, logs written 11:14 on wake, zero companies done). Before blaming the pooler, compare the log mtime with the job's start time. Wrap any multi-hour local job in /usr/bin/caffeinate -i -s (as run_chunked.sh/the loader shards now are), and make it reconnect-and-redo per company so a drop costs one company, not the run.

[2026-11-01 curator] MERGED into dev-mac-sleep-kills-long-db-jobs-silently-run-them-under-caf.
