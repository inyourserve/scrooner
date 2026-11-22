---
id: run-scrooner-cells-loads-in-actions-pipeline-cells-load-yml-
title: Run scrooner-cells loads in Actions: pipeline-cells-load.yml (plan then apply, 20 shards, --skip-loaded resume)
kind: howto
tags: cells, loader, actions
paths: .github/workflows/pipeline-cells-load.yml
evidence: CODE-CHECKED
status: active
created: 2026-11-01
verified: 2026-11-01
---
gh workflow run pipeline-cells-load.yml --ref main -f family=<f> -f file=fsn-notes/cells/<f>/<date>/cells.jsonl.gz [-f then_family=.. -f then_file=..] -f shards=20 -f apply=true. Every shard plans before any applies; a rerun resumes past companies already loaded from the same file sha. Pooler (session mode, 5432) took 30 concurrent connections fine 2026-11-01. capex_da_cash_debt: 20 shards plan+apply in ~17 min (run 41297432544). Apply only on the founder's typed words.
