# ARW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-012765 (CIK 0000007536, filed 2026-02-11): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001650030-16-000009 (CIK 0000007536, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001859644-23-000005 (CIK 0000007536, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000007536.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Sales | 30852935000 | 30852935000 | 27923324000 | 27923324000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 27386216000 | 27386216000 | 24630916000 | 24630916000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 3466719000 | 3466719000 | 3292408000 | 3292408000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 2644496000 | 2644496000 | 2523851000 | 2523851000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general, and administrative | 2390627000 | 2390627000 | 2217940000 | 2217940000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (914 tags across all 87 R pages, face and notes) of 0001104659-26-012765; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 822223000 | 822223000 | 768557000 | 768557000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (914 tags across all 87 R pages, face and notes) of 0001104659-26-012765; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 717928000 | 717928000 | 489319000 | 489319000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 148234000 | 148234000 | 95812000 | 95812000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to shareholders | 571266000 | 571266000 | 392074000 | 392074000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 11.03 | 11.03 | 7.36 | 7.36 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 10.93 | 10.93 | 7.29 | 7.29 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 51804000 | 51804000 | 53282000 | 53282000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 52255000 | 52255000 | 53797000 | 53797000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 306467000 | 306467000 | 188807000 | 188807000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 19738666000 | 19738666000 | 13030991000 | 13030991000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 5081863000 | 5081863000 | 4709706000 | 4709706000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 25660031000 | 25660031000 | 18401413000 | 18401413000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment, net | 474650000 | 474650000 | 469260000 | 469260000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2120071000 | 2120071000 | 2055295000 | 2055295000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 29078138000 | 29078138000 | 21757707000 | 21757707000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 17383796000 | 17383796000 | 11047470000 | 11047470000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 18845398000 | 18845398000 | 12636162000 | 12636162000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (914 tags across all 87 R pages, face and notes) of 0001104659-26-012765; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders' equity | 6584712000 | 6584712000 | 5761151000 | 5761151000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 64049000 | 64049000 | 1130413000 | 1130413000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used for) investing activities | 23604000 | 23604000 | -94442000 | -94442000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used for financing activities | -206137000 | -206137000 | -956827000 | -956827000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Acquisition of property, plant, and equipment | -101254000 | 101254000 | -92703000 | 92703000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 137750000 | 137750000 | 162994000 | 162994000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Amortization of stock-based compensation | 27883000 | 27883000 | 34631000 | 34631000 | Y | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (914 tags across all 87 R pages, face and notes) of 0001104659-26-012765; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock | -161669000 | 161669000 | -265142000 | 265142000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-012765 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R55.htm | Debt - LT Debt (Details) |  | 163200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R55.htm 'Debt - LT Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R59.htm | Income Taxes (Details) |  | 195200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R59.htm 'Income Taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings, including current portion of long-term debt + Long-term debt | 3085056000 | 3085056000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R72.htm | Shareholders' Equity - Common Stock Outstanding Activity (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R72.htm 'Shareholders' Equity - Common Stock Outstanding Activity (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Sales' on us-gaap:SalesRevenueNet = 23282020000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 20246770000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001650030-16-000009 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Total Costs and Expenses' on us-gaap:CostsAndExpenses = 22457538000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Selling, general, and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1986249000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 824482000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Income before income taxes' on arw:IncomeBeforeIncomeTaxesAndAdjustmentForNoncontrollingInterest = 692183000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 191697000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Net income attributable to shareholders' on us-gaap:NetIncomeLoss = 497726000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 5.26 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 5.2 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 94608000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001650030-16-000009 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 95686000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 273090000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 6161418000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 2466490000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 9186471000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Property, plant, and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 700178000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Cost in excess of net assets of companies acquired' on us-gaap:Goodwill = 2368832000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Total assets' on us-gaap:Assets = 13021930000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 5192665000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 6056152000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001650030-16-000009 R4.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 4142443000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 655079000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -664027000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Net cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -84187000 (FILING-CHECKED)
- capex: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Acquisition of property, plant, and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -154800000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 155754000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Amortization of stock-based compensation' on us-gaap:ShareBasedCompensation = 47274000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001650030-16-000009 R6.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -356434000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001650030-16-000009 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001650030-16-000009 R6.htm read; no row matched (auto)
- income_before_tax: era 10-K 0001859644-23-000005 R3.htm prints 'Income before income taxes' on arw:IncomeBeforeIncomeTaxesAndAdjustmentForNoncontrollingInterest = 1884150000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | mapped-sample | agree | page value 3466719000 vs printed 3466719000 |
| operating_expenses | combined | agree | page value 2644496000 vs printed 2644496000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| stockholders_equity | mapped-sample | agree | page value 6584712000 vs printed 6584712000 |
| capex | mapped-sample | agree | page value -101254000 vs printed -101254000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 163200000 vs API 163200000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 195200000 vs API 195200000 |
| total_debt | component sum | agree | page value 3085056000 vs printed 3085056000 |
| shares_outstanding | NOTE | agree | value 55592000 read off its own R page (no companyfacts fact to compare) |
