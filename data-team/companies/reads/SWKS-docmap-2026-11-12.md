# SWKS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000004127-26-000055 (CIK 0000004127, filed 2026-11-10): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000004127-15-000037 (CIK 0000004127, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000004127-18-000046 (CIK 0000004127, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000004127-20-000058 (CIK 0000004127, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000004127.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net revenue | 3959600000 | 3959600000 | 4086900000 | 4086900000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods sold | 2344700000 | 2344700000 | 2404800000 | 2404800000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1614900000 | 1614900000 | 1682100000 | 1682100000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 1398200000 | 1398200000 | 1182100000 | 1182100000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general, and administrative | 436100000 | 436100000 | 371500000 | 371500000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 837000000 | 837000000 | 785500000 | 785500000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 216700000 | 216700000 | 500000000 | 500000000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | -41300000 | 41300000 | -27100000 | 27100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 213700000 | 213700000 | 5.267e+08 | 526700000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 41600000 | 41600000 | 49600000 | 49600000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 172100000 | 172100000 | 477100000 | 477100000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 1.15 | 1.15 | 3.09 | 3.09 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 1.14 | 1.14 | 3.08 | 3.08 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 150000000 | 150000000 | 154400000 | 154400000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 151000000 | 151000000 | 155100000 | 155100000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R3.htm period ..2026-10-02 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 2606100000 | 2606100000 | 1161300000 | 1161300000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net of allowances of $0.9 and $0.9, respectively | 494700000 | 494700000 | 598100000 | 598100000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventory | 1070000000 | 1070000000 | 754700000 | 754700000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 4684400000 | 4684400000 | 3077000000 | 3077000000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment, net | 1197600000 | 1197600000 | 1194600000 | 1194600000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2176700000 | 2176700000 | 2176700000 | 2176700000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 9436800000 | 9436800000 | 7917000000 | 7917000000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 301800000 | 301800000 | 236000000 | 236000000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 934600000 | 934600000 | 1323200000 | 1323200000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3721100000 | 3721100000 | 2159900000 | 2159900000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 5715700000 | 5715700000 | 5757100000 | 5757100000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R5.htm period ..2026-10-02 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 549900000 | 549900000 | 1300800000 | 1300800000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -134300000 | -134300000 | -234000000 | -234000000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | 1029200000 | 1029200000 | -1274100000 | -1274100000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -320600000 | 320600000 | -195000000 | 195000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation | 289100000 | 289100000 | 278700000 | 278700000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 218400000 | 218400000 | 232400000 | 232400000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| dividends_paid | mapped | us-gaap:PaymentsOfOrdinaryDividends | R7.htm | Dividends paid | -320100000 | 320100000 | -432600000 | 432600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock - stock repurchase program | -114500000 | 114500000 | -830200000 | 830200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | 25900000 | 25900000 | 25400000 | 25400000 | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid, after refunds received | 140300000 | 140300000 |  |  | Y | FILING-CHECKED | accn 0000004127-26-000055 R7.htm period ..2026-10-02 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebt | R5.htm | Current portion of long-term debt + Long-term debt | 2472800000 | 2472800000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding | 149100000 | 149100000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-10-02; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Net revenue' on us-gaap:SalesRevenueNet = 3258400000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 1703900000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1554500000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 531400000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 191300000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 303200000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1023100000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000004127-15-000037 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1023600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 225300000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 798300000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 4.21 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 4.1 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 189500000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000004127-15-000037 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 194900000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1.044e+09 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Receivables, net of allowance for doubtful accounts of $0.4 and $0.8, respective' on us-gaap:ReceivablesNetCurrent = 538000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Inventory' on us-gaap:InventoryNet = 2.679e+08 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1914700000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 826400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 856700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Total assets' on us-gaap:Assets = 3719400000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 291100000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 463900000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 560200000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000004127-15-000037 R4.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 3159200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 992800000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -454700000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -300300000 (FILING-CHECKED)
- capex: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -430100000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000004127-15-000037 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 99800000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfOrdinaryDividends = -123100000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Repurchase of common stock - share repurchase program' on us-gaap:PaymentsForRepurchaseOfCommonStock = -237300000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000004127-15-000037 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000004127-15-000037 R6.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 126100000 (FILING-CHECKED)
- revenue: era 10-K 0000004127-18-000046 R2.htm prints 'Net revenue' on us-gaap:SalesRevenueNet = 3868000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000004127-18-000046 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 1917300000 (FILING-CHECKED)
- cfo: era 10-K 0000004127-18-000046 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1260600000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000004127-18-000046 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1150400000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000004127-18-000046 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -993700000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000004127-20-000058 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 891700000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| goodwill | mapped-sample | agree | page value 2176700000 vs printed 2176700000 |
| accounts_payable | mapped-sample | agree | page value 301800000 vs printed 301800000 |
| cfo | mapped-sample | agree | page value 549900000 vs printed 549900000 |
| capex | mapped-sample | agree | page value -320600000 vs printed -320600000 |
| depreciation_and_amortization | component sum | agree | page value 289100000 vs printed 289100000 |
| total_debt | component sum | agree | page value 2472800000 vs printed 2472800000 |
