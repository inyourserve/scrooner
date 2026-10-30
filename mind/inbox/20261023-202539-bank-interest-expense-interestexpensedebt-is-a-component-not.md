---
id: bank-interest-expense-interestexpensedebt-is-a-component-not
title: Bank interest_expense: InterestExpenseDebt is a component not the face total; banks moved to InterestExpenseOperating from 2021-09
kind: gotcha
tags: bank, interest-expense, tags
paths: data-team/strategy/team/TAG-MAPPER-INTEREST-EXPENSE-AND-BDC-GATE-2026-10-22.md
evidence: FILING-CHECKED
created: 2026-10-23
verified: 2026-10-23
---
Stored values from InterestExpenseDebt are wrong at RBB (4,800K vs 117,297K), NBBK, MYFW, COLB, HWBK. 308 of 326 active banks file InterestExpenseOperating. Non-banks file it with other meanings (MTZ, HTZ net interest), so gate by bank group. bdc_total_investment_income (GrossInvestmentIncomeOperating) is fed by 47 insurers' gross note line, not NetInvestmentIncome.
