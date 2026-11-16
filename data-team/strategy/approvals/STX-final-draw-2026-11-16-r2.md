# STX display certification, 2026-11-16 (second request): FAIL

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/STX-request-2026-11-16.md`. This supersedes the STX verdict of the 2026-11-15 request.
Coverage: `data-team/strategy/certification/STX-coverage-2026-11-16.csv`, sha256 `212b6c0455572a9627ccad9318481313059a823a4ea0f13a1aba523693426585` (checked against the request). Cells: HIDDEN_ROW=12, SHOWN_VALUE=540.
Method: CERTIFICATION-METHOD-2026-11-16.md and doc 02 (founder decision 2026-11-16, display rules 2bc5a106, founder approvals 2026-11-17 93c8d6ba), run by `certify_display.py --request ... --live` in https://github.com/inyourserve/scrooner/actions/runs/43935238837 (read-only, fsn.*, no re-downloads).

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession, R page on every shown cell and part; signed parts sum; per-share plausibility census | 1 failing |
| 32 random shown cells (seed `STX-212b6c045557`) | 32 match, 0 wrong |
| total_debt census | 12 of 12 years match |
| Hide classes, hidden rows and years | evidenced |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for STX alone. Pooled over the latest PASS of each company in registry.csv (GILD, JNJ): 0 wrong in 64, upper bound 4.57%.

## Findings

- **The 2026-11-16 finding is not fixed.** dividends_per_share FY2022 is still shown as 2,770,000 (FY2024 10-K 0001137789-24-000068, R9, `CommonStockDividendsPerShareDeclared`, a filer scale error for $2.77). This draw did not pick that cell; the gate's per-share census (every shown cell, not the sample) caught it. Fix: take FY2022 from its own 10-K or the R9 rendered figure, and have the builder reject per-share values above 1,000.
- Everything else checked clean: 32 of 32 random shown cells match, total_debt matches in all 12 years, the gross_profit hide is evidenced.

## Hides evidenced

- gross_profit: no presented, undimensioned, annual GrossProfit fact at a display-year end.

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days), duration and dimensions; presented on the cited R page; summed cells part by part; derived cells by their identity.

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_receivable | 2015 | 1735000000 | 0001047469-15-006787 | R2 | AccountsReceivableNetCurrent |
| 2 | accounts_receivable | 2022 | 1532000000 | 0001137789-22-000055 | R4 | AccountsReceivableNetCurrent |
| 3 | capex | 2021 | 498000000 | 0001137789-21-000049 | R7 | PaymentsToAcquirePropertyPlantAndEquipment |
| 4 | capex | 2024 | 254000000 | 0001137789-24-000068 | R8 | PaymentsToAcquirePropertyPlantAndEquipment |
| 5 | cash_and_equivalents | 2024 | 1358000000 | 0001137789-24-000068 | R5 | CashAndCashEquivalentsAtCarryingValue |
| 6 | cash_flow_investing | 2020 | -635000000 | 0001137789-20-000057 | R7 | NetCashProvidedByUsedInInvestingActivities |
| 7 | cash_paid_for_income_taxes | 2021 | 44000000 | 0001137789-21-000049 | R7 | IncomeTaxesPaidNet |
| 8 | cash_paid_for_interest | 2020 | 226000000 | 0001137789-22-000055 | R8 | InterestPaidNet |
| 9 | cash_paid_for_interest | 2021 | 184000000 | 0001137789-22-000055 | R8 | InterestPaidNet |
| 10 | cf_ap_change | 2017 | 121000000 | 0001193125-17-248796 | R6 | IncreaseDecreaseInAccountsPayable |
| 11 | cf_ap_change | 2021 | -14000000 | 0001137789-21-000049 | R7 | IncreaseDecreaseInAccountsPayable |
| 12 | cf_ap_change | 2024 | 227000000 | 0001137789-24-000068 | R8 | IncreaseDecreaseInAccountsPayable |
| 13 | cf_inventory_change | 2016 | -145000000 | 0001047469-16-014732 | R6 | IncreaseDecreaseInInventories |
| 14 | cf_inventory_change | 2021 | 64000000 | 0001137789-21-000049 | R7 | IncreaseDecreaseInInventories |
| 15 | comprehensive_income | 2017 | 780000000 | 0001193125-17-248796 | R5 | ComprehensiveIncomeNetOfTax |
| 16 | income_before_tax | 2016 | 274000000 | 0001193125-17-248796 | R4 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| 17 | income_tax_expense | 2015 | 228000000 | 0001047469-15-006787 | R4 | IncomeTaxExpenseBenefit |
| 18 | interest_income | 2019 | 84000000 | 0001193125-19-212028 | R4 | InvestmentIncomeInterest |
| 19 | interest_income | 2026 | 30000000 | 0001137789-26-000159 | R4 | InvestmentIncomeInterest |
| 20 | inventory | 2026 | 1571000000 | 0001137789-26-000159 | R3 | InventoryNet |
| 21 | operating_expenses | 2023 | 1693000000.0000 | 0001137789-23-000049 | R7 | Amortizationofintangibleassetsexcludingamountincludedincostofrevenue + LossContingencyLossInPeriod + ResearchAndDevelopmentExpense + RestructuringCostsAndAssetImpairmentCharges + SellingGeneralAndAdministrativeExpense |
| 22 | ppe_net | 2026 | 2034000000 | 0001137789-26-000159 | R3 | PropertyPlantAndEquipmentNet |
| 23 | research_and_development | 2024 | 654000000 | 0001137789-24-000068 | R6 | ResearchAndDevelopmentExpense |
| 24 | research_and_development | 2026 | 755000000 | 0001137789-26-000159 | R4 | ResearchAndDevelopmentExpense |
| 25 | revenue | 2021 | 10681000000 | 0001137789-21-000049 | R5 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 26 | revenue | 2025 | 9097000000 | 0001137789-25-000157 | R6 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 27 | sga_expense | 2023 | 491000000 | 0001137789-23-000049 | R7 | SellingGeneralAndAdministrativeExpense |
| 28 | share_buybacks | 2021 | 2047000000 | 0001137789-21-000049 | R7 | PaymentsForRepurchaseOfCommonStock |
| 29 | total_assets | 2015 | 9845000000 | 0001047469-15-006787 | R2 | Assets |
| 30 | total_assets | 2023 | 7556000000 | 0001137789-23-000049 | R5 | Assets |
| 31 | weighted_basic_shares | 2020 | 262000000 | 0001137789-20-000057 | R5 | WeightedAverageNumberOfSharesOutstandingBasic |
| 32 | weighted_diluted_shares | 2018 | 292000000 | 0001193125-18-238271 | R4 | WeightedAverageNumberOfDilutedSharesOutstanding |

## Limits

- Evidence for the coverage file above, not approval for a production write (founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
