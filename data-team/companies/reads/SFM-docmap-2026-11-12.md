# SFM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001575515-26-000008 (CIK 0001575515, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001564590-16-013299 (CIK 0001575515, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001564590-18-002782 (CIK 0001575515, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001564590-19-003562 (CIK 0001575515, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001575515.json (one call); submissions CIK0001575515.json (SIC 5411).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 8806159000 | 8806159000 | 7719290000 | 7719290000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 5389770000 | 5389770000 | 4777799000 | 4777799000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 3416389000 | 3416389000 | 2941491000 | 2941491000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:DepreciationAndAmortization+sfm:IncomeExpenseStoreClosureAndOtherCostsNet | R5.htm | Selling, general and administrative expenses + Depreciation and amortization (exclusive of depreciation included in cost | 2730231000 |  | 2436994000 |  | API missing | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 2574687000 | 2574687000 | 2291350000 | 2291350000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No R&D expense anywhere; the grocery retailer's income statement and segment expense page carry none. / pages opened: R5, R12, R39, R63, R82, R98, R108 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 686158000 | 686158000 | 504497000 | 504497000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest (income) expense, net | -2626000 | 2626000 | -2201000 | 2201000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 688784000 | 688784000 | 506698000 | 506698000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | 165114000 | 165114000 | 126097000 | 126097000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 523670000 | 523670000 | 380601000 | 380601000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 5.36 | 5.36 | 3.79 | 3.79 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 5.31 | 5.31 | 3.75 | 3.75 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 97687000 | 97687000 | 100363000 | 100363000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 98704000 | 98704000 | 101379000 | 101379000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R5.htm period ..2025-12-28 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 257282000 | 257282000 | 265159000 | 265159000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Accounts receivable, net | 65221000 | 65221000 | 30901000 | 30901000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 427095000 | 427095000 | 343329000 | 343329000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 809904000 | 809904000 | 675520000 | 675520000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net of accumulated depreciation | 1085356000 | 1085356000 | 895189000 | 895189000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 381750000 | 381750000 | 381750000 | 381750000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4158649000 | 4158649000 | 3640699000 | 3640699000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 291033000 | 291033000 | 213414000 | 213414000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 870803000 | 870803000 | 679968000 | 679968000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2755575000 | 2755575000 | 2318806000 | 2318806000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 1403074000 | 1403074000 | 1321893000 | 1321893000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R3.htm period ..2025-12-28 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash flows from operating activities | 715998000 | 715998000 | 645214000 | 645214000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Cash flows used in investing activities | -248267000 | -248267000 | -230375000 | -230375000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Cash flows used in financing activities | -474050000 | -474050000 | -351496000 | -351496000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -248267000 | 248267000 | -230375000 | 230375000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization expense | 157722000 | 157722000 | 140164000 | 140164000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 31103000 | 31103000 | 28417000 | 28417000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No dividends in the equity statement or cash flow statement; only repurchases. / pages opened: R6, R7 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -471926000 | 471926000 | -228472000 | 228472000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 1809000 | 1809000 | 5008000 | 5008000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes | 120076000 | 120076000 | 102226000 | 102226000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001575515-26-000008 R7.htm period ..2025-12-28 |
| total_debt | combined | sfm:LongTermDebtAndFinanceObligationsNoncurrent | R3.htm | Long-term debt and other finance obligations | 81585000 |  |  |  |  | FILING-CHECKED | check: hand / Revolver debt is $0 (R75); the face shows debt only inside 'long-term debt and other finance obligations' ($81,585K = finance obligations $69,420K + finance leases $12,165K) plus a current finance-lease/obligation line o / pages opened: R3, R4, R7, R67, R69, R75 |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 95926024 | 95926024 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-28; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 3593031000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Cost of sales, buying and occupancy' on us-gaap:CostOfMerchandiseSalesBuyingAndOccupancyCosts = 2541403000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 1051628000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Direct store expenses + Selling, general and administrative expenses + Store pre' on sfm:DirectStoreExpenses+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:PreOpeningCosts+sfm:IncomeExpenseStoreClo = 822874000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 106412000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 228754000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Interest expense' on us-gaap:InterestExpenseDebt = -17723000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 205993000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = -77002000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 128991000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 0.84 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 0.83 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 153099000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013299 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 155877000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 136069000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 20424000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 165434000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 345215000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Property and equipment, net of accumulated depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 494067000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 368078000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Total assets' on us-gaap:Assets = 1426364000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 134480000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 230422000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 603372000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013299 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 822992000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 239898000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -128312000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -106030000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -125313000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Depreciation and amortization expense' on us-gaap:DepreciationAndAmortization = 69169000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Equity-based compensation' on us-gaap:ShareBasedCompensation = 8018000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -25735000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaidNet = 17455000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013299 R6.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 40656000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564590-18-002782 R4.htm prints 'Interest expense' on us-gaap:InterestExpenseDebt = -21177000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-002782 R8.htm prints 'Cash flows from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 309567000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-002782 R8.htm prints 'Cash flows used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -198594000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-002782 R8.htm prints 'Cash flows used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -103959000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001564590-18-002782 R8.htm prints 'Depreciation and amortization expense' on us-gaap:DepreciationAndAmortization = 96744000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564590-19-003562 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -27435000 (FILING-CHECKED)
- accounts_payable: era 10-K 0001564590-19-003562 R2.htm prints 'Accounts payable and other accrued liabilities' on us-gaap:AccountsPayableAndOtherAccruedLiabilitiesCurrent = 253969000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001564590-19-003562 R8.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 15527000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:DepreciationAndAmortization+sfm:IncomeExpenseStoreClosureAndOtherCostsNet)
