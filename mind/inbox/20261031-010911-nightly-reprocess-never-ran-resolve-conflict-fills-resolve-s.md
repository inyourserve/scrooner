---
id: nightly-reprocess-never-ran-resolve-conflict-fills-resolve-s
title: Nightly reprocess never ran resolve-conflict-fills/resolve-statement-fallbacks; now per-company via --ciks
kind: lesson
tags: nightly, conflict-fills, resolved-concepts, reprocess
paths: pipeline/scripts/reprocess_recent_filers.sh, pipeline/src/scrooner_pipeline/mapper/conflict_resolution.py, pipeline/src/scrooner_pipeline/jobs/map.py
evidence: DATA-INFERRED
created: 2026-10-31
verified: 2026-10-31
---
resolve-conflict-fills is the SOLE writer of net_income_resolved and 18 other *_resolved concepts (its baseline pass-through), yet reprocess_recent_filers.sh ran only resolve-facts + resolve-concept-fallbacks, so every *_resolved concept froze at the last manual population recompute (2026-10-21): 17 top-1000 companies had a Sep-2026 net_income fact and no net_income_resolved row on 2026-10-31. Fix on branch work/engineering/nightly-resolve-stages (d2f6c1a): both stages take --ciks (reads and writes scoped, incl. capex-software, D&A-max and stock-split helpers), --dry-run (one rolled-back transaction: conn.commit is neutralised, then rollback) and --statement-timeout (default 10min). Known one-pass lag, pre-existing: gross_profit/opex arithmetic fallbacks run BEFORE conflict-fills in the same run, so they read the previous run's cost_of_revenue conflict fill; 2 of 78,488 rows differed between pass 1 and pass 2 for the 17 companies, converging on the next run. Dry-run on 17 companies: ~2.5 min single process.
