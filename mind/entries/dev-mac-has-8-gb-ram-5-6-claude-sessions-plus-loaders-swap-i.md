---
id: dev-mac-has-8-gb-ram-5-6-claude-sessions-plus-loaders-swap-i
title: Dev Mac has 8 GB RAM: 5-6 Claude sessions plus loaders swap it to a hang; run heavy loads in Actions
kind: gotcha
tags: mac, memory, swap, sessions, hang, actions
paths: pipeline
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
Measured 2026-11-01 (hw.memsize, vm_stat, vm.swapusage): 8 GB RAM, 17.6 of 21.5 GB swap used, ~27 GB in the memory compressor, ~64 MB free while 5-6 Claude sessions, VS Code, Chrome and Python loaders ran. The result was system hangs, stale DB connections and dead sessions mid-load (two load runs lost). Keep at most ~3 local sessions; run long loads, sharding and plans in GitHub Actions or cloud sessions, not on the Mac. Related: dev-mac-sleep-kills-long-db-jobs-silently-run-them-under-caf.
