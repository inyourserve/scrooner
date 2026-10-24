# S4. What the 13,349 no-reason blanks are (Data Verifier, 2026-10-22)

Role: Data Verifier (16). Read-only on DB and code. Scope: top-986 cohort, `data-team/strategy/data/cohort_cells.csv` rows with `has_value=f` and empty `gap_reason` (13,349, re-counted), groups from `group_assignment_draft.csv` (DRAFT, unaudited). DB: 9 read-only queries, one connection each, `default_transaction_read_only=on`, statement_timeout 60s, pg_stat_activity 16-21 (gate <= 40). SEC: 40 filings, FilingSummary + statement R-files (+3 main documents for employee counts, deleted after use), declared User-Agent, <= 1.7 req/s, 44.3 MB total downloaded, all deleted after use. Status: COMPLETE for the sample; extrapolation is a model (section 5).

## 1. Mechanism: "no reason" means "never computed", not a separate failure (code read + DATA-INFERRED)
- `pipeline/src/scrooner_pipeline/mapper/coverage_matrix.py` `build_coverage` (L700-800): concept rows get `has_value` from "any canonical_fact in any period" and get a reason ONLY from `classify_concept_gaps` (revenue family, L180) or `apply_filing_line_evidence` (9 concepts, L262-321). Metric rows take `is_null_reason` of the latest `metric_value` row. Ownership rows have no reason mechanism.
- Measured on the 13,349: **9,564 concept cells, all with 0 canonical_fact rows in any period** (query over every cell); **3,723 metric cells, all with 0 metric_value rows** (the metric engine writes no row, hence no reason, when an input never exists); **62 ownership cells** (insider 5, institutional 6, mutual fund 51).
- Lineage state of the 9,564 concept cells (`analytics.company_concept_lineage`): mapped tag filed 0; a candidate tag filed 1,336; nothing filed 6,528; no lineage row 1,700. So the pipeline drops nothing it maps; every concept blank is vocabulary, template or real absence.
- Metric cascades (DATA-INFERRED, joins to cohort_cells): of no-reason metric cells with defined inputs, 691 have a no-reason input, **594 have an input that already carries a reason that is not propagated** (e.g. inventory_days 282 and payables_days 280 blank because cost_of_revenue has `line_not_presented_in_filing`; fcf_growth_* 88 x3 because fcf has `incomplete:subtract`), 37 have all inputs valued (any-period; RBA below shows these can be stale-input cases, not arithmetic defects).

## 2. Breakdown: top 40 data points (13,349 total, 109 data points)
Group columns: corp / bank / reit / insurer / other_fin / bdc_fund_or_unclassified / utility / energy / no_revenue_line.
| # | data point | no-reason | corp | bank | reit | ins | oth_fin | bdc/unc | util | energy | norev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | collaborative_arrangement_revenue | 982 | 697 | 40 | 54 | 28 | 49 | 29 | 50 | 34 | 1 |
| 2 | bdc_total_investment_income | 957 | 701 | 40 | 54 | 28 | 49 | 0 | 50 | 34 | 1 |
| 3 | employee_count | 925 | 653 | 39 | 53 | 26 | 46 | 28 | 48 | 31 | 1 |
| 4 | net_lease_revenue | 861 | 649 | 25 | 16 | 27 | 46 | 29 | 38 | 30 | 1 |
| 5 | ap_change_reconciliation_gap | 436 | 226 | 40 | 46 | 27 | 35 | 29 | 16 | 17 | 0 |
| 6 | inventory_change_reconciliation_gap | 423 | 201 | 40 | 50 | 27 | 46 | 28 | 16 | 14 | 1 |
| 7 | cf_ap_change | 422 | 219 | 40 | 46 | 26 | 33 | 27 | 15 | 16 | 0 |
| 8 | cf_inventory_change | 413 | 192 | 40 | 50 | 27 | 46 | 28 | 16 | 13 | 1 |
| 9 | ar_change_reconciliation_gap | 381 | 193 | 40 | 37 | 26 | 27 | 25 | 23 | 9 | 1 |
| 10 | cf_ar_change | 365 | 183 | 40 | 36 | 25 | 24 | 24 | 23 | 9 | 1 |
| 11 | other_income_expense_net | 314 | 201 | 0 | 27 | 23 | 13 | 24 | 12 | 14 | 0 |
| 12 | total_debt_split | 306 | 151 | 37 | 44 | 15 | 32 | 15 | 6 | 5 | 1 |
| 13 | dps_growth_yoy | 296 | 264 | 0 | 2 | 4 | 13 | 1 | 7 | 5 | 0 |
| 14 | dps_growth_3y_cagr | 296 | 264 | 0 | 2 | 4 | 13 | 1 | 7 | 5 | 0 |
| 15 | dividends_per_share_resolved | 294 | 263 | 0 | 2 | 4 | 12 | 1 | 7 | 5 | 0 |
| 16 | dividends_per_share | 294 | 263 | 0 | 2 | 4 | 12 | 1 | 7 | 5 | 0 |
| 17 | inventory_days | 291 | 99 | 39 | 33 | 21 | 36 | 27 | 22 | 13 | 1 |
| 18 | payables_days | 291 | 99 | 39 | 33 | 21 | 36 | 27 | 22 | 13 | 1 |
| 19 | dividends_paid | 280 | 246 | 0 | 3 | 4 | 15 | 1 | 6 | 4 | 1 |
| 20 | dividends_paid_resolved | 280 | 246 | 0 | 3 | 4 | 15 | 1 | 6 | 4 | 1 |
| 21 | total_liabilities | 190 | 149 | 0 | 2 | 1 | 0 | 0 | 29 | 9 | 0 |
| 22-27 | current_liabilities(_resolved), current_assets(_resolved), current_ratio, working_capital (each) | 167 | 13 | 40 | 44 | 16 | 27 | 27 | 0 | 0 | 0 |
| 28 | quick_ratio | 160 | 9 | 40 | 43 | 15 | 26 | 27 | 0 | 0 | 0 |
| 29 | amortization_of_intangibles | 151 | 69 | 0 | 20 | 7 | 5 | 14 | 14 | 21 | 1 |
| 30 | sga_expense | 149 | 35 | 40 | 1 | 13 | 17 | 17 | 25 | 1 | 0 |
| 31-32 | interest_expense(_resolved) (each) | 136 | 114 | 1 | 3 | 1 | 10 | 0 | 5 | 2 | 0 |
| 33 | total_debt | 129 | 96 | 5 | 6 | 4 | 8 | 4 | 3 | 2 | 1 |
| 34-35 | depreciation_and_amortization(_resolved) (each) | 126 | 61 | 17 | 7 | 15 | 6 | 12 | 4 | 4 | 0 |
| 36-38 | fcf_growth_3y/5y/yoy (each) | 95 | 19 | 9 | 26 | 8 | 8 | 10 | 4 | 11 | 0 |
| 39-40 | share_buybacks(_resolved) (each) | 89 | 53 | 1 | 14 | 1 | 7 | 0 | 9 | 3 | 1 |
Group totals: corporate 7,679; reit 1,315; other_financial 1,012; bank 927; bdc_fund_or_unclassified 715; insurer 651; utility 577; energy 446; no_revenue_line 27. The top 40 rows hold 11,875 (89%). Rows 41-109 (1,474) are listed in the scratch output; largest: net_interest_income 88, capex(_resolved) 81, ppe_net(_resolved) 79, total_debt_resolved 79, diluted_shares_growth x3 65, shares_outstanding(_resolved) 64.

## 3. Sample design
Seeded random draw (seed 20261021) of 40 cells across 22 of the top data points, stratified by draft group: corporate 23, reit 7, bank 3, insurer 4, other_financial 4, utility 2 (one other_financial cell, BMNR, is a crypto treasury company that SIC puts in finance). Latest 10-K from `core.filing` per company; INNIO has no 10-K yet (recent listing), so its latest 10-Q was used. Classes: (a) row should not exist for this company (sector/population gating or internal row); (b) applicable concept, line legitimately absent (incl. combined-only presentation); (c) present in filing, not captured (tag/label named); (d) computation defect with inputs present; (e) cannot determine.

## 4. Case table (all FILING-CHECKED unless marked)
| # | cell | co (group) | accession | locator and what the filing shows | class |
|---|---|---|---|---|---|
| 1 | collaborative_arrangement_revenue | TDG (corp) | 0001260221-25-000081 | R5: one revenue line `Revenues` "Net sales" 8,831M; no collaboration revenue on statements | a |
| 2 | collaborative_arrangement_revenue | BPOP (bank) | 0001193125-26-085756 | R5: bank income statement; no collaboration revenue | a |
| 3 | collaborative_arrangement_revenue | HST (reit) | 0001070750-26-000054 | R5: hotel revenues on RCFC; none | a |
| 4 | bdc_total_investment_income | HWM (corp) | 0000004281-26-000012 | R3: RCFC "Sales" 8,252M; not a BDC | a |
| 5 | bdc_total_investment_income | ERIE (ins) | 0001628280-26-010666 | R3: operating revenue on RCFC; investment income is a nonoperating custom line `erie:NetInvestmentIncome...` 85,837K; not a BDC | a |
| 6 | employee_count | DKNG (corp) | 0001883685-26-000013 | dkng-20251231.htm Item 1 Human Capital: "over 5,500 employees"; no dei:EntityNumberOfEmployees in R1 | c (narrative, untagged) |
| 7 | employee_count | VCTR (oth_fin) | 0001193125-26-077057 | vctr-20251231.htm Human Capital: "699 full-time employees"; untagged | c |
| 8 | employee_count | SWX (util) | 0001692115-26-000062 | swx-20251231.htm: "2,453 regular full-time equivalent employees" (Southwest Gas); untagged | c |
| 9 | net_lease_revenue | SNPS (corp) | 0000883241-25-000028 | R5: RCFC only; not a lessor | a |
| 10 | net_lease_revenue | CCI (reit) | 0001051470-26-000016 | R5: "Site rental revenues" 4,049M on custom `cci:Siterentalrevenues` (lease income) | c (custom tag; whether this row should apply to a tower REIT is a template call) |
| 11 | cf_ap_change | ST (corp) | 0001477294-26-000007 | R7: only `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities` "Accounts payable and accrued expenses" 56.7M | b (combined only) |
| 12 | cf_ap_change | TTWO (corp) | 0001628280-26-037434 | R7: custom `ttwo:AccountsPayableAccruedExpensesIncomeTaxesPayableAndOtherLiabilities` (365.3M) | b (combined only) |
| 13 | cf_ap_change | JPM (bank) | 0001628280-26-008131 | R9: `jpm:IncreaseDecreaseInAccountsPayableAndOtherLiabilities` 5,270M; bank template | a |
| 14 | cf_inventory_change | FROG (corp) | 0001193125-26-051382 | R7: software company, no inventory row (R2 no inventory) | b |
| 15 | cf_inventory_change | EGP (reit) | 0000049600-26-000010 | R6: industrial REIT, no inventory | a |
| 16 | cf_ar_change | CMI (corp) | 0000026172-26-000009 | R6: `IncreaseDecreaseInAccountsAndNotesReceivable` "Accounts and notes receivable" (612)M | c (unmapped tag; includes notes: perimeter call) |
| 17 | cf_ar_change | AXS (ins) | 0001214816-26-000097 | R8: premiums/reinsurance net (custom), accrued interest; no trade AR | a |
| 18 | other_income_expense_net | USFD (corp) | 0001665918-26-000008 | R5: `OtherNonoperatingIncomeExpense` "Other (income) expense-net" (4)M | c |
| 19 | other_income_expense_net | AHR (reit) | 0001193125-26-082692 | R4: `InterestAndOtherIncome` "Other income, net" 8,805K | c |
| 20 | total_debt_split | CDE (corp) | 0000215466-26-000004 | R4: `DebtCurrent` 16,996K + custom `cde:LongTermDebtAndLeaseObligationNet` 323,537K; split tags not filed. Row is an internal fallback (concept description: "never consumed") | a (internal row); side finding W1 |
| 21 | total_debt_split | AMP (oth_fin) | 0000820027-26-000011 | R5: `LongTermDebt` only under ConsolidatedEntitiesAxis members (Ameriprise 3,077M; CIEs 2,585M), no undimensioned total | a (internal row); side finding W2 |
| 22 | dividends_per_share | NOW (corp) | 0001373715-26-000007 | no dividend row on any statement (R3-R8) | b |
| 23 | dividends_per_share | PLTR (corp) | 0001321655-26-000011 | none on any statement | b |
| 24 | dividends_paid | ADBE (corp) | 0000796343-26-000003 | none on any statement | b |
| 25 | dividends_paid | SNEX (oth_fin) | 0000913760-25-000196 | none on any statement | b |
| 26 | inventory_days | RBA (corp) | 0001628280-26-011682 | R5 inventory 139.8M; R3 `CostOfRevenue` "Direct expenses" only under ProductOrServiceAxis members (1,431.3 + 1,030.6M), no consolidated fact; stored cost_of_revenue ends 2019 | c (member-only) |
| 27 | total_liabilities | ADSK (corp) | 0000769397-26-000015 | R6: no total liabilities row; total L&E 12,467M | b (derivable) |
| 28 | total_liabilities | DUK (util) | 0001326160-26-000014 | R6: no total liabilities row; total L&E 195,736M | b (derivable) |
| 29 | current_assets | TXT (corp) | 0000217346-26-000006 | R5: `AssetsCurrent` 7,913M only in the "Manufacturing group" section; Finance group unclassified; no consolidated total | b (member-only subtotal) |
| 30 | current_assets | MCY (ins) | 0000064996-26-000005 | R3: unclassified insurer balance sheet | a |
| 31 | amortization_of_intangibles | DHI (corp) | 0000882184-25-000081 | R7: only `DepreciationDepletionAndAmortization` 101.3M | b |
| 32 | sga_expense | ALLY (bank) | 0000040729-26-000005 | R3: noninterest expense lines | a |
| 33 | sga_expense | GAP (corp) | 0001628280-26-018573 | R6: single `OperatingExpenses` "Operating expenses" 5,153M | b (equivalence to SG&A is an accounting call) |
| 34 | interest_expense | OSK (corp) | 0001193125-26-054061 | R2: `InterestAndDebtExpense` "Interest expense" (117.6)M | c |
| 35 | interest_expense | BMNR (oth_fin) | 0001493152-25-024679 | R4: `InterestExpenseNonoperating` (245)K | c |
| 36 | total_debt | MANH (corp) | 0001193125-26-037138 | R4: no debt on balance sheet | b |
| 37 | depreciation_and_amortization | BRO (ins) | 0001193125-26-046984 | R2: `AdjustmentForAmortization` 312M + `Depreciation` 55M as separate lines (R8 same, amortization custom) | c (components, needs composition) |
| 38 | fcf_growth_yoy | FR (reit) | 0000921825-26-000012 | R9: development capex on `PaymentsForLeasingCostsCommissionsAndTenantImprovements` 283.8M; fcf has reason `incomplete:subtract`, not propagated | c (REIT capex perimeter is a template call) |
| 39 | share_buybacks | INIO (corp) | 10-Q 0001193125-26-319072 | R7: no repurchase row | b |
| 40 | capex | FRT (reit) | 0000034903-26-000017 | R8: custom `frt:CapitalExpendituresDevelopmentRedevelopment` 179.1M + `frt:CapitalExpendituresOther` 112.3M | c |
Result: a 13, b 14, c 13, d 0, e 0.

Wrong or stale displayed values found on the way (route to owners):
- W1 CDE `total_debt_resolved` FY2025 = 16,996K (current debt only) vs face debt 16,996K + 323,537K (R4; the custom noncurrent line includes lease obligations, so the right perimeter is a Standardization call); 2026-06-30 shows 2,388K. Wrong value, FILING-CHECKED (value DATA-INFERRED from canonical_fact).
- W2 AMP `total_debt_resolved` latest 2020-09-30, `total_debt` 2011-09-30: current debt exists only as member facts (R5). Stale value if displayed.
- W3 SWX `employee_count_resolved` latest 2022-12-31 while the 10-K states 2,453 FTE at 2025-12-31 (stale).

## 5. Extrapolation to 13,349 (model, not measurement)
Method: each sampled data point represents its own no-reason count plus its `_resolved` twin and downstream metrics (reconciliation gaps -> cf_*_change; dps_growth -> dividends_per_share; payables_days -> inventory_days; current_* family and ratios -> current_assets; fcf_growth_* -> fcf_growth_yoy; net_interest_income, interest_coverage -> interest_expense; cash_returned -> share_buybacks), split by its sampled classes. 1,076 cells (8%) map to no sampled point.
| class | point estimate | interval | basis |
|---|---|---|---|
| a gating / internal row | ~4,400 (33%) | 2,900-5,300 | 2,800 in collab/bdc/net-lease (lineage: no tag filed 1,160 + no lineage row 1,640; 6 of 7 sampled a) + current_* family at financials (154 of 167 per row are bank/reit/insurer/other_fin/bdc) + split row |
| b legitimately absent | ~4,200 (31%) | 3,000-5,300 | dividends family (non-payers; but S3 found 26 of 280 dividends_paid blanks file unmapped common-dividend tags, so ~9% of that family is c), combined AP (291 of 422 cf_ap_change blanks file `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities`, DATA-INFERRED), no inventory, no debt, totals not presented |
| c present, not captured | ~3,700 (28%) | 2,700-5,000 | employee_count 925 (narrative only; the displayed `employee_count_resolved` is valued for 978/986, so this row is mostly redundant), `OtherNonoperatingIncomeExpense` filed by 220 of 314 other_income blanks, `IncreaseDecreaseInReceivables` by 140 of 365 cf_ar blanks (perimeter check needed), interest tags, member-only facts, REIT capex |
| d computation defect | 0 seen | 0-7.5% (0/40, rule of three) | the 37 "all inputs valued" metric cells are the only d candidates; RBA, one of them, was a stale input, not arithmetic |
| e cannot determine | 0 seen | n/a | all 40 decided at statement level |
| not sampled | 1,076 (8%) | | ppe_net, shares/diluted-share growth, operating_income, ownership, tax rate rows |
Sampled-share Wilson 95% intervals on n=40: a 33% (20-48), b 35% (22-50), c 33% (20-48). The intervals above are wider than the sample alone would give where population lineage counts disagree with family weighting.

Reason-propagation defect (separate from the class of the blank): 594 metric cells (and the 95 x3 fcf_growth cells) are blank for an already-recorded reason that the metric engine never writes because it emits no row. Fixing that is pure plumbing.

## 6. Fully explained data points (filing-checked sample + population signal agree)
- collaborative_arrangement_revenue (982), bdc_total_investment_income (957): a. Gate by group; keep collaborative revenue as a statement line only where presented.
- net_lease_revenue (861): a except true lessors with custom lease-revenue tags (CCI type, c); a group gate plus a lessor rule.
- current_assets/liabilities, current_ratio, working_capital, quick_ratio (167/160 each): a at 154 financials, b at 13 corporates (unclassified or member-only, TXT). Needs the S3 "unclassified balance sheet" reason.
- employee_count (925): c; the row duplicates employee_count_resolved; retire the base row from coverage or label it "XBRL cover tag not filed".
- dividends family (~1,750 cells): b, minus the S3 unmapped-tag subset.
- total_debt_split (306): internal row; remove from coverage.
Not fully explained: cf_ar_change, other_income_expense_net, interest_expense, D&A, capex, inventory/payables days (mixed b/c; need the tag decisions below).

## 7. Recommendation
1. Write reasons where none exist (no data change, no accountant): group gates for rows 1, 2, 4 and the current_* family at financials; "combined line only" from the cash-flow face for cf_ap_change; propagate input reasons into metrics (594+285 cells) by emitting a null metric row with the input's reason.
2. Remove internal rows (total_debt_split, base employee_count) from the coverage denominator only after the founder accepts the redefinition; never silently.
3. Vocabulary leads for the Tag Mapper (coexistence check first): `OtherNonoperatingIncomeExpense`, `InterestAndDebtExpense`, `InterestExpenseNonoperating`, `IncreaseDecreaseInAccountsAndNotesReceivable`/`IncreaseDecreaseInReceivables`, member-only CostOfRevenue/LongTermDebt summing, composition D&A.
4. Fix W1-W3.
Risks: one sampled cell per data point x group; family weighting assumes cascades share the base class; group labels are a draft. What would change the estimate: a second 40-cell draw from rows 11-40 and the unsampled 8%.

Untested scope: notes and MD&A beyond the face statements (a collaboration or lessor note could exist without a face line); the 37 all-inputs-valued metric cells; rows 41-109 except via family mapping.
