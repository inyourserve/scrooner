# MSFT final draw (Ritwik cloud, 2026-11-14): FAIL, 1 error

Coverage: `data-team/strategy/certification/MSFT-coverage-2026-11-14.csv` at 847725da. Values, classes and accessions are identical to 4211cb1b. 552 cells: 516 PROVEN, 36 REASON. Seed: `msft-final-2026-11-14`.

| Check | Result |
|---|---|
| 32 PROVEN cells (random, excluding total_debt) | 32/32 match the filing's own R page (28 by script, 4 by hand: DPS FY2026 and FY2019 on the equity statement R7, revenue FY2017 R2, basic EPS FY2017 R2 of the FY2019 10-K) |
| 5 REASON cells | 5/5: each cites its own FY 10-K, and the page prints the combined line (OI&E R2 'Other income, net'; D&A 'Depreciation, amortization, and other') |
| All 36 REASON cells cite their own period's filing | 35 cite their own FY 10-K; D&A FY2025 cites the FY2026 10-K, which presents the FY2025 column (allowed) |
| Locators | 0 cells missing an accession or R page; all 36 sum cells have per-part locators |
| total_debt, all 12 FY, full perimeter | **11/12. FY2016 FAILS** |

**The error: total_debt FY2016.** Served 53,461 = short-term debt 12,904 + current LTD 0 + LTD 40,557 (FY2017 10-K 0001564590-17-014900 R5). That filing's commitments note (R24 text, R102 detail) states that at June 30, 2016 capital lease obligations of $25M sat in other current liabilities and $761M in other long-term liabilities. These are pre-842 capital leases, which are inside the founder's 2026-11-04 debt perimeter (Engineering's R07 includes them). Correct value: **54,247**. My own earlier check value of 53,461 had the same omission.

FY2015: neither the FY2015 nor the FY2016 10-K discloses capital lease obligations at June 30, 2015, so 35,292 stands.

FY2017-26 match face debt plus 'Total finance lease liabilities' from each filing's own lease note: R103 for FY2017-18, R101, R95, R93, R94, R100, R100, R90, R92.

MSFT is not certified. To certify: fix FY2016 total_debt, make the R07 perimeter scan capital leases disclosed only in note text or detail (other current and long-term liabilities), and re-run the total_debt sweep. The 32-cell PROVEN sample stands.
