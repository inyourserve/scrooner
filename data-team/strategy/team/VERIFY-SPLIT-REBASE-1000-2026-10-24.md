# Verify: split re-base, 1,000-company cohort dry-run (2026-10-24)

Verifier 1. Branch origin/work/period-engineer/split-rebase d7fdefd. Table: doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz (340,719 rows). I did not read the Period Engineer's rationale before sampling. Read-only. No DB writes. SEC fetches used SEC_USER_AGENT at 4 req/s or less, and the downloads have been deleted.

## Verdict

**GATE FAILS. 14 shown values are wrong (13 FILING-CHECKED; GLPI 2020-04-29 DATA-INFERRED), and 6 more are unresolved.** Every one of them is in the `other_changed` class (195 rows), which I checked in full. The split arithmetic itself is clean:
- All 190 sampled shown cells equal the chosen filing's value divided by the factor (or multiplied, for share counts).
- 31 cells whose change is not just the factor were checked against the period's original filing. All are correct.

The failures come from which copy of a value the new code picks, not from the factor. In 13 of the 14 cells (all but TSCO), today's stored value is right and the new code would make it wrong.

## Frames and samples (seed 20261024-split1000)

| Class | Frame | Sampled | Result |
|---|---|---|---|
| was unadjusted (fixed) | 6,476 | 30 | 30 right. Today's stored values were unadjusted (e.g. NOW FY2023 8.42 shown today; right value 1.68) |
| was double-divided (fixed) | 1,452 | 30 | 30 right |
| shares re-based | 6,301 | 30 | 30 right |
| other changed | 195 | **all 195** | **14 wrong, 6 unresolved** (see below) |
| new | 995 | 20 | 20 right |
| unchanged control | 277,648 | 30 | 30 right |
| H restated copies disagree | 5,373 | 25 | 2 false holds (TOL Q2 FY21 0.17; LEA 9M 2014 0.60). The rest are real two-vintage restatements. ULTA shares unresolved |
| H copies disagree after conversion | 1,913 | 15 | Holds justified (AHR 2020 0.45x4 vs 0.86; BF-A share bases). DATA-INFERRED for the 13 with no candidate |
| H unconfirmed split candidate | 2,289 | 15 | Hidden, which is acceptable. PRAX 1-for-15 is real (SEC StockholdersEquityNoteStockSplitConversionRatio1 0.0667, 2023-11-28), so its 20 hidden share cells are false holds and today's values are unadjusted (wrong today). EOG 6M 2009 0.57 looks right (false hold, DATA-INFERRED) |
| H dividend basis pending | 9,653 | 15 | 15 values equal the filed value in every copy (MSA, HAL, V, AON, JNJ 1.68, PG 2.069, IBKR 0.1/4). These are policy holds of correct values (DATA-INFERRED as false holds) |
| H units scale suspect | 753 | 15 | False holds: SAIA 15,937,821 (0001193125-11-290967), EXEL 129,685,614 (0001193125-11-284100), C Q1 2012 DPS 0.01, CF 2007 DPS 0.08/5. Correct holds: ENSG, PCG, RAL 100, SFD 1000 |
| H zero share count filed | 107 | 10 | Holds justified. Today's stored 0 shares are wrong today |
| H quarter equals year | 33 | 10 | Likely false holds. Quarterly rates sit on year contexts (BPOP FY2016 declared 0.6 in 0001193125-17-066025, so Q4 0.15 is right). LEA FY2018 fact not found |
| H derived-only removed (RU-1) | 19,839 | 25 | 23: no filed 3-month fact in the next 3-5 10-Q/10-K instances, so the hold is structural. 2 (CP): the filed facts are CAD (iso4217_CAD_per_shares / cadPerShare, 0000016875-16-000039, 0000016875-25-000039). Hiding is right; today's 0.468 is a CAD value |
| H company invariant | 3,855 (10 cos) | all 10 | False holds: CPRT Q2 FY24 0.33 (0000900075-24-000007), AAON FY2014 0.80/1.5 (0000824142-15-000014), HEI Q2 FY23 0.76 (0000046619-23-000083). Likely false: HOMB, ANF, CELH, SNEX. Correct hold: BRO Q3 2013 0.39 unadjusted (0001193125-13-433040). Unresolved: HWM, KDP |
| 20 largest changes | | 20 | 4 wrong (OHI, TRMB, BWA, TEX; included in the 14) |

## The 14 wrong shown values (all in other_changed)

| Cell | New | Right | Today's value | Evidence |
|---|---|---|---|---|
| OHI Q1 2019 DPS | -0.66 | 0.66 | right | Later filing 0000888491-20-000034 sign-flipped. Own filings 0000888491-19-000015/-000018 show 0.66; DividendsCommonStock is +136.7M |
| BWA FY2019 DPS | 0 | 0.68 | right | 0000908255-20-000014 files 0 but PaymentsOfDividendsCommonStock 2019 = 140M in the same instance |
| TEX Q2 2020 DPS | 0.12 | 0 | right | 0000097216-20-000259 has DividendsCommonStock only for Q1 2020, and 9M payments = Q1 8.4M. The 0.12 is Q1's rate on an Apr-Jun context |
| TRMB Q4 2016 diluted EPS | -0.14 | 0.15 | right | The FY2018 10-K 0000864749-19-000006 labels 2017 quarters as 2016 (they sum to 0.45, not the FY 0.52). Own 10-K 0000864749-17-000007 has 0.15 |
| DCI Q4 FY2015 diluted EPS | 0.44 | 0.41 | right | The FY2017 10-K 0000029644-17-000019 labels FY2016 quarters as FY2015. Its "FY2016" quarters sum to 1.74 (= FY2017), not 1.42. Own filing 0000897101-15-001507 has 0.41 |
| XYL Q3 2019 DPS | 0.26 | 0.24 | right | 0001524472-20-000020 (Q1 2020 10-Q) puts the 2020 rate on a Jul-Sep 2019 context. Own 0001524472-19-000055 has 0.24 |
| XYL Q3 2023 DPS | 0.36 | 0.33 | right | Same pattern in 0001524472-24-000015. Own 0001524472-23-000041 has 0.33 |
| OGE Q1 2020 DPS | 1.505 | 0.3875 | right | 0001021635-20-000089 tags the annual rate on Q1. Later copies (-20-000111, -20-000136) have 0.3875 |
| GLPI 2018-04-24 DPS | 0.60 | 0.63 | right | 0001575965-21-000025 restates a stale value. 3 own filings (0001575965-18-000019, -18-000024, -19-000005) have 0.63 |
| GLPI 2021-05-20 DPS | 0.705 | 0.67 | right | 0001575965-22-000021 vs 0001575965-21-000035 and -22-000005 (0.67) |
| GLPI 2020-04-29 DPS | 0.67 | 0.60 (DATA-INFERRED) | right | Same later-filing drift. No original copy found |
| TSCO 2023-02-08 DPS | 0.22 | 1.03/5 = 0.206 | wrong (1.03 unadjusted) | 0000916365-25-000089 puts the 2024 rate on the 2023 date. Original 1.03 in 3 filings |
| WTRG FY2024 / FY2023 DPS | 0.3255 / 0.3071 | 1.2652 / 1.1882 | right | 0000078128-26-000050 tags the quarterly rate as Declared on the year context. CashPaid for the same year carries the annual value |

(14 cells: WTRG is two cells on one line.)

Unresolved, and showing them is not supported:
- COO Q1 FY2020 DPS 0. The copies disagree: 0 in 0000711404-20-000021 and 0.03 in -20-000032.
- LDOS May-Jul 2012 EPS 0.72, basic and diluted. The original was 0.32 before the 1-for-4 reverse split, which gives 1.28. In 0001336920-14-000007 the quarters do not sum to the FY 6.19.
- IONS FY2019 basic 2.00 and diluted 1.90. The originals were 2.12 and 2.08 (0000874015-20-004500).
- HSIC Q2 2019 basic 0.77 vs 0.79.

The pattern: the chosen copy is often a later vintage whose comparative contexts are year-shifted or carry the current rate, or the copy is a lone filer error. The restated-copies guard did not fire even where copies disagree (OGE, XYL, GLPI, TSCO, COO). I verified that only by outcome; I did not read the code. A fix should do two things: (a) require the period's own original filing to agree with any later copy, and treat disagreement as a restatement hold unless a known restatement explains it; (b) add same-filing guards: DPS <= 0 while PaymentsOfDividends > 0; a quarterly rate on a year context; an annual rate on a quarter context.

Accepted later-vintage recasts, where the filer's own recast is the right basis:
- CHTR 2015, at the 0.9042 TWC exchange ratio.
- TMUS 2011 -8.81, the accounting-acquirer recast.
- MTCH 2019, the predecessor recast.
- RGA 2009-11, the DAC accounting change.
- PPC 2011, the rights-offering bonus element.
- GE 2019 x8, the reverse split.
- SIRI 2022 x10.
- SCI 2012 0.23 (the original filed 0).
- MORN Q1 2013 0.125.

The TMUS, MTCH, RGA and PPC recasts are DATA-INFERRED.

## Named items

- **LDOS Q1 FY2014 DPS 4.48:** right as filed in 0001336920-14-000014 (factor 1). Reading it as (1.00 special + 0.12) x 4 after the 1-for-4 reverse split is DATA-INFERRED. 6M 4.96 is consistent.
- **AHR H1 2021 0.8:** right. 0.2 x 4 at the 1-for-4 reverse split (factor 1/4). Q2 2021 hidden as restated.
- **DD FY2018 13.68:** right. 4.56 as filed x 3. The 2026 1-for-3 reverse split is FILING-CHECKED:
  - SEC split fact 0.333 in 0001666700-26-000053.
  - Shares 409,921,306 (2026-05-01) fell to 135,042,975 (2026-07-31).
  - Q1 2026 DPS 0.20 in 0001666700-26-000031 is consistent with H1 1.20 (0.60 + 0.60).
  - An 8-K with items 3.03/5.03 was filed 2026-06-24.
- **BKNG 25:1:** right. 165.57/25 = 6.6228; 84.41/25 = 3.3764. The 2026-filed post-split Q1/Q2 2025 values are 0.40 and 1.10.
- **PRAX 1-for-15:** real. The one shown cell, 49,382,453/15 = 3,292,163, is right. The other 20 hidden cells are false holds.

## Unconfirmed split rows (IPO/merger exchange ratios)

67 companies in analytics.company_stock_split never get a factor other than 1 from the new pass. The brief said 55; my count includes AWI, AAON, CPRT, SNEX and others with real splits that the new pass also leaves at 1 for these rows.

The IPO/merger cases are wrong today, and the new pass shows them as filed:

| Company | Today's value | As filed (new) | Filing |
|---|---|---|---|
| CFG 2012 EPS | 0.00695 | 1.15 | 0000759944-15-000016 |
| JXN 2019 | -0.1254 | -13.16 | |
| WMG | 0.00126 | 0.06 | |

The same holds for SFD, INGM, PACS, VG, RVMD, AXSM and KNSA, all in the double-divided and other classes. All of these are right in the new pass.

## Today's stored wrong values found (fixed by the new pass unless noted)

- CB and LOGI DPS are stored in CHF, not USD.
- Unadjusted per-share values: NOW, DRI, PINS, BRO, PRAX shares.
- Pre-IPO ratio divisions: CFG, JXN, WMG, SFD, PACS, VG and others.
- Double-divided values: DD, AOS, CHDN, LDOS.
- CP CAD EPS shown as USD.
- Zero share counts (107).
- TSCO 2023-02-08 1.03, unadjusted. The new value is also wrong.

## Untested

- Hidden classes with 0 candidates (H_conflict and H_review rows with n=0). Their old values were judged against split arithmetic only.
- ULTA, HWM and KDP invariant cells.
- Plausibility of the 6,476 / 1,452 / 6,301 classes beyond the 90 sampled cells.
- No code was read.

## Commands

- Seeded sampling from the CSV.
- s1k/chk.py: chosen-filing instance check, 190 shown cells plus hidden candidates.
- s1k/ru1.py: RU-1 search.
- s1k/orig.py and orig_all.py: compare each other/new/largest cell and the 31 unexplained cells with the first three 10-Q/10-K instances for the period.
- Ad hoc instance dumps: OHI, BWA, TEX, TRMB, DCI, XYL, OGE, GLPI, TSCO, WTRG, TEL, LDOS, BF-A, DD.
- SEC companyconcept StockholdersEquityNoteStockSplitConversionRatio1 for DD.

Scripts are in the session scratchpad. The SEC cache has been deleted.
