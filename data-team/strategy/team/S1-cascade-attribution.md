# S1: Cascade attribution via the metric dependency graph (2026-10-22)

Scope: blank classes C1 (8,142), C2 (2,764), D1 (4,086) = 14,992 blank cells of the 160,718-cell cohort (986 companies). Class counts were reproduced exactly from cohort_cells.csv with these rules: C1 = reason starts `incomplete:`; D1 = `missing:*_ttm`; C2 = other `missing:*` that is not prior_period/fewer_than_3y/4_consecutive/non_consecutive (those 2,839 are H1).
Evidence labels: graph = FILING-CHECKED only where stated; everything else DATA-INFERRED (live DB read 2026-10-21/22, one connection, 60s timeout; the live latest `metric_value` row matched cohort_cells for all 14,992 cells). Nothing in the pipeline or DB was changed.
Artifacts: graph `data-team/strategy/data/metric_dependency_graph.csv` (164 rows: 163 data points + the Alpaca `price` source; columns data_point, kind, module, period_basis, direct_inputs, ultimate_leaf_inputs, cohort_blank_cells). Scripts: `data-team/strategy/tools/s1_cascade/` (extra, reproducible; delete if unwanted). Inputs came from `mapper/*.py` and live `analytics.metric_definition_input` (note `definitions.py` seed for gross_margin is stale vs live).

## 1. The graph (summary)
Kinds: 51 leaf concepts (XBRL tag first_match/sum), 22 resolved concepts (= base + conflict fill, a superset), 4 derived concepts (gross_profit_resolved, cost_of_revenue_resolved, operating_expenses_resolved, operating_income_resolved, total_debt_resolved: OR over alternatives), ~75 metrics (engine `calculate.py`, `ttm.py`, `expanded_metrics.py`, `quality_*`, `fcf_growth`, `reconciliation`), 6 price metrics (Alpaca price x shares), 3 ownership sources. Depth is at most 3: leaf -> engine metric -> TTM/yield/growth metric (e.g. capex, cfo -> fcf -> fcf_per_share / dividends_pct_fcf / fcf_growth_*; operating_income_resolved + D&A -> ebitda (quarterly + persisted TTM) -> net_debt_ebitda, ebitda_margin, debt_to_ebitda, ev_ebitda).

## 2. Headline finding: only about half of the cascade is a missing leaf
For each blank cell I walked its named input(s) to leaves using cohort presence, then, where every input exists somewhere in history ("period residual", 7,983 cells = 53%), diagnosed the latest metric period against canonical_fact, core.period, period_gap and SEC tag usage.

Cell classes (each cell counted once; rule: any evidenced-legitimate input absence => class L; else any unevidenced => U; else fixable):

| Class | Cells | Share | C1 | C2 | D1 |
|---|---|---|---|---|---|
| L. legitimate absence propagating (should be not-applicable by rule) | 3,306 | 22.1% | 2,164 | 706 | 436 |
| U. leaf missing, no evidence either way (absence or vocabulary) | 4,520 | 30.1% | 2,333 | 571 | 1,616 |
| F1. fixable leaf or period derivation (tag/extraction/Q4/YTD/FY history) | 5,020 | 33.5% | 2,058 | 1,361 | 1,601 |
| F2. engine defect: cover-date anchor | 1,503 | 10.0% | 1,427 | 76 | 0 |
| F3. engine/feed: latest 10-Q missing from SEC feed (company level) mixed with F2 | 535 | 3.6% | 101 | 1 | 433 |
| Other/blocked (price/ownership, rule) | 108 | 0.7% | 59 | 49 | 0 |

Answer to (3): legitimate-absence propagating = 22.1% evidenced (3,306). Upper bound if all of U later proves to be absence = 52.2%. Fixable (F1+F2+F3) = 47.1% (7,058 cells), of which 13.6% (2,038) are system fixes, not leaf fixes. By group (cells): corporate 9,259 (L 1,416, U 2,846, fixable 4,939); bank 847 (L 508); reit 1,283; other_financial 945; utility 802; insurer 574; energy 617; bdc 634; no_revenue_line 31.

"Legit" means: filing-line evidence says the line is not on the statements (`company_filing_line_evidence`, label-matching: DATA-INFERRED, not FILING-CHECKED), sector reasons (bank/REIT/BDC interest-income-not-revenue), pre-revenue. "U" never calls absence structural: lineage "no relevant tag filed" is relative to our ~88 mapped tags (circular, per infra map section 7.5).

## 3. Root causes that are NOT leaf inputs (engine/system), found by this analysis
1. Cover-date anchor (1,427 cells, 718 companies, all groups; corporate 979). Per-share balance-sheet metrics (book_value_per_share 786, net_cash_per_share 800 residual, debt/equity-type ones) anchor on the latest period of any input; `shares_outstanding` is dated at the 10-Q cover date, after the balance-sheet date, so the latest row is null (`incomplete:numerator`) while a valid row exists one period earlier. Coverage takes the latest row, so the cell shows blank. FILING-CHECKED example: AAPL 10-Q 0000320193-26-000020: R1 period end Jun 27 2026, cover shares 14,594,180 (thousands); R4 equity 107,520 at Jun 27 2026. DB: book_value_per_share row 2026-07-17 null, row 2026-06-27 = 7.3599. Fix owner: Mapper/Data Engineer (do not emit or do not select cover-date anchor rows). No leaf fix helps.
2. Latest 10-Q not in SEC Company Facts (84 companies, 576 cells, TTM metrics all blank via the 150-day staleness guard). Test: latest 10-Q/10-K period_of_report is more than 45 days newer than the latest canonical revenue/NI/CFO/op-income period for 88 of 986 companies (85 by one quarter). Example KO: 10-Q 2026-07-29 (period 2026-07-03) in `core.filing`, newest fact 2026-04-28, `raw.sec_companyfacts` sha256 identical across fetches 2026-08-13 to 2026-09-29. DATA-INFERRED; likely SEC feed lag (period_gap `not_in_sec_feed`). Fix owner: Data Engineer (FSDS / filing XBRL as source, consistent with the FSDS direction).
3. Share count 1-year-ago window (76 cells): `_shares_outstanding_now_and_1y_ago` demands a fact 350-380 days earlier; cover dates rarely align.
4. Also in the residual: 199 cells where the latest quarter exists only as YTD (not derived), 360 unclassified missing quarter, 377 with all quarters present (staleness/other), 665 FY-history gaps (fcf growth, piotroski), mostly Period Engineer territory.

## 4. Top 25 LEAF inputs by downstream blank cells explained
Cells = blank cascade cells where the leaf is at least one cause (a cell with two causes counts for both; fractional weights sum to 14,992). Buckets: LEGIT / UNEV (unevidenced) / FIX (tag, extraction, drift) / PER (period or feed). Groups: corp, reit, bank, util, ofin (other_financial), ins, en, bdc.

| # | Leaf | Cells | Cos | LEGIT | UNEV | FIX | PER | corp | reit | bank | util | ofin | ins | en | bdc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | capex | 1567 | 401 | 0 | 911 | 206 | 450 | 602 | 329 | 106 | 74 | 103 | 105 | 125 | 122 |
| 2 | total_debt (+split, resolved) | 1086 | 236 | 21 | 673 | 465 | 207 | 788 | 71 | 45 | 9 | 106 | 35 | 6 | 19 |
| 3 | operating_income | 963 | 213 | 565 | 90 | 243 | 65 | 288 | 75 | 264 | 6 | 84 | 73 | 46 | 127 |
| 4 | dividends_per_share | 810 | 442 | 0 | 724 | 6 | 80 | 690 | 12 | 5 | 27 | 31 | 14 | 26 | 3 |
| 5 | interest_expense | 798 | 585 | 0 | 143 | 649 | 6 | 666 | 22 | 3 | 40 | 30 | 9 | 22 | 4 |
| 6 | share_buybacks | 717 | 350 | 2 | 384 | 101 | 230 | 457 | 75 | 16 | 66 | 42 | 14 | 30 | 15 |
| 7 | shares_outstanding | 683 | 307 | 0 | 405 | 0 | 236 | 550 | 19 | 9 | 21 | 49 | 8 | 22 | 5 |
| 8 | dividends_paid | 683 | 408 | 1 | 535 | 95 | 52 | 577 | 14 | 6 | 16 | 38 | 10 | 18 | 3 |
| 9 | accounts_receivable | 672 | 356 | 260 | 13 | 310 | 89 | 375 | 49 | 70 | 18 | 45 | 46 | 25 | 43 |
| 10 | research_and_development | 626 | 626 | 604 | 10 | 8 | 4 | 354 | 51 | 40 | 49 | 44 | 28 | 33 | 27 |
| 11 | cost_of_revenue | 624 | 262 | 566 | 1 | 48 | 9 | 198 | 66 | 83 | 59 | 80 | 46 | 32 | 58 |
| 12 | operating_expenses | 576 | 120 | 515 | 0 | 61 | 0 | 159 | 33 | 176 | 3 | 48 | 47 | 30 | 80 |
| 13 | interest_income | 557 | 557 | 327 | 32 | 197 | 1 | 341 | 42 | 37 | 31 | 30 | 26 | 24 | 26 |
| 14 | inventory | 553 | 368 | 403 | 20 | 51 | 79 | 373 | 44 | 6 | 44 | 41 | 9 | 26 | 10 |
| 15 | gross_profit | 505 | 255 | 505 | 0 | 0 | 0 | 151 | 57 | 78 | 39 | 61 | 42 | 23 | 52 |
| 16 | depreciation_and_amortization | 480 | 126 | 0 | 82 | 398 | 0 | 232 | 26 | 66 | 16 | 22 | 54 | 16 | 48 |
| 17 | depreciation_and_amortization_resolved | 433 | 113 | 0 | 103 | 272 | 58 | 323 | 8 | 4 | 24 | 30 | 16 | 8 | 20 |
| 18 | operating_income_resolved | 358 | 93 | 0 | 122 | 177 | 59 | 205 | 67 | 6 | 5 | 33 | 2 | 10 | 30 |
| 19 | accounts_payable | 301 | 203 | 92 | 3 | 120 | 86 | 225 | 23 | 1 | 14 | 19 | 7 | 10 | 2 |
| 20 | revenue | 245 | 61 | 88 | 8 | 0 | 149 | 126 | 34 | 4 | 9 | 30 | 0 | 7 | 22 |
| 21 | cfo | 235 | 123 | 0 | 37 | 0 | 198 | 198 | 5 | 3 | 8 | 14 | 1 | 6 | 0 |
| 22 | gross_profit_resolved | 232 | 137 | 116 | 2 | 0 | 114 | 166 | 11 | 1 | 27 | 6 | 2 | 16 | 3 |
| 23 | current_assets | 219 | 210 | 61 | 98 | 15 | 45 | 54 | 46 | 40 | 2 | 31 | 18 | 1 | 27 |
| 24 | current_liabilities | 205 | 205 | 40 | 21 | 104 | 40 | 44 | 44 | 40 | 2 | 29 | 18 | 1 | 27 |
| 25 | income_before_tax | 194 | 91 | 2 | 57 | 32 | 103 | 107 | 43 | 7 | 11 | 6 | 6 | 7 | 5 |

Read-across: D&A (rows 16+17) and operating income (rows 3+18) are each one family split by raw vs resolved name; combined they are about 890 and 1,250 distinct-leaf cell appearances (not additive across cells). Items 10, 11, 12, 14, 15 are mostly legitimate absence (R&D 604 of 626; cost of revenue, opex, gross profit, inventory): these cascades (rnd_intensity, gross_margin, inventory_days, interest_coverage) should become not-applicable by template, not be "fixed". Banks: 508 of 847 cascade cells are legit.

## 5. Evidence on the unevidenced block (U = 4,520 cells), SEC FSDS 2025q4 sample
For each (company, leaf) unevidenced pair, the company's latest FSDS filing (968 of 986 cohort companies covered) was tested for a presented line carrying one of our mapped tags or a plausible alternative tag (strict tag regex; DATA-INFERRED, filings not opened except where noted):
- 3,117 U cells (69%): the filing presents no matching line. Consistent with real absence (non-payers: dividends_paid 468 none vs 4 mapped; dividends_per_share 668 none; capex 641 none; share_buybacks 305 none) and a candidate for "evidenced zero / not applicable" rule once a presented-line check (the `company_filing_line_evidence` mechanism) is extended to these leaves. Not structural until that evidence exists. Caveat: my tag regex may miss unusual tags.
- 718 U cells (16%): a line IS presented. Mapped tag present 14-59 per leaf (capex 59, share_buybacks 41, dividends_per_share 34, operating_income_resolved 28, D&A 24) means our canonical lacks a value despite a mapped tag (pipeline/period problem); alternative tag present = vocabulary (capex 193, total_debt 111+15, dividends_paid 47, D&A 48, interest_expense 11).
- 685 (15%) untestable (shares_outstanding, company not in FSDS).
FILING-CHECKED vocabulary example: LLY 10-Q 0000059478-25-000254 CF line "Purchases of property and equipment" is tagged PaymentsToAcquireOtherPropertyPlantAndEquipment; our capex mapping lists only PaymentsToAcquirePropertyPlantAndEquipment and PaymentsToAcquireProductiveAssets, and LLY's last canonical capex is 2022-09-30 (core.fact has the new tag through 2026-06-30). Mapped vocabulary is only about 88 tags (interest_expense 2, cfo 2, D&A 2), which is why interest_expense (649 FIX cells: InterestExpenseNonoperating in 278 of 407 tested stopped cases) and D&A (Depreciation, DepreciationAmortizationAndAccretionNet, AmortizationOfIntangibleAssets: 85 of 104 vocab-candidate cases) top the fixable list.

## 6. Expected cell gain
Top 10 fixable leaves, ranked by cells with a FIX or period cause: total_debt family 672, capex 656, interest_expense 655, accounts_receivable 399, depreciation_and_amortization 398, share_buybacks 331, D&A_resolved 330, operating_income 308, shares_outstanding 236, operating_income_resolved 236.
A cell is counted only when every one of its causes is fixed (a cell still blocked by a legitimate input stays blank or becomes N/A). Upper bounds; the metric may still be null for other rules (negative base, immaterial base):
- Tag/extraction/drift fixes on those 10 leaves (bucket FIX only): +2,223 cells.
- Plus period derivation and freshness on those leaves: +3,379 cells.
- System fixes alone (cover-date anchor 1,427 + 76, feed-lag companies, 535 mixed): +2,038 cells, no leaf work.
- Top 10 leaves plus system fixes: +5,441 cells (+3.4 points of the 160,718-cell cohort; fill 76.7% to about 80.1%, before any denominator relief).
- All fixable causes anywhere: +7,058 cells (4.4 points).
- Denominator relief (separate, not fill gain): 3,306 evidenced-L cells would move from blank to not-applicable; with the U block's 3,117 FSDS-consistent absences if the evidence rule is built, up to 6,423 cells (4.0 points of denominator).
Recommended order: (1) cover-date anchor fix (largest single, no data work); (2) tag vocabulary for interest_expense, D&A, capex, total_debt, share_buybacks (Tag Mapper + Standardization Lead, needs coexistence checks; components differ in perimeter, e.g. D&A, debt); (3) feed freshness for the 84-88 companies; (4) not-applicable rules for R&D, cost of revenue, gross profit, opex, inventory, interest income with evidence; (5) evidenced-zero check for dividends/buybacks/capex/sbc.

## 7. Risks and what I could not verify
- Presence of a concept cell means "any canonical_fact ever" (coverage_matrix); latest-period diagnosis used facts since 2023-06 only. "Stopped since 2023-06" (about 1,750 cause-cells) may include rarely-tagged items; 243 cells in that block have the line no longer on the statement (legit).
- The FSDS test is one filing per company (Q3/FY 2025), regex-based; cash-flow lines may be absent from a short filing for reasons unrelated to the latest period.
- Only the AAPL anchor example and the LLY vocabulary example were opened in filings; the KO feed lag is inferred from sha256 and filing index, not from SEC's API.
- Cohort is the top 986 companies; rates will differ in the tail.
- Piotroski and growth reasons are truncated in the DB; I used all nine required inputs.
- Would change my mind: if the coverage matrix is changed to take the latest non-null row, the 1,427-cell engine block disappears from "blank" without a pipeline change (still a display decision).
