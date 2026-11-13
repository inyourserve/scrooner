# INGR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008603 (CIK 0001046257, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0001104659-16-098429 (CIK 0001046257, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001558370-18-000857 (CIK 0001046257, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001558370-21-001632 (CIK 0001046257, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0001046257.json (one call); submissions CIK0001046257.json (SIC 2040).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 7219000000 | 7219000000 | 7430000000 | 7430000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 5391000000 | 5391000000 | 5639000000 | 5639000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1828000000 | 1828000000 | 1791000000 | 1791000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | ingr:OperatingExpensesExcludingRestructuringCharges+us-gaap:OtherOperatingIncomeExpenseNet+us-gaap:RestructuringSettlementAndImpairmentProvisions | R3.htm | Operating expenses + Other operating (income), net + Restructuring/impairment charges | 812000000 |  | 908000000 |  | API missing | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI; company extension tag, matched by printed label / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| sga_expense | combined | ingr:OperatingExpensesExcludingRestructuringCharges | R3.htm | Operating expenses | 815000000 |  |  |  |  | FILING-CHECKED | check: hand / Face shows a single custom 'Operating expenses' line ($815M) below gross profit with no separate SG&A; SG&A is only inside that broader line, and no listed note breaks it out. / pages opened: R19, R35, R44, R45, R53, R63, R3 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R96.htm | Research and development expense | 71000000 | 71000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R96.htm 'Supplementary Information - Narrative (Details)' (MetaLinks.json presentation) |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 1016000000 | 1016000000 | 883000000 | 883000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| interest_expense | combined | ingr:FinancingCostsNet | R3.htm | Financing costs | 37000000 |  |  |  |  | FILING-CHECKED | check: hand / Interest is printed only inside the net custom 'Financing costs' line (net of interest income); no gross interest expense on the debt pages. / pages opened: R59, R16, R32, R51, R52, R3 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 974000000 | 974000000 | 931000000 | 931000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 238000000 | 238000000 | 277000000 | 277000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Ingredion | 729000000 | 729000000 | 647000000 | 647000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 11.36 | 11.36 | 9.88 | 9.88 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 11.18 | 11.18 | 9.71 | 9.71 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 64200000 | 64200000 | 65500000 | 65500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 65200000 | 65200000 | 6.66e+07 | 66600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 1030000000 | 1030000000 | 997000000 | 997000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net | 1185000000 | 1185000000 | 1093000000 | 1093000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 1227000000 | 1227000000 | 1187000000 | 1187000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 3505000000 | 3505000000 | 3355000000 | 3355000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 2526000000 | 2526000000 | 2264000000 | 2264000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R43.htm | Balance at the end of the period | 922000000 | 922000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R43.htm 'Intangible Assets - Goodwill (Details)' (MetaLinks.json presentation) |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 7897000000 | 7897000000 | 7444000000 | 7444000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 693000000 | 693000000 | 604000000 | 604000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1316000000 | 1316000000 | 1281000000 | 1281000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 3531000000 | 3531000000 | 3554000000 | 3554000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Ingredion stockholders’ equity | 4274000000 | 4274000000 | 3804000000 | 3804000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Cash provided by operating activities | 944000000 | 944000000 | 1436000000 | 1436000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Cash used for investing activities | -444000000 | -444000000 | -47000000 | -47000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Cash used for financing activities | -491000000 | -491000000 | -765000000 | -765000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures and mechanical stores purchases, net | -433000000 | 433000000 | -295000000 | 295000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 222000000 | 222000000 | 214000000 | 214000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| sbc | mapped | ingr:ProceedsFromCommonStockUnderIncentiveAndShareBasedCompensationPlansNetOfSettlements | R9.htm | Common stock activity for share-based compensation, net | -12000000 |  | 46000000 |  | API missing | FILING-CHECKED | check: machine-full-filing / company extension tag, matched by printed label / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid, including to non-controlling interests | -211000000 | 211000000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R9.htm 'Consolidated Statements of Cash Flows' (MetaLinks.json presentation) |
| share_buybacks | mapped | us-gaap:ProceedsFromRepurchaseOfEquity | R9.htm | Repurchases of common stock, net | -224000000 | -224000000 | -216000000 | -216000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001628280-26-008603 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R96.htm | Interest paid | 37000000 | 37000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R96.htm 'Supplementary Information - Narrative (Details)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R57.htm | Total income taxes paid, net of refunds | 389000000 | 389000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R57.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Short-term borrowings + Long-term debt | 1790000000 | 1790000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R77.htm | Common stock, outstanding, ending balance (in shares) | 62973000 |  |  |  |  | FILING-CHECKED | check: hand / Equity share-activity note gives undimensioned common shares outstanding at 2025-12-31 of 62,973 thousand. / pages opened: R1, R3, R7, R75, R77, R84 |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 5621000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 4379000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1242000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Operating expenses' on us-gaap:OperatingExpenses = 582000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001104659-16-098429 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 660000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 599000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 187000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Net income attributable to Ingredion' on us-gaap:NetIncomeLoss = 402000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 5.62 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 5.51 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 71600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001104659-16-098429 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 73000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 434000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Accounts receivable - net' on us-gaap:ReceivablesNetCurrent = 775000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 715000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1950000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1989000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 601000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Total assets' on us-gaap:Assets = 5074000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 423000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 742000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001104659-16-098429 R5.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001104659-16-098429 R5.htm prints 'Total Ingredion stockholders' equity' on us-gaap:StockholdersEquity = 2144000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 686000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -649000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -116000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -280000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 194000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Excess tax benefit on share-based compensation' on us-gaap:ExcessTaxBenefitFromShareBasedCompensationFinancingActivities = 8000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001104659-16-098429 R9.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001104659-16-098429 R9.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -41000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001104659-16-098429 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001104659-16-098429 R9.htm read; no row matched (auto)
- cost_of_revenue: era 10-K 0001558370-18-000857 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 4359000000 (FILING-CHECKED)
- share_buybacks: era 10-K 0001558370-18-000857 R9.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -123000000 (FILING-CHECKED)
- accounts_receivable: era 10-K 0001558370-21-001632 R5.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 1011000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (ingr:OperatingExpensesExcludingRestructuringCharges+us-gaap:OtherOperatingIncomeExpenseNet+us-gaap:RestructuringSettlementAndImpairmentProvisions)
- sbc: API missing (ingr:ProceedsFromCommonStockUnderIncentiveAndShareBasedCompensationPlansNetOfSettlements)
