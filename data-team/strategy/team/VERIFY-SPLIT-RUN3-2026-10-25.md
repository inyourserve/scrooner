# Verify: split re-base run 3 (2026-10-25)

Verifier 1. Branch work/period-engineer/split-rebase @cf379fa. Table: doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz (340,719 rows). DB connections used: 0. SEC access used SEC_USER_AGENT at 4 req/s or less; downloads deleted.

Method:
- Each cell's tag and period were read from the XBRL instance of the first three 10-Q/10-K filings after the period.
- Disputed cells were also read across every filing through SEC companyconcept.
- Split facts were checked with dei share-count steps and StockholdersEquityNoteStockSplitConversionRatio1.

## Verdict

**GATE FAILS.**
- **1 shown value is wrong (FILING-CHECKED):** PPL 2022-06 DPS.
- **2 shown values are not supported:** Dominion Q1 2024 basic and diluted EPS. The latest filing contradicts them.
- **All 15 cells I reported wrong in the previous round are now right or held.**
- **False holds are large.** 29 of the 40 sampled "unconfirmed split / stock dividend" cells hide a correct value. Extrapolated, that is about 7,000 of the 9,824 cells in that class.

## 1. other_changed (182 cells, 132 since 2015): all checked

- **146 cells** were in the class in run 2 with the same new value, and I judged them right then.
- **36 cells are new to the class.** Results:

| Cell | New | Verdict |
|---|---|---|
| D Q1 2024 basic and diluted EPS | 0.50 | **NOT SUPPORTED.** The copies say 0.78 (10-Q 0000950170-24-051708), then 0.50 (10-K 0000950170-25-028387 and 10-Q -25-061558), then 0.46 (10-K 0001193125-26-063120). NetIncomeLoss is restated with them: 674M, then 441M, then 403M. The majority rule picked 0.50 over the latest restatement. Hold the cell, or take the latest restatement once the cause is confirmed |
| ALV Q2 2017 basic EPS | 1.47 | Unresolved, minor. The originals say 1.48 (0001564590-17-013770, -18-002787). One 2018 10-Q says 1.47 and the FY2018 10-K says 1.54. No later majority exists, so this should have stayed with the original |
| NTRA Q2 2017 EPS -0.55; LMT FY2017 6.75/6.82; WPC Q2 2011 1.99/2.02; EHC FY2011 1.91; FRHC FY2022 3.84; ANF Q1 FY2012 -0.25; LNC FY2022 7.78/7.93 and Q3 2012 1.51/1.54; TAP Q1 2016 0.80; SWK basic Q2 2017 1.86; PNR FY2011 -0.08 | as listed | Right on the latest restated basis. Two or more later copies agree, and NI is restated with EPS where I checked: PNR FY2013 10-K 0000077360-14-000010 has NI -7.5M; LNC's restatement is the LDTI one. The reasons for the restatements are DATA-INFERRED |
| AES Q2 2021 DPS | 0 | Right on a declared basis. FY declared 0.6095 = 0.15 + 0 + 0.15 + 0.31 in 0000874761-22-000022 and -23-000010 |
| MCO FY2012 DPS 0.68; RBC FY2020; TSN Q1 FY2019; SWK 2018-2019 (4 cells); BWA FY2015; BKH 2013; LGND 2012 | | Right: equal to the original filing |

## 2. My 15 wrong cells from round 2

All are now right or held:
- **Now shown and right (all FILING-CHECKED in round 2):**
  - TEX Q2 2020 DPS 0
  - COO Q1 FY2020 DPS 0.0075
  - DCI Q4 FY2015 DPS 0.175
  - OC 2020-03-31 DPS 0.24
  - AMGN Q4 2025 DPS 2.52
  - PPL 2013-11 DPS 0.3675
  - TSCO 2023-02-08 DPS 0.206
- **Now held as basis_review:** CBSH (3 cells) and VLY (5 cells).

The 17 other cells that left other_changed:
- **Shown and right:** LMT Q3 2015 DPS 1.50. The 10-K basis: FY declared 6.15 = 1.50x3 + 1.65; the 10-Qs say 1.65; this is DATA-INFERRED.
- **Shown and WRONG:** PPL 2022-06 DPS 0.24. The originals (0000922224-22-000042, -22-000049) say 0.225, and H1 2022 is 0.425 = 0.20 + 0.225. Three 2023 10-Qs (-23-000031, -000045, -000049) put the 2023 rate on the 2022 comparative, so the "majority of later copies" rule picked the repeated label error. Today's stored value is also 0.24, so this cell is in class `unchanged` and is a wrong value both today and after the run.
- **Held, but correct values exist (false holds).** These are the run-2 values I verified:
  - MSI Q3 2011 0.22
  - NSC Q3 2019 0.94
  - RSG April 2017 0.32
  - AMGN Q4 2023 2.25
  - PPL 2017-11 0.395
  - OGE Q3 2020 0.4025
  - OC 2019-09-30 0.22
  - MORN Q3 2010 0.05
  - SCI 2011 0.20 (now held as dividend_per_share_invalid)
  - CASY Q4 FY2013 0.60/0.61
  - ESE 9M FY2015 1.18 and 6M 0.73
  - CB Q1 2010 and Q1 2011 (basis_review; CB's CHF/USD copies, not a stock dividend)

## 3. CBSH and VLY: 30 cells (random.Random(20261101); 15 shown, 15 held)

The stock-dividend dates are FILING-CHECKED from dei share steps:
- CBSH: about 5% every December, 2010 through 2025.
- VLY: about 5% in May 2011 and May 2012. Later steps are acquisitions.

- **Shown, 15 of 15 right.** The sample drew only VLY cells: CBSH has only 15 shown cells in total and none came up in the seeded draw. All 15 VLY cells come from filings after May 2012, so they are on today's basis. I separately listed all 15 CBSH shown cells: all come from filings after the December 2025 stock dividend, so they are on today's basis (FY2025 EPS 4.04 in 0000022356-26-000069, and the 2026 quarters).
- **The 4 VLY 2009-2011 cells still shown** (2010 and 2011 annual and quarterly cells sourced from the FY2012 10-K 0001193125-13-084204, e.g. 2010 DPS 0.66): right, because that filing post-dates the last stock dividend.
- **Held, 15 of 15 justified.** Their stored values are on a pre-stock-dividend basis. A true value needs re-basing, which is not built yet. This is not a false hold.

## 4. Released and shown cells

| Cell | Status | Verdict |
|---|---|---|
| BWA FY2019 DPS 0.68 | shown | Right |
| HOMB Q2 2011 0.1125 (0.45/4) | shown | Right |
| ANF Q3 FY2009 0.44 | shown | Right (equals the original) |
| CELH 2026-02-23 shares 256,975,993 | shown | Right |
| SSNC Q4 2023 0.24 and Q4 2024 0.25; HST 2009-12-31 0.25 | **still hidden** (quarter_equals_year_label_error) | Contradicts the summary's claim that they were released. They remain false holds (DATA-INFERRED) |
| HEI Q2 FY23 0.76; LEA 9M 2014 0.60; PRAX share cells | still held | Still false holds |

## 5. Hidden "unconfirmed split / stock dividend" (basis_review, 9,824 cells): 40 sampled (random.Random(20261101))

- **29 false holds.** The stored value is right and there is no split after the source filing.
  - 17 are FILING-CHECKED (the stored value equals the original filing value):
    - EQIX shares 2011 and 2013
    - IRM Q4 2013 0.25
    - BAC 2015-07-23 DPS 0.05 and Q1 2010 EPS 0.28
    - CNH shares 2022
    - BAH 0.31
    - PFG 0.52
    - PAYX 0.52 and DPS 0.66
    - BIO 1.41
    - CCI 0.33 and shares 2014
    - ZBRA 1.78
    - GSAT Q3 2011 0
    - CELH Q3 2016 0
    - IONS -0.27
  - 12 are DATA-INFERRED (no earlier copy found): AKAM, IRM, NRG, FLR, LYV, BAX 2008, ZBRA, REG, SANM (2), HUBS, TRNO.
  - The "no split" judgment rests on the absence of a split ratio fact and of a matching share step (IRM, EQIX and BAC share jumps are distributions, offerings or acquisitions).
- **8 justified holds.** In each, the stored value is wrong or a real event is still pending:
  - TTC (2:1 in 2012 and 2016; stored 1.065 vs 2.13/4)
  - ET (2014 2:1 candidate)
  - CELH Q1 2016 (stored double-divided)
  - GSAT 2014 and 2024 (1:15 in 2025)
  - AOS Q3 2014 (stored 0.14 vs 0.56/2)
  - CBSH shares
  - SMCI shares (10:1 in 2025)
- **3 unresolved:**
  - CVNA: ratio fact 0.2 at 2026-05; no share step seen.
  - SYRE: the 2025 step is an offering, not a split, so this is probably a false hold.
  - BAX Q3 2018 0.97 vs original 1.02: Baxter's 2019 restatement; DATA-INFERRED.

The class holds a correct value about 72% of the time. Most companies in it are not among the 52 review events, so the hold is probably triggered by a near-5%/10% ratio between restated copies, read as a stock dividend.

## Next action (Period Engineer)

1. The majority-of-later-copies rule must not override the originals when the later copies equal the next year's value at the same position (the PPL pattern). Re-run the check on `unchanged` cells too, because those include wrong stored values that equal the new pick.
2. Dominion: hold, or take the latest restatement after confirming it.
3. Narrow the stock-dividend trigger to filed stock-dividend evidence: StockIssuedDuringPeriodValueStockDividend, or an equal ratio on 2 or more consecutive years (CBSH, VLY). Release the other basis_review cells.
4. Release SSNC, HST, HEI, LEA and PRAX, and the restated_between_filings false holds listed in section 2.
