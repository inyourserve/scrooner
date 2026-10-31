---
id: match-a-cell-date-to-an-fsds-fsn-column-by-its-nearest-month
title: Match a cell date to an FSDS/FSN column by its nearest month end, never a fixed day window
kind: gotcha
tags: fsds, fsn, dates, quick_ratio
paths: pipeline/src/scrooner_pipeline/mapper/quick_ratio_evidence.py
evidence: FILING-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
FSDS/FSN ddate is rounded to the NEAREST month end, which can be 7+ days away for 52/53-week filers. quick_ratio _column used a 6-day window and hid RAVE (0000718332) 2023-12-24 and 2024-03-24 (10-Qs 0001140361-24-005023/-023848) as statement_unavailable although the face shows 2023-12-31/2024-03-31 with no inventory line (Verifier V5). Fix (work/per-share/quick-ratio-v6 945508a): exact match, else the date's nearest month end only.
