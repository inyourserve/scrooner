# Verify: split re-base run 6 (work/period-engineer/split-rebase 9b81a73), 2026-10-26

Seed random.Random(20261121), drawn in this order:
- 30 dividend_basis_pending (frame 3,686)
- 20 basis_review (687)
- 20 restated_between_filings (1,711)
- 30 unchanged DPS cells (36,740)

Files: doc/data-moat/team/backups/split_rebase_dryrun_cohort1000_20261024.csv.gz (259,325 rows; new columns chosen_tag, note). Claimed counts: other_changed=258, mixed-basis companies 240 -> 0.

Evidence class: FILING-CHECKED unless marked. Report sections follow the kit's `verdict_skeleton` (pipeline/src/scrooner_pipeline/verification/filing_kit.py on main). The kit's face-statement readers target balance sheets and income statements, so DPS was checked against XBRL instance and companyconcept copies instead.

## Result

**GATE FAILS: 3 shown values are wrong, all FILING-CHECKED.** Everything else checked is right, or is a hold.

| Cell | Shown | Right | Evidence |
|---|---|---|---|
| LOGI Oct-Dec 2021 DPS | 0.95 | 0 | The annual dividend was paid in September (Jul-Sep 0.95; Sep-2021 one-month 0.95 in three 10-Ks). In the Q3 FY22 10-Q 0001032975-22-000006, the 9M Apr-Dec total is 0.95, which equals Jul-Sep alone, so Oct-Dec is 0. The filer put the YTD value on the 3-month context |
| AMT FY2022 DPS (declared basis) | 4.30 | 5.86 | AMT's four 2022 declaration facts are 1.40 (03-10), 1.43 (05-18), 1.47 (09-21) and 1.56 (12-07), which sum to 5.86. The 10-K 0001053507-25-000025 tags 4.30 as Declared (only three declarations) and 5.86 as CashPaid |
| AMT FY2023 DPS (declared basis) | 6.31 | 6.45 | The 2023 declarations are 1.56, 1.57, 1.62 and 1.70, which sum to 6.45. The 10-Ks (0001053507-25-000025, -26-000035) tag 6.31 (the paid sum) as Declared and 6.45 as CashPaid, so the tags are swapped |

For AMT and LOGI, a full-year or YTD dividend has to agree with the company's own quarterly or declaration facts on the chosen basis. The fiscal-year solve applied to COP/OKE should also cover these cases.

## Method

- **other_changed:** all 258 cells (238 since 2015) were compared with the first three 10-Q/10-K instances for each period. The 164 cells unchanged from earlier rounds keep their earlier verdicts; the 94 new cells were checked one by one.
- **Named cells:** looked up in the table, then checked against every companyconcept copy and against the company's own quarterly sums.

## Cell table (named cells and claims)

| Cell | Shown / status | Verdict |
|---|---|---|
| AFL Q1 2026 DPS | 0.61 (CashPaid) | Right |
| AES Q2 2020 / Q2 2021 | 0.1433 / 0.1505 | Right |
| CWEN Q3 2014 / Q4 2015 | 0.365 / 0.215 | Right |
| LMT Q4 2024 / Q4 2025 | 3.30 / 3.45 | Right |
| AMT 2023 quarterly paid-basis cells | hidden | Correct to hide. The declared instants are shown (1.56, 1.57, 1.62, 1.70), but the FY values are wrong (see Result) |
| CVI Q2 2020 | hidden | Acceptable: declared 0 sits beside 0.40 paid |
| DCI Q3 FY2019 | 0.19 (stored -379.62) | Right |
| TDG FY2015 and FY2016 DPS 0 (quarters, 6M, 9M, FY) | shown | **Right.** PaymentsOfDividends was 3.4M in FY2015 and 3.0M in FY2016, which is dividend equivalents, not a common dividend. The $24 special was paid in Q1 FY2017 (shown 24, FY2017 46 = 24 + 22). **Correction to my run-5 report:** TDG 9M FY2016 was a false hold, not a justified one |
| MSM 9M FY2021 5.75 | hidden (off-basis; the basis is Declared) | False hold. No declared copy exists, and the value would be the same on either basis: 0.75 x 3 + the $3.50 special (DATA-INFERRED) |
| HL FY2020 0.01625 | hidden (off-basis) | False hold (DATA-INFERRED: HL declares and pays in the same quarter) |
| LLY FY2019 2.68 | hidden (off-basis; the basis is CashPaid) | Correct to hide. 2.68 is the declared value; on the paid basis it is 0.645 x 4 = 2.58 |
| WYNN Q1 2021 0 | hidden (off-basis) | False hold. Paid was also 0 (dividend suspended); the 2023 CashPaid 1 copy is mislabeled |
| Released holds: BPOP 0, NWSA 0, BX 1.92, FE 1.44, WY 1.63, VAL 0.04, HL Q1 2021 0.00875, NPO 1.29, BE -0.10, ANF, BWXT, SNDK, NLY x3, LYFT, QXO 0, AM, SYRE | shown | All right |
| TSCO and TTEK shares | shown | Right; re-based x5 (TSCO 5:1 2024; TTEK 5:1 2025) |

## Withheld cells (avoidable holds)

- **dividend_basis_pending, 30 sampled.**
  - About 25 hold an off-basis value that equals the company's regular rate declared and paid in the same quarter, so the basis-tag value would be identical. Examples: CMI Q1 2014 0.625, UNH, AWK, NSC Q1 2016 0.59, GLPI, LIN FY2018 3.30, EXC FY2014 1.24, JBHT, BAC FY2014 0.12, TPL Q3 2024 11.17/3. These are avoidable holds (DATA-INFERRED).
  - The other 5 are real timing differences, so holding them is right: HWM Q1 2019 (declared 0.08, paid 0.06), FE FY2023 (1.60 vs 1.58), MSM 9M FY2023, MCHP 2018-09-04 instant, IBM January 2017 one-month.
- **basis_review, 20 sampled.**
  - **6 false holds:**
    - AHR 9M 2017 1.80, Q3 2017 0.60 and FY2017 2.40 DPS (= 0.45/0.15/0.60 x 4, post 1:4)
    - AHR Q2 2019 basic -0.28
    - QXO FY2023 -1.63 (2025 10-K copy)
    - NAVN 9M 2025 -6.94 (as filed; DATA-INFERRED)
  - **11 justified:**
    - Old-basis history: MTCH 2014/2015 (x3), DELL FY2016 (Class V era), WULF, UHAL shares
    - PNFP FY2023 (copies 7.14 vs 3.46)
    - AHR shares 2016 and FY2017 EPS 0.02 (not x4)
    - NAVN Q3 2024 (stored -2.76 vs filed -0.92)
    - KMI H1 2014 (declared 0.85 vs paid 0.83)
  - **3 unresolved:** UHAL DPS 2020 0.50, FY2017 1.00 and shares, around the 2022 non-voting distribution.
- **restated_between_filings, 20 sampled.**
  - **5 false holds** where the lone disagreeing copy is a label error:
    - NWSA Q1 2015 0.04 (vs -0.26)
    - NWSA Jul-Sep 2014 0.11 (vs 0.30)
    - SWK Q4 2014 0.91 (vs 1.77 in a 10-K that does not present that quarter)
    - SWK Q4 2017 1.88 (vs -0.72)
    - FORM 9M 2017 0.49 (vs 0.03)
  - **13 policy holds**, real restatements: BIO, FSLR, SCCO, D, ALLY, VMI, DAL, RBC, CRBG, L, TYL, MAR, EQH (LDTI).
  - **2 unresolved:** MOG-A 1.50 vs 1.65; IQV (no copies on these tags).

## False holds

Listed above, inside the withheld cells: MSM, HL FY2020, WYNN; about 25 dividend_basis_pending cells; 6 basis_review cells; 5 restated cells. Holds that were right to hold: LLY FY2019, AMT 2023 paid quarters, CVI Q2 2020, the 5 basis-pending timing cells, 11 basis_review cells, and the 13 restated policy holds.

## Findings for the builder

1. **other_changed:** 94 new cells. 93 are right; the wrong one is LOGI. The paid-basis replacements are correct for BA, LMT, LLY, AMGN, PLD, HWM, TEL, AFL, AWK, FE, MAS, MKC (with the 2020 2:1), GLPI, AES, DCI, APTV, ALV, MATX, HXL, CWEN and RLI.
2. **unchanged DPS:** 0 of 30 are PPL-type. All copies agree, or are split-adjusted (LMT FY2016 6.77 is equal on both tags).
3. **Full-year and YTD dividends must agree with the company's own quarterly or declaration facts on the chosen basis.** That catches the AMT swapped tags, AMT's FY2022 3-of-4 declarations, and LOGI's YTD on a 3-month context.
4. **Release** the same-quarter declared = paid off-basis holds, the lone-label-error restated holds, and the AHR/QXO current-basis cells.

## Requests and disk

- SEC requests: roughly 1,300, at 4 req/s or less with SEC_USER_AGENT.
- Downloads deleted after every batch: yes.
- Free disk at the end: about 4 GB (the low point was 4.1 GB; 3 GB is the stop).
- DB connections: 0.

## Untested scope

- The fixed classes (2,922 / 1,376 / 4,660), new (1,088), basis_conflict (285), invariant (546), units (182).
- Dividend-basis consistency for companies not named here. The claim "240 -> 0 mixed companies" was not re-derived; I spot-checked AES, AFL, AMT, CVI, CWEN and LMT through the named cells.
