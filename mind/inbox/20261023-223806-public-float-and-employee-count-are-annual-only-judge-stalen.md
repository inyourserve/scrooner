---
id: public-float-and-employee-count-are-annual-only-judge-stalen
title: Public float and employee count are annual-only: judge staleness on ~650 days, not on the quarterly rule
kind: rule
tags: certification, staleness, public_float, mli
paths: pipeline/src/scrooner_pipeline/certification/currency.py
evidence: FILING-CHECKED
source: MLI 10-K 0000089439-26-000008 R1 (held-out validation 2026-10-22)
created: 2026-10-23
verified: 2026-10-23
---
dei:EntityPublicFloat is measured at the end of the second fiscal quarter and first appears in the NEXT 10-K, so against the latest 10-Q its legitimate age reaches about 20 months (MLI float of 2025-06-27 vs a 10-Q of 2026-09-26 = 456 days). ANNUAL_ONLY_MAX_GAP_DAYS = 650 in certification/thresholds.py; employee_count follows the same rule.
