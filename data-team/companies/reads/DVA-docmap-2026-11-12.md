# DVA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000927066-26-000012 (CIK 0000927066, filed 2026-02-11): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001564590-16-013587 (CIK 0000927066, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000927066-20-000014 (CIK 0000927066, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000927066-18-000030 (CIK 0000927066, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000927066.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenues | 13643069000 | 13643069000 | 12815550000 | 12815550000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1156 tags across all 111 R pages, face and notes) of 0000927066-26-000012; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1156 tags across all 111 R pages, face and notes) of 0000927066-26-000012; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 11599454000 | 11599454000 | 10725067000 | 10725067000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | 1673630000 | 1673630000 | 1538341000 | 1538341000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1156 tags across all 111 R pages, face and notes) of 0000927066-26-000012; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 2043615000 | 2043615000 | 2090483000 | 2090483000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R83.htm | Long-Term Debt - Additional information (Detail) |  | 539924000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R83.htm 'Long-Term Debt - Additional information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 1346823000 | 1346823000 | 1530393000 | 1530393000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 293107000 | 293107000 | 279656000 | 279656000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to DaVita Inc. | 746803000 | 746803000 | 936342000 | 936342000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic net income | 10.06 | 10.06 | 11.02 | 11.02 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted net income | 9.84 | 9.84 | 10.73 | 10.73 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic shares (in shares) | 74227000 | 74227000 | 84991000 | 84991000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted shares (in shares) | 75885000 | 75885000 | 87274000 | 87274000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 676438000 | 676438000 | 794933000 | 794933000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable | 2414690000 | 2414690000 | 2146975000 | 2146975000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 160627000 | 160627000 | 134559000 | 134559000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 4058003000 | 4058003000 | 3746072000 | 3746072000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net of accumulated depreciation | 2812966000 | 2812966000 | 2940916000 | 2940916000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 7545095000 | 7545095000 | 7375216000 | 7375216000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Assets, Total | 17480103000 | 17480103000 | 17285268000 | 17285268000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 696148000 | 696148000 | 547200000 | 547200000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 3141634000 | 3141634000 | 2973410000 | 2973410000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 16321665000 | 16321665000 | 15193917000 | 15193917000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total DaVita Inc. shareholders' equity (deficit) | -651082000 | -651082000 | 121122000 | 121122000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net Cash Provided by (Used in) Operating Activities, Total | 1886500000 | 1886500000 | 2022038000 | 2022038000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash Provided by (Used in) Investing Activities, Total | -654949000 | -654949000 | -771429000 | -771429000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -1374780000 | -1374780000 | -816937000 | -816937000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Additions of property and equipment | -575864000 | 575864000 | -555443000 | 555443000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation and amortization | 715348000 | 715348000 | 723860000 | 723860000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 139953000 | 139953000 | 102788000 | 102788000 | Y | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R93.htm | Long-term Incentive Compensation and Shareholders’ Equity - Additional Information (Details) |  | 0 |  |  |  | FILING-CHECKED | not on the face statement; shown in R93.htm 'Long-term Incentive Compensation and Shareholders’ Equity - Additional Informati' (MetaLinks.json presentation); value from companyfacts same accession |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchase of treasury stock | -1308366000 | 1308366000 | -1385932000 | 1385932000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927066-26-000012 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R111.htm | Supplemental Cash Flow Information (Details) |  | 515497000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R111.htm | Supplemental Cash Flow Information (Details) |  | 176688000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt + Long-term debt | 10273189000 | 10273189000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 68549000 | 68549000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Total net revenues' on us-gaap:HealthCareOrganizationRevenue = 13781837000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Total operating expenses and charges' on us-gaap:CostsAndExpenses = 12611142000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-013587 R2.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 1452135000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1170695000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-013587 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 723136000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 295726000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Net income attributable to DaVita HealthCare Partners Inc.' on us-gaap:NetIncomeLoss = 269732000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Basic net income per share attributable to DaVita HealthCare Partners Inc.' on us-gaap:EarningsPerShareBasic = 1.27 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Diluted net income per share attributable to DaVita HealthCare Partners Inc.' on us-gaap:EarningsPerShareDiluted = 1.25 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 211867714 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-013587 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 216251807 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1499116000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Accounts receivable, less allowance of $264,144 and $242,674' on us-gaap:AccountsReceivableNetCurrent = 1724228000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 185575000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4503280000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2788740000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 9294479000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Total assets' on us-gaap:Assets = 18514875000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 513950000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2399138000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 12566637000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-013587 R4.htm prints 'Total DaVita HealthCare Partners Inc. shareholders' equity' on us-gaap:StockholdersEquity = 4870780000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1557200000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -881784000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -138970000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Additions of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -707998000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Depreciation and amortization' on dva:AdjustmentDepreciationAndAmortization = 638024000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 56664000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001564590-16-013587 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001564590-16-013587 R6.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -549935000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-013587 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-013587 R6.htm read; no row matched (auto)
- income_before_tax: era 10-K 0000927066-20-000014 R2.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1195439000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0000927066-18-000030 R6.htm prints 'Depreciation and amortization' on dva:AdjustmentDepreciationAndAmortization = 777485000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 11599454000 vs printed 11599454000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | NOTE | agree | page value 539924000 vs API 539924000 |
| weighted_basic_shares | mapped-sample | agree | page value 74227000 vs printed 74227000 |
| cash_flow_financing | mapped-sample | agree | page value -1374780000 vs printed -1374780000 |
| depreciation_and_amortization | combined | agree | page value 715348000 vs printed 715348000 |
| dividends_paid | NOTE | agree | page value 0 vs API 0 |
| cash_paid_for_interest | NOTE | agree | page value 515497000 vs API 515497000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 176688000 vs API 176688000 |
| total_debt | component sum | agree | page value 10273189000 vs printed 10273189000 |
| shares_outstanding | mapped-sample | agree | page value 68549000 vs printed 68549000 |
