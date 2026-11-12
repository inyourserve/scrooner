# FICO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000814547-26-000042 (CIK 0000814547, filed 2026-11-06): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0000814547-15-000019 (CIK 0000814547, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000814547-17-000014 (CIK 0000814547, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000814547-18-000010 (CIK 0000814547, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0000814547.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 2534873000 | 2534873000 | 1990869000 | 1990869000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenues | 351480000 | 351480000 | 353722000 | 353722000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (861 tags across all 97 R pages, face and notes) of 0000814547-26-000042; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 1269179000 | 1269179000 | 1066019000 | 1066019000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 681099000 | 681099000 | 513028000 | 513028000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 209307000 | 209307000 | 188347000 | 188347000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1265694000 | 1265694000 | 924850000 | 924850000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| interest_expense | combined | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense, net | -223314000 | 223314000 | -133647000 | 133647000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1100050000 | 1100050000 | 802595000 | 802595000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 265083000 | 265083000 | 150649000 | 150649000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 834967000 | 834967000 | 651946000 | 651946000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 36.52 | 36.52 | 26.9 | 26.9 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 36.32 | 36.32 | 26.54 | 26.54 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 22863000 | 22863000 | 24239000 | 24239000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 22988000 | 22988000 | 24561000 | 24561000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R5.htm period ..2026-09-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 217599000 | 217599000 | 134136000 | 134136000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 602946000 | 602946000 | 529148000 | 529148000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (861 tags across all 97 R pages, face and notes) of 0000814547-26-000042; label search over every tag in the filing (custom included) found no candidate |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 911671000 | 911671000 | 705165000 | 705165000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 97142000 | 97142000 | 67713000 | 67713000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 791867000 | 791867000 | 783340000 | 783340000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2075022000 | 2075022000 | 1868133000 | 1868133000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 34672000 | 34672000 | 32315000 | 32315000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 919694000 | 919694000 | 849215000 | 849215000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 5948233000 | 5948233000 | 3613917000 | 3613917000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ deficit | -3873211000 | -3873211000 | -1745784000 | -1745784000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R3.htm period ..2026-09-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1072065000 | 1072065000 | 778807000 | 778807000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -45401000 | -45401000 | -43719000 | -43719000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -941129000 | -941129000 | -750329000 | -750329000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -2140000 | 2140000 | -8922000 | 8922000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 16718000 | 16718000 | 14952000 | 14952000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 185457000 | 185457000 | 156667000 | 156667000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (861 tags across all 97 R pages, face and notes) of 0000814547-26-000042; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock, inclusive of excise tax | -3045991000 | 3045991000 | -1414502000 | 1414502000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 224366000 | 224366000 | 103564000 | 103564000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes, net of refunds of $8,555, $8,649 and $859 during the years ended September 30, 2026, 2025 an | 226367000 | 226367000 | 162089000 | 162089000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000814547-26-000042 R7.htm period ..2026-09-30 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current maturities on debt + Long-term debt | 5259104000 | 5259104000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 21381000 | 21381000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-09-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 838781000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Cost of revenues' on us-gaap:CostOfRevenue = 270535000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 701276000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 300002000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 98824000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 137505000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -29150000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 109238000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 22736000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 86502000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Basic earnings per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.75 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Diluted earnings per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.65 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Shares used in computing basic earnings per share (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 31402000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000814547-15-000019 R4.htm prints 'Shares used in computing diluted earnings per share (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 32609000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 86120000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 158773000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 286602000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 38208000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 814750000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Total assets' on us-gaap:Assets = 1230163000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 19852000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 243875000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 793165000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000814547-15-000019 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 436998000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 132977000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -81916000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -58635000 (FILING-CHECKED)
- capex: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -24999000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 33889000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 45308000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -130719000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 30470000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000814547-15-000019 R6.htm prints 'Cash paid for income taxes, net of refunds of $1,592, $3,424 and $2,471 during t' on us-gaap:IncomeTaxesPaidNet = 33752000 (FILING-CHECKED)
- revenue: era 10-K 0000814547-17-000014 R4.htm prints 'Total revenues' on us-gaap:SalesRevenueNet = 932169000 (FILING-CHECKED)
- revenue: era 10-K 0000814547-18-000010 R4.htm prints 'Revenues' on us-gaap:Revenues = 1032475000 (FILING-CHECKED)
- cfo: era 10-K 0000814547-18-000010 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 223052000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000814547-18-000010 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -14119000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000814547-18-000010 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -218627000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000814547-18-000010 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 26106000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 9 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:FICO); disagree on the mapped sample: 0/3
- cost_of_revenue: agree (R5 Cost of revenues 351,480)
- dividends_paid: agree (R7 prints no dividend line)
- gross_profit: agree (R5 prints no gross profit line)
- interest_expense: agree (R5 'Interest expense, net' is a net line: combined)
- inventory: agree (R3 prints no inventory line (software company))
- operating_expenses: agree (R5 'Total operating expenses' CostsAndExpenses 1,269,179 includes cost of revenues 351,480: combined, never opex)
- sga_expense: agree (R5 SG&A 681,099)
- shares_outstanding: agree (R4 common stock shares outstanding 21,381,000 at 2026-09-30)
- total_debt: agree (R3 current maturities 337,500 + long-term debt 4,921,604 = 5,259,104 (thousands))
