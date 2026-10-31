# Verify: W3 source.periodic_form_only@1 + dedupe.matching_copies@1 (origin/work/dhairya/w3-periodic-form-only 9a1624d, w3_cohort_dryrun_2026-10-31/verifier_draw.csv), 2026-11-02

Draw: the package's own 100 rows (seed 20261031): 40 authority_value_changed, 30 value_to_none_financial, 10 value_to_none_pvp_or_fee_tag, 20 stage2eb_retire. All 100 checked. Evidence class: FILING-CHECKED (periodic filings' statement R pages; Q4 rows recomputed as 10-K FY minus Q3 10-Q 9M). The pay-vs-performance rows are DATA-INFERRED from tag definition. Verifier 2 (scrooner-bc).

## Result
| Stratum | Verdict | Count |
|---|---|---|
| authority_value_changed | **YES** (none proven wrong) | 31 of 40 confirmed: 13 recast-8-K rows equal the original 10-K/10-Q printed line; 18 Q4 rows equal FY - 9M from the faces. 2 not explained by the original faces (#0, #39). 7 unreadable (kit) |
| value_to_none_financial | **NO** | 19 of 30 rightly blank (8-K-only: no 10-K/10-Q prints the line for that period). **11 of 30 are coverage losses:** a 10-K/10-Q prints the line, but copies disagree (rounding, recast, restatement), so the group ends with no authoritative value |
| value_to_none_pvp_or_fee_tag | **YES** | 10 of 10: pay-vs-performance / fee-table tags never appear on a 10-K/10-Q face |
| stage2eb_retire (20) | **NO (1 cell)** | 19 of 20 fine. The next value is the latest periodic copy, printed on that filing's face where it is a statement column. Wrong: #94 WRB (11544) FY2023 net income goes blank although the 10-Ks print 1,381,359K |
| Pinnacle FY2023 | **confirmed** | 10-K 0002082866-26-000018 prints Net income 562,152,000 for 2023 (available to common 546,960,000) |

## Coverage losses (value_to_none_financial, a periodic filing prints the line)
| Row | CIK | Tag / period | Periodic copies (form, value) | Face check |
|---|---|---|---|---|
| 42 | 1179929 | CFO FY2014 | 10-K 2015 1,060,257K; 10-K 2016/2017 1,060M | 2017 10-K CF prints 1,060M |
| 44 | 1283699 | Operating income Q3 2016 | 10-Q 2016 989M; 10-Q 2017 1,048M | quarter comparative (10-Q) |
| 46 | 1219601 | Investing CF FY2017 | 10-K 2018 -509M; 10-K 2019/2020 +496M | 2020 10-K prints 496M |
| 47 | 107263 | Financing CF FY2015 | 481M; 451M (2018 10-K) | 2018 10-K prints 451M |
| 53 | EXC 1109357 | Revenues FY2020 | 33,039M; 16,663M (2023 10-K, recast) | 2023 10-K prints 16,663M |
| 56 | 1571996 | CFO FY2017 | 2,222M / 2,309M / 2,367M | 2019 10-K prints 2,367M |
| 59 | 313616 | Gross profit Q3 2014 | 2,565.7M; 2,452.3M (2015 10-Q) | quarter comparative |
| 60 | 1021635 | Operating income FY2016 | 503.3M; 530.8M (2019 10-K) | 2019 10-K prints 530.8M |
| 62 | C 831001 | Net income FY2014 | 7,313M; 7,310M | 2017 10-K prints 7,310M |
| 66 | TAP 24545 | CFO FY2014 | 1,272.6M; 1,287.9M | 2017 10-K prints 1,287.9M |
| 68 | 1276187 | Revenues Q1 2015 | 10,380M ... 6,447M, 9,661M (later 10-Ks) | quarter comparative |

## Findings for the builder
1. **value_to_none with periodic copies:** after the 8-K copies are excluded, a group whose remaining periodic copies disagree must not end with no value. Apply the restatement rule (latest periodic filing, or original as filed per the founder's ruling) to the periodic copies only. Re-verify the 11 rows above.
2. **#94 WRB FY2023 NetIncomeLoss:** the periodic copies agree (1,381,359K on three 10-Ks), yet the retire leaves the cell blank. Look at why the DEF 14A (rounded 1,381M) retirement blanks instead of falling back.
3. **Q4 rows not explained by the original faces:** #0 1001316 Q4 2022 (after -78,471K; original FY -198,335K minus 9M -145,341K = -52,994K) and #39 1632970 Q4 2021 (after -23,032K; FY -47,794K minus 9M -13,293K = -34,501K). Likely restated FY or attributable-vs-consolidated; confirm which filing the derived Q4 uses.
4. Unreadable here (kit parse): #3, #7, #18, #20, #27, #32, #33.

## Requests and disk
SEC requests: 463. DB: one connection to locate FY/Q3 filings and original filings for 8-K-only rows.
