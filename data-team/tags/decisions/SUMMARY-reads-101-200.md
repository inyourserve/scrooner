# Document-first reads, ranks 101-200 (Ritwik cloud), running totals

The numbers only, updated at each 10-company commit. Per-company files are `data-team/companies/reads/<TICKER>-docmap-2026-11-12.{md,csv}`.

| chunk | companies read | data points | value mismatches (printed vs companyfacts) | disagreements with my file | corrections to my exceptions file | corrections to the tag library |
|---|---|---|---|---|---|---|
| ranks 101-110 | 10 | 460 | 0 | 6 | 3 rows (SYK interest, SYK total liabilities, LOW operating income: latest-era map rows) | 0 |
| ranks 101-110, re-read with the shared tool (558f2f15) + hand checks | 10 | 380 | 0 | 6 machine errors corrected in checked rows | see the decisions file | 6 tool fixes proposed (NOTES-TAG-EXPERT-reads-101-110-2026-11-12.md) |
| ranks 111-120 (shared tool + hand checks) | 10 | 380 | 0 | 14 tool errors corrected (incl. FCX net interest), 4 review rows decided by the filing | 0 | 0 new (same classes as the 6 proposed fixes) |
| ranks 121-130 (shared tool + hand checks) | 10 | 380 | 0 | 11 corrections (8 checked rows + 3 sample disagreements), 0 rows left as review | 0 | 0 new |
| ranks 131-140 (shared tool + hand checks) | 10 | 380 | 0 | 21 corrections (16 tool errors + 4 sample disagreements + FCX debt held), 0 rows left as review | 0 | 0 new |

Hand checks on ranks 101-110:
- 67 rows hand-checked: every non-mapped row and every NOTE row.
- 30 mapped rows sampled. The disagreement rate is 1/30 = 3.3%, above 2%. Dhairya's ruling (2026-11-12): do not stop; the mapped sample is 20% until the tool fixes land.

Hand checks on ranks 111-120 (SNOW ABNB CME NET HCA TT MAR FCX BNY EQIX):
- 89 rows hand-checked (every non-mapped and NOTE row) plus FCX interest_expense.
- 58 mapped rows sampled (20%). Disagreements: 2/58 = 3.4% (ABNB accounts_payable and HCA goodwill: bundled lines, now combined).
- Corrections in checked rows: 14 (opex component sums 5: ABNB, TT, FCX, EQIX + CME opex mapped; total_debt 5: SNOW, NET, CME, BNY, EQIX; CME interest; EQIX capex; MAR receivables; FCX net interest combined).
- The 4 review rows, decided by the filing: CME shares mapped 358,953,100 (R88 class sum), TT shares not_presented (R77: 245.0M includes 23.5M subsidiary-held treasury), HCA SG&A not_presented (R40 548M is corporate-office costs only; my first mapping was a key error, corrected per Dhairya, card AD.7), BNY SBC mapped NOTE 508M (R119).
- EQIX total_debt 21,267M includes finance leases (lease note R88: 2,355). FCX net interest stays combined (no gross-minus-capitalized tie in R14/R48).
- BNY: 6 template rows set to OUT (bank).
- blind-grade.csv: 0 key_error rows for these tickers.

Hand checks on ranks 121-130 (APH CEG ADBE DUK PWR GD MELI ELV USB ICE):
- 77 rows hand-checked (every non-mapped and NOTE row).
- 60 mapped rows sampled (20%). Disagreements: 3/60 = 5.0% (MELI SG&A = G&A alone while S&M is printed; MELI accounts payable and ICE PP&E are bundled lines, now combined).
- Corrections in checked rows: 8 (opex: GD component sum, USB noninterest expense instead of the parent-only statement; total_debt: DUK VIE double count removed, MELI on the BS face, USB long-term debt added; GD D&A adds amortization; GD R&D component_in_note (R50); USB shares not_presented (R101 count is a rounded 1.6 billion)).
- USB: 6 template rows set to OUT (bank).
- Corrections to my own 111-120 rows: BNY opex = NoninterestExpense 13,054 (bank precedent C, SCHW); HCA SG&A not_presented (Dhairya).
- blind-grade.csv: 0 key_error rows for these tickers.

Finance-lease sweep of ranks 101-130 (founder 2026-11-04 item 5): every total_debt row was checked for finance leases.
- 2 re-keys: CME +50.7 (note R82) and GD +392 (R79, leases in other liabilities).
- Leases already inside the debt lines, no change: DUK (R138/R139), HCA (R65), MELI (R105), EQIX (explicit lines), and every row whose debt tag is LongTermDebtAndCapitalLeaseObligations*.
- No finance-lease facts in the filing: ABNB, ADBE, ADP, BNY, ELV, ICE, NET, PLD, SBUX, SNOW, SYK, TT, WDC.
- Open: FCX, where only per-asset rounded lease amounts are tagged (R82).

Hand checks on ranks 131-140 (WM CSX JCI EMR HOOD MRSH APP HWM CDNS SNPS), carrying sentence read for every NOTE fact:
- 77 rows hand-checked, 61 mapped rows sampled (20%).
- Disagreements: 4/61 = 6.6%. WM net interest is now combined; HOOD and CDNS accounts payable are bundled lines, now combined; SNPS SG&A was G&A alone while S&M is printed.
- 16 corrections in checked rows:
  - opex component sums at WM, APP, HWM, CDNS; CSX 'Total Expense' mapped (no cost of revenue);
  - CDNS cost of revenue = both printed cost-of-sales rows (722,249k);
  - net interest combined at APP, EMR, HWM;
  - HOOD interest not_presented (R51 securities-lending interest sits inside revenue);
  - WM shares: first not_presented, then mapped 402,900,000 (R93, 2025-12-31) under the 0.1% precision rule;
  - APP total_debt adds finance leases (R59);
  - CDNS total_debt on the BS face;
  - JCI interest mapped via a company-scope override (Dhairya condition 2'; R74: net of capitalized only, interest income on its own line);
  - EMR gross profit mapped NOTE (R77 undimensioned rows are Emerson's own; ties to R3).
- FCX total_debt: HELD as not_presented (finance_lease_total_not_disclosed; R82, R19, R14), per Dhairya's ruling.
- blind-grade.csv: 0 key_error rows for these tickers.
