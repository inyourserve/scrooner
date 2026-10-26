# Verify: BS batch 6 (origin/work/scrooner-25/slot-records fd9b6be), 2026-10-26

Verifier 2. Manifest results/bs_batch6_verifier_manifest.json (457 instants at 28 companies: first, last and every era boundary, plus own-cal instants) and all 28 withheld cells from bs_replay_batch6_report.json. Each instant checked on the balance-sheet R page of its own accession (463 pages, deleted after use). FILING-CHECKED unless marked.

## Result: no wrong value published. 436 of 436 published instants equal the face. 25 of the 28 withheld cells have a right total-liabilities value on the face; withholding blanks it (no wrong number shown, but coverage is lost and the reasons point at fixable defects).

## 1. Published instants (436)
- 402 read automatically: the printed "Total liabilities", or L&E total minus total equity (including NCI) minus mezzanine, in the cell's own date column. Every one is equal within the filer's rounding unit.
- 34 read by hand where my parser failed, all equal:
  - XEL 2018-12-31: 45,987 - 12,222 = 33,765.
  - HRL "shareholders' investment" faces.
  - TYL 2015-2020 ("Liabilities and Shareholders' equity, Total").
  - Bio-Techne 2015 (unlabelled L&E row).
  - IDACORP 2020-2025: combined filing, the IDACORP block, not the Idaho Power block: 6,609,950 - 2,473,271 = 4,136,679.
  - LDOS 2016-12-30: 9,132 - total equity 3,147 = 5,985.
  - Tradeweb 2019-12-31: printed 502,589.
- Own-cal instants (1-19 per company) and boundary instants: all in the 436, all equal.

## 2. The 28 withheld cells
| CIK | Instant | Face | Verdict |
|---|---|---|---|
| 48465 (HRL) | 2025-07-27 | lines sum 5,403,632; L&E - equity 5,403,634 | right value withheld: a 2K gap from the filer's own rounding, against a 1K tolerance |
| 721371 (CAH) | 2015-09-30 | lines 24,576.0; identity 24,575.6 (redeemable NCI 119.4 printed to 0.1M) | right value withheld: rounding |
| 102729 (VMI) | 2015-03-28, 2015-06-27 | "Deferred income taxes" 66,329 is a liability line; the member sum uses -66,329 (DeferredTaxAssetsLiabilitiesNetNoncurrent sign) | right value withheld (1,440,266 / 1,426,799) |
| 775158 (OSK) | 2021-12-31 | member sum omits "Long-term customer advances" 207.0 | right value withheld (3,645.4) |
| 860731 (TYL) | 2019-12-31 | member sum omits "Deferred income taxes" 48,442 | right value withheld (574,556) |
| 1336920 (LDOS) | 2016-01-01 | member sum omits "Deferred tax liabilities" 34 | right value withheld (2,302) |
| 885725 (BSX) | 2021-12-31 | member sum counts the EQUITY line "AOCI, Cash Flow Hedge" 206 as a liability | right value withheld (15,607; face lines 15,608) |
| 851968 (MHK) | 2016-10-01 | printed "Total liabilities" 4,723,164; member sum is current liabilities only | right printed value withheld |
| 1090425 (LAMR) | 2016-09-30 | printed "Total liabilities" 2,846,214; members are current liabilities + a deferred-tax ASSET | right printed value withheld |
| 936340 (DTE) | 13 instants 2015-09-30 .. 2019-09-30 | printed subtotals: current + "Total Long-Term Debt" + "Total Noncurrent/Other Liabilities" (2015-09: 2,273 + 8,856 + 8,692 = 19,821 = identity) | right value withheld: the member sum adds children (deferred taxes, decommissioning, other, capital leases) beside their printed parent |
| 1637459 (KHC) | 2015-06-28 | current 2,653 + "Total long-term liabilities" 18,108 = 20,761 = the member sum | right value withheld: the member sum is right and the identity is wrong. The identity misses the "9% Series A cumulative redeemable preferred stock" 8,320 shown between liabilities and equity (mezzanine) |
| 1057877 (IDACORP) | 2023-12-31 | L&E 8,475,918 - total equity 2,914,743 = 5,561,175; member sum 2,785,385 (current + other liabilities only). The R page shows no long-term debt row and no NCI row | right value withheld (5,561,175, matching earlier years' method); member sum wrong |
| 833444 (JCI) | 2017-03-31 | printed "Current liabilities" 10,742 + "Long-term liabilities" 18,496 = 29,238; L&E - equity 29,406. The R page does not foot by 168 (probably redeemable NCI, not shown; DATA-INFERRED) | probably right (29,238) but ambiguous: withholding acceptable |
| 88941 | 2019-10-27 | lines 350,167; L&E - equity 350,418; the R page does not foot by 251 | truly ambiguous: withholding right |
| 842023 (Bio-Techne) | 2016-09-30 | lines 622,082; L&E - equity 622,109; does not foot by 27 | truly ambiguous: withholding right |

Truly not publishable from the face: 2 (88941, 842023), plus JCI arguably. The other 25 are coverage losses with these causes:
- The tolerance is one unit. It needs to allow the filer's footing rounding (about one unit per summed member).
- The member set includes children beside their parent (DTE), an equity line (BSX) and a deferred-tax asset (LAMR).
- Asset-named deferred-tax tags take the asset sign (VMI).
- Lines are missing from the cal (OSK, TYL, LDOS).
- The printed total is not used (MHK, LAMR).
- The mezzanine misses redeemable preferred (KHC).

Not tested: the 174 cells that need the instance reader, and the tie instants outside the manifest.
