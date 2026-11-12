# UTHR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001082554-26-000006 (CIK 0001082554, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001047469-16-010392 (CIK 0001082554, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001047469-18-000911 (CIK 0001082554, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001082554-24-000005 (CIK 0001082554, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001082554.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 3182700000 | 3182700000 | 2877400000 | 2877400000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 384400000 | 384400000 | 309700000 | 309700000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R88.htm | Segment Information - General (Details) |  | 2798300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R88.htm 'Segment Information - General (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 1690200000 | 1690200000 | 1500400000 | 1500400000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general, and administrative | 755800000 | 755800000 | 709700000 | 709700000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 550000000 | 550000000 | 481000000 | 481000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1492500000 | 1492500000 | 1377000000 | 1377000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -19500000 | 19500000 | -42900000 | 42900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1713900000 | 1713900000 | 1539000000 | 1539000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -379200000 | 379200000 | -343900000 | 343900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1334700000 | 1334700000 | 1195100000 | 1195100000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 30.13 | 30.13 | 26.44 | 26.44 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 27.86 | 27.86 | 24.64 | 24.64 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 44300000 | 44300000 | 45200000 | 45200000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 47900000 | 47900000 | 48500000 | 48500000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1557100000 | 1557100000 | 1697200000 | 1697200000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, no allowance for 2025 and 2024 | 350200000 | 350200000 | 279300000 | 279300000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, net | 183100000 | 183100000 | 157900000 | 157900000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 3702500000 | 3702500000 | 3873900000 | 3873900000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant, and equipment, net | 1729700000 | 1729700000 | 1222400000 | 1222400000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R3.htm | Goodwill and other intangible assets, net | 116500000 | 116500000 | 111900000 | 111900000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7880000000 | 7880000000 | 7364000000 | 7364000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 488000000 | 488000000 | 344500000 | 344500000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 560600000 | 560600000 | 738100000 | 738100000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 783800000 | 783800000 | 920000000 | 920000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 7096200000 | 7096200000 | 6444000000 | 6444000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1561200000 | 1561200000 | 1327100000 | 1327100000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -551300000 | -551300000 | 417200000 | 417200000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1150000000 | -1150000000 | -1254800000 | -1254800000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant, and equipment | -520500000 | 520500000 | -246500000 | 246500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 85600000 | 85600000 | 72500000 | 72500000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based compensation expense | 147700000 | 147700000 | 144000000 | 144000000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (966 tags across all 94 R pages, face and notes) of 0001082554-26-000006; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Payments to repurchase common stock | -1000000000 | 1000000000 | -1000000000 | 1000000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 13500000 | 13500000 | 40200000 | 40200000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash paid for income taxes | 313300000 | 313300000 | 400600000 | 400600000 | Y | FILING-CHECKED | accn 0001082554-26-000006 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LinesOfCreditCurrent | R3.htm | Line of credit | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 43643165 | 43643165 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1465761000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Cost of product sales' on us-gaap:CostOfGoodsSold = 69036000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-16-010392 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 766746000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 452612000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 245098000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 699015000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -4735000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1044437000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -392798000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Net income' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 651639000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 14.17 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 12.72 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 46000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-010392 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 51221000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 831798000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Accounts receivable, net of allowance of none for 2015 and 2014' on us-gaap:AccountsReceivableNetCurrent = 192827000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 81334000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1275335000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 495774000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Goodwill and other intangible assets, net' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 28378000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Total assets' on us-gaap:Assets = 2184445000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 103433000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 440824000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 584798000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-010392 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1588552000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 382761000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 503579000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -446943000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Purchases of property, plant and equipment, net' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -49792000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 32921000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 280254000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Payments to repurchase common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -394484000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaidNet = 1015000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-16-010392 R7.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 293331000 (FILING-CHECKED)
- revenue: era 10-K 0001047469-18-000911 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1725300000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001047469-18-000911 R4.htm prints 'Cost of product sales' on us-gaap:CostOfGoodsSold = 105700000 (FILING-CHECKED)
- interest_expense: era 10-K 0001082554-24-000005 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -59300000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
