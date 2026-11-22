---
id: template-out-no-companyfacts-fact-under-the-concept-tag-set-
title: Template-OUT 'no companyfacts fact under the concept tag set' is not absence evidence: narrow tag sets and a successor CIK (XOM 2115436) make printed lines look absent
kind: lesson
tags: template, verifier, coverage, tag-set
evidence: FILING-CHECKED
status: active
source: scratchpad verify-candidates-2026-11-11.md
created: 2026-11-12
verified: 2026-11-12
---
Verifier 2026-11-12, ranks 1-50: 28 of 63 sampled template-OUT rows FAIL. The filing prints the line under a tag outside the concept's set (bank Interest income InterestAndDividendIncomeOperating; OtherNonoperatingIncomeExpense at KO/CAT/TXN/TSLA; InterestExpenseDebt at CVX; IncreaseDecreaseInRetailRelatedInventories at HD). Combined lines were also proposed OUT. XOM is mapped to new holding CIK 0002115436, which has no 10-K, so all of its history (CIK 34088) was invisible. Note-sourced FAILs (14 of 34): segment totals (ORCL GP R81, JNJ OI 0000200406-15-000019 R42), the GE-industrial column (GE GP FY2016 R164), component-as-total (JPM/GS InvestmentIncomeInterest, CSCO PP&E D&A), and values that sit on the face (AMD, SHOP, JPM cash, CAT/PG equity). Rule: OUT needs an R-page face and notes search, not a companyfacts tag-set miss.
