# TXN certification: final Verifier sample 2026-11-14 (independent seed)

- **Population:** data-team/strategy/certification/TXN-coverage-2026-11-14.csv at e14e25e4: 506 FY template cells FY2015-FY2025, 474 PROVEN and 32 REASON.
- **Draw:** 32 cells from PROVEN + REASON, ordered by md5('verifier-TXN-final-20261114|data_point|fiscal_year'). Result: 31 PROVEN (including total_debt FY2025) and 1 REASON. Every other total_debt year was also checked: 11 total_debt cells, FY2015-FY2025. That makes 42 distinct cells.
- **Check:** each served cell's own 10-K was opened on sec.gov. The line carrying the served tag was read at the period's column (12 months, or the instant at the fiscal year end). Value x page scale was compared with the served value, and the sign compared. The REASON cell was checked against the balance-sheet parenthetical.

## Result
| set | checked | wrong | one-sided 95% Clopper-Pearson upper bound |
|---|---|---|---|
| random sample (PROVEN + REASON) | 32 | 0 | 8.94% |
| total_debt, every year | 11 | 0 | 23.84% |
| all distinct cells | 42 | 0 | 6.88% |

- total_debt = printed 'Current portion of long-term debt' + 'Long-term debt' every year. No finance-lease liability tag exists in the FY2021 or FY2025 10-K (MetaLinks), so founder item 5 adds nothing.
- cash_paid_for_interest FY2022 and FY2024 were read by hand: debt note R69 / R73 print 'Interest paid' 198,000,000 / 473,000,000 in the 12-month column.
- REASON shares_outstanding FY2024 is confirmed: the balance-sheet parenthetical prints only shares authorized, issued and treasury, with no outstanding count.
- Seven cells match the printed value with the opposite sign (XBRL fact vs cash-flow presentation): cf_inventory_change FY2017 and FY2020, cf_ar_change FY2023, capex FY2018, share_buybacks FY2021, FY2022 and FY2025. They are counted right under the XBRL sign convention, which still awaits a ruling.
