# MSFT certification sample, Verifier, 2026-11-13

Company: MSFT (company_id 4, CIK 0000789019). Population: 552 FY template cells FY2015-FY2026 (516 PROVEN, 36 REASON) from the coverage file `shard_msft4/coverage/top100-coverage.csv` (same content as `MSFT-coverage-2026-11-13.csv`, commit 871efe42). Per-cell results: `MSFT-verifier-sample-2026-11-13.csv`.

## Sampling (seed 20261113)

Code: `MSFT-verifier-sample-2026-11-13-sampler.py` (run as `python3 sampler.py top100-coverage.csv`). Rows sorted by (class, statement, data_point, fiscal_year), then shuffled with `random.Random(20261113)`, PROVEN first and REASON second on the same generator. PROVEN: greedy take of 8 IS, 8 BS and 8 CF cells, at most 2 per fiscal year, at most 1 per data point (24 cells, all 12 years). REASON: 2 per reason data point (D&A, interest_income, other_income_expense_net), distinct years (6 cells). Statement buckets: BS = balance-sheet items plus shares_outstanding; CF = cash-flow items; IS = everything else, including EPS, DPS and weighted shares.

## Method

For each cell, the served value is read from `analytics.canonical_fact` (fiscal_period FY, concept name with `_resolved` / `revenue_sanity_resolved`). All 24 PROVEN values equal the coverage file and the `cell_proof` v3 row. Then I opened the original sec.gov R pages for the cited 10-K and for every later 10-K that prints the same column, up to the latest one (BS +1 year, IS/CF +2 years). For working-capital signs I also read the XBRL instance (`msft-20240630_htm.xml`, `msft-20260630_htm.xml`). 12 10-Ks in all; SEC requests were spaced 0.3 s apart (under 4/s), with the declared User-Agent.

## Result

| | Sampled | Wrong | Clopper-Pearson 95% upper bound (two-sided / one-sided) |
|---|---|---|---|
| All | 30 | 1 | 17.2% / 14.9% |
| PROVEN (served values) | 24 | 0 | 14.3% / 11.7% |
| REASON | 6 | 1 | 64.1% / 58.2% |

Each of the 24 served values matches the latest eligible filing, with the right sign and scale. That includes one restated column: AR FY2017 is served as 22,431, the ASC 606 figure printed in the FY2018 10-K. The FY2017 10-K originally printed 19,792.

The one error is #25, depreciation_and_amortization FY2022. The blank is right, but the reason shown ("the line is not mapped for this era") states a pipeline gap, not a filing fact. The filing prints D&A only inside the combined line "Depreciation, amortization, and other" (14,460), so the reason should read combined. The coverage file gives the same era_unmapped reason for FY2015-FY2024, 10 cells in all (DATA-INFERRED).

A clean PROVEN draw means no errors were found in these 24 cells. It is not a guarantee for the other 492.

## Defects that are not value errors (route to the owner of the coverage/evidence export)

1. **Wrong R-page locators (7 of 30 sampled cells).** The value is right in each case, but the cited page is a different report:
   - #1 goodwill: cites R4, the CI parenthetical (BS is R5).
   - #4 AP FY2017: cites R4 in the FY2017 10-K (BS is R5).
   - #11: cites R82 (correct page R83).
   - #15: cites R75 (correct page R74).
   - #17 DPS: cites R7, the cash flow statement (DPS is on R2).
   - #27 and #28: cite R48 (correct pages R57, R52 and R49).

   In the FY2015-FY2017 10-Ks, R4 is the CI parenthetical, R5 the BS, R6 the BS parenthetical and R7 the CF. The export cites R4 for BS and R6 for CF there, which suggests it uses the FY2018+ layout. That pattern covers about 84 PROVEN rows (DATA-INFERRED count from the CSV).
2. **REASON codes disagree with each other.** For FY2015-FY2024, interest_income and other_income_expense_net carry `not_in_template`. Both data points are inside the 46-cell template, and FY2025/26 carry `combined` for the same situation. The substance holds:
   - MSFT's face line "Other income (expense), net" contains interest/dividend income and interest expense (note: Components of Other Income), so serving it would double-count interest_expense. Ledger 2026-11-11 says the same: "Total non-operating is not other income".
   - interest_income is printed only combined with dividends.

   `data-team/companies/MSFT.md` still lists other_income_expense_net as mapped to NonoperatingIncomeExpense, which contradicts the served REASON.
3. **Stale proof row.** A cell_proof_v1_2026-10-31 row (NOT_PRESENTED, shown 34.3B) is still stored for D&A FY2026, beside the current v3 rows.

## Out-of-sample wrong values found while checking restatements (FILING-CHECKED, not counted in the 1/30)

These cells are PROVEN in cell_proof, but they are served from the original, pre-ASC 606 vintage, while neighbouring cells use the restated vintage:

| Cell | Served (vintage) | Latest eligible filing prints | Locator |
|---|---|---|---|
| revenue FY2016 | 85,320 (FY2016 10-K) | 91,154 | 0001564590-18-019062 R2 |
| revenue FY2017 | 89,950 (FY2017 10-K) | 96,571 | 0001564590-19-027952 R2 (also -18-019062 R2) |
| operating_expenses FY2016 | 32,358 (FY2017 10-K parts; S&M 14,697) | 32,296 (R&D 11,988 + S&M 14,635 + G&A 4,563 + impairment 1,110) | 0001564590-18-019062 R2 |
| operating_expenses FY2017 | 33,363 (FY2017 10-K parts; S&M 15,539) | 33,285 (13,037 + 15,461 + 4,481 + 306) | 0001564590-18-019062 R2 (S&M 15,461 also in -19-027952 R2) |

gross_profit, operating_income, net_income, EPS, tax and sga_expense for FY2016-17 are served from the restated filings. The served FY2017 statement is therefore internally inconsistent: revenue 89,950 minus cost of revenue 34,261 is 55,689, but served gross_profit is 62,310. FY2018 revenue growth comes out at 22.7% instead of 14.3%.

The likely cause is a revenue tag change (SalesRevenueNet to RevenueFromContractWithCustomerExcludingAssessedTax at the FY2018 10-K) combined with the comparative-year era rule. The opex vintage was already marked "under review" in commit 871efe42. The cause is ASSUMED, not traced in code.

cell_proof shares the vintage choice with the mapper (commit 5011f781: "one latest_complete_filing shared by mapper and proof"), so the proof cannot catch this. Route to the FSN/mapper owner. Then replay every MSFT FY2016-17 cell, and every company with an ASC 606 full-retrospective restatement.

## Untested

The other 522 cells. Quarterly cells. Restated balance-sheet columns not in the draw: FY2016 total assets 193,694 vs 193,468, and FY2017 current assets 159,851 vs 162,696, both restated in the next 10-K. They are worth a targeted check. Whether the UI shows CF working-capital values with the element sign (#14, #16) or the printed sign was not checked.
