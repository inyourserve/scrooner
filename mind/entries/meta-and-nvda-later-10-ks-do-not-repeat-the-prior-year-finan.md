---
id: meta-and-nvda-later-10-ks-do-not-repeat-the-prior-year-finan
title: META and NVDA later 10-Ks do not repeat the prior-year finance lease: take it from the prior 10-K when face debt lines are equal
kind: gotcha
tags: debt, finance-lease, META, NVDA, vintage
paths: pipeline/scripts/slot_records/replay_debt_fsn.py, data-team/strategy/team/VERIFY-DEBT-PORT-2026-11-01.md
evidence: FILING-CHECKED
status: active
created: 2026-11-03
verified: 2026-11-03
---
META 10-K 0001326801-24-000012 tags FinanceLeaseLiability (+Current/Noncurrent) only at the current-year instant (context c-5 = 2023-12-31, R64); the 2022 column is blank. The 2022-12-31 lease is 687 (129+558) in 0001326801-23-000013 R65, so META 2022-12-31 total debt = 9,923 + 687 = 10,610 (an earlier answer key said 10,613 by reading the 2023 column). NVDA FY2019 10-K 0001045810-19-000023 folds prior-year CapitalLeaseObligationsCurrent (5) into Other accrued liabilities (R57); take it from 0001045810-18-000010 R49. META FY2019 10-K 0001326801-20-000013 R47 mis-tags the noncurrent 418 to FI2018Q4 (2018-12-31 debt = 0; 2019 = 473). Rule applied (approver ruling 2026-11-02): use the earlier 10-K's lease only when the latest copy's printed debt lines equal it. Verifier 2026-11-03, 42 SEC requests.
