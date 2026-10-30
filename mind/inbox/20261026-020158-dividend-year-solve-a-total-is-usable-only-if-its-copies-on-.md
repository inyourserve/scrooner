---
id: dividend-year-solve-a-total-is-usable-only-if-its-copies-on-
title: Dividend year solve: a total is usable only if its copies on one tag agree; year-solved quarters skip the mixed-tag hide
kind: gotcha
tags: dividends, dps, share_basis, COP, CommonStockDividendsPerShareDeclared
paths: pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py
evidence: DATA-INFERRED
source: work/period-engineer/split-rebase run 6; Verifier run 4
created: 2026-10-26
verified: 2026-10-26
---
COP files Declared 9M 2021 as both 0.46 (2021-11-04 10-Q) and 1.75 (2022-11-03 10-Q, FY figure on a 9M context), and Declared Q3 2021 as 0.46 and 0.89. Using the latest Declared 9M as a constraint made the solver pick Q3 0.89 (wrong; 0.43). Fix: _dps_year_solve.total() returns a span total only from the first tag whose copies all agree (else falls to CashPaid 1.29); quarter candidates include the other dividend tag's filed copies; a quarter fixed by the year's filed totals (note YEAR_SOLVE_NOTE) is exempt from _one_dividend_basis's mixed-tag hide. Test: test_year_solve_uses_the_nine_month_total_without_a_filed_q4 (3 targeted mutants killed).
