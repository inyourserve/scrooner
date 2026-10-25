# Verify: split re-base rerun, other_changed class (2026-10-25)

Verifier 1. Branch work/period-engineer/split-rebase @09b0841, dry-run table doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz (340,719 rows; class other_changed = 178, 127 ending 2015-01-01 or later). Read-only; no DB queries. SEC: SEC_USER_AGENT, <= 4 req/s; downloads deleted.

## Verdict

**GATE FAILS: 15 of 178 shown cells are wrong. 9 of them end in 2015 or later. All 15 are FILING-CHECKED.** The previous round's 14 wrong cells: 12 are fixed (OHI, BWA, TRMB, DCI EPS, XYL x2, OGE, GLPI x3, WTRG x2). TSCO and TEX are still wrong.

**Method.** I checked all 178 cells, so no seeded sample was needed. For each cell I read the filings' XBRL facts for that tag and period: the first three 10-Q/10-K instances after the period end. For every disputed cell I also read SEC companyconcept, which lists that tag's facts across all filings with their accessions. I did not open R pages, except an attempt for PPL; its instance file is "File Unavailable" at SEC, so I used companyconcept.

## Wrong shown values

| Cell | New | Right | Today's stored value | Evidence |
|---|---|---|---|---|
| TEX Q2 2020 DPS | 0.12 | 0 | 0, right | FY2021 and FY2022 10-Ks file Apr-Jun 2020 = 0 (0000097216-22-000013, -23-000012). The 0.12 in 0000097216-20-000259 is Q1's rate (dividend suspended) |
| TSCO 2023-02-08 DPS | 0.22 | 1.03/5 = 0.206 | 1.03, wrong (unadjusted) | 0000916365-25-000089 puts the 2024 rate on the 2023 date. 1.03 appears in 3 own filings |
| PPL 2013-11 DPS | 0.36 | 0.3675 | 0.3675, right | The FY2012 10-K 0000922224-13-000025 files 0.36 on a 2013-11 context, a date in the future at filing time. FY2013 10-K 0000922224-14-000024 has 0.3675 (per-annum 1.47) |
| OC 2020-03-31 DPS | 0.22 | 0.24 | 0.24, right | Q1 2020 10-Q 0001370946-20-000032 has 0.22 at 2020-03-31 and 0.24 at 2018-03-31 (swapped). Later filings -20-000042 and -20-000054 have 0.24 |
| AMGN Q4 2025 DPS | 2.38 | 2.52 | 2.52, right | FY2025 10-K 0000318154-26-000010: Q4 2.38, but the same filing has December 2025 = 2.52 and FY 9.66 = 2.38x3 + 2.52. 10-Qs -26-000057 and -26-000126 file Q4 = 2.52. The same 10-K also re-files Q4 2023 as 2.13 against 2.25 in three other filings |
| DCI Q4 FY2015 DPS | 0.34 | 0.175 | 0.175, right | Original 10-K 0000897101-15-001507 declares 0.34. Later 10-Ks 0001628280-16-019746 and 0000029644-17-000019 file 0.175, and FY declared 0.67 = 0.165x3 + 0.175 |
| COO Q1 FY2020 DPS | 0 | 0.03/4 = 0.0075 | 0.03, wrong (unadjusted for the 2024 4:1 split) | Only 0000711404-20-000021 files 0. Five later filings file 0.03 (-20-000032, -21-000008, -21-000016, -21-000025, 10-K -21-000038). The filer's own convention puts the semiannual dividend in Q1 (Q1 FY2019 = 0.03 too) even though payment is in February |
| CBSH Q2 2018 diluted / basic, Q3 2018 diluted EPS (3 cells) | 1.01 / 1.02 / 1.03 | Lower: on today's share basis after the annual 5% stock dividends | 0.96 / 0.96 / 0.98, also wrong (partly adjusted) | The originals (0000022356-18-000042, -18-000050) are restated in 2019 10-Qs to 0.96 / 0.96 / 0.98 (0000022356-19-000034, -19-000043). The 5% stock dividends are not in the split table, and 258 other CBSH cells are hidden as restated_between_filings |
| VLY DPS: FY2009, 6M/9M/FY2010, 9M 2011 (5 cells) | 0.72, 0.36, 0.54, 0.72, 0.52 | Lower: on today's share basis after the 5% stock dividends | 0.69, 0.34, 0.52, 0.69, 0.49, also wrong (partly adjusted) | Restated in each later filing: FY2010 0.72 (0001193125-11-050288), then 0.69 (-12-085595), then 0.66 (-13-084204); Q3 2011 0.17, then 0.16 |

CBSH and VLY share one cause. A 5% stock dividend restates every earlier per-share value in later filings, but it is not a row in the split table. Picking the original filing then shows a value on an old share basis. The fix needs to do one of two things: treat recurring stock dividends as split events, or hold every per-share cell for these companies until they are re-based.

## The four cells that stay other_changed

| Cell | Stored value right? | New value right? | Basis |
|---|---|---|---|
| COO Q1 FY2020 DPS | No: 0.03 is unadjusted; right is 0.0075 | No: 0 | FILING-CHECKED, above |
| DCI Q4 FY2015 DPS | Yes: 0.175 | No: 0.34 | FILING-CHECKED, above |
| TEX Q2 2020 DPS | Yes: 0 | No: 0.12 | FILING-CHECKED, above |
| HSIC Q2 2019 basic EPS | No: 0.79 | Yes: 0.77 | FILING-CHECKED. The 10-Q 0001000228-19-000048 has total 0.77, continuing 0.79, discontinued -0.01. The 10-Ks (0001000228-20-000018, -21-000019) put the continuing-ops figure under EarningsPerShareBasic for both quarters. Q1 2019 is the same: total 0.73, continuing 0.79 |

## Right (163 cells)

- **Agrees with the original filing (78 cells), including:**
  - RSG April 2017 0.32 (a later copy has 0.345).
  - MSI Q3 2011 0.22 declared.
  - OC 2019-09-30 0.22.
  - EMN 2010 (originals / 2 at the 2011 2:1 split).
  - HSIC Q1 2019 0.73 total.
  - ESE and NEM: the new value is total EPS; the other copy is continuing ops.
  - TKO 2023-09-12..30 -0.26. The FY2023 10-K's -0.43 belongs to Sep 12-Dec 31, and the Q1 2024 10-Q's -1.26 equals Q1 2024. Both are label errors. Stored -1.26 is wrong.
  - AMGN Q4 2023 2.25. Stored 2.13 is wrong.
  - MORN Q3 2010 0.05.
  - PPL 2017-11 0.395 and 2022-06 0.225.
- **CB and LOGI (CHF and USD copies of the same fact):** the new code picks the USD fact.
- **No earlier copy in these tags (FILING-CHECKED against the chosen filing):**
  - IPO and merger-ratio companies (RVMD, VG, PACS, AXSM, KNSA, JXN).
  - RGA 2009-11 DAC recast.
  - KNX, BX, and the CB year/9M cells.

## The false holds reported as released

All of these are now shown and right:
- TOL Q2 FY21 0.17.
- C Q1 2012 0.01.
- BPOP Q4 2016 0.15.
- CPRT Q2 FY24 0.33.
- AAON FY2014 0.80/1.5.
- EXEL 129,685,614.
- SNEX 2026-08-04 120,616,735 (filed after the split).
- CF 2007 0.08/5.
- BRO Q3 2013 0.39/2.
- SAIA 15,937,821 x 3/2 = 23,906,732. The 3:2 split is FILING-CHECKED: dei shares went from 16,186,591 (2013-04-29) to 24,422,744 (2013-07-31).
- EOG 6M 2009 basic 0.57/2 = 0.285. The 0.57 was filed in 2009 and 2010 (0000821189-09-000047, -10-000037), before the 2014 2:1 split. **Correction to my 2026-10-24 report:** there I called stored 0.57 a likely false hold (DATA-INFERRED). It is unadjusted; the new 0.285 is right.

**Still hidden, so still false holds:**
- HEI Q2 FY23 0.76 (0000046619-23-000083), basis_review_company_invariant.
- LEA 9M 2014 0.60, restated_between_filings.
- PRAX 2021-12-31 and its other pre-split share cells, now basis_conflict. The 1-for-15 split is real (SEC ratio fact 0.0667).
- HOMB, ANF, CELH (DATA-INFERRED).
- SSNC and HST quarter-equals-year (DATA-INFERRED).

## Untested

- Cells outside other_changed in this rerun (the 6,831 / 1,435 / 6,738 fixed classes, 877 new, 2,851 rounding_only).
- The CBSH (101 unchanged) and VLY (390 unchanged) shown cells, which probably have the same stock-dividend basis problem. This is DATA-INFERRED: the CBSH and VLY restatements are FILING-CHECKED, but I did not open those unchanged cells.

## Next action (Period Engineer)

1. Treat recurring stock dividends (CBSH, VLY, and any company filing the same restatement) as split events, or hold every per-share cell for those companies.
2. When copies disagree, never let a lone outlier win over a majority of later copies. This covers COO, AMGN, DCI, TEX and OC.
3. Reject a context dated after its filing date (PPL).
4. TSCO: the instant 2023-02-08 should come from the 2023 filings with factor 5.
5. Re-run, and send me the other_changed class plus 30 unchanged cells for CBSH and VLY.
