# INCY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000879169-26-000010 (CIK 0000879169, filed 2026-02-10): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001558370-16-003196 (CIK 0000879169, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001558370-19-000682 (CIK 0000879169, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001558370-18-000722 (CIK 0000879169, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000879169.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 5141242000 | 5141242000 | 4241217000 | 4241217000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of product revenues (including definite-lived intangible amortization) | 372130000 | 372130000 | 312068000 | 312068000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (980 tags across all 100 R pages, face and notes) of 0000879169-26-000010; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs, expenses and other | 3626383000 | 3626383000 | 4179851000 | 4179851000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1376206000 | 1376206000 | 1242157000 | 1242157000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 2050152000 | 2050152000 | 2606848000 | 2606848000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 1514859000 | 1514859000 | 61366000 | 61366000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -2428000 | 2428000 | -2280000 | 2280000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 1664451000 | 1664451000 | 316630000 | 316630000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 377801000 | 377801000 | 284015000 | 284015000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1286650000 | 1286650000 | 32615000 | 32615000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 6.59 | 6.59 | 0.16 | 0.16 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 6.41 | 6.41 | 0.15 | 0.15 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 195204000 | 195204000 | 207110000 | 207110000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 200700000 | 200700000 | 210530000 | 210530000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 3097817000 | 3097817000 | 1687829000 | 1687829000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R3.htm | Accounts receivable | 1024407000 | 1024407000 | 853154000 | 853154000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 101060000 | 101060000 | 58872000 | 58872000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 5023902000 | 5023902000 | 3239030000 | 3239030000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 730885000 | 730885000 | 763411000 | 763411000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 133000000 | 133000000 | 155593000 | 155593000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 6957973000 | 6957973000 | 5444322000 | 5444322000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 209938000 | 209938000 | 197465000 | 197465000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1515170000 | 1515170000 | 1641847000 | 1641847000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1790495000 | 1790495000 | 1996694000 | 1996694000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 5167478000 | 5167478000 | 3447628000 | 3447628000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1413498000 | 1413498000 | 335337000 | 335337000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -102610000 | -102610000 | 157517000 | 157517000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 101039000 | 101039000 | -2021547000 | -2021547000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireOtherProductiveAssets | R9.htm | Capital expenditures | -58867000 | 58867000 | -86263000 | 86263000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 93286000 | 93286000 | 89248000 | 89248000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 249346000 | 249346000 | 266058000 | 266058000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (980 tags across all 100 R pages, face and notes) of 0000879169-26-000010; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of Common Stock | 0 | 0 | -2004790000 | 2004790000 | Y | FILING-CHECKED | accn 0000879169-26-000010 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (980 tags across all 100 R pages, face and notes) of 0000879169-26-000010; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R84.htm | Income Taxes - Schedule of Income Taxes Paid, Net of (Refunds) Received (Details) |  | 212178000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'Income Taxes - Schedule of Income Taxes Paid, Net of (Refunds) Received (Details' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | mapped | us-gaap:LongTermDebt | R95.htm | Commitments and contingencies - Commitments (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R95.htm 'Commitments and contingencies - Commitments (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 198460009 | 198460009 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Total revenues' on us-gaap:Revenues = 753751000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Cost of product revenues' on us-gaap:CostOfGoodsSold = 26972000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 703100000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 196614000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 479514000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Income (loss) from operations' on us-gaap:OperatingIncomeLoss = 50651000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -45603000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Income (loss) before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 7556000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Provision (benefit) for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1025000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Net income (loss)' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 6531000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 0.04 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 0.03 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 179601000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001558370-16-003196 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 187302000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 521439000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Accounts receivable' on us-gaap:AccountsReceivableNet = 114450000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 1783000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 842375000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 86006000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001558370-16-003196 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Total assets' on us-gaap:Assets = 1007440000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 30085000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 168007000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 836285000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001558370-16-003196 R2.htm prints 'Total stockholders' equity (deficit)' on us-gaap:StockholdersEquity = 171155000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 86536000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -105010000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 87616000 (FILING-CHECKED)
- capex: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -26003000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Depreciation and amortization of debt discounts' on us-gaap:DepreciationDepletionAndAmortization = 44883000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 69872000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Loss on repurchase of convertible senior notes' on us-gaap:GainLossOnRepurchaseOfDebtInstrument =  (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001558370-16-003196 R8.htm prints 'Incomes taxes paid' on us-gaap:IncomeTaxesPaid = 62000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-19-000682 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1881883000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001558370-18-000722 R4.htm prints 'Cost of product revenues (including definite-lived intangible amortization)' on us-gaap:CostOfGoodsSold = 79479000 (FILING-CHECKED)
- net_income: era 10-K 0001558370-18-000722 R4.htm prints 'Net income (loss)' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = -313142000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001558370-18-000722 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 6305000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
