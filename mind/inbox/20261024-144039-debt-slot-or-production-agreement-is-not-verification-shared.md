---
id: debt-slot-or-production-agreement-is-not-verification-shared
title: Debt slot or production agreement is not verification: shared vocabulary misses whole face lines (KO NotesAndLoansPayable, ORCL LongTermNotesAndLoans, AMD LinesOfCreditCurrent)
kind: lesson
tags: total_debt, slot_records, verifier, face_coverage
paths: data-team/strategy/team/VERIFY-SLOT-RECORDS-30SET-2026-10-24.md
evidence: FILING-CHECKED
source: Verifier 30-set slot records 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
12 of 126 'agree exactly' debt cells (KO 4, ORCL 8) are wrong in both slot and production: both miss a face debt line whose tag escapes the regex/vocabulary (KO 0000021344-18-000042 R4 12,973M; ORCL 0001193125-16-797253 R2 50,489M). Require a face coverage check per era record. Also: non-auth fallback took a GE 8-K recast copy (2021-12-31); CVX total debt = face ST + face LT line (ShortTermDebtRefinancedAmount reclass), never LongTermDebt or pre-reclass DebtCurrent.
