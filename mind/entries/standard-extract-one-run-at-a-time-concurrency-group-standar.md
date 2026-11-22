---
id: standard-extract-one-run-at-a-time-concurrency-group-standar
title: Standard extract: one run at a time (concurrency group standard-extract), ~3h per shard; a second dispatch sits pending with 0 jobs
kind: gotcha
evidence: DATA-INFERRED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Runs 44890618221 and 44894493070 sat pending with zero jobs for hours behind in_progress run 44890468680 (success, shards 3h01-3h09). Before dispatching pipeline-standard-extract, check gh run list --workflow pipeline-standard-extract.yml for an in_progress run and reuse its artifact. A local single-connection extract via run_extract_sql.py is far slower (face stage statement timeouts and re-splits, 30 min per unit) and adds pooler load next to the cloud shards; do not run both. Resolver .86 (886ccb51) was built from run 44890468680.
