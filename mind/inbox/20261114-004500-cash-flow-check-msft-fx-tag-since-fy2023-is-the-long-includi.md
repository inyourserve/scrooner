---
id: cash-flow-check-msft-fx-tag-since-fy2023-is-the-long-includi
title: Cash-flow check: MSFT FX tag since FY2023 is the long IncludingDisposalGroupAndDiscontinuedOperations variant
kind: gotcha
evidence: FILING-CHECKED
created: 2026-11-14
verified: 2026-11-14
---
2026-11-13 (Tag Expert, main 65278cc9): MSFT tags FX as EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations from FY2023; it was missing from CF_FX so cf_parts_eq_change failed (FY2024 diff -210M = FX). Fix: use the filer's calc tree under the change-in-cash line; no-arc fallback CFO+CFI+CFF (+discontinued) + any FX-family element vs the cash+restricted total. Top-110 failures 918 -> 38 (MSFT 57 -> 0, GE 78 -> 2). Remaining: filer rounding (MCD +/-1M x19) and linkbase weight defects (UNH, ISRG weight CFO -1).
