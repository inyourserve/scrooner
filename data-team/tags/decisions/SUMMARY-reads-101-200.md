# Document-first reads, ranks 101-200 (Ritwik cloud), running totals

The numbers only, updated at each 10-company commit. Per-company files are `data-team/companies/reads/<TICKER>-docmap-2026-11-12.{md,csv}`.

| chunk | companies read | data points | value mismatches (printed vs companyfacts) | disagreements with my file | corrections to my exceptions file | corrections to the tag library |
|---|---|---|---|---|---|---|
| ranks 101-110 | 10 | 460 | 0 | 6 | 3 rows (SYK interest, SYK total liabilities, LOW operating income: latest-era map rows) | 0 |
| ranks 101-110, re-read with the shared tool (558f2f15) + hand checks | 10 | 380 | 0 | 6 machine errors corrected in checked rows | see the decisions file | 6 tool fixes proposed (NOTES-TAG-EXPERT-reads-101-110-2026-11-12.md) |
| ranks 111-120 (shared tool + hand checks) | 10 | 380 | 0 | 14 tool errors corrected (incl. FCX net interest), 4 review rows decided by the filing | 0 | 0 new (same classes as the 6 proposed fixes) |
| ranks 121-130 (shared tool + hand checks) | 10 | 380 | 0 | 11 corrections (8 checked rows + 3 sample disagreements), 0 rows left as review | 0 | 0 new |
| ranks 131-140 (shared tool + hand checks) | 10 | 380 | 0 | 21 corrections (16 tool errors + 4 sample disagreements + FCX debt held), 0 rows left as review | 0 | 0 new |
| ranks 141-150 (shared tool + hand checks) | 10 | 380 | 0 | 27 corrections (25 tool errors + 2 sample disagreements), 0 rows left as review | 0 | 1 new class (cost of revenue split across member rows) |
| ranks 151-160 (shared tool + hand checks) | 10 | 380 | 0 | 36 corrections (35 tool errors incl. 6 OUT + 1 sample disagreement), 3 definition calls (EPD MLP) | 0 | 2 new classes (IS title with non-breaking spaces; float-formatted printed values) |

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

Card rules confirmed by Dhairya on 2026-11-12, for the Tag Expert:
- **Interest override, condition (2'):** the "net of capitalized interest" line and a separate interest-income line must be in the same printed table. That table can be the face or a note. Example: JCI R74, mapped NOTE at 223.
- **Shares from a narrative fact:** allowed when all four hold:
  - it is an XBRL-tagged fact;
  - it is dated at the BS date;
  - it counts consolidated common shares;
  - it is precise to within 0.1% of the count.
  - Passes: WM 402.9M (0.012%). Fails: USB "1.6 billion" (about 6%).

Hand checks on ranks 141-150 (INTU PNC DDOG AMT MRNA WMB MMM CTAS MCO REGN), carrying sentence read for every NOTE fact:
- 80 rows hand-checked; 59 mapped rows sampled (20%).
- Disagreements: 2/59 = 3.4%:
  - PNC net income: the ProfitLoss row includes NCI, and no attributable line is printed, so it is now combined.
  - MCO accounts payable: a bundled line, now combined.
- New tool error class, cost of revenue printed as several rows on one tag (member rows):
  - the tool took only the first row;
  - corrected to the sum at INTU (4,253), AMT (2,748.1), WMB (2,199) and REGN (2,100.7);
  - same as CDNS in 131-140.
- Opex component sums, each tying to revenue - COR - OI: INTU, AMT, MRNA, WMB, MMM, CTAS, MCO, REGN.
- Bank (PNC):
  - opex = NoninterestExpense;
  - 6 template rows OUT.
- total_debt:
  - PNC = 'Total borrowed funds' 57,101 (the tool double-counted senior debt);
  - DDOG on the BS face;
  - finance leases added at MRNA (+45, R70) and REGN (+720.0 face line);
  - AMT leases already inside long-term obligations (R94).
- AMT dividends = the CF 'Distributions paid' 3,157.2, not distributions declared (3,180.8).
- WMB goodwill combined: the R64 466 is acquisition goodwill, and the BS bundles goodwill into intangibles.
- D&A:
  - INTU = depreciation + amortization (846);
  - CTAS combined (the amortization line bundles capitalized contract costs).
- Gross profit:
  - CTAS GP mapped NOTE (R85 total ties to R3);
  - AMT GP and PNC SG&A are component_in_note (segment-only values).
- WMB cash interest = 1,404 (R95 consolidated row).
- MCO net interest: combined.
- blind-grade.csv: 0 key_error rows for these tickers.

Hand checks on ranks 151-160 (EOG UPS MDLZ DASH SHW ECL BX TRV CI EPD), carrying sentence read for every NOTE fact:
- 110 rows hand-checked, 54 mapped rows sampled (20%).
- Disagreements: 1/54 = 1.9%. EPD 'Depreciation and accretion' is now combined.
- New tool error: SHW's income-statement title uses non-breaking spaces. The tool missed the whole IS and took 12 data points from notes; all 12 are re-keyed to the R3 face.
- New tool error: the tool writes some printed values as floats with 4 significant digits (e.g. 8.518e+09). This violates the Decimal rule.
  - 18 CSV cells in ranks 101-200 are replaced with the exact printed value from the cached R page (scripts/fixfloat.py).
  - 8 era-evidence strings in md prose (older filings) still carry floats; they are flagged for the docmap.py owner.
- Opex:
  - mapped totals where no cost of revenue is printed: EOG, UPS;
  - component sums tying to revenue - COR - OI: DASH, ECL;
  - EPD 'Total operating costs and expenses' includes cost of sales: combined.
- total_debt:
  - finance leases added at SHW (+195.4, R83) and EPD (+16, R119);
  - leases already inside the debt lines: EOG (R84), UPS (R82), MDLZ (R59), CI (R84);
  - BX = BS 'Loans Payable' (the tool used scheduled principal);
  - TRV and DASH on the BS face.
- Other fixes:
  - EOG capex = O&G additions + other PP&E additions;
  - CI capex 'purchases, net': combined;
  - ECL D&A adds amortization;
  - ECL net interest: combined;
  - MDLZ shares 1,281,576,414 (R101 printed ending balance).
- EOG interest: mapped through an override (condition (1): R3 face prints incurred 321 - capitalized 86 = 235).
- TRV (insurer): 6 template rows OUT.
- EPD (MLP): definition calls for Dhairya on partners' equity as stockholders_equity, distributions as dividends_paid, and units as shares_outstanding.
- blind-grade.csv: 0 key_error rows for these tickers.
