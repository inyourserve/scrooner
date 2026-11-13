# PEGA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001013857-26-000017 (CIK 0001013857, filed 2026-02-10): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001193125-16-478369 (CIK 0001013857, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001013857-19-000005 (CIK 0001013857, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001193125-18-058491 (CIK 0001013857, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001013857.json (one call); submissions CIK0001013857.json (SIC 7374).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 1745812000 | 1745812000 | 1497180000 | 1497180000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Total cost of revenue | 421382000 | 421382000 | 390665000 | 390665000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1324430000 | 1324430000 | 1106515000 | 1106515000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1061330000 | 1061330000 | 982633000 | 982633000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R5.htm | General and administrative + Selling and marketing | 727359000 | 727359000 | 647628000 | 647628000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 312681000 | 312681000 | 298074000 | 298074000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 263100000 | 263100000 | 123882000 | 123882000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -1285000 | 1285000 | -6835000 | 6835000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before (benefit from) provision for income taxes | 280627000 | 280627000 | 142636000 | 142636000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | (Benefit from) provision for income taxes | -112810000 | -112810000 | 43447000 | 43447000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 393437000 | 393437000 | 99189000 | 99189000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 2.3 | 2.3 | 0.58 | 0.58 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 2.13 | 2.13 | 0.55 | 0.55 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 170782000 | 170782000 | 170530000 | 170530000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 184790000 | 184790000 | 179268000 | 179268000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 212447000 | 212447000 | 337103000 | 337103000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 264713000 | 264713000 | 305468000 | 305468000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Software company; no inventory line on the balance sheet or inventory change in the cash flow. / pages opened: R3, R5, R9 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 978295000 | 978295000 | 1333704000 | 1333704000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R64.htm | Property and equipment, net | 45240000 | 45240000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R64.htm 'PROPERTY AND EQUIPMENT - Schedule of Property and Equipment (Details)' (MetaLinks.json presentation) |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 81506000 | 81506000 | 81113000 | 81113000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1631844000 | 1631844000 | 1768273000 | 1768273000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 12924000 | 12924000 | 6226000 | 6226000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 737778000 | 737778000 | 1086058000 | 1086058000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 844463000 | 844463000 | 1182793000 | 1182793000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 787381000 | 787381000 | 585480000 | 585480000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Cash provided by operating activities | 505227000 | 505227000 | 345926000 | 345926000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Cash provided by (used in) investing activities | 197246000 | 197246000 | -202576000 | -202576000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Cash (used in) financing activities | -834630000 | -834630000 | -30214000 | -30214000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Investment in property and equipment | -14504000 | 14504000 | -7712000 | 7712000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Amortization of intangible assets and depreciation | 13699000 | 13699000 | 17585000 | 17585000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 155239000 | 155239000 | 142718000 | 142718000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividend payments to stockholders | -15422000 | 15422000 | -10199000 | 10199000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Common stock repurchases under stock repurchase program | -499689000 | 499689000 | -68057000 | 68057000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | pega:InterestPaidOnConvertibleDebt | R9.htm | Interest paid on convertible notes | 1754000 |  | 3810000 |  | API missing | FILING-CHECKED | check: machine-full-filing / company extension tag, matched by printed label / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid, net | 21630000 | 21630000 | 82317000 | 82317000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001013857-26-000017 R9.htm period ..2025-12-31 |
| total_debt | component_in_note | us-gaap:SeniorNotes | R83.htm | DEBT - Credit Facility (Details) |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / only component tag(s) SeniorNotes in the filing (R83.htm 'DEBT - Credit Facility (Details)'); the data point itself is not reported |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 170347000 | 170347000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Total revenue' on us-gaap:Revenues = 682695000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Total cost of revenue' on us-gaap:CostOfRevenue = 213446000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 469249000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 404588000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-478369 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 36738000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 126374000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 64661000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-478369 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 60505000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 24183000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 36322000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 0.47 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 0.46 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 76507000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-478369 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 79043000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 93026000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Trade accounts receivable, net of allowance of $4,631 and $1,540' on us-gaap:AccountsReceivableNetCurrent = 211846000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 458865000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 31319000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 46776000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Total assets' on us-gaap:Assets = 627758000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 12675000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 267188000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 304899000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-478369 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 322859000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 62528000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -44452000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -35384000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Investment in property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -11020000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 23093000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 30054000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Dividend payments to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -9194000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Common stock repurchases under share repurchase programs' on us-gaap:PaymentsForRepurchaseOfCommonStock = -22825000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-478369 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-478369 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 30215000 (FILING-CHECKED)
- revenue: era 10-K 0001013857-19-000005 R4.htm prints 'Total revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 891581000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001013857-19-000005 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 114422000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001193125-18-058491 R4.htm prints 'Total cost of revenue' on us-gaap:CostOfRevenue = 279673000 (FILING-CHECKED)
- cfo: era 10-K 0001193125-18-058491 R8.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 158235000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-058491 R8.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -14759000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-058491 R8.htm prints 'Cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -54229000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cash_paid_for_interest: API missing (pega:InterestPaidOnConvertibleDebt)
