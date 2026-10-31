# Verify: income-statement release package 1 (origin/work/income-statement/slot-records 9a7e146, results/release_is_1), 2026-11-01

Seed 20261101. Files: is_{revenue,net_income,operating_income}_release1_cells.jsonl. Claimed: revenue 2,497 cells (1,783 differ / 714 fill), net income attributable 917 (810 / 107), operating income 79 (62 / 17). Evidence class: FILING-CHECKED (each cell's own accession, income-statement R page, column by date and duration). Verifier 2 (scrooner-bc).

## Result
- **Net income attributable: YES.** 18 of 18 right (15 differences, 3 fills). Every slot is the printed attributable line. Production most often carries ProfitLoss (including NCI) or a later or computed value.
- **Operating income: YES.** 10 of 10 right; production's computed values are wrong in 8.
- **Revenue: NO (1 class).** 20 of 21 right (16 differences incl. Exelon Q1/Q2 2018 and Aptiv Q1 2015, 5 fills). Wrong: Snap-on Q1 2016. The face prints "Net sales" 834.2 and "Financial services revenue" 66.3 and no total line. The slot takes "Net sales" as the printed total (834.2M); total revenue is 900.5M (production's value).

## Method
Kit filing_kit at origin/main (includes the duration-header fix 2183604). Income statement by `select_income_statement` (combined registrant pages: first block). Shown value = the printed line of the slot's label at the matching column.

## Sample
`random.Random(20261101)` over each family's release-1 cells sorted by (cik, start, end): revenue 2 Exelon 2018 + 13 differences, plus Aptiv Q1 2015 (added after the draw), 5 fills; net income 15 differences + 3 fills; operating income 10 of 79.

## Cell table: revenue
| CIK | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| EXC 1109357 | Q1 2018 | Revenues 9,693 (Exelon block) | 9,693M | 10M (alternative revenue programs line) | right |
| EXC 1109357 | Q2 2018 | Total operating revenues 8,076 | 8,076M | -26M | right |
| APTV 1521332 | Q1 2015 | Net sales 3,797 | 3,797M | 1M | right |
| BE 1664703 | FY2024 | Total revenue 1,473,856 | same | 1,441,394K | right |
| RYN 52827 | FY2021 | SALES 1,109,597 (kit did not select the page; read by name) | same | 1,108,445K | right |
| 82811 | Q2 2017 | Net Sales 869.2 | same | 959.7M (later filing) | right |
| 1057877 | FY2023 | Revenues 1,766,356 (electric 1,762,894 + other 3,462) | same | 1,639,612K | right |
| TAP 24545 | Q2 2022 | Sales 3,501.4, excise, Net sales 2,921.7 | 2,921.7M | 3,501.4M | right (net of excise) |
| 1601046 | 6M FY2016 | Total net revenue 1,452 | same | 1,461M (later filing) | right |
| CHE 19584 | Q2 2024 | Service revenues and sales 595,880 | same | 374,558K | right |
| TAP 24545 | 6M 2019 | Net Sales 5,251.6 (Sales 6,420.1) | same | 6,420.1M | right |
| FANG 1539838 | Q2 2021 | Total revenues 1,681,000,000 | same | 1,667M | right |
| M 794367 | Q2 2026 | Net sales 4,866 + other revenue 193 = Total revenue 5,059 | 5,059M | 4,866M | right |
| PPL 922224 | Q2 2019 | Operating Revenues 1,803 (PPL block) | same | 1,773M | right |
| STLD 1022671 | 9M 2019 | Total net sales 8,114,795 | same | 8,104,129K | right |
| SNA 91440 | Q1 2016 | Net sales 834.2; Financial services revenue 66.3; no total printed | 834.2M | 900.5M | **wrong: financial services revenue omitted** |
| fills: 51253 9M 2016, 1088856 6M 2015, 1341766 Q3 2015, 1125376 Q2 2015, 29644 Q1 FY2016 | | printed lines 2,353,790K; 22,058K; 3,652,424; 311,056K; 517,200K | same | blank | right (5) |

## Cell table: net income attributable
| CIK | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| SCHW 316709 | FY2023 | Net Income 5,067; available to common 4,649 | 5,067M | 4,649M | right (attributable, before preferred) |
| PBF 1534504 | Q3 2019 | NI 86.3; NCI 16.8; attributable 69.5 (first block) | 69.5M | 86.3M | right |
| LNG 3570 | FY2022 | NI 2,635; NCI 1,207; attributable 1,428 | 1,428M | 2,635M | right |
| ALV 1034670 | FY2020 | NI 188.3; NCI 1.4; attributable 186.9 | 186.9M | 188M | right |
| MTZ 15615 | Q2 2018 | NI 80,401; NCI -91; attributable 80,492 | 80,492K | 80.4M | right |
| CBRE 1138118 | Q1 2023 | 125,072; 8,180; 116,892 | 116,892K | 125M | right |
| NLY 1043219 | Q3 2016 | 730,880; -336; 731,216 | 731,216K | 730,880K | right |
| HRS 202058 | Q3 FY2015 | attributable 125.7 | 125.7M | 125.6M | right |
| CBRE 1138118 | Q3 2023 | 200,945; 10,392; 190,553 | 190,553K | 201M | right |
| BAX 10456 | 6M 2018 | Net income 732 | 732M | 723M | right |
| TRMB 864749 | FY2014 | 213,888; -230; 214,118 | 214,118K | 213.9M | right |
| CZR 1590895 | FY2025 | -437; -65; -502 | -502M | -437M | right |
| HUT 1964789 | FY2025 | -247,998; +21,849; -226,149 | -226,149K | -247,998K | right |
| GWW 277135 | Q3 2017 | 170,816; 8,810; 162,006 | 162,006K | 170,816K | right |
| VOYA 1535929 | Q3 2017 | 214.0; 65.4; 148.6 | 148.6M | 214M | right |
| fills: CB 896159 6M 2026 5,174; HCA 860730 Q2 2026 1,699; 775158 Q2 2026 183.2 | | printed | same | blank | right (3) |

## Cell table: operating income
| CIK | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| BKH 1130464 | Q3 2016 | 58,409 | same | 48,770K (computed) | right |
| WEX 1309108 | Q3 2017 | 63,723 | same | 62,657K | right |
| LNG 3570 | 9M 2016 | -151,737 (fixed kit; 3M column is 15,276) | -151,737K | -505M | right |
| 775158 | Q2 2026 | 243.2 | same | blank | right |
| 1004434 | Q1 2017 | 176.6 | same | 152.6M | right |
| 1425205 | 9M 2015 | -19,406 | same | -19,381K | right |
| BKH 1130464 | Q2 2016 | 35,298 | same | 27,652K | right |
| PANW 1327567 | 6M FY2015 | -62,279 | same | +50.5M | right |
| 1039399 | 9M 2017 | 40,904 | same | 301,884K | right |
| 1616862 | 6M 2026 | 313 | same | blank | right |

## Withheld cells / false holds
Not in scope (release cells only).

## Findings for the builder
1. **Revenue G1 gate:** "Net sales" is a printed total only when no other revenue line sits beside it. Snap-on (and any filer with "Financial services revenue", "Other revenue" or "Rental income" lines and no total) needs the sum of the revenue lines or a hold. Re-verify Snap-on Q1 2016 = 900.5M, and scan the release for G1 cells whose label is "Net sales"/"Sales" with a sibling revenue line.
2. filing_kit `select_income_statement` returns None for Rayonier's "CONSOLIDATED STATEMENTS OF INCOME AND COMPREHENSIVE INCOME" (2022 10-K). A kit gap, not a builder defect; read by name here.
3. Production often takes a later filing's or an alternative tag's value (Exelon's alternative-revenue-programs line, Aptiv 1M). The release corrects those.

## Requests and disk
SEC requests: 103. No DB access.

## Untested scope
21 of 2,497 revenue, 18 of 917 net income, 10 of 79 operating income; precision and restated-copies strata are outside release 1 and not sampled.
