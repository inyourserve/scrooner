---
id: bs-totals-detect-equity-block-guard-demotes-long-term-debt-a
title: bs_totals_detect equity-block guard demotes long-term debt at capitalization-format utilities (NI, AWK, FE)
kind: gotcha
tags: balance-sheet, bs_totals, utilities, total-liabilities
paths: pipeline/scripts/slot_records/bs_totals_detect.py
evidence: CODE-CHECKED
status: active
created: 2026-11-01
verified: 2026-11-09
---
The UPS guard (liab line after equity starts -> equity_component) resets only at Total capitalization; utilities print equity, then LTD, then Total capitalization, so LongTermDebtAndCapitalLeaseObligations / LongTermDebtNoncurrent leave the total-liabilities members (70 of 338 v3 records differ). Face-sum + identity tie -> withheld, not wrong. Unfixed; needs a Verifier draw. BS-PORT-2026-11-01.md 5.2.

[2026-11-09] Curator 2026-11-09: guard confirmed in bs_totals_detect.py (EQUITY-BLOCK position guard, ~line 191); 'unfixed' status not re-checked beyond that; cited BS-PORT doc not re-read.
