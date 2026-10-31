---
id: nightly-reprocess-never-refreshes-conflict-fill-or-statement
title: Nightly reprocess never refreshes conflict-fill or statement-fallback *_resolved concepts (net_income_resolved lags a quarter)
kind: gotcha
tags: resolve-lag, nightly, stage-order
paths: pipeline/scripts/reprocess_recent_filers.sh, pipeline/src/scrooner_pipeline/mapper/conflict_resolution.py, pipeline/src/scrooner_pipeline/mapper/concept_fallback.py
evidence: DATA-INFERRED
source: scrooner-bc data session 2026-10-31
created: 2026-10-31
verified: 2026-10-31
---
Live 2026-10-31 at 17 cohort companies (OMC HAL TXN WDC JBHT JBL KMI DGX STLD ALV TDY AYI CME LVS RNG PM BAH): base net_income has the Sep-2026 quarter (rewritten 2026-10-27); net_income_resolved has it at none; gross_profit_resolved at 8. Newest *_resolved write is 2026-10-24; last pipeline-recompute success is 2026-10-21. net_income_resolved is written only by resolve-conflict-fills (conflict_resolution.py:90); gross_profit_resolved by resolve-statement-fallbacks (concept_fallback.py:146) plus conflict-fills. reprocess_recent_filers.sh runs only resolve-facts and resolve-concept-fallbacks, so both stages are manual-recompute-only. This is NOT a coverage-before-resolve ordering bug: coverage runs after reprocess in the refresh. Fix: per-company --ciks mode for both stages in the nightly, or a scheduled recompute after the refresh.
