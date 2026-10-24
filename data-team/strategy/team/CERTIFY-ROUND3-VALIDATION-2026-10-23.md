# Certification round 3: validation (rule samples + fresh held-out shards)

Role: Data Verifier. Date: 2026-10-23. Code: branch `certify-round3`, commit `5382813` (worktree `/Users/vikash/scrooner-certify-r3`, used read-only; nothing in it was changed). Scope: top-1000 cohort. Dry run only, no DB writes.

**Status: COMPLETE.** 180 sampled cells checked against filings (60 rule-sample cells on S010/S030/S060, 120 fresh held-out cells: 30 flagged + 30 passed for each of P and K); 9 fresh cells NOT-VERIFIED (listed, excluded from denominators).

## 1. Runs
- Driver `r3/drive3.py`: one read-only connection per run, `statement_timeout` 20s set before every statement (the loader does it), pooler/app backends (excluding `supabase*`, `authenticator`, `pgbouncer`) checked before every company with stop at > 12, no retry on timeout. Seen: 2 such backends throughout, 0 timeouts, 0 stops.
- Run A (S010, S030, S060; the round-2 held-out set, now partly training for round 3): 30 companies, 9,672 findings, wrong_value 1,516 (author reports 1,616 including TSLA).
- Run B, **fresh** shards S025, S044, S058, picked by `random.Random('20261023-shards').sample(<97 shards other than S001/S002/S010/S030/S060>, 3)`: AZO VST F TER FIX VEEV EW HUM PYPL DAL / STZ RBRK INCY DINO USFD CRCL XPO NRG ARXS STE / AIZ SWK PAG HAS DOCU TRMB GWRE OHI NBIX HALO. 8,701 findings: wrong_value 1,220, review 6,055, info 1,426; all 30 uncertified. Caveat: SWK and F appear in ledger rows from 2026-10-18 (other cells), not in the certify training set.
- Frames (run B, displayed cells since 2015-01-01): 42,924 cells; P flagged 986 / passed 41,938; K flagged 1,002 / passed 41,031 (907 cells carry review only). Seed `20261023` (`random.Random(f"20261023-{class}-{flagged|passed}")`), same frame and draw rules as the round-2 report (one cell per company and rule, at most 2 per company).
- Evidence: SEC R-files of the source accession, 8-K Ex. 99.1 for derived Q4 EPS, FY minus 9M face lines for derived tax rates; three tax-rate cases used the filing's facts through SEC companyconcept (marked). Shared flock limiter, 5 req/s, cached. One regex reader (column misalignment caught and re-read on SWK, TER, MPC); no second reader.

## 2. Task 1: the new or larger wrong_value rules (run A, training cells named in the round-2 report excluded, seed 20261023-<rule>)
| Rule (scope) | Frame | Checked | Flag right | Notes |
|---|---|---|---|---|
| cross_vintage_arithmetic, SPGI gross profit | 37 | 10 | **0/10** | Revenue is identical in both vintages; the stored GP is the LATER 10-Q's own revenue minus its own operating-related expenses, so one filing does give the stored value. Rule refuted for this pattern |
| liabilities_nci_treatment, EL + ILMN | 27 | 10 | **10/10** | Stored = assets - parent equity + NCI. Suite's expected value right 7/7 at EL, 0/3 at ILMN (redeemable NCI not subtracted) |
| reit_calculated_subtotal, DOC | 115 | 10 | **10/10** | No GP / OI subtotal on any face; values such as GP -251.5M |
| negative_on_nonnegative_concept, LMT operating expenses | 54 | 10 | **10/10** | Stored = minus "Other income, net" |
| debt_isolated_dip | 12 | 10 | **10/10** | Stored = current portion only (BAX x5, MO, EL, VLO, ALLE, NEM) |
| share_basis_mismatch, new in round 3 | 70 | 10 | **10/10** | All 10 sampled are ODFL (the training company for the 3-for-2) |

## 3. Task 2: fresh held-out shards (run B)
| Class | Flagged checked | Flagged wrong (strict) | Precision strict | Policy-inclusive | Passed checked | Passed wrong | Miss rate (95%) |
|---|---|---|---|---|---|---|---|
| P (wrong_value) | 28 of 30 | 16 (1 pre-split share count) | **16/28 = 57%** | 20/28 = 71% (4 derived Q4 EPS equal the release); +1 definition question (OHI) | 30 of 30 | 0 | 0/30 (< 9.5%) |
| K (review) | 26 of 30 | 5 (4 FILING-CHECKED, 1 DATA-INFERRED) | **5/26 = 19%** | flagged condition real in 23/26 (3 false premises) | 27 of 30 | 0 | 0/27 (< 10.5%) |

**P by rule (fresh):** per_share_derived on tax rate 6/6 wrong (NRG, TRMB, HAS, DINO, VEEV, VST); per_share_derived on EPS 6/10 wrong by 0.01-0.03 (DAL, USFD, HALO, INCY, NBIX, PYPL), 4/10 equal the release (PAG, TER, F, STE); **share_basis_mismatch 1/5** (EW right; INCY x0.8, STE x0.8, TER x2, DOCU /4 are invented splits: a self-tender, an acquisition, nothing, and an IPO preferred conversion); liabilities_nci_treatment 2/2 (XPO, SWK); debt_below_component 1/1 (HALO); debt_isolated_dip 0/1 (FIX: the dip is real); stale_quarter_basis 0/1 (PAG: named Q3 cell equals its 10-Q); statement_role_suspect 0/1 (NBIX launch-year COGS); reit_calculated_subtotal 1 definition question (OHI: total revenues minus total expenses, both face totals).

**K by rule (fresh):** non_authoritative_source 2/10 wrong (STZ superseded vintage, AZO 17-year cumulative buyback window, DATA-INFERRED); value_not_in_sources 2/2 (SWK liabilities NCI added, 6M; XPO, also P); quarters_do_not_sum_to_year 1/2 (SWK Q1 2017 revenue 3,209.3 vs filed 2,805.6, a label shift); stale_displayed_value 0/5 value-wrong (staleness itself DATA-INFERRED); neighbour_magnitude 0/1, quarter_equals_adjacent_quarter 0/1, cash_roll_forward 0/1 (all false premises); recast_8k_lineage 0/2; share_jump_without_split 0/1 value-wrong (condition real).

**Recall, P class (fresh):** the random passed sample has 0 wrong. The review-only stratum (907 cells) has 3 FILING-CHECKED wrong values in 25 checked non-P cells (STZ, SWK liabilities, SWK revenue; +1 DATA-INFERRED AZO): about 12-16%. Estimate (DATA-INFERRED arithmetic): TP ~ 0.57 x 986 ~ 560; FN in the review-only stratum ~ 0.12-0.16 x 907 ~ 110-145; unflagged stratum 0 observed, bound < 10% of 41,031. **Point recall ~ 80-84%, lower bound not established.**

## 4. Round 3 vs round 2
| | Round 2 (held-out S010/S030/S060) | Round 3 (fresh S025/S044/S058) |
|---|---|---|
| P strict precision | 22/28 = 79% | **16/28 = 57%** |
| P precision incl. policy-only | 28/28 | 20/28 = 71% |
| K value-wrong precision | 7/28 = 25% | 5/26 = 19% |
| Random passed cells wrong | 0/30 (P), 0/28 (K) | 0/30 (P), 0/27 (K) |
| P recall point estimate | ~74% | ~80-84% |

Different shards, so this is not a like-for-like comparison of one rule set. What moved:
- **Recall rose:** the round-3 gates catch the round-2 review-only misses (liabilities NCI, debt dip, LMT negative opex, REIT subtotals) and they hold up on fresh cells (XPO, SWK, HALO).
- **Precision fell, for two new reasons:**
  1. The non-integer / inferred split logic invents splits. 4 of 5 fresh share_basis flags are false: INCY (2024 self-tender), STE (Cantel acquisition shares), TER (no event), DOCU (IPO preferred conversion). The INCY FY2021 EPS and STE FY2020 DPS/EPS cells carry the same false flags. These come from integer steps (DOCU 4x, TER 2x) as well as the 1.25 ratio, so the "restated per-share comparatives" proof is either not applied to integer steps or not working.
  2. cross_vintage_arithmetic fires on SPGI where the later filing alone reproduces the value (0/10).
- The derived-Q4 classes are unchanged: tax rate always wrong; EPS wrong in about 60% of cases by 0.01-0.03; the rest equal the release but are still unsourced.

## 5. Next actions (owner: suite author)
1. Require the restated-per-share-comparative proof for EVERY inferred split, integer or not, and never infer a split across an IPO, a tender offer (SC TO-I) or an acquisition share issuance. Re-test INCY, STE, TER, DOCU (training cells now).
2. cross_vintage_arithmetic: before firing, check whether the newer filing alone reproduces the value (the SPGI pattern: one input restated, the other unchanged). Re-test the 37 SPGI cells.
3. Promote: value_not_in_sources on total_liabilities when the stored value equals assets - equity + NCI at any size (SWK 2021, 6M); label-shift on a quarter that equals another year's same quarter (SWK Q1 2017 = Q1 2019).
4. Exclude non-standard windows (AZO 1998-2015 cumulative) from display and from every check frame.
5. liabilities_nci_treatment: subtract redeemable NCI too (ILMN).
6. Fresh sample after the fix, from shards not used here (S001, S002, S010, S025, S030, S044, S058, S060 are now all seen).

## 6. Untested scope
I11 and metric findings; info findings; derived copies of passed cells marked "not verified"; 9 NOT-VERIFIED fresh cells (F Q4 SBC, VST Q4 2017 EPS, PYPL Q1 2024 interest, HAS and DINO and F derived DPS, AZO debt, DOCU D&A and capex); staleness claims (DATA-INFERRED); rules without a sampled cell on the fresh shards (sign_flip_between_copies, layer_sign_conflict, dps_rate_on_ytd, per_share_basis_mix as sole rule, quarter_equals_longer_window, identity:balance_sheet); second-reader subsample. n=30 bounds a clean result at 9.5%.

## 7. Task 1 verdicts
### cross_vintage_arithmetic, SPGI gross_profit (frame 37, seed 20261023-R_cross_vintage_SPGI_GP); verdict on the flag
| Cell | Stored | Original 10-Q (rev, op-related exp) | Later 10-Q (rev, op-related exp) | Flag |
|---|---|---|---|---|
| 6M 2015 | 1,792 | 0001628280-15-005469 R2: 2,615, 812 | 0000064040-16-000090 R2: 2,615, 823 -> 1,792 | WRONG FLAG |
| Q3 2015 | 905 | 0000064040-15-000026 R2: 1,324, 407 | 0000064040-16-000109 R2: 1,324, 419 -> 905 | WRONG FLAG |
| FY 2015 | 3,595 | 0000064040-16-000042 R2: 5,313, 1,672 | 0000064040-18-000061 R2: 5,313, 1,718 -> 3,595 | WRONG FLAG |
| 6M 2016 | 1,900 | 0000064040-16-000090 R2: 2,823, 926 | 0000064040-17-000051 R2: 2,823, 923 -> 1,900 | WRONG FLAG |
| 6M 2020 | 2,718 | 0000064040-20-000144 R2: 3,729, 1,014 | 0000064040-21-000155 R2: 3,729, 1,011 -> 2,718 | WRONG FLAG |
| 9M 2020 | 4,047 | 0000064040-20-000188 R2: 5,575, 1,533 | 0001628280-21-020543 R2: 5,575, 1,528 -> 4,047 | WRONG FLAG |
| 6M 2021 | 3,067 | 0000064040-21-000155 R2: 4,122, 1,060 | 0000064040-22-000143 R2: 4,122, 1,055 -> 3,067 | WRONG FLAG |
| FY 2022 | 7,428 | 0000064040-23-000058 R3: 11,181, 3,766 | 0000064040-24-000071 R3: 11,181, 3,753 -> 7,428 | WRONG FLAG |
| Q1 2024 | 2,380 | 0000064040-24-000125 R2: 3,491, 1,120 | 0000064040-25-000126 R2: 3,491, 1,111 -> 2,380 | WRONG FLAG |
| 9M 2024 | 7,362 | 0000064040-24-000178 R2: 10,616, 3,277 | 0000064040-25-000167 R2: 10,616, 3,254 -> 7,362 | WRONG FLAG |
Separate open question (not this rule): SPGI presents expenses by nature, so "gross profit" = revenue - operating-related expenses is our construction, not a face line.

### liabilities_nci_treatment, EL + ILMN (frame 27)
| Cell | Stored | Face: assets / total equity / redeemable NCI -> liabilities | Suite expected | Flag | Expected value |
|---|---|---|---|---|---|
| EL 2017-06-30 | 7,202 | 0001104659-17-053604 R4: 11,568 / 4,402 / - -> 7,166 | 7,166 | RIGHT | right |
| EL 2017-12-31 | 8,063 | 0001104659-18-006059 R4: 12,604 / 4,589 -> 8,015 | 8,015 | RIGHT | right |
| EL 2018-03-31 | 8,087 | 0001104659-18-029710 R4: 12,772 / 4,737 -> 8,035 | 8,035 | RIGHT | right |
| EL 2022-06-30 | 16,162 | 0001001250-22-000122 R5: 20,910 / 5,590 / 842 -> 14,478 | 14,478 | RIGHT | right |
| EL 2022-09-30 | 15,280 | 0001001250-22-000182 R4: 19,989 / 5,517 / 808 -> 13,664 | 13,664 | RIGHT | right |
| EL 2022-12-31 | 15,648 | 0001001250-23-000010 R4: 20,731 / 5,902 / 819 -> 14,010 | 14,010 | RIGHT | right |
| EL 2023-12-31 | 18,421 | 0001001250-24-000007 R4: 23,283 / 5,712 / 850 -> 16,721 | 16,721 | RIGHT | right |
| ILMN 2016-07-03 | 2,013,460K | 0001110803-16-000203 R2: 3,985,090 / 2,139,912 / 33,733 -> 1,811,445 | 1,845,178 | RIGHT | off by redeemable NCI |
| ILMN 2018-09-30 | 3,347 | 0001110803-18-000031 R2: 6,759 / 3,594 / 218 -> 2,947 | 3,165 | RIGHT | off by redeemable NCI |
| ILMN 2019-03-31 | 3,490 | 0001110803-19-000022 R2: 7,390 / 4,070 / 37 -> 3,283 | 3,320 | RIGHT | off by redeemable NCI |

### reit_calculated_subtotal, DOC (frame 115): face rows are only "Total revenues" and "Total costs and expenses"
| Cell | Stored | Built from | Statement | Flag |
|---|---|---|---|---|
| GP FY2016 | 1,390.9M | Revenues - CostOfGoodsAndServicesSold (2017 and 2019 filings) | 0001628280-19-001407 R4 | RIGHT |
| GP 9M 2019 | -113.5M | RCFC 517.5 - 631.0 | 0001628280-19-012968 R4 | RIGHT |
| GP Q3 2020 | 240.4M | Revenues 423.6 - 183.1 | 0001628280-22-002117 R5 | RIGHT |
| GP 6M 2023 | -187.7M | RCFC 257.3 - 444.9 | 0001628280-23-026103 R4 | RIGHT |
| GP 6M 2025 | -251.5M | RCFC 297.8 - 549.3 | 0001628280-25-036063 R4 | RIGHT |
| OI Q3 2015 | 484.4M | Revenues 658.0 - OperatingExpenses 173.5 | 0001558370-16-003110 R4 | RIGHT |
| OI Q1 2017 | 333.1M | 492.2 - 159.1 | 0001558370-17-003225 R4 | RIGHT |
| OI 6M 2019 | -461.4M | RCFC 304.5 - 382.9 x2 | 0001628280-19-009779 R4 | RIGHT |
| OI 9M 2022 | -915.9M | RCFC 369.1 - 642.5 x2 | 0001628280-22-027830 R4 | RIGHT |
| OI Q2 2023 | -313.5M | RCFC 130.2 - 221.8 x2 | 0001628280-23-026103 R4 | RIGHT |

### negative_on_nonnegative_concept, LMT operating_expenses (frame 54): stored = minus "Other income, net"
| Cell | Stored | Face | Flag |
|---|---|---|---|
| Q1 2016 | -63M | other (expense) income, net 63 | RIGHT |
| Q2 2016 | -145M | not read (FY structure GP -> other income -> OP, 0000936468-18-000013 R2) | RIGHT |
| Q4 2017 | -973M | derived; FY2017 other income 373 (0000936468-18-000013 R2) | RIGHT |
| Q1 2018 | -67M | 0000936468-18-000023 R2: GP 1,658, OP 1,725, other 67 | RIGHT |
| 6M 2019 | -110M | 0000936468-19-000058 R2: 4,181 / 4,291 / 110 | RIGHT |
| Q3 2019 | -42M | 0000936468-19-000069 R2: 2,063 / 2,105 / 42 | RIGHT |
| 9M 2022 | -70M | 0000936468-22-000120 R2: 5,985 / 6,055 / 70 | RIGHT |
| Q2 2023 | -45M | 0000936468-23-000099 R2: 2,090 / 2,135 / 45 | RIGHT |
| FY 2024 | -83M | 0000936468-25-000009 R3: 6,930 / 7,013 / 83 | RIGHT |
| 6M 2025 | -63M | 0001628280-25-035565 R2: 3,057 / 3,120 / 63 | RIGHT |

### debt_isolated_dip (frame 12): stored = current portion only
| Cell | Stored | Face (current; long-term) | Flag |
|---|---|---|---|
| BAX 2018-09-30 | 3M | 0001564590-18-026904 R5: 3; 3,485 | RIGHT |
| BAX 2019-09-30 | 2M | 0001628280-20-003692 R2: 0 + 2; 5,063 | RIGHT |
| BAX 2022-03-31 | 409M | 0001628280-22-010922 R2: 200 + 209; 16,765 | RIGHT |
| BAX 2022-06-30 | 408M | 0001628280-22-019640 R2: 200 + 208; 16,278 | RIGHT |
| BAX 2025-06-30 | 8M | 0001628280-25-037877 R2: 6 + 2; 9,492 | RIGHT |
| MO 2015-12-31 | 4M | 0000764180-16-000128 R2: 4; 12,915 | RIGHT |
| EL 2015-06-30 | 29.8M | 0001104659-15-061122 R4: 29.8; 1,607.5 | RIGHT |
| VLO 2015-12-31 | 127M | 0001035002-16-000069 R2: 127; 7,250 | RIGHT |
| ALLE 2015-12-31 | 65.6M | 0001579241-16-000056 R3: 65.6; 1,479.8 | RIGHT |
| NEM 2017-12-31 | 4M | 0001558370-18-000894 R7: 4; 4,061 | RIGHT |

### share_basis_mismatch, new in round 3 (frame 70; all 10 sampled cells ODFL, a training company): as filed, true = /3 (pre-2020) or /2 (2020-2024)
| Cell | Stored | As filed (R4 of) | Suite expected | Flag |
|---|---|---|---|---|
| basic EPS Q2 2015 | 0.50 | 1.00 (0000878927-15-000035) | 0.333 | RIGHT |
| basic EPS Q4 2016 | 0.415 | 0.83 (0000878927-17-000005, row not rendered) | 0.277 | RIGHT (as-filed DATA-INFERRED) |
| basic EPS Q3 2017 | 0.62 | 1.24 (0000878927-17-000035) | 0.413 | RIGHT |
| basic EPS Q4 2017 | 1.20 | 2.40 (0000878927-18-000005, row not rendered; 2.40 in 0001564590-19-004755 R45) | 0.800 | RIGHT |
| basic EPS 6M 2018 | 1.66 | 3.32 (0000878927-18-000042) | 1.107 | RIGHT |
| diluted EPS Q2 2015 | 0.50 | 1.00 (0000878927-15-000035) | 0.333 | RIGHT |
| diluted EPS 9M 2016 | 1.365 | 2.73 (0000878927-16-000089) | 0.910 | RIGHT |
| diluted EPS Q3 2017 | 0.62 | 1.24 (0000878927-17-000035) | 0.413 | RIGHT |
| diluted EPS FY2019 | 5.10 | 5.10 filed 2022 (0001564590-22-006303), after the 1.5 split | 2.55 | RIGHT |
| DPS Q3 2018 | 0.065 | 0.13 (0000878927-18-000054) | 0.043 | RIGHT |


## 8. Task 2 verdicts (fresh shards)
### P flagged
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | INCY | shares_outstanding 2020-03-31 (share_basis_mismatch, expects x0.8) | 216,952,325 | as filed 216,952,325; INCY never split: the 2024 drop is a self-tender (SC TO-I 0001104659-24-060326); suite inferred a 1.25 split | REFUTED | FILING-CHECKED | INCY 10-Q 0001558370-20-005185 R3; SC TO-I 0001104659-24-060326; cover 196,322,703 in 10-Q 0000879169-25-000118 R1 |
| 1 | NRG | effective_tax_rate_reported Q4 2021 | -0.787 (derived) | Q4 = (672-840)/(2,859-3,454) = -168/-595 = 28.2% | CONFIRMED | FILING-CHECKED | NRG 10-K 0001013871-22-000010 R3; 10-Q 0001013871-21-000022 R2 |
| 2 | DAL | basic_eps Q4 2021 | -0.63 (derived) | loss per share $0.64 | CONFIRMED | FILING-CHECKED | DAL 8-K 0001683168-22-000238 delta_ex9901.htm |
| 3 | PAG | basic_eps Q4 2019 | 1.25 (derived) | 1.25 reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | PAG 8-K 0001019849-20-000002 Ex.99.1 |
| 4 | TER | diluted_eps Q4 2023 | 0.72 (derived) | 0.72 reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | TER 8-K 0000950170-24-009126 ter-ex99_1.htm EPS table |
| 5 | XPO | total_liabilities 2019-03-31 (liabilities_nci_treatment) | 12,153M | 14,196 - total equity 2,833 = 11,363 (= suite expected) | CONFIRMED | FILING-CHECKED | XPO 10-Q 0001166003-19-000030 R2 |
| 6 | PAG | cost_of_revenue Q3 2025 (stale_quarter_basis) | 6,446.2M | 'Total cost of sales' 6,446.2 for Q3 2025 in its own 10-Q; the named cell is right (inconsistency, if any, sits in Q1/Q2) | REFUTED (named cell right) | FILING-CHECKED | PAG 10-Q 0001628280-25-047533 R4 |
| 7 | NBIX | cost_of_revenue FY2017 (statement_role_suspect) | 1,254,000 | 'Cost of sales' $1,254K (launch year) | REFUTED | FILING-CHECKED | NBIX 10-K 0001564590-19-002328 R4 |
| 8 | F | sbc Q4 2018 (negative, derived) | -8,000,000 | FY 191 (10-K R6); 9M input not located on the 10-Q cash-flow face | NOT-VERIFIED | - | F 10-K 0000037996-19-000012 R6; 10-Q 0000037996-18-000084 R6 |
| 9 | DOCU | diluted_eps Q1 FY2018 (share_basis_mismatch, expects /4) | -0.66 | (0.66) as filed; DOCU has never split (no split-ratio facts; cover counts rise smoothly 156.6M -> 194.8M 2018-21); the step is the IPO preferred conversion | REFUTED | FILING-CHECKED (EPS) / no-split via SEC companyconcept | DOCU 10-Q 0001261333-18-000009 R4 |
| 10 | USFD | basic_eps Q4 2022 | 0.38 (derived) | 0.37 reported | CONFIRMED | FILING-CHECKED | USFD 8-K 0001665918-23-000021 usfd12312022ex991.htm |
| 11 | STE | dividends_per_share FY2020 (share_basis_mismatch, expects x0.8) | 1.45 | 1.45 declared as filed; STE never split (no split-ratio facts; cover 85.3M -> 99.8M in 2021 = Cantel acquisition shares) | REFUTED | FILING-CHECKED | STE 10-K 0001757898-20-000012 R4 |
| 12 | F | diluted_eps Q4 2025 | -2.77 (derived) | (2.77) reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | F 8-K 0000037996-26-000014 Ex.99 EPS reconciliation |
| 13 | TRMB | effective_tax_rate_reported Q4 2015 | -0.46 (derived) | Q4 = (31.1-26.7)/(151.8-123.5) = 4.4/28.3 = 15.5% | CONFIRMED | FILING-CHECKED | TRMB 10-K 0000864749-16-000092 R4; 10-Q 0000864749-15-000061 R4 |
| 14 | HAS | effective_tax_rate_reported Q2 2023 | 0.003 (derived) | Q2 tax 7.0 on pretax (227.9) = -3.1% | CONFIRMED | FILING-CHECKED | HAS 10-Q 0000046080-23-000083 R4 |
| 15 | DINO | effective_tax_rate_reported Q4 2024 | -0.628 (derived) | Q4 = (34-235.0)/(218-1,060.1) = -201/-842 = 23.9% | CONFIRMED | FILING-CHECKED | DINO 10-K 0001915657-25-000019 R5; 10-Q 0001915657-24-000123 R4 |
| 16 | HALO | total_debt 2019-09-30 (debt_below_component) | 9,308K | current portion 54,537 + long-term 9,308 = 63,845K | CONFIRMED | FILING-CHECKED | HALO 10-Q 0001159036-19-000060 R2 |
| 17 | OHI | operating_income Q3 2022 (reit_calculated_subtotal) | 61.76M | Total revenues 239,430 - Total expenses 177,670 (both face totals); face then adds other income to 'Income before income tax' 102,138 | DEFINITION-QUESTION (not counted wrong) | FILING-CHECKED | OHI 10-Q 0000888491-22-000029 R4 |
| 18 | TER | dividends_per_share Q4 2015 (share_basis_mismatch, expects x2) | 0.06 | 0.06 declared as filed; TER never split (no split-ratio facts; cover 217.8M 2015 -> 202.3M 2016) | REFUTED | FILING-CHECKED | TER 10-K 0001193125-16-484381 R4 |
| 19 | PYPL | basic_eps Q4 2021 | 0.67 (derived) | 0.68 reported | CONFIRMED | FILING-CHECKED | PYPL 8-K 0001633917-22-000021 q4-fyx21xpaypalxearnings.htm |
| 20 | HALO | basic_eps Q4 2021 | 0.49 (derived) | 0.48 reported | CONFIRMED | FILING-CHECKED | HALO 8-K 0001159036-22-000012 ex991q420218-k.htm |
| 21 | INCY | basic_eps Q4 2021 | 2.56 (derived) | GAAP basic EPS 2.55. (The FY2021 4.30 cell also carries a false share_basis flag, expected x1.25) | CONFIRMED | FILING-CHECKED | INCY 8-K 0001558370-22-000883 Ex.99.1 |
| 22 | VEEV | effective_tax_rate_reported Q4 FY2026 | -0.487 (derived) | Q4 = (285.6-212.3)/(1,194.5-877.0) = 23.1% | CONFIRMED | FILING-CHECKED (facts of 10-K 0001393052-26-000014 and 10-Q 0001393052-25-000078 via SEC companyconcept) | VEEV 10-K 0001393052-26-000014; 10-Q 0001393052-25-000078 |
| 23 | NBIX | diluted_eps Q4 2022 | 0.91 (derived) | 0.88 reported | CONFIRMED | FILING-CHECKED | NBIX 8-K 0000914475-23-000005 q4-2022 earnings release |
| 24 | EW | shares_outstanding 2019-07-23 | 207,969,219 | cover as filed; 3-for-1 split 2020-05-07 -> 623,907,657 | CONFIRMED(policy: re-base) | FILING-CHECKED | EW 10-Q 0001099800-19-000019 R1; split ratio 3 in 10-Q 0001099800-20-000019 |
| 25 | SWK | total_liabilities 2015-04-04 (liabilities_nci_treatment) | 10,410.5M | 15,943.7 - total shareowners' equity 5,697.2 = 10,246.5 (= expected) | CONFIRMED | FILING-CHECKED | SWK 10-Q 0000093556-15-000013 R3 |
| 26 | VST | diluted_eps Q4 2017 | -1.35 (derived) | release located has FY table only | NOT-VERIFIED | - | VST 8-K 0001193125-18-057237 |
| 27 | FIX | total_debt 2017-03-31 (debt_isolated_dip) | 1,805K | face debt lines are only current maturities 1,112 + long-term 693 = 1,805K; the dip is real | REFUTED | FILING-CHECKED | FIX 10-Q 0001558370-17-002931 R2 |
| 28 | VST | effective_tax_rate_reported Q4 2019 | -0.596 (derived) | Q4 = (290-270)/(1,216-962) = 20/254 = 7.9% | CONFIRMED | FILING-CHECKED | VST 10-Q 0001692819-19-000018 R2; 10-K 0001692819-20-000005 (facts via SEC companyconcept) |
| 29 | STE | diluted_eps Q4 FY2025 | 1.48 (derived) | 1.48 per diluted share (continuing ops) reported | VALUE-CORRECT (policy-only) | FILING-CHECKED | STE 8-K 0001757898-25-000004 ste03312025ex991.htm |

### P passed
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | SWK | share_buybacks Q1 2018 | 11.4M | (11.4) purchase of common stock for treasury | RIGHT | FILING-CHECKED | SWK 10-Q 0000093556-18-000016 R5 |
| 1 | VST | accounts_receivable 2023-03-31 | 1,464M | 1,464 | RIGHT | FILING-CHECKED | VST 10-Q 0001628280-23-016662 R6 |
| 2 | GWRE | sbc 6M FY2023 | 71,275K | 71,275 | RIGHT (Q2 derived copy not verified) | FILING-CHECKED | GWRE 10-Q 0001528396-23-000017 R7 |
| 3 | TER | accounts_payable 2015-04-05 | 59,831K | 59,831 | RIGHT | FILING-CHECKED | TER 10-Q 0001193125-15-179303 R2 |
| 4 | DAL | diluted_eps Q1 2021 | -1.85 | (1.85) | RIGHT | FILING-CHECKED | DAL 10-Q 0000027904-21-000006 R4 |
| 5 | INCY | operating_income FY2019 | 402,006K | 402,006 | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | INCY 10-K 0001558370-20-000774 R4 |
| 6 | HUM | net_income Q2 2025 | 545M | 545 attributable | RIGHT | FILING-CHECKED | HUM 10-Q 0000049071-25-000042 R4 |
| 7 | PYPL | current_assets 2023-12-31 | 62,569M | 62,569 | RIGHT | FILING-CHECKED | PYPL 10-K 0001633917-24-000024 R3 |
| 8 | STE | ppe_net 2026-06-30 | 2,171,700K | 2,171,700 | RIGHT | FILING-CHECKED | STE 10-Q 0001628280-26-054830 R2 |
| 9 | STZ | other_income_expense_net Q2 FY2016 | -77.3M | the only non-operating face line is interest expense (77.3), tagged InterestIncomeExpenseNonoperatingNet | RIGHT (perimeter = filer's only non-operating line) | FILING-CHECKED | STZ 10-Q 0000016918-15-000044 R4 |
| 10 | RBRK | cost_of_revenue Q2 FY2025 | 55,168K | total cost of revenue 55,168 | RIGHT | FILING-CHECKED | RBRK 10-Q 0001943896-24-000018 R4 |
| 11 | SWK | basic_eps Q3 2021 | 2.60 | 2.60 (my reader first misaligned it) | RIGHT | FILING-CHECKED | SWK 10-K 0000093556-22-000006 R2 |
| 12 | TRMB | cash_flow_investing Q1 2018 | -353.5M | (353.5) | RIGHT | FILING-CHECKED | TRMB 10-Q 0000864749-18-000067 cash-flow R page |
| 13 | STE | net_income Q1 FY2025 | 145.5M | 145,500K | RIGHT | FILING-CHECKED | STE 10-Q 0001757898-25-000008 R4 |
| 14 | VEEV | operating_income FY2015 | 69,966K | 69,966 | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | VEEV 10-K 0001564590-15-002300 R4 |
| 15 | USFD | accounts_receivable 2024-03-30 | 1,966M | 1,966 | RIGHT | FILING-CHECKED | USFD 10-Q 0001665918-24-000101 R2 |
| 16 | OHI | diluted_eps FY2018 | 1.40 | 1.40 | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | OHI 10-K 0000888491-19-000006 R4 |
| 17 | DOCU | cost_of_revenue Q2 FY2018 | 28,458K | total cost of revenue 28,458 | RIGHT | FILING-CHECKED | DOCU 10-Q 0001261333-18-000017 R4 |
| 18 | NRG | net_income 9M 2019 | 1,055M | 1,055 attributable | RIGHT | FILING-CHECKED | NRG 10-Q 0001013871-19-000035 R2 |
| 19 | TRMB | operating_income Q1 2021 | 140.9M | 140.9 | RIGHT | FILING-CHECKED | TRMB 10-Q 0000864749-21-000050 R4 |
| 20 | EW | comprehensive_income 6M 2020 | 198.6M | 198.6 | RIGHT | FILING-CHECKED | EW 10-Q 0001099800-20-000019 R5 |
| 21 | HUM | sga_expense FY2017 | 6,567M | insurer face line 'Operating costs' 6,567 | RIGHT (perimeter: insurer operating costs as SG&A) | FILING-CHECKED | HUM 10-K 0000049071-18-000014 R4 |
| 22 | DAL | dividends_paid Q1 2020 | 260M | (260) | RIGHT | FILING-CHECKED | DAL 10-Q 0000027904-20-000007 R5 |
| 23 | PYPL | operating_expenses Q2 2024 | 6,560M | total operating expenses 6,560 | RIGHT | FILING-CHECKED | PYPL 10-Q 0001633917-24-000098 R4 |
| 24 | AZO | cost_of_revenue 6M FY2026 | 4,300,055K | 4,300,055 | RIGHT | FILING-CHECKED | AZO 10-Q 0001104659-26-032757 R4 |
| 25 | TER | net_income Q2 2017 | 174,976K | 174,976 | RIGHT | FILING-CHECKED | TER 10-Q 0001193125-17-255654 R5 |
| 26 | NBIX | sga_expense Q3 2024 | 234.3M | 234.3 | RIGHT | FILING-CHECKED | NBIX 10-Q 0000914475-24-000211 R4 |
| 27 | DINO | cf_ar_change Q1 2022 | +419,609K | prints (419,609) on the cash-flow row (an AR increase); stored sign is the fact's sign | RIGHT | FILING-CHECKED | DINO 10-Q 0001915657-22-000011 R6 |
| 28 | OHI | revenue Q1 2021 | 273,768K | total revenues 273,768 | RIGHT | FILING-CHECKED | OHI 10-K 0000888491-22-000015 R4 |
| 29 | HAS | current_assets 2024-09-29 | 3,021.6M | 3,021.6 | RIGHT | FILING-CHECKED | HAS 10-Q 0000046080-24-000167 R2 |

### K flagged
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | PYPL | interest_expense Q1 2024 (stale_displayed_value) | 86M | rendered row not located; staleness not opened | NOT-VERIFIED | - | PYPL 10-Q 0001633917-24-000048 |
| 1 | OHI | net_income Q1 2016 (quarters_do_not_sum_to_year, review) | 55,555K | 'Net income available to common stockholders' 55,555 (10-Q/A); tile gap is elsewhere | VALUE-RIGHT | FILING-CHECKED | OHI 10-Q/A 0001571049-17-007314 R4 |
| 2 | XPO | operating_income 9M 2020 (non_authoritative_source) | 75M | 75 in the FY2021 10-Q comparative (re-presented after the GXO spin) | VALUE-RIGHT as re-presented | FILING-CHECKED | XPO 10-Q 0001166003-21-000099 R4 |
| 3 | EW | diluted_eps 6M 2019 (non_authoritative_source) | 0.77 | 0.77 post-split comparative (2.32 / 3) | VALUE-RIGHT | FILING-CHECKED | EW 10-Q 0001099800-20-000019 R4 |
| 4 | VEEV | operating_expenses FY2017 (quarters_vs_year_basis_mix) | 256,173K | GP 376,861 - OI 120,688 in FY2018 10-K | VALUE-RIGHT, basis mix real | FILING-CHECKED | VEEV 10-K 0001564590-19-009853 R4 |
| 5 | STZ | total_assets 2015-02-28 (non_periodic_form) | 15,144.5M | original 10-Q comparatives 15,144.5; later 10-Ks and the 8-K re-present 15,093.0 (debt-issuance-cost reclass); the stored value is the superseded vintage | VALUE-WRONG (superseded vintage under latest-filed rule) | FILING-CHECKED (values via our source facts of named filings; face not rendered) | STZ 10-K 0000016918-16-000075; 10-Q 0000016918-15-000033 |
| 6 | HALO | total_liabilities 2018-09-30 (non_authoritative_source) | 204,769K | 444,507 - 239,738 | VALUE-RIGHT | DATA-INFERRED (face not rendered) | HALO 10-Q 0001159036-18-000043 |
| 7 | DINO | dividends_paid FY2019 (recast_8k_lineage) | 225.17M | (225,170,000) in HollyFrontier recast 8-K | VALUE-RIGHT as recast | FILING-CHECKED | DINO 8-K 0001915657-22-000073 R6 |
| 8 | SWK | total_liabilities 2021-04-03 (value_not_in_sources) | 12,477.2M | 23,876.0 - total equity 11,404.8 = 12,471.2; stored adds NCI 3.0 instead of subtracting (liabilities_nci_treatment did not fire: under its tolerance) | VALUE-WRONG (6M, 0.05%) | FILING-CHECKED | SWK 10-Q 0000093556-21-000015 R3 |
| 9 | NBIX | interest_expense FY2023 (stale_displayed_value) | 4.6M | (4.6) correct; staleness not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | NBIX 10-K 0000914475-24-000054 R5 |
| 10 | HAS | dividends_per_share Q4 2024 (per_share_derived, review) | 0.0 (derived) | FY declared 2.10 (10-K R5); 9M declared not opened | NOT-VERIFIED | - | HAS 10-K 0000046080-25-000027 R5 |
| 11 | NRG | capex 6M 2018 (non_authoritative_source) | 282M | (282) | VALUE-RIGHT | FILING-CHECKED | NRG 10-Q 0001013871-19-000028 R6 |
| 12 | DINO | dividends_per_share Q4 2022 (per_share_derived, review) | 0.40 (derived) | FY 1.20 (10-K R9); 9M not opened | NOT-VERIFIED | - | DINO 10-K 0001915657-23-000015 R9 |
| 13 | GWRE | operating_expenses 6M FY2022 (non_authoritative_source) | 275,419K | FY2023 10-Q comparative: revenue 370,567, COGS 199,982 (recast; original 211,163), OI (104,834) -> 275,419 from one filing | VALUE-RIGHT (single later vintage) | FILING-CHECKED | GWRE 10-Q 0001528396-23-000017 R4; 10-Q 0001528396-22-000021 R4 |
| 14 | VEEV | depreciation_and_amortization FY2020 (stale_displayed_value) | 19,859K | 19,859 correct; staleness not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | VEEV 10-K 0001628280-20-004385 R7 |
| 15 | F | dividends_per_share Q4 2018 (per_share_derived, review) | 0.15 (derived) | FY row not rendered | NOT-VERIFIED | - | F 10-K 0000037996-19-000012 |
| 16 | XPO | total_liabilities 2020-06-30 (value_not_in_sources; also P liabilities_nci_treatment) | 13,307M | 15,641 - total equity (2,484 + 150) = 13,007 | VALUE-WRONG (also P-flagged) | FILING-CHECKED (assets on face; equity from source facts) | XPO 10-Q 0001166003-20-000047 R2 |
| 17 | NRG | operating_income FY2017 (recast_8k_lineage) | -741M | (741) in recast 8-K | VALUE-RIGHT as recast | FILING-CHECKED | NRG 8-K 0001013871-20-000027 R2 |
| 18 | TRMB | basic_eps FY2017 (non_authoritative_source) | 0.47 | 0.47 | VALUE-RIGHT | FILING-CHECKED | TRMB 10-K 0000864749-20-000029 R4 |
| 19 | GWRE | cash_flow_financing Q4 FY2023 (neighbour_magnitude) | -47,813K (derived) | FY (261,579) - 9M (213,766) = (47,813); neighbours are just small | VALUE-RIGHT, FLAG REFUTED | FILING-CHECKED | GWRE 10-K 0001528396-23-000089 R8; 10-Q 0001528396-23-000061 R7 |
| 20 | STE | interest_expense Q1 FY2025 (stale_displayed_value) | 30,384K | 30,384 correct; staleness not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | STE 10-Q 0001757898-24-000016 R4 |
| 21 | HAS | interest_expense FY2015 (non_authoritative_source) | 97,122K | 97,122 | VALUE-RIGHT | FILING-CHECKED | HAS 10-K 0001193125-18-058659 R4 |
| 22 | RBRK | total_debt_split 2025-04-30 (stale_displayed_value) | 322,821K | debt, noncurrent 322,821; staleness not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | RBRK 10-Q 0001943896-25-000030 R2 |
| 23 | USFD | operating_expenses Q4 2023 (quarter_equals_adjacent_quarter) | 1,312M (derived) | FY 5,131 - 9M 3,819 = 1,312; Q3 is also 1,312 (coincidence) | VALUE-RIGHT, FLAG REFUTED | FILING-CHECKED | USFD 10-K 0001665918-24-000014 R5; 10-Q 0001665918-23-000144 R4 |
| 24 | INCY | interest_expense Q1 2024 (stale_displayed_value) | 430K | (430) correct; staleness not opened | VALUE-RIGHT; staleness DATA-INFERRED | FILING-CHECKED (value) | INCY 10-Q 0000879169-24-000077 R4 |
| 25 | DOCU | shares_outstanding 2018-04-30 (share_jump_without_split, review) | 36,775,658 | as filed 36,775,658; the jump to 156.6M is the IPO preferred conversion, not a split (review right; the P share_basis_mismatch on it is wrong) | VALUE-RIGHT (review condition real) | FILING-CHECKED | DOCU 10-Q 0001261333-18-000009 R3 |
| 26 | OHI | cash_and_equivalents 2018-12-31 (cash_roll_forward) | 10,300K | 10,300 on the face; roll-forward gap is restricted cash | VALUE-RIGHT, FLAG REFUTED | FILING-CHECKED | OHI 10-K 0000888491-19-000006 R2 |
| 27 | STE | diluted_eps Q4 FY2020 (non_periodic_form) | 1.44 | 1.44 in the 10-K too (8-K copy identical) | VALUE-RIGHT | FILING-CHECKED (via the 10-K copy in our source facts) | STE 10-K 0001757898-20-000012 |
| 28 | SWK | revenue Q1 2017 (quarters_do_not_sum_to_year, review) | 3,209.3M | Q1 2017 net sales 2,805.6 as filed; 3,209.3 is the Q1 2019 figure carried on a 2017 context in the FY2019 10-K (label shift) | VALUE-WRONG | FILING-CHECKED | SWK 10-Q 0000093556-17-000011 R2; source 10-K 0000093556-20-000006 |
| 29 | AZO | share_buybacks 1998-01-01..2015-05-09 (non_authoritative_source) | 14,872M | cumulative program-to-date repurchases over a 6,337-day window shown as a cell; 9M FY2015 is (840,918)K | VALUE-WRONG (not a reporting period) | DATA-INFERRED (cumulative row not rendered) | AZO 10-Q 0001193125-15-225958 R7 |

### K passed
| # | Co | Cell | Stored | Filing says | Verdict | Evidence | Locator |
|---|---|---|---|---|---|---|---|
| 0 | HALO | comprehensive_income Q1 2018 | -27,881K | (27,881) | RIGHT | FILING-CHECKED | HALO 10-Q 0001159036-18-000031 R5 |
| 1 | INCY | depreciation_and_amortization 6M 2022 | 32,945K | 32,945 | RIGHT (Q2 derived copy not verified) | FILING-CHECKED | INCY 10-Q 0001558370-22-011631 R8 |
| 2 | PAG | comprehensive_income FY2021 | 1,179.6M | 1,179.6 attributable | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | PAG 10-K 0001019849-22-000013 R6 |
| 3 | PYPL | cash_flow_investing 6M 2017 | -2,972M | (2,972) | RIGHT | FILING-CHECKED | PYPL 10-Q 0001633917-18-000171 R6 |
| 4 | FIX | goodwill 2023-06-30 | 637,487K | 637,487 | RIGHT | FILING-CHECKED | FIX 10-Q 0001558370-23-012288 R2 |
| 5 | STZ | stockholders_equity 2023-02-28 | 8,413.6M | total CBI stockholders' equity 8,413.6 | RIGHT | FILING-CHECKED | STZ 10-K 0000016918-23-000045 R3 |
| 6 | AZO | total_debt 2023-08-26 | 7,709.6M | DebtLongtermAndShorttermCombinedAmount row not rendered in 40 R pages | NOT-VERIFIED | - | AZO 10-K 0001558370-23-016668 |
| 7 | SWK | income_before_tax Q1 2021 | 573.3M | 573.3 (continuing ops) | RIGHT | FILING-CHECKED | SWK 10-K 0000093556-22-000021 R2 |
| 8 | DOCU | depreciation_and_amortization Q1 FY2024 | 22,867K | row not rendered | NOT-VERIFIED | - | DOCU 10-Q 0001261333-23-000070 |
| 9 | TRMB | operating_expenses Q3 2021 | 357.0M | total operating expense 357.0 | RIGHT | FILING-CHECKED | TRMB 10-Q 0000864749-21-000137 R4 |
| 10 | USFD | operating_expenses Q2 2025 | 1,405M | 1,405 | RIGHT | FILING-CHECKED | USFD 10-Q 0001665918-25-000127 R4 |
| 11 | NRG | depreciation_and_amortization Q1 2022 | 183M | 183 | RIGHT | FILING-CHECKED | NRG 10-Q 0001013871-22-000016 R2 |
| 12 | XPO | diluted_eps FY2022 | 5.76 | 5.76 | RIGHT (Q4 derived copy -0.81 not verified) | FILING-CHECKED | XPO 10-K 0001166003-23-000017 R5 |
| 13 | USFD | diluted_eps Q3 2023 | 0.38 | 0.38 | RIGHT | FILING-CHECKED | USFD 10-Q 0001665918-23-000144 R4 |
| 14 | TER | dividends_paid FY2022 | 69,711K | (69,711) | RIGHT (Q4 derived copy not verified) | FILING-CHECKED | TER 10-K 0001193125-23-044711 R9 |
| 15 | HAS | sga_expense Q1 2026 | 259.1M | selling, distribution and administration 259.1 | RIGHT | FILING-CHECKED | HAS 10-Q 0000046080-26-000026 R4 |
| 16 | TER | ppe_net 2020-09-27 | 386,170K | 386,170 | RIGHT | FILING-CHECKED | TER 10-Q 0001193125-20-283796 R2 |
| 17 | PAG | total_debt_split 2020-12-31 | 1,689.6M | 87.5 + 1,602.1 (floor-plan notes payable excluded: perimeter) | RIGHT under the borrowings-only perimeter | FILING-CHECKED | PAG 10-K 0001558370-21-001299 R2 |
| 18 | STZ | goodwill 2019-05-31 | 7,756.0M | 7,756.0 | RIGHT | FILING-CHECKED | STZ 10-Q 0000016918-19-000056 R2 |
| 19 | HUM | current_liabilities 2018-06-30 | 18,768M | 18,768 | RIGHT | FILING-CHECKED | HUM 10-Q 0000049071-18-000100 R2 |
| 20 | FIX | operating_income Q2 2016 | 28,615K | 28,615 | RIGHT | FILING-CHECKED | FIX 10-Q 0001558370-16-006894 R4 |
| 21 | OHI | public_float 2018-06-30 | 6,210,297,921 | cover 6,210,297,921 | RIGHT | FILING-CHECKED | OHI 10-K 0000888491-19-000006 R1 |
| 22 | HAS | cash_and_equivalents 2019-09-29 | 1,060,432K | 1,060,432 | RIGHT | FILING-CHECKED | HAS 10-Q 0000046080-19-000112 R2 |
| 23 | DOCU | capex 9M FY2024 | 70,277K | row not rendered | NOT-VERIFIED | - | DOCU 10-Q 0001261333-23-000103 |
| 24 | INCY | cf_ap_change 6M 2017 | -6,506K | (6,506) | RIGHT (Q2 derived copy not verified) | FILING-CHECKED | INCY 10-Q 0001558370-17-005591 R6 |
| 25 | STE | gross_profit 6M FY2025 | 1,151,200K | 1,151,200 | RIGHT | FILING-CHECKED | STE 10-Q 0001628280-25-050160 R4 |
| 26 | AIZ | basic_eps 6M 2020 | 5.35 | 5.35 | RIGHT | FILING-CHECKED | AIZ 10-Q 0001267238-20-000040 R4 |
| 27 | HALO | cost_of_revenue Q1 2019 | 4,649K | cost of product sales 4,649 | RIGHT | FILING-CHECKED | HALO 10-Q 0001159036-19-000027 R4 |
| 28 | EW | other_income_expense_net Q3 2020 | +0.8M | 'Interest income, net' prints (0.8) inside the expense block (negated row); fact is +0.8 income | RIGHT (sign through row negation) | FILING-CHECKED | EW 10-Q 0001099800-20-000024 R4 |
| 29 | AZO | sga_expense Q2 FY2025 | 1,421,634K | 1,421,634 | RIGHT | FILING-CHECKED | AZO 10-Q 0001558370-25-003476 R4 |

## 9. Artifacts (scratchpad, not committed)
`/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/r3/`: `drive3.py`, `heldold.json/.pkl/.txt` (run A), `fresh.json/.pkl/.txt` (run B), `heldold_samples.json`, `fresh_samples.json`, `fresh_verdicts.tsv`, `task1.md`.
