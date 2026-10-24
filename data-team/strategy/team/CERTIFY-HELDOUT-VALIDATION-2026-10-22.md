# Certification suite round 2: held-out validation (S010, S030, S060)

Role: Data Verifier. Date: 2026-10-22/23. Code: origin/main `4aa3503` (no later commit touches `pipeline/src/scrooner_pipeline/certification/`), run from a detached worktree, dry run, nothing written. Scope: top-1000 cohort shards S010, S030, S060 (30 companies, none in the S001/S002 tuning set) plus TSLA (S001) for the four named cells only.

**Status: COMPLETE for the sample; 6 of 120 sampled cells could not be read with my tools (NOT-VERIFIED, listed).** The author's 96% recall was measured on training gold cells it was tuned against; the numbers below are the first held-out figures.

## 1. Run
- One read-only DB connection for the whole run (driver `hv/drive.py`: registry loaded once, one company per chunk, `pg_stat_activity` checked on the same connection before every company, loader sets `statement_timeout` 60s before every statement, no retry on timeout). Max 11 client backends seen, 0 timeouts, 31 companies in about 14 min. A second light read (canonical cells + source facts per company, same limits) built the sampling frames. The coordinator's later 20s / 12-backend rule came after both reads; no DB query was issued after it.
- Output (31 companies incl. TSLA): 9,959 findings: wrong_value 1,246, review 7,173, info 1,540; all 31 `uncertified`. Without TSLA: wrong_value 1,145, review 6,876.
- Frames (30 held-out companies, displayed cells with period end >= 2015-01-01, 47,991 cells). A cell = (company, displayed base concept, period end). I11 missing-cell findings, metric findings and other non-cell findings are outside the frames (untested, section 6).
  - P frame flagged = cells with >= 1 wrong_value finding: **1,053**; P passed = cells with none: **46,938** (of which 1,296 carry only review findings).
  - K frame flagged = cells with >= 1 review finding: **1,412**; K passed = cells with no finding at all: **45,642**.
- Sampling: seed `20261022` (Python `random.Random(f"20261022-{class}-{flagged|passed}")`), 30 per frame, at most one cell per (company, rule) for flagged and per (company, concept) for passed, at most 2 per company. This spreads the flagged draw across rules, so flagged precision is a per-draw figure, not a frequency-weighted population estimate; per-rule counts are given. Where a (company, concept, end) key matched both a quarter and a longer window, the verdict is on the flagged cell (stored value in the finding) or, for passed cells, the filed (non-derived) window; derived copies that were not checked are marked.
- Filing checks: SEC R-files of the source accession (rendered row label + column), earnings-release Ex. 99.1 for Q4 per-share cells, FY minus 9M from the two face statements for derived tax rates. SEC access through the shared flock limiter (5 req/s cap), declared User-Agent, cached. Reader caveat: one regex R-file reader; it misaligned columns where a row has empty or footnote cells (caught on MPC CFI and SGI R&D, re-read raw or via SEC companyconcept). There was no second reader, so the 10% second-reader rule of the check cards was NOT met.

## 2. Definitions
- **Precision (flagged)**: of flagged cells I could verify, the share whose displayed value is wrong on the filing (sign, scale, basis, definition, cross-vintage or split basis). Reported strict (the named cell is wrong) and policy-inclusive (the rule's own policy is violated even if the number is right, e.g. a derived Q4 EPS that equals the release).
- **Miss rate (passed)**: of passed cells verified, the share that is wrong. Recall = TP / (TP + FN); with 0 wrong found in a passed sample, recall is bounded only by the clean-sample bound (n=30: 9.5% miss rate at 95%).
- Share counts before a split are counted wrong under the ledger rule "re-base share counts too" (22-FILING-LESSONS-LEDGER, NVDA row 2026-10-21); listed separately.

## 3. Results
| Class | Flagged checked | Flagged wrong (strict) | Precision strict | Policy-inclusive | Passed checked | Passed wrong | Miss rate (95% bound) |
|---|---|---|---|---|---|---|---|
| P (wrong_value) | 28 of 30 | 22 (6 are pre-split share counts) | **22/28 = 79%** | 28/28 (5 derived Q4 EPS equal the release; 1 finding names the right FY cell but the wrong value is its Q4) | 30 of 30 | 0 | 0/30 (< 9.5%) |
| K (review) | 28 of 30 | 7 | **7/28 = 25%** (value wrong) | flagged condition real in 23/28; false premise in 5/28 (4 identity, 1 stale) | 28 of 30 | 0 | 0/28 (< 10.2%) |

All verdicts FILING-CHECKED except where marked; the six NOT-VERIFIED cells are not in any denominator.

**P per rule (flagged sample):** share_basis_mismatch 7/7 wrong (6 share counts under the re-base rule, 1 per-share GGG); per_share_derived_by_subtraction on effective tax rate 7/7 wrong (every derived Q4 rate is nonsense, e.g. PGR -40.4% vs 20.6%; KR/MPC not verified); per_share_derived_by_subtraction on EPS 6/11 wrong by 0.01-0.59 (AVY, EL, NEM, CBRE, FTNT, TTWO) and 5/11 equal to the release (CSGP, ILMN, BAX, SPGI, BMY); negative_on_nonnegative_concept 1/1; mixed_vintage 1/1; quarters_do_not_sum_to_year 0/1 on the named cell (the FY is right; the wrong value is the Q4 it names as suspect).

**K per rule (flagged sample):** identity:net_income / identity:gross_profit 0/4 (all false premises: NCI at MPC and SPGI, excise taxes at MO, REIT at DOC); non_authoritative_source 4/12 wrong (CMG tax sign, GGG split, DOC definition, BMY cross-vintage); layer_disagreement 1/1 (BAX debt); value_not_in_sources 1/1 (VLO); negative_on_nonnegative (review) 1/1 (LMT); stale_displayed_value 0/3 value-wrong (MLI public float is annual-only, so the flag is false; ILMN, ROP staleness DATA-INFERRED); per_share_derived DPS 0/3; recast_8k_lineage 0/1; quarters_vs_year_basis_mix 0/2 value-wrong (basis mix real both times). Under tier K's rule (9 of 10 confirmed keeps a review rule) the identity rules fail outright.

**Recall, P class:** the random passed sample found no wrong cell, but the K-flagged sample is a stratum of the P-passed frame (1,296 cells with review only) and 6 of its 27 verified non-P cells are wrong values (CMG, LMT FY, BAX, DOC, VLO, BMY). Those are P misses: wrong values that are not gating. Rough estimate (DATA-INFERRED arithmetic on FILING-CHECKED samples): TP ~ 0.79 x 1,053 ~ 830; FN in the review-only stratum ~ 6/27 x 1,296 ~ 290; FN in the unflagged stratum 0 observed, bound < 10% of 45,642. **Held-out P recall point estimate ~ 74%, lower bound not established**, against the author's 96% training figure.

**Recall misses found outside the random draw (risk-selected, FILING-CHECKED):**
- **ODFL 3-for-2 split (March 2020) is invisible to the suite.** `thresholds.CLEAN_RATIOS` has no 1.5 and the split table lacks it, so (a) stored FY2015-2017 diluted EPS 1.785 / 1.78 / 2.815 (as filed 3.57 / 3.56 / 5.63, divided by 2 only; right value /3 = 1.19 / 1.19 / 1.88) pass as clean; (b) flagged pre-2020 share counts carry the wrong expected value (164.75M instead of 247.1M). Evidence: ODFL 10-Q 0001564590-20-021054 R16 'Common stock split, conversion ratio 1.5'; FY2017 EPS 5.63 in 10-K 0000878927-18-000005.
- **BAX total debt 2020-06-30 = 319M vs 6,374M on the face** (1 + 318 + 6,055 'Long-term debt and finance lease obligations', 10-Q 0001628280-20-010911 R2): only review. `debt_below_component` did not fire, so `LongTermDebtAndCapitalLeaseObligations` (noncurrent) is apparently not among the registry components it reads (DATA-INFERRED; not traced in code).
- **CMG FY2018 income tax stored -91.9M (a benefit) vs +91.9M expense**: the FY2020 10-K re-tags the comparative with a flipped sign; the latest copy won. Only review (non_authoritative). I3 cannot see it because tax can legitimately be negative.

## 4. TSLA diluted EPS (company 4945)
Splits: 5-for-1 (10-K 0001564590-21-004599 R5, 2020) and 3-for-1 (10-K 0000950170-23-001409 R5, 2022), factor 15.

| Cell | Stored | As filed (locator) | Right value on today's basis | Suite | Verdict |
|---|---|---|---|---|---|
| Q1 2015 (2015-01-01..03-31) | -1.22 | (1.22), 10-Q 0001564590-15-003789 R4 | -0.081 | share_basis_mismatch, wrong_value | flag CONFIRMED |
| Q2 2015 3M (04-01..06-30) | -1.45 | (1.45), 10-Q 0001564590-15-006666 R4 | -0.097 | share_basis_mismatch | CONFIRMED |
| 6M 2015 (01-01..06-30) | -2.68 | (2.68), same R4 | -0.179 | share_basis_mismatch | CONFIRMED |
| Q1 2016 | -2.13 | (2.13), 10-Q 0001564590-16-018886 R4 | -0.142 | share_basis_mismatch | CONFIRMED |
| Q2 2016 3M | -2.09 | (2.09), 10-Q 0001564590-16-023024 R4 | -0.139 | share_basis_mismatch | CONFIRMED |
| 6M 2016 | -4.22 | (4.22), same R4 | -0.281 | share_basis_mismatch | CONFIRMED |

They are not 3-month vs YTD duplicates: each window is its own cell with one source fact equal to its own column (FILING-CHECKED). The stored values are as filed and were never split-adjusted, so the flag is right and the expected value it reports is right. The 'newest copy' rule is not exercised here (one source each). Open question for the owner (DATA-INFERRED): why the retroactive split stage skipped these rows while TSLA Q3 2019 was adjusted.

## 5. What to fix (owner: suite author; revision goes back to the owner, not changed here)
1. Add 1.5 (and other non-integer ratios such as 2.5 / 1.25) to split detection, or make the split table authoritative from the filer's `StockholdersEquityNoteStockSplitConversionRatio1` facts; re-run ODFL.
2. Make `per_share_derived_by_subtraction` on effective_tax_rate unconditional wrong (7/7) and, for EPS, compare with a filed Q4 figure where one exists; the policy (ledger: Q4 EPS cannot be derived) already makes the 5 numerically right ones unpublishable, so the class stays gating, but the report should separate "wrong number" from "unsourced".
3. Promote to gating, or add a gating check for: a total below a balance-sheet line it must contain (BAX), sign flip between copies of the same fact across filings (CMG), liabilities = assets - equity +/- NCI (VLO), opex derived as GP - OI where no opex line exists (LMT; negative), opex = revenue - a property-expense line at REITs (DOC), cross-vintage arithmetic (BMY).
4. Demote or fix identity:net_income / identity:gross_profit (0/4: NCI, excise taxes, REITs) and stale_displayed_value for annual-only items (public float).
5. `quarters_do_not_sum_to_year` should name the suspect quarter as the finding cell (ODFL Q4 2017 tax +104.9M is the filer's Tax Act remeasurement benefit tagged as a 3-month total provision with positive sign).

## 6. Untested scope
I11 missing-cell and missing-metric findings (5,065 review), metric-level findings (stale metrics, market cap, P/E), info findings, derived quarter copies marked "not verified" in the tables, 6 NOT-VERIFIED cells (KR Q4 EPS, MPC Q4 ETR, PGR goodwill staleness, NEM and BAX 2016 cash, VRTX 6M GP), the second-reader 10% subsample, and every rule that drew no sample cell (layer_sign_conflict, neighbour_magnitude, statement_role_suspect, dps_rate_on_ytd, debt_below_component, share_jump_without_split, per_share_basis_mix as sole rule, quarter_equals_longer_window, stale_quarter_basis, differs_from_authoritative_copy, non_periodic_form wrong_value, I1). n=30 per frame bounds a clean result at 9.5%; it does not show any rule is correct.

## 7. Verdicts (compact)
### P flagged (wrong_value)
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | LMT | operating_expenses Q4 2025 (2025-09-29..12-31) | -9,000,000 (derived GP-OI) | LMT has no opex line between GP and OP; GP 7,619 -> Other income, net 112 -> OP 7,731 (FY); value is other income with flipped sign | CONFIRMED | FILING-CHECKED | LMT 10-K 0001628280-26-004195 R3 |
| 1 | FTNT | shares_outstanding 2018-04-30 | 168,097,115 | cover 168,097,115 as filed; 5-for-1 split 2022 -> 840,485,575 on today's basis | CONFIRMED(policy: re-base share counts, ledger NVDA row) | FILING-CHECKED | FTNT 10-Q 0001262039-18-000019 R1; split: 10-Q 0001262039-22-000029 ratio 5 |
| 2 | ODFL | shares_outstanding 2017-09-30 | 82,375,945 | as filed 82,375,945; splits 3-for-2 (2020, ratio 1.5) and 2-for-1 (2024) -> 247,127,835; suite's expected 164,751,890 is wrong (misses the 1.5 split) | CONFIRMED (flag right, expected value wrong) | FILING-CHECKED | ODFL 10-Q 0000878927-17-000035 R3; 10-Q 0001564590-20-021054 R16 (split ratio 1.5) |
| 3 | AVY | diluted_eps Q4 2025 | 2.16 (derived) | 2.15 reported | CONFIRMED | FILING-CHECKED | AVY 8-K 0000008818-26-000004 Ex.99.1 table 'Net income per common share, assuming dilution' |
| 4 | CSGP | shares_outstanding 2018-07-20 | 36,391,084 | cover 36,391,084 as filed; 10-for-1 split 2021 -> 363,910,840 | CONFIRMED(policy: re-base) | FILING-CHECKED | CSGP 10-Q 0001057352-18-000082 R1; split: 10-Q 0001057352-21-000082 ratio 10 |
| 5 | ODFL | income_tax_expense FY2017 (finding names the FY cell) | 112,058,000 | FY 112,058 correct; the wrong cell is Q4 2017 = +104,900,000, which is the filer's Tax Act remeasurement BENEFIT tagged as 3-month IncomeTaxExpenseBenefit (footnote [1]: provisional tax benefit of $104.9M) | FINDING-CONFIRMED / CELL-REFUTED (named cell correct, suspect quarter wrong) | FILING-CHECKED | ODFL 10-K 0000878927-18-000005 R4; 10-K 0001564590-19-004755 R33, R45 fn [1] |
| 6 | EL | diluted_eps Q4 FY2023 (2023-04-01..06-30) | -0.08 (derived) | (0.09) reported | CONFIRMED | FILING-CHECKED | EL 8-K 0001001250-23-000110 Ex.99.1 GAAP/non-GAAP EPS table |
| 7 | MLI | shares_outstanding 2020-03-28 | 56,752,790 | balance-sheet parenthetical 56,752,790 as filed; suite expects x4 (splits 2023-09-26 and 2026-05-29); split FC pending | CONFIRMED(policy: re-base) | FILING-CHECKED | MLI 10-Q 0000089439-20-000025 R6; split: MLI 10-Q 0000089439-23-000070 (2:1 2023) + 10-Q 0000089439-26-000032 R2 fn [1] (2:1 2026-06-30; cover 221.2M vs 110.6M) |
| 8 | CSGP | diluted_eps Q4 2022 | 0.31 (derived) | 0.31 reported | VALUE-CORRECT (policy-only: no filed Q4 source) | FILING-CHECKED | CSGP 8-K 0001057352-23-000026 q42022earningspressrelease.htm |
| 9 | ILMN | basic_eps Q4 2023 | -1.11 (derived) | (1.11) reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | ILMN 8-K 0001110803-24-000007 a4q23earningsrelease.htm |
| 10 | BAX | diluted_eps Q4 2021 | 0.47 (derived) | 0.47 reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | BAX 8-K 0001628280-22-002932 Ex.99.1 |
| 11 | PGR | effective_tax_rate_reported Q4 2023 | -0.404 (derived by subtracting rates) | Q4 = (1,001.3-485.7)/(4,903.7-2,400.3) = 515.6/2,503.4 = 20.6% | CONFIRMED | FILING-CHECKED | PGR 10-K 0000080661-24-000007 R3; 10-Q 0000080661-23-000049 R2 |
| 12 | NEM | basic_eps Q4 2023 | -3.80 (derived) | (3.21) reported | CONFIRMED | FILING-CHECKED | NEM 8-K 0001164727-24-000006 newmontq42023earning*.htm per-share table |
| 13 | CMG | shares_outstanding 2019-04-22 | 27,713,556 | cover 27,713,556 as filed; 50-for-1 split 2024 -> 1,385,677,800 | CONFIRMED(policy: re-base) | FILING-CHECKED | CMG 10-Q 0001058090-19-000015 R1; split: 10-Q 0001058090-24-000032 ratio 50 |
| 14 | CBRE | basic_eps Q4 2022 | 0.28 (derived) | 0.26 reported | CONFIRMED | FILING-CHECKED | CBRE 8-K 0001138118-23-000005 Ex.99.1 'Net income per share attributable to CBRE Group' |
| 15 | FTNT | diluted_eps Q4 2022 | 0.39 (derived) | 0.40 reported | CONFIRMED | FILING-CHECKED | FTNT 8-K 0001262039-23-000003 ftntq4-2022ex991.htm |
| 16 | SGI | effective_tax_rate_reported Q4 2021 | -0.485 (derived) | Q4 = (198.3-143.9)/(824.0-593.0) = 54.4/231.0 = 23.5% | CONFIRMED | FILING-CHECKED | SGI 10-K 0001206264-22-000057 R3; 10-Q 0001206264-21-000250 R2 |
| 17 | SPGI | diluted_eps Q4 2024 | 2.85 (derived) | 2.85 reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | SPGI 8-K 0000064040-25-000046 Ex.99.1 'GAAP Diluted EPS $2.85' |
| 18 | TTWO | effective_tax_rate_reported Q4 FY2022 (2022-01-01..03-31) | -0.544 (derived) | Q4 = (47,376-36,507)/(465,398-343,557) = 10,869/121,841 = 8.9% | CONFIRMED | FILING-CHECKED | TTWO 10-K 0001628280-22-014580 R5; 10-Q 0001628280-22-001929 R4 |
| 19 | CSL | operating_expenses FY2018 | 664,700,000 (GP from original 10-K minus OI from 2021 recast 8-K) | original basis 1,174.7-509.0 = 665.7M (S&A 625.4 + R&D 55.1 - other op 14.8); recast basis 613.3M; stored matches neither | CONFIRMED | FILING-CHECKED | CSL 10-K 0000790051-19-000070 R2; 8-K 0000790051-21-000226 R2 |
| 20 | GGG | basic_eps 6M 2016 (and Q2 2016 copy) | 1.63 / 0.92 | as filed 1.63 / 0.92; 3-for-1 split Dec 2017 not applied -> 0.543 / 0.307 | CONFIRMED | FILING-CHECKED | GGG 10-Q 0000042888-16-000020 R2; split: GGG 10-K 0000042888-18-000009 R8 (three-for-one; cover 169.4M vs 56.0M in 0000042888-17-000027) |
| 21 | DHI | effective_tax_rate_reported Q4 FY2023 | -0.474 (derived) | Q4 = (1,519.5-1,026.7)/(6,314.7-4,296.4) = 492.8/2,018.3 = 24.4% | CONFIRMED | FILING-CHECKED | DHI 10-K 0000882184-23-000115 R4; 10-Q 0000882184-23-000093 R3 |
| 22 | SGI | shares_outstanding 2019-02-18 | 54,641,297 | cover 54,641,297 as filed; 4-for-1 split Nov 2020 -> 218,565,188 | CONFIRMED(policy: re-base) | FILING-CHECKED | SGI 10-K 0001206264-19-000047 R1; split: SGI 10-K 0001206264-21-000053 split ratio 4 (2020-11-24) |
| 23 | TTWO | diluted_eps Q4 FY2025 | -21.27 (derived) | (21.08) reported | CONFIRMED | FILING-CHECKED | TTWO 8-K 0001628280-25-025900 ttwo4q25earningsrelease.htm |
| 24 | KR | basic_eps Q4 FY2024 | 0.91 (derived) | release table not parsed by my reader | NOT-VERIFIED | - | KR 8-K 0001104659-25-021187 (opened, row not found) |
| 25 | MPC | effective_tax_rate_reported Q4 2018 | -0.26 (derived) | FY 962/4,568 = 21.1%; 9M column misread by my R-file reader | NOT-VERIFIED | - | MPC 10-K 0001510295-19-000014 R2; 10-Q 0001510295-18-000215 R2 |
| 26 | LMT | effective_tax_rate_reported Q4 2024 | -0.328 (derived) | Q4 = (884-892)/(6,220-5,701) = -8/519 = -1.5% | CONFIRMED | FILING-CHECKED | LMT 10-K 0000936468-25-000009 R3; 10-Q 0000936468-24-000110 R2 |
| 27 | CMG | effective_tax_rate_reported Q4 2017 | -0.790 (derived) | Q4 = (99,490-81,817)/(275,743-214,277) = 17,673/61,466 = 28.8% | CONFIRMED | FILING-CHECKED | CMG 10-K 0001058090-18-000018 R4; 10-Q 0001058090-17-000044 R4 |
| 28 | BMY | diluted_eps Q4 2021 | 1.07 (derived) | 1.07 reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | BMY 8-K 0000014272-22-000047 q42021ex991.htm |
| 29 | MLI | effective_tax_rate_reported Q4 2024 | -0.50 (derived) | Q4 = (205,076-159,406)/(820,462-642,250) = 45,670/178,212 = 25.6% | CONFIRMED | FILING-CHECKED | MLI 10-K 0000089439-25-000010 R3; 10-Q 0000089439-24-000061 R2 |

### P passed (no wrong_value finding)
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | ROP | shares_outstanding 2025-10-24 | 107,637,430 | cover 107,637,430 | RIGHT | FILING-CHECKED | ROP 10-Q 0000882835-25-000045 R1 |
| 1 | TTWO | accounts_receivable 2017-03-31 | 219,558,000 | 219,558K | RIGHT | FILING-CHECKED | TTWO 10-K 0001628280-17-005833 R2 |
| 2 | BAX | operating_expenses FY2019 | 2,989,000,000 | SG&A 2,535 + R&D 595 - other operating income 141 = 2,989 (= GP 4,761 - OI 1,772) | RIGHT (Q4 762M derived copy not verified) | FILING-CHECKED | BAX 10-K 0001628280-20-003693 R4 |
| 3 | AVY | shares_outstanding 2015-08-01 | 91,437,757 | cover 91,437,757; no split since | RIGHT | FILING-CHECKED | AVY 10-Q 0001104659-15-055774 R1 |
| 4 | BMY | dividends_per_share Q1 2026 | 0.63 | 0.63 declared | RIGHT | FILING-CHECKED | BMY 10-Q 0000014272-26-000010 R80 |
| 5 | BMY | cf_ap_change Q4 2018 | 127,000,000 (derived) | FY (59) - 9M (186) = +127 | RIGHT | FILING-CHECKED | BMY 10-K 0000014272-19-000047 R6; 10-Q 0000014272-18-000197 R5 |
| 6 | ALLE | income_before_tax Q2 2021 | 136,200,000 | 136.2M | RIGHT | FILING-CHECKED | ALLE 10-Q 0001579241-21-000062 R2 |
| 7 | GGG | operating_income Q3 2023 | 163,189,000 | 163,189K | RIGHT | FILING-CHECKED | GGG 10-Q 0000042888-23-000051 R2 |
| 8 | CSGP | revenue Q3 2021 | 499,319,000 | 499,319K | RIGHT | FILING-CHECKED | CSGP 10-Q 0001057352-22-000121 R2 |
| 9 | KR | stockholders_equity 2021-01-30 | 9,576,000,000 | 9,576M (Kroger shareholders) | RIGHT | FILING-CHECKED | KR 10-K 0001558370-21-003706 R2 |
| 10 | DOC | shares_outstanding 2025-09-30 | 694,946,444 | 694,946,444 | RIGHT | FILING-CHECKED | DOC 10-Q 0001628280-25-046273 R3 |
| 11 | ALLE | cost_of_revenue Q2 2021 | 426,400,000 | 426.4M | RIGHT | FILING-CHECKED | ALLE 10-Q 0001579241-21-000062 R2 |
| 13 | SGI | gross_profit 6M 2026 / Q2 2026 | 1,594.1M / 817.2M | 1,594.1 / 817.2 | RIGHT | FILING-CHECKED | SGI 10-Q 0001206264-26-000113 R2 |
| 14 | ILMN | research_and_development Q3 2017 | 134,000,000 | 134M | RIGHT | FILING-CHECKED | ILMN 10-Q 0001110803-17-000045 R3 |
| 15 | ILMN | amortization_of_intangibles Q1 2024 | 49,000,000 | 49M | RIGHT | FILING-CHECKED | ILMN 10-Q 0001110803-24-000024 R6 |
| 16 | VRTX | accounts_receivable 2022-09-30 | 1,385,200,000 | 1,385.2M | RIGHT | FILING-CHECKED | VRTX 10-Q 0000875320-22-000038 R5 |
| 17 | CBRE | shares_outstanding 2024-07-22 | 306,431,434 | 306,431,434 | RIGHT | FILING-CHECKED | CBRE 10-Q 0001138118-24-000023 R1 |
| 18 | CSL | current_liabilities 2017-06-30 | 601,900,000 | 601.9M | RIGHT | FILING-CHECKED | CSL 10-Q 0001628280-17-007300 R3 |
| 19 | VRTX | diluted_eps Q1 2023 | 2.69 | 2.69 | RIGHT | FILING-CHECKED | VRTX 10-Q 0000875320-23-000012 R2 |
| 12 | EL | depreciation_and_amortization Q3 FY2020 | 160,000,000 (derived) | 9M 447 - 6M 287 = 160 | RIGHT | FILING-CHECKED | EL 10-Q 0001001250-20-000033 R6; 10-Q 0001104659-20-011857 R6 |
| 20 | SGI | cash_flow_investing 9M 2025 | -2,948,400,000 | (2,948.4) | RIGHT (Q3 derived copy -70.3M not verified) | FILING-CHECKED | SGI 10-Q 0001206264-25-000194 R7 |
| 21 | MO | total_liabilities 2018-03-31 | 28,465,000,000 | 28,465M | RIGHT | FILING-CHECKED | MO 10-Q 0000764180-18-000038 R2 |
| 22 | SPGI | cash_flow_investing 9M 2017 | -155,000,000 | (155) | RIGHT (Q3 derived copy not verified) | FILING-CHECKED | SPGI 10-Q 0000064040-17-000069 R6 |
| 23 | MLI | total_debt 2025-06-28 | 74,000 | current portion of debt 74K + long-term 0 | RIGHT | FILING-CHECKED | MLI 10-Q 0000089439-25-000044 R5 |
| 24 | MLI | cf_inventory_change FY2015 | -41,086,000 | prints 41,086 on negated row (inventory decrease); stored sign is the fact's sign | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | MLI 10-K 0000089439-16-000038 R7 |
| 25 | AVY | stockholders_equity 2019-06-29 | 1,062,500,000 | 1,062.5M | RIGHT | FILING-CHECKED | AVY 10-Q 0001410578-19-000582 R2 |
| 26 | CSL | stockholders_equity 2021-09-30 | 2,544,800,000 | 2,544.8M | RIGHT | FILING-CHECKED | CSL 10-Q 0000790051-21-000233 R3 |
| 27 | TTWO | stockholders_equity 2016-06-30 | 533,540,000 | 533,540K | RIGHT | FILING-CHECKED | TTWO 10-Q 0001047469-16-014693 R2 |
| 28 | CBRE | depreciation_and_amortization Q3 2020 | 127,725,000 | 127,725K | RIGHT | FILING-CHECKED | CBRE 10-Q 0001564590-20-048948 R4 |
| 29 | PGR | revenue FY2017 | 26,839,000,000 | 26,839.0M | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | PGR 10-K 0000080661-20-000006 R2 |

### K flagged (review)
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | CMG | income_tax_expense FY2018 (non_authoritative_source) | -91,883,000 | expense of +91,883K: FY2018/FY2019 10-Ks tag +91,883,000; the FY2020 10-K re-tags the comparative as -91,883,000 (filer sign flip); stored took the latest (flipped) copy. Derived Q4 2018 -172.3M also wrong | VALUE-WRONG (sign) | FILING-CHECKED | CMG 10-K 0001058090-21-000010 R4 'Benefit (provision) for income taxes (91,883)'; 0001058090-19-000007 (+91,883,000 via SEC companyconcept) |
| 1 | MPC | net_income 6M 2022 (identity:net_income) | 6,718,000,000 | NI attributable to MPC 6,718; identity gap is NCI 42+629=671 | VALUE-RIGHT (flag premise false: NCI not applied) | FILING-CHECKED | MPC 10-Q 0001510295-22-000063 R2 |
| 2 | BAX | gross_profit Q3 2016 (recast_8k_lineage) | 1,073,000,000 | recast 8-K 1,073 (original 10-Q 1,071) | VALUE-RIGHT as recast (lineage note real) | FILING-CHECKED | BAX 8-K 0001564590-18-022264 R4 |
| 3 | ROP | operating_income FY2019 (quarters_vs_year_basis_mix) | 1,328,300,000 | FY from FY2021 10-K re-presentation 1,328.3; quarters from original 10-Qs sum 1,498.4 | VALUE-RIGHT, basis mix real | FILING-CHECKED | ROP 10-K 0000882835-22-000012 R5 |
| 4 | GGG | diluted_eps Q3 2016 (non_authoritative_source) | 0.95 | as filed 0.95; 3-for-1 split Dec 2017 not applied (0.317) | VALUE-WRONG (split basis; also P-flagged) | FILING-CHECKED (as-filed) | GGG 10-Q 0000042888-17-000030 R2 |
| 5 | DHI | cash_flow_investing 6M FY2018 (non_authoritative_source) | 31,400,000 | 31.4 (comparative in FY2019 10-Q) | VALUE-RIGHT | FILING-CHECKED | DHI 10-Q 0000882184-19-000096 R7 |
| 6 | CBRE | cfo FY2016 (quarters_vs_year_basis_mix) | 616,985,000 | 616,985K in FY2018 10-K (re-presented); Q4 derived from continuing-ops tag of original 10-K | VALUE-RIGHT, basis mix real | FILING-CHECKED | CBRE 10-K 0001564590-19-005666 R7 |
| 7 | BMY | dividends_per_share Q4 2025 (per_share_derived) | 0.63 (derived) | FY declared 2.49 = 3 x 0.62 + 0.63 (FY from 10-K; quarterly rate 0.63 declared Dec 2025) | VALUE-RIGHT (derivation still policy-disallowed) | FILING-CHECKED (FY) / quarter rate DATA-INFERRED | BMY 10-K 0000014272-26-000004 |
| 8 | SPGI | net_income FY2015 (identity:net_income) | 1,156,000,000 | 1,156 attributable; identity gap = NCI | VALUE-RIGHT (flag premise false) | FILING-CHECKED | SPGI 10-K 0000064040-16-000042 R2 |
| 9 | PGR | goodwill 2023-09-30 (stale_displayed_value) | 227,900,000 | goodwill line exists in Q3 2023 10-Q; absence from latest filing not checked | NOT-VERIFIED | - | PGR 10-Q 0000080661-23-000049 R2 |
| 10 | LMT | operating_expenses FY2021 (negative_on_nonnegative_concept, review) | -62,000,000 | no opex line between GP 9,061 and OP 9,123 (other income +62); negative opex is other income | VALUE-WRONG | FILING-CHECKED | LMT 10-K 0000936468-22-000008 R3 |
| 11 | BAX | total_debt 2020-06-30 (layer_disagreement) | 319,000,000 (resolved) | short-term 1 + current LTD 318 + LTD and finance lease 6,055 = 6,374M; resolved misses the long-term line; base row 1M also wrong | VALUE-WRONG (and debt_below_component did not fire) | FILING-CHECKED | BAX 10-Q 0001628280-20-010911 R2 |
| 12 | MO | dividends_per_share Q4 2024 (per_share_derived) | 1.02 (derived) | FY declared 4.00 = 0.98+0.98+1.02+1.02 | VALUE-RIGHT | FILING-CHECKED (FY) | MO 10-K 0000764180-25-000019 R10 |
| 13 | DOC | operating_income Q2 2016 (non_authoritative_source) | 359,252,000 | REIT has no operating-income subtotal; value = total revenues 538,332 minus the 'Operating' property-expense line 179,080 (total costs and expenses 463,934); cross-vintage inputs | VALUE-WRONG (definition) | FILING-CHECKED | DOC (HCP) 10-Q 0001628280-17-007720 R4 |
| 14 | SPGI | operating_expenses Q1 2024 (non_authoritative_source) | 995,000,000 | S&G 714 + depreciation 23 + amortization 264 = 1,001; GP-OI = 995 nets a 6M operating gain | VALUE-RIGHT under the GP-minus-OI convention (definition question) | FILING-CHECKED | SPGI 10-Q 0000064040-25-000126 R2 |
| 15 | VLO | total_liabilities 2020-12-31 (value_not_in_sources) | 33,814,000,000 | total assets 51,774 - total equity 19,642 = 32,132; stored = assets - Valero equity + NCI (NCI added instead of subtracted) | VALUE-WRONG | FILING-CHECKED | VLO 10-K 0001035002-21-000051 R2 |
| 16 | NEM | cash_and_equivalents 2016-03-31 (non_authoritative_source) | 1,781,000,000 | balance-sheet row not located by my reader | NOT-VERIFIED | - | NEM 10-Q 0001558370-17-002832 |
| 17 | ALLE | gross_profit FY2017 (non_authoritative_source) | 1,072,900,000 | 2,408.2 - 1,335.3 = 1,072.9 | VALUE-RIGHT | FILING-CHECKED | ALLE 10-K 0001579241-20-000013 R2 |
| 18 | KR | operating_income Q4 FY2017 (non_authoritative_source) | 44,000,000 | 44 as filed in 10-K/A (original basis; FY 2,085 vs 2,612 after the pension re-presentation) | VALUE-RIGHT as originally filed (basis question) | FILING-CHECKED | KR 10-K/A 0001558370-18-003055 R4 |
| 19 | MPC | dividends_per_share Q4 2022 (per_share_derived) | 0.75 (derived) | FY 2.49 = 3 x 0.58 + 0.75 | VALUE-RIGHT | FILING-CHECKED (FY) | MPC 10-K 0001510295-23-000012 R13 |
| 20 | LMT | operating_income 9M 2017 (non_authoritative_source) | 4,795,000,000 | 4,795 in FY2018 10-Q comparative (ASC 606 re-presented) | VALUE-RIGHT as re-presented | FILING-CHECKED | LMT 10-Q 0000936468-18-000067 R2 |
| 21 | ILMN | interest_expense FY2023 (stale_displayed_value) | 77,000,000 | (77) FY2023 correct; staleness vs latest filing not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | ILMN 10-K 0001110803-24-000010 R5 |
| 22 | ROP | capex FY2018 (stale_displayed_value) | 49,100,000 | (49.1) correct; staleness not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | ROP 10-K 0000882835-19-000010 R8 |
| 23 | MLI | public_float 2025-06-27 (stale_displayed_value) | 8,641,564,012 | cover of latest 10-K (FY2025, filed 2026-02-25); float is annual-only, so 'not in latest 10-Q' is expected | VALUE-RIGHT, FLAG REFUTED (annual-only item judged on quarterly staleness) | FILING-CHECKED | MLI 10-K 0000089439-26-000008 R1 |
| 24 | BMY | gross_profit 6M 2017 (non_authoritative_source) | 7,239,000,000 | original revenue 10,073 - recast COGS 2,834 (original 10-Q COGS 2,821 -> GP 7,252) | VALUE-WRONG (cross-vintage, 0.2%) | FILING-CHECKED | BMY 10-Q 0000014272-17-000165 R2; 10-Q 0000014272-18-000160 R2 |
| 25 | MO | gross_profit Q2 2020 (identity:gross_profit) | 3,287,000,000 | filed GrossProfit 3,287; identity gap from excise taxes in revenue | VALUE-RIGHT, FLAG REFUTED | FILING-CHECKED | MO 10-Q 0000764180-20-000074 R4 |
| 26 | DOC | net_income Q1 2019 (identity:net_income) | 61,470,000 | 61,470K attributable to HCP | VALUE-RIGHT, FLAG REFUTED | FILING-CHECKED | DOC 10-Q 0001628280-19-005690 R4 |
| 27 | FTNT | diluted_eps 9M 2021 (non_authoritative_source) | 0.49 | 0.49 in FY2022 10-Q comparative (post 5-for-1); original 2.44/5 = 0.488 | VALUE-RIGHT | FILING-CHECKED | FTNT 10-Q 0001262039-22-000038 R4 |
| 28 | EL | gross_profit 9M FY2016 (non_authoritative_source) | 6,946,000,000 | 8,616 - 1,670 (original 10-Q cost of sales 1,670.4) | VALUE-RIGHT | FILING-CHECKED | EL 10-Q 0001104659-16-117119 R2 |
| 29 | ODFL | dividends_per_share FY2023 (non_authoritative_source) | 0.80 | 0.80 (post-split basis, FY2025 10-K). Note the Q4 2023 copy 0.1 = filed 0.2 (already post-split) divided by 2 again; P flags it | VALUE-RIGHT | FILING-CHECKED | ODFL 10-K 0001193125-26-067161 R4; 10-K 0000950170-25-026661 R6 |

### K passed (no finding)
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | CSGP | shares_outstanding 2021-07-23 | 394,955,148 | cover 394,955,148 (post 10-for-1) | RIGHT | FILING-CHECKED | CSGP 10-Q 0001057352-21-000082 R1 |
| 1 | KR | total_debt_split 2025-02-01 | 15,909,000,000 | LongTermDebtCurrent 104 + Noncurrent 15,805; face lines incl. finance leases 272 + 17,633 | RIGHT under the borrowings-only perimeter (finance-lease perimeter is a definition decision) | FILING-CHECKED (face) / split DATA-INFERRED | KR 10-K 0001558370-25-004267 R2 |
| 2 | EL | basic_eps Q1 FY2016 | 0.83 | 0.83 (no split since) | RIGHT | FILING-CHECKED | EL 10-Q 0001104659-15-074840 R2 |
| 3 | DHI | dividends_paid Q1 FY2024 | 99,900,000 | (99.9) | RIGHT | FILING-CHECKED | DHI 10-Q 0000882184-24-000014 R5 |
| 4 | MLI | net_income Q1 2026 | 239,018,000 | 239,018K attributable | RIGHT | FILING-CHECKED | MLI 10-Q 0000089439-26-000018 R2 |
| 5 | ALLE | shares_outstanding 2018-10-22 | 95,055,763 | 95,055,763 | RIGHT | FILING-CHECKED | ALLE 10-Q 0001579241-18-000037 R1 |
| 6 | MPC | cash_flow_investing FY2016 | -2,967,000,000 | (2,967) in the FY2016 column (my reader first misaligned it to 3,398 = 2017) | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | MPC 10-K 0001510295-19-000014 R7 |
| 7 | CMG | ppe_net 2023-12-31 | 2,170,038,000 | 2,170,038K | RIGHT | FILING-CHECKED | CMG 10-K 0001562762-24-000023 R2 |
| 8 | AVY | revenue FY2024 | 8,755,700,000 | 8,755.7M | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | AVY 10-K 0000008818-25-000003 R5 |
| 9 | ODFL | cash_flow_financing Q1 2019 | -45,366,000 | (45,366) | RIGHT | FILING-CHECKED | ODFL 10-Q 0001564590-19-016333 R6 |
| 10 | ALLE | sga_expense Q2 2020 | 150,100,000 | 150.1M | RIGHT | FILING-CHECKED | ALLE 10-Q 0001579241-20-000061 R2 |
| 11 | VRTX | gross_profit 6M 2025 | 4,964,400,000 | not compared (row lookup returned revenue rows only) | NOT-VERIFIED | - | VRTX 10-Q 0000875320-25-000216 R2 |
| 12 | CSGP | amortization_of_intangibles Q1 2021 | 18,419,000 | 'Customer base amortization' 18,419K; CSGP also has cost-of-revenue amortization on other lines (perimeter not checked) | RIGHT for the line read | FILING-CHECKED | CSGP 10-Q 0001057352-21-000067 R2 |
| 13 | SGI | research_and_development FY2017 | 21,700,000 | 21.7M (2017 context in three 10-Ks; R45 column order is context-sorted) | RIGHT | FILING-CHECKED | SGI 10-K 0001206264-18-000033 R45 (+0001206264-19-000047, -20-000079) |
| 14 | TTWO | sbc 9M FY2025 | 244,400,000 | 244.4M | RIGHT (Q3 derived copy not verified) | FILING-CHECKED | TTWO 10-Q 0001628280-25-004308 R6 |
| 15 | TTWO | share_buybacks FY2020 | 0 | 'Repurchase of common stock' 0 (FY2019 362,392) | RIGHT (reported zero) | FILING-CHECKED | TTWO 10-K 0001628280-20-008291 R6 |
| 16 | BAX | cash_and_equivalents 2016-03-31 | 2,211,000,000 | balance-sheet row not located by my reader | NOT-VERIFIED | - | BAX 10-Q 0001193125-16-582011 |
| 17 | DHI | cash_flow_financing Q1 FY2025 | -2,064,600,000 | (2,064.6) | RIGHT | FILING-CHECKED | DHI 10-Q 0000882184-25-000014 R5 |
| 18 | VLO | cash_flow_investing 9M 2016 | -1,384,000,000 | (1,384) | RIGHT (Q3 derived copy not verified) | FILING-CHECKED | VLO 10-Q 0001035002-16-000123 R7 |
| 19 | NEM | current_assets 2019-09-30 | 5,698,000,000 | 5,698M | RIGHT | FILING-CHECKED | NEM 10-Q 0001558370-19-009890 R7 |
| 20 | VRTX | shares_outstanding 2018-04-20 | 254,830,232 | 254,830,232 | RIGHT | FILING-CHECKED | VRTX 10-Q 0000875320-18-000014 R1 |
| 21 | GGG | goodwill 2024-06-28 | 363,537,000 | 363,537K | RIGHT | FILING-CHECKED | GGG 10-Q 0000042888-24-000028 R4 |
| 22 | SPGI | capex 6M 2025 | 104,000,000 | (104) | RIGHT (Q2 derived copy not verified) | FILING-CHECKED | SPGI 10-Q 0000064040-25-000147 R6 |
| 23 | ILMN | capex Q1 2019 | 56,000,000 | (56) | RIGHT | FILING-CHECKED | ILMN 10-Q 0001110803-19-000022 R6 |
| 24 | KR | dividends_paid FY2016 | 429,000,000 | (429) | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | KR 10-K 0001558370-17-002198 R7 |
| 25 | CMG | revenue Q3 2018 | 1,225,007,000 | 1,225,007K | RIGHT | FILING-CHECKED | CMG 10-Q 0001058090-18-000055 R4 |
| 26 | PGR | cash_flow_investing FY2023 | -10,842,000,000 | (10,842) in the 2023 column | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | PGR 10-K 0000080661-26-000086 R7 |
| 27 | ILMN | cf_ap_change FY2024 | -4,000,000 | (4) | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | ILMN 10-K 0001110803-25-000019 R8 |
| 28 | FTNT | sbc 9M 2022 | 162,600,000 | 162.6 | RIGHT (Q3 derived copy not verified) | FILING-CHECKED | FTNT 10-Q 0001262039-22-000038 R7 |
| 29 | ROP | cost_of_revenue Q2 2020 | 461,300,000 | 461.3 | RIGHT | FILING-CHECKED | ROP 10-Q 0000882835-20-000025 R2 |

## 8. Artifacts (scratchpad, not committed)
Driver, frames and caches: `/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/hv/` (`drive.py`, `heldout.json` = all findings, `heldout.txt` = suite text report, `cells.pkl`, `samples.json`, `verdicts_final.tsv`, SEC cache).
