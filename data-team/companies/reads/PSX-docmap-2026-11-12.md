# PSX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001534701-26-000006 (CIK 0001534701, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001534701-16-000119 (CIK 0001534701, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001534701-18-000065 (CIK 0001534701, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001534701-20-000070 (CIK 0001534701, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001534701.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Sales and other operating revenues | 132376000000 | 132376000000 | 143153000000 | 143153000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Purchased crude oil and products | 116093000000 | 116093000000 | 129962000000 | 129962000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1383 tags across all 149 R pages, face and notes) of 0001534701-26-000006; no face row matched |
| operating_expenses | combined | psx:CostAndExpenses | R3.htm | Total Costs and Expenses | 131140000000 |  | 142821000000 |  | API missing | FILING-CHECKED | printed total includes cost of revenue: combined, never opex; company extension tag, matched by printed label / accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 2437000000 | 2437000000 | 2814000000 | 2814000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R145.htm | Other Financial Information (Details) |  | 6000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R145.htm 'Other Financial Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1383 tags across all 149 R pages, face and notes) of 0001534701-26-000006; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R145.htm | Other Financial Information (Details) |  | 997000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R145.htm 'Other Financial Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Income before income taxes | 5420000000 | 5420000000 | 2675000000 | 2675000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 892000000 | 892000000 | 500000000 | 500000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income Attributable to Phillips 66 | 4403000000 | 4403000000 | 2117000000 | 2117000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 10.82 | 10.82 | 5.01 | 5.01 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 10.79 | 10.79 | 4.99 | 4.99 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 406008000 | 406008000 | 420174000 | 420174000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 408053000 | 408053000 | 421888000 | 421888000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1116000000 | 1116000000 | 1738000000 | 1738000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R68.htm | DCP Midstream, LLC and DCP Midstream, LP Mergers - Schedule of Variable Interest Entities (Details) |  | 9771000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R68.htm 'DCP Midstream, LLC and DCP Midstream, LP Mergers - Schedule of Variable Interest' (MetaLinks.json presentation); value from companyfacts same accession |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 5097000000 | 5097000000 | 3995000000 | 3995000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total Current Assets | 17271000000 | 17271000000 | 17910000000 | 17910000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Net properties, plants and equipment | 39097000000 | 39097000000 | 35264000000 | 35264000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 1433000000 | 1433000000 | 1575000000 | 1575000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 73680000000 | 73680000000 | 72582000000 | 72582000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 8581000000 |  | 9792000000 |  | API missing | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total Current Liabilities | 13326000000 | 13326000000 | 15087000000 | 15087000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total Liabilities | 43439000000 | 43439000000 | 44119000000 | 44119000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Stockholders’ Equity | 29093000000 | 29093000000 | 27408000000 | 27408000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net Cash Provided by Operating Activities | 4962000000 | 4962000000 | 4191000000 | 4191000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash Used in Investing Activities | -2097000000 | -2097000000 | -2463000000 | -2463000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net Cash Used in Financing Activities | -3537000000 | -3537000000 | -3305000000 | -3305000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| capex | mapped | psx:CapitalExpendituresAndInvestments | R7.htm | Capital expenditures and investments | -2233000000 |  | -1859000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 3251000000 | 3251000000 | 2363000000 | 2363000000 | Y | FILING-CHECKED | accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R132.htm | Share-Based Compensation Plans - Schedule of Compensation Expense and Tax Benefit (Details) |  | 220000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R132.htm 'Share-Based Compensation Plans - Schedule of Compensation Expense and Tax Benefi' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid on common stock | -1922000000 | 1922000000 | -1882000000 | 1882000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -1207000000 | 1207000000 | -3451000000 | 3451000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001534701-26-000006 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R144.htm | Cash Flow Information (Details) |  | 972000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R144.htm 'Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R144.htm | Cash Flow Information (Details) |  | 200000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R144.htm 'Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Short-term debt + Long-term debt | 19716000000 | 19716000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1383 tags across all 149 R pages, face and notes) of 0001534701-26-000006; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Sales and other operating revenues' on us-gaap:SalesRevenueNet = 98975000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001534701-16-000119 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Total Costs and Expenses' on psx:CostAndExpenses = 94905000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1670000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001534701-16-000119 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001534701-16-000119 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 6044000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1764000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Net Income Attributable to Phillips 66' on us-gaap:NetIncomeLoss = 4227000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Net Income Attributable to Phillips 66 Per Share of Common Stock (in dollars)' on us-gaap:EarningsPerShareBasic = 7.78 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Net Income Attributable to Phillips 66 Per Share of Common Stock (in dollars)' on us-gaap:EarningsPerShareDiluted = 7.73 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 542355000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001534701-16-000119 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 546977000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3074000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Accounts and notes receivable (net of allowances of $55 million in 2015 and $71 ' on psx:AccountsAndNotesReceivableNetOfAllowance = 4411000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 3477000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 12256000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Net properties, plants and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 19721000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 3275000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Total Assets' on us-gaap:Assets = 48580000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 5155000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 7531000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Total Liabilities' on us-gaap:Liabilities = 24642000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001534701-16-000119 R5.htm prints 'Total Stockholders' Equity' on us-gaap:StockholdersEquity = 23100000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 5713000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Net Cash Used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -5738000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Net Cash Used in Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2117000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Capital expenditures and investments' on psx:CapitalExpendituresAndInvestments = -5764000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 1078000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001534701-16-000119 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -1172000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001534701-16-000119 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1512000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001534701-16-000119 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001534701-16-000119 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001534701-18-000065 R2.htm prints 'Sales and other operating revenues' on us-gaap:SalesRevenueNet = 102354000000 (FILING-CHECKED)
- revenue: era 10-K 0001534701-20-000070 R2.htm prints 'Sales and other operating revenues' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 102354000000 (FILING-CHECKED)
- accounts_receivable: era 10-K 0001534701-20-000070 R4.htm prints 'Accounts and notes receivable (net of allowances of $41 million in 2019 and $22 ' on us-gaap:AccountsNotesAndLoansReceivableNetCurrent = 7376000000 (FILING-CHECKED)
- ppe_net: era 10-K 0001534701-20-000070 R4.htm prints 'Net properties, plants and equipment' on us-gaap:PropertyPlantAndEquipmentNet =  (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001534701-20-000070 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 1341000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (psx:CostAndExpenses)
- accounts_payable: API missing (us-gaap:AccountsPayableCurrent)
- capex: API missing (psx:CapitalExpendituresAndInvestments)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: R3 prints no gross profit line; MetaLinks: GrossProfit absent
- operating_expenses: combined psx:CostAndExpenses (R3.htm): 2026-11-12 R3.htm: R3 'Total Costs and Expenses' 131,140 (psx:CostAndExpenses) includes purchased crude and products (cost of revenue): combined
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R145.htm): 2026-11-12 R145.htm: R145 'Other Financial Information' prints R&D expense 6 million = XBRL: mapped, stmt NOTE
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: R3 prints no operating income line (income before taxes only); MetaLinks: OperatingIncomeLoss absent
- interest_expense: mapped us-gaap:InterestAndDebtExpense (R3.htm): 2026-11-12 R3.htm: R3 face prints 'Interest and debt expense' 1,039 (InterestAndDebtExpense, a gross charge after capitalized interest); the machine NOTE row (R145 InterestExpenseDebt 997, the debt-only component) missed
- accounts_receivable: combined us-gaap:AccountsNotesAndLoansReceivableNetCurrent (R5.htm): 2026-11-12 R5.htm: R5 prints 'Accounts and notes receivable' (notes inside) beside other receivable lines: notes receivable are never AR, so combined; the machine NOTE row (R68) is the DCP Midstream VIE schedule, not PSX
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R132.htm): 2026-11-12 R132.htm: no SBC line on the CF (R7); R132 note prints share-based compensation expense 220 = XBRL: mapped, stmt NOTE
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R144.htm): 2026-11-12 R144.htm: R144 cash flow note prints interest paid 972 = XBRL (InterestPaidNet, net of capitalized): mapped, stmt NOTE
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R144.htm): 2026-11-12 R144.htm: R144 prints income taxes paid 200 = XBRL: mapped, stmt NOTE
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: R5 prints short-term debt 1,038 + long-term debt 18,678 = 19,716 = XBRL; no other borrowing line
- shares_outstanding: not_presented  (R5.htm): 2026-11-12 R5.htm: R5/R6 print issued and treasury counts only; MetaLinks: CommonStockSharesOutstanding absent: not_presented
- income_before_tax: mapped us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'Income before income taxes' is the income_before_tax line, printed 5420000000 = filing XBRL 5420000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R5.htm): 2026-11-12 R5.htm: 10% mapped sample: BS R5.htm 'Total Stockholders’ Equity' is the stockholders_equity line, printed 29093000000 = filing XBRL 29093000000; agrees
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R7.htm): 2026-11-12 R7.htm: 10% mapped sample: CF R7.htm 'Net Cash Provided by Operating Activities' is the cfo line, printed 4962000000 = filing XBRL 4962000000; agrees
