# MDLZ document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-005345 (CIK 0001103982, filed 2026-02-04): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001193125-16-469394 (CIK 0001103982, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001193125-18-037332 (CIK 0001103982, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001103982-20-000003 (CIK 0001103982, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0001103982.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Net revenues | 38537000000 | 38537000000 | 36441000000 | 36441000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | -27602000000 | 27602000000 | -22184000000 | 22184000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 10935000000 | 10935000000 | 14257000000 | 14257000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions+mdlz:GainLossOnAcquisitionAndDispositionOfBusiness+us-gaap:AmortizationOfIntangibleAssets | R3.htm | Selling, general and administrative expenses + Asset impairments and exit costs + Gain on divestitures and acquisition + | -7387000000 |  | -7912000000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | -7173000000 | 7173000000 | -7439000000 | 7439000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R48.htm | Summary of Significant Accounting Policies - Additional Information (Details) |  | 400000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R48.htm 'Summary of Significant Accounting Policies - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 3548000000 | 3548000000 | 6345000000 | 6345000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R74.htm | Debt and Borrowing Arrangements - Interest and Other Expense, Net (Details) |  | 599000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Debt and Borrowing Arrangements - Interest and Other Expense, Net (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Earnings before income taxes | 3014000000 | 3014000000 | 6261000000 | 6261000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax provision | -782000000 | 782000000 | -1469000000 | 1469000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings attributable to Mondelēz International | 2451000000 | 2451000000 | 4611000000 | 4611000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per share attributable to Mondelēz International (in dollars per share) | 1.89 | 1.89 | 3.44 | 3.44 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per share attributable to Mondelēz International (in dollars per share) | 1.89 | 1.89 | 3.42 | 3.42 | Y | FILING-CHECKED | accn 0001628280-26-005345 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R116.htm | Earnings per Share - Schedule of Basic and Diluted Earnings Per Share (Details) |  | 1294000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R116.htm 'Earnings per Share - Schedule of Basic and Diluted Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R116.htm | Earnings per Share - Schedule of Basic and Diluted Earnings Per Share (Details) |  | 1298000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R116.htm 'Earnings per Share - Schedule of Basic and Diluted Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations | R5.htm | Cash and cash equivalents | 2125000000 | 2125000000 |  | 1351000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade receivables, less allowance ($35 and $37, respectively) | 3903000000 | 3903000000 |  | 3874000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 4419000000 | 4419000000 |  | 3827000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 12951000000 | 12951000000 |  | 13242000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, plant and equipment, net | 10667000000 | 10667000000 |  | 9481000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 24336000000 | 24336000000 |  | 23017000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 71487000000 | 71487000000 |  | 68497000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 10139000000 | 10139000000 |  | 9433000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 21864000000 | 21864000000 |  | 19549000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | TOTAL LIABILITIES | 45596000000 | 45596000000 |  | 41539000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Mondelēz International Shareholders’ Equity | 25838000000 | 25838000000 |  | 26932000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 4514000000 | 4514000000 | 4910000000 | 4910000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in)/provided by investing activities | -1196000000 | -1196000000 | 526000000 | 526000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -2759000000 | -2759000000 | -5780000000 | -5780000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -1279000000 | 1279000000 | -1387000000 | 1387000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 1358000000 | 1358000000 | 1302000000 | 1302000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 114000000 | 114000000 | 147000000 | 147000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid | -2487000000 | 2487000000 | -2349000000 | 2349000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of Common Stock | -2385000000 | 2385000000 | -2334000000 | 2334000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 570000000 | 570000000 | 554000000 | 554000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Income taxes | 1074000000 | 1074000000 | 1474000000 | 1474000000 | Y | FILING-CHECKED | accn 0001628280-26-005345 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Short-term borrowings + Current portion of long-term debt + Long-term debt | 21205000000 | 21205000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R101.htm | Capital Stock - Common Stock (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R101.htm 'Capital Stock - Common Stock (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Net revenues' on us-gaap:Revenues = 29636000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 18124000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 11512000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Selling, general and administrative expenses + Asset impairment and exit costs +' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions+us-gaap:GainLossOn = 2615000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 7577000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001193125-16-469394 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 8897000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-469394 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Earnings from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 7884000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 593000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Net earnings attributable to Mondelez International' on us-gaap:NetIncomeLoss = 7267000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Net earnings attributable to Mondelez International' on us-gaap:EarningsPerShareBasic = 4.49 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-469394 R2.htm prints 'Net earnings attributable to Mondelez International' on us-gaap:EarningsPerShareDiluted = 4.44 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-469394 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-469394 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations = 1870000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Trade receivables (net of allowances of $54 at December 31, 2015 and $66 at Dece' on us-gaap:AccountsReceivableNetCurrent = 2634000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Inventories, net' on us-gaap:InventoryNet = 2609000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 8958000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 8362000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 20664000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-469394 R4.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 62843000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 4890000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 10922000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-469394 R4.htm prints 'TOTAL LIABILITIES' on us-gaap:Liabilities = 34743000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-469394 R4.htm prints 'Total Mondelez International Shareholders' Equity' on us-gaap:StockholdersEquity = 28012000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 3728000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Net cash provided by / (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 2649000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -5883000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1514000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 894000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 136000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -1008000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Repurchase of Common Stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -3622000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Interest' on us-gaap:InterestPaid = 747000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-469394 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 745000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001193125-18-037332 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 15831000000 (FILING-CHECKED)
- ppe_net: era 10-K 0001103982-20-000003 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet =  (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions+mdlz:GainLossOnAcquisitionAndDispositionOfBusiness+us-gaap:AmortizationOfIntangibleAssets)

## Hand checks 2026-11-12 (Ritwik cloud)
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions+mdlz:GainLossOnAcquisitionAndDispositionOfBusiness+us-gaap:AmortizationOfIntangibleAssets (R3.htm): 2026-11-12 R3.htm: agree: 7,173 + 85 - 13 + 142 = 7,387 = GP 10,935 - OI 3,548
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R48.htm): 2026-11-12 R48.htm: agree: R48 'Research and development expense' 400, the total
- interest_expense: mapped us-gaap:InterestExpenseDebt (R74.htm): 2026-11-12 R74.htm: agree: R74 gross interest expense on debt 599; the face prints only 'Interest and other expense, net'
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R116.htm): 2026-11-12 R116.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R116.htm): 2026-11-12 R116.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: agree: R5 lines on LongTermDebtAndCapitalLeaseObligations* (leases inside by tag, finance-lease ruling (founder 2026-11-04 item 5))
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R101.htm): 2026-11-12 R101.htm: decided by R101: printed roll-forward 'Shares Outstanding - Ending balance' 1,281,576,414 at 2025-12-31 (exact)
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income tax provision' is the income_tax_expense line, printed -782000000 = filing XBRL 782000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic earnings per share attributable to Mondelēz ' is the basic_eps line, printed 1.89 = filing XBRL 1.89; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Trade receivables, less allowance ($35 and $37, re' is the accounts_receivable line, printed 3903000000 = filing XBRL 3903000000; agrees
- goodwill: mapped us-gaap:Goodwill (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Goodwill' is the goodwill line, printed 24336000000 = filing XBRL 24336000000; agrees
- accounts_payable: mapped us-gaap:AccountsPayableCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Accounts payable' is the accounts_payable line, printed 10139000000 = filing XBRL 10139000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Capital expenditures' is the capex line, printed -1279000000 = filing XBRL 1279000000; agrees
- total_debt: finance-lease ruling (founder 2026-11-04 item 5): R59 places finance leases inside current and long-term debt; no lease added
