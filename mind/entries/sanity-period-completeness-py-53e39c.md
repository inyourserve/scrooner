---
id: sanity-period-completeness-py-53e39c
title: `sanity/period_completeness.py`
kind: gotcha
tags: pipeline
paths: pipeline/CLAUDE.md
evidence: DOC-CITED
source: pipeline/CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
(`analytics.company_data_finding`, `analytics.period_gap`) is the main coverage-gap tracker — every missing (company, concept, period) cell gets one classified cause (`no_mapped_tag`, `q4_not_derived`, `conflict_split`, `not_in_sec_feed`, etc.), each mapped to a `finding_type` (`pipeline_bug`/`filer_error`/`data_limit`/`legitimate_absence`). **`not_in_sec_feed` is not always a genuine SEC-side limit** — the single-tag `companyconcept` probe this check used to rely on can return an empty result for a real company with real data (confirmed on Visa, Abbott, Ford, PayPal, and ~14% of a sampled population); fixed 2026-10-09 to only trust a non-empty probe result. Separately, SEC's own bulk Company Facts product can lag 2+ months behind a real, confirmed-filed 10-Q for large companies' most recent quarter — a genuine data-currency gap, not a classifier bug, that the existing rendered-report-parser pattern could in principle close (not yet built for core balance-sheet/income-statement concepts).
