---
id: company-history-source-windows-must-use-fsn-month-end-period
title: company_history_source windows must use FSN month-end periods, and a predecessor needs the later 10-K to reprint its exact numbers
kind: gotcha
tags: company_history_source, predecessor, exclude, 0121
paths: pipeline/db/migrations/0121_company_history_source.sql
evidence: FILING-CHECKED
status: active
source: verifier 2026-11-10; fsn.filing 0001613103-15-000008 period 2015-01-31 for a 2015-01-23 balance date
created: 2026-11-10
verified: 2026-11-10
---
fsn.filing.period is month-end normalized (Medtronic plc 10-Q dated 2015-01-23 is stored as 2015-01-31), so a window ending on the exact fiscal date (2015-01-23, 2015-12-26) can drop the last predecessor filing; use the month end. A parent-of-subsidiary filer is not automatically the predecessor: Lantheus Holdings' 2015 10-K reprints FY2014 net loss (3,561)K vs Lantheus Medical Imaging's own (1,169)K (0001193125-16-490104 R4 vs 0001193125-15-076795 R4); Vistra reprints TCEH 2015 net loss (4,677)M vs EFCH (4,603)M (0001692819-18-000018 R2 vs 0001445049-16-000016 R2). Common-control mergers (IBRX/NantKwest) are retrospectively combined: own-CIK pre-merger filings are wrong-entity (NantKwest 2020 NL 92.4M vs IBRX-reported 224.2M).
