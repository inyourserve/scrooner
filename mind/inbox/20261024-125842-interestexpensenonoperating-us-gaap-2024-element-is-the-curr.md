---
id: interestexpensenonoperating-us-gaap-2024-element-is-the-curr
title: InterestExpenseNonoperating (us-gaap 2024+ element) is the current non-bank 'Interest expense' line and interest_expense does not map it
kind: gotcha
tags: interest_expense, taxonomy, era, InterestExpenseNonoperating
paths: data-team/tags/cards/interest.md, data-team/22-FILING-LESSONS-LEDGER.md
evidence: FILING-CHECKED
source: CL 0000021665-25-000053 R2; AVY 0000008818-25-000049 R4; FASB elts us-gaap-2023.xsd vs 2024.xsd
created: 2026-10-24
verified: 2026-10-24
---
InterestExpenseNonoperating and InterestExpenseOperating first appear in the us-gaap 2024 schema (absent 2015/2019/2022/2023). Earlier period ends in sec_tag_library (2020-12, 2021-09) are re-tagged comparatives. CL and AVY print 'Interest expense' on IEN; our interest_expense (InterestExpense p1, InterestExpenseDebt p2) stops at FY2023/Q1 2024. 1,542 companies have recent IEN and no recent mapped interest tag (company_sec_tag, DATA-INFERRED). Key era rules to the filing taxonomy version, not period dates; ~11% of IEN face labels say ', net'.
