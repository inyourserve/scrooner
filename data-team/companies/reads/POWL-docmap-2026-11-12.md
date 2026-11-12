# POWL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000080420-25-000152 (CIK 0000080420, filed 2025-11-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001564590-15-011208 (CIK 0000080420, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000080420-17-000032 (CIK 0000080420, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000080420-18-000036 (CIK 0000080420, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000080420.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues | 1104318000 | 1104318000 | 1012356000 | 1012356000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 779937000 | 779937000 | 739268000 | 739268000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 324381000 | 324381000 | 273088000 | 273088000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R75.htm | Total segment operating expenses | 886458000 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R75.htm 'Segment Information - Schedule of Segment Net Income, Including Segment Expenses' (MetaLinks.json presentation) |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 95401000 | 95401000 | 84888000 | 84888000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development expenses | 11008000 | 11008000 | 9427000 | 9427000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 217860000 | 217860000 | 178773000 | 178773000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income, net | -15690000 | 15690000 | -17315000 | 17315000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 233550000 | 233550000 | 196088000 | 196088000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | 52803000 | 52803000 | 46240000 | 46240000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 180747000 | 180747000 | 149848000 | 149848000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 14.98 | 14.98 | 12.51 | 12.51 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 14.86 | 14.86 | 12.29 | 12.29 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 12062000 | 12062000 | 11982000 | 11982000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 12167000 | 12167000 | 12188000 | 12188000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R5.htm period ..2025-09-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 450739000 | 450739000 | 315331000 | 315331000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, less allowance for credit losses of $368 and $414, respectively | 217065000 | 217065000 | 214405000 | 214405000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 84719000 | 84719000 | 85873000 | 85873000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total Current Assets | 931716000 | 931716000 | 776481000 | 776481000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 111049000 | 111049000 | 103421000 | 103421000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 6125000 | 6125000 | 1003000 | 1003000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 1108984000 | 1108984000 | 928180000 | 928180000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 67080000 | 67080000 | 73633000 | 73633000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total Current Liabilities | 446387000 | 446387000 | 428015000 | 428015000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 468214000 | 468214000 | 445107000 | 445107000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Stockholders’ Equity | 640770000 | 640770000 | 483073000 | 483073000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R3.htm period ..2025-09-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 167937000 | 167937000 | 108661000 | 108661000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -8342000 | -8342000 | -21874000 | -21874000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -25117000 | -25117000 | -19252000 | -19252000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment | -13149000 | 13149000 | -11983000 | 11983000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 7265000 | 7265000 | 6871000 | 6871000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 4635000 | 4635000 | 4747000 | 4747000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -12869000 | 12869000 | -12653000 | 12653000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000080420-25-000152 R9.htm period ..2025-09-30 |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (718 tags across all 82 R pages, face and notes) of 0000080420-25-000152; HAND REVIEW: 6 label candidate(s) incl. custom tags: us-gaap:CommonStockSharesIssued 'Common stock, shares issued (in shares) / Common Stock, Shar' R4; us-gaap:CommonStockValueOutstanding 'Common stock, par value $0.01; 30,000,000 shares authorized;' R3; us-gaap:PreferredStockSharesIssued 'Preferred stock, shares issued (in shares) / Preferred Stock' R4; us-gaap:PreferredStockValue 'Preferred stock, par value $0.01; 5,000,000 shares authorize' R3; us-gaap:TreasuryStockCommonShares 'Treasury stock (in shares) / Beginning balance, Treasury sto' R4,R7; us-gaap:TreasuryStockValue 'Treasury stock, 806,018 shares at cost / Treasury Stock, Val' R3 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (718 tags across all 82 R pages, face and notes) of 0000080420-25-000152; HAND REVIEW: 1 label candidate(s) incl. custom tags: powl:InterestPaidNetOfInterestIncome 'Interest received, net of interest expense / Interest Paid, ' R43 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R43.htm | Income taxes paid, net of refunds | 56133000 | 56133000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R43.htm 'Summary of Significant Accounting Policies - Schedule of Supplemental Disclosure' (MetaLinks.json presentation) |
| total_debt | mapped | us-gaap:LongTermDebt | R58.htm | Revolving credit facility borrowings, outstanding amount | 0 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R58.htm 'Long-Term Debt (Details)' (MetaLinks.json presentation) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 12070178 | 12070178 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-09-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Revenues' on us-gaap:ContractsRevenue = 661858000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Cost of goods sold' on us-gaap:ContractRevenueCost = 553597000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 108261000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Selling, general and administrative expenses + Research and development expenses' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:AmortizationOfIntangibleAss = 87613000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 76801000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Research and development expenses' on us-gaap:ResearchAndDevelopmentExpense = 6980000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 20648000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 145000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 22991000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 13552000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 9439000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 0.8 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted = 0.79 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 11869000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-15-011208 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 11908000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 43569000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Accounts receivable, less allowance for doubtful accounts of $746 and $1,577' on us-gaap:AccountsReceivableNetCurrent = 101784000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 32891000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 297099000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 154594000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Goodwill and intangible assets, net' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 2393000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Total Assets' on us-gaap:Assets = 468824000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 48008000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 124952000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 135562000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-15-011208 R2.htm prints 'Total Stockholders' Equity' on us-gaap:StockholdersEquity = 333262000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-15-011208 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 12918000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-15-011208 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -34607000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-15-011208 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -34948000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-15-011208 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -34719000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-15-011208 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001564590-15-011208 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 3171000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-15-011208 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -12358000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-15-011208 R8.htm read; no row matched (auto)
- revenue: era 10-K 0000080420-17-000032 R4.htm prints 'Revenues' on us-gaap:ContractsRevenue = 395911000 (FILING-CHECKED)
- cfo: era 10-K 0000080420-17-000032 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 36815000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000080420-17-000032 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -55304000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000080420-17-000032 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -12673000 (FILING-CHECKED)
- revenue: era 10-K 0000080420-18-000036 R4.htm prints 'Revenues' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 448716000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:OperatingExpenses)
- total_debt: API missing (us-gaap:LongTermDebt)
