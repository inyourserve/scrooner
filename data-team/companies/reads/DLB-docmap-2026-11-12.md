# DLB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001308547-25-000007 (CIK 0001308547, filed 2025-11-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- 10-K 0001628280-15-008974 (CIK 0001308547, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001628280-19-014472 (CIK 0001308547, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001628280-20-016459 (CIK 0001308547, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0001308547.json (one call); submissions CIK0001308547.json (SIC 6794).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 1349130000 | 1349130000 | 1273721000 | 1273721000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenue | 160132000 | 160132000 | 140496000 | 140496000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross margin | 1188998000 | 1188998000 | 1133225000 | 1133225000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 924039000 | 924039000 | 874899000 | 874899000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R5.htm | General and administrative + Sales and marketing | 647240000 | 647240000 | 604852000 | 604852000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 261792000 | 261792000 | 263663000 | 263663000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 264959000 | 264959000 | 258326000 | 258326000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNet | R5.htm | Interest income/(expense), net | 15376000 |  |  |  |  | FILING-CHECKED | check: hand / Interest expense appears only inside the net 'Interest income/(expense), net' line ($15,376K net income for FY2025); R91 gives only the tax-related interest increase ($12.2M), not a gross interest charge. / pages opened: R5, R91, R97, R96 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest | 303485000 | 303485000 | 312479000 | 312479000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | -46993000 | 46993000 | -48163000 | 48163000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Dolby Laboratories, Inc. | 255018000 | 255018000 | 261825000 | 261825000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (usd per share) | 2.66 | 2.66 | 2.74 | 2.74 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (usd per share) | 2.62 | 2.62 | 2.69 | 2.69 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (shares) | 95868000 | 95868000 | 95544000 | 95544000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (shares) | 97479000 | 97479000 | 97325000 | 97325000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R5.htm period ..2025-09-26 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 701893000 | 701893000 | 482047000 | 482047000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for credit losses of $7,221 and $5,361 | 331096000 | 331096000 | 315465000 | 315465000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 30424000 | 30424000 | 33728000 | 33728000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1388261000 | 1388261000 | 1194417000 | 1194417000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 470608000 | 470608000 | 479109000 | 479109000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 529900000 | 529900000 | 533208000 | 533208000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3227760000 | 3227760000 | 3109928000 | 3109928000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 17840000 | 17840000 | 17380000 | 17380000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 437790000 | 437790000 | 417836000 | 417836000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 595814000 | 595814000 | 623035000 | 623035000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity – Dolby Laboratories, Inc. | 2622557000 | 2622557000 | 2477162000 | 2477162000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R3.htm period ..2025-09-26 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided by operating activities | 472198000 | 472198000 | 327252000 | 327252000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash provided by/(used in) investing activities | -10586000 | -10586000 | -286292000 | -286292000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash used in financing activities | -247238000 | -247238000 | -287814000 | -287814000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Purchases of property, plant and equipment | -36348000 | 36348000 | -30007000 | 30007000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R10.htm | Depreciation and amortization | 87827000 | 87827000 | 75559000 | 75559000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation | 128514000 | 128514000 | 119825000 | 119825000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Payment of cash dividend | -126599000 | 126599000 | -114579000 | 114579000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Repurchase of common stock | -124992000 | 124992000 | -160001000 | 160001000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| cash_paid_for_interest | not_presented |  | R10.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Cash flow statement and listed notes report no interest paid; the company has no debt. / pages opened: R10, R71, R72, R96, R97 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R10.htm | Cash paid for income taxes, net of refunds received | 73737000 | 73737000 | 63217000 | 63217000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001308547-25-000007 R10.htm period ..2025-09-26 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet has no borrowings, notes or debt lines (only operating lease liabilities); R65/R66 cover debt securities held as investments, which are assets. / pages opened: R3, R6, R7, R9, R10, R65, R66 |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common Stock, Shares, Outstanding | 95462661 |  |  |  |  | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-09-26; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Total revenue' on us-gaap:Revenues = 970638000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Total cost of revenue' on us-gaap:CostOfRevenue = 94816000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Gross margin' on us-gaap:GrossProfit = 875822000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 662594000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-15-008974 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 182176000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 201324000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 213228000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 245782000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -62542000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Net income attributable to Dolby Laboratories, Inc.' on us-gaap:NetIncomeLoss = 181390000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Basic (usd per share)' on us-gaap:EarningsPerShareBasic = 1.77 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Diluted (usd per share)' on us-gaap:EarningsPerShareDiluted = 1.75 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 102354000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001628280-15-008974 R4.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 103862000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 531926000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $1,615 and $514' on us-gaap:AccountsReceivableNetCurrent = 101563000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 13872000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 918330000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 403091000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 307708000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Total assets' on us-gaap:Assets = 2133293000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 20710000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 209681000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 317286000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-15-008974 R2.htm prints 'Total stockholders’ equity – Dolby Laboratories, Inc.' on us-gaap:StockholdersEquity = 1807068000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 309377000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Net cash provided by/(used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -203595000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -138519000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -157552000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 69133000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 67069000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Payment of cash dividend' on us-gaap:PaymentsOfDividends = -41018000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -107349000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-15-008974 R8.htm prints 'Cash paid for income taxes, net of refunds received' on us-gaap:IncomeTaxesPaid = 51881000 (FILING-CHECKED)
- revenue: era 10-K 0001628280-19-014472 R4.htm prints 'Total revenue' on us-gaap:Revenues = 1241620000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001628280-19-014472 R8.htm prints 'Payment of cash dividend' on us-gaap:PaymentsOfDividends = -77496000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001628280-20-016459 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 239715000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
