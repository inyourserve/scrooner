# MOG-A document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-25-054103 (CIK 0000067887, filed 2025-11-26): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000067887-15-000081 (CIK 0000067887, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000067887-17-000087 (CIK 0000067887, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000067887-18-000053 (CIK 0000067887, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000067887.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Net sales | 3860624000 | 3860624000 | 3608960000 | 3608960000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 2794802000 | 2794802000 | 2589525000 | 2589525000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1057348000 | 1057348000 | 1012408000 | 1012408000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1112 tags across all 140 R pages, face and notes) of 0001628280-25-054103; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 553968000 | 553968000 | 501253000 | 501253000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 93671000 | 93671000 | 112773000 | 112773000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R131.htm | Segments (Operating Profit By Segment and Reconciliation to Consolidated Amounts) (Details) |  | 449606000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R131.htm 'Segments (Operating Profit By Segment and Reconciliation to Consolidated Amounts' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest | 72075000 | 72075000 | 66330000 | 66330000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before income taxes | 312648000 | 312648000 | 269746000 | 269746000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 77620000 | 77620000 | 60960000 | 60960000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 235028000 | 235028000 | 208786000 | 208786000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic | 7.42 | 7.42 | 6.53 | 6.53 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted | 7.33 | 7.33 | 6.45 | 6.45 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic | 31680280 | 31680280 | 31954689 | 31954689 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted | 32082601 | 32082601 | 32359338 | 32359338 | Y | FILING-CHECKED | accn 0001628280-25-054103 R3.htm period ..2025-09-27 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 62013000 | 62013000 | 58191000 | 58191000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R65.htm | Receivables (Narrative) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Receivables (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories, net | 914302000 | 914302000 | 924682000 | 924682000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 2369980000 | 2369980000 | 2385930000 | 2385930000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 1019906000 | 1019906000 | 988125000 | 988125000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 842313000 | 842313000 | 802089000 | 802089000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 4426055000 | 4426055000 | 4384020000 | 4384020000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 318402000 | 318402000 | 289160000 | 289160000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1119068000 | 1119068000 | 1006765000 | 1006765000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 2433500000 | 2433500000 | 2470974000 | 2470974000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders’ equity | 1992555000 | 1992555000 | 1913046000 | 1913046000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R5.htm period ..2025-09-27 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided (used) by operating activities | 273086000 | 273086000 | 197862000 | 197862000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided (used) by investing activities | -175256000 | -175256000 | -155592000 | -155592000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided (used) by financing activities | -98291000 | -98291000 | -48201000 | -48201000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property, plant and equipment | -144731000 | 144731000 | -151995000 | 151995000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R8.htm | Depreciation | 94013000 | 94013000 | 85878000 | 85878000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Equity-based compensation expense | 16708000 | 16708000 | 14959000 | 14959000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Payment of dividends | -36430000 | 36430000 | -35476000 | 35476000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchase of outstanding shares for treasury | -142707000 | 142707000 | -36738000 | 36738000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 70977000 | 70977000 | 65382000 | 65382000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid, net of refunds | 100347000 | 100347000 | 78482000 | 78482000 | Y | FILING-CHECKED | accn 0001628280-25-054103 R8.htm period ..2025-09-27 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current installments of long-term debt + Long-term debt, excluding current installments | 945686000 | 945686000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R6.htm | Common Stock, Shares, Outstanding | 31662305 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-09-27; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 2525532000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 1788828000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 736704000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 371498000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 132271000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000067887-15-000081 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Interest' on us-gaap:InterestExpense = 28967000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 183834000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 51951000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 131883000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 3.39 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 3.35 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 38945880 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000067887-15-000081 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 39334520 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 309853000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Receivables' on us-gaap:ReceivablesNetCurrent = 698419000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 493360000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1627495000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 536756000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 737212000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Total assets' on us-gaap:Assets = 3086471000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 165973000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 605505000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000067887-15-000081 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 2091939000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000067887-15-000081 R4.htm prints 'TOTAL SHAREHOLDERS' EQUITY' on us-gaap:StockholdersEquity = 994532000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 334546000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Net cash used by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -67598000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -165999000 (FILING-CHECKED)
- capex: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Purchase of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -80693000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000067887-15-000081 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Equity-based compensation expense' on us-gaap:ShareBasedCompensation = 5074000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000067887-15-000081 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Purchase of outstanding shares for treasury' on us-gaap:PaymentsForRepurchaseOfCommonStock = -363848000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Interest' on us-gaap:InterestPaid = 23718000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000067887-15-000081 R7.htm prints 'Income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 39890000 (FILING-CHECKED)
- revenue: era 10-K 0000067887-17-000087 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 2497524000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000067887-18-000053 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 36689000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | NOTE | agree | page value 449606000 vs API 449606000 |
| accounts_receivable | NOTE | agree | value 668021000 read off its own R page (no companyfacts fact to compare) |
| ppe_net | mapped-sample | agree | page value 1019906000 vs printed 1019906000 |
| cash_flow_financing | mapped-sample | agree | page value -98291000 vs printed -98291000 |
| depreciation_and_amortization | component sum | agree | page value 94013000 vs printed 94013000 |
| share_buybacks | mapped-sample | agree | page value -142707000 vs printed -142707000 |
| cash_paid_for_interest | mapped-sample | agree | page value 70977000 vs printed 70977000 |
| total_debt | component sum | agree | page value 945686000 vs printed 945686000 |
| shares_outstanding | component sum | agree | page value 31662305 vs printed 31662305 |
