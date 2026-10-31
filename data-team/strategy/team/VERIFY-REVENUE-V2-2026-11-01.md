# Verify: revenue release v2 (origin/work/income-statement/slot-records 2889959, results/release_is_revenue_1), 2026-11-01

Seed 20261101. File: is_revenue_release1_cells.jsonl (2,444 cells; sha256 b98f509f... per PACKAGE.json). Strata: plain_face 1,429, dimensioned_face 1,012, calc_sum 3. Evidence class: FILING-CHECKED (each cell's own accession, income-statement R page; filing_kit at origin/main). Verifier 2 (scrooner-bc).

## Result
**Release cells: YES.** 23 of 23 right.
- plain face: 10 of 10.
- dimensioned face: 10 of 10, incl. Snap-on 9M 2018 3,035.2M (= Net sales 2,788.2 + Financial services 247.0) and FY2018 4,070.4M (= 3,740.7 + 329.7). The V1 Snap-on defect is fixed.
- calc sum: 3 of 3 (NiSource FY2017-2019: Customer revenues + Other revenues = printed Total Operating Revenues).
**Sibling holds (542): not verified.** PACKAGE.json gives only counts (hold_sibling_custom 347, hold_sibling_revenue_no_total 195); no cell list is committed.

## Sample
`random.Random(20261101)` over release cells sorted by (cik, start, end): 10 plain; Snap-on 9M and FY2018 plus 8 dimensioned; all 3 calc-sum.

## Cell table
| Stratum | CIK | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|---|
| plain | 51253 | Q2 2016 | Net sales 793,478 | same | blank | right |
| plain | 82811 | 9M 2016 | Net Sales 2,466.4 | same | blank | right |
| plain | 1130310 | Q2 2022 | utility 1,862 + non-utility 82 = Total 1,944 | 1,944M | 1,959M | right |
| plain | 29534 | 9M FY2016 | Net sales 15,977,352 | same | blank | right |
| plain | 2001184 | 6M 2026 | patient revenue 2,847,456 + other 1,036 = Total Revenue 2,848,492 | same | 2,847,456K | right |
| plain | TAP 24545 | FY2022 | Sales 12,807.5; Net sales 10,701.0 | 10,701.0M | 12,807.5M | right (net of excise) |
| plain | TAP 24545 | 9M 2025 | Sales 9,914.5; Net sales 8,478.4 | 8,478.4M | 9,914.5M | right |
| plain | VST 1692819 | 9M 2019 | Operating revenues 8,949 | same | 8,807M | right |
| plain | ACM 868857 | FY2015 | Revenue 17,989,880 | same | blank | right |
| plain | 916365 | 9M 2017 | Net sales 5,303,544 | same | blank | right |
| dim | SNA 91440 | 9M 2018 | total 3,035.2 (2,788.2 + 247.0) | 3,035.2M | 2,772.3M | right |
| dim | SNA 91440 | FY2018 | total 4,070.4 (3,740.7 + 329.7) | 4,070.4M | 3,719.6M | right |
| dim | SUI 912593 | 6M 2017 | Total revenues 472,299 | same | 460,723K | right |
| dim | GE 40545 | Q3 2018 | Sales 27,465 + GE Capital 2,109 = Total revenues 29,573 | 29,573M | 27,465M | right |
| dim | RYN 52827 | Q3 2021 | SALES 364,726 | same | 364,382K | right |
| dim | CCI 1051470 | 6M 2017 | Net revenues 2,054,277 | same | blank | right |
| dim | 1849253 | Q2 2024 | Total revenue 695,441 (incl. fiduciary income 15,193) | same | 680,248K | right |
| dim | DUK 1326160 | Q1 2021 | Total operating revenues 6,150 | same | 6,094M | right |
| dim | SWX 1692115 | 9M 2016 | gas 980,927 + construction 838,038 = 1,818,965 | same | 1,743,762K | right |
| dim | EVRG 1711269 | Q1 2018 | Westar Energy statement: OPERATING REVENUES 600.2 | same | 601.3M | right (as presented) |
| calc | NI 1111711 | FY2017 | 4,730.2 + 144.4 = Total Operating Revenues 4,874.6 | 4,874.6M | 4,730.2M | right |
| calc | NI 1111711 | FY2018 | 4,991.1 + 123.4 = 5,114.5 | 5,114.5M | 4,991.1M | right |
| calc | NI 1111711 | FY2019 | 5,053.4 + 155.5 = 5,208.9 | 5,208.9M | 5,053.4M | right |

## Findings for the builder
1. Commit the 542 sibling-hold cells (cik, start, end, accession, sibling labels) so the hold stratum can be drawn.
2. Cosmetic: calc-sum cells carry the first member's label ("Customer revenues") although the value is the printed total; use the total's label.

## Requests and disk
SEC requests: 46. No DB access.

## Untested scope
Precision stratum (827) and restated-copies hide stratum (2,439) not sampled; sibling holds pending a cell list.
