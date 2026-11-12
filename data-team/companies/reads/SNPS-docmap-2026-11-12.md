# SNPS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000883241-25-000028 (CIK 0000883241, filed 2025-12-22): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000883241-15-000014 (CIK 0000883241, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000883241-18-000012 (CIK 0000883241, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000883241-23-000019 (CIK 0000883241, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0000883241.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 7054178000 | 7054178000 | 6127436000 | 6127436000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenue | 1623549000 | 1623549000 | 1245289000 | 1245289000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross margin | 5430629000 | 5430629000 | 4882147000 | 4882147000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 4515702000 | 4515702000 | 3526436000 | 3526436000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 769648000 | 769648000 | 568496000 | 568496000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 2479338000 | 2479338000 | 2082360000 | 2082360000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 914927000 | 914927000 | 1355711000 | 1355711000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -446729000 | 446729000 | -36829000 | 36829000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1393142000 | 1393142000 | 1513858000 | 1513858000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 55991000 | 55991000 | 99718000 | 99718000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributed to Synopsys | 1332220000 | 1332220000 | 2263380000 | 2263380000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in USD per share) | 8.13 | 8.13 | 14.78 | 14.78 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in USD per share) | 8.04 | 8.04 | 14.51 | 14.51 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic ( in shares) | 163947000 | 163947000 | 153138000 | 153138000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 165656000 | 165656000 | 155944000 | 155944000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R5.htm period ..2025-10-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2888030000 | 2888030000 | 3896532000 | 3896532000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 1505427000 | 1505427000 | 934470000 | 934470000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 365190000 | 365190000 | 361849000 | 361849000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 6012102000 | 6012102000 | 6469666000 | 6469666000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 696693000 | 696693000 | 563006000 | 563006000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 26899215000 | 26899215000 | 3448850000 | 3448850000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 48224461000 | 48224461000 | 13073561000 | 13073561000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued liabilities | 1326211000 | 1326211000 | 1163592000 | 1163592000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 3722494000 | 3722494000 | 2650120000 | 2650120000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 19897446000 | 19897446000 | 4050355000 | 4050355000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Synopsys stockholders’ equity | 28327602000 | 28327602000 | 8990702000 | 8990702000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R3.htm period ..2025-10-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1518608000 | 1518608000 | 1407029000 | 1407029000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -15881269000 | -15881269000 | 1223013000 | 1223013000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 13355757000 | 13355757000 | -181297000 | -181297000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment, net | -169454000 | 169454000 | -139500000 | 139500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Amortization and depreciation | 660430000 | 660430000 | 295065000 | 295065000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 893294000 | 893294000 | 692316000 | 692316000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1133 tags across all 124 R pages, face and notes) of 0000883241-25-000028; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchases of treasury stock | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest payments during the year: | 353773000 | 353773000 | 814000 | 814000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid for income taxes during the year: | 512705000 | 512705000 | 680064000 | 680064000 | Y | FILING-CHECKED | accn 0000883241-25-000028 R9.htm period ..2025-10-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Short-term debt + Long-term debt | 13484515000 | 13484515000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 185994000 | 185994000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-10-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Total revenue' on us-gaap:Revenues = 2242211000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Total cost of revenue' on us-gaap:CostOfRevenue = 518920000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Gross margin' on us-gaap:GrossProfit = 1723291000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 1456825000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000883241-15-000014 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 165097000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 776229000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 266466000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000883241-15-000014 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 281610000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Provision (benefit) for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 55676000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 225934000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Basic (in USD per share)' on us-gaap:EarningsPerShareBasic = 1.46 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Diluted (in USD per share)' on us-gaap:EarningsPerShareDiluted = 1.43 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 154957000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000883241-15-000014 R4.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 158065000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 836188000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Accounts receivable, net of allowances of $2,561 and $2,026, respectively' on us-gaap:AccountsReceivableNetCurrent = 385694000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000883241-15-000014 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1563801000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 263077000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 2471241000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Total assets' on us-gaap:Assets = 5045739000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 385542000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1578353000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1911750000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000883241-15-000014 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 3133989000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 495160000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -559629000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -62070000 (FILING-CHECKED)
- capex: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -86965000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Amortization and depreciation' on us-gaap:DepreciationDepletionAndAmortization = 211821000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Stock compensation' on us-gaap:ShareBasedCompensation = 86400000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -260000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Interest payments during the year:' on us-gaap:InterestPaid = 2710000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000883241-15-000014 R8.htm prints 'Cash paid for income taxes during the year:' on us-gaap:IncomeTaxesPaid = 59731000 (FILING-CHECKED)
- revenue: era 10-K 0000883241-18-000012 R4.htm prints 'Total revenue' on us-gaap:Revenues = 3121058000 (FILING-CHECKED)
- cfo: era 10-K 0000883241-18-000012 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 424232000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000883241-18-000012 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -743525000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000883241-18-000012 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 5138000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000883241-18-000012 R8.htm prints 'Interest payments during the year:' on us-gaap:InterestPaid = 15307000 (FILING-CHECKED)
- interest_expense: era 10-K 0000883241-23-000019 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- dividends_paid: not_presented  (R9.htm): 2026-11-12 R9.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: agree: R3 debt lines; no finance-lease facts in the filing
- sga_expense: component sum us-gaap:SellingAndMarketingExpense+us-gaap:GeneralAndAdministrativeExpense (R5.htm): 2026-11-12 R5.htm: sample DISAGREES (key-error class): G&A alone while S&M is printed; 1,074,191 + 769,648
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts receivable, net' is the accounts_receivable line, printed 1505427000 = filing XBRL 1505427000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total Synopsys stockholders’ equity' is the stockholders_equity line, printed 28327602000 = filing XBRL 28327602000; agrees
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash provided by operating activities' is the cfo line, printed 1518608000 = filing XBRL 1518608000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash provided by (used in) investing activitie' is the cash_flow_investing line, printed -15881269000 = filing XBRL -15881269000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Stock-based compensation' is the sbc line, printed 893294000 = filing XBRL 893294000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Purchases of treasury stock' is the share_buybacks line, printed 0 = filing XBRL 0; agrees
