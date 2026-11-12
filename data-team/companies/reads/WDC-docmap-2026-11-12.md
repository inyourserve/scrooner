# WDC document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0001628280-26-057139 (CIK 0000106040, filed 2026-08-14, FY ended 2026-07-03). Statement pages: BS R3.htm, CF R6.htm, CI R5.htm, COVER R1.htm, EQ R7.htm, IS R4.htm.
- Era 10-K for interest_expense (InterestExpense, FY2023): 0000106040-23-000024: IS R5.htm 'Interest expense' printed -312000000 API 312000000 match Y (sign differs: printed in parentheses/negated label).
- Era 10-K for depreciation_and_amortization (DepreciationAndAmortization, FY2025): 0000106040-25-000038: CF R7.htm 'Depreciation and amortization' printed 451000000 API 451000000 match Y.
- Era 10-K for depreciation_and_amortization (Depreciation, FY2025): 0000106040-25-000038: tag not on the statement pages (note or dimensioned).
- Era 10-K for dividends_paid (PaymentsOfDividends, FY2025): 0000106040-25-000038: CF R7.htm 'Dividends paid to shareholders' printed -44000000 API 44000000 match Y (sign differs: printed in parentheses/negated label).
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R4.htm | Revenue, net | 12919000000 | 12919000000 | 9520000000 | 9520000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R4.htm | Cost of revenue | 6608000000 | 6608000000 | 5828000000 | 5828000000 | Y | FILING-CHECKED | line above gross profit (rule 4) |
| gross_profit | mapped | GrossProfit | IS R4.htm | Gross profit | 6311000000 | 6311000000 | 3692000000 | 3692000000 | Y | FILING-CHECKED |  |
| operating_expenses | mapped | OperatingExpenses | IS R4.htm | Total operating expenses | 1858000000 | 1858000000 | 1358000000 | 1358000000 | Y | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R4.htm | Selling, general and administrative | 551000000 | 551000000 | 568000000 | 568000000 | Y | FILING-CHECKED |  |
| research_and_development | mapped | ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost | IS R4.htm | Research and development | 1161000000 | 1161000000 | 994000000 | 994000000 | Y | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R4.htm | Operating income (loss) | 4453000000 | 4453000000 | 2334000000 | 2334000000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpenseNonoperating | IS R4.htm | Interest expense | -165000000 | 165000000 | -357000000 | 357000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| interest_income | mapped | InvestmentIncomeInterest | IS R4.htm | Interest income | 51000000 | 51000000 | 45000000 | 45000000 | Y | FILING-CHECKED |  |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R4.htm | Other income (expense), net | -25000000 | -25000000 | -20000000 | -20000000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R4.htm | Income (loss) before taxes | 9905000000 | 9905000000 | 1130000000 | 1130000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R4.htm | Income tax expense (benefit) | 481000000 | 481000000 | -513000000 | -513000000 | Y | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R4.htm | Net income (loss) from continuing operations | 9424000000 | 9424000000 | 1889000000 | 1889000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R4.htm | Net income (loss) per share - basic (in dollars per share) | 26.92 | 26.92 | 5.31 | 5.31 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R4.htm | Net income (loss) per share - diluted (in dollars per share) | 24.28 | 24.28 | 5.12 | 5.12 | Y | FILING-CHECKED |  |
| weighted_basic_shares | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| weighted_diluted_shares | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| dividends_per_share | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R5.htm | Total comprehensive income (loss) | 9427000000 | 9427000000 | 2075000000 | 2075000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R3.htm | Cash and cash equivalents | 1579000000 | 1579000000 | 2114000000 | 2114000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | BS R3.htm | Accounts receivable, net | 2026000000 | 2026000000 | 1486000000 | 1486000000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R3.htm | Inventories | 1511000000 | 1511000000 | 1291000000 | 1291000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R3.htm | Total current assets | 5634000000 | 5634000000 | 5856000000 | 5856000000 | Y | FILING-CHECKED |  |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R3.htm | Property, plant and equipment, net | 2476000000 | 2476000000 | 2343000000 | 2343000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R3.htm | Goodwill | 4321000000 | 4321000000 | 4319000000 | 4319000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R3.htm | Total assets | 13861000000 | 13861000000 | 14002000000 | 14002000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R3.htm | Accounts payable | 1774000000 | 1774000000 | 1266000000 | 1266000000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R3.htm | Total current liabilities | 4240000000 | 4240000000 | 5418000000 | 5418000000 | Y | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R3.htm | Total liabilities | 4997000000 | 4997000000 | 8462000000 | 8462000000 | Y | FILING-CHECKED |  |
| total_debt | component sum | LongTermDebtCurrent+LongTermDebtNoncurrent | BS R3.htm | Current portion of long-term debt + Long-term debt | 1052000000 | 1052000000 | 4711000000 | 4711000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R3.htm | Total shareholders’ equity | 8864000000 | 8864000000 | 5311000000 | 5311000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding (in shares) | 360540944 | 360540944 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R6.htm | Net cash provided by (used in) operating activities | 3929000000 | 3929000000 | 1691000000 | 1691000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R6.htm | Net cash provided by (used in) investing activities | -429000000 | -429000000 | 150000000 | 150000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R6.htm | Net cash provided by (used in) financing activities | -4032000000 | -4032000000 | -1612000000 | -1612000000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R6.htm | Purchases of property, plant and equipment | -418000000 | 418000000 | -412000000 | 412000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R6.htm | Depreciation and amortization | 375000000 | 375000000 | 451000000 | 451000000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R6.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R6.htm | Stock-based compensation | 204000000 | 204000000 | 265000000 | 265000000 | Y | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R6.htm | Dividends paid to common shareholders | -174000000 | 174000000 | -44000000 | 44000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R6.htm | Repurchases of common stock | -2592000000 | 2592000000 | -149000000 | 149000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | CF R6.htm | Accounts receivable, net | -541000000 | 541000000 | 79000000 | -79000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R6.htm | Inventories | -218000000 | 218000000 | -409000000 | 409000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayableTrade | CF R6.htm | Accounts payable | 385000000 | 385000000 | 307000000 | 307000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R6.htm | Cash paid for interest | 169000000 | 169000000 | 367000000 | 367000000 | Y | FILING-CHECKED |  |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R6.htm | Cash paid for income taxes | 734000000 | 734000000 | 789000000 | 789000000 | Y | FILING-CHECKED |  |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2024, 2025, 2026]; ERA-CHECK others: {'InterestExpense': [2022, 2023]}
- depreciation_and_amortization: chosen tag FY[2026]; ERA-CHECK others: {'DepreciationAndAmortization': [2022, 2023, 2024, 2025], 'Depreciation': [2022, 2023, 2024, 2025]}
- dividends_paid: chosen tag FY[2026]; ERA-CHECK others: {'PaymentsOfDividends': [2022, 2025]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- none

## Mismatches (printed vs API)
- none beyond sign differences
