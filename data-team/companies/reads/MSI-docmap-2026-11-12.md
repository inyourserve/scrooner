# MSI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000068505-26-000010 (CIK 0000068505, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000068505-16-000017 (CIK 0000068505, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000068505-18-000009 (CIK 0000068505, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000068505-24-000008 (CIK 0000068505, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000068505.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 11682000000 | 11682000000 | 10817000000 | 10817000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Costs of sales | 5647000000 | 5647000000 | 5305000000 | 5305000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross margin | 6035000000 | 6035000000 | 5512000000 | 5512000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:OtherOperatingIncomeExpenseNet | R3.htm | Selling, general and administrative expenses + Research and development expenditures + Other charges | 3047000000 | 2633000000 | 2824000000 | 2514000000 | N (printed 3047000000 vs API 2633000000) | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 1870000000 | 1870000000 | 1752000000 | 1752000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development expenditures | 970000000 | 970000000 | 917000000 | 917000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating earnings | 2988000000 | 2988000000 | 2688000000 | 2688000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense, net | -302000000 | 302000000 | -227000000 | 227000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Net earnings before income taxes | 2812000000 | 2812000000 | 1972000000 | 1972000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 652000000 | 652000000 | 390000000 | 390000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings attributable to Motorola Solutions, Inc. | 2154000000 | 2154000000 | 1577000000 | 1577000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (USD per share) | 12.93 | 12.93 | 9.45 | 9.45 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (USD per share) | 12.75 | 12.75 | 9.23 | 9.23 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 166600000 | 166600000 | 166800000 | 166800000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 169000000 | 169000000 | 170800000 | 170800000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1165000000 | 1165000000 | 2102000000 | 2102000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 2200000000 | 2200000000 | 1952000000 | 1952000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories, net | 983000000 | 983000000 | 766000000 | 766000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 6300000000 | 6300000000 | 6479000000 | 6479000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, plant and equipment, net | 1165000000 | 1165000000 | 1022000000 | 1022000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 6800000000 | 6800000000 | 3526000000 | 3526000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 19389000000 | 19389000000 | 14595000000 | 14595000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 1134000000 | 1134000000 | 1018000000 | 1018000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 6078000000 | 6078000000 | 5055000000 | 5055000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1175 tags across all 125 R pages, face and notes) of 0000068505-26-000010; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Motorola Solutions, Inc. stockholders’ equity | 2410000000 | 2410000000 | 1703000000 | 1703000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 2837000000 | 2837000000 | 2391000000 | 2391000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -5164000000 | -5164000000 | -507000000 | -507000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used for) financing activities | 1309000000 | 1309000000 | -1448000000 | -1448000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Capital expenditures | -265000000 | 265000000 | -257000000 | 257000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 425000000 | 425000000 | 336000000 | 336000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation expenses | 293000000 | 293000000 | 243000000 | 243000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Payment of dividends | -728000000 | 728000000 | -654000000 | 654000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | msi:PaymentsForRepurchaseOfCommonStockNetExciseTax | R8.htm | Purchases of common stock | -1154000000 |  | -247000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 285000000 | 285000000 | 253000000 | 253000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income and withholding taxes, net of refunds | 569000000 | 569000000 | 627000000 | 627000000 | Y | FILING-CHECKED | accn 0000068505-26-000010 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Short-term borrowings + Long-term debt | 9162000000 | 9162000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock outstanding (in shares) | 165700000 | 165700000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Net sales' on us-gaap:Revenues = 5695000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Costs of sales' on us-gaap:CostOfRevenue = 2976000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Gross margin' on us-gaap:GrossProfit = 2719000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Selling, general and administrative expenses + Research and development expendit' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:OtherCostAndExpenseOperatin = 1725000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1021000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Research and development expenditures' on us-gaap:ResearchAndDevelopmentExpense = 620000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Operating earnings (loss)' on us-gaap:OperatingIncomeLoss = 994000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -173000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Earnings (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 917000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Income tax expense (benefit)' on us-gaap:IncomeTaxExpenseBenefit = 274000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Net earnings attributable to Motorola Solutions, Inc.' on us-gaap:NetIncomeLoss = 610000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Basic (US$ per share):' on us-gaap:EarningsPerShareBasic = 3.06 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Diluted (US$ per share):' on us-gaap:EarningsPerShareDiluted = 3.02 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 199600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000068505-16-000017 R2.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 201800000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1980000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 1362000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Inventories, net' on us-gaap:InventoryNet = 296000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4582000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 487000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 420000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Total assets' on us-gaap:Assets = 8387000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 518000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2193000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000068505-16-000017 R4.htm prints 'Total Motorola Solutions, Inc. stockholders’ equity (deficit)' on us-gaap:StockholdersEquity = -106000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Net cash provided by (used for) operating activities from continuing operations' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1005000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Net cash provided by (used for) investing activities from continuing operations' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -528000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Net cash used for financing activities from continuing operations' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2382000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -175000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 150000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 78000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Payment of dividends' on us-gaap:PaymentsOfDividendsCommonStock = -277000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Purchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -3177000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Interest, net' on us-gaap:InterestPaidNet = 163000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000068505-16-000017 R7.htm prints 'Income and withholding taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 105000000 (FILING-CHECKED)
- revenue: era 10-K 0000068505-18-000009 R2.htm prints 'Net sales' on us-gaap:Revenues = 6380000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000068505-18-000009 R2.htm prints 'Costs of sales' on us-gaap:CostOfRevenue = 3356000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000068505-18-000009 R2.htm prints 'Earnings from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1076000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000068505-24-000008 R3.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -216000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: N (printed 3047000000 vs API 2633000000) (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:OtherOperatingIncomeExpenseNet)
- share_buybacks: API missing (msi:PaymentsForRepurchaseOfCommonStockNetExciseTax)

## Hand checks 2026-11-12 (Ritwik cloud)
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:OtherOperatingIncomeExpenseNet (R3.htm): 2026-11-12 R3.htm: agree: 1,870 + 970 + 207 = 3,047 = GP 6,035 - OI 2,988
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServicesSold (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Costs of sales' is the cost_of_revenue line, printed 5647000000 = filing XBRL 5647000000; agrees
- gross_profit: mapped us-gaap:GrossProfit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Gross margin' is the gross_profit line, printed 6035000000 = filing XBRL 6035000000; agrees
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Research and development expenditures' is the research_and_development line, printed 970000000 = filing XBRL 970000000; agrees
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net earnings before income taxes' is the income_before_tax line, printed 2812000000 = filing XBRL 2812000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic (USD per share)' is the basic_eps line, printed 12.93 = filing XBRL 12.93; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Share-based compensation expenses' is the sbc line, printed 293000000 = filing XBRL 293000000; agrees
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BSP R6.htm 'Common stock outstanding (in shares)' is the shares_outstanding line, printed 165700000 = filing XBRL 165700000; agrees
- interest_expense: combined ('Interest expense, net')
