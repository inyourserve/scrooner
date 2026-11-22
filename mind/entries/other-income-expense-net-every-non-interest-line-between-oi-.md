---
id: other-income-expense-net-every-non-interest-line-between-oi-
title: other_income_expense_net = every non-interest line between OI and pretax (incl equity-method income, gains)
kind: decision
tags: other_income, income_statement
evidence: DOC-CITED
status: active
created: 2026-11-14
verified: 2026-11-22
---
Dhairya 2026-11-14: other_income_expense_net = pretax - OI - separately printed interest expense/income, i.e. sum of every non-interest line in the OI->pretax band, including equity-method income and gains. A single nonoperating total that includes interest (GOOG NonoperatingIncomeExpense, ISRG/BKNG/GEV 'interest and other') is combined. Other income printed inside operating costs with no after-OI band is not_presented (BMY, CVX, WELL, MDT). Served narrow 'Other'-line values move (resolver-is 5373c297).

[2026-11-22] The 'inside operating costs -> not_presented' clause is superseded by supersedes-other-income-printed-inside-total-expenses-is-ser (served with flag presented_within_expenses).
