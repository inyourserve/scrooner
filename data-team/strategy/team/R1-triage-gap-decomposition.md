# R1. Top-1000 gap decomposition by root cause (Data Triage, 2026-10-21)

Role: Data Triage (17). Read-only. No DB query ran, no filing was opened by me, nothing was written except this file (plus one line in tags/feedback-inbox.md, standing rule).
Status: PARTIAL. Every cell count below is a projection from files, not a fresh query, because the pooler stayed above the gate (`select count(*) from pg_stat_activity` returned 18, 22, 21, 21, 19 on five attempts; gate is <= 14). The exact SQL that turns the estimates into measurements is in section 8.

## 0. Evidence classes used here
- MEASURED-DB (by another agent, a DB query, cited file): `shards.csv` baseline (2026-10-18), `data-team/31` section B (Tag Mapper, top 1000, 2026-10-21), `data-team/36` (Verifier), shard "population" counts in `results/S0xx.md`.
- FILING-CHECKED: only where the cited shard/Verifier file says it opened the filing (I did not re-open any). Counted separately below.
- ESTIMATE: my projection or allocation. Every ESTIMATE says how it was built. None is a rate to accept; they size where to work.
- Sample caveat: shards S001-S045 are ranked by market cap, not random. Rates describe the examined companies; later ranks (S046-S100, 550 companies) have NOT been examined (workload sample, not a rate).

## 1. Baseline and the has_value overcount
- Cohort: 986 non-excluded companies x 163 data points = 160,718 cells (`shards.csv`, MEASURED-DB, baseline 2026-10-18, old definition).
- Old definition: filled 130,787 (81.4%); blank 29,931, of which 13,349 (44.6%) carry NO reason.
- The overcount (`coverage_matrix.py:746`, `bool_or(value is not null)` over all periods) is fixed in code (commit fb26fb6, 2026-10-19, `has_value` = latest period; old figure kept in `has_value_any_period`, migration 0096). Whether the live table was rebuilt and 0096 applied is NOT_RUN (DB unreachable); the 2026-10-20 shard counts behave as if it was.
- Correction, two independent routes (both DATA-INFERRED):
  1. Hidden cells counted per company in the three shards that measured them: S014 79, S018 65, S019 69 = 213 over 29 companies = 7.3 per company.
  2. 2026-10-20 blank totals vs the 2026-10-18 baseline for ten shards (S020, S021, S023, S027, S028, S029, S040, S042, S043, S044): +694 over 100 companies = +6.9 per company (range 2.7 to 9.9 by shard).
  - Use 7.0 per company: about 6,900 hidden blanks (range 5,500 to 8,500). Corrected blank cells about 36,800 (35,400 to 38,400); filled about 123,900 = 77.1% (76.1 to 78.0). The headline 81.4% overstated by about 4 points.
  - What the hidden cells are (S019 detail, 69 cells, ESTIMATE of shares): unmapped-tag cascades (interest coverage, NII, pretax, AR) 33%; cover-date share pairing (book value per share, net cash per share, Piotroski) 22%; TTM/YTD-only chains and growth 10%; correct reasoned blanks (negative-base CAGR, no inventory) 24%; member-only cost 9%; unknown 2%.

## 2. Method (so the numbers can be challenged)
1. The only cell-level cause classification that exists is the shard workers' own tables (S001-S019: `not_applicable`, `NR-F` filing-checked not-reported, `SNR` suspected not-reported, `mapping_gap`, `derivation_gap`, `period_gap`, `unknown`). I parsed 169 company rows (S002, S003, S005-S019) plus S004; S001 only as totals.
2. Stratified projection: three strata (banks SIC 6020-6036; other financials 6000-6799; non-financials), sample cause shares per stratum applied to the MEASURED cohort blank total of that stratum (banks 2,209 blank cells/40 companies; other financials 8,299/169; non-financials 19,423/777). Sample: 8 banks, 21 other financials, 143 non-financials (excluded companies removed). Financials are thin in the sample, so the C and B shares carry the widest error.
3. Re-bucketing into A-G used the family tables in S002-S045 (company hit counts) and `data-team/31` section B. The splits I had to assume are marked ASSUMED in section 3.
4. The old-definition projection reproduces the cohort total (29,924 vs 29,931).

## 3. Blank cells by root cause, top 1000 (corrected definition, about 36,800 cells)
| Bucket | Cells (range) | Share | Companies with at least one cell (ESTIMATE) | Evidence | What is in it |
|---|---|---|---|---|---|
| A vocabulary: tag filed, not mapped | 4,900 (3,800-6,000) | 13% | 800-900 (80-90%) | DI; FC on named cases (S009-S019, S016 EOG, S019 SLB/LITE) | Interest expense (`InterestExpenseNonoperating`, `InterestAndDebtExpense`), `OtherNonoperatingIncomeExpense`, `ReceivablesNetCurrent`, `IncreaseDecreaseInReceivables`, `PaymentsOfOrdinaryDividends`, `PaymentsForRepurchaseOfEquity`, E&P/utility/REIT/software capex tags, `us-gaap:Cash`, PP&E incl. finance-lease ROU, instrument-only debt (66 top-1000 companies at latest FY: NET, PANW, SNOW, CME, CDNS, DLR, O, ILMN, DHI), opex totals, continuing-ops-only EPS. Built as: 65% of `mapping_gap` (2,600) + 33% of hidden (2,300). 65% is ASSUMED from the S014-S019 cell lists |
| B composition / perimeter | 3,700 (2,800-4,800) | 10% | 600-700 (60-70%) | DI; FC on named cases | Combined lines that must not be mapped as plain AP/AR (about 1,800 cells, 30% of companies for AP-and-accrued, ASSUMED 4-5 cells each), D&A filed as components, total liabilities not tagged but derivable (about 25% of companies), cost of revenue only on product/service members, MLP/partners' capital template (EPD 25 cells), total-debt composition, member-only lines |
| C applicability: line legitimately not presented, or cell does not apply | 20,900 (17,000-23,000) | 57% | 986 (100%) | NR-F cells FILING-CHECKED about 4,400 before the combined-line carve-out; the rest DI/ASSUMED | See split below |
| D period / history / date alignment | 3,800 (3,000-4,600) | 10% | about 900 (90%) | DI | Cover-date share count vs balance-sheet date (D1: book value per share, net cash per share, Piotroski shares; blank at 8-10 of 10 companies in every shard S021-S045), YTD-only D&A/capex/dividends breaking TTM, 52/53-week and 16-week quarter labels, predecessor CIK history, restatement basis, history before listing |
| E ingestion: facts never reach us | 1,400 (900-1,900) | 4% | 220-260 (22-26%) | MEASURED-DB for counts of companies; cells ESTIMATE | Latest 10-Q in `core.filing` with 0 facts and absent from SEC companyfacts (48 of about 450 examined = 10.7%, CI 8-14%; population 150-190 filings); filing never indexed (HPQ, MDB); stale fetch (DE); dimension-only facts (dual-class cover shares: 127 top-1000 companies lack the cover count in every filing; class-dimensioned EPS; segment-only debt/capex at GM, KKR, PCAR, F, FCX); custom-extension-only tags (NEE capex, SLB current debt, ISRG/ACN/SCHW D&A); no 10-KT rows |
| F resolver bug producing a blank | 100 | 0.3% | n/a | DI | Wrong zero blocks a fallback; see section 4 for the wrong-VALUE classes, which are the main F content |
| G unknown | 2,000 (1,500-2,600) | 5% | n/a | n/a | Remaining `unknown: other` after removing `employee_count`. Needs a classifier; a blank with no reason and no filing check cannot be assigned |

### 3a. Split of C (ESTIMATE, built from shard narratives S003-S045)
| Sub-class | Cells | Evidence |
|---|---|---|
| Four universal cells (`bdc_total_investment_income`, `collaborative_arrangement_revenue`, `net_lease_revenue`, `employee_count`) at nearly every company | 3,500-3,900 | DI/SNR (named at 10 of 10 in every shard); `employee_count` is a dei tag filed by about 6% of examined companies (T, ETN, CSX file it) |
| Dividend, buyback and cash-return chain at non-payers (8-10 cells each, reason missing) | 3,500-4,500 | DI. Population: 3,242 companies have `dividends_per_share` blank with no reason (S021, MEASURED-DB, population not cohort); cohort share 40-50% ASSUMED |
| Sector-template cells at financials (banks 55-62 each; brokers, insurers, REITs, asset managers 24-45): current assets, working capital, inventory, gross profit, EBITDA, FCF | 6,000-7,500 | MEASURED-DB: financials SIC 6000-6799 are 209 companies (21%) but 10,508 of 29,931 old blank cells (35%); banks alone 2,209 |
| Other filing-checked NR-F (line absent on the face: R&D, inventory, interest income, cost of revenue, gross profit) | 3,000-4,000 | FILING-CHECKED in S002, S009, S012-S019 (4,400 NR-F cells before carve-out; recorded in 11 of 19 shards only, so a lower bound) |
| Correct reasoned blanks (negative-base CAGR, pre-listing history) | about 1,700 | DI, from the hidden-cell allocation |
- Only the NR-F row and the cases where a worker opened the statement can call a blank structural. Of C, roughly 20% is filing-checked; 80% is "leaning structural" and stays in the denominator as unresolved until checked.

### 3b. Reason coverage (the user-visible standard)
- Blank cells with no reason: 13,349 of 29,931 (44.6%, MEASURED-DB, old definition). Strata: non-financials 8,640, other financials 3,782, banks 927.
- The hidden cells (about 6,900) carry a null or a wrong-flavour reason too (S014: null). So 36-46% of blank cells have no honest explanation today, independent of any data fix.
- Wrong reasons (blank cell, false explanation), MEASURED-DB population counts from shard queries (not top-1000): `financial_institution_interest_income_not_revenue` on 328 companies, 142 of them not SIC 6xxx (S023); `pre_revenue_biotech_pharma` on 495 companies, 366 with stored revenue, 29 above $500M revenue (S026, S032); `no_dividend_history` on 3,433 cells, 502 with `dividends_paid` stored (upper bound for the false set, S021).

## 4. Displayed values that are wrong or misleading (not blanks)
Each class is assigned to one bucket by the permanent root cause. Rates are over examined companies (S001-S045, about 450, non-random); "x986" is the naive projection; intervals are Wilson 95%.
| Class | Bucket | Examined hits | Rate (CI) | x986 | Evidence |
|---|---|---|---|---|---|
| Stale value shown as current (old value, new tag unmapped or member-only) | A (member-only cost and custom tags: B/E) | 107 of 138 (S002-S019) | 78% (70-84) | about 765 companies; about 3.5-4 cells each = 3,000-3,900 cells | FC in S013-S019 (R-pages), DI elsewhere. The cells count as FILLED in the old measure and are not in section 3. Interim control: a staleness guard (marks unavailable); permanent fix: the vocabulary |
| total_debt wrong, displayed concept `total_debt_resolved` | B (composition), F (wrong zero) | MEASURED top-1000 latest FY (998): 50 flagged by identity tests (5.0%), 18 below a filed instrument tag, 76 blank while debt is filed, 18 indeterminate. All periods since 2015: 51 double counts, 83 current-omitted, 463 outside-list short-term omitted, 171 bare-tag, 636 below an instrument tag, 77 wrong zeros (148 companies across both concepts) | 5-7% identity-detectable | 50-70 companies | DI (file 31 B2/B3). Shards claim "any wrong debt row 50%" (74 of 149): that includes the legacy base `total_debt`, which no metric reads (file 31, code read). Filing-checked resolved errors in S009-S019 (SLB custom tag, CMI bank loans, LITE, MAR, UBER double count) are not identity-detectable, so the true displayed rate is between 5% and about 15-25%: unresolved |
| Revenue = contract subset or component instead of the face total, either direction | F (precedence) | 33 of about 450 FC-or-DI hits | 7% (5-10) | about 70 | FC mostly (AMT, CEG, FCX, DUK, KMI, WMB, AXP, MET, ADM). MEASURED potential: 467 top-1000 companies file both tags; they differ by >1% in 4,479 periods at 201 companies (Revenues larger 3,990, contract tag larger 489), so no fixed priority is right |
| Proxy (DEF 14A) or 8-K value wins over the 10-K | F | about 10 | 2% (1-4) | about 22 | FC for MRK, SCHW, MDT (DI), JPM 5 FY + 5 Q4 cells and MA (Verifier, data-team/36 item 2: Stage 2e conflict grouping and the safe-fill path have no form filter). Population unmeasured |
| Net income includes noncontrolling interest (`ProfitLoss` fallback) | F | about 15 | 3.3% (2-5) | about 33 | FC: FCX, AMT, CMI, OXY |
| Gross margin from a partial cost line | F | 11 of 150 | 7% (4-13) | about 70 | FC: UNH, CVX, ELV, WM, RCL, RSG |
| Operating income = revenue minus a partial `OperatingExpenses` | F | population count 168 companies (S023, MEASURED-DB) | n/a | top-1000 share unmeasured | FC: DVN, CASY, AJG, EQR |
| Derived Q4 per-share, sign-impossible and basis-mixed derived values | D/F | KLAC, V, WELL, DIS, TPL, JBHT, MDT, FTNT | about 2% named | every derived Q4 EPS is unverifiable (MSFT 4.80 vs 4.81 filed, AAPL 1.84 vs 1.85) | FC |
| Split-adjustment: split missing or counted twice | F | NVDA 216 wrong display cells (FC arithmetic, data-team/36 item 3). Population: 156 companies have a forward-split ratio fact on a non-instant context and no split row; 12 have the same split recorded twice | 156 of 986 candidates | up to a per-share series per company | DI population, FC anchor; the detector ignores duration-context facts and its 45-day merge window is too short. Each candidate needs a filing check; do not extrapolate cells |
| Restatement basis mix (FY from the restated later 10-K, quarters from the originals) | D | MSFT FY2016/FY2017 (FC) | unmeasured | every ASC 606 full-retrospective adopter for FY2016-17 | FC: MSFT 0001564590-18-019062 R2 vs 0001193125-16-662209 R2; breaks growth and TTM vs FY |
| Market cap / share count wrong | F | 7 confirmed (S000, FC); multi-class cover understated (EXPE, NKE, IBKR); SHOP 0 shares | 0.7% (0.3-1.5) confirmed | 7 + about 10% multi-class stale (ESTIMATE) | FC for the 7 |
| Meaningless ratios shown as numbers (negative equity or earnings, near-zero denominators) | F | named in most shards | trailing_pe negative in 1,634 of 4,287 stored values (population, S025) | cohort share unmeasured | DI; blank-only guard |
| Bank/broker/exchange revenue and total debt | B/F | 30 banks: 59 wrong values, 38 metric cells (data-team/32, FC) | 40 banks suppressed at serve time (5b96ff2/153574d); brokers/exchanges/asset managers (36) and other credit (14) not suppressed | about 90 financials outside the suppression | FC for the 30 banks |
- The most trust-damaging class by reach is the first (stale-as-current), not any single-tag error.

## 5. Top 10 concepts (families) by lost cells
Lost = blank + stale-displayed, top 1000, ESTIMATE = (companies affected, from shard hit rates or file 31 counts) x (cells per cascade from the shard cell lists). Overlaps are not removed (#3 and #9 overlap by about 300-500).
| # | Concept family | Lost cells | Bucket | Basis |
|---|---|---|---|---|
| 1 | Dividend / buyback / cash-return chain at non-payers and unmapped payers | 3,500-4,500 | C (reason layer), A for payers (`PaymentsOfOrdinaryDividends`, `PaymentsForRepurchaseOfEquity`: 426 filers) | 8-10 cells x 40-50% non-payers; 3,242-company population count |
| 2 | Per-share date pairing: `book_value_per_share`, `net_cash_per_share`, Piotroski shares, `share_dilution_trend`, `total_shareholder_yield` | 2,100-2,800 | D | blank at 85% of examined companies (S021-S045: 7 to 10 of 10 every shard) x 2.5-3.3 |
| 3 | Interest expense / coverage / NII (stale or blank) | 1,800-2,300 | A | 5-8 of 10 companies in every shard S002-S019; `InterestExpenseNonoperating` is not a single-tag mapping (I-2 = 136 periods, I-3 larger in 723) so the fix is a rule, not one line |
| 4 | Total debt and its cascade (D/E, net cash, net cash per share, zero_debt, ROIC, Piotroski, split) | 2,000-2,300 | A 66 instrument-only + B 50-70 flagged + C/E1 107 no-tag + 17 zero | file 31 B2 counts (MEASURED-DB) x 9 cells |
| 5 | Receivables/payables working-capital chain (AR, debtor days, cash conversion cycle, AR/AP change reconciliation) | 1,500-2,000 | A (`ReceivablesNetCurrent` 739 filers, `IncreaseDecreaseInReceivables`) + B (combined lines) | 40% of companies x 4-5 |
| 6 | EBITDA family (D&A, EBITDA, margin, EV/EBITDA, debt/EBITDA, net debt/EBITDA) | 1,200-1,700 | B (components) + E (custom) + D (YTD-only D&A) | 20-25% of companies x 6-7 |
| 7 | Capex and the FCF chain (9-15 cells) | 900-1,400 | A (E&P 60-72 filers, utility, REIT, software, "other productive assets") | 8-10% of companies |
| 8 | Universal industry cells (bdc, collaborative, net_lease, employee_count) | 3,500-3,900 | C | lowest effort, zero data gain, pure denominator/reason correction |
| 9 | Shares outstanding for multi-class and Up-C issuers | 1,000-1,500 | E | 127 top-1000 companies lack the cover count in every filing; 96 lack it in 2026 filings (file 31 B9); 8-12 cells each |
| 10 | Cost of revenue / gross profit / operating expenses / operating income (member-only, partial cost, total opex unmapped, no subtotal) | 800-1,500 | B/A/C mix | 2-6 cells x about 25% |
Next in line: sector-template cells for 209 financials (6,000-7,500, C, a template not a concept); 0-facts latest quarter (about 100 companies, about 10 TTM-chain cells each, 1,000, E); `other_income_expense_net` (350-700, A); total liabilities derivable (about 250, B).

## 6. Expected gain per bucket if fixed (ESTIMATE; nothing here is a target to accept)
Recovery rates are judgements from how many named cases survived coexistence checks in `data-team/31` and the Verifier files.
| Bucket | Blank cells | Recoverable as correct values | Cells gained | Also removes wrong values | Gate |
|---|---|---|---|---|---|
| A vocabulary | 4,900 | 75-85% | 3,700-4,200 | most of the 3,000-3,900 stale-as-current cells | per-tag full-population coexistence check; interest and debt are rules, not single tags |
| B composition | 3,700 | 45-60% | 1,700-2,200 | total_debt 50-70 companies, D&A | Standardization definitions plus an accountant (perimeter changes) |
| C applicability | 20,900 | 0 | 0 (denominator and reason correction) | wrong reasons: 142 + 366 + up to 502 companies | Sector Analyst rules; only filing-checked evidence removes a cell from the denominator |
| D period / date | 3,800 | 65-75% | 2,400-2,900 | cross-basis growth, derived-Q4 EPS | Period Engineer; D1 needs a rule for which share count pairs with which balance sheet |
| E ingestion | 1,400 | 70-85% | 1,000-1,200 | dual-class EPS and cover shares, 0-facts quarter at about 100 companies | instance/FSDS reader with a 50-accession exact-match self-test (file 33 B) |
| F resolver | 100 (blank) | n/a | n/a | F carries most wrong values: precedence (201 candidate companies), proxy, NCI, partial cost, splits (156 candidates) | dry-run plus zero-wrong Verifier sample |
| G unknown | 2,000 | 0 until classified | 0 | n/a | classifier plus filing sample |
- Total fill gain if A, B, D, E all land at the mid recovery rates: about 9,700 cells. Fill rate (all 160,718 cells): 77.1% now to about 83.1%.
- On an applicable denominator that excludes ALL of C (an upper bound, because only about 20% of C is filing-checked): 88.6% now to about 95.5%. With only the filing-checked C excluded the gain is smaller; say which denominator is used.
- Reading: of the 36,800 blanks, tag non-uniformity (A + B) is about 23%. The largest block is C (57%): it is a denominator and reason problem, not a mapping problem. D (10%) is pipeline logic, not tags. The tag/perimeter problem is dominant in WRONG values, not in blanks.

## 7. Where the needle moves, in order (impact per effort; for the Chief)
1. Reason layer and denominator (C): no accountant, no data risk, removes the 44.6% unexplained share and about 10,000 reasonless cells (universal cells 3,700 + non-payer chain 4,000 + sector templates). Fixes the user-visible standard fastest.
2. D1 per-share pairing (D): about 2,100-2,800 cells, no new data, one rule.
3. Staleness guard now (interim, F) + interest-expense and debt rules (A/B): turns the 78% stale-as-current class into marked-unavailable immediately, then into values.
4. Ingestion reader (E): about 1,000-1,200 cells plus quarter freshness at about 100 companies; only needed beyond that if the vocabulary work shows custom/dimensional lines.
5. Precedence and proxy-form rules (F): few cells, highest trust damage per company; needs the dry-run discipline.
6. Classify G (2,000 cells) before claiming completeness.

## 8. Not verified, and the exact queries that would settle it
NOT_RUN and UNTESTED SQL (DB unreachable; column and table names taken from migrations/code, not executed; run only when `select count(*) from pg_stat_activity` <= 14, one connection, `set statement_timeout = '20s'`, chunk `company_id = any(%s)` by 100 ids from `shards.csv`):
```sql
-- Q1: cohort blanks by reason and data point (verifies sections 1 and 3b)
select data_point_name, has_value, has_value_any_period, gap_reason, count(*)
from analytics.company_data_point_coverage where company_id = any(%s) group by 1,2,3,4;
-- Q2: hidden-cell count (needs migration 0096 applied and a rebuild after fb26fb6)
select count(*) from analytics.company_data_point_coverage
where company_id = any(%s) and has_value_any_period and not has_value;
-- Q3: period causes for the cohort
select gap_cause, count(*) from analytics.period_gap where company_id = any(%s) group by 1;
-- Q4: 0-facts latest filings in the cohort
select f.company_id, f.accession_number from core.filing f
where f.company_id = any(%s) and f.form in ('10-Q','10-K') and f.filing_date >= date '2026-07-01'
  and not exists (select 1 from core.fact x where x.filing_id = f.id);
```
Other unmeasured items: S046-S100 (550 companies) never examined; sector share of the 65/22/10/3 split of `mapping_gap` is ASSUMED; the combined-line carve-out (1,800 cells) is ASSUMED; C's filing-checked share (about 20%) is a lower bound; stale-as-current cells per company (3.5-4) come from 20 companies (S014, S019); the 156 split candidates and 168 W3 companies were not intersected with the top 1000; no cell-level classification of the 13,349 unexplained cells exists beyond the shard narratives.
Unverified claims from older docs that this analysis contradicts or narrows: (1) "the pipeline does not drop mapped data" (infra map section 8): SEC companyfacts itself drops custom, dimensional and about 10% of the latest 10-Q accessions, so bucket E is real; (2) shards' "50% have a wrong debt row": base-row inflated, displayed rate 5-25%.

## 9. Hand-offs
- Data Engineer: Q1-Q4 above when the pooler is free; confirm 0096 applied and a post-fb26fb6 rebuild; reader for bucket E.
- Sector Analyst + Standardization Lead: bucket C template rules (financial strata) and the four universal cells.
- Period Engineer: D1 pairing rule, YTD-only D&A/capex/dividends.
- Tag Mapper: A list in section 5 (#3, #4, #5, #7) with coexistence checks; revenue precedence needs the presentation-linkbase rule (file 31 B8).
- Verifier: filing-check 30 cells of the 36-46% reasonless blanks (classify structural vs ours), the 156 split candidates (sample), and 20 stale-as-current cells outside S013-S019.
- Chief: decide whether "reasoned unavailable" counts as done for C before any coverage claim.
