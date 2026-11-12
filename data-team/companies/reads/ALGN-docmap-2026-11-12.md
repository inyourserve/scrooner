# ALGN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001097149-26-000014 (CIK 0001097149, filed 2026-02-27): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001097149-16-000031 (CIK 0001097149, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001097149-18-000010 (CIK 0001097149, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001097149-21-000007 (CIK 0001097149, era filing): COVER R1.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0001097149.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net revenues | 4034964000 | 4034964000 | 3999012000 | 3999012000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of net revenues | 1323951000 | 1323951000 | 1199853000 | 1199853000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 2711013000 | 2711013000 | 2799159000 | 2799159000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 2165258000 | 2165258000 | 2191531000 | 2191531000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 1755791000 | 1755791000 | 1763193000 | 1763193000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 369911000 | 369911000 | 364202000 | 364202000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Income from operations | 545755000 | 545755000 | 607628000 | 607628000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (887 tags across all 101 R pages, face and notes) of 0001097149-26-000014; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Net income before provision for income taxes | 585287000 | 585287000 | 608959000 | 608959000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Tax expense | 174936000 | 174936000 | 187597000 | 187597000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 410351000 | 410351000 | 421362000 | 421362000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income per share, basic (usd per share) | 5.66 | 5.66 | 5.63 | 5.63 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (usd per share) | 5.65 | 5.65 | 5.62 | 5.62 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (shares) | 72542000 | 72542000 | 74877000 | 74877000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (shares) | 72588000 | 72588000 | 74993000 | 74993000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1094908000 | 1094908000 | 1043887000 | 1043887000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowance for doubtful accounts of $34,213 and $19,131, respectively | 1101757000 | 1101757000 | 995685000 | 995685000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 226343000 | 226343000 | 254287000 | 254287000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 2616562000 | 2616562000 | 2492441000 | 2492441000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 1131453000 | 1131453000 | 1271134000 | 1271134000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 491833000 | 491833000 | 442630000 | 442630000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 6233693000 | 6233693000 | 6214600000 | 6214600000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 121450000 | 121450000 | 108693000 | 108693000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1920015000 | 1920015000 | 2038027000 | 2038027000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 2184546000 | 2184546000 | 2362615000 | 2362615000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 4049147000 | 4049147000 | 3851985000 | 3851985000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 593223000 | 593223000 | 738231000 | 738231000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -112445000 | -112445000 | -254912000 | -254912000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -464580000 | -464580000 | -355722000 | -355722000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property, plant and equipment | -102445000 | 102445000 | -115580000 | 115580000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 237436000 | 237436000 | 145034000 | 145034000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 185870000 | 185870000 | 173703000 | 173703000 | Y | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (887 tags across all 101 R pages, face and notes) of 0001097149-26-000014; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Common stock repurchases, net of excise tax | -465939000 | 465939000 | -352878000 | 352878000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001097149-26-000014 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (887 tags across all 101 R pages, face and notes) of 0001097149-26-000014; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R90.htm | Income Taxes - Schedule of Income Tax Paid (Details) |  | 134753000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Income Taxes - Schedule of Income Tax Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (887 tags across all 101 R pages, face and notes) of 0001097149-26-000014; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, outstanding (shares) | 71364000 | 71364000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 845486000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Cost of revenues' on us-gaap:CostOfRevenue = 205376000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 640110000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 451476000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 390239000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 61237000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 188634000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Net income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 186101000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 42081000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 144020000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Basic (usd per share)' on us-gaap:EarningsPerShareBasic = 1.8 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Diluted (usd per share)' on us-gaap:EarningsPerShareDiluted = 1.77 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 79998000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001097149-16-000031 R2.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 81521000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 167714000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Accounts receivable, net of allowance for doubtful accounts and returns of $2,47' on us-gaap:AccountsReceivableNetCurrent = 158550000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 19465000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 732010000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 136473000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Goodwill' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 79162000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Total assets' on us-gaap:Assets = 1158633000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 34354000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 271672000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 310707000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001097149-16-000031 R4.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 847926000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 237997000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -166361000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -100786000 (FILING-CHECKED)
- capex: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Purchase of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -53451000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 18004000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 52943000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001097149-16-000031 R7.htm prints 'Common stock repurchase' on us-gaap:PaymentsForRepurchaseOfCommonStock = -101791000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001097149-16-000031 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001097149-18-000010 R2.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 1473413000 (FILING-CHECKED)
- income_before_tax: 10-K 0001097149-21-000007 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | mapped-sample | agree | page value 2165258000 vs printed 2165258000 |
| sga_expense | mapped-sample | agree | page value 1755791000 vs printed 1755791000 |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 1131453000 vs printed 1131453000 |
| depreciation_and_amortization | mapped-sample | agree | page value 237436000 vs printed 237436000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 134753000 vs API 134753000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
