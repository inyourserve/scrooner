---
id: bs-totals-detect-equity-block-guard-demotes-long-term-debt-a
title: bs_totals_detect equity-block guard demotes long-term debt at capitalization-format utilities (NI, AWK, FE)
kind: gotcha
tags: balance-sheet, bs_totals, utilities, total-liabilities
paths: pipeline/scripts/slot_records/bs_totals_detect.py
evidence: CODE-CHECKED
created: 2026-11-01
verified: 2026-11-01
---
The UPS guard (liab line after equity starts -> equity_component) resets only at Total capitalization; utilities print equity, then LTD, then Total capitalization, so LongTermDebtAndCapitalLeaseObligations / LongTermDebtNoncurrent leave the total-liabilities members (70 of 338 v3 records differ). Face-sum + identity tie -> withheld, not wrong. Unfixed; needs a Verifier draw. BS-PORT-2026-11-01.md 5.2.
