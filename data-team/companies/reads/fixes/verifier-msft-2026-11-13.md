# MSFT certification: independent Verifier sample 2026-11-13 (final)

- **Frame:** MSFT FY template cells in data-team/strategy/top100-coverage.csv @ 6e9a31be. The snapshot has 552 cells: 510 PROVEN, 36 REASON, 4 UNCHECKED, 2 DISAGREE. Dhairya quotes 516/36 on main 6e9a31be; the committed snapshot predates the 6-cell fix (457ae03a), so it still shows them as non-proven. The draw is from the 546 PROVEN + REASON rows.
- **Draw:** 32 cells, ordered by md5('verifier-msft-indep-20261113|dp|fy'). This seed is independent of Ritwik's and of my first run (msft-cert32-20261113, kept as -run1). Result: 29 PROVEN, 3 REASON.
- **Check:** each served cell's own 10-K was opened on sec.gov (FilingSummary, then the R pages carrying the served tag). The printed line was read at the fiscal-year column (12-month duration, or instant at the fiscal year end). Printed value x page scale was compared with the served value, and the sign compared. For each REASON cell, the face statement and the note were read to confirm the stated reason.

## Result
**0 wrong of 32. One-sided 95% Clopper-Pearson upper bound 8.94%.**

- PROVEN 29/29 right: value, period and R page match. 6 of them (cf_ar_change FY2021, cf_inventory_change FY2017, capex FY2023, share_buybacks FY2018 and FY2021, dividends_paid FY2015) match with the opposite sign: the served value is the XBRL fact; the page prints the cash-flow presentation (capex, buybacks, dividends, AR and inventory changes). They count as right under the XBRL sign convention; the convention ruling is still open.
- REASON 3/3 confirmed: interest_income FY2015 and FY2026 are printed only as 'Dividends and interest income' (combined). other_income_expense_net FY2021: the face 'Other income, net' includes interest; the note 'Other, net' 98 is a residual component (component_in_note would be more precise; no value is wrong).

Correction to run 1: run 1 said the 12 other_income_expense_net REASON cells 'look wrong'. On reading the notes (FY2015 R58, FY2021 R49, FY2026 R48), 'Other, net' is a residual after gains, derivatives and FX, not the data point. The combined reason stands.
