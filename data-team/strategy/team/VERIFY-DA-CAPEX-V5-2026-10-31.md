# Verify: D&A/capex v5 (work/cash-flow/da-capex a02ed58, results/cf_da_capex_v5), 2026-10-31

Seed 20261031. Files: cells.jsonl.gz (sha256 ea5ffb3147a5...), summary.json. Claimed: D&A 35,447 published, 2,354 differ from production; capex 2,152 published-and-differ (outside perimeter classes). Evidence class: FILING-CHECKED (the cell's own accession, cash-flow R page; AMD income statement for the 2a tie). Verifier 2 (scrooner-bc).

## Result
- **D&A: NO.** 11 of 15 graded shown values right, 4 wrong; 2 more are definition questions and 1 was not readable. The 2a tie-out is right (AMD FY2025 3,004M). Hiding 3 of 3 combined lines is right.
- **Capex: NO (2 defects).** 13 of 15 right, 2 wrong. In the 13, production is wrong or only rounded against the same filing.
- My count of differing cells is D&A 2,388 and capex 2,250 (any nonzero difference). The run reports 2,354 / 2,152, so it probably uses a tolerance.

## Method
Each drawn cell vs the printed lines of its claimed filing's cash-flow statement: column by end date (+-10 days) and duration; slot members matched to face lines by label, value and sign. Production value from the cell file (`prod_value`). Not used as evidence: production, builder code.

## Sample
D&A: 16 seeded from published cells that differ from production, plus AMD FY2025 (2a tie), plus 3 seeded `da_combined_with_other_items` cells where production shows a value. Capex: 15 seeded from published cells with no perimeter case (`cases` empty) that differ from production.

## Cell table: D&A
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| EXC | 6M 2018 | D&A 3,000 (Exelon block, first) | 3,000M | 2,179M | right |
| ANF | FY2020 | D&A 166,281,000 printed on two rows (same fact, two labels) | 332,562,000 | 166,281,000 | **wrong: double count** |
| CUBE | 9M 2018 | 106,986K | 106,986K | 105,251K | right |
| PCAR | 6M 2017 | PP&E D&A 151.5; equipment on operating leases 376.7 | 151.5M | 528.2M | definition: lessor-equipment depreciation excluded |
| FTAI | Q1 2015 | D&A 10,562; amortization of lease intangibles and incentives 2,156 | 12,718K | 10,562K | definition: lease incentives (a revenue offset) included |
| HAS | FY2022 | PP&E 127.3 + intangibles 105.3 | 232.6M | 232.5M | right |
| SUI | FY2018 | D&A 274,432 + ground-lease intangibles 1,638 | 276,070K | 287,262K | right (asset amortization only) |
| IRM | FY2021 | Depreciation 465,072; Amortization 231,898 incl. 16,548 financing costs | 465,072K | 680,422K | **wrong: amortization dropped**; production = 465,072 + 231,898 - 16,548 exactly |
| TRNO | 6M 2025 | D&A 54,953; amortization of lease intangibles printed (10,342) | 65,295K | 54,953K | **wrong: negative lease-intangible line added as positive** |
| FR | 6M 2020 | not read (kit and hand regex missed the row) | 50,695K | 63,163K | ungraded |
| D | Q1 2024 | 694 (Dominion block, first) | 694M | 621M | right |
| SWK | 6M 2020 | PP&E 187.0 + intangibles 98.8 | 285.8M | 187.0M | right |
| ZS | 9M FY2025 | 74,101 + acquired intangibles 12,740 | 86,841K | 74,101K | right |
| OMC | 6M 2026 | "Depreciation and amortization of right-of-use assets" 98.1 (the only depreciation line; IS prints D&A 333.2) + intangibles 235.1 | 235.1M | 333.2M | **wrong: depreciation line excluded** |
| VLO | FY2025 | 3,158 | 3,158M | 63M | right |
| FRHC | FY2025 | 17,158 | 17,158K | 12,138K | right |
| AMD | FY2025 | CF D&A 750 + Amortization 2,254; IS amortization of acquisition intangibles 1,031 (COGS) + 1,223 = 2,254 | 3,004M | blank | right (2a tie holds) |
| BEN | 6M 2021 | "Depreciation and other amortization" 44.8; intangibles 116.1 | hidden | 44.8M | hide right |
| AMGN | 9M 2025 | "Depreciation, amortization and other" 4,035 | hidden | 4,035M | hide right |
| ANET | FY2018 | "Depreciation, amortization and other" 27,671 | hidden | 27,671K | hide right |

## Cell table: capex
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| GEN | 6M to 2015-10-02 | 149 | 149M | 111M | right |
| EXLS | 6M 2020 | 22,051 | 22,051K | 22,351K | right |
| XPO | FY2016 | 483.4 | 483.4M | 483M | right (prod rounded) |
| AEIS | 9M 2021 | 22,721 | 22,721K | 21,184K | right |
| RTX | FY2019 | Capital expenditures 2,256 (collaboration intangibles 351 separate) | 2,256M | 1,868M | right |
| GE | 9M 2023 | PP&E and internal-use software (combined) 1,065 | 1,065M | 612M | right (combined line is the filer's total) |
| AR | Q1 2022 | unproved 23,789 + drilling and completion 184,557 + other P&E 7,530 = 215,876 | 7,530K | 215,876K | **wrong: oil-and-gas development lines dropped** |
| ADBE | FY2019 | 394,479 | 394,479K | 395M | right |
| ALSN | 9M 2020 | 80 | 80M | 84M | right |
| ANET | Q1 2024 | 9,395 | 9,395K | 9.4M | right |
| RKT | Q1 2025 | 14,005 (net of disposals) | 14,005K | 14.0M | right |
| CHTR | Q1 2022 | Purchases of PP&E 1,857; "Change in accrued expenses related to capital expenditures" +10 | 1,867M | 1,857M | **wrong: non-cash accrual change added** |
| MPLX | Q1 2019 | 457 | 457M | 575M | right |
| WYNN | 9M 2015 | 1,331,676 (net of construction payables) | 1,331,676K | 1,425,943K | right |
| CF | 9M 2015 | 1,791.3 | 1,791.3M | 1,791M | right |

## Withheld cells (avoidable holds)
None in scope beyond the combined-line holds, which are correct.

## False holds
None.

## Findings for the builder
1. **D&A double count (ANF):** when two face rows carry the same fact (same tag or same value from one context), count it once. Re-verify ANF FY2020.
2. **D&A sign (TRNO):** a lease-intangible amortization line printed negative is a net below-market-lease (revenue) adjustment, not D&A. Exclude lease-intangible and lease-incentive amortization (TRNO, FTAI), or at least never flip a printed sign.
3. **D&A dropped lines (IRM, OMC):** a combined "Amortization (includes deferred financing costs of $X)" line is D&A less the stated financing part (IRM 231,898 - 16,548). "Depreciation and amortization of right-of-use assets" is OMC's depreciation line (the IS D&A 333.2 confirms). Classify by tie to the IS D&A where one is printed.
4. **Capex E&P (AR):** "Drilling and completion costs" and "Additions to unproved/proved properties" are capex for oil and gas filers; the ppe-nature filter missed them. Production 215,876K equals the face sum.
5. **Capex supplemental lines (CHTR):** "Change in accrued expenses related to capital expenditures" is a non-cash reconciling item, not a payment. Exclude change-in-accrual / payables lines from capex members.
6. Definition questions for the Standardization Lead: lessor operating-lease equipment depreciation in D&A (PCAR), lease-incentive amortization (FTAI).

## Requests and disk
SEC requests: 75. Scratch holds only the draw. No DB access.

## Untested scope
16 of 2,388 D&A and 15 of 2,250 capex differences drawn; agree cells and production-blank cells not sampled; perimeter classes excluded by brief.
