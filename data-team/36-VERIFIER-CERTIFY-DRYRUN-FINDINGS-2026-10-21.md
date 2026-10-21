# Verifier: filing check of the certification dry-run `wrong_value` findings (2026-10-21)

Role: Data Verifier (16). Objective: open the original filing for every `wrong_value` finding of the `scrooner-certify` dry-run shards S001 (AAPL, AMZN, AVGO, GOOG, LLY, META, MSFT, NVDA, TSLA) and S002 (AMD, JNJ, JPM, MA, MU, V, WMT, XOM) and return FILING-CHECKED verdicts. Inputs: scratchpad `s001.json` (230 wrong_value), `s002.json` (232 wrong_value). Read-only: one DB connection, statement_timeout 20s, read-only session; SEC fetches with declared User-Agent, one process, <= 2 req/s. No writes.

Evidence labels: FILING-CHECKED (original filing opened, locator cited), DATA-INFERRED (our tables only), ASSUMED.

Status: COMPLETE (2026-10-21). Summary and false-positive rate in "Suite accuracy" below.

## Item 1. MSFT FY2016 (FY ended 2016-06-30): net income 20,539M and operating income 26,078M vs quarter sums 16,798M / 20,182M

Verdict: **both defensible; the finding is a restatement-basis mix, not a wrong value** (FILING-CHECKED). Suite rule I5 `quarters_do_not_sum_to_year` is a false positive as `wrong_value` here; it should be `review: basis_conflict`.

| Value | Basis | Filing | Locator |
|---|---|---|---|
| NI 20,539M, OI 26,078M, revenue 91,154M (FY2016) | ASC 606, full retrospective restatement | 10-K FY2018, 0001564590-18-019062 (filed 2018-08-03) | R2 Income Statements, column Jun. 30, 2016; R8 Accounting Policies: "We elected to early adopt the standard effective July 1, 2017, using the full retrospective method, which required us to restate each prior reporting period presented" |
| NI 16,798M, OI 20,182M, revenue 85,320M (FY2016) | ASC 605, as originally reported | 10-K FY2016, 0001193125-16-662209 | R2 Income Statements, column Jun. 30, 2016 |
| Quarters NI 4,902 / 5,018 / 3,756 / 3,122; OI 5,793 / 6,026 / 5,283 / 3,080 (sum 16,798 / 20,182) | ASC 605 | 10-K FY2017, 0001564590-17-014900 | R127 Quarterly Information (Detail), columns Sep 2015 to Jun 2016 |

No ASC 606 quarterly breakdown of FY2016 exists in any 10-K/10-Q (the FY2018 10-K quarterly note covers FY2018 and FY2017 only), so the quarters can only be shown on the 605 basis.

Root cause: latest-filed precedence takes the FY value from the 3-year comparative of the FY2018 10-K (restated), while the quarter cells come from the original filings. Same for FY2017 (stored NI 25,489M / OI 29,025M from 10-K FY2019 0001564590-19-027952; original 21,204M / 22,326M).

Real downstream defects found while checking (DATA-INFERRED from `analytics.metric_value`, basis from the filings above):
- `net_income_growth_yoy` FY2016 = 0.6845 = 20,539 (606) / 12,193 (FY2015, 605; FY2015 was never restated) - 1. Cross-basis growth: on one basis it is 16,798/12,193 - 1 = 0.3777. **Wrong value** (mixed basis).
- `net_margin` TTM ending 2016-06-30 = 0.1969 (605 quarters: 16,798/85,320) while FY2016 = 0.2253 (606: 20,539/91,154). Two different numbers for the identical 12 months on one page. Each defensible on its own basis; showing both unlabeled is a defect.
- `revenue_sanity_resolved` FY2016 stored 85,320M (`SalesRevenueNet`, 605) while `net_income_resolved` FY2016 is 606: cross-concept basis mix within one fiscal year (the margin metrics use the 606 revenue 91,154M and are internally consistent).
- `net_income_growth_yoy` Q4 FY2016 = -1.977 (3,122 vs Q4 FY2015 -3,195): growth on a negative base; should be undefined like the CAGR rule.

Rule family proposed: **R-BASIS (restatement basis mix)**: when a FY value comes from a later filing than all of its quarters and differs from the original FY value of the same tag, the FY cell, its growth vs the prior year and the TTM at that year end must carry one basis or be flagged; the I5 check should compare quarter sum against the FY value *from the same filing vintage* before calling `wrong_value`.

## Item 2. JPM and MA annual net income FY2021-FY2025 sourced from DEF 14A `NetIncomeLoss`

Verdict: **JPM: wrong value confirmed (5 cells), rounded to $0.1B. MA: values correct (5 cells), wrong source form.** FILING-CHECKED. Not corrected by the doc 57 D1 recompute; the company page shows the proxy values today.

| Company | FY | Stored (DEF 14A) | 10-K value | Diff | 10-K locator |
|---|---|---|---|---|---|
| JPM | 2021 | 48,300M | 48,334M | -34M | 0000019617-24-000225 R3 "Net income/(loss)" Dec. 31, 2021 |
| JPM | 2022 | 37,700M | 37,676M | +24M | 0000019617-24-000225 R3, Dec. 31, 2022 |
| JPM | 2023 | 49,600M | 49,552M | +48M | 0001628280-26-008131 R3 "Net income", Dec. 31, 2023 |
| JPM | 2024 | 58,500M | 58,471M | +29M | 0001628280-26-008131 R3, Dec. 31, 2024 |
| JPM | 2025 | 57,000M | 57,048M | -48M | 0001628280-26-008131 R3, Dec. 31, 2025 |
| MA | 2021-2025 | 8,687 / 9,930 / 11,195 / 12,874 / 14,968M | identical | 0 | 0001141391-26-000013 R3 "Net Income" (2025, 2024, 2023); 0001141391-24-000022 R3 (2022, 2021) |

Proxy locators: JPM DEF 14A 0000019617-26-000096 R2 Pay vs Performance, "Net Income" column printed in $ billions to one decimal (57.0, 58.5, 49.6, 37.7, 48.3); MA DEF 14A 0001141391-26-000021 R2 Pay vs Performance, Net Income in $ millions (14,968 ... 8,687).

Current state (DATA-INFERRED, same SQL as `apps/app/lib/company/db.ts::getStatement`, which reads `analytics.statement_line` -> `net_income_resolved`): the P&L "Net Income" row shows JPM 48.3B / 37.7B / 49.6B / 58.5B / 57.0B and MA's proxy-sourced values. `canonical_fact.resolved_at` for these rows is 2026-09-08 (`net_income_resolved`) and 2026-10-18/19 (`net_income`); the D1 run did not touch them. JPM (CIK 19617) is not in `doc/data-moat/team/backups/s2_ciks_20261018.txt`; MA is, but its proxy facts are authoritative, so the conflict-fill rerun had nothing to change. `scrooner.com` was not reachable from this session (ECONNREFUSED), so the rendered page itself was not opened.

Root causes (code read, `pipeline/src/scrooner_pipeline/mapper/conflict_resolution.py` at HEAD):
- JPM: the 10-K copies (48,334M, three filings) and the rounded DEF 14A copy (48.3B) disagree, so Stage 2e marks every copy non-authoritative. `resolve_conflict_fill` -> `_safe_fill_value` (line 173) accepts the group (ratio <= 15%) and takes the **highest fact_id**, which is the most recently loaded proxy fact. `_load_conflict_groups` (line 124) has no form filter. Commit 3defd93 added the eligible-form rule only to the latest-filed resolver, not to this safe-fill path. `resolve_conflict_fill` skips cells already in `canonical_fact` (`_load_already_resolved`, insert-only), so a rerun can never replace a wrong fill.
- MA: MA's 10-K tags the face "Net Income" line `ProfitLoss` (R3 defref `us-gaap_ProfitLoss`; there is no NCI line). Its only `NetIncomeLoss` facts for FY2021-2025 are the DEF 14A ones, which are authoritative because they are the lone copies. `net_income` maps `NetIncomeLoss` at priority 1 and `ProfitLoss` at priority 2 (`concept_mapping` ids 7, 8), so first_match picks the proxy fact. The values equal the 10-K values, so the displayed numbers are right. The lineage is wrong, and for a filer with NCI the same path could show a value that is not on its statements.
- Ledger row 2026-10-18 (AEMD) already says "never take financial-statement values from proxy filings". The same failure is still live for two top-20 companies.

Fix (for the owner, not done here): exclude DEF 14A (and every non-10-K/10-Q-family form) from Stage 2e conflict grouping and from both fill paths, so a rounded proxy copy cannot de-authorize precise 10-K copies. Then delete and refill the affected cells after a reviewed dry-run. In S001/S002 scope: JPM `net_income` + `net_income_resolved` x5 years, MA the same x5 (20 cells). Population scope is not measured yet.

Additional JPM cells, not flagged by the suite (DATA-INFERRED from `core.fact`, arithmetic against the FILING-CHECKED FY values above): the Normalizer derived a Q4 fact from the proxy FY, `core.fact` 182608846 (`is_derived`, filed under DEF 14A 0000019617-26-000096): Q4 2025 = 57,000 - 44,023 = 12,977M, where 10-K FY minus 9M gives 13,025M (the correct derived copy is fact 340478). `canonical_fact` concept `net_income` holds the proxy-derived Q4 for 2021-2025: 10,365 / 11,032 / 9,355 / 14,034 / 12,977M, where FY(10-K) minus 9M gives 10,399 / 11,008 / 9,307 / 14,005 / 13,025M. Those 5 cells are wrong. `net_income_resolved` Q4 2025 holds the correct 13,025M. But its FY 2025 is 57,000M, so on the page Q1 to Q4 sum to 57,048M while FY shows 57,000M. Total confirmed wrong for JPM: 15 cells (5 FY in each of `net_income` and `net_income_resolved`, plus 5 Q4 in `net_income`).

## Item 3. NVDA 10-for-1 split (June 2024): split table and per-share basis

Verdict: **wrong values confirmed (FILING-CHECKED for the splits and anchor values; full cell list DATA-INFERRED by arithmetic on those filed factors).** The split table has two defects, not one.

Filing evidence:
- 10-for-1 split: 10-Q Q2 FY2025, 0001045810-24-000264, R8 Summary of Significant Accounting Policies: "In May 2024, we announced a ten-for-one stock split ... Shareholders of record at the close of market on June 6, 2024 received nine additional shares ... distributed after the close of market on June 7, 2024. All share, equity award and per share amounts presented herein [have been retroactively adjusted]". Cover R1: Entity Common Stock, Shares Outstanding 24,530 (millions). R2: Q2 FY2025 basic EPS 0.68, Q2 FY2024 0.25 (split-adjusted).
- One 4-for-1 split in 2021: 10-K FY2022, 0001045810-22-000036, R10: "On July 19, 2021, we executed a four-for-one stock split"; R42 "Stock split ratio 4".
- Fully adjusted anchors: 10-K FY2025, 0001045810-25-000023, R3: basic EPS FY2025 2.97, FY2024 1.21, FY2023 0.18; diluted 2.94 / 1.19 / 0.17.

`analytics.company_stock_split` for NVDA (DATA-INFERRED) holds 2021-06-03 ratio 4 (fact 39316261, 10-Q 0001045810-21-000131) **and** 2021-07-19 ratio 4 (fact 39316264, 10-K 0001045810-22-000036). That is one split recorded twice, and there is no 2024 row.

Root causes (`pipeline/src/scrooner_pipeline/corporate_actions/stock_splits.py::detect_stock_splits`):
1. **2024 split missing**: the query keeps `p.period_type = 'instant'` only (line 116). NVDA files the 10-for-1 ratio (`StockholdersEquityNoteStockSplitConversionRatio1` = 10) only on duration contexts: facts 39316269 (2024-05-01..2024-05-31, 0001045810-24-000264, authoritative), 39316271, 39316273 (2024-06-01..2024-06-30, 0001045810-25-000116).
2. **2021 split double-counted**: `_MERGE_WINDOW_DAYS = 45` (line 99). The two disclosed dates of the same split (2021-06-03 in the 10-Q, 2021-07-19 in the 10-K) are 46 days apart, so they are not merged. Pre-2021 per-share values are divided by 16 (4 x 4) instead of 40 (4 x 10).

Wrong-basis cells. Display concepts (`*_resolved`), period_end >= 2015-01-01. Classified by source filing date (pre 2021-07-19 needs /40, 2021-07-19 to 2024-06-07 needs /10, later as filed); DATA-INFERRED from `canonical_fact` + `core.fact`:

| Concept | Wrong | Right | Wrong range | Typical error |
|---|---|---|---|---|
| diluted_eps_resolved (on the P&L page) | 57 | 22 | FY2015 to Q1 FY2024 | FY2015-FY2019 at 1/16 of filed (FY2015 0.07 vs 0.0285 correct); FY2020 4.52 unadjusted; FY2021-FY2023 not /10 (FY2023 1.74 vs 0.17 filed) |
| basic_eps_resolved | 57 | 22 | same | FY2023 1.76 vs 0.18 filed; Q1 FY2024 0.83 vs 0.083 |
| dividends_per_share_resolved | 55 | 22 | FY2015 to FY2024 | FY2023 0.16 vs 0.016 (10-Q 0001045810-24-000264 R6 shows Q2 FY2024 at 0.004) |
| shares_outstanding_resolved | 47 | 11 | 2015-01-25 to 2024-05-24 | 2024-05-24 2.46B (the pre-split cover count of 10-Q 0001045810-24-000124) next to 24.53B on 2024-08-23; pre-2021 about 0.6B unadjusted |

The suite flagged only 1 shares cell and 1 DPS cell for NVDA (I9). The real count is about 216 display cells. The as-filed concepts (`basic_eps`, `diluted_eps`, `dividends_per_share`, `shares_outstanding`) are as-filed by design and are not counted as wrong.

Downstream (DATA-INFERRED, `analytics.metric_value`): `book_value_per_share` FY2023 = 8.96 (should be 0.896 on the current basis); `diluted_shares_growth_3y_cagr` FY2023 = 0.59 and `_5y_cagr` = 0.32 (both are just the 2021 split showing up as dilution); the EPS history on the page drops from 1.74 (FY2023) to 1.19 (FY2024) where the filed adjusted values rise from 0.17 to 1.19.

Fix (owner: Period Engineer / Data Engineer; nothing written here): (a) accept duration-context split-ratio facts, using the context end or the disclosed record date as the event date; (b) merge same-ratio disclosures within a wider window (at least 60 days), or key on (ratio, fiscal quarter); (c) re-run the retroactive adjustment for the NVDA per-share and share series after a dry-run, then rerun I9 across the top 1,000 for every company with a split-ratio fact on a duration context or two same-ratio dates 45-90 days apart.

Population scope (DATA-INFERRED, read-only queries 2026-10-21): 12 companies have two same-ratio split rows 46-120 days apart, so the same split may be counted twice. 156 companies have an authoritative forward-split ratio fact (`StockholdersEquityNoteStockSplitConversionRatio1` > 1, period_end >= 2015) only on a non-instant context, with no split row within 120 days, so the split may be missing. Reverse splits (ratio < 1) were not counted. Each needs the same filing check before any re-basing.

## Item 4. V quarterly dividends per share stored negative (-0.75 to -1.18)

Verdict: **wrong values confirmed (FILING-CHECKED cause). The defect is wider than the negatives: every Visa FY and YTD DPS cell holds the quarterly rate.**

Filing evidence: 10-K FY2025, 0001403161-25-000089, R8 Consolidated Statements of Changes in Equity (Parenthetical), 12 Months Ended Sep. 30, 2025 / 2024 / 2023: "Dividends declared, quarterly, per share $0.59 / $0.52 / $0.45". The element label says *quarterly*, but the context is the 12-month year. 10-Q Q3 FY2025, 0001403161-25-000052, R7: the same 0.59 sits on both the 3-month and the 9-month contexts. R25 Stockholders' Equity: "In fiscal 2025, 2024 and 2023, the Company declared and paid dividends of $4.6 billion, $4.2 billion and $3.8 billion". No annual per-share total is stated; four quarterly declarations of 0.59 give 2.36 for FY2025 (arithmetic on filed quarterly rates; this sum is DATA-INFERRED).

Root cause: Visa tags the quarterly rate (`CommonStockDividendsPerShareDeclared` / `...CashPaid`) on every YTD and FY context. The Normalizer's Q4 = FY - 9M derivation and the YTD-difference derivation then produce rate - 3 x rate = -2 x rate, and rate - rate = 0. Ledger row 2026-10-18 (AGNT, MUR) already says DPS derivation must be routed; this is the same family with a filer-specific trigger.

Stored cells, `dividends_per_share_resolved` (Visa company_id 5718; DATA-INFERRED listing, cause FILING-CHECKED):
- Negative derived Q4: FY2022 Q4 -0.750, FY2023 Q4 -0.90, FY2024 Q4 -1.04, FY2025 Q4 -1.18 (true Q4 rates 0.375 / 0.45 / 0.52 / 0.59, the same rate as Q1-Q3 of each year, filed in the following 10-K/10-Q parentheticals).
- Derived zeros: FY2015 Q3 0.00, Q4 0.00; FY2016 Q2 0.00, Q3 0.00, Q4 0.00 (true: 0.12 and 0.14 per quarter).
- FY cells holding one quarter's rate: FY2015 0.12, FY2016 0.14, FY2017 0.165, FY2019 0.25, FY2020 0.30, FY2021 0.32, FY2022 0.375, FY2023 0.45, FY2024 0.52, FY2025 0.59. Correct FY = the sum of the four quarterly declarations (FY2025 2.36, FY2024 2.08, FY2023 1.80, FY2022 1.50).
- 6M/9M YTD cells (`fiscal_period` null, 14 cells, FY2015-FY2026) hold the quarterly rate. They are not shown on the page, but they feed the derivations above.
- Same defect in concept `dividends_per_share`: Q4 FY2020 -0.6 (CashPaid) and Q4 FY2022-FY2025 negatives.
- Correct: the 3-month Q1-Q3 cells taken from the 10-Qs (e.g. Q3 FY2025 0.59).

Suite verdict: the 13 I3/I9 wrong_value findings for Visa are true positives, and they cover only the negative cells. The 10 FY cells and 5 zeros are wrong and were not flagged. Proposed rule family **R-RATE-ON-YTD**: a per-share element whose YTD/FY value equals the same filing's 3-month value (and whose label contains "quarterly") is a rate, not a period total. Do not store it as FY. Never derive from it. Show FY DPS only from a filed annual per-share fact, or as the sum of four filed quarterly declarations under a stated rule (a Standardization Lead decision, not made here).

## Item 5. JNJ R&D FY2024 / FY2025 stored 1.84B / 0.109B vs quarter sums 17.2B / 14.7B

Verdict: **wrong values confirmed (FILING-CHECKED). The stored FY values are a cash-flow adjustment line, not R&D expense. Three more FY cells (FY2021-FY2023) are wrong the same way and were not flagged.**

| FY | Stored (`research_and_development`) | Source tag | Correct R&D expense | Locator |
|---|---|---|---|---|
| 2025 | 109M | ResearchAndDevelopmentExpense | 14,665M | 10-K 0000200406-26-000016 R5 "Research and development expense"; the 109 is R10 Cash Flows "Charges for acquired in-process research and development" |
| 2024 | 1,841M | ResearchAndDevelopmentExpense | 17,232M | 10-K 0000200406-25-000038 R5; 1,841 = R10 "Charges for acquired in-process research and development assets" (iXBRL `us-gaap:ResearchAndDevelopmentExpense`, contextRef c-1, in jnj-20241229.htm) |
| 2023 | 483M | ResearchAndDevelopmentExpense | 15,085M | 10-K 0000200406-24-000013 R5; 483 = R10 "Charge for purchase of in-process research and development assets" |
| 2022 | 0 | ResearchAndDevelopmentExpense | 14,135M | same R5; R10 shows 0 |
| 2021 | 0 | ResearchAndDevelopmentExpense | 14,277M (as re-presented in the FY2023 10-K; the original FY2021 10-K printed 14,714M before Kenvue re-presentation) | same R5 |

The face R&D line is tagged `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost` (R5 defref). The quarters come from that tag, so the quarter values are right. The derived Q4s (5,298M for 2024 = 17,232 - 11,934; 4,252M for 2025) are also right, because derivation used the face-tag FY.

Root cause: `research_and_development` maps `ResearchAndDevelopmentExpense` at priority 1 (approved) and `...ExcludingAcquiredInProcessCost` at priority 2 (provisional). JNJ uses the priority-1 tag only for the cash-flow add-back of acquired IPR&D charges. first_match therefore takes a different line from a different statement. This is ledger rule 12 again: the same tag means different things at different filers.

Population scope (DATA-INFERRED, read-only query): in 1,073 company-periods, the stored R&D comes from `ResearchAndDevelopmentExpense` while an authoritative `...ExcludingAcquiredInProcessCost` fact exists for the same period. In 456 of them (81 companies) the two differ by >1%. Each is a candidate for the same error. A filing sample is needed before any precedence change; some filers may put total R&D on the priority-1 tag and use the "excluding" tag for a subtotal.

Proposed rule family **R-STATEMENT-ROLE**: a fact feeding an income-statement concept must come from the income-statement presentation role (FSDS `pre.txt` stmt = IS), not from a cash-flow reconciliation line using the same element. The `xbrl-structure` skill method covers this.

## Item 6. TSLA FY2017 operating income 1,179M "sourced from a Revenues fact"

Verdict: **wrong value confirmed (FILING-CHECKED).** The correct value is -1,632,086K ("Loss from operations"), 10-K FY2017 0001564590-18-002956 R4. The suite's stated reason is a rule artefact; the real cause is below.

`operating_income_resolved` FY2017 = 1,179,271K, `source_fact_ids` [49453658 Revenues 11,758,751K, 49430294 OperatingExpenses 3,855M, 49390897 CostOfGoodsSold 6,724,480K]. It is an arithmetic fallback, Revenues - CostOfGoodsSold - OperatingExpenses. R4 shows `CostOfGoodsSold` is "Cost of revenues - Automotive sales" 6,724,480K, one component. "Total cost of revenues" is 9,536,264K (`CostOfRevenue`). With the total, 11,758,751 - 9,536,264 - 3,854,573 = -1,632,086 ties to the face line.

Root causes:
1. `cost_of_revenue` priorities are CostOfGoodsAndServicesSold (1), CostOfRevenue (2), **CostOfGoodsSold (3, provisional)**. When the FY2017 `CostOfRevenue` copies are not authoritative (thousands in the FY2017 10-K vs millions in later 10-Ks), first_match drops to the component tag. `cost_of_revenue` and `cost_of_revenue_resolved` FY2017 = 6,724,480K: **wrong** (correct 9,536,264K, R4 "Total cost of revenues").
2. `operating_income_resolved` was written 2026-09-13 by the fallback, when `operating_income` had no FY2017 value. `operating_income` now holds the correct -1,632M (fact 49430854, 10-K 0001564590-20-004475, authoritative, resolved 2026-10-18). The insert-only `_resolved` row was never replaced, which is the stale-fallback pattern of ledger 2026-10-17 (company 2835).
3. Suite rule I6 `differs_from_authoritative_copy` compared the multi-source derived cell with the Revenues fact's other copy (11,759M). That comparison means nothing for a calculated cell. The verdict is right, the evidence is wrong. I6 should skip cells with more than one source fact, or compare each source fact with its own copies.

Related TSLA cells in the same family (FILING-CHECKED against the same R4; quarters from the FY2017 10-K R30 Quarterly Results were not opened, the arithmetic uses the stored 10-Q totals):
- `cost_of_revenue_resolved` Q4 2017 = 1,999,631K (derived from the component tag): wrong. Total-basis Q4 = 9,536,264 - (2,028,324 + 2,122,942 + 2,535,535) = 2,849,463K.
- I2 `identity:gross_profit` Q4 2017 flagged `gross_profit_resolved` 438,786K. That value is **right** (3,288,249 - 2,849,463 = 438,786). The wrong term is cost of revenue, so the suite pointed at the wrong cell.
- I5 `cost_of_revenue_resolved` FY2017 6,724,480K vs quarter sum 8,686,432K: true positive (both are wrong-basis mixes).

## Item 7. Values sourced from 8-K filings (LLY, MSFT; also GOOG, AVGO in the same suite rule)

Verdict: **the 8-K values themselves are right as filed (FILING-CHECKED), so most I6 `non_periodic_form` "wrong_value" findings are lineage defects, not wrong values. The real wrong values are cells that combine an 8-K recast figure with an original-basis figure.**

In-window cells (period_end >= 2015) whose source fact is from an 8-K: MSFT 10, GOOG 2, LLY 34, AVGO 4 (DATA-INFERRED listing: `canonical_fact.source_fact_ids` -> `core.filing.form`). Earlier 8-K-sourced cells (JPM 2011, AAPL 2013/2015, MSFT 2013, MU 2014/2017) have period_end before 2015 and are outside the certification window.

**MSFT, 8-K 0001193125-15-353706** (Item 8.01: recast of the FY2015 10-K for the FY2016 segment change; consolidated totals unchanged). All 10 cells (FY2015 revenue 93,580M, Q3/Q4 FY2015 revenue 21,729 / 22,180M, Q4 FY2015 operating income -2,053M, CFO 29,080M, current assets 124,712M, current liabilities 49,858M, total assets 176,223M, total liabilities 96,140M) equal the original FY2015 10-K 0001193125-15-272806 (R5 Balance Sheets, R7 Cash Flows) and the 8-K's own R5/R7/R130. **Values right as originally reported; lineage wrong.** Note: the FY2016 10-K 0001193125-16-662209 re-presents 2015-06-30 (R5: current assets 122,797, total assets 174,472, current liabilities 49,647, total liabilities 94,389) and FY2015 CFO (R7: 29,668). Under the latest-filed rule used for MSFT FY2016 income (item 1), these cells should carry the re-presented values. They come from the 8-K only because it holds the highest fact_id in the conflict group. Both values are defensible; the basis is chosen by load order, not by policy.

**GOOG, 8-K 0001652044-16-000022** (recast for ASU 2016-09). CFO 2015 26,572M equals the 8-K R8 and the FY2016 10-K 0001652044-17-000008 R8: **right**. Capex 2015 9,915M equals the 8-K R8 and the original 10-K, but the FY2016 10-K R8 re-presents it as 9,950M. **Defensible but not the latest filed.** FCF 2015 then mixes the latest CFO with an older capex (16,657M vs 16,622M on the latest 10-K basis).

**AVGO, 8-K 0001730168-20-000126.** FY2017 operating income 2,371M and total operating expenses 6,138M equal the 10-K FY2019 0001730168-19-000144 R4 (Oct. 29, 2017 column); 2019-11-03 shares 397,560,810 equal the FY2019 10-K copy. **Right; lineage only.**

**LLY, 8-K 0000059478-19-000274** (recast of the 2018 10-K for the Elanco disposition as discontinued operations; R2 and R99 Selected Quarterly Data). 26 of 34 cells equal the 8-K exactly (FY2016 revenue 18,312.8M, income before taxes 3,276.3M, taxes 551.4M; 2017 quarterly revenue 4,514.9 / 5,091.6 / 4,961.0 / 5,406.4M, cost of sales Q1 957.7M, operating expenses, taxes, Q4 2017 pretax 397.0M; 2017-12-31 cash 6,211.8M and PP&E 7,885.1M in R5). **Right as re-presented (continuing operations).** The defects:
- **Wrong, mixed basis inside one cell (7):** `gross_profit_resolved` FY2016 12,657.9M = 8-K revenue 18,312.8 (excludes Elanco) minus original 10-K COGS 5,654.9 (includes Elanco). On the recast basis it is 18,312.8 - 4,160.5 = 14,152.3M; as originally reported, 21,222.1 - 5,654.9 = 15,567.2M. Q2 2017 3,540.0M and Q3 2017 3,394.9M (8-K revenue minus original 10-Q COGS 1,551.6 / 1,566.1; recast 3,951.5 / 3,797.5M). `operating_income_resolved` Q2-Q4 2017 776.2 / 716.7 / 727.6M (the same COGS mix). `income_before_tax` Q4 2016 794.3M (derived fact 243581271 = recast FY 3,276.3 minus original 9M).
- **Review, definition (1):** `operating_income_resolved` Q1 2017 974.7M = revenue - cost of sales - "Operating expenses" (R99), all from the 8-K. LLY presents no operating-income line, and R99 "Operating expenses" (R&D plus marketing/SG&A) leaves out acquired IPR&D (857.6M in Q1 2017) and special charges (111.4M). Whether `operating_income` means this is a Standardization Lead decision. Not counted as wrong.
- **Series break:** every other LLY 2015-2017 cell is on the original (Elanco-included) basis, so Q1 2017 revenue (4,514.9M, recast) next to Q1 2016 (4,865.1M, original) makes YoY growth -7%. Same restatement-basis family as item 1. The 2017-12-31 balance sheet mixes recast cash and PP&E with original-basis totals.

Suite tally for this rule. 51 I6 `non_periodic_form` wrong_value findings (S001 41, S002 10):
- **Confirmed wrong (11):** JPM 5; LLY 6 (GP FY2016, Q2, Q3 2017; OI Q2-Q4 2017, all from the mix, not the form).
- **Review (1):** LLY OI Q1 2017 (definition).
- **Refuted, values right as filed (33):** MA 5, MSFT revenue/OI 4, AVGO 3, GOOG CFO 1, LLY 20.
- **Refuted but defensible, not the latest filed (6):** MSFT CA/CL/TA/TL/CFO 2015 (re-presented in the FY2016 10-K), GOOG capex 2015.
The suite's `expected_or_other_value` for the LLY GP/OI cells is the value of one input fact (e.g. Revenues), so its evidence never showed the real defect. Proposed change: split I6 into `lineage_non_periodic_form` (severity review, plus a lineage fix to the 10-K copy where values match) and a separate **R-MIXED-VINTAGE** check: a calculated cell whose inputs come from filings with different restatement bases (8-K recast vs original, or an older vs newer 10-K re-presentation) is `wrong_value`.

## Item 8. AAPL: shares not split-adjusted, EPS split-adjusted

Verdict: **wrong values confirmed (FILING-CHECKED basis; cell list DATA-INFERRED by arithmetic on the filed ratio).** Shares are on the wrong basis for every period before the 2020 split. Eight EPS cells and one DPS cell were also never adjusted.

Filing evidence: 10-K FY2020, 0000320193-20-000096, R8 Summary of Significant Accounting Policies: "On August 28, 2020, the Company effected a four-for-one stock split ... All share, restricted stock unit ('RSU') and per share or per RSU information has been retroactively adjusted". R2: diluted EPS FY2018 2.98, FY2019 2.97, FY2020 3.28; basic FY2018 3.00; weighted diluted shares FY2018 20,000,435K. R6: FY2018 dividends declared per share 0.68.

Stored (`canonical_fact`, AAPL company_id 3):
- `shares_outstanding_resolved`: **45 cells wrong**, 2015-01-09 to 2020-07-17, all as filed before the split (e.g. 2015-09-26 5,578,753,000; adjusted 22,315,012,000). Then 16,976,763,000 on 2020-09-26: a false 4x step in the series. 48 later cells are right.
- `diluted_eps_resolved` FY2018 11.91 (filed adjusted 2.98), Q1-Q3 FY2019 4.18 / 2.46 / 2.18 (adjusted 1.045 / 0.615 / 0.545); `basic_eps_resolved` FY2018 12.01 and Q1-Q3 FY2019; `dividends_per_share_resolved` FY2018 2.72 (filed adjusted 0.68). **9 cells wrong.** The page shows FY EPS 2.30 (FY2017), 11.91 (FY2018), 2.97 (FY2019).
- All other AAPL EPS/DPS cells since 2015 are on the adjusted basis (77 each).
- Suite: the I4 `eps_vs_net_income_over_shares` review findings (ratio about 4.15) are true signals of this defect. They were rated `review`, not `wrong_value`.

Root causes (`pipeline/src/scrooner_pipeline/corporate_actions/stock_splits.py`):
1. `RETROACTIVE_ADJUSTMENT_CONCEPTS` (line 210) holds only diluted_eps, basic_eps and dividends_per_share. Share counts (`shares_outstanding`, weighted averages) are never re-based, though the filer restates them ("All share ... information has been retroactively adjusted").
2. `resolve_retroactive_split_adjustments` skips any (company, period) already in the resolved concept (line 303, insert-only). Cells that an earlier passthrough filled with the as-filed value (AAPL FY2018 to Q3 FY2019) are never corrected. CLAUDE.md already records this "existing rows are skipped" behaviour (2026-10-13 basic_eps backfill).
3. Latent: the adjustment tests only `split effective_date > period end_date`, not whether the source filing came before the split. A pre-split period sourced from a post-split filing (already adjusted) would be divided again if it ever reached this path. Not observed in AAPL or NVDA cells today, but the rule has no guard.

Proposed rule family **R-SPLIT-BASIS** (covers items 3 and 8): each per-share and share cell gets an explicit basis (the cumulative split factor between its source filing date and today). Re-base by that factor, not by period end. Include share counts. Refresh existing rows under a dry-run, not insert-only. The I9 check should compare every cell's basis, not only adjacent jumps of 1.5x or more.

## Other `wrong_value` findings outside the eight items (all checked)

| Company | Finding | Verdict | Evidence |
|---|---|---|---|
| LLY | I4 `total_debt` 2015-09-30 = 9.3M | **Confirmed wrong.** The base concept holds DebtCurrent only; total = 9.3 + 8,069.6 = 8,078.9M (`total_debt_resolved` is right) | 10-Q 0000059478-15-000175 R4 |
| LLY | I5 revenue / income tax FY2016 vs quarter sums | Refuted, basis mix. FY is the Elanco recast (8-K), quarters are original | 8-K 0000059478-19-000274 R2 |
| LLY | I5 share_buybacks FY2016 600.1M | **Mislocated.** FY is right (10-K 0000059478-17-000098 R7 "Purchases of common stock (600.1)"). The wrong cell is Q4 2016 = 60.0M from a quarter context outside the cash-flow statement; CF arithmetic gives FY 600.1 minus 9M 300.1 (10-Q 0000059478-16-000440 R6) = 300.0M | as cited |
| NVDA | I3 DPS Q4 FY2016 -0.165 (as-filed) and -0.0103 (resolved); I9 same cell | **Confirmed (3)**, same family as Visa. 10-K 0001045810-16-000205 R58 tags quarterly rates 0.0975 / 0.115 on 6-month and 12-month contexts | R58 |
| NVDA | I5 income tax Q1 FY2021 64M equals the 9M value | **Refuted, coincidence.** Q1 64, Q2 -13, Q3 12; 9M is 64 | 10-Q 0001045810-20-000065 R2; 0001045810-20-000189 R2 |
| NVDA | I9 shares 2024-08-23 24.53B | **Mislocated.** This cell is right; the 2.46B and older cells are wrong (item 3) | 0001045810-24-000264 R1 |
| TSLA | I2 GP Q4 2017 | **Mislocated.** GP 438.8M is right; cost of revenue is wrong (item 6) | 0001564590-18-002956 R4 |
| TSLA | I5 CFI FY2016 -1,081.1M vs quarters -1,416.4M | Refuted, basis mix. FY from the FY2018 10-K re-presentation, quarters original (likely ASU 2016-18 restricted cash; reason not opened) | core.fact 49424998 vs 78680505 |
| TSLA | I5 COGS FY2017; I5 and I6 OI FY2017 | **Confirmed (3)** (item 6) | R4 |
| TSLA | I5 NI FY2018 -976M | **Mislocated.** FY is right (10-K 0001564590-21-004599 R4 "attributable to common stockholders (976)"). The wrong cells are Q1/Q2 2018, stored from `ProfitLoss` (-784.6 / -742.7M, including NCI) instead of attributable (-709.6M Q1) | 10-Q 0001564590-18-011086 R4 |
| TSLA | I9 shares 2021-12-31 3.1B / 2022-01-31 1.0335B | 2022-01-31 **confirmed** (not adjusted for 3:1 2022-08 although the split is on record; whole pre-split series unadjusted, same as AAPL item 8). 2021-12-31 **mislocated** (right on the current basis) | core.fact 49385699, 49367457 |
| AMD | I3 buybacks Q4 2023 -8M, Q4 2025 -16M | **Confirmed (2).** Negative buybacks, derived from equity-statement values that double count Q2 (next row) | below |
| AMD | I5 buybacks Q2 2023 241M, Q2 2026 221M | **Confirmed (2), filer error.** In the Q2 10-Q equity statements, the 3-month block prints the YTD repurchase (241 / 221) in the total column while treasury stock shows 0 and the 6M cash flow equals Q1 | 10-Q 0000002488-23-000139 R7 + R6; 0000002488-26-000123 R7 |
| AMD | I5 buybacks Q1 2023, Q1 2026 | Refuted (right) | same |
| AMD | I5 CFF Q2 2018 28M = 9M | Refuted, coincidence (6M 20 - Q1 -8 = 28) | core.fact copies of 10-Q 0000002488-18-000128 |
| AMD | I5 NI Q1 2017 -33M = FY | Refuted, coincidence (ASC 606 restated Q1 -33, FY -33) | 10-K 0000002488-19-000011 R2 |
| AMD | I5 pretax FY2017 -15M vs quarters -8M | Refuted, perimeter mix. Quarters and face are "before equity loss" (-8 FY); -15 is after the 7M equity loss, from a later 10-K | R2 same filing |
| WMT | I9 basic EPS Q4 FY2021 -0.2467 | **Refuted.** -0.74 / 3 (2024 split); the release prints basic (0.74) | 8-K 0000104169-21-000022 Ex. 99.1 |
| JNJ | I5 COGS FY2022, interest FY2023 | Refuted, basis mix (Kenvue re-presentation). FY 24,596 and 772 are on the face | 10-K 0000200406-25-000038 R5; 0000200406-24-000013 R5 |
| JNJ | R&D x2 | **Confirmed** (item 5) | |
| GOOG/AVGO/MSFT/MA/LLY I6 | see items 2 and 7 | | |

## I8 `per_share_derived_by_subtraction` (364 of the 462 `wrong_value` findings)
The suite applied a policy and never compared values (`value_checked: false`). By data point:
- `effective_tax_rate_reported` (96): **confirmed as a class.** Subtracting a 9M rate from a FY rate does not give a Q4 rate (e.g. MSFT Q4 FY2018 -1.464). Not filing-checked per cell, but the method is invalid.
- `basic_eps_resolved` / `diluted_eps_resolved` (176): **confirmed as a class by sample.** Apple derived Q4 diluted EPS FY2021 1.23 / FY2022 1.29 / FY2023 1.47 vs earnings releases 1.24 / 1.29 / 1.46 (8-K Ex. 99.1 0000320193-21-000104, -22-000107, -23-000104). With the two ledger cases (MSFT Q4 FY26, AAPL Q4 FY25), 4 of 5 sampled are off by 0.01. Policy (ledger 2026-10-21): show only a filed value or mark unavailable.
- `dividends_per_share_resolved` (92): **mostly not a wrong value.** Declared DPS adds up across quarters when each quarter is declared on one share basis. Apple Q4 FY2021 0.22 is correct. The failures are the rate-on-YTD filers (V, NVDA, item 4), which I3/I9 already catch. This should be `review`, not `wrong_value`, unless R-RATE-ON-YTD fires.

## Suite accuracy: false-positive rate of `wrong_value`
Base: 462 `wrong_value` findings (S001 230 + S002 232).

Non-I8 (98, each checked; 93 FILING-CHECKED, 5 by arithmetic on filed values):
- **Confirmed wrong cell: 39.** LLY 8, NVDA 3, TSLA 4, JPM 5, AMD 4, JNJ 2, V 13.
- **Defect real but the flagged cell is right (mislocated): 5.** LLY buybacks FY, NVDA shares, TSLA GP Q4 2017, NI FY2018, shares 2021-12-31.
- **Review (definition): 1.** LLY OI Q1 2017.
- **Refuted: 53.** Of these, 14 sit in a basis-mix series that both readings can defend (restatement, recast, re-presentation, perimeter). 39 are plain false positives: 33 lineage-only (value right, source form wrong: MA 5, LLY 20, MSFT 4, GOOG 1, AVGO 3) and 6 coincidences / right values (NVDA tax, AMD CFF, AMD NI, AMD buybacks Q1 x2, WMT EPS).
- **Non-I8 false-positive rate: 53 / 98 = 54%** (59 / 98 = 60% if mislocated and review findings also count as misses on the flagged cell).

I8 (364): ETR 96 + EPS 176 confirmed as classes = 272. DPS 92: 14 at the rate-on-YTD filers (V 9, NVDA 5) count as wrong (DATA-INFERRED from the filing-checked cause); 78 are false positives.

**Whole suite:** 325 of 462 confirmed or confirmed-as-class (70%), 131 refuted (28.4%), 6 mislocated or review (1.3%). **False-positive rate: 28% overall (30% counting mislocated); 54% outside I8; I6 non_periodic_form alone 78% (40 of 51).**

Rule-level breakdown (for threshold tuning):
- I6 `non_periodic_form`: 11 / 51 confirmed. Mostly lineage → make it `review`, plus R-MIXED-VINTAGE.
- I5 `quarters_do_not_sum_to_year`: 5 confirmed, 3 mislocated, 7 basis-mix refutes out of 15 → compare against a same-vintage FY first.
- I5 `quarter_equals_longer_window`: 2 / 7 confirmed, 3 coincidences → require the quarter to also differ from its own 3-month filed copy, or a decimals-aware equality on non-rounded values.
- I3 `negative_on_nonnegative`: 13 / 13 confirmed. Keep.
- I9: 6 / 9 confirmed, 2 mislocated, 1 refuted (genuine loss quarter) → flag the series and both sides of a jump, and exclude sign flips that equal a filed loss.
- I2 identity: 0 / 1 (mislocated).
- I4 layer_disagreement: 1 / 1.
- Coverage gap: the suite caught only a small part of the real defects. NVDA about 216 wrong-basis cells, AAPL 54, V FY/zero DPS 15, JNJ R&D FY2021-23 3, JPM Q4 5. Detection recall is the bigger problem than precision. Run the I9 basis check per cell (R-SPLIT-BASIS).

New rule families proposed: R-BASIS (restatement basis mix), R-MIXED-VINTAGE (a calculated cell from mixed-basis inputs), R-SPLIT-BASIS (per-cell split factor, including shares; refresh not insert-only; duration-context and 46-day split disclosures), R-RATE-ON-YTD (quarterly rate tagged on YTD/FY), R-STATEMENT-ROLE (JNJ cash-flow line under an IS tag), AMD equity-statement Q2 YTD duplication (filer quirk; prefer cash-flow YTD-derived quarters).

## Extra check (coordinator request): EMR FY2022 and NTAP FY2026 `revenue_sanity_resolved`

**EMR FY2022 (2021-10-01..2022-09-30): stored 1,660,000,000. Wrong (FILING-CHECKED).** Source: `core.fact` 2733743, tag `us-gaap:Revenues`, **undimensioned** context 2021-10-01..2022-09-30, filed in **10-Q** Q2 FY2023 0000032604-23-000030 (emr-20230331.htm, displayed "1.66", scale 9). The text is the acquisitions note: "On April 12, 2023, Emerson announced an agreement to acquire National Instruments Corporation ... NI ... had revenues of $1.66 billion in 2022". It is the **acquisition target's revenue**, tagged with Emerson's own total-revenue element on Emerson's fiscal-year context. Emerson's total is 13,804M (`RevenueFromContractWithCustomerExcludingAssessedTax`, fact 2733645, 10-K 0000032604-24-000041; the `revenue` concept holds it correctly). `revenue_sanity_resolved` took the bare `Revenues` fact ahead of the face RCFC (written 2026-09-08, never refreshed).

**NTAP FY2026 (2025-04-26..2026-04-24): stored 6,237,000,000. Wrong (FILING-CHECKED).** Source: `core.fact` 30584531, tag `us-gaap:Revenues`, **undimensioned** context C_8b080b7c-... (2025-04-26..2026-04-24), 10-K 0001193125-26-259683 (ntap-20260424.htm, MD&A p.40 table "Hybrid Cloud Segment Net Revenues by Storage Category", row "Hybrid Cloud segment net revenues $6,237"). It is a **segment total tagged without the segment axis**. Consolidated "Net revenues" on R4 is 6,925M (`RevenueFromContractWithCustomerExcludingAssessedTax`, fact 30584245). The same error hits FY2025 (stored 5,907 = Hybrid Cloud, fact 30584530; face 6,572) and FY2024 (stored 5,657, fact 30584528; face 6,268): **3 wrong cells** for NTAP.

Rule (supports data-team/37 revenue-total rule): an undimensioned `Revenues` fact is not proof of a consolidated total. It can be an acquiree's revenue in a narrative note (EMR) or a segment table missing its axis (NTAP), same as GE ledger 2026-10-21. Accept a total-revenue fact only if it sits on the income statement presentation (FSDS `pre.txt` stmt = IS) or equals the face line for the same context. Prefer the face RCFC when a bare `Revenues` fact is smaller than it by more than rounding.

Status: COMPLETE for items 1-8, the extra EMR/NTAP check and all 98 non-I8 findings. I8 was judged by class with a 3-case filing sample.
