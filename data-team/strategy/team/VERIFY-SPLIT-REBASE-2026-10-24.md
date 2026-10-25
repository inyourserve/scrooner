# Verifier sample: split re-base pass (root fix #2, origin/work/period-engineer/split-rebase @e312dfb), 2026-10-24

Role: Data Verifier. I did not read the Period Engineer's rationale before checking.

**Inputs.** The two per-cell dry-run tables in `doc/data-moat/team/backups/` (4,161 cells at 11 companies):
- `split_rebase_dryrun_cohort11_20261024.csv.gz`;
- `split_rebase_dryrun_cohort11_with_ru1_20261024.csv.gz` (the same cells, with RU-1 applied).

**DB.** One read-only query (20s, 3 pooler/app backends) to get the tag and period of the 525 source facts named by the sampled cells.

**SEC.** `SEC_USER_AGENT` only, at most 4 req/s through the shared limiter, one process; downloads deleted afterwards.

**Evidence: FILING-CHECKED.** For every sampled cell, every candidate filing's own XBRL instance was read: the tag, an undimensioned context with the exact start/end, and its value. Named cells were also read on the rendered R page. Then I checked that the shown value = the filed value ÷ the split factor (× for share counts), where the factor is the product of the splits effective after that filing's filing date.

**Verdict: GATE PASSES.**
- **0 wrong shown values** among 194 checked shown cells: classes 1-4, 6, 8, 9 and the named cells.
- Every detected split event is real.
- RU-1's "not filed separately" is honest in 30 of 30 sampled cells.
- **18 false holds**, all hidden with the reason "restated between filings" although the conflicting copy is a filer label error and the value was right. 16 are AMZN 2011-12, which is pre-2015; 2 are NVDA 6M FY2018. Plus definition notes below.

## Sample (seed `random.Random('20261024-splitrebase')`; frames from the with-RU-1 table)
| Class | Frame | Checked | Right | Wrong |
|---|---|---|---|---|
| 1 was_unadjusted -> new | 520 | 30 | 30 | 0 |
| 2 was_double_divided (GOOG pre-2022, ODFL) | 76 | 30 | 30 | 0 |
| 3 share_count_rebased | 548 | 30 | 30 | 0 |
| 4 rounding_only | 100 | 30 | 30 | 0 |
| 6 new_value | 22 | 22 (all) | 22 | 0 |
| 8 unchanged (control) | 2,627 | 20 | 20 | 0 |
| 9 other_changed | 2 | 2 (all) | 2 | 0 |
| Named cells | - | 15 | 15 | 0 |
| 5 hidden (restated 59 + NVDA DPS label error 1) | 60 | 60 (all) | 42 holds correct | **18 false holds** |
| 7 RU-1 derived-only removed (2015+) | 156 | 30 | 30 "not filed separately" honest | 0 |

## Split events (all FILING-CHECKED, `StockholdersEquityNoteStockSplitConversionRatio1` or restated comparatives)
| Company | Events | Evidence |
|---|---|---|
| AAPL | 7:1 2014-06 | 0001193125-14-277160 |
| AAPL | 4:1 2020-08 | 0000320193-20-000096 R8 |
| GOOG | Class C 2:1 dividend 2014-04 | 0001652044-16-000012 |
| GOOG | 20:1 2022-07 | 0001652044-22-000090 (also announced 2022-02, 0001652044-22-000029; counted once) |
| TSLA | 5:1 2020-08 | 0001564590-21-004599 R5 |
| TSLA | 3:1 2022-08 | 0000950170-22-019867, 0000950170-23-001409 R5 |
| ODFL | 3:2 2010 | not in the split table: proven by restated comparatives, 6M-2010 basic EPS 0.78 in 0001193125-10-180556 vs 0.52 in 0001193125-11-215739 |
| ODFL | 3:2 2012-09 | 0000878927-13-000039 |
| ODFL | 3:2 2020-03 | 0001564590-20-021054 R16 |
| ODFL | 2:1 2024 | 0000950170-24-054284 (10-Q Q1 2024) |
| NVDA | 4:1 2021-07 | 0001045810-21-000131, -22-000036 |
| NVDA | 10:1 2024-06 | 0001045810-24-000264 |
| AMZN | 20:1 2022-06 | 0001018724-22-000019 |
| AVGO | 10:1 2024-07 | 0001730168-24-000099 |
| MSFT, META, LLY, MU | none | no split-ratio facts; the pass uses factor 1 |

Factors used by the pass and confirmed per cell: AAPL 28 / 4 / 1; GOOG 40 (pre-2014) / 20; TSLA 15 / 3; ODFL 27/4, 9/2, 3, 2; NVDA 40 / 10; AMZN 20; AVGO 10.

## Named cells
| Cell | Old -> new | Filing | Verdict |
|---|---|---|---|
| AAPL FY2018 diluted EPS | 11.91 -> 2.98 | 10-K 0000320193-20-000096 R2 prints 2.98 (post-split comparative) | right |
| AAPL Q4 FY2018 diluted EPS | 0.7275 (unchanged) | 10-K 0000320193-19-000119 R34: 2.91 / 4 | right |
| GOOG Q2 2022 diluted EPS | 0.0605 -> 1.21 | 10-Q 0001652044-23-000070 R4 (comparative), also 0001652044-22-000071 R4 | right |
| GOOG 6M 2022 diluted EPS | 0.122 -> 2.44 | 0001652044-23-000070 R4 | right |
| TSLA Q1 2015 diluted EPS | -1.22 -> -0.0813 | 10-Q 0001564590-16-018886 R4: (1.22) / 15 | right |
| ODFL FY2015 / FY2016 / FY2017 diluted EPS | 1.785 / 1.78 / 2.815 -> 1.19 / 1.1867 / 1.8767 | 0000878927-18-000005 R4 3.57; 0001564590-19-004755 R4 3.56; 0001564590-20-006626 R4 5.63; all / 3 | right |
| ODFL Q4 2015 / 2016 / 2017 diluted EPS | -> 0.2833 / 0.2767 / 0.7967 | 10-K quarterly notes R46 / R45 / R45: 0.85 / 0.83 / 2.39, / 3 | right |
| LLY Q3 2018 / Q3 2019 DPS | 0.00 -> 0.5625 / 0.645 | 10-K 0000059478-20-000057: `CommonStockDividendsPerShareCashPaid` 0.5625 / 0.6450 (R120) | right as filed. **Definition note:** these are cash-PAID amounts, while LLY's other DPS cells are DECLARED (LLY declares in Q4), so the quarterly series mixes two bases |

## Hidden cells (60)
| Group | Cells | Filings | Verdict |
|---|---|---|---|
| AAPL FY2008, FY2009, Q3 FY2009 EPS | 6 | FY2009 10-K 0001193125-09-214859 vs 10-K/A 0001193125-10-012091 (retrospective revenue-recognition restatement) | hold correct (pre-2015) |
| MSFT FY2016-17 and Q1 FY2016/17 EPS | 12 | e.g. FY2016 basic 2.12 (0001193125-16-662209) vs 2.59 (FY2018 10-K 0001564590-18-019062, ASC 606 full retrospective) | hold correct; reason honest |
| META 2016 interim EPS | 10 | e.g. Q1 2016 basic 0.53 (0001326801-16-000067) vs 0.61 (0001326801-17-000007) | hold correct (two vintages) |
| NVDA FY2017 interim EPS | 5 | e.g. Q1 FY17 basic 0.36 (0001045810-16-000275) vs 0.39 (0001045810-16-000353, -17-000027) | hold correct (two vintages) |
| TSLA 2024 interim EPS | 8 | e.g. Q1 2024 basic 0.37 (0001628280-24-017503) vs 0.45 (0001628280-25-018911) | hold correct (2024 interims recast in 2025 filings) |
| NVDA Q4 FY2015 DPS | 1 | 10-K 0001045810-15-000036: 0.340 (the annual DPS) on a 3-month context | hold correct (label error) |
| **AMZN 2011-2012 quarterly EPS** | **16** | The original 10-Qs and the FY2011/FY2013 10-Ks agree (e.g. Q1 2011 basic 0.44 in 0001193125-11-110197, -12-032846, -12-187203). Only the FY2012 10-K 0001193125-13-028520 carries shifted quarters (Q1 2011 = 0.29, the Q1 2012 value; Q3 2011 = -0.60, the Q3 2012 value) | **FALSE HOLDS**: a filer label error, not a restatement. The value was right (as-filed / 20). Pre-2015 |
| **NVDA 6M FY2018 basic / diluted EPS** | **2** | 10-Qs 0001045810-17-000123 and -18-000114 give 1.83 / 1.71; the FY2018 10-K 0001045810-18-000010 has 0.98 / 0.92 on the 6-month context (the Q2 value) | **FALSE HOLDS**: label error in the 10-K. Right value 1.83/40 and 1.71/40. Inside the 2015 window |

Mechanism of the 18 false holds: "restated between filings" fires on any two disagreeing filed copies. A copy that equals the same tag's value for ANOTHER period in the same filing is a label shift (ledger rows for SWK, CB, F), not a restatement. The pass should drop that copy and show the agreeing value.

## RU-1 removed cells (30 of 156)
For each derived Q4 / Q3 per-share cell I searched:
- the period's 10-K (or 10-Q) instance;
- the following year's 10-K, for a separately filed fact with the exact 3-month context.

None was found in any of the 30. Example: LLY Q3 2022 DPS, where 10-Q 0000059478-22-000250 files only the 9-month 1.96. So "not filed separately" is honest for the periodic filings. Q4 EPS does appear in 8-K earnings releases, which are not in the store.

## To the owner (Period Engineer)
1. Before hiding with "restated_between_filings", test the disagreeing copy for a label shift: it equals the same tag's value at another period in the same filing (AMZN FY2012 10-K, NVDA FY2018 10-K). Drop that copy, show the agreeing value, and re-test the 18 cells.
2. LLY DPS: pick one basis (declared or paid) per series, or label it; do not show paid quarters beside declared years.
3. Releasing the shown values is supported by this sample (0 wrong of 194). The false holds are coverage losses, not wrong values.
