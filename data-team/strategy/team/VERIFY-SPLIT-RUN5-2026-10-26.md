# Verify: split re-base run 5 (2026-10-26)

Verifier 1. Branch work/period-engineer/split-rebase @0971482. Table: doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz (259,325 rows; more pre-2015 facts were removed upstream, e.g. COST FY2013, CYTK 2012 and HST 2009 cells no longer exist). Seed random.Random(20261116), used in this order: 20 dividend_per_share_invalid (frame 346), 30 restated_between_filings (1,777), 30 basis_review+basis_conflict (2,274), 30 unchanged DPS cells (38,696). DB connections: 0. SEC: SEC_USER_AGENT only, <= 4 req/s; downloads deleted after each batch (disk stayed >= 6 GB).

Method: every other_changed cell (all 190; 178 since 2015) was compared with the period's first three 10-Q/10-K instances. Each sampled cell was compared with every SEC companyconcept copy. Splits were checked with dei share-count steps.

## Verdict

**GATE FAILS: 1 shown value is wrong (FILING-CHECKED), and the shown DPS series mixes the declared and paid bases within the same company (6 companies checked).**

- **The wrong value: AFL Q1 2026 DPS is shown as 0.** The same filing has CommonStockDividendsPerShareCashPaid 0.61. AFL's other 34 shown quarters are on the paid basis (e.g. Q1 2023 0.42, Q1 2024 0.50, Q1 2025 0.58, shown here as other_changed). This contradicts run 4's own rule that a zero copy beside dividends paid is dropped.
- **Basis drift.** Each value equals a filed fact, but a company's quarters switch between bases:
  - **AES:** Q2 2020 and Q2 2021 are 0 (declared) while 0.1433 and 0.1505 were paid. Q2-Q4 2025 are 0.17595 (paid).
  - **AMT:** Q4 2023 is 1.62 (paid). The declared value is 1.70, and the other AMT quarters are on the declared basis.
  - **CVI:** Q2 2020 is 0.40 (paid; declared 0). Other quarters are declared.
  - **CWEN:** Q3 2014 is 0.365 (paid; declared 0.375). Q4 2015 is 0 (declared) while 0.215 was paid.
  - **LMT:** declared through 2021 (Q2 2016 3.30, two declarations). Q4 2024 and Q4 2025 are on the paid basis.

  This needs the dividend-basis decision (AC-24) applied per company. Until then, the off-basis quarters cannot be called right.

## Claimed fixes

| Item | Verdict |
|---|---|
| COP 2021 | Right: Q1/Q2/Q3 0.43, 6M 0.86, 9M 1.29, FY 1.75 |
| OKE 2014 | Right: Q1 0.40, Q2 0.56, Q3 0.575, Q4 0.59, 6M 0.96, 9M 1.535, FY 2.125 |
| COST Q2 FY2013 | The cell is no longer in the table (pre-2015 removal), so it could not be checked |
| CVNA | Right: FY2021 -1.63/5 = -0.326; FY2025 diluted 8.45/5 = 1.69 and basic 10.22/5 = 2.044. Today's stored values (-8.15, 42.25, 51.1) are wrong today, multiplied instead of divided |
| GL | Released and right: 307 cells unchanged and shown. The early 2014 cells come from post-split filings (Q1 2014 EPS 0.98 from 0000320335-16-000059); the 2014-02/04 share counts are re-based x1.5 (88,555,738 -> 132,833,607). 1 cell held as dividend_per_share_invalid, 2 as restated |
| FNB Q4 2016 0.12 | Shown, right |
| MSM Q1 FY2020 0.75 | Shown, right |
| MSM 9M FY2021 5.75 (other_changed) | Right: the original 10-Q 0001003078-21-000127; 6M 5.00 = 1.50 regular + 3.50 special. The later copies (2.25 and 1.50) leave out the special. The special is DATA-INFERRED. Today's stored 2.25 is wrong |
| HST | All 271 remaining cells shown (FY2015 0.80). The 2009 cell was removed upstream |
| CYTK | All 227 shown. The 2012 cell was removed upstream |
| SNDK shares 2025-02-27 144,863,251 | **Still held** (basis_review). False hold: the 10-Q/A corrects 114,863,251 |

## other_changed (190 cells): all checked

- **172 cells** match an earlier round's judged-right value.
- **18 new cells:**
  - **17 right:**
    - LYB June 2024 1.34
    - HEI FY2014 and 6M/9M FY2014 (6 cells): x125/64, as filed 1.80/0.83/1.32
    - AES Q2 2025 0.17595
    - ESI Q1 2015 0. ESI paid no common dividend then; today's stored 22.85 is wrong.
    - MSM 5.75
    - HR Q1 2022 0.31: the accounting acquirer's history after the HTA merger (DATA-INFERRED)
    - The basis-drift cells, each equal to a filed fact (judged above): AFL Q1 2023/2024/2025, AMT, CVI, CWEN
  - **1 is basis drift** (AES Q2 2020 0, above).
  - **1 is wrong:** AFL Q1 2026, which is outside other_changed (class unchanged).

## dividend_per_share_invalid (346): 20 sampled

- **10 false holds.** The value is real:
  - HL Q1 2021 0.00875 and FY2020 0.01625 (two later copies agree)
  - FE FY2016 1.44
  - BX FY2014 1.92
  - LLY FY2019 2.68 (declared: 0.645 x 3 + 0.74)
  - WY Q1 2022 1.63 (base plus variable)
  - BPOP Q1 2015 0 (no common dividend before Q2 2015)
  - WYNN Q1 2021 0 (dividend suspended; the 2023 copy of 1 is mislabeled)
  - VAL Q1 2019 0.04 (after the 1:4)
  - NWSA FY2015 0 (DATA-INFERRED)
- **8 justified.** The value really is invalid:
  - A quarterly rate on a year context: LEA FY2022 0.77; TEX FY2016 0.07; V FY2023 0.45; HL FY2024 0.01 (paid 0.04); GPN FY2018 0.01 (paid 0.04).
  - XYL FY2015 0.005632, a scale error (0.5632 in 2018).
  - IDCC 0.35 on a 2018-2023 multi-year context.
  - TDG 9M FY2016 0, beside a special dividend paid in that period.
- **2 unresolved:** TDG FY2018 0 and 9M FY2023 0. Whether a special dividend was paid inside each period was not checked.

## restated_between_filings (1,777): 30 sampled

- **5 false holds.** The other copy is a clerical error:
  - NPO Q3 2022 1.29 (the 10-K copy says 1,290,000)
  - ANF shares 68,016,186 (the 10-Q says 86,016,786; the next day's filing corrects it)
  - BWXT shares 106,710,346 (10-K/A corrects 121,586,254)
  - TSCO shares 136,416,000 and TTEK shares 54,714,000 (the later copy belongs to another date)
- **1 justified, value recoverable:** BE Q3 2025 basic is stored as -100. The 2026 copy is -0.10.
- **21 policy holds (as-reported vs restated).** Real two-vintage restatements: JAZZ, LH, HALO, LHX, FLS, DELL, D, PEN, LUV, MKL, NTNX, GD, PCAR, TDG, DVN, CVLT, META, TSLA, FANG, IFF, NOC. Where the later copy comes from a full-retrospective accounting change (ASC 606 at GD, LHX and NTNX; META 2016), a single choice of "show the latest restated" would turn these into shown values.
- **3 unresolved:**
  - LDOS: alternates 0.47/0.52 across filings.
  - ALV Q4 2017: 0.72 vs 2.26.
  - KNX: no copies on these tags.

## basis_review + basis_conflict (2,274): 30 sampled

- **8 false holds.** The stored value equals a current-basis filed copy:
  - NLY Q4 2016 basic 7.16 (1.79 x 4), Q1 2021 DPS 0.88 (0.22 x 4), 9M 2020 DPS 2.76 (0.69 x 4)
  - LYFT Q2 2019 -2.23
  - QXO Q2 2018 0
  - AM shares 484,042,000 (the 10-K's 484,042 is a scale error)
  - SYRE shares 2024-02-21 36,150,941 (three copies)
  - SIRI H1 2024 1.76 (2025 copy, current entity; DATA-INFERRED)
- **22 justified holds.** The stored value is on a pre-event basis but recoverable, or the basis is unclear:
  - Pre-event share counts: NLY 2017, VRNS 2014, QXO x3, OTEX 2014, UHAL x2 (before the 2022 non-voting distribution).
  - Aeglea-era SYRE cells: 7 EPS and share cells (x25).
  - Other entities' history or companies with no clear basis: WULF, DELL, FRHC, BMNR.
  - Disagreeing copies: AHR Q3 2021, NLY Q4 2015, CHTR Q4 2015, SIRI Q4 2018.

## unchanged DPS (38,696): 30 sampled for PPL-type errors

**0 of 30.** Every shown value equals a filed copy adjusted by a confirmed split:
- GE x8
- WSM /2
- RLI /2
- ELS /2
- KLAC /10. The 2026 10:1 split is confirmed: dei shares went from 130,627,521 (2026-04-27) to 1,306,546,783 (2026-08-03).

Other cells checked: specials (AFG 11.68), CI Q4 2017 0, and the rest as filed.

## Still open from the brief

LMT one-basis, PRAX x15, CBSH on the 2026 basis, and the QXO/NLY/SYRE/MTCH holds are not fixed. The NLY, SYRE and QXO samples above show false holds persisting.

## Next action (Period Engineer)

1. Apply one dividend basis per company (the AC-24 decision). Drop zero declared copies beside a paid dividend: AFL Q1 2026 is still shown as 0.
2. Release:
   - dividend_per_share_invalid cells whose value is real: specials, full-year declared totals that include the next declaration, and quarters before a first dividend;
   - clerical-copy restated holds (scale and digit typos, amendment-corrected, other-date copies);
   - current-basis basis holds (NLY, SYRE, AM, LYFT, QXO 0, SNDK).
3. Founder or Accountant decision: for full-retrospective restatements, show the latest restated value or the as-reported one. Until that is decided, these remain policy holds.
