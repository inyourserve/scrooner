# Document-first reads, ranks 101-200 (Ritwik cloud), running totals

The numbers only, updated at each 10-company commit. Per-company files are `data-team/companies/reads/<TICKER>-docmap-2026-11-12.{md,csv}`.

| chunk | companies read | data points | value mismatches (printed vs companyfacts) | disagreements with my file | corrections to my exceptions file | corrections to the tag library |
|---|---|---|---|---|---|---|
| ranks 101-110 | 10 | 460 | 0 | 6 | 3 rows (SYK interest, SYK total liabilities, LOW operating income: latest-era map rows) | 0 |
| ranks 101-110, re-read with the shared tool (558f2f15) + hand checks | 10 | 380 | 0 | 6 machine errors corrected in checked rows | see the decisions file | 6 tool fixes proposed (NOTES-TAG-EXPERT-reads-101-110-2026-11-12.md) |
| ranks 111-120 (shared tool + hand checks) | 10 | 380 | 0 | 13 tool errors corrected in checked rows, 4 rows left as review | 0 | 0 new (same classes as the 6 proposed fixes) |

Hand checks on ranks 101-110:
- 67 rows hand-checked: every non-mapped row and every NOTE row.
- 30 mapped rows sampled. The disagreement rate is 1/30 = 3.3%, above 2%. Dhairya's ruling (2026-11-12): do not stop; the mapped sample is 20% until the tool fixes land.

Hand checks on ranks 111-120 (SNOW ABNB CME NET HCA TT MAR FCX BNY EQIX):
- 89 rows hand-checked (every non-mapped and NOTE row) plus FCX interest_expense.
- 58 mapped rows sampled (20%). Disagreements: 2/58 = 3.4% (ABNB accounts_payable and HCA goodwill: bundled lines, now combined).
- Corrections in checked rows: 14 (opex component sums 5: ABNB, TT, FCX, EQIX + CME opex mapped; total_debt 5: SNOW, NET, CME, BNY, EQIX; CME interest; EQIX capex; MAR receivables; FCX net interest combined).
- Left as review (R page read owed): CME shares (R88), TT shares (R76), HCA SG&A (R40), BNY SBC (R119).
- BNY: 6 template rows set to OUT (bank).
- blind-grade.csv: 0 key_error rows for these tickers.
