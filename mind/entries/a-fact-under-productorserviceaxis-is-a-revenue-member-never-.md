---
id: a-fact-under-productorserviceaxis-is-a-revenue-member-never-
title: A fact under ProductOrServiceAxis is a revenue member, never non-operating income (DE other_income served Deere's 'Other income' revenue line for 10 years)
kind: rule
tags: other-income, revenue, dimensions, resolver
paths: data-team/strategy/open-shown-fixes/DE-2026-11-21.csv
evidence: FILING-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Deere's income statement has no non-operating section: Net sales and revenues (incl. an 'Other income' member under ProductOrServiceAxis, us-gaap:Revenues; earlier us-gaap:OtherIncome 706.5/745.5M FY2015/16) -> Costs and expenses -> pretax, and the identity ties every year. The resolver served that revenue member as other_income_expense_net FY2015-FY2025 (e.g. 1,295/1,003/1,198/1,019M FY2022-25). Dhairya ruling 2026-11-21: a fact dimensioned by ProductOrServiceAxis is a revenue component and can never serve a non-operating data point; other_income for such a company is HIDE structural_not_presented with the revenue-to-pretax identity as evidence.
