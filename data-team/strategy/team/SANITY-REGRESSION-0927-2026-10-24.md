# Sanity regression vs the 2026-09-27 baseline (Data Triage, 2026-10-24)
Read-only; run 40087951154. Labels: MEASURED (DB today), FILING-CHECKED (10 filings), DATA-INFERRED. yfinance is a signal only.

## 1. What I could not do
`analytics.data_sanity_check` has **no history** (one overwritten row per company and metric, all dated 10-02 or later); `data_sanity_gate_baseline` holds counts only. A per-company mover list for 09-27 cannot be built, and `created_at`/`resolved_at` are rewritten nightly. Proxy: TTM metrics keep daily snapshots, so I compared ours on 09-27 with ours now, both against today's yfinance value. Cohort = cohort_v1_1.

## 2. Headline (MEASURED, all companies)
quick_ratio `missing_ours` fell 2,072 to 680 (f67a927, 10-09): evaluated rows rose 2,462 to 3,851, so +238 majors came with +1,389 newly compared companies. **The major rate among evaluated rows fell, 24.5% to 21.8%**; the gate divides by all rows, so more coverage reads as regression. Same pattern: ebitda_margin evaluated +230 (5eeb7a0), peg +124, PE +199 (ace07fd).

## 3. Causes
| metric | cause | count | examples |
|---|---|---|---|
| quick_ratio | **(A) REAL**: inventory absent from our facts is treated as zero (f67a927), so quick = current ratio | 74 of 145 cohort majors (population: 431 of 841 equal current_ratio) | NKE, BA, GAP, AZO, XOM, KR, SYY |
| quick_ratio | (d) Yahoo defines it as (cash+STI+AR)/CL; ours is (CA-inventory)/CL, and our formula reproduces from stored inputs in 59 of 64 | 66 | TGT, KO, LLY |
| quick_ratio | stale base period (5) or sanity row older than the current value (7) | 12 | SOFI, BEN, T |
| ebitda_margin | **sanity artefact**: the newest TTM snapshot is NULL (150-day guard 5eeb7a0, 10-09) but the check reads an older non-null snapshot. The product (`resolve.py`, `getLatestMetrics`) takes the NULL | 296 of 850 majors (cohort 64 of 155) | AMD, HRB, ECL |
| ebitda_margin | newly computed / changed / unchanged since 09-27 (unchanged = major then, or yfinance moved) | 68 / 83 / 403 | CASY, LHX |
| peg_ratio | ours changed >2% (candidate commits ace07fd, ef6392b; not isolated) / newly computed / NULL-snapshot artefact / unchanged | 353 / 58 / 28 / 72 | |
| trailing_pe | no history (one row per company). Cohort: split basis (e) APH, MNST; real NFLX; unresolved EPS gap (ours about 2x Yahoo's) HAL, OXY, DLR | 37 cohort | |
| shares_outstanding | evaluated rows flat (4,534 to 4,549), so the +45 is not coverage. Cohort: 41 of 59 are older than 400 days vs the latest filing (NKE 2015, CHTR 2016); 9 are stored 0 | 59 | PINS, SHOP, TAP |

## 4. Real wrong values of ours (FILING-CHECKED)
Stored quick_ratio equals CA/CL because inventory is missing:
- NKE 0000320187-26-000193 (R4): inventories 7,846; stored 2.075, correct 1.387.
- BA 0001628280-26-050038 (R5): inventories 88,388; stored 1.138, correct 0.331.
- GAP 0001628280-26-059345 (R2): merchandise inventory 2,297; stored 1.822, correct 1.109.
- AZO 0001104659-26-073525 (R2): inventories 7,559,056; stored 0.890, correct 0.137.
- XOM 0000034088-26-000093 (R5): inventories 25,563 in two sub-lines, no total; stored 1.135, correct 0.847.

25 of the 74 cohort cells have an unmapped inventory-like us-gaap tag filed in 2026 (DATA-INFERRED). Also real: NFLX diluted EPS Q4-2025 = -17.14 (post-split FY minus pre-split quarters), so P/E is negative.

## 5. yfinance noise or definition (ours is right by our formula)
- Yahoo's formula reproduces: NKE (6,903+1,465+5,242)/11,409 = 1.193; GAP 2,485/3,221 = 0.771; TGT 0000027419-26-000042: 5,411/21,180 = 0.255, and our 0.363 reproduces.
- ADP 0000008670-26-000030, ICE 0001571949-26-000011: client funds (43,958) or margin deposits (114,599) sit in current assets, so ours is about 1.0 vs Yahoo 0.155 and 0.024. Definition, not extraction.
- T 0000732717-26-000372: current 0.820 is correct; the sanity row is old.
- SOFI 0001104659-21-070841: the stored value is a 2021 SPAC balance sheet.
- All 10 filings are quick_ratio; peg, EBITDA, P/E and shares rest on DB evidence only.

## 6. Recommendation: FIX, do not reset the baseline now
1. Sanity check: use the product rule (newest snapshot, NULL means missing_ours). ebitda_margin falls from 850 to about 554 majors, below the 787 baseline; peg falls from 511 to 483, still above 445.
2. quick_ratio: treat inventory as zero only where `company_filing_line_evidence` says the line is not presented; otherwise NULL. Map the unmapped inventory tags (XOM sub-lines, AZO).
3. Gate: add a rate among evaluated rows next to the count, and compare quick_ratio against Yahoo's own formula built from our inputs. Reset only after 1 and 2 and a passing run.
4. Period Engineer: shares_outstanding staleness and zeros; APH and MNST split basis (RF-22); the P/E EPS gap.
Not done: any company's 09-27 status; a cause for the shares +45.
