# HWM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000004281-26-000012 (CIK 0000004281, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001193125-16-470162 (CIK 0000004281, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000004281-18-000042 (CIK 0000004281, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000004281-19-000031 (CIK 0000004281, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000004281.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Sales (C) | 8252000000 | 8252000000 | 7430000000 | 7430000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R3.htm | Cost of goods sold (exclusive of expenses below) | 5432000000 | 5432000000 | 5119000000 | 5119000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1071 tags across all 124 R pages, face and notes) of 0000004281-26-000012; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R59.htm | Segment and Geographic Area Information - Schedule of Segment Operating Profit to Consolidated Net Income (loss) Income  |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Segment and Geographic Area Information - Schedule of Segment Operating Profit t' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general administrative, and other expenses | 370000000 | 370000000 | 347000000 | 347000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development expenses | 37000000 | 37000000 | 33000000 | 33000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 2046000000 | 2046000000 | 1633000000 | 1633000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest expense, net (E) | 151000000 | -151000000 | 182000000 | -182000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 1840000000 | 1840000000 | 1383000000 | 1383000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes (H) | 332000000 | 332000000 | 228000000 | 228000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 1508000000 | 1508000000 | 1155000000 | 1155000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in usd per share) | 3.73 | 3.73 | 2.83 | 2.83 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in usd per share) | 3.71 | 3.71 | 2.81 | 2.81 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 404000000 | 404000000 | 408000000 | 408000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 406000000 | 406000000 | 410000000 | 410000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 742000000 | 742000000 | 564000000 | 564000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables from customers, less allowances of $— in both 2025 and 2024 (L) | 779000000 | 779000000 | 689000000 | 689000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories (M) | 1849000000 | 1849000000 | 1840000000 | 1840000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 3779000000 | 3779000000 | 3362000000 | 3362000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Properties, plants, and equipment, net (N) | 2593000000 | 2593000000 | 2386000000 | 2386000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill (O) | 4022000000 | 4022000000 | 4010000000 | 4010000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 11179000000 | 11179000000 | 10519000000 | 10519000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable, trade | 845000000 | 845000000 | 948000000 | 948000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1771000000 | 1771000000 | 1549000000 | 1549000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 5826000000 | 5826000000 | 5965000000 | 5965000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total equity | 5353000000 | 5353000000 | 4554000000 | 4554000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash provided from operations | 1884000000 | 1884000000 | 1298000000 | 1298000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Cash used for investing activities | -438000000 | -438000000 | -316000000 | -316000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Cash used for financing activities | -1269000000 | -1269000000 | -1026000000 | -1026000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures (C and S) | -453000000 | 453000000 | -321000000 | 321000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 283000000 | 283000000 | 277000000 | 277000000 | Y | FILING-CHECKED | accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| sbc | mapped | hwm:IncreaseDecreaseInSharebasedCompensation | R7.htm | Stock-based compensation | 73000000 |  | 63000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfOrdinaryDividends | R7.htm | Dividends paid to shareholders (I) | -181000000 | 181000000 | -109000000 | 109000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock (I) | -700000000 | 700000000 | -500000000 | 500000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000004281-26-000012 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R118.htm | Cash Flow Information - Schedule of Cash Paid for Interest and Income Taxes (Details) |  | 157000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R118.htm 'Cash Flow Information - Schedule of Cash Paid for Interest and Income Taxes (Det' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R82.htm | Income Taxes - Cash Paid For Income Taxes (Details) |  | 312000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R82.htm 'Income Taxes - Cash Paid For Income Taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Long-term debt due within one year (Q and R) + Long-term debt, less amount due within one year (Q and R) | 3050000000 | 3050000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R88.htm | Preferred and Common Stock - Narrative (Details) |  | 401620565 |  |  |  | FILING-CHECKED | not on the face statement; shown in R88.htm 'Preferred and Common Stock - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-470162 R2.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Cost of goods sold (exclusive of expenses below)' on us-gaap:CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization = 18069000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 22286000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Selling, general administrative, and other expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 979000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Research and development expenses' on us-gaap:ResearchAndDevelopmentExpense = 238000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-470162 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Interest expense (V)' on us-gaap:InterestExpense = 498000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 248000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Provision for income taxes (T)' on us-gaap:IncomeTaxExpenseBenefit = 445000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Consolidated net (loss) income attributable to Alcoa' on us-gaap:NetIncomeLoss = -322000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Basic | $ / shares' on us-gaap:EarningsPerShareBasic = -0.31 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-470162 R2.htm prints 'Diluted | $ / shares' on us-gaap:EarningsPerShareDiluted = -0.31 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-470162 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-470162 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Cash and cash equivalents (X)' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1919000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Receivables from customers, less allowances of $13 in 2015 and $14 in 2014 (U)' on us-gaap:AccountsReceivableNetCurrent = 1340000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Inventories (G)' on us-gaap:InventoryNet = 3442000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 7953000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Properties, plants, and equipment, net (H)' on us-gaap:PropertyPlantAndEquipmentNet = 14815000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Goodwill (A & E)' on us-gaap:Goodwill = 5401000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Total Assets' on us-gaap:Assets = 36528000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Accounts payable, trade' on us-gaap:AccountsPayableCurrent = 2889000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 5211000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 22397000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-470162 R4.htm prints 'Total Alcoa shareholders' equity' on us-gaap:StockholdersEquity = 12046000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Cash provided from operations' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1582000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1060000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Cash (used for) provided from financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -441000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1180000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Depreciation, depletion, and amortization' on us-gaap:DepreciationDepletionAndAmortization = 1280000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Stock-based compensation (R)' on us-gaap:ShareBasedCompensation = 92000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-470162 R6.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -223000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-470162 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-470162 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-470162 R6.htm read; no row matched (auto)
- interest_expense: era 10-K 0000004281-18-000042 R2.htm prints 'Interest expense (S)' on us-gaap:InterestExpense = 496000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000004281-18-000042 R2.htm prints 'Interest expense (S)' on us-gaap:InterestExpense = 496000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000004281-18-000042 R6.htm prints 'Cash provided from (used for) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 540000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000004281-18-000042 R6.htm prints 'Cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -963000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000004281-19-000031 R2.htm prints 'Interest expense (E)' on us-gaap:InterestExpense = 378000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- sbc: API missing (hwm:IncreaseDecreaseInSharebasedCompensation)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:DepreciationAndAmortization+us-gaap:RestructuringCostsAndAssetImpairmentCharges (R3.htm): 2026-11-12 R3.htm: corrected: the NOTE R59 segment row had no value; lines after cost of goods sold: 370 + 37 + 283 + 84 = 774 = 8,252 - 5,432 - 2,046
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R118.htm): 2026-11-12 R118.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R82.htm): 2026-11-12 R82.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 debt lines; no finance-lease facts in the filing
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R88.htm): 2026-11-12 R88.htm: agree: R88 401,620,565 at 2025-12-31 (companyfacts end date)
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Sales (C)' is the revenue line, printed 8252000000 = filing XBRL 8252000000; agrees
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Diluted (in shares)' is the weighted_diluted_shares line, printed 406000000 = filing XBRL 406000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current assets' is the current_assets line, printed 3779000000 = filing XBRL 3779000000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current liabilities' is the current_liabilities line, printed 1771000000 = filing XBRL 1771000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total equity' is the stockholders_equity line, printed 5353000000 = filing XBRL 5353000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Capital expenditures (C and S)' is the capex line, printed -453000000 = filing XBRL 453000000; agrees
- interest_expense: combined check: hand 2026-11-12 R3.htm: 'Interest expense, net' on InterestIncomeExpenseNonoperatingNet is a net line: combined
