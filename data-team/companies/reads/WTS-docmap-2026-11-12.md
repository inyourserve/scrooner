# WTS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-018541 (CIK 0000795403, filed 2026-02-23): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001047469-16-010540 (CIK 0000795403, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001558370-18-001010 (CIK 0000795403, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001558370-19-000893 (CIK 0000795403, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000795403.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net sales | 2438500000 | 2438500000 | 2252200000 | 2252200000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of goods sold | 1232500000 | 1232500000 | 1190200000 | 1190200000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | GROSS PROFIT | 1206000000 | 1206000000 | 1062000000 | 1062000000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions | R2.htm | Selling, general and administrative expenses + Restructuring | 7.579e+08 | 757900000 | 671600000 | 671600000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 734200000 | 734200000 | 664400000 | 664400000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R54.htm | Accounting Policies - Shipping and Handling, and Research and Development (Details) |  | 73500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R54.htm 'Accounting Policies - Shipping and Handling, and Research and Development (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | OPERATING INCOME | 448100000 | 448100000 | 390400000 | 390400000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R2.htm | Interest expense | 10800000 | 10800000 | 14700000 | 14700000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | INCOME BEFORE INCOME TAXES | 445800000 | 445800000 | 386000000 | 386000000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 105000000 | 105000000 | 94800000 | 94800000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R2.htm | NET INCOME | 340800000 | 340800000 | 291200000 | 291200000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | NET INCOME PER SHARE | 10.17 | 10.17 | 8.7 | 8.7 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | NET INCOME PER SHARE | 10.17 | 10.17 | 8.69 | 8.69 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Weighted average number of shares | 33500000 | 33500000 | 33500000 | 33500000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Weighted average number of shares | 33500000 | 33500000 | 33500000 | 33500000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 405500000 | 405500000 | 386900000 | 386900000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade accounts receivable, less reserve allowances of $12.5 million at December 31, 2025 and $11.9 million at December 3 | 294000000 | 294000000 | 253200000 | 253200000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Total Inventories | 5.243e+08 | 524300000 | 392100000 | 392100000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total Current Assets | 1286100000 | 1286100000 | 1083500000 | 1083500000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 297100000 | 297100000 | 254800000 | 254800000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 859000000 | 859000000 | 715000000 | 715000000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | TOTAL ASSETS | 2881200000 | 2881200000 | 2397000000 | 2397000000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 182200000 | 182200000 | 148000000 | 148000000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total Current Liabilities | 512400000 | 512400000 | 417900000 | 417900000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1030 tags across all 98 R pages, face and notes) of 0001104659-26-018541; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Stockholders' Equity | 2027700000 | 2027700000 | 1707900000 | 1707900000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 402000000 | 402000000 | 361100000 | 361100000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -302800000 | -302800000 | -124700000 | -124700000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) provided by financing activities | -96900000 | -96900000 | -190500000 | -190500000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Additions to property, plant and equipment | -45700000 | 45700000 | -35300000 | 35300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R8.htm | Depreciation + Amortization of intangibles | 5.68e+07 | 56800000 | 5.44e+07 | 54400000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 21200000 | 21200000 | 19500000 | 19500000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1030 tags across all 98 R pages, face and notes) of 0001104659-26-018541; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Payments to repurchase common stock | -16000000 | 16000000 | -17000000 | 17000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 9900000 | 9900000 | 12700000 | 12700000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes | 74400000 | 74400000 | 117200000 | 117200000 | Y | FILING-CHECKED | accn 0001104659-26-018541 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | LONG-TERM DEBT | 197700000 | 197700000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R6.htm | Common Stock, outstanding shares | 33342823 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueNet = 1467700000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 914600000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-16-010540 R2.htm prints 'GROSS PROFIT' on us-gaap:GrossProfit = 553100000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Selling, general and administrative expenses + Restructuring and other charges, ' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringSettlementAndImpairmentProvisions+us-gaap:GoodwillAn = 643200000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 491300000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047469-16-010540 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001047469-16-010540 R2.htm prints 'OPERATING (LOSS) INCOME' on us-gaap:OperatingIncomeLoss = -90100000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 24300000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047469-16-010540 R2.htm prints '(LOSS) INCOME FROM CONTINUING OPERATIONS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -111000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1900000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-16-010540 R2.htm prints 'NET (LOSS) INCOME' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = -112900000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-010540 R2.htm prints 'NET (LOSS) INCOME (in dollars per share)' on us-gaap:EarningsPerShareBasic = -3.24 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-010540 R2.htm prints 'NET (LOSS) INCOME (in dollars per share)' on us-gaap:EarningsPerShareDiluted = -3.24 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Weighted average number of shares (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 34900000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-010540 R2.htm prints 'Weighted average number of shares (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 34900000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations = 296200000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Trade accounts receivable, less allowance for doubtful accounts of $10.1 in 2015' on us-gaap:AccountsReceivableNetCurrent = 186400000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Inventories, net' on us-gaap:InventoryNet = 240000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 809000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-16-010540 R5.htm prints 'PROPERTY, PLANT AND EQUIPMENT, NET' on us-gaap:PropertyPlantAndEquipmentNet = 184400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 489000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-010540 R5.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 1692800000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 101700000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 295000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-010540 R5.htm prints 'Total Stockholders' Equity' on us-gaap:StockholdersEquity = 704900000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 109400000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -17300000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -70900000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Additions to property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -27700000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-010540 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 10900000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Payments to repurchase common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -44600000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Interest' on us-gaap:InterestPaid = 23100000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-16-010540 R8.htm prints 'Taxes' on us-gaap:IncomeTaxesPaid = 24500000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-18-001010 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueNet = 1456700000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001558370-19-000893 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 908400000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 757900000 = printed 7.579e+08 at 4 significant digits; fy0_printed restored to the page value |
| research_and_development | NOTE | agree | page value 73500000 vs API 73500000 |
| diluted_eps | mapped-sample | agree | page value 10.17 vs printed 10.17 |
| accounts_receivable | mapped-sample | agree | page value 294000000 vs printed 294000000 |
| accounts_payable | mapped-sample | agree | page value 182200000 vs printed 182200000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cfo | mapped-sample | agree | page value 402000000 vs printed 402000000 |
| depreciation_and_amortization | component sum | agree | page value 56800000 = printed 5.68e+07 at 4 significant digits; fy0_printed restored to the page value |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 200300000 vs printed 200300000 |
| shares_outstanding | component sum | agree | page value 33342823 vs printed 33342823 |
