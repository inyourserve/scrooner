---
id: sanity-newest-null-counts-are-history-rows-most-are-delibera
title: Sanity 'newest NULL' counts are history rows; most are deliberate metric guards, not coverage loss
kind: gotcha
tags: sanity, missing_ours, coverage, triage
paths: pipeline/src/scrooner_pipeline/sanity/report.py
evidence: DATA-INFERRED
status: active
source: scrooner-bc triage 2026-11-01
created: 2026-10-31
verified: 2026-10-31
---
A count of data_sanity_check rows whose newest metric_value (TTM first, then latest period_end) is NULL multiplies by up to 17 daily runs: 5,288 rows population-wide became 775 cohort company-metrics. Every one carries metric_value.is_null_reason. A 10-example draw found 9 guard/rule blanks (JCI/BALL no operating income since 2016/2024, INTC/LSCC D&A withdrawn after 2019, ORCL/NAVN debt guard, AJG/TMO no gross-profit line, ATI no dividends) and 1 ingestion gap: Visa 10-Q 0001403161-26-000104 has 0 core.fact rows (B9). Deduplicate and group by is_null_reason before calling it coverage loss.
