# SPGI document-first map, 2026-11-12 (read-only, built bottom-up from the 10-K)

Latest 10-K: accession 0000064040-26-000013, period end 2025-12-31. Evidence: R pages of FilingSummary (face statements + notes opened: R1.htm, R3.htm, R4.htm, R5.htm, R6.htm, R7.htm, R8.htm, R9.htm, R49.htm, R50.htm, R51.htm, R53.htm, R54.htm, R55.htm, R57.htm, R58.htm, R61.htm, R63.htm, R66.htm, R75.htm, R80.htm, R81.htm, R82.htm, R85.htm, R86.htm, R90.htm, R91.htm), values compared with data.sec.gov companyfacts (undimensioned, same accession). Values below are scaled to full units (USD, shares, USD/share). match = printed vs API; Y(abs) = same magnitude, sign differs (expense/outflow printed negative, tag positive).  Custom (company-prefix) tags are not in companyfacts: match NA.

Face statements: R3 income, R4 comprehensive income, R5 balance sheet, R7 cash flows. FY0 = FY2025. R3 also prints 'Actual shares outstanding at year end'.

| data_point | status | tags | page | label | fy0 printed | fy0 api | fy1 printed | fy1 api | match | note |
|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 15336000000 | 15336000000 | 14208000000 | 14208000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cost_of_revenue | mapped | CostOfRevenue | R3.htm | Operating-related expenses | 4563000000 | 4563000000 | 4361000000 | 4361000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| gross_profit | not_presented |  |  |  |  |  |  |  |  | IS prints Revenue, Operating-related expenses, Selling and general, Depreciation, Amortization, Total expenses; no gross profit line (agrees with Ritwik) |
| operating_expenses | mapped | CostsAndExpenses | R3.htm | Total expenses | 9159000000 | 9159000000 | 8730000000 | 8730000000 | Y/Y | printed 'Total expenses' (includes operating-related expenses = cost of revenue) / fy0=2025-12-31 fy1=2024-12-31 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | R3.htm | Selling and general expenses | 3417000000 | 3417000000 | 3196000000 | 3196000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| research_and_development | not_presented |  |  |  |  |  |  |  |  | no R&D line (ResearchAndDevelopmentExpense absent per MetaLinks) |
| operating_income | mapped | OperatingIncomeLoss | R3.htm | Operating profit | 6478000000 | 6478000000 | 5580000000 | 5580000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| interest_expense | combined | InterestExpenseNonoperating | R3.htm | Interest expense, net | 287000000 | 287000000 | 297000000 | 297000000 | Y/Y | 'Interest expense, net' is the company's own net line (FY2025 tag InterestExpenseNonoperating; Ritwik row: InterestIncomeExpenseNet 2018-2022) / fy0=2025-12-31 fy1=2024-12-31 |
| interest_income | not_presented |  |  |  |  |  |  |  |  | no separate interest income line (netted in 'Interest expense, net'); InvestmentIncomeInterest absent per MetaLinks |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | R3.htm | Other (income) expense, net | -36000000 | 36000000 | -25000000 | 25000000 | Y(abs)/Y(abs) | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before taxes on income | 6227000000 | 6227000000 | 5308000000 | 5308000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R3.htm | Provision for taxes on income | 1407000000 | 1407000000 | 1141000000 | 1141000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| net_income | mapped | NetIncomeLoss | R3.htm | Net income attributable to S&P Global Inc. | 4471000000 | 4471000000 | 3852000000 | 3852000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | R3.htm | Basic (in USD per share) | 14.67 | 14.67 | 12.36 | 12.36 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | R3.htm | Diluted (in USD per share) | 14.66 | 14.66 | 12.35 | 12.35 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 304800000 | 304800000 | 311600000 | 311600000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 305100000 | 305100000 | 311900000 | 311900000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | R9.htm | Dividends declared per share (in USD per share) | 3.84 | 3.84 | 3.64 | 3.64 | Y/Y | equity statement parenthetical R9 (annual dividends declared per share) / fy0=2025-12-31 fy1=2024-12-31 |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R4.htm | Comprehensive income attributable to S&P Global Inc. | 4657000000 | 4657000000 | 3732000000 | 3732000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1745000000 | 1745000000 | 1666000000 | 1666000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowance for doubtful accounts: | 3441000000 | 3441000000 | 2867000000 | 2867000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| inventory | not_presented |  |  |  |  |  |  |  |  | no inventory line (information services); InventoryNet absent per MetaLinks |
| current_assets | mapped | AssetsCurrent | R5.htm | Total current assets | 6296000000 | 6296000000 | 5459000000 | 5459000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 278000000 | 278000000 | 265000000 | 265000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| goodwill | mapped | Goodwill | R5.htm | Goodwill | 36475000000 | 36475000000 | 34917000000 | 34917000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| total_assets | mapped | Assets | R5.htm | Total Assets | 61200000000 | 61200000000 | 60221000000 | 60221000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| accounts_payable | mapped | AccountsPayableCurrent | R5.htm | Accounts payable | 610000000 | 610000000 | 553000000 | 553000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | R5.htm | Total current liabilities | 7637000000 | 7637000000 | 6392000000 | 6392000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| total_liabilities | mapped | Liabilities | R5.htm | Total liabilities | 25048000000 | 25048000000 | 22713000000 | 22713000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| total_debt | component sum | DebtCurrent;LongTermDebtNoncurrent | R5.htm | Short-term debt + Long-term debt | 13088000000 | 13088000000 | 11398000000 | 11398000000 | Y/Y | instant sum: 'Short-term debt' + 'Long-term debt'; operating leases excluded; no finance lease line on BS / fy0=2025-12-31 fy1=2024-12-31 |
| stockholders_equity | mapped | StockholdersEquity | R5.htm | Total equity – controlling interests | 31127000000 | 31127000000 | 33159000000 | 33159000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | R3.htm | Actual shares outstanding at year end (in shares) | 298800000 | 298800000 | 307800000 | 307800000 | Y/Y | IS face line 'Actual shares outstanding at year end (in shares)' (millions) / fy0=2025-12-31 fy1=2024-12-31 |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash provided by operating activities | 5651000000 | 5651000000 | 5689000000 | 5689000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R7.htm | Cash (used for) provided by investing activities | -704000000 | -704000000 | -255000000 | -255000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R7.htm | Cash used for financing activities | -4930000000 | -4930000000 | -4998000000 | -4998000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| capex | mapped | PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -195000000 | 195000000 | -124000000 | 124000000 | Y(abs)/Y(abs) | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| depreciation_and_amortization | component sum | Depreciation;AmortizationOfIntangibleAssets | R7.htm | Depreciation + Amortization of intangibles | 1179000000 | 1179000000 | 1173000000 | 1173000000 | Y/Y | CF prints 'Depreciation' 110 and 'Amortization of intangibles' 1,069 on separate lines; D&A = duration sum of the two printed face lines / fy0=2025-12-31 fy1=2024-12-31 |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | R7.htm | Amortization of intangibles | 1069000000 | 1069000000 | 1077000000 | 1077000000 | Y/Y | CF/IS 'Amortization of intangibles' 1,069 / fy0=2025-12-31 fy1=2024-12-31 |
| sbc | mapped | ShareBasedCompensation | R7.htm | Stock-based compensation | 236000000 | 236000000 | 247000000 | 247000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to shareholders | -1170000000 | 1170000000 | -1134000000 | 1134000000 | Y(abs)/Y(abs) | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of treasury shares | -5001000000 | 5001000000 | -3301000000 | 3301000000 | Y(abs)/Y(abs) | 'Repurchase of treasury shares' 5,001; 'Employee withholding tax on share-based payments' 132 is a separate line and excluded / fy0=2025-12-31 fy1=2024-12-31 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | R7.htm | Accounts receivable | -600000000 | 600000000 | -79000000 | 79000000 | Y(abs)/Y(abs) | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cf_inventory_change | not_presented |  |  |  |  |  |  |  |  | no inventory change line on CF |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | R7.htm | Accounts payable and accrued expenses | -55000000 | -55000000 | 245000000 | 245000000 | Y/Y | 'Accounts payable and accrued expenses' combined change (own label) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | R7.htm | Interest | 390000000 | 390000000 | 391000000 | 391000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | R7.htm | Income taxes | 1502000000 | 1502000000 | 1159000000 | 1159000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
No disagreement. interest_expense 'Interest expense, net' = combined (agrees; FY2025 carries the gross tag InterestExpenseNonoperating on the net-captioned line, so the combined status must follow the CAPTION not the tag); gross_profit not_presented (agrees).

## Era checks (older 10-K opened: tag on the same printed line?)
Older 10-K opened: 0000064040-21-000063 (period 2020-12-31); face pages ['R2.htm', 'R3.htm', 'R4.htm', 'R5.htm', 'R6.htm', 'R7.htm', 'R8.htm']. Result: 41 mapped rows checked.
- interest_expense: TAG CHANGED vs 0000064040-21-000063 (2020-12-31): old tag us-gaap:InterestExpense on 'Interest expense, net' (new 'Interest expense, net' us-gaap:InterestExpenseNonoperating)
- total_debt: tag us-gaap:DebtCurrent ABSENT from the old filing 0000064040-21-000063 (2020-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read) ; same_tag@2020-12-31
- (39 rows: same tag and same label on the older 10-K, no change)

## Mismatches / unresolved
- none

## Method and untested scope
- FILING-CHECKED = value read from the 10-K R page (MetaLinks used to locate tags/pages) and compared with companyfacts for the same accession; not_presented/OUT rows are FILING-CHECKED for the statements opened (all face statements plus the note pages that carry the candidate tags per MetaLinks); a note not opened could still hold an unprinted detail.
- Era check: one older 10-K per company (statement pages only, via MetaLinks); same-tag / label comparison on the same statement type. Note-page values of the older filing were not opened.
- Not covered: 10-Q-era tag history, quarterly values, segment-level data points, FSN store comparison (document-first read only).