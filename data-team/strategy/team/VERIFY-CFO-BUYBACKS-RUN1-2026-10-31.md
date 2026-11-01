# Verify: CFO and buybacks replay run 1 (work/cashflow/cfo-buybacks 2977e0a, results/cf_run1), 2026-10-31

Seed 20261031. Files: cfo_prod_differs.json (268), buybacks_prod_differs.json (1,113), cfo_cells.jsonl.gz, buybacks_cells.jsonl.gz. Claimed: CFO 34,877 publishable (29,098 agree, 5,511 production blank, 268 differ); buybacks 23,243 publishable (16,831 agree, 5,299 blank, 1,113 differ). Evidence class: FILING-CHECKED (the claimed accession's cash-flow R page, by date and duration). Verifier 2 (scrooner-bc).

## Result
- **CFO: NO as packaged; YES once one class is fixed.** 19 of 20 graded cells right, 1 wrong. 15 of 15 differences: the slot equals the printed operating-activities total and production is wrong against the same filing; 3 of them differ only by rounding. New values: 4 of 5 right. Valaris 0000314808-21-000102 shows -19.0M as a 6-month cell, but the face prints it as the 5-month successor period (May-Sep 2021, fresh start). No 6-month column exists.
- **Buybacks: NO.** 9 of 30 right, 16 wrong, 5 perimeter questions. Systemic: inflow lines are summed as repurchases, and signed net lines keep the filer's sign.
- **The production-blank counts look inflated.** In 400 seeded publishable cells per family, production "blank" by exact end date: CFO 68, buybacks 100. Within +-10 days (52/53-week filers, whose real end is e.g. 2024-03-29 while the cell file says 2024-03-31): CFO 5, buybacks 31. If the 5,511 / 5,299 counts used exact dates, most of those are not new values. My first blank draw hit this; I redrew with the tolerance, which left only 5 truly blank CFO cells to grade (the brief asked 10).

## Method
Slot value vs the printed line(s) of the claimed filing's cash-flow statement, column by end date (+-10 days) and duration. For buybacks, every slot member was checked against the face line it came from, including its direction (outflow or inflow). Production values: the run's differs files; for blanks, analytics.canonical_fact (cfo, cfo_resolved, share_buybacks, share_buybacks_resolved) at a matching end date and duration.

## Sample
CFO differences: WTRG FY2023 plus 14 stratified by size of difference (big / mid / small / rounding). Buyback differences: UBER FY2017 and EMR FY2024 plus 18, at most 3 pure rounding. Blanks: first cells in seeded order with no production value within +-10 days.

## Cell table: CFO differences (slot = face in all 15)
| Ticker | Period | Face (slot) | Production | Note |
|---|---|---|---|---|
| WTRG | FY2023 | 933,587K | 1,874M | production wrong |
| LNG | Q1 2016 | -88,690K | -131M | production wrong |
| MSCI | FY2015 | 305,994K | 321,247K | production wrong (hand-read, kit parsed no columns) |
| DVN | Q3 2016 | 726M | 727M | production wrong; one later copy agrees with face |
| CBOE | FY2016 | 229,563K | 229.6M | rounding (hand-read) |
| SYM | Q1 FY2022 (to 2021-12-25) | 40,000K | -1,894,368 | production wrong |
| HLT | FY2017 | 924M incl. discontinued | 849M | production is continuing-only; wrong per spec (total first) |
| CAT | Q1 2016 | 489M | 490M | production wrong |
| BE | 9M 2020 | -79,990K | -79,989K | rounding |
| LEN | 6M 2018 | 34,397K (consolidated, first block) | 19,514K | production wrong |
| PNFP | FY2025 | 759,008K | 676,074K | production wrong |
| URI | Q1 2017 | 623M | 622M | production wrong |
| NBIX | 9M 2019 | 49,501K | 49,500K | rounding |
| GM | Q1 2016 | -164M | -108M | production wrong (no later disagreeing copy in run) |
| BKH | 6M 2016 | 222,775K | 183,503K | production wrong |

## Cell table: CFO new values (production blank within +-10 days)
| CIK | Period | Face | Slot | Verdict |
|---|---|---|---|---|
| 314808 (Valaris) | "6M" to 2021-09-30 | -19.0M is the 5-month successor column | -19.0M as 6M | **wrong period** |
| 909832 (Costco) | 36 weeks to 2019-05-12 | 4,063M | 4,063M (labelled 9M, end 2019-04-30) | right value (YTD label) |
| 65984 (ETR) | FY2015 | 3,291,184K (Entergy Corp block) | same | right |
| 1002910 (AEE) | Q1 2021 | -35M | -35M | right |
| 1002910 (AEE) | 9M 2021 | 1,192M | 1,192M | right |

## Cell table: buyback differences
| Ticker | Period | Face lines | Slot | Production | Verdict |
|---|---|---|---|---|---|
| EMR | FY2024 | Purchases of common stock (435); AspenTech purchases (208) | 643M | 435M | perimeter: subsidiary's own buyback added |
| UBER | FY2017 | Repurchase of outstanding shares (131); option proceeds net +3 | 134M | 32M | slot wrong (inflow added); production also wrong (face 131) |
| CVX | 6M 2019 | Net sales (purchases) of treasury shares (840) | -840M | 1,539M | slot wrong (net line, sign kept) |
| MRSH | 9M 2017 | Purchase of treasury shares (600); issuance from treasury +134 | 734M | 600M | slot wrong (inflow added) |
| DECK | 9M 2025 | Repurchases (813,488); excise tax (5,042) | 818,530K | 813,488K | perimeter: excise tax |
| REG | Q1 2017 | Repurchase (18,275); sale of treasury +76 | 18,351K | 18,275K | slot wrong (inflow added) |
| KMI | Q1 2018 | Repurchases of shares (250) | -250M | 250M | slot wrong (sign) |
| ADBE | 9M 2018 | Treasury purchases (1,750,000); reissuance proceeds +189,743 | 1,939,743K | 1,750,000K | slot wrong (inflow added) |
| CAT | 6M 2024 | Purchase (6,275); stock issued +8 | 6,283M | 6,275M | slot wrong (inflow added) |
| REG | 9M 2019 | Program repurchases (32,777); treasury sale +9 | 32,786K | 32,777K | slot wrong (inflow added) |
| CVX | FY2021 | Net sales (purchases) of treasury shares +38 | 38M | 1,383M | slot wrong (a net sale shown as a buyback) |
| SNX | FY2025 | Repurchases (596,109); issuance proceeds +33,621 | 629,730K | 596,109K | slot wrong (inflow added) |
| ZETA | 6M 2025 | Repurchase of shares (57,931) | 57,931K | 57,059K | slot right, production wrong |
| G | 6M 2020 | Stock repurchased and retired (45,021) | 45,021K | 45,000K | slot right (rounding) |
| CLS | FY2025 | Repurchase for cancellation (153.4); treasury for SBC plans (221.6) | 375.0M | 153.4M | perimeter: SBC-plan purchases |
| SGI | Q1 2022 | Treasury stock repurchased (494.8) | 494.8M | 449.2M | slot right, production wrong (transposed digits) |
| VLO | FY2025 | Purchases (2,598); excise tax (28) | 2,626M | 2,598M | perimeter: excise tax |
| JCI (Tyco) | FY2015 (to 2015-09-25) | Repurchase of ordinary shares (417) | 417M | 1,362M | slot right, production wrong |
| FICO | FY2016 | Repurchases (138,399); treasury issuance proceeds +17,828 | 156,227K | 138,399K | slot wrong (inflow added) |
| FICO | FY2022 | Repurchases (1,104,180); proceeds +16,026 | 1,120,206K | 1,104,180K | slot wrong (inflow added) |

## Cell table: buyback new values (production blank within +-10 days)
| CIK | Period | Face | Slot | Verdict |
|---|---|---|---|---|
| 89800 (SHW) | 9M 2025 | Treasury stock purchased (1,538.4) | 1,538.4M | right |
| 80661 (PGR) | FY2017 | Treasury for RS tax liabilities (57.6); open market (4.9) | 62.5M | perimeter: tax-withholding shares counted |
| 1121788 | Q1 2018 | Treasury issuance proceeds +1,926; purchase for equity awards (6,562) | 8,488K | wrong (inflow added) |
| 66570 | 9M 2016 | Company stock purchases (1,881) | 1,881K | right |
| 65984 (ETR) | 9M 2022 | Proceeds from sale of treasury stock +31,802 | 31,802K | wrong (inflow as buyback) |
| 315852 | FY2024 | Treasury stock purchases (65,260,000 whole $) | 65,260,000 | right |
| 89800 (SHW) | Q1 2016 | Treasury stock purchased 0 | 0 | right |
| 66570 | FY2022 | Company stock purchases (34,394) | 34,394K | right |
| 882835 | 9M 2020 | Treasury stock sales +7.3 | 7.3M | wrong (inflow as buyback) |
| 1618732 | 6M to 2020-01-31 | Proceeds from employee plan share sales +26,486 | 26,486K | wrong (inflow as buyback) |

## Withheld cells (avoidable holds)
Not in scope.

## False holds
None examined.

## Findings for the builder
1. **Buybacks: classify members by cash direction, not by vocabulary.** Exclude every inflow line (Proceeds*, ProceedsFromSaleOfTreasuryStock, ProceedsFromStockOptionsExercised, ProceedsFromIssuanceOrSaleOfEquity, employee plan sales, "Treasury stock sales", IncreaseDecreaseInOutstandingChecks used for issuance). For a net line (ProceedsFromRepurchaseOfEquity, "Net sales (purchases) of treasury shares"), show a buyback only when the net is an outflow, as a positive number, and label it net; a net inflow is not a buyback (CVX FY2021). Re-verify: CVX, KMI, ADBE, CAT, REG, FICO, SNX, MRSH, UBER, 1121788, ETR 2022, 882835, 1618732.
2. **Buyback perimeter needs a founder or Standardization call** before release: subsidiary's own repurchases (EMR/AspenTech), excise tax on repurchases (DECK, VLO), SBC-plan treasury purchases (CLS), treasury acquired for restricted-stock tax liabilities (PGR). Production's definition is "repurchases of common stock".
3. **CFO: take the duration from the column dates, not FSN quarters.** Valaris's 5-month successor stub (fresh start) became a 6-month cell. Hold predecessor/successor stub columns.
4. **Recount "production blank" with a +-10-day end-date match** (52/53-week filers). 63 of 68 CFO and 69 of 100 buyback exact-date blanks in my 400-cell samples have a production value within 10 days.
5. Kit note: v3.3/v3.6-era R pages (MSCI 2016, CBOE 2017) parse to zero columns in filing_kit; they were read by hand.

## Requests and disk
SEC requests: about 158. Scratch holds only re-derivable draw files. Two DB reads (single connection, 60s timeout).

## Untested scope
Sampled 20 of 268 CFO and 20 of 1,113 buyback differences, 5 + 10 blanks. "Agree" cells (29,098 / 16,831) were not sampled: an agreeing buyback can still carry an inflow member that happens to be 0. Later-copy disagreement handling was not tested.
