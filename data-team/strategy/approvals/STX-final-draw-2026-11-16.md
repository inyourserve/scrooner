# STX display certification, 2026-11-16: FAIL

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/STX-request-2026-11-15.md`.
Coverage: `data-team/strategy/certification/STX-coverage-2026-11-15.csv`, sha256 `8e978b2772b91edfe2448824e0e8abae8af2339315274effe5f2330af582fa18` (checked against the request). Cells: HIDDEN_ROW=12, SHOWN_VALUE=540.
Method: CERTIFICATION-METHOD-2026-11-16.md, run by `pipeline/scripts/certify_display.py --request ... --live` in workflow run https://github.com/inyourserve/scrooner/actions/runs/43813141621 (read-only). Every check reads SEC's Financial Statement and Notes data for the cited filing (fsn.*); nothing was re-downloaded.

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession and R page on every shown cell and part; signed parts sum | pass |
| 32 random shown cells (seed `STX-8e978b2772b9`) | 31 match, 1 wrong |
| total_debt census, face debt lines plus note leases | 12 of 12 years match |
| Hidden rows and hidden years | evidenced |

**Bound:** 1 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **13.98%** for STX alone. Pooled over certified companies (registry.csv): GILD and JNJ, 0 wrong in 64, upper bound 4.57%. The 0.10% target needs about 2,995 pooled cells.

## Findings

- **dividends_per_share FY2022 is shown as 2,770,000.** It is copied faithfully from the filing: the FY2024 10-K (0001137789-24-000068, R9, equity statement) tags `CommonStockDividendsPerShareDeclared` at 2022-06-30 as 2,770,000 with unit USD, a filer scale error for $2.77. A screener cannot display a $2.77 million dividend per share. The fix is to take FY2022 from its own 10-K (FY2022) or from the R9 rendered figure, and the builder should reject per-share values above 1,000.
- Everything else checked clean: 31 of 32 random shown cells match, total_debt matches in all 12 years, the gross_profit hide is evidenced.

## Hides evidenced

- gross_profit: no presented, undimensioned, annual GrossProfit fact at a display-year end.

## The 32 drawn cells

Each except dividends_per_share FY2022 (see Findings) matched the cited filing in fsn.*: same tag, period end (within 7 days, for 52/53-week years), duration and dimensions; presented on the cited R page; summed cells match part by part; derived cells match their identity (total liabilities = assets less total equity including NCI; gross profit = shown revenue less shown cost of revenue).

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_payable | 2016 | 1517000000 | 0001047469-16-014732 | R2 | AccountsPayableCurrent |
| 2 | accounts_payable | 2024 | 1786000000 | 0001137789-24-000068 | R5 | AccountsPayableCurrent |
| 3 | amortization_of_intangibles | 2023 | 9000000 | 0001137789-23-000049 | R58 | AmortizationOfIntangibleAssets |
| 4 | capex | 2021 | 498000000 | 0001137789-21-000049 | R7 | PaymentsToAcquirePropertyPlantAndEquipment |
| 5 | cash_and_equivalents | 2019 | 2220000000 | 0001193125-19-212028 | R2 | CashAndCashEquivalentsAtCarryingValue |
| 6 | cash_paid_for_income_taxes | 2021 | 44000000 | 0001137789-21-000049 | R7 | IncomeTaxesPaidNet |
| 7 | cash_paid_for_income_taxes | 2024 | 30000000 | 0001137789-24-000068 | R8 | IncomeTaxesPaidNet |
| 8 | cf_ap_change | 2017 | 121000000 | 0001193125-17-248796 | R6 | IncreaseDecreaseInAccountsPayable |
| 9 | cf_ap_change | 2025 | -242000000 | 0001137789-25-000157 | R8 | IncreaseDecreaseInAccountsPayable |
| 10 | cf_ar_change | 2020 | 127000000 | 0001137789-20-000057 | R7 | IncreaseDecreaseInAccountsReceivable |
| 11 | cfo | 2024 | 918000000 | 0001137789-24-000068 | R8 | NetCashProvidedByUsedInOperatingActivities |
| 12 | cost_of_revenue | 2026 | 6637000000 | 0001137789-26-000159 | R4 | CostOfGoodsAndServicesSold |
| 13 | current_assets | 2020 | 4114000000 | 0001137789-20-000057 | R3 | AssetsCurrent |
| 14 | diluted_eps | 2018 | 4.05 | 0001193125-18-238271 | R4 | EarningsPerShareDiluted |
| 15 | dividends_paid | 2016 | 727000000 | 0001047469-16-014732 | R6 | PaymentsOfDividendsCommonStock |
| 16 | dividends_per_share | 2022 | 2770000 | 0001137789-24-000068 | R9 | CommonStockDividendsPerShareDeclared |
| 17 | goodwill | 2020 | 1237000000 | 0001137789-20-000057 | R3 | Goodwill |
| 18 | income_before_tax | 2024 | 445000000 | 0001137789-24-000068 | R6 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| 19 | income_tax_expense | 2021 | 34000000 | 0001137789-21-000049 | R5 | IncomeTaxExpenseBenefit |
| 20 | interest_expense | 2024 | 332000000 | 0001137789-25-000157 | R6 | InterestExpenseNonoperating |
| 21 | inventory | 2022 | 1565000000 | 0001137789-22-000055 | R4 | InventoryNet |
| 22 | net_income | 2020 | 1004000000 | 0001137789-20-000057 | R5 | NetIncomeLoss |
| 23 | net_income | 2022 | 1649000000 | 0001137789-22-000055 | R6 | NetIncomeLoss |
| 24 | net_income | 2024 | 335000000 | 0001137789-24-000068 | R6 | NetIncomeLoss |
| 25 | operating_expenses | 2020 | 1542000000.0000 | 0001137789-22-000055 | R6 | RestructuringCostsAndAssetImpairmentCharges + SellingGeneralAndAdministrativeExpense + ResearchAndDevelopmentExpense + Amortizationofintangibleassetsexcludingamountincludedincostofrevenue |
| 26 | operating_income | 2019 | 1487000000 | 0001193125-19-212028 | R4 | OperatingIncomeLoss |
| 27 | other_income_expense_net | 2017 | -29000000 | 0001193125-17-248796 | R4 | OtherNonoperatingIncomeExpense |
| 28 | research_and_development | 2024 | 654000000 | 0001137789-24-000068 | R6 | ResearchAndDevelopmentExpense |
| 29 | share_buybacks | 2025 | 0 | 0001137789-25-000157 | R8 | PaymentsForRepurchaseOfCommonStock |
| 30 | share_buybacks | 2026 | 176000000 | 0001137789-26-000159 | R5 | PaymentsForRepurchaseOfCommonStock |
| 31 | weighted_basic_shares | 2022 | 220000000 | 0001137789-22-000055 | R6 | WeightedAverageNumberOfSharesOutstandingBasic |
| 32 | weighted_diluted_shares | 2017 | 299000000 | 0001193125-17-248796 | R4 | WeightedAverageNumberOfDilutedSharesOutstanding |

## Limits

- This certifies evidence for the coverage file above. It is not approval for a production write (that needs the founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
- fsn.* is SEC's own extraction. Where it lacks a fact, the tool reports NOT_FOUND for the approver; there were none in this run.

## To re-request

Fix the findings, re-export the coverage file, and file a new request. The new file's hash gives a new seed and a new draw.
