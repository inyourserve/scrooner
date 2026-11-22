---
id: every-new-display-hide-class-needs-a-filing-checked-sample-b
title: Every new display-hide class needs a filing-checked sample before it goes live
kind: rule
evidence: FILING-CHECKED
status: active
created: 2026-11-16
verified: 2026-11-16
---
Display hides (HIDDEN_ROW/HIDDEN_YEAR) must never hide a number the filing prints. The resolver's tag-list lookup misses printed content: custom tags (QCOM interest paid, CRM amortization), quarterly-only DPS (C, SYK), face lines under a wrong standard tag (T Inventories tagged PrepaidExpenseCurrent), composition notes (NFLX trade receivables), MD&A-only figures (PH interest income). Two 20-cell verifier samples on 2026-11-16 found 6/20 and 8/20 wrong hides. So absent_in_own_filing is an ALLOWLIST (operating_income, shares_outstanding, share_buybacks: 0 wrong); a data point or hide class joins only after a >=20-cell filing check with 0 wrong (Dhairya, 2026-11-16).
