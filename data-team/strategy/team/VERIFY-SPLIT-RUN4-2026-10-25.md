# Verify: split re-base run 4 (2026-10-25/26)

Verifier 1. Branch work/period-engineer/split-rebase @ab19c54. Table: doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz (304,590 rows; upstream removed pre-2015 facts between runs). Seed random.Random(20261108), used in order for: 40 basis_review cells (frame 1,790), 30 restated_between_filings cells (frame 3,304), 40 unchanged DPS cells (frame 40,977). DB connections: 0. SEC: SEC_USER_AGENT, <= 4 req/s; downloads deleted as I went (disk was 3.4 GB at one point, then 11 GB).

Method:
- Each cell was compared with the tag/period facts in the first three 10-Q/10-K instances after the period end.
- Disputed cells were checked across every filing copy in SEC companyconcept, including the filing's own FY totals.
- Splits were checked through the dei share-count step, StockholdersEquityNoteStockSplitConversionRatio1, and EPS restatement chains.

## Verdict

**GATE FAILS: 4 shown values are wrong (all FILING-CHECKED), and 1 shown value sits on a different dividend basis from the rest of its company.** All four come from the new own-vintage dividend rule. A 10-Q's "declared" fact often carries the dividend declared after quarter end, or leaves out a special dividend. The filing's FY total does not add up with it.

| Cell | Shown | Right | Stored (today) | Evidence |
|---|---|---|---|---|
| COST Q2 FY2013 DPS (2012-11-26..2013-02-17) | 0.275 | 7.275 | 7.275, right | 10-Qs 0001193125-13-117085 and 0000909832-14-000008 say 0.275 and leave out the $7 special declared 2012-11-28. The FY2014 10-K 0000909832-14-000021 has Q2 = 7.275, and FY2013 = 8.17, which only adds up with 7.275 |
| OKE Q2 2014 DPS | 0.575 | 0.56 | 0.56, right | The own 10-Q 0001039684-14-000065 has 0.575 (the July declaration). The later 10-Q -15-000060 has 0.56, the 6M total is 0.96 = 0.40 + 0.56, and the FY declared total is 2.125 = 0.40 + 0.56 + 0.575 + 0.59 (0001039684-15-000017) |
| OKE Q3 2014 DPS | 0.59 | 0.575 | 0.575, right | Same pattern. 10-Q -15-000076 has 0.575; 9M total 1.535 |
| COP Q3 2021 DPS | 0.46 | 0.43 | 0.43, right | The own 10-Q 0001562762-21-000409 has 0.46 (the October declaration). FY 2021 declared is 1.75 = 0.43 x 3 + 0.46 in three 10-Ks (0001562762-22-000031 and others) |
| LMT Q3 2015 DPS | 1.50 | 1.65 on the basis LMT is shown on elsewhere | 1.50 | Basis inconsistent. LMT Q3 2019 is shown as 2.40 (declared in quarter; 2019 adds up as 2.2 + 4.4 + 2.4 + 0 = 9.0). On that same basis Q3 2015 is 1.65 (10-Q 0001193125-15-350723; FY 6.15). Either both cells use the declared-in-quarter basis or both use the paid basis |

Fix: an own-vintage dividend copy should stand only if the filing's own YTD and FY totals add up with it. If not, take the 10-K or later copy whose quarters add up to the FY total.

## (1) other_changed: 231 cells (168 since 2015), all checked

- **180 cells already judged in earlier rounds** with the same value: right.
- **51 new or changed cells:** 47 right, 4 wrong (above).
  - Right, among them:
    - NEE Q4 2020 0.35 (the later 0.385 is the 2021 rate).
    - LMT Q3 2019 2.40.
    - ABBV 2015 0.51 x3.
    - BNY 0.34 and 0.62.
    - MSI 0.79 and 0.88.
    - RSG Oct 2017 0.345; MCHP 0.346/2.
    - TEL in USD; PPL Q4 2024 0.2575.
    - CASY, JKHY, SANM, FLS and IONS: equal to the original filing.
    - DD H1 2018 1.14 x 9 = 10.26. The 2018 quarters are 0.38 + 0.76 (two declarations in Q2) + 0 + 0.38 = FY 1.52, so H1 equals 9M by coincidence.
    - HEI x125/64. Three 5:4 splits after 2016, FILING-CHECKED: FY2016 EPS is 2.33, then 1.86 (2017 10-K), then 1.19 (2018 10-K). The event list in the summary shows only two of them.
    - GSAT 2019 x15. The 2020 copy, -0.01, is next year's value at the same position.
    - RBA, SEIC, FRT, IDA (4 cells), ARE.
    - AAON Q3 2022 DPS 0, on a declared basis. The 6M declared total is 0.19, FY 0.43, and the payment fell in Q3.
- **The eight named cells are all shown with the values I verified in round 2:**
  - RSG Apr-2017 0.32
  - PPL 2017-11 0.395
  - OC 2019-09-30 0.22
  - NSC Q3 2019 0.94
  - OGE Q3 2020 0.4025
  - MORN Q3 2010 0.05
  - AMGN Q4 2023 2.25
  - PPL 2022-06 0.225, now from 0000922224-22-000049

## (2) Dominion

Q1 2024 basic and diluted EPS are held as restated_between_filings. Correct.

## (3) CBSH and VLY

- **CBSH:** 248 cells are held as basis_review_company_invariant and 0 are shown. The 15 cells I judged right last round (2026 filings) are now hidden too, so those 15 are false holds.
- **VLY:** 67 held as basis_review and 343 shown.
- **The VLY 2009-2011 shown cells:** 38 VLY cells ending before 2013 are shown, all sourced from filings dated after the May 2012 stock dividend (e.g. 0001193125-13-084204). They are right on today's basis.

## (4a) basis_review (1,790 cells): 40 sampled

- **11 false holds.** The stored value equals a filed current-basis copy:
  - QXO Q2 2023 0.52 (= 0.07 x 8)
  - MTCH 9M 2019 1.82, FY2019 2.15, FY2017 DPS 0
  - NLY Q3 2021 1.36 (= 0.34 x 4)
  - TRNO H1 2012 0 and Q1 2011 -0.14
  - SNDK shares 144,863,251 (from the 10-Q/A)
  - CYTK Q3 2012 -0.45 (filed after the 1:6 reverse split)
  - SYRE Q1 2024 0.72 (the 10-Q/A corrects -1.20)
  - SMMT shares (DATA-INFERRED)
- **25 justified holds.** No current-basis copy exists, or the history belongs to another entity:
  - MDGL x5: Synta's pre-merger history.
  - WULF x5: IKONICS's pre-2021 history.
  - TMUS 2008 and 2010: MetroPCS. TMUS Q1 2012: stored 0.06, while the current-basis copy is 0.37 (2014 10-K).
  - MTCH 2014 and 2018: old IAC-era basis.
  - SYRE shares x4: Aeglea, before the 1:25.
  - ET shares x2: before the 2014 and 2015 2:1 splits.
  - VLY: stock dividend.
  - CHTR 2012 x2: before the 0.9042 exchange ratio.
  - CVNA FY2021: see below.
- **4 unresolved:** FRHC shares x2, QXO 2010 (1/30 candidate), BKH shares (10-K 43,957,502 vs 10-Q 43,924,736).

**CVNA stored values are wrong today (FILING-CHECKED).** The May 2026 event is a 5-for-1 forward split. Q2 2025 weighted basic shares are 677,070,000 in 0001690820-26-000055, about 5x the roughly 136M Class A shares; the ratio fact 0.2 is old shares per new share. Stored FY2021 basic EPS is -8.15 = -1.63 x 5. The right value is -1.63/5 = -0.326. The stored pre-2026 CVNA per-share values were multiplied instead of divided. They are hidden in the dry-run but shown today.

## (4b) restated_between_filings (3,304 cells): 30 sampled

- **13 false holds:**
  - FNB Q4 2016 0.12
  - WAL Q2 2013 0
  - EWBC Q1 2010 0.01
  - MSM 0.75
  - MS H1 2012 0.10 and Q2 2010 0.05
  - AM 0.3075
  - NEM Q2 2009 0.10
  - HAS 2017-04-24 shares (original cover page)
  - RGA FY2011 7.37 (the latest two copies agree)
  - LGND Q3 2015 10.01 (the latest three agree)
  - ASTS 0.16 (10-K/A)
  - EQH H1 2019 -0.82 (DATA-INFERRED)

  The first 8 (from FNB to NEM; MS counts twice) have only one value across their copies, so the restated hold looks like a bug, probably triggered by the other dividend tag.
- **15 justified two-vintage disagreements:** THC, THG, CVS, AMAT, MKL, BIO, AIZ, IBRX, COLB, ECHO, DAL, EPD, COP 2009, NTRA FY2016, ADP.
- **1 stored wrong but recoverable:** GPN, stored 0.01; the 2010 copy is 0.02.
- **1 unresolved:** SUI (no copies on these tags).

## (5) unchanged DPS cells: 40 sampled for PPL-type repeats

0 of 40. In 36 cells all copies agree with the shown value, or a later majority corrects an own-filing error: SBUX FY2017's own 10-K says 0, two later 10-Ks say 1.05, and 1.05 is shown, which is right. TSCO Q4 2015 0.20/5 = 0.04 is right. The other 4 (AXS, AMKR, KNX, BG) had no copy on these tags; their values are plausible (DATA-INFERRED).

## (6) Released cells

| Cell | Status | Verdict |
|---|---|---|
| LEA 9M 2014 DPS 0.60 | shown | Right (0.20 x 3) |
| HEI Q2 FY23 0.76 / 0.77 | shown | Right |
| SSNC Q4 2023 0.24 and Q4 2024 0.25 DPS | **still hidden** (dividend_basis_pending) | Still false holds |
| HST 2009-12-31 DPS 0.25 | **still hidden** (dividend_basis_pending) | Still a false hold (DATA-INFERRED) |

## (7) GL and PRAX

- **GL: both 3:2 splits are real (FILING-CHECKED).**
  - dei shares went from 76,056,097 (2011-04-27) to 105,084,520 (2011-07-25), and from 87,811,120 (2014-04-28) to 130,589,470 (2014-07-28).
  - The ratio fact is 1.5 at 2014-06/07.
  - EPS was restated: FY2010 6.30, then 4.20; FY2013 5.68, then 3.79.
  - All 467 GL cells are hidden by the company invariant. The right values are computable, so these are false holds (DATA-INFERRED per cell).
- **PRAX: the 1-for-15 is real (FILING-CHECKED).** dei shares went from 128,550,152 (2023-11-03) to 13,238,349 (2024-03-01), with ratio fact 0.0667.
  - 66 basis_conflict cells and 13 basis_review cells are hidden.
  - Pre-split share counts are stored unadjusted, so they are wrong today; the right value is the count / 15.
  - Several stored EPS values are already x15 (e.g. FY2020 -117.84 vs filed -7.86).
  - These are recoverable false holds.

## Not tested

- The fixed classes and new (1,028).
- dividend_basis_pending (4,132), basis_conflict (1,780) and the invariant classes beyond GL, CBSH and PRAX.

## Next action (Period Engineer)

1. Own-vintage dividend: keep it only if the filing's YTD and FY totals add up with it. Otherwise use the 10-K or later copy whose quarters add up to the FY total. This fixes COST, OKE x2 and COP.
2. Pick one dividend basis per company (LMT).
3. Fix the CVNA direction: the 2026 event is 5-for-1 forward, so stored EPS must be divided.
4. Release:
   - the single-value restated holds;
   - GL (both splits confirmed);
   - PRAX (re-base x15 / ÷15);
   - the CBSH 2026-basis cells;
   - SSNC and HST.
