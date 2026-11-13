# KMI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001506307-26-000011 (CIK 0001506307, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001506307-16-000072 (CIK 0001506307, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001506307-18-000010 (CIK 0001506307, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001506307-21-000022 (CIK 0001506307, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0001506307.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenues | 16937000000 | 16937000000 | 15100000000 | 15100000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R90.htm | Related Party Transactions (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Related Party Transactions (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1234 tags across all 114 R pages, face and notes) of 0001506307-26-000011; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total Operating Costs, Expenses, and Other | 12213000000 | 12213000000 | 10716000000 | 10716000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 744000000 | 744000000 | 712000000 | 712000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1234 tags across all 114 R pages, face and notes) of 0001506307-26-000011; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 4724000000 | 4724000000 | 4384000000 | 4384000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest, net | -1801000000 | -1801000000 | -1844000000 | -1844000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income Before Income Taxes | 3992000000 | 3992000000 | 3407000000 | 3407000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Tax Expense | -832000000 | 832000000 | -687000000 | 687000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income Attributable to Kinder Morgan, Inc. | 3056000000 | 3056000000 | 2613000000 | 2613000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic Earnings Per Share | 1.37 | 1.37 | 1.17 | 1.17 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted Earnings Per Share | 1.37 | 1.37 | 1.17 | 1.17 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic Weighted Average Shares Outstanding | 2223000000 | 2223000000 | 2220000000 | 2220000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted Weighted Average Shares Outstanding | 2223000000 | 2223000000 | 2220000000 | 2220000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 63000000 | 63000000 | 88000000 | 88000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableGrossCurrent | R6.htm | Accounts receivable | 1714000000 | 1714000000 | 1506000000 | 1506000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 574000000 | 574000000 | 555000000 | 555000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 2754000000 | 2754000000 | 2521000000 | 2521000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant, and equipment, net | 39331000000 | 39331000000 | 38013000000 | 38013000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 20084000000 | 20084000000 | 20084000000 | 20084000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total Assets | 72748000000 | 72748000000 | 71407000000 | 71407000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 1408000000 | 1408000000 | 1395000000 | 1395000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 4322000000 | 4322000000 | 5101000000 | 5101000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total Liabilities | 40299000000 | 40299000000 | 39540000000 | 39540000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Kinder Morgan, Inc.’s stockholders’ equity | 31162000000 | 31162000000 | 30531000000 | 30531000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net Cash Provided by Operating Activities | 5917000000 | 5917000000 | 5635000000 | 5635000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net Cash Used in Investing Activities | -3179000000 | -3179000000 | -2629000000 | -2629000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net Cash Used in Financing Activities | -2843000000 | -2843000000 | -2887000000 | -2887000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -3026000000 | 3026000000 | -2629000000 | 2629000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation, depletion, and amortization | 2453000000 | 2453000000 | 2354000000 | 2354000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| sbc | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ShareBasedCompensation, AllocatedShareBasedCompensationExpense in MetaLinks.json (1234 tags across all 114 R pages, face and notes) of 0001506307-26-000011; no face row matched |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends (Note 10) | -2604000000 | 2604000000 | -2557000000 | 2557000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of shares (Note 10) | 0 | 0 | -7000000 | 7000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid during the period for interest (net of capitalized interest) | 1811000000 | 1811000000 | 1816000000 | 1816000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid during the period for income taxes, net | 47000000 | 47000000 | 33000000 | 33000000 | Y | FILING-CHECKED | accn 0001506307-26-000011 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current portion of debt + Total long-term debt | 32003000000 | 32003000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 2224777750 | 2224777750 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Total Revenues' on us-gaap:Revenues = 14403000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Costs of sales' on us-gaap:CostOfGoodsSold = 4115000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Total Operating Costs, Expenses and Other' on us-gaap:CostsAndExpenses = 11956000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001506307-16-000072 R2.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 690000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 2447000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001506307-16-000072 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Income from Continuing Operations Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 772000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Income Tax Expense' on us-gaap:IncomeTaxExpenseBenefit = -564000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Net Income Attributable to Kinder Morgan, Inc.' on us-gaap:NetIncomeLoss = 253000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Basic Earnings Per Common Share' on us-gaap:EarningsPerShareBasic = 0.1 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Diluted Earnings Per Common Share' on us-gaap:EarningsPerShareDiluted = 0.1 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Basic Weighted Average Common Shares Outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 2187000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001506307-16-000072 R2.htm prints 'Diluted Weighted Average Common Shares Outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 2193000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 229000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 1315000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 407000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2824000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 40547000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 23790000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Total Assets' on us-gaap:Assets = 84104000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1324000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 4065000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Total Liabilities' on us-gaap:Liabilities = 48701000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001506307-16-000072 R5.htm prints 'Total Kinder Morgan, Inc.’s stockholders’ equity' on us-gaap:StockholdersEquity = 35119000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 5303000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Net Cash Used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -5706000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Net Cash Provided by (Used in) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 327000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -3896000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Depreciation, depletion and amortization' on us-gaap:DepreciationDepletionAndAmortization = 2309000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Cash dividends (Note 11)' on us-gaap:PaymentsOfDividends = -4224000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Repurchases of shares and warrants' on kmi:Paymentsforrepurchasesofsharesandwarrants = -12000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Cash paid during the period for interest (net of capitalized interest)' on us-gaap:InterestPaidNet = 1985000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001506307-16-000072 R7.htm prints 'Cash (refund) paid during the period for income taxes, net' on us-gaap:IncomeTaxesPaidNet = -331000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001506307-18-000010 R2.htm prints 'Costs of sales' on us-gaap:CostOfGoodsSold = 4345000000 (FILING-CHECKED)
- basic_eps: era 10-K 0001506307-18-000010 R2.htm prints 'Basic Earnings Per Common Share' on us-gaap:EarningsPerShareBasic = 0.01 (FILING-CHECKED)
- diluted_eps: era 10-K 0001506307-18-000010 R2.htm prints 'Diluted Earnings Per Common Share' on us-gaap:EarningsPerShareDiluted = 0.01 (FILING-CHECKED)
- dividends_paid: era 10-K 0001506307-18-000010 R7.htm prints 'Cash dividends - common shares (Note 11)' on us-gaap:PaymentsOfDividends = -1120000000 (FILING-CHECKED)
- basic_eps: era 10-K 0001506307-21-000022 R2.htm prints 'Basic and Diluted Earnings Per Common Share' on us-gaap:EarningsPerShareBasicAndDiluted = 0.05 (FILING-CHECKED)
- diluted_eps: era 10-K 0001506307-21-000022 R2.htm prints 'Basic and Diluted Earnings Per Common Share' on us-gaap:EarningsPerShareBasicAndDiluted = 0.05 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization (R3.htm): 2026-11-12 R3.htm: corrected: the face prints 'Costs of sales' 5,529; the tool took a related-party note (R90)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:OperatingCostsAndExpenses+us-gaap:DepreciationDepletionAndAmortization+us-gaap:GeneralAndAdministrativeExpense+us-gaap:TaxesExcludingIncomeAndExciseTaxes+us-gaap:OtherOperatingIncomeExpenseNet (R3.htm): 2026-11-12 R3.htm: corrected: 3,057 + 2,453 + 744 + 445 - 15 = 6,684 = 16,937 - 5,529 - 4,724
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- sbc: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R6.htm): 2026-11-12 R6.htm: agree: R6 debt lines; no finance-lease facts in the filing
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating Income' is the operating_income line, printed 4724000000 = filing XBRL 4724000000; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net Income Attributable to Kinder Morgan, Inc.' is the net_income line, printed 3056000000 = filing XBRL 3056000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic Earnings Per Share' is the basic_eps line, printed 1.37 = filing XBRL 1.37; agrees
- total_assets: mapped us-gaap:Assets (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total Assets' is the total_assets line, printed 72748000000 = filing XBRL 72748000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Capital expenditures' is the capex line, printed -3026000000 = filing XBRL 3026000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Repurchases of shares (Note 10)' is the share_buybacks line, printed 0 = filing XBRL 0; agrees
