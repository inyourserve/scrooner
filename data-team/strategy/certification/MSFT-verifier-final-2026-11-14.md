# MSFT certification: final Verifier sample 2026-11-14 (independent seed)

- **Population:** data-team/strategy/certification/MSFT-coverage-2026-11-14.csv at 4211cb1b: 552 FY template cells FY2015-FY2026, 516 PROVEN and 36 REASON (proof v12, main 56e76dc6).
- **Draw:** 32 cells from PROVEN + REASON, ordered by md5('verifier-MSFT-final-20261114|data_point|fiscal_year'). This seed is independent of the other Verifier's seeds 20261113 and 20261114. Result: 30 PROVEN and 2 REASON. Separately, every total_debt year was checked (12 cells, FY2015-FY2026), as Dhairya asked.
- **Check:** each served cell's own 10-K (the cell's accession) was opened on sec.gov. The line carrying the served tag was read at the period's column: 12 months, or the instant at the fiscal year end. Printed value x page scale was compared with the served value, and the sign compared. total_debt sums each component: balance-sheet debt lines plus the lease note's 'Total finance lease liabilities' (FY2017 onward), following founder item 5. For each REASON cell, the face and the 'Components of Other Income (Expense), Net' note were read.

## Result
| set | checked | wrong | one-sided 95% Clopper-Pearson upper bound |
|---|---|---|---|
| random sample (PROVEN + REASON) | 32 | 0 | 8.94% |
| total_debt, every year | 12 | 0 | 22.09% |
| all checked cells | 44 | 0 | 6.58% |

- total_debt FY2017-FY2026 equals the printed debt lines plus the finance lease liabilities from the lease note (R103/R101/R95/R93/R94/R100/R90/R92). FY2015-FY2016 are debt lines only; no finance lease is presented.
- cash_paid_for_income_taxes FY2018 was read by hand: R88 prints 5,500 in the 12-month column ending Jun. 30, 2018.
- Six cells match the printed value with the opposite sign: cf_ar_change FY2017 and FY2023, cf_inventory_change FY2017, dividends_paid FY2017 and FY2022, interest_expense FY2018 (other-income note). The served value is the XBRL fact; the page prints the cash-flow or other-income presentation. They are counted right under the XBRL sign convention, which is still awaiting a ruling.
- REASON (2): interest_income FY2016 and FY2020. The note prints interest only together with dividends ('Dividends and interest income' 903; 'Interest and dividends income' 2,680), and the face only 'Other income (expense), net'. Combined is confirmed.
