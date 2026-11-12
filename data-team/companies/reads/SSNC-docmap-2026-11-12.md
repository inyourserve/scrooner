# SSNC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-076745 (CIK 0001402436, filed 2026-02-26): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm, IS R4.htm
- 10-K 0001564590-16-013602 (CIK 0001402436, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CF R5.htm
- 10-K 0001564590-18-003827 (CIK 0001402436, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R5.htm, IS R4.htm
- companyfacts CIK0001402436.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Total revenues | 6272200000 | 6272200000 | 5882000000 | 5882000000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Total cost of revenues | 3250600000 | 3250600000 | 3018400000 | 3018400000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profit | 3021600000 | 3021600000 | 2863600000 | 2863600000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Total operating expenses | 1584900000 | 1584900000 | 1520100000 | 1520100000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R4.htm | General and administrative + Selling and marketing | 1077400000 | 1077400000 | 1002400000 | 1002400000 | Y | FILING-CHECKED | check: hand R4.htm (0001193125-26-076745): CORRECTED (was mapped us-gaap:GeneralAndAdministrativeExpense): R4 prints 'Selling and marketing' 625.0 and 'General and administrative' 452.4: SG&A is never G&A alone when S&M is printed (Dhairya 2026-11-13) = 1,077.4 / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 507500000 | 507500000 | 5.177e+08 | 517700000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 1436700000 | 1436700000 | 1343500000 | 1343500000 | Y | FILING-CHECKED | check: hand R4.htm (0001193125-26-076745): agree: printed value on the R page equals the API value / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | -434700000 | 434700000 | -463000000 | 463000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 974800000 | 974800000 | 893700000 | 893700000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Provision for income taxes (Note 17) | 176100000 | 176100000 | 132000000 | 132000000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to SS&C common stockholders | 796900000 | 796900000 | 760500000 | 760500000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic earnings per share attributable to SS&C common stockholders | 3.26 | 3.26 | 3.09 | 3.09 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted earnings per share attributable to SS&C common stockholders | 3.15 | 3.15 | 3 | 3 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic weighted-average number of common shares outstanding | 244300000 | 244300000 | 246400000 | 246400000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted weighted-average number of common and common equivalent shares outstanding | 253100000 | 253100000 | 253800000 | 253800000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 462100000 | 462100000 | 567100000 | 567100000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net of allowance for credit losses of $34.9 and $31.6, respectively (Note 3) | 978700000 | 978700000 | 902000000 | 902000000 | Y | FILING-CHECKED | check: hand R2.htm (0001193125-26-076745): agree: R2 'Accounts receivable, net' on AccountsReceivableNetCurrent; client funds receivable is a separate extension line / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand R2.htm (0001193125-26-076745): agree: no such line on the face; whole-filing check below confirmed by reading the face page / whole-filing check: none of InventoryNet in MetaLinks.json (1141 tags across all 106 R pages, face and notes) of 0001193125-26-076745; label search over every tag in the filing (custom included) found no candidate |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 5487700000 | 5487700000 | 4862400000 | 4862400000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property, plant and equipment, net (Note 4) | 289500000 | 289500000 | 299600000 | 299600000 | Y | FILING-CHECKED | check: hand R2.htm (0001193125-26-076745): agree: printed value on the R page equals the API value / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill (Note 9) | 9991300000 | 9991300000 | 9218100000 | 9218100000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 20711700000 | 20711700000 | 19044700000 | 19044700000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 87200000 | 87200000 | 70200000 | 70200000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 5111300000 | 5111300000 | 4354300000 | 4354300000 | Y | FILING-CHECKED | check: hand R2.htm (0001193125-26-076745): agree: printed value on the R page equals the API value / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 13769900000 | 13769900000 | 12435600000 | 12435600000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total SS&C stockholders' equity | 6887600000 | 6887600000 | 6534900000 | 6534900000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R5.htm | Net cash provided by operating activities | 1744800000 | 1744800000 | 1388600000 | 1388600000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used in investing activities | -1307600000 | -1307600000 | -855700000 | -855700000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash (used in) provided by financing activities | -243500000 | -243500000 | -152300000 | -152300000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R5.htm | Additions to property and equipment | -80800000 | 80800000 | -61400000 | 61400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R5.htm | Depreciation and amortization | 703800000 | 703800000 | 680100000 | 680100000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Stock-based compensation expense | 257700000 | 257700000 | 203300000 | 203300000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R5.htm | Dividends paid on common stock | -253800000 | 253800000 | -244900000 | 244900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R5.htm | Purchases of common stock for treasury | -1036000000 | 1036000000 | -737500000 | 737500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R5.htm | Interest | 427800000 | 427800000 | 452400000 | 452400000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R5.htm | Income taxes, net of refunds | 219400000 | 219400000 | 286200000 | 286200000 | Y | FILING-CHECKED | check: machine-full-filing / value_source sec_api / accn 0001193125-26-076745 R5.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R2.htm | Current portion of long-term debt (Note 10) + Long-term debt, net of current portion (Note 10) | 7433400000 | 7433400000 |  |  | Y | FILING-CHECKED | check: hand R2.htm (0001193125-26-076745): agree: R2 current portion 25.0 + long-term debt 7,408.4 / value_source sec_api / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 241400000 | 241400000 |  |  | Y | FILING-CHECKED | check: hand R3.htm (0001193125-26-076745): agree: printed value on the R page equals the API value / value_source sec_api / balance-sheet date 2025-12-31; single row |

## Hand check (2026-11-13)
Machine pass: data-team/companies/reads/tools/docmap.py (origin/work/reads/901-1000 d918c527). Hand-checked 8 rows against the printed R pages of 0001193125-26-076745 (every not_presented, combined, component and NOTE row, plus a random 10% of mapped rows, seed '401-500:SSNC': 4 sampled, 0 disagreed). Corrections: 1.
- sga_expense: R4 prints 'Selling and marketing' 625.0 and 'General and administrative' 452.4: SG&A is never G&A alone when S&M is printed (Dhairya 2026-11-13) = 1,077.4

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0001564590-16-013602 statement not identified (auto)
- cost_of_revenue: 10-K 0001564590-16-013602 statement not identified (auto)
- gross_profit: 10-K 0001564590-16-013602 statement not identified (auto)
- operating_expenses: 10-K 0001564590-16-013602 statement not identified (auto)
- sga_expense: 10-K 0001564590-16-013602 statement not identified (auto)
- research_and_development: 10-K 0001564590-16-013602 statement not identified (auto)
- operating_income: 10-K 0001564590-16-013602 statement not identified (auto)
- interest_expense: 10-K 0001564590-16-013602 statement not identified (auto)
- income_before_tax: 10-K 0001564590-16-013602 statement not identified (auto)
- income_tax_expense: 10-K 0001564590-16-013602 statement not identified (auto)
- net_income: 10-K 0001564590-16-013602 statement not identified (auto)
- basic_eps: 10-K 0001564590-16-013602 statement not identified (auto)
- diluted_eps: 10-K 0001564590-16-013602 statement not identified (auto)
- weighted_basic_shares: 10-K 0001564590-16-013602 statement not identified (auto)
- weighted_diluted_shares: 10-K 0001564590-16-013602 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 434159000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $2,957 and $2,241' on us-gaap:AccountsReceivableNetCurrent = 169951000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 675066000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 67143000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 3549212000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Total assets' on us-gaap:Assets = 5802242000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 11957000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 416718000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 3696796000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013602 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 2105446000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 230624000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -2748312000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 2847066000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -13600000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 150834000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Stock-based compensation expense' on us-gaap:AllocatedShareBasedCompensationExpense = 44079000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -45451000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Purchase of common stock for treasury' on us-gaap:PaymentsForRepurchaseOfCommonStock =  (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Interest' on us-gaap:InterestPaid = 42221000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013602 R5.htm prints 'Income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 42210000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-003827 R4.htm prints 'Total revenues' on us-gaap:Revenues = 1675295000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-003827 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 470362000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-003827 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -63383000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-003827 R5.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -466413000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001564590-18-003827 R5.htm prints 'Interest' on us-gaap:InterestPaid = 102703000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
