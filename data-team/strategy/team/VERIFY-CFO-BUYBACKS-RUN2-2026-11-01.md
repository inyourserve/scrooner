# Verify: CFO and buybacks run 2 (work/cashflow/cfo-buybacks f636f57, results/cf_run2), 2026-11-01

Seed 20261101. Files: cfo/buybacks_prod_differs.json (301 / 267), cfo/buybacks_prod_blank.json (563 / 812), *_cells.jsonl.gz, prod_compare.json. Evidence class: FILING-CHECKED (each claimed accession's cash-flow R page), except the 2 stub holds (DATA-INFERRED, see below). Verifier 2 (scrooner-bc).

## Result
- **CFO: YES.** 10 of 10 differences: slot = printed total, production wrong (incl. LPLA 338,995K vs 104,831K, RJF 325,619K vs 422M). 5 of 5 blanks: slot = face. 2 of 2 stub holds kept (durations 27% and 49% off nominal; kit could not parse those pages).
- **Buybacks: NO (6 cells that the run's own hold rules should have caught).** 14 of 20 differences right. UBER FY2017 = 131M as required. 8 of 10 blanks right, 1 perimeter (HEI), 1 not blank (DPZ).
- **Blank lists still contain cells production has**, at exactly 10 days apart: DPZ 6M to 2021-06-20 (production 1,025M) and AXS 6M 2026 (production 1,150,940K = slot). They are harmless (values agree) but inflate "new values". The rest re-checked blank with a +-10-day match.

## Method
As in run 1: column by end date (+-10 days) and duration (36-week YTD = the 9M cell), members matched by label, value and printed sign. Blanks re-checked in analytics.canonical_fact (cfo/cfo_resolved, share_buybacks/_resolved), one connection.

## Cell table: buyback differences
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| DHI | 6M 2023 | Repurchases (419.8); withholding (55.8) excluded | 419.8M | 421.3M | right |
| DHI | 9M 2026 | (2,209.4) | 2,209.4M | 2,200M | right |
| ROST | 9M 2020 | Treasury stock purchased (45,091); Repurchase of common stock (132,467) | 177,558K | 132,467K | **should hold: two repurchase lines summed (perimeter_multiple_repurchase_lines)** |
| CHDN | 6M 2018 | (514.7) | 514.7M | 501.8M | right |
| BPOP | 9M 2024 | "Net payments for repurchase of common stock" (59,556) | 59,556K | -65,923K | right (net outflow shown positive) |
| BRO | FY2022 | Purchase of treasury stock (74.1); withholding (48.8) excluded | 74.1M | 74.0M | right |
| LDOS | FY2020 | "Repurchases of stock and other" (105) | 105M | 67M | **should hold: combined with other items** |
| MPWR | 9M 2025 | (5,703) | 5,703K | 4.7M | right |
| PWR | Q3 2022 | (20,751) | 20,751K | 21,033K | right |
| EL | FY2016 | (889.9) | 889.9M | 890M | right |
| G | 6M 2021 | (147,224) | 147,224K | 147,152K | right |
| SGI | Q1 2020 | (199.3) | 199.3M | 187.5M | right |
| UNP | 9M 2018 | (7,024); "repurchased but not yet paid" +10 excluded | 7,024M | 6,304M | right |
| FIS | Q1 2015 | "Treasury stock activity" (155.9) | 155.9M | 150.4M | **should hold: "activity" may be net or include withholding** |
| AAON | Q1 2025 | "Repurchase of stock" printed 31,536 without parentheses; withholding printed (6,768) | 31,536K | 30.0M | **should hold: sign_unclear** |
| ROST | 9M 2015 | Treasury stock purchased (67,083); Repurchase (530,303) | 597,386K | 530,303K | **should hold (as ROST 2020)** |
| AUR | FY2021 | Payments to repurchase unvested early-exercised options 0 | 0 | 754.59M | right (production wrong) |
| VRSN | 6M 2021 | (361,199) | 361,199K | 361.2M | right |
| ROST | FY2019 | Treasury stock purchased (60,665); Repurchase (1,275,000) | 1,335,665K | 1,275,000K | **should hold (as ROST 2020)** |
| UBER | FY2017 | Repurchase of outstanding shares (131); option proceeds +3 now "inflow" | 131M | 32M | right |

## Cell table: buyback blanks
| Ticker | Period | Face | Slot | Verdict |
|---|---|---|---|---|
| AZO | 36 wks to 2025-05-10 | (1,135,260) | 1,135,260K | right |
| PEP | 36 wks to 2016-09-03 | common (2,079); preferred (3) excluded | 2,079M | right |
| AAON | 9M 2017 | (12,991) | 12,991K | right |
| COR | 9M 2026 | (1,000,052) | 1,000,052K | right |
| SO | 9M 2015 | Redemptions and repurchases: Common stock (115,000,000) | 115M | right |
| UI | 6M 2015 | (100,000) | 100,000K | right |
| BAM | Q3 2024 | 0 | 0 | right |
| SHW | Q1 2025 | (351.7) | 351.7M | right |
| HEI | Q1 FY2021 | "Common stock issued, repurchased and retired related to stock option exercises" (3,571) | 3,571K | perimeter: option-exercise related, not a buyback program |
| DPZ | 24 wks to 2021-06-20 | (1,025,000) | 1,025,000K | right value; production already has it (not blank) |

## Cell table: CFO
| Ticker | Period | Face | Slot | Prod | Verdict |
|---|---|---|---|---|---|
| DVN | Q3 2016 | 726 | 726M | 727M | right |
| LPLA | 6M 2017 | 338,995 | 338,995K | 104,831K | right |
| MKSI | Q1 2021 | 126.9 | 126.9M | 127M | right |
| ALB | Q1 2024 | 97,954 | 97,954K | 97,485K | right |
| CSX | Q1 2023 | 1,251 | 1,251M | 1,256M | right |
| FTV | 9M to 2020-09-25 | 1,151.9 | 1,151.9M | 1,152M | right |
| RJF | Q1 FY2018 | 325,619 | 325,619K | 422M | right |
| LKQ | Q1 2016 | 130,207 | 130,207K | 134,844K | right |
| NBIX | 9M 2019 | 49,501 | 49,501K | 49.5M | right |
| GM | Q1 2016 | (164) | -164M | -108M | right |
| SO | FY2024 | 9,788 | 9,788M | blank | right |
| PEP | 36 wks to 2024-09-07 | 6,220 | 6,220M | blank | right |
| TXNM | FY2020 | 485,700,000 (first block) | 485.7M | blank | right |
| AEE | 6M 2024 | 1,049 (first block) | 1,049M | blank | right |
| AXS | 6M 2026 | 1,150,940 | 1,150,940K | has 1,150,940K | right; not blank |
| CIK 1801368 | Q1 2020 | page unparsed by kit | held stub_column (durp 0.27) | - | hold kept (DATA-INFERRED) |
| CIK 1792044 | FY2019 | page unparsed by kit | held stub_column (durp 0.49) | - | hold kept (DATA-INFERRED) |

## Withheld cells (avoidable holds)
None found.

## False holds
None found.

## Findings for the builder
1. ROST prints two repurchase lines ("Treasury stock purchased" and "Repurchase of common stock"). The run has a `perimeter_multiple_repurchase_lines` hold, but these were summed and published: apply the hold when two `common` members both carry repurchase labels. Re-verify ROST FY2019, 9M 2015, 9M 2020.
2. "Repurchases of stock and other" (LDOS) must go to `buyback_combined_with_other_items`. Match "and other" in the member label.
3. A repurchase line printed without parentheses while its neighbours are (AAON Q1 2025) must go to `sign_unclear`.
4. "Treasury stock activity" (FIS) is ambiguous (net, or withholding included): hold it as perimeter or sign-unclear.
5. HEI-style "issued, repurchased and retired related to stock option exercises" belongs with the tax-withholding / option-exercise perimeter.
6. The blank lookup still misses matches exactly 10 days apart (DPZ, AXS): use <= 10 days inclusive, or match on the period id.

## Requests and disk
SEC requests: 113. DB: one connection for 15 blank re-checks.

## Untested scope
20 of 267 and 10 of 812 buybacks, 10 of 301 and 5 of 563 CFO, 2 of 75 stubs; agree cells not sampled.
