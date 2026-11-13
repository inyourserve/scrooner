# MSFT certification sample 2026-11-13 (Verifier)

- **Population:** 546 FY template cells, FY2015 to FY2026: 510 PROVEN and 36 REASON. It was rebuilt live from analytics.cell_proof (detector cell_proof_v2_2026-11-13, basis latest) and analytics.cell_blank_reason with the rules of pipeline/src/scrooner_pipeline/mapper/top100_coverage.py, and matches Dhairya's 510/36.
- **Draw:** 32 cells, seeded by md5('msft-cert32-20261113|dp|fy'). All 32 were PROVEN; no REASON cell was drawn.
- **Check:** each cell's own filing (accession of the served copy) was opened on sec.gov. The line carrying the served tag was located on the R page, and the 12-month column (or instant at fiscal year end) was read. Printed value x page scale was compared with the served value; the sign was compared too.

## Result
0 wrong of 32. One-sided 95% Clopper-Pearson upper bound 8.94%.

Six cells match the printed value with the opposite sign. The served value follows the XBRL fact sign, and the page prints the cash-flow or other-income presentation: cf_ar_change FY2016, cf_inventory_change FY2019, capex FY2024 and FY2026, dividends_paid FY2015, interest_expense FY2025 (note R48 prints it as (2,385)). They are counted right under the XBRL sign convention. If served values must carry the printed sign, these 6 are sign errors. That ruling is still open; see the earlier question to Dhairya.

## REASON cells (none drawn; checked on the FY2026 10-K 0001193125-26-323660)
The 36 REASON cells are depreciation_and_amortization, interest_income and other_income_expense_net, 12 years each, all 'combined'.
- depreciation_and_amortization: confirmed. R6.htm prints only 'Depreciation, amortization, and other' 38,534 (msft:DepreciationAmortizationAndOther), a combined line.
- interest_income: confirmed as combined. The face prints only 'Other income (expense), net'. The note R48.htm prints 'Interest and dividends income' 3,301 (us-gaap:InvestmentIncomeNet), which is interest plus dividends, so it is combined. The stored reason text cites the face line, not the note; the class is right.
- other_income_expense_net: **probably wrong reason.** The note R48.htm 'Components of Other Income (Expense), Net' prints 'Other, net' 4,722 on us-gaap:OtherNonoperatingIncomeExpense. By the whole-filing ruling, a data point found only in a note is mapped (stmt NOTE, R page), not combined. The same note already serves MSFT interest_expense (PROVEN from R48). Engineering and the Tag Expert: map other_income_expense_net to R48 'Other, net' for each year the note prints it. This affects 12 REASON cells outside this sample.
