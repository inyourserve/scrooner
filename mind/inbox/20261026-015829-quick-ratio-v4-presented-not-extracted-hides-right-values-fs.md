---
id: quick-ratio-v4-presented-not-extracted-hides-right-values-fs
title: quick_ratio V4: presented_not_extracted hides right values; FSDS statement_dates span all statements
kind: lesson
tags: quick_ratio, inventory, FSDS
paths: data-team/strategy/team/VERIFY-QUICK-RATIO-4-2026-10-26.md
evidence: FILING-CHECKED
source: STE 0001757898-19-000005; TXN 0001564590-19-003839; 0001907982-24-000040
created: 2026-10-26
verified: 2026-10-26
---
18/18 sampled presented_not_extracted cells store exactly (CA - face inventory)/CL; the hide keys on a missing canonical inventory fact, not on the stored value. FSDS statement_dates include dates from equity/other statements, so 0001907982 FY2020 is treated as shown though the BS has only 2022/2021. FDX spare parts/supplies and ConEd fuel/materials lines stay unhidden. Corrects my V3 claim that the STE hide was right.
