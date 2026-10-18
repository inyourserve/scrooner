# Sector templates for "every row filled" (2026-10-19)

Role: Sector Analyst (12). Founder direction 2026-10-18: every displayed metric row is a correct value, OR is replaced by the metric that applies to that kind of company (a template), OR (rare) shows a stated reason. No empty rows.

**STATUS: ALL TEMPLATE, FORMULA AND FAMILY CHOICES BELOW ARE PROPOSAL-ONLY until an accounting reviewer approves them.** Nothing was mapped, coded, seeded or written to the DB. No filing was opened for this file, so every conclusion is **DATA-INFERRED** (our tables) or **ASSUMED** unless it cites file 26/27 (FILING-CHECKED there). Only a rendered-statement check can classify a blank as structural (21 section 6).

## 0. How this was measured (commands actually run)
- Read: data-team 20, 21, 22, 12, 26, 27; `doc/data-moat/decisions.md`; `mapper/coverage_matrix.py` (POPULATION_QUERIES, `_FAMILY_POPULATION` lives in `mapper/coverage_snapshot.py`); root and pipeline CLAUDE.md.
- DB (read-only session, one connection at a time, `statement_timeout=20s`, `default_transaction_read_only=on`; pg_stat_activity showed 16 sessions / 4 active at start, so only light indexed reads were run). Tables read: `core.company` (sic_code is TEXT), `analytics.company_population`, `analytics.coverage_snapshot` (latest `snapshot_date` = 2026-10-17, fresh), `analytics.company_data_point_coverage`, `analytics.metric_definition(_input)`, `analytics.canonical_concept`, `analytics.concept_mapping`, `analytics.sec_tag_library`, `analytics.company_sec_tag` (2.0M rows, indexed).
- Scripts (scratch, outside repo): `/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/sa/{q.py,tagfam.py,pivot.py,fam.sql,fam_all.sql}`.
- Population used: `real_operating_company` (4,808 per `company_population`; the coverage table sums to 4,813 across my SIC bins, a 5-company unreconciled difference; use counts as approximate). Family = SIC bin only. SIC is a hypothesis: the role spec forbids classifying by sector label alone, so every family below needs a filing-evidence confirmation rule (section 2).
- Metric registry: 82 active `metric_definition` rows (matches the founder's "82"); 78 `canonical_concept` rows. Populations: default `real_operating_company`; dividend, buyback, capital-return, BDC and three `has_*` reconciliation populations are the only narrower ones (`coverage_matrix.py` lines 346-505). **There is no sector population in code today, so a bank is measured against industrial rows.**
- Not run: any fact-level query, any rendered-statement check, any full-population coexistence check.

## 1. Company families (real operating companies; approximate)
| Code | Family | SIC rule | Active (all) | Real operating | Non-gated blank rows today (of 82 metrics, DATA-INFERRED) |
|---|---|---|---|---|---|
| A1 | Banks and thrifts | 6020-6036 | 326 | 326 | 9,046 |
| A2 | Non-bank lenders, credit, other finance (includes BDCs, fintech, mortgage bankers, 6199 "Finance services") | 6099-6199 | 160 | 148 | 3,749 |
| B | Brokers, dealers, asset managers, advisers | 6200-6299 | 180 (6221 is 104, mostly commodity trusts already excluded) | 107 | 3,015 |
| C | Insurers and insurance agents | 6311-6411 | 127 | 127 | 2,998 |
| D1 | REITs (equity and mortgage mixed) | 6798 | 196 | 196 | 5,023 |
| D2 | Other real estate operators and developers | 6500-6599 | 71 | 69 | 1,734 |
| S | Blank checks / SPACs / royalty trusts / other investors | 6600-6799 except 6798 | 326 (6770 alone is 295) | 37 (SPACs already removed from the operating population by the existing classifier) | 1,299 |
| E | Utilities and waste | 4900-4991 | 127 | 124 | 2,188 |
| F | Energy (E&P, services, refining, oil pipelines) | 1311-1389, 2911, 2990, 4610 | 150 | 145 | 2,954 |
| G | Transport (rail, truck, air, water, services) | 4000-4799 except 4610 | 85 | 84 | 1,339 |
| H | Pharma, biotech, labs | 2830-2836, 8071, 8731 | 711 | 710 (about 131 have no revenue value, 579 do) | 16,168 |
| J | Everything else: tech, retail, industrial, services | remaining SICs | about 2,732 | 2,686 | 40,088 |
| Z | No SIC on file | null | 54 | 54 | 2,531 |

"Non-gated blank rows" excludes the dividend, buyback, capital-return and reconciliation-gap metrics (13 of the 82), whose denominators are already narrowed to payer/holder populations; those rows still need a displayed reason for non-payers (section 3, rule R5). Source: `fam_all.out` pivot of `company_data_point_coverage.has_value`; evidence class DATA-INFERRED.

Hazards in these counts: (a) SIC 6199 and 6211 mix very different businesses, so A2 and B must be split by filing evidence; (b) 6798 mixes equity and mortgage REITs (role spec: keep separate); (c) pharma by SIC includes profitable companies, so "pre-revenue" must be decided by filing evidence, not SIC; (d) 54 companies have no SIC.

## 2. Templates per family (PROPOSAL-ONLY)
Counts after a tag name = companies in that family with at least one undimensioned fact under that tag in `company_sec_tag` (second number = last period end on or after 2025-01-01). DATA-INFERRED: presence of a tag is not proof of a face line or of the right perimeter. "Exists" below means a `canonical_concept` of that meaning exists today (checked by name against the 78 concepts); "missing" means no concept.

Concepts that exist and are reusable: total_assets, stockholders_equity, net_income, income_before_tax, income_tax_expense, interest_expense (InterestExpense, InterestExpenseDebt), interest_income (**only `InvestmentIncomeInterest`, 15 of 326 banks**, so it is not loan interest), other_income_expense_net (NonoperatingIncomeExpense first, then `InterestIncomeExpenseNet`, then `InterestIncomeExpenseNonoperatingNet`), revenue (includes provisional `InterestAndDividendIncomeOperating`), sga_expense, cfo, capex, depreciation_and_amortization, dividends_paid, shares_outstanding, goodwill, total_debt_resolved, ppe_net, net_lease_revenue (`OperatingLeaseLeaseIncome`), research_and_development, employee_count, bdc_total_investment_income.

### 2.1 A1 Banks and thrifts (326)
Classification rule (needs filing check): SIC 6020-6036 AND the income statement shows interest income, interest expense and a provision caption AND the balance sheet is unclassified with deposits. Do not call a company a bank merely because interest income is present (role spec). Keep trust/non-depository banks (6099) out until checked.

Do NOT apply (replace or reason): gross_margin, current_ratio, quick_ratio, working_capital, inventory_days, debtor_days, payables_days, cash_conversion_cycle, piotroski_f_score (Piotroski's own method needs a classified balance sheet and gross margin; the registry text already says null by design), rnd_intensity, sga_pct_revenue, margin_expanding_3yr (uses gross margin), ebitda, ebitda_margin, ev_ebitda, debt_to_ebitda, net_debt_ebitda, interest_coverage_ratio, operating_margin (11/326 have it; interest is an operating cost), roic (2/326), fcf family and fcf_yield (209/326 currently have a value: DATA-INFERRED hazard, see section 6), net_cash, net_cash_per_share, debt_to_equity and zero_debt (borrowings exclude deposits; 210/326 show a value today, perimeter unreviewed), ev_sales, goodwill_pct_assets (keep as optional).
Keep (apply): roe, roa, net_margin, pretax_margin (need a bank revenue definition), book_value_per_share, price_to_book, trailing_pe, market_cap, eps and net income growth, dividend family, buyback family, institutional_ownership_pct, share dilution, sbc_pct_revenue, profitable_streak_years, eps_dilution_spread.

Replacement rows (formula in canonical terms; tag evidence):
| Row | Formula | Input status |
|---|---|---|
| Net interest income | `InterestIncomeExpenseNet` (321/326, 318 recent) | Tag is mapped only as priority 2 of other_income_expense_net, so a bank's NII is not stored under a bank concept. **Missing concept** `net_interest_income_bank`. Existing metric `net_interest_income` = interest_income - interest_expense uses InvestmentIncomeInterest and total interest expense; for banks that is securities interest less ALL interest expense, which is wrong. Rename/split (section 6) |
| Interest income, loans and securities | `InterestAndDividendIncomeOperating` (309/326), `InterestAndFeeIncomeLoansAndLeases` (292/270 recent) | Missing concept |
| Interest expense, deposits | `InterestExpenseDeposits` (280/272) | Missing; `interest_expense` concept cannot hold it (InterestExpense only 34 recent) |
| Noninterest income / expense | `NoninterestIncome` (322/320), `NoninterestExpense` (322/320) | Missing (both are `candidate` in the tag library) |
| Provision for credit losses | `ProvisionForLoanLossesExpensed` (266/177), `ProvisionForLoanLeaseAndOtherLosses` (268/197), `ProvisionForLoanAndLeaseLosses` (275/6) | Missing; **tag switches over time (CECL)**, needs a period-scoped tag set, not one tag |
| Deposits | `Deposits` (323/316); components `NoninterestBearingDepositLiabilities` (252/236), `InterestBearingDepositLiabilities` (232/212) | Missing |
| Loans, net | pre-CECL `LoansAndLeasesReceivableNetReportedAmount` (282/7); post `FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss` (229/225) | Missing; same period-scoped switch (the AAPL revenue lesson, ledger 2026-08) |
| Allowance for credit losses | pre `LoansAndLeasesReceivableAllowance` (284/3); post `FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest` (238/233) | Missing |
| Gross loans | `FinancingReceivableExcludingAccruedInterestBeforeAllowanceForCreditLoss` (218/215); pre `LoansAndLeasesReceivableGrossCarryingAmount` | Missing |
| Nonaccrual loans | `FinancingReceivableRecordedInvestmentNonaccrualStatus` (289/181), `FinancingReceivableExcludingAccruedInterestNonaccrual` (158/148) | Missing |
| Net interest margin proxy | Net interest income / average total assets (average of period-end assets, labelled "NII / average assets", NOT "NIM") | NII missing; total_assets exists. True NIM needs average earning assets, which has no standard tag; keep NIM unavailable with a reason, or take it from FDIC for the launch slice (decisions.md 2026-10-18; separate labelled rows, never mixed) |
| Efficiency ratio | NoninterestExpense / (Net interest income + NoninterestIncome), reported basis, labelled "reported basis, not company-adjusted" | Both inputs missing concepts; tags present at 322 banks |
| Loans to deposits | Net loans / Deposits | Both missing; tags present |
| Allowance coverage | Allowance / Gross loans | Both missing |
| Nonaccrual loans / gross loans | Nonaccrual / Gross loans | Missing |
| Net charge-off rate | (`FinancingReceivableAllowanceForCreditLossesWriteOffs` 269/130 minus `...Recovery` 417 library-wide) / average gross loans | Missing; pre/post-CECL tags differ |
| Tier 1 risk-based capital ratio | `TierOneRiskBasedCapitalToRiskWeightedAssets` (209/144), leverage `TierOneLeverageCapitalToAverageAssets` (210/152), CET1 ratio `CommonEquityTierOneCapitalRatio` (126/102) | Missing. **Uncertain**: regulatory tables are often dimensioned by entity (holding company vs bank subsidiary) and by Actual/Minimum; companyfacts strips dimensions, so the undimensioned fact may be either entity. Needs a filing check per bank before display |
| Equity / assets, cost of deposits | stockholders_equity / total_assets; InterestExpenseDeposits / average deposits | Exist/missing as above |
| Tangible book value per share | (Equity - goodwill - other intangibles - preferred) / shares | Other intangibles and preferred missing; goodwill exists |
| Bank revenue (for net_margin, pretax_margin, growth) | Proposed "total revenue = net interest income + noninterest income" | Today revenue for banks = whichever of `Revenues` (68), RCFC (85), provisional `InterestAndDividendIncomeOperating` (309) matched, so revenue can be total interest income or a different perimeter bank to bank. **Open perimeter question for the reviewer** |

Evidence needed before any bank row is published: Verifier opens the income statement and balance sheet of a stratified bank sample (national, state, thrift, large, small, a CECL-deferral bank) and checks each input.

### 2.2 A2 Non-bank lenders and other finance (148) and B Brokers and asset managers (107)
Split by filing evidence, not SIC. Sub-shapes: consumer/commercial lenders and mortgage bankers (6141, 6153, 6159, 6162: bank-like income statement, borrowings are the funding, so debt IS operating); broker-dealers (6211, 6200, about 31: bank-like partial); asset managers/advisers (6282, 45: ordinary fee-based income statement, many tag OperatingIncomeLoss); BDCs (118 in `bdc_company`, already have `bdc_total_investment_income`); fintech/crypto/exchanges (6199: mixed, often ordinary). Template: lenders use the A1 income-statement rows (NII, provision, efficiency) plus debt-to-equity KEPT (borrowings are funding), interest coverage replaced by "net interest spread" only where interest income and expense are both found; asset managers use the J template minus gross margin (reason or total-expense ratio = (revenue - operating income)/revenue); BDCs: net investment income, NAV per share, dividend coverage by NII (concepts missing except total investment income). Counts of sub-shapes beyond SIC not measured.

### 2.3 C Insurers (127)
Split property/casualty (6331, 6351, 6361: 57+8+4), life (6311: 17), health plans (6321, 6324: 14), agents/brokers (6411: 26: ordinary fee income statement, interest is NOT operating, keep standard rows). Do not apply a P&C combined ratio to life or to brokers (role spec).
Do NOT apply: gross_margin, inventory_days, payables_days, cash_conversion_cycle, debtor_days (premiums receivable is not trade AR), current_ratio, quick_ratio, working_capital (no classified balance sheet), piotroski, rnd_intensity, margin_expanding_3yr, ebitda family and interest_coverage (interest/operating income not defined the industrial way; OperatingIncomeLoss exists for only 55/127), roic, sga_pct_revenue, fcf family (cash from operations is dominated by float movements). Keep: roe, roa, book_value_per_share, price_to_book, trailing_pe, net_margin, pretax_margin, eps/net income growth, dividend and buyback families.
Replacement rows:
| Row | Formula | Input status |
|---|---|---|
| Premiums earned | `PremiumsEarnedNet` (102/98) | Missing concept |
| Premiums written | `PremiumsWrittenNet` (70/61), `DirectPremiumsWritten` (74) | Missing |
| Losses and loss expenses incurred | `PolicyholderBenefitsAndClaimsIncurredNet` (93/86); P&C alt `IncurredClaimsPropertyCasualtyAndLiability` (23/0) | Missing |
| Loss ratio (P&C and health only) | Claims incurred / Premiums earned, reported basis | Both missing |
| Expense ratio inputs | DAC amortization `DeferredPolicyAcquisitionCostAmortizationExpense` (92/74), `OtherUnderwritingExpense` (25/19), `GeneralInsuranceExpense` (7/4) | Missing and sparse. **Combined ratio is NOT computable broadly**: underwriting-expense captions vary and the company-reported ratio is non-GAAP in MD&A. Offer "loss ratio" for the P&C/health subset where both inputs exist; combined ratio only after a per-company filing check, otherwise reason "reported in MD&A, not in XBRL face statements" |
| Net investment income | `NetInvestmentIncome` (92/90), `InvestmentIncomeNet` (42/22) | Missing; two tags |
| Total revenue | `Revenues` (121/116) | Exists (revenue) |
| Reserves / equity | `LiabilityForClaimsAndClaimsAdjustmentExpense` (99/88) / equity | Reserve concept missing |
| Debt / (debt + equity) | total_debt_resolved / (total_debt_resolved + equity) | Exists, but EG-type senior notes and FHLB advances are unmapped (file 27); FHLB advance perimeter is a reviewer decision |
| Book value per share, ROE | exist | Exist |
Underwriting income `UnderwritingIncomeLoss` is tagged by only 16/127; do not rely on it.

### 2.4 D1 REITs (196) and D2 real estate operators (69)
Split equity vs mortgage REITs by filing evidence (mortgage REIT: interest income is revenue, funding via repos; model separately, role spec). 
Do NOT apply to either: inventory_days, payables_days, cash_conversion_cycle, debtor_days, rnd_intensity, piotroski, margin_expanding_3yr (gross margin), current_ratio, quick_ratio, working_capital (REIT balance sheets are unclassified: current ratio has 16/196, so blank is probably correct but needs the rendered check), gross_margin (cost of revenue exists for 21-67 REITs only), fcf family and fcf_yield (maintenance capex is not separable; acquisitions are investing), sga_pct_revenue (G&A tag present at 172, usable as "G&A % revenue" instead). Keep: ebitda/net_debt_ebitda/debt_to_ebitda (D&A mapped for 123; OI for 142), interest coverage, roe/roa/book value, dividend family.
Replacement rows (equity REIT):
| Row | Formula | Input status |
|---|---|---|
| Rental revenue | `OperatingLeaseLeaseIncome` (113/103) | Exists (net_lease_revenue) |
| Property operating expense | `DirectCostsOfLeasedAndRentedPropertyOrEquipment` (67/30), `RealEstateTaxExpense` (56/45), `CostOfPropertyRepairsAndMaintenance` (22) | Missing and sparse |
| NOI proxy | Rental revenue - property operating expenses | **Not generally computable** (inputs at 67 of 196). Reason "property operating expenses not separately tagged" only after a rendered check |
| Real estate investment, net / at cost / accumulated depreciation | `RealEstateInvestmentPropertyNet` (148/135), `...AtCost` (127/114), `...AccumulatedDepreciation` (134/121) | Missing |
| Debt / gross real estate | total_debt_resolved / RealEstateInvestmentPropertyAtCost | Debt exists; real estate at cost missing |
| Secured debt share | `SecuredDebt` (124/82) / (`SecuredDebt` + `UnsecuredDebt` 74) | Missing |
| Dividend coverage by operating cash flow | cfo / dividends_paid | Both exist (a new metric; `dividends_pct_fcf` should not be used for REITs) |
| EBITDAre (Nareit) | NI + interest + taxes + D&A + loss/-gain on property sales + impairments | Inputs partly missing (property-sale gains tag not found in 196 REITs under the name tried; `ImpairmentOfRealEstate` 128/81). Propose only with a reviewer; current `ebitda` = OI + D&A stays |
| FFO / AFFO | **Not computed.** Reason: "non-GAAP; reconciled in MD&A, not in XBRL face statements" (21 section 5). Do not build as net income plus all depreciation (role spec) | |
| Occupancy, same-store NOI, AUM-style KPIs | Not standard us-gaap tags; unavailable with that reason | |
Mortgage REITs: interest income (`InterestIncomeOperating` 50/29, `InterestAndDividendIncomeOperating` 24/14), interest expense (`InterestExpense`, `InterestExpenseOperating` 39/37), net interest spread, book value per share, economic leverage = (debt)/equity, dividend coverage by CFO. Funding and fair-value tags not surveyed.

### 2.5 E Utilities (124), F Energy (145), G Transport (84)
These are ordinary corporate templates with operating income in most cases (E 116, F 125, G 80 of their companies tag `OperatingIncomeLoss`). Differences are row applicability, not a new template family:
- Utilities: gross margin and inventory/R&D rows are often not applicable (cost of goods tagged by 52/124); balance sheets are usually classified (AssetsCurrent 120). Add: net plant (`PublicUtilitiesPropertyPlantAndEquipmentNet` 42/35; `ppe_net` exists), regulatory assets/liabilities (47/45, missing), capex % revenue (exists), dividend payout (exists). Rate-base is NOT in XBRL face statements (reason, not a row).
- Energy: reserves are supplementary, dimensioned, outside companyfacts. Add: exploration expense (42/30), impairment of oil and gas properties (69/34), DD&A (111/100, exists), capitalized costs of producing activities (53/38), CFO/revenue. Pipelines (7 oil, 15+6+13 gas) use the standard template; distributions per unit are custom tags (unverified).
- Transport/airlines: no cost-of-revenue line is typical (CostOfRevenue 23/84, GrossProfit 23/84), so gross_margin and inventory_days need the rendered check then reason; add fuel % revenue (`FuelCosts` 31/24), labor % revenue (`LaborAndRelatedExpense` 45/43). Capacity KPIs (ASMs, RASM) are custom, unavailable.
Both-sided check: do not declare these families "no template" because the input counts are partial; the dominant blanks here are input-fix blanks (OI fallback, debt tags), see section 4.

### 2.6 H Pharma, biotech (710) and the pre-revenue overlay
Pre-revenue is an overlay on the corporate template, never an SIC class (role spec). Candidate rule (needs filing check): no revenue line value in the latest 10-K and R&D expense present. About 131 of 710 pharma-SIC companies have no `revenue_sanity_resolved` value today (DATA-INFERRED; some are our gaps, not pre-revenue; collaboration revenue is mapped as a separate concept).
Do NOT apply to pre-revenue: gross_margin, margin_expanding_3yr, operating_margin, net_margin, pretax_margin, ebitda_margin, debtor_days, inventory_days, payables_days, cash_conversion_cycle, sga_pct_revenue, rnd_intensity (R&D / revenue undefined), price_to_sales, ev_sales, revenue growth family, fcf_margin, peg_ratio (negative EPS), dividend family.
Replacement rows (all from existing concepts unless noted):
| Row | Formula | Input status |
|---|---|---|
| R&D expense, annual and % of operating expenses | research_and_development; research_and_development / operating_expenses_resolved | Exist (R&D tagged by 655/710; `ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost` 103 is an unmapped variant to check) |
| Operating cash burn | -cfo (TTM) when cfo < 0 | Exists |
| Cash and short-term investments | cash_and_equivalents + marketable securities | Cash exists; `ShortTermInvestments` 225, `MarketableSecuritiesCurrent` 203, `AvailableForSaleSecuritiesDebtSecuritiesCurrent` 178 are unmapped, so liquidity is understated if only cash is used |
| Cash runway (months) | (Cash + short-term investments) / (monthly operating cash burn), shown only if burn > 0, with formula, period and assumptions disclosed (role spec: cash divided by a non-negative OCF magnitude is not universally meaningful) | Needs the investments concept |
| Dilution | share_dilution_trend, diluted_shares_growth_yoy | Exist |
| Accumulated deficit | `RetainedEarningsAccumulatedDeficit` (709/706) | Missing concept (also in Standardization Lead's 24 lines) |
| Net proceeds from equity issuance | `ProceedsFromIssuanceOfCommonStock` (634/396) | Missing |
Do not classify all biotech as pre-revenue: 579 of 710 have revenue and use the J template, but gross margin is present for only 326.

### 2.7 S SPACs, shells, trusts (37 real operating, about 300 excluded already)
SPACs (6770), royalty/commodity trusts are already removed from `real_operating_company` by the `revenue_sanity_resolved` gap_reason classifier (`pre_revenue_spac`, `passthrough_trust`, `passthrough_commodity_trust`). Display rule proposed: the company page shows no ratio rows, only a stated reason ("blank-check company: no operations" / "pass-through trust") plus trust assets, cash held in trust, and shares. That reason is a template statement and needs the filing-evidence check already used by the classifier (not verified here). Remaining non-SPAC shells with no operations fall under the pre-revenue overlay plus a "going concern / shell" reason.

### 2.8 J Standard industrial, tech, retail, services (2,686) and Z (no SIC, 54)
The standard template (all 82 rows) applies. Blank rows in J are NOT a template problem except where the line is not presented. They fall into: (i) lines a company does not present (R&D, inventory, goodwill, cost of revenue: 1,339 companies with revenue but no cost of revenue or gross profit, doc 20); (ii) input gaps (operating income, debt, cash, share count: files 26/27); (iii) history gaps (10-year CAGRs). The same row can be "calculate", "reason" or "swap" depending on evidence: section 3.
Z (54, no SIC): classify by filing (statement shape) first; 47 of 54 lack revenue growth etc. Likely new/young filers: route to Company Master (SIC missing is an identity gap, not a metric gap).

## 3. The 12 lowest-coverage metrics: decision per family
Snapshot 2026-10-17 coverage (of 4,808): piotroski_f_score 29.49%, cash_conversion_cycle 35.30%, net_interest_income 35.34%, peg_ratio 38.04%, rnd_intensity 41.18%, margin_expanding_3yr 42.45%, inventory_days 44.82%, revenue_growth_10y_cagr 47.32%, payables_days 51.00%, fcf_yield 53.22%, roic 54.47%, eps_growth_10y_cagr 56.99% (`coverage_snapshot`). Blank counts below are today's `has_value=false` per family (A1 banks 326, A2 148, B 107, C 127, D1 196, D2 69, E 124, F 140, G 84, H 710, J 2,686, S 37, Z 54), same query as section 1.

Decision codes: **CALC** = should be calculated (input fix named); **SWAP** = replaced by template row(s) from section 2; **REASON** = show a stated reason.

### 3.0 Evidence classes for a stated reason ("not applicable") 
| Class | What it proves | May justify |
|---|---|---|
| E1 Rendered statement | The rendered income statement or balance sheet of the cited filing (R-file, accession and row) shows no such line, or shows only a combined line | "Line not presented", "combined with other lines" (uses `company_filing_line_evidence`: `line_not_presented_in_filing`, `line_presented_combined_with_others`; it is EVIDENCE, 14-34% of held values show no face line, so wording is "not shown on the statements") |
| E2 Math condition | A stored, verified input makes the formula undefined (negative or zero denominator, negative base for a CAGR) | "Earnings negative, PEG undefined"; valid only once the inputs themselves are verified |
| E3 History | The company's earliest periodic filing (submissions index) is later than the start of the required window | "Fewer than 10 years of filings" |
| E4 Filing-stated | The filing's own text states the fact (e.g. "no borrowings outstanding") with locator | Zero-debt E2/E3 states in file 27 decision 3 |
| Never sufficient | A missing XBRL tag, an unmatched tag dictionary, `no_line_item_filed` (18% of a rendered sample showed the line), SIC alone, or any vendor figure (yfinance "Total Debt" includes leases) | Nothing; the cell stays an open gap |
So "not applicable" for a bank's gross margin needs E1 on that bank's statement (SIC 602x plus a statement showing interest income/expense and no gross profit); SIC alone makes it a hypothesis.

### 3.1 Decisions
| Metric | A1 Banks | A2 / B | C Insurers | D1/D2 RE | E/F/G | H Pharma | J Standard |
|---|---|---|---|---|---|---|---|
| piotroski_f_score (blank: 326 / 127+97 / 116 / 189+64 / 82+108+74 / 592 / 1,537) | SWAP: row set 2.1 (ROA, ROE, equity/assets, efficiency). REASON on the Piotroski row: "needs classified balance sheet and gross margin", E1 | Lenders/brokers as banks; asset managers CALC if inputs exist, else REASON E1 | SWAP (ROE, ROA, book value growth) | REASON E1 (unclassified BS, no gross profit) for most | CALC where gross profit and current assets exist; REASON E1 otherwise (airlines with no cost line) | CALC for revenue-generating; REASON (E2/E1) pre-revenue | CALC: the score needs 9 inputs over 2 years, so blanks are mostly gross-margin / current-asset lines not presented (E1) or short history (E3). Do not invent a "reduced" Piotroski; a variant would be a new, differently named metric |
| cash_conversion_cycle (326 / 113+104 / 125 / 193+64 / 91+103+75 / 497 / 1,346) | SWAP: loans-to-deposits | SWAP for lenders/brokers; CALC asset managers | SWAP: combined/expense ratio inputs | SWAP: debt / gross real estate, dividend coverage | CALC; REASON E1 where no inventory/receivable/payable lines | REASON E1 (no inventory) or SWAP to cash runway if pre-revenue | CALC when inventory, AR, AP and cost of revenue all exist; if the rendered BS shows no inventory, the reviewer must decide whether CCC = DSO - DPO is acceptable (a different definition, needs its own name) else REASON E1 |
| net_interest_income (311 / 109+76 / 112 / 118+46 / 77+93+38 / 414 / 1,668) | **CALC with a new bank concept**: `InterestIncomeExpenseNet` (321 banks). Today's formula (InvestmentIncomeInterest - InterestExpense) is wrong for banks: suppress the 15 bank values until fixed | Lenders CALC (same tag); brokers: `InterestAndDividendIncomeOperating` less interest expense, reviewer | Insurers: REASON (net investment income row replaces it) | REIT: mortgage REITs CALC; equity REITs REASON (E1) | REASON E1: not an operating concept for these; the current corporate "interest income minus interest expense" is non-operating and should be renamed so it is not confused | REASON | CALC if kept as "net interest (non-operating)"; rename |
| peg_ratio (112 / 109+54 / 52 / 122+46 / 65+92+50 / 509 / 1,704) | CALC where EPS growth positive (214/326 already have it) | CALC | CALC | CALC | CALC | REASON E2 (negative EPS or negative growth) | CALC; REASON E2 when P/E or growth is negative or zero (PEG is mathematically undefined/meaningless) or E3 when the growth base is missing. This is the one blank class where the reason comes from our own verified values, not a filing check |
| rnd_intensity (325 / 103+101 / 122 / 195+64 / 103+124+74 / 273 / 1,275) | REASON E1 (no R&D caption) | REASON E1 | REASON E1 | REASON E1 | REASON E1 mostly | CALC (655/710 tag R&D; remaining 55: check variant tag and pre-revenue) | CALC where R&D is presented (1,411 of 2,686 have it); REASON E1 otherwise; a zero is NEVER used. If R&D is combined in "SG&A and R&D" the reason is `line_presented_combined_with_others` |
| margin_expanding_3yr (324 / 106+98 / 117 / 179+52 / 101+123+68 / 564 / 968) | SWAP: efficiency ratio improving 3 years (needs the bank concepts) | SWAP | SWAP: loss-ratio / ROE trend | SWAP: operating margin or NOI margin trend | SWAP: "operating margin expanding" where no gross profit | REASON (pre-revenue) / CALC | CALC when gross profit exists for 3 consecutive FYs; where only cost-less statements exist SWAP to "operating margin expanding 3yr" (new, differently named metric); REASON E3 for short history |
| inventory_days (326 / 106+102 / 122 / 187+59 / 85+91+67 / 460 / 979) | REASON E1 (no inventory on an unclassified bank BS) | REASON E1 | REASON E1 | REASON E1 | CALC for energy/utility with inventory; REASON E1 otherwise | CALC where inventory shown, else REASON E1 | CALC where inventory and cost of revenue exist; REASON E1 where the rendered BS has no inventory line (population `has_inventory_company` has 2,552 of 4,808; DATA-INFERRED only, because "no fact" is not "no line") |
| revenue_growth_10y_cagr (88 / 105+46 / 35 / 89+40 / 50+66+33 / 550 / 1,367) | CALC (requires the bank revenue definition, section 2.1) | CALC | CALC | CALC | CALC | CALC / E3 | CALC when 11 fiscal years of revenue exist on one definition; REASON E3 "fewer than 10 years of filings" or E2 negative base; restated/recast perimeters (discontinued ops) must use one basis. History gate: no value before 2015-01-01 may be presented as current (doc 38), so a 10-year window ending FY2025 starts FY2015 and is borderline. A real conflict with "no empty rows": the gate may force REASON "history window" for many; the founder/reviewer must decide the allowed window |
| payables_days (326 / 93+101 / 118 / 188+56 / 70+85+53 / 430 / 780) | REASON E1 | REASON E1 | REASON E1 | REASON E1 | CALC where AP and cost of revenue exist; REASON E1 where cost of revenue is not presented. Combined "payable and accrued" lines are never mapped as plain AP (21 section 3) | CALC/REASON E1 | CALC; for companies with AP but no cost of revenue a variant on total costs is a new metric, not this one |
| fcf_yield (117 / 99+60 / 67 / 180+51 / 48+93+34 / 368 / 1,055) | REASON E1 / SWAP: dividend and earnings yield; the 209 existing bank values are not a defined concept (cash from operations includes deposit and loan flows): hazard, reviewer decides whether to suppress | Same | Same (float movements) | SWAP: CFO yield or AFFO unavailable; reviewer | CALC | CALC if CFO > 0 and market cap known; REASON E2 if FCF negative (still shown as negative value, not blank) | CALC. The blanks are input blanks: market_cap blanks (464 in J, 89 in H), capex blanks (407 J), cfo. Fix inputs first (share count and price, capex tag); a negative FCF yield is a value, not a blank |
| roic (324 / 89+73 / 87 / 125+34 / 33+54+21 / 428 / 863) | SWAP: ROE, ROA, ROTCE (tangible needs missing concepts). REASON E1: invested capital includes deposit funding in no standard way | A2 lenders: SWAP ROE; asset managers CALC | SWAP: ROE | CALC for D2 / equity REIT where OI and debt exist; mortgage REITs SWAP | CALC; main blank cause `incomplete:total_debt_resolved` and missing OI (file 26/27) | CALC; pre-revenue REASON E2 (OI negative: ROIC shown as negative value if inputs exist) | CALC after the input fixes: roic blanks list `total_debt_resolved` in about 1,800 of 2,200 incomplete reasons (DATA-INFERRED from gap_reason sample, counted from the first listing). Needs the zero-borrowings rule (file 27 D3) and debt tags (D5, F1/F2) and the OI fallback (D1/D2) |
| eps_growth_10y_cagr (97 / 91+44 / 41 / 47+38 / 43+60+27 / 405 / 1,121) | CALC (banks 229/326 already) | CALC | CALC | CALC | CALC | CALC / REASON E2 (negative base) | CALC; REASON E2 (EPS base zero or negative: CAGR undefined) or E3 (history); never subtract EPS across restated/split bases (ledger 2026-10-18: re-base split series) |

Rows that already exist but lack an explicit reason today: `is_null_reason` exists in `metric_value`; the template/reason layer must fill every cell (section 5).

## 4. Prioritized build list (rows resolved per company's worth of work)
Estimation method (all numbers are **estimates**, label DATA-INFERRED for the counting, ASSUMED where marked): rows resolved = sum over the metrics a template marks "not applicable / swap" of today's `has_value=false` count in that family (section 1 pivot). That is an UPPER bound on blanks removed: a SWAP puts a template row in the same slot, but only if the replacement input exists and is verified, and a REASON row is only allowed with E1 evidence. "Work" = new concepts plus companies needing a filing check.

| Rank | Template | Companies | Blank rows addressed (estimate) | Rows per company | Work (proposal) |
|---|---|---|---|---|---|
| 1 | **Bank / thrift (A1)** | 326 | about 6,440 non-gated rows (sum of 20 inapplicable-metric blanks: current ratio 326, working capital 325, quick ratio 326, gross margin 320, inventory/payables/CCC 326 each, debtor days 307, piotroski 326, rnd 325, sga 310, ebitda family 322+324+324+325+326, interest coverage 315, operating margin 315, roic 324, margin trend 324) plus 311 net-interest-income rows plus up to 976 reconciliation-gap rows if those display | about 20 | about 14 new concepts (NII, interest income loans/securities, deposit interest, noninterest income/expense, provision, deposits, net/gross loans, allowance, nonaccrual, Tier 1) with period-scoped tags; Verifier checks a stratified bank sample; cheapest because 321-323 of 326 banks already tag NII, noninterest expense and deposits |
| 2 | **Pre-revenue / early-stage overlay (inside H, plus any no-revenue shell)** | about 131 (DATA-INFERRED upper bound; confirm by filing) | ASSUMED 2,000 to 3,300 (131 companies x about 15-25 revenue-dependent rows; not counted from data per row, so low confidence) | about 15-25 | Overlay rows are mostly from existing concepts (R&D, CFO, dilution); needs a cash-plus-investments concept and an accumulated-deficit concept; E1 check per company that revenue is truly absent |
| 3 | **Equity REIT and real estate operator (D1 equity part, D2)** | about 200 to 265 (D1 196 includes mortgage REITs; D2 69) | about 2,030 core + about 180 fcf_yield for D1 (inventory 187, payables 188, CCC 193, debtor days 104, gross margin 132, rnd 195, piotroski 189, margin trend 179, current/quick/working capital 180/180/178, roic 125, then fcf_yield 180), plus about 400 for D2 (ASSUMED from its pivot) = about 2,600 | about 10 | Mostly REASON-with-E1 (unclassified BS, no gross profit) and a few new rows (rental revenue exists; real-estate-at-cost, accumulated depreciation, secured debt, CFO dividend coverage); FFO stays unavailable with a stated reason |
| 4 | **Insurer (C), split P&C / life / health / agents** | 127 | about 1,910 (sum of the 20 inapplicable-metric blanks in the insurer column) | about 15 | Concepts: premiums earned/written, claims incurred, DAC amortization, net investment income, reserves; 93-102 of 127 tag the key ones; combined ratio only for a verified subset |
| 5 | **Lenders, brokers and BDCs (A2, B non-asset-manager)** | about 120 to 150 of 255 (sub-shapes not measured; ASSUMED) | about 800 to 1,000 ASSUMED (A2 and B blanks in the same inapplicable metrics at roughly half the company count) | about 7 | Reuse the bank concepts; classification by filing evidence is the main work; BDC rows need NII and NAV concepts |

Cross-cutting levers that remove more blank rows than any single template but are NOT sector templates (do not mix them into the template work):
- X1 Input fixes (files 26/27): total_debt tags and the zero-borrowings rule, operating-income-from-components, interest-expense net/expense tags, cash tag. The `roic` gap list shows `total_debt_resolved` missing in roughly 1,800 of about 2,200 incomplete cells (DATA-INFERRED, summed from the gap_reason listing; may overlap with banks). Also cuts debt_to_equity, net_cash, ev_ebitda and zero_debt blanks. Highest rows per effort overall, but each tag needs its own full-population coexistence check and is PROPOSAL-ONLY pending a reviewer.
- X2 Evidence layer for REASON rows in J (inventory family 979+780+1,346, rnd 1,275, piotroski 1,537 blanks in J): extend `company_filing_line_evidence` coverage to every blank (E1), because without it none of those blanks may be called not-applicable. Rows resolved are bounded by probe coverage, which was not measured.

Order I would build: X1 (inputs, so templates have correct inputs), then 1, 4, 3 (clear schemas, tags exist), then 2 and 5.

## 5. Proposed display contract for "no empty rows" (PROPOSAL-ONLY, product decision)
- R1 Every row slot has exactly one state: VALUE (with formula version and inputs), SWAPPED (shows the template metric, labelled with its own name, never under the industrial label), or REASON (one of: line not presented in the filing [E1 + accession], line combined with others [E1], earnings/base negative [E2], fewer than N years of filings [E3], filing states none [E4], not separately disclosed, not computable: input missing [open gap, not a structural claim], not reported in XBRL face statements [FFO, ASMs, rate base]).
- R2 Open gaps must be visible as gaps: "not available: input missing" is the only honest text for a blank we cannot yet prove structural; it is not an acceptable final state and counts against coverage.
- R3 A swapped template metric keeps its own definition page; never recompute an industrial metric on a bank's inputs.
- R4 FDIC-sourced bank rows (NIM, efficiency, Tier 1, NPL, top 30-50 banks, decisions.md 2026-10-18) are separate labelled rows and never mixed into SEC-derived rows. SEC-derived efficiency ratio (2.1) and FDIC bank-level efficiency can both exist and will differ (consolidated vs bank subsidiary): label both.
- R5 Dividend, buyback and reconciliation-gap rows for non-payers/non-holders need REASON text too ("no dividend paid in the latest FY", E2 from verified values), since their populations already narrow the denominator.
- R6 Classification stays effective-dated: a company that changes shape (a bank holding company that sells its bank, a SPAC after a merger) moves family at a filing date.
- R7 Present-but-inapplicable values (section 6) are suppressed or relabelled before any new swap, otherwise a bank would show both its own template rows and a meaningless fcf_yield.

## 6. Hazards and the biggest uncertainties
1. **Wrong or misleading values that exist today (DATA-INFERRED, not filing-checked): ** banks show values for fcf_yield (209/326), net_cash, debt_to_equity (210/326), ev_sales and 15 `net_interest_income` values built as InvestmentIncomeInterest minus total InterestExpense. These can be wrong-class values, not only blanks; they need Verifier review before the template ships. Route to the Data Chief.
2. **Bank NII is stored under the wrong concept.** `InterestIncomeExpenseNet` maps (priority 2) to `other_income_expense_net`, which resolves `NonoperatingIncomeExpense` first; a bank's net interest income can therefore appear as "other income/expense" or be absent. Not checked at fact level.
3. **Bank revenue perimeter** (total interest income vs NII + noninterest income vs `Revenues`) is undefined; every bank growth and margin row depends on it. Reviewer decision.
4. **Tag switches over time** (CECL, ASC 606-type): loans, allowance and provision change tags (recent counts: net loans pre-CECL tag 7 recent vs post-CECL 225; allowance 3 vs 233). A single-tag map will silently lose history. Needs period-scoped tag sets and coexistence checks.
5. **Tier 1 and other regulatory ratios** may be consolidated or bank-subsidiary only (dimension stripped by companyfacts): unverified which entity the undimensioned fact belongs to.
6. **Sector by SIC is a hypothesis**: 6199, 6211, 6798, 2834-2836 each hide several business models; the family counts will shift once classification uses filing evidence. SPAC/trust exclusion is already filing-based in code, others are not.
7. **Pre-revenue count (131) is not a measurement**: it is `revenue_sanity_resolved` missing in pharma SIC, mixing true pre-revenue with our own gaps.
8. **Combined ratio, FFO/AFFO, NOI, occupancy, NIM (true), same-store metrics** are not computable from standard XBRL for most companies; the contract must say so (R1) rather than fabricating them. How many insurers/REITs actually disclose component lines on the face is only tag-presence-estimated.
9. **Evidence ceiling**: no filing was opened for this file. Section 2 tag counts are our own tables; none is proof of a face line (21 section 6). Every REASON still needs E1.
10. **Rows-resolved estimates are upper bounds** from today's blank counts; ranks 2 and 5 are ASSUMED. The 10-year CAGR rows may conflict with the 2015 history gate; the "no empty rows" goal and the gate need a founder/reviewer ruling.
11. The 13 gated metrics (dividends etc.) and 82-metric registry: counts exclude them; a company page that shows all 82 slots would add them back.
12. **Concurrency**: the DB had 16 sessions when queried; no heavy query was run, so no fact-level coexistence check exists for any tag named here.

## 7. Next actions (proposal)
1. Accounting reviewer named; approves or rejects the bank bank-revenue perimeter, bank row set, and the SWAP/REASON contract (section 5).
2. Verifier: open 30 stratified banks' statements (income statement, balance sheet, regulatory-capital note) and confirm inputs and the NII storage concern (hazards 1-2), before any concept is added.
3. Tag Mapper: full-population coexistence checks for the section 2.1 bank tags (period-scoped sets) and the insurer premium/claims tags; Standardization Lead writes definitions.
4. Data Engineer/Chief: extend filing-line evidence probing to cover every currently blank slot in J (X2) and report probe coverage.
5. Sector Analyst (next run): classify a frozen cohort (30 banks, 20 insurers, 20 REITs split equity/mortgage, 20 pre-revenue candidates) from original statements and produce the row diff.

## Proposed ledger rows (not appended: this task restricts writes to this file)
| 2026-10-19 | Sector rows are blank by construction: no sector population exists in code, so banks are measured against industrial rows (326 banks, about 6,440 non-gated blank rows in 20 inapplicable metrics) | Coverage for a template-bound metric must use a filing-evidence-based family population, not SIC alone | `coverage_matrix.py` POPULATION_QUERIES; `company_data_point_coverage` pivot 2026-10-19 (DATA-INFERRED) |
| 2026-10-19 | `InterestIncomeExpenseNet` (321 of 326 banks) is mapped only as priority 2 of `other_income_expense_net`, and `interest_income` maps only `InvestmentIncomeInterest` (15 banks) | A bank's net interest income needs its own concept; the corporate `net_interest_income` formula is wrong for banks | `concept_mapping` and `company_sec_tag` queries 2026-10-19 (DATA-INFERRED) |

## Status
Task: COMPLETE as a design pass; every decision PROPOSAL-ONLY; every check that needs a filing or a fact-level query is NOT_RUN. Files touched: this file only. Untested scope: all filing evidence; fact-level coexistence; stored values of the present-but-inapplicable bank metrics; sub-shape counts inside 6199/6211/6798/pharma; probe coverage of `company_filing_line_evidence`.
