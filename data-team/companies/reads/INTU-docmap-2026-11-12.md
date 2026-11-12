# INTU document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000896878-26-000037 (CIK 0000896878, filed 2026-09-09): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000896878-15-000116 (CIK 0000896878, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000896878-17-000130 (CIK 0000896878, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000896878-25-000035 (CIK 0000896878, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0000896878.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total net revenue | 21448000000 | 21448000000 | 18831000000 | 18831000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of revenue | 4016000000 |  | 3624000000 |  | API missing | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (953 tags across all 96 R pages, face and notes) of 0000896878-26-000037; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total costs and expenses | 15564000000 | 15564000000 | 13908000000 | 13908000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 1623000000 | 1623000000 | 1601000000 | 1601000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 3376000000 | 3376000000 | 2928000000 | 2928000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 5884000000 | 5884000000 | 4923000000 | 4923000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R3.htm | Interest expense | -256000000 | 256000000 | -247000000 | 247000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| income_before_tax | mapped | us-gaap:IncomeLossAttributableToParent | R3.htm | Income before income taxes | 6017000000 | 6017000000 | 4834000000 | 4834000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax provision | 1451000000 | 1451000000 | 965000000 | 965000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 4566000000 | 4566000000 | 3869000000 | 3869000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic net income per share (in dollars per share) | 16.53 | 16.53 | 13.82 | 13.82 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted net income per share (in dollars per share) | 16.46 | 16.46 | 13.67 | 13.67 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Shares used in basic per share calculations (in shares) | 276000000 | 276000000 | 280000000 | 280000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Shares used in diluted per share calculations (in shares) | 277000000 | 277000000 | 283000000 | 283000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R3.htm period ..2026-07-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 4705000000 | 4705000000 | 2884000000 | 2884000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowance for doubtful accounts of $5 and $5 | 625000000 | 625000000 | 530000000 | 530000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (953 tags across all 96 R pages, face and notes) of 0000896878-26-000037; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 15311000000 | 15311000000 | 14107000000 | 14107000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 1023000000 | 1023000000 | 961000000 | 961000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 13981000000 | 13981000000 | 13980000000 | 13980000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 36786000000 | 36786000000 | 36958000000 | 36958000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 873000000 | 873000000 | 792000000 | 792000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 10163000000 | 10163000000 | 10370000000 | 10370000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 17794000000 | 17794000000 | 17248000000 | 17248000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 18992000000 | 18992000000 | 19710000000 | 19710000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R5.htm period ..2026-07-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 8838000000 | 8838000000 | 6207000000 | 6207000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -1412000000 | -1412000000 | -2318000000 | -2318000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -7689000000 | -7689000000 | -1510000000 | -1510000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment | -175000000 | 175000000 | -84000000 | 84000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 187000000 | 187000000 | 172000000 | 172000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based compensation expense | 2056000000 | 2056000000 | 1968000000 | 1968000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends and dividend rights paid | -1347000000 | 1347000000 | -1189000000 | 1189000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Cash paid for purchases of treasury stock | -5412000000 | 5412000000 | -2772000000 | 2772000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 295000000 | 295000000 | 284000000 | 284000000 | Y | FILING-CHECKED | accn 0000896878-26-000037 R9.htm period ..2026-07-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R79.htm | Income Taxes - Cash Income Taxes Paid (Details) |  | 281000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R79.htm 'Income Taxes - Cash Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt + Long-term debt | 7669000000 | 7669000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares, outstanding (in shares) | 268384000 | 268384000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-07-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Total net revenue' on us-gaap:SalesRevenueNet = 4192000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Cost of product revenue' on us-gaap:CostOfGoodsSold = 139000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 3454000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000896878-15-000116 R2.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 483000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 798000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Operating income from continuing operations' on us-gaap:OperatingIncomeLoss = 738000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Interest expense' on us-gaap:InterestExpenseDebt = -27000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 712000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 299000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 365000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Basic net income per share' on us-gaap:EarningsPerShareBasic = 1.3 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Diluted net income per share' on us-gaap:EarningsPerShareDiluted = 1.28 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Shares used in basic per share calculations' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 281000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000896878-15-000116 R2.htm prints 'Shares used in diluted per share calculations' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 286000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 808000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $45 and $40' on us-gaap:AccountsReceivableNetCurrent = 91000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2560000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 682000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1266000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Total assets' on us-gaap:Assets = 4968000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 190000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1744000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 2636000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000896878-15-000116 R4.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 2332000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1504000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -182000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -1337000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -142000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000896878-15-000116 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 257000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Dividends and dividend rights paid' on us-gaap:PaymentsOfDividends = -283000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Cash paid for purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1245000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 32000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000896878-15-000116 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 222000000 (FILING-CHECKED)
- revenue: era 10-K 0000896878-17-000130 R2.htm prints 'Total net revenue' on us-gaap:SalesRevenueNet = 5177000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000896878-25-000035 R3.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4834000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0000896878-25-000035 R9.htm prints 'Income taxes paid, net' on us-gaap:IncomeTaxesPaid = 1408000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingAndMarketingExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:GeneralAndAdministrativeExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:RestructuringCharges (R3.htm): 2026-11-12 R3.htm: corrected: opex = 5,534 + 3,376 + 1,623 + 485 + 293 = 11,311 = 21,448 - 4,253 - 5,884
- inventory: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AdjustmentForAmortization (R9.htm): 2026-11-12 R9.htm: corrected: the tool took depreciation alone; CF R9 also prints amortization 659: 187 + 659
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R79.htm): 2026-11-12 R79.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating income' is the operating_income line, printed 5884000000 = filing XBRL 5884000000; agrees
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income tax provision' is the income_tax_expense line, printed 1451000000 = filing XBRL 1451000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic net income per share (in dollars per share)' is the basic_eps line, printed 16.53 = filing XBRL 16.53; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Accounts receivable, net of allowance for doubtful' is the accounts_receivable line, printed 625000000 = filing XBRL 625000000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash used in investing activities' is the cash_flow_investing line, printed -1412000000 = filing XBRL -1412000000; agrees
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BSP R6.htm 'Common stock, shares, outstanding (in shares)' is the shares_outstanding line, printed 268384000 = filing XBRL 268384000; agrees
- cost_of_revenue: component sum check: hand 2026-11-12 R3.htm: corrected: R3 prints three cost-of-revenue rows; the tool took only the service member: 4,016 + 63 + 174 = 4,253
