---
id: q4-dps-fy-9m-must-use-one-tag-series-cfg-tags-a-q4-declared-
title: Q4 DPS = FY - 9M must use ONE tag series: CFG tags a Q4 declared DPS on a 12-month context
kind: gotcha
tags: dps, per-share, fsn, q4
paths: pipeline/scripts/slot_records/fsn_company_pershare.py
evidence: DATA-INFERRED
created: 2026-11-01
verified: 2026-11-01
---
CFG FY2017 10-K 0000759944-18-000016 tags CommonStockDividendsPerShareDeclared = 0.18 with qtrs 4 (really the Q4 declared amount) beside CashPaid FY = 0.64. Choosing the tag per key (Declared first, mapper order) and subtracting the CashPaid 9M (0.46) gives -0.28. Derive Q4 only when FY and 9M come from the same tag; hide a negative Q4. The FY cell itself still shows 0.18 under Declared-first: open question to Dhairya (CF-PERSHARE-PORT-2026-11-01.md section 6).
