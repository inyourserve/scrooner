# Verify: D&A/capex v10 (work/cash-flow/da-capex 67e4e48, results/cf_da_capex_v10), 2026-11-01

Seed 20261101 (own draw; the branch's verifier_draw file was not used). Files: cells.jsonl.gz, summary.json. Claimed: D&A 33,364 published, 1,723 differ; capex 1,455 published-and-differ. Evidence class: FILING-CHECKED (each cell's own accession, cash-flow and income-statement R pages). Verifier 2 (scrooner-bc).

## Result
- **Capex: YES.** 15 of 15 right. Production is wrong or only rounded in every one.
- **D&A: NO (2 cells, one class each).** 18 of 20 right, 2 wrong (GD, KEY).
- **V5 fixes confirmed in v10:** ANF 166,281K, TRNO 54,953K, IRM 680,422K, OMC 333.2M, AR 215,876K and CHTR 1,857M each equal the face. PCAR and FTAI are held (`da_definition_question`).
- **AMZN combined holds: 5 of 5 correctly held, not over-held.** The full label is "Depreciation and amortization of property and equipment and capitalized content costs, operating lease assets, and other". It includes operating-lease asset amortization and "other". Publishing it as D&A needs a definition call.

## Method
As in VERIFY-DA-CAPEX-V5-2026-10-31: column by end date (+-10 days) and duration, members matched by label, value and sign. The income-statement D&A was used as a cross-check where printed.

## Sample
`random.Random(20261101)`: 20 of 1,847 D&A published-and-differ cells, 15 of 2,123 capex published-and-differ cells with no perimeter case, 5 of 68 AMZN "property and equipment and capitalized content" holds. (Any nonzero difference; the run's own counts use a tolerance.)

## Cell table: D&A
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| VRSK | 6M 2025 | fixed assets 133.4 + intangibles 32.1 | 165.5M | 133.4M | right |
| J | 9M to 2016-07-01 | under "Depreciation and amortization:": PP&E 63,447 + intangibles 35,499 | 98,946K | 63,447K | right |
| CVS | FY2017 | 2,479 | 2,479M | 2,480M | right |
| FRHC | FY2026 | 34,560 | 34,560K | 26,368K | right |
| GD | Q1 2024 | depreciation of PP&E 152; "Amortization of intangible and finance lease right-of-use assets" 59 | 152M | 211M | **wrong: amortization line dropped** |
| ECHO | 6M 2017 | CF D&A 256,776 (IS 245,117) | 256,776K | 245,117K | right (CF line) |
| DDS | 6M to 2018-08-04 | CF 113,174 (IS 112,224) | 113,174K | 112,224K | right (CF line) |
| EQT | FY2018 | depreciation and depletion 1,729,739 + intangibles 77,374 (incl. discontinued; IS continuing 1,569,038) | 1,807,113K | 1,569,038K | right (total incl. discontinued) |
| CVI | FY2018 | 213 (IS 202 + 11) | 213M | 274M | right |
| SYK | FY2017 | depreciation 271 + intangibles 371 | 642M | 859M | right |
| ATO | FY2015 | under D&A: charged to D&A 274,796 + charged to other accounts 1,209 | 276,005K | 274,796K | right (CF add-back) |
| EXE | FY2017 | 995 (IS 913 + 82) | 995M | 82M | right |
| MLI | Q1 2019 | CF 10,635 (IS 10,555) | 10,635K | 10,555K | right (CF line) |
| KEY | FY2021 | "Depreciation and amortization expense, net" 32; IS intangible amortization alone 58 | 32M | 298M | **wrong: a net line below its own intangible amortization** |
| SPG | FY2023 | CF 1,333,584 (IS 1,262,107) | 1,333,584K | 1,262,107K | right (CF line) |
| JAZZ | FY2025 | intangibles 654,661 + depreciation 41,636 | 696,297K | 41.6M | right |
| PCVX | Q1 2022 | 582 (operating ROU 1,787 excluded) | 582K | 600K | right |
| GTLB | FY2023 | 2,362,000 + 3,231,000 | 5,593,000 | 3,231,000 | right |
| PCVX | FY2025 | 16,396 | 16,396K | 16.4M | right |
| GPN | 9M 2025 | PP&E 319,726 + acquired intangibles 759,634 | 1,079,360K | 888,088K | right |

## Cell table: capex
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| TFX | FY2023 | 91,442 | 91,442K | 46,421K | right |
| RGEN | 9M 2018 | 8,580 | 8,580K | 7,368K | right |
| APD | 9M 2016 | 797.3 | 797.3M | 700.9M | right |
| WEX | 9M 2022 | PP&E and capitalized software (combined) 75,476 | 75,476K | 75.5M | right |
| FLS | FY2019 | 66,170 | 66,170K | 75,716K | right |
| AMRX | FY2021 | PP&E 47,728 + deposits for future PP&E 3,211 | 50,939K | 47,728K | right (deposits are PP&E payments) |
| FN | 9M to 2021-03-26 | 29,061 | 29,061K | 33,269K | right |
| TJX | FY2020 | 568,021 | 568,021K | 568M | right |
| AMRX | Q1 2026 | 8,175 + deposits 5,685 | 13,860K | 8,175K | right |
| BAX | Q1 2015 | 521 | 521M | 214M | right |
| VRTX | Q1 2021 | 70,926 | 70,926K | 70.9M | right |
| CSX | Q1 2024 | 524 | 524M | 517M | right |
| NPO | 6M 2019 | 17.0 | 17.0M | 10.0M | right |
| PAG | Q1 2025 | 76.6 | 76.6M | 84.7M | right |
| REGN | FY2017 | 272,626 | 272,626K | 272.6M | right |

## Withheld cells (avoidable holds)
None: the 5 AMZN holds are correct holds under the rule.

## False holds
None.

## Findings for the builder
1. **GD:** "Amortization of intangible and finance lease right-of-use assets" is D&A (finance-lease ROU amortization is depreciation of a leased asset). Classify intangible / finance-lease ROU amortization as asset D&A; keep only operating-lease ROU amortization excluded. Re-verify: GD Q1 2024 = 211M.
2. **KEY:** a bank's "Depreciation and amortization expense, net" nets other items (32 vs intangible amortization 58 on the IS). Hold a D&A line labelled "net" when it is below a printed component; do not publish it.
3. AMZN: definition question for the Standardization Lead, not a builder defect. The line bundles operating-lease asset amortization and "other".
4. Note: in ECHO, DDS, MLI and SPG the CF D&A line exceeds the IS D&A. The slot follows the CF line, consistent with the family definition. If the product shows IS D&A anywhere, the two will differ by design.

## Requests and disk
SEC requests: 109. No DB access. Scratch holds only the draw.

## Untested scope
20 of 1,847 D&A and 15 of 2,123 capex differences; agree and production-blank cells not sampled; perimeter classes excluded by brief.
