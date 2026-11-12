# MCK document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0000927653-26-000069 (CIK 0000927653, filed 2026-05-08, FY ended 2026-03-31). Statement pages: BS R5.htm, BSP R6.htm, CF R9.htm, CI R4.htm, COVER R1.htm, EQ R7.htm, EQP R8.htm, IS R3.htm.
- Era 10-K for interest_expense (InterestExpense, FY2024): 0000927653-25-000036: tag not on the statement pages (note or dimensioned).
- Era 10-K for income_before_tax (IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, FY2025): 0000927653-26-000069: tag not on the statement pages (note or dimensioned).
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R3.htm | Revenues | 403430000000 | 403430000000 | 359051000000 | 359051000000 | Y | FILING-CHECKED |  |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R3.htm | Cost of sales | -388880000000 | 388880000000 | -345728000000 | 345728000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | line above gross profit (rule 4) |
| gross_profit | mapped | GrossProfit | IS R3.htm | Gross profit | 14550000000 | 14550000000 | 13323000000 | 13323000000 | Y | FILING-CHECKED |  |
| operating_expenses | mapped | OperatingExpenses | IS R3.htm | Total operating expenses | -8338000000 | 8338000000 | -8901000000 | 8901000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R3.htm | Selling, distribution, general, and administrative expenses | -8096000000 | 8096000000 | -8507000000 | 8507000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R3.htm | Operating income | 6212000000 | 6212000000 | 4422000000 | 4422000000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpenseNonoperating | IS R3.htm | Interest expense | -247000000 | 247000000 | -265000000 | 265000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| interest_income | not_presented |  | IS R3.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R3.htm | Other income, net | 236000000 | 236000000 | 202000000 | 202000000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossIncludingPortionAttributableToNoncontrollingInterest | IS R3.htm | Income before income taxes | 6201000000 | 6201000000 | 4359000000 | 4359000000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R3.htm | Income tax expense | -1102000000 | 1102000000 | -878000000 | 878000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R3.htm | Net income attributable to McKesson Corporation | 4762000000 | 4762000000 | 3295000000 | 3295000000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R3.htm | Basic (in dollars per share) | 38.55 | 38.55 | 25.86 | 25.86 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R3.htm | Diluted (in dollars per share) | 38.38 | 38.38 | 25.72 | 25.72 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R3.htm | Basic (in shares) | 123600000 | 123600000 | 127400000 | 127400000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R3.htm | Diluted (in shares) | 124100000 | 124100000 | 128100000 | 128100000 | Y | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | EQP R8.htm | Cash dividends declared per common share (in dollars per sha | 3.17 | 3.17 | 2.75 | 2.75 | Y (printed column 3) | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R4.htm | Comprehensive income attributable to McKesson Corporation | 4949000000 | 4949000000 | 3244000000 | 3244000000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R5.htm | Cash and cash equivalents | 3975000000 | 3975000000 | 5691000000 | 5691000000 | Y | FILING-CHECKED |  |
| accounts_receivable | mapped | ReceivablesNetCurrent | BS R5.htm | Receivables, net | 27985000000 | 27985000000 | 25643000000 | 25643000000 | Y | FILING-CHECKED |  |
| inventory | mapped | InventoryNet | BS R5.htm | Inventories, net | 24207000000 | 24207000000 | 23001000000 | 23001000000 | Y | FILING-CHECKED |  |
| current_assets | mapped | AssetsCurrent | BS R5.htm | Total current assets | 57210000000 | 57210000000 | 55398000000 | 55398000000 | Y | FILING-CHECKED |  |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R5.htm | Property, plant, and equipment, net | 2668000000 | 2668000000 | 2502000000 | 2502000000 | Y | FILING-CHECKED |  |
| goodwill | mapped | Goodwill | BS R5.htm | Goodwill | 11316000000 | 11316000000 | 10022000000 | 10022000000 | Y | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R5.htm | Total assets | 82323000000 | 82323000000 | 75140000000 | 75140000000 | Y | FILING-CHECKED |  |
| accounts_payable | mapped | AccountsPayableCurrent | BS R5.htm | Drafts and accounts payable | 59973000000 | 59973000000 | 55330000000 | 55330000000 | Y | FILING-CHECKED |  |
| current_liabilities | mapped | LiabilitiesCurrent | BS R5.htm | Total current liabilities | 67017000000 | 67017000000 | 61604000000 | 61604000000 | Y | FILING-CHECKED |  |
| total_liabilities | not_presented |  | BS R5.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| total_debt | component sum | LongTermDebtAndCapitalLeaseObligationsCurrent+LongTermDebtAndCapitalLeaseObligations | BS R5.htm | Current portion of long-term debt + Long-term debt | 6526000000 | 6526000000 | 5654000000 | 5654000000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R5.htm | Total McKesson Corporation stockholders’ deficit | -2172000000 | -2172000000 | -2074000000 | -2074000000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 120204051 | 120204051 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R9.htm | Net cash provided by operating activities | 6155000000 | 6155000000 | 6085000000 | 6085000000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R9.htm | Net cash used in investing activities | -3432000000 | -3432000000 | -733000000 | -733000000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R9.htm | Net cash used in financing activities | -4631000000 | -4631000000 | -3965000000 | -3965000000 | Y | FILING-CHECKED |  |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R9.htm | Payments for property, plant, and equipment | -436000000 | 436000000 | -537000000 | 537000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | capitalized software printed separately: founder perimeter may add it (IBM ruling) |
| depreciation_and_amortization | mapped | Depreciation | CF R9.htm | Depreciation | 256000000 | 256000000 | 242000000 | 242000000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R9.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | not_presented |  | CF R9.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | CF R9.htm | Dividends paid | -381000000 | 381000000 | -345000000 | 345000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R9.htm | Share repurchases | -4750000000 | 4750000000 | -3146000000 | 3146000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ar_change | mapped | IncreaseDecreaseInReceivables | CF R9.htm | Receivables | -1999000000 | 1999000000 | -3935000000 | 3935000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R9.htm | Inventories | -1082000000 | 1082000000 | -2270000000 | 2270000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R9.htm | Drafts and accounts payable | 4317000000 | 4317000000 | 8301000000 | 8301000000 | Y | FILING-CHECKED |  |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R9.htm | Interest, net | 212000000 | 212000000 | 273000000 | 273000000 | Y | FILING-CHECKED |  |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | CF R9.htm | Income taxes, net of refunds | 1211000000 | 1211000000 | 1124000000 | 1124000000 | Y | FILING-CHECKED |  |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2025, 2026]; ERA-CHECK others: {'InterestExpense': [2022, 2023, 2024]}
- income_before_tax: chosen tag FY[2026]; ERA-CHECK others: {'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest': [2022, 2023, 2024, 2025]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- none

## Mismatches (printed vs API)
- none beyond sign differences
