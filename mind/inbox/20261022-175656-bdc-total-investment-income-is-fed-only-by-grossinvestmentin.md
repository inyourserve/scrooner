---
id: bdc-total-investment-income-is-fed-only-by-grossinvestmentin
title: bdc_total_investment_income is fed only by GrossInvestmentIncomeOperating; 47 of its 118 filers are insurers (gross note line), so insurers sit in the BDC concept and the bdc_company population
kind: lesson
tags: GrossInvestmentIncomeOperating, NetInvestmentIncome, bdc_total_investment_income, insurer, BDC, coverage_matrix
paths: data-team/tags/cards/investment-income-and-funds.md, pipeline/src/scrooner_pipeline/mapper/coverage_matrix.py
evidence: FILING-CHECKED
source: CINF 0000020286-26-000008; ARCC 0001287750-26-000006; concept_mapping read 2026-10-22
created: 2026-10-22
verified: 2026-10-22
---
Hypothesis that NetInvestmentIncome feeds it is refuted (unmapped). Insurer meaning: gross investment income before investment expenses (CINF 1,182 - 17 = NII 1,165). BDC NetInvestmentIncome is PRE-tax (ARCC 1,458 vs after-tax 1,415 on InvestmentIncomeOperatingAfterExpenseAndTax). Also: banks moved total interest expense to InterestExpenseOperating from 2021-09 and interest_expense maps only InterestExpense (EFSC FY2025 blank); SEC Frames entity counts are lower bounds.
