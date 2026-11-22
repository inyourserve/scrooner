---
id: core-period-holds-several-fy-labelled-periods-per-fiscal-yea
title: core.period holds several FY-labelled periods per fiscal year; anchor to the annual filing and the company's year length, never the latest end
kind: lesson
tags: period, fiscal-year, 52-53-week, top100
paths: pipeline/src/scrooner_pipeline/mapper/top100_coverage.py
evidence: DATA-INFERRED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Found 2026-11-21 (fix 174cbcd1). Stray FY-labelled rows: PG FY2024 2023-10-01..2024-09-30 beside the real 06-30 year; MU FY2023 calendar 2023; MU FY2026 instant 2026-09-12 beside 09-03; DE 365/366-day duplicates beside its real 364-day years. The latest-end rule keyed 111 open rows wrong. The filing period (fsn.filing.period and core.filing.period_of_report for older years) is MONTH-END ROUNDED for 52/53-week filers (Deere's 10-Ks say 10-31 for FY2015, which ended 11-01, and FY2016, which ended 10-30), so distance to the filing period alone picks the wrong duplicate. What works: candidate must fsn_end_matches an annual filing period, then prefer the company's year length (364/371 days if a 52/53-week filer, voted over single-candidate years; else 365/366), then the closest end. A blanket whole-week preference breaks calendar filers (BLK, BAC, KLAC carry stray 364-day duplicates).
