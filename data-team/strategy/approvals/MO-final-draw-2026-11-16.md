# MO display certification, 2026-11-16: FAIL

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/MO-request-2026-11-15.md`.
Coverage: `data-team/strategy/certification/MO-coverage-2026-11-15.csv`, sha256 `6025e024d1601d433ec7b8ff62a206b336e9721fbe70cb480f34c7a30f6b3621` (checked against the request). Cells: HIDDEN_ROW=33, SHOWN_VALUE=447.
Method: CERTIFICATION-METHOD-2026-11-16.md, run by `pipeline/scripts/certify_display.py --request ... --live` in workflow run https://github.com/inyourserve/scrooner/actions/runs/43813141621 (read-only). Every check reads SEC's Financial Statement and Notes data for the cited filing (fsn.*); nothing was re-downloaded.

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession and R page on every shown cell and part; signed parts sum | pass |
| 32 random shown cells (seed `MO-6025e024d160`) | 32 match, 0 wrong |
| total_debt census, face debt lines plus note leases | 9 of 9 years match |
| Hidden rows and hidden years | see findings |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for MO alone. Pooled over certified companies (registry.csv): GILD and JNJ, 0 wrong in 64, upper bound 4.57%. The 0.10% target needs about 2,995 pooled cells.

## Findings

- **other_income_expense_net is hidden as never reported, but it is reported.** The FY2015 10-K (0000764180-16-000128) prints "Other income, net" on the income statement (R4, `OtherNonoperatingIncomeExpense`): FY2015 $5,000,000, FY2014 and FY2013 $0. The row must be shown, at least for FY2015, with the in-row gap rule applied to the other years.
- Everything else checked clean: 32 of 32 random shown cells match, total_debt matches in all 9 years, the sbc and sga_expense hides are evidenced.

## Hides evidenced

- sbc and sga_expense: no presented, undimensioned, annual fact of the family at a display-year end.

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days, for 52/53-week years), duration and dimensions; presented on the cited R page; summed cells match part by part; derived cells match their identity (total liabilities = assets less total equity including NCI; gross profit = shown revenue less shown cost of revenue).

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | basic_eps | 2021 | 1.34 | 0000764180-22-000019 | R5 | EarningsPerShareBasic |
| 2 | basic_eps | 2023 | 4.57 | 0000764180-24-000018 | R5 | EarningsPerShareBasic |
| 3 | cash_paid_for_interest | 2015 | 776000000 | 0000764180-16-000128 | R6 | InterestPaid |
| 4 | cf_ap_change | 2019 | -79000000 | 0000764180-20-000018 | R6 | IncreaseDecreaseInAccountsPayable |
| 5 | cf_ap_change | 2022 | 92000000 | 0000764180-23-000020 | R7 | IncreaseDecreaseInAccountsPayable |
| 6 | cf_inventory_change | 2023 | 15000000 | 0000764180-24-000018 | R7 | IncreaseDecreaseInInventories |
| 7 | cfo | 2022 | 8256000000 | 0000764180-23-000020 | R7 | NetCashProvidedByUsedInOperatingActivities |
| 8 | comprehensive_income | 2025 | 6720000000 | 0000764180-26-000017 | R6 | ComprehensiveIncomeNetOfTax |
| 9 | cost_of_revenue | 2015 | 14320000000 | 0000764180-16-000128 | R4 | CostOfGoodsSold + ExciseAndSalesTaxes |
| 10 | current_assets | 2020 | 7117000000 | 0000764180-21-000037 | R2 | AssetsCurrent |
| 11 | current_assets | 2021 | 6083000000 | 0000764180-22-000019 | R3 | AssetsCurrent |
| 12 | depreciation_and_amortization | 2023 | 272000000 | 0000764180-24-000018 | R7 | DepreciationDepletionAndAmortization |
| 13 | depreciation_and_amortization | 2025 | 266000000 | 0000764180-26-000017 | R7 | DepreciationDepletionAndAmortization |
| 14 | diluted_eps | 2021 | 1.34 | 0000764180-22-000019 | R5 | EarningsPerShareDiluted |
| 15 | dividends_per_share | 2021 | 3.52 | 0000764180-22-000019 | R9 | CommonStockDividendsPerShareDeclared |
| 16 | income_before_tax | 2024 | 13658000000 | 0000764180-25-000019 | R5 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| 17 | income_tax_expense | 2017 | -399000000 | 0000764180-18-000028 | R4 | IncomeTaxExpenseBenefit |
| 18 | income_tax_expense | 2024 | 2394000000 | 0000764180-25-000019 | R5 | IncomeTaxExpenseBenefit |
| 19 | interest_expense | 2015 | 808000000 | 0000764180-16-000128 | R99 | InterestExpense |
| 20 | interest_expense | 2017 | 736000000 | 0000764180-20-000018 | R107 | InterestExpense |
| 21 | interest_expense | 2019 | 1322000000 | 0000764180-20-000018 | R107 | InterestExpense |
| 22 | inventory | 2021 | 1194000000 | 0000764180-22-000019 | R3 | InventoryNet |
| 23 | net_income | 2023 | 8130000000 | 0000764180-24-000018 | R5 | NetIncomeLoss |
| 24 | operating_expenses | 2018 | 3139000000.0000 | 0000764180-19-000023 | R4 | AssetImpairmentandBusinessExitCosts + MarketingAdministrationandResearchCosts |
| 25 | research_and_development | 2015 | 186000000 | 0000764180-16-000128 | R99 | ResearchAndDevelopmentExpense |
| 26 | revenue | 2019 | 25110000000.0000 | 0000764180-20-000018 | R4 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 27 | revenue | 2020 | 26153000000.0000 | 0000764180-21-000037 | R4 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 28 | share_buybacks | 2018 | 1673000000 | 0000764180-19-000023 | R6 | PaymentsForRepurchaseOfCommonStock |
| 29 | stockholders_equity | 2019 | 6222000000 | 0000764180-20-000018 | R2 | StockholdersEquity |
| 30 | total_liabilities | 2015 | 28549000000 | 0000764180-17-000028 | R2 | Liabilities |
| 31 | weighted_basic_shares | 2016 | 1952000000 | 0000764180-19-000023 | R74 | WeightedAverageNumberOfSharesOutstandingBasic |
| 32 | weighted_basic_shares | 2017 | 1921000000 | 0000764180-19-000023 | R74 | WeightedAverageNumberOfSharesOutstandingBasic |

## Limits

- This certifies evidence for the coverage file above. It is not approval for a production write (that needs the founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
- fsn.* is SEC's own extraction. Where it lacks a fact, the tool reports NOT_FOUND for the approver; there were none in this run.

## To re-request

Fix the findings, re-export the coverage file, and file a new request. The new file's hash gives a new seed and a new draw.
