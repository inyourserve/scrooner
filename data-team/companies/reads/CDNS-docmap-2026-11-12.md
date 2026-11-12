# CDNS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000813672-26-000016 (CIK 0000813672, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0000813672-16-000040 (CIK 0000813672, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000813672-18-000008 (CIK 0000813672, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000813672-19-000008 (CIK 0000813672, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0000813672.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 5296759000 | 5296759000 | 4641264000 | 4641264000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 518673000 |  | 436600000 |  | API missing | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1032 tags across all 116 R pages, face and notes) of 0000813672-26-000016; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 3804717000 | 3804717000 | 3290501000 | 3290501000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 313387000 | 313387000 | 273961000 | 273961000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost | R5.htm | Research and development | 1768772000 | 1768772000 | 1549093000 | 1549093000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 1492042000 | 1492042000 | 1350763000 | 1350763000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest expense | -116541000 | 116541000 | -75999000 | 75999000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 1522043000 | 1522043000 | 1395819000 | 1395819000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 413155000 | 413155000 | 340335000 | 340335000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1108888000 | 1108888000 | 1055484000 | 1055484000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income per share - basic (in usd per share) | 4.09 | 4.09 | 3.89 | 3.89 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income per share - diluted (in usd per share) | 4.06 | 4.06 | 3.85 | 3.85 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average common shares outstanding - basic (shares) | 271333000 | 271333000 | 271212000 | 271212000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average common shares outstanding - diluted (shares) | 273312000 | 273312000 | 273833000 | 273833000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 3001317000 | 3001317000 | 2644030000 | 2644030000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Receivables, net | 944939000 | 944939000 | 680460000 | 680460000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 303545000 | 303545000 | 257711000 | 257711000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4669673000 | 4669673000 | 4016079000 | 4016079000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 517004000 | 517004000 | 458200000 | 458200000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2749143000 | 2749143000 | 2378671000 | 2378671000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 10153148000 | 10153148000 | 8974482000 | 8974482000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued liabilities | 856856000 | 856856000 | 632692000 | 632692000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1635291000 | 1635291000 | 1370105000 | 1370105000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1032 tags across all 116 R pages, face and notes) of 0000813672-26-000016; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 5474181000 | 5474181000 | 4673578000 | 4673578000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1728781000 | 1728781000 | 1260551000 | 1260551000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -460523000 | -460523000 | -837118000 | -837118000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used for) financing activities | -948975000 | -948975000 | 1239241000 | 1239241000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, plant and equipment | -141871000 | 141871000 | -142542000 | 142542000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 227828000 | 227828000 | 196935000 | 196935000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 455175000 | 455175000 | 391219000 | 391219000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1032 tags across all 116 R pages, face and notes) of 0000813672-26-000016; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Payments for repurchases of common stock | -925034000 | 925034000 | -550026000 | 550026000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 111951000 | 111951000 | 43219000 | 43219000 | Y | FILING-CHECKED | accn 0000813672-26-000016 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R84.htm | INCOME TAXES - Cash Taxes Paid (Details) |  | 247367000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'INCOME TAXES - Cash Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | mapped | us-gaap:LongTermDebt | R67.htm | DEBT - Senior Notes (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R67.htm 'DEBT - Senior Notes (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock shares outstanding (in shares) | 271799000 | 271799000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 1702091000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000813672-16-000040 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 1416661000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000813672-16-000040 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 109982000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost = 637567000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 285430000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -28311000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Income before provision (benefit) for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 267596000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Provision (benefit) for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 15179000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 252417000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Net income per share - basic (in usd per share)' on us-gaap:EarningsPerShareBasic = 0.88 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Net income per share - diluted (in usd per share)' on us-gaap:EarningsPerShareDiluted = 0.81 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Weighted average common shares outstanding - basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 288018000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000813672-16-000040 R4.htm prints 'Weighted average common shares outstanding - diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 312302000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 616686000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 164848000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 56762000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 964761000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 228599000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 551772000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Total assets' on us-gaap:Assets = 2351015000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 238022000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 536307000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000813672-16-000040 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1376115000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 378200000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -44504000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Net cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -626310000 (FILING-CHECKED)
- capex: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -44808000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 118165000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 92341000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Payments for repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -333189000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 19918000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000813672-16-000040 R7.htm prints 'Cash paid (received) for income taxes, net' on us-gaap:IncomeTaxesPaidNet = 29494000 (FILING-CHECKED)
- revenue: era 10-K 0000813672-18-000008 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 1943032000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000813672-19-000008 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 23018000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingAndMarketingExpense+us-gaap:ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost+us-gaap:GeneralAndAdministrativeExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:LossContingencyLossInPeriod+us-gaap:RestructuringCharges (R5.htm): 2026-11-12 R5.htm: corrected: 802,633 + 1,768,772 + 313,387 + 39,937 + 128,545 + 29,194 = 3,082,468 = 5,296,759 - (518,673 + 203,576) - 1,492,042 (thousands)
- total_liabilities: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R84.htm): 2026-11-12 R84.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: mapped us-gaap:UnsecuredLongTermDebt (R3.htm): 2026-11-12 R3.htm: corrected: the debt line is on the BS face (R3); the NOTE row had no value; no finance-lease facts in the filing
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Net income per share - basic (in usd per share)' is the basic_eps line, printed 4.09 = filing XBRL 4.09; agrees
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Weighted average common shares outstanding - dilut' is the weighted_diluted_shares line, printed 273312000 = filing XBRL 273312000; agrees
- inventory: mapped us-gaap:InventoryNet (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Inventories' is the inventory line, printed 303545000 = filing XBRL 303545000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Property, plant and equipment, net' is the ppe_net line, printed 517004000 = filing XBRL 517004000; agrees
- accounts_payable: combined us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: 'Accounts payable and accrued liabilities' bundles accrued liabilities: combined
- stockholders_equity: mapped us-gaap:StockholdersEquity (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total stockholders’ equity' is the stockholders_equity line, printed 5474181000 = filing XBRL 5474181000; agrees
- cost_of_revenue: component sum check: hand 2026-11-12 R5.htm: corrected: R5 prints two cost-of-sales rows (product and maintenance 518,673; services 203,576); the tool took only the first: 722,249 (thousands)
