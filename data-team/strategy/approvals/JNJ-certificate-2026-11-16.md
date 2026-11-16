# JNJ display certification, 2026-11-16: PASS

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/JNJ-request-2026-11-15.md`.
Coverage: `data-team/strategy/certification/JNJ-coverage-2026-11-15.csv`, sha256 `1fa552133fb82c88e9b3f748434f71aef01c59748395d45d6bf7fb3f57ef31be` (checked against the request). Cells: HIDDEN_ROW=44, SHOWN_VALUE=462.
Method: CERTIFICATION-METHOD-2026-11-16.md, run by `pipeline/scripts/certify_display.py --request ... --live` in workflow run https://github.com/inyourserve/scrooner/actions/runs/43813141621 (read-only). Every check reads SEC's Financial Statement and Notes data for the cited filing (fsn.*); nothing was re-downloaded.

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession and R page on every shown cell and part; signed parts sum | pass |
| 32 random shown cells (seed `JNJ-1fa552133fb8`) | 32 match, 0 wrong |
| total_debt census, face debt lines plus note leases | 11 of 11 years match |
| Hidden rows and hidden years | evidenced |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for JNJ alone. Pooled over certified companies (registry.csv): GILD and JNJ, 0 wrong in 64, upper bound 4.57%. The 0.10% target needs about 2,995 pooled cells.

## Hides evidenced

- cf_ap_change, operating_expenses, operating_income, shares_outstanding: no presented, undimensioned, annual fact of the row's tag family at a display-year end in any periodic filing (JNJ prints accounts payable change only combined with accrued liabilities, prints no operating income or total operating expenses line, and prints shares issued, not outstanding, on the balance sheet).

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days, for 52/53-week years), duration and dimensions; presented on the cited R page; summed cells match part by part; derived cells match their identity (total liabilities = assets less total equity including NCI; gross profit = shown revenue less shown cost of revenue).

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_receivable | 2020 | 13576000000 | 0000200406-21-000008 | R2 | AccountsReceivableNetCurrent |
| 2 | amortization_of_intangibles | 2024 | 4500000000 | 0000200406-25-000038 | R66 | AmortizationOfIntangibleAssets |
| 3 | basic_eps | 2021 | 7.93 | 0000200406-22-000022 | R5 | EarningsPerShareBasic |
| 4 | cash_and_equivalents | 2025 | 19709000000 | 0000200406-26-000016 | R3 | CashAndCashEquivalentsAtCarryingValue |
| 5 | cash_flow_financing | 2022 | -8871000000 | 0000200406-23-000016 | R10 | NetCashProvidedByUsedInFinancingActivities |
| 6 | cash_flow_investing | 2015 | -7735000000 | 0000200406-16-000071 | R8 | NetCashProvidedByUsedInInvestingActivities |
| 7 | cf_ar_change | 2017 | 633000000 | 0000200406-18-000005 | R8 | IncreaseDecreaseInAccountsReceivable |
| 8 | cf_ar_change | 2022 | 1290000000 | 0000200406-23-000016 | R10 | IncreaseDecreaseInAccountsReceivable |
| 9 | cfo | 2019 | 23416000000 | 0000200406-20-000010 | R9 | NetCashProvidedByUsedInOperatingActivities |
| 10 | cfo | 2025 | 24530000000 | 0000200406-26-000016 | R10 | NetCashProvidedByUsedInOperatingActivities |
| 11 | cost_of_revenue | 2019 | 27556000000 | 0000200406-20-000010 | R4 | CostOfGoodsAndServicesSold |
| 12 | current_assets | 2024 | 55893000000 | 0000200406-25-000038 | R3 | AssetsCurrent |
| 13 | current_liabilities | 2018 | 31230000000 | 0000200406-19-000009 | R2 | LiabilitiesCurrent |
| 14 | depreciation_and_amortization | 2024 | 7339000000 | 0000200406-25-000038 | R10 | DepreciationDepletionAndAmortization |
| 15 | diluted_eps | 2019 | 5.6300 | 0000200406-20-000010 | R4 | EarningsPerShareDiluted |
| 16 | diluted_eps | 2020 | 5.51 | 0000200406-21-000008 | R4 | EarningsPerShareDiluted |
| 17 | dividends_per_share | 2015 | 2.95 | 0000200406-16-000071 | R4 | CommonStockDividendsPerShareCashPaid |
| 18 | gross_profit | 2020 | 54157000000 | 0000200406-21-000008 | R4 | GrossProfit |
| 19 | gross_profit | 2025 | 63937000000 | 0000200406-26-000016 | R5 | GrossProfit |
| 20 | income_before_tax | 2025 | 32581000000 | 0000200406-26-000016 | R5 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| 21 | interest_income | 2022 | 490000000 | 0000200406-23-000016 | R5 | InvestmentIncomeInterest |
| 22 | net_income | 2018 | 15297000000.0000 | 0000200406-19-000009 | R4 | NetIncomeLoss |
| 23 | other_income_expense_net | 2017 | 42000000 | 0000200406-20-000010 | R4 | OtherNonoperatingIncomeExpense |
| 24 | other_income_expense_net | 2020 | -2899000000 | 0000200406-21-000008 | R4 | OtherNonoperatingIncomeExpense |
| 25 | ppe_net | 2018 | 17035000000 | 0000200406-19-000009 | R2 | PropertyPlantAndEquipmentNet |
| 26 | ppe_net | 2020 | 18766000000 | 0000200406-21-000008 | R2 | PropertyPlantAndEquipmentNet |
| 27 | research_and_development | 2015 | 9046000000 | 0000200406-16-000071 | R4 | ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost |
| 28 | sbc | 2022 | 1138000000 | 0000200406-23-000016 | R10 | ShareBasedCompensation |
| 29 | share_buybacks | 2017 | 6358000000 | 0000200406-18-000005 | R8 | PaymentsForRepurchaseOfCommonStock |
| 30 | share_buybacks | 2021 | 3456000000 | 0000200406-22-000022 | R10 | PaymentsForRepurchaseOfCommonStock |
| 31 | total_assets | 2020 | 174894000000 | 0000200406-21-000008 | R2 | Assets |
| 32 | total_liabilities | 2021 | 107995000000 | 0000200406-22-000022 | R3 | Liabilities |

## Limits

- This certifies evidence for the coverage file above. It is not approval for a production write (that needs the founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
- fsn.* is SEC's own extraction. Where it lacks a fact, the tool reports NOT_FOUND for the approver; there were none in this run.
