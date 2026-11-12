# COO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-25-055615 (CIK 0000711404, filed 2025-12-05): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000711404-15-000021 (CIK 0000711404, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000711404-17-000044 (CIK 0000711404, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000711404-18-000047 (CIK 0000711404, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000711404.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 4092400000 | 4092400000 | 3895400000 | 3895400000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 1410300000 | 1410300000 | 1299700000 | 1299700000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 2682100000 | 2682100000 | 2595700000 | 2595700000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:AmortizationOfIntangibleAssets | R3.htm | Selling, general and administrative expense + Research and development expense + Amortization of intangibles | 1999200000 | 1999200000 | 1890000000 | 1890000000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expense | 1627800000 | 1627800000 | 1533700000 | 1533700000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development expense | 172200000 | 172200000 | 155100000 | 155100000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 682900000 | 682900000 | 705700000 | 705700000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 100000000 | 100000000 | 114300000 | 114300000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 566500000 | 566500000 | 582300000 | 582300000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes (Note 6) | 191600000 | 191600000 | 190000000 | 190000000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 374900000 | 374900000 | 392300000 | 392300000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 1.88 | 1.88 | 1.97 | 1.97 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 1.87 | 1.87 | 1.96 | 1.96 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 199100000 | 199100000 | 198900000 | 198900000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 200000000 | 200000000 | 200400000 | 200400000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R3.htm period ..2025-10-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 110600000 | 110600000 | 107600000 | 107600000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Trade accounts receivable, net of allowance for credit losses of $51.9 at October 31, 2025 and $43.5 at October 31, 2024 | 829000000 | 829000000 | 717000000 | 717000000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories (Note 1) | 846000000 | 846000000 | 802700000 | 802700000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 2106400000 | 2106400000 | 1951500000 | 1951500000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R6.htm | Property, plant and equipment, net | 2082000000 | 2082000000 | 1863400000 | 1863400000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill (Note 4) | 3853400000 | 3853400000 | 3838400000 | 3838400000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 12394800000 | 12394800000 | 12315200000 | 12315200000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 300400000 | 300400000 | 260500000 | 260500000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1112800000 | 1112800000 | 1022800000 | 1022800000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 4155700000 | 4155700000 | 4.232e+09 | 4231600000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Cooper stockholders' equity | 8238900000 | 8238900000 | 8083400000 | 8083400000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R6.htm period ..2025-10-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided by operating activities | 796100000 | 796100000 | 709300000 | 709300000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash used in investing activities | -372900000 | -372900000 | -764600000 | -764600000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash provided (used in) by financing activities | -425900000 | -425900000 | 39200000 | 39200000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Purchases of property, plant and equipment | -362400000 | 362400000 | -421200000 | 421200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation and amortization | 377400000 | 377400000 | 375100000 | 375100000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Share-based compensation expense | 70500000 | 70500000 | 75100000 | 75100000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Dividends on common stock | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Repurchase of common stock | -290100000 | 290100000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Interest | 115100000 | 115100000 | 134800000 | 134800000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R10.htm | Income taxes | 100000000 | 100000000 | 78400000 | 78400000 | Y | FILING-CHECKED | accn 0001628280-25-055615 R10.htm period ..2025-10-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Short-term debt (Note 5) + Long-term debt (Note 5) | 2505300000 | 2505300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, outstanding (in shares) | 195900000 | 195900000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-10-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 1797060000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 726798000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1070262000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Selling, general and administrative expense + Research and development expense +' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:AmortizationOfIntangibleAss = 833591000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Selling, general and administrative expense' on us-gaap:SellingGeneralAndAdministrativeExpense = 712543000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Research and development expense' on us-gaap:ResearchAndDevelopmentExpense = 69589000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 236671000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 18103000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 215485000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 10341000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Net income attributable to Cooper stockholders' on us-gaap:NetIncomeLoss = 203523000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Earnings per share attributable to Cooper stockholders - basic' on us-gaap:EarningsPerShareBasic = 4.2 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Earnings per share attributable to Cooper stockholders - diluted' on us-gaap:EarningsPerShareDiluted = 4.14 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 48452000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000711404-15-000021 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 49179000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 16426000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Trade accounts receivable, net of allowance for doubtful accounts of $5,956 at O' on us-gaap:AccountsReceivableNetCurrent = 282918000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 419692000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 841818000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 967097000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 2197077000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Total assets' on us-gaap:Assets = 4460610000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 116912000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 569172000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 1786706000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000711404-15-000021 R5.htm prints 'Total Cooper stockholders' equity' on us-gaap:StockholdersEquity = 2667509000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 390970000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -287947000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -106677000 (FILING-CHECKED)
- capex: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -243023000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Depreciation and amortization expense' on us-gaap:DepreciationDepletionAndAmortization = 191403000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 32879000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Dividends on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -2906000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -67304000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Interest, net of amounts capitalized' on us-gaap:InterestPaidNet = 14035000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000711404-15-000021 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 12167000 (FILING-CHECKED)
- revenue: era 10-K 0000711404-17-000044 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 2139000000 (FILING-CHECKED)
- revenue: era 10-K 0000711404-18-000047 R2.htm prints 'Net sales' on us-gaap:Revenues = 2532800000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0000711404-18-000047 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 18800000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 1999200000 vs printed 1999200000 |
| sga_expense | mapped-sample | agree | page value 1627800000 vs printed 1627800000 |
| accounts_receivable | mapped-sample | agree | page value 829000000 vs printed 829000000 |
| goodwill | mapped-sample | agree | page value 3853400000 vs printed 3853400000 |
| total_assets | mapped-sample | agree | page value 12394800000 vs printed 12394800000 |
| total_debt | component sum | agree | page value 2505300000 vs printed 2505300000 |
