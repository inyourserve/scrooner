---
id: expanded-metrics-wrote-one-ttm-row-per-compute-date-a-hide-l
title: expanded_metrics wrote one TTM row per compute date: a hide leaves older valued rows behind
kind: gotcha
tags: ttm, expanded_metrics, guards
paths: pipeline/src/scrooner_pipeline/mapper/expanded_metrics.py
evidence: DATA-INFERRED
created: 2026-10-23
verified: 2026-10-23
---
784,191 TTM rows for 15 owned metrics, 705,336 (90%) superseded, across 30 period_end dates. A guard hides by writing a newer null row but the older valued rows stay; certification/loader.py (~L406) reads the latest NON-null TTM row, so certify judged values users no longer see; has_value_any_period would count hidden cells as valued. Fix on branch lane2-ttm-row-cleanup (delete prior rows per company in one transaction under an advisory lock; archive migration 0107, not applied).
