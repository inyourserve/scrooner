# AIT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000109563-26-000033 (CIK 0000109563, filed 2026-08-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000109563-15-000129 (CIK 0000109563, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000109563-16-000283 (CIK 0000109563, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000109563-25-000080 (CIK 0000109563, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, CF R6.htm
- companyfacts CIK0000109563.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 4966686000 | 4966686000 | 4563424000 | 4563424000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 3459901000 | 3459901000 | 3180265000 | 3180265000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1506785000 | 1506785000 | 1383159000 | 1383159000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, distribution, and administrative expense, including depreciation | 957316000 | 957316000 | 884630000 | 884630000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, distribution, and administrative expense, including depreciation | 957316000 | 957316000 | 884630000 | 884630000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (837 tags across all 88 R pages, face and notes) of 0000109563-26-000033; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 549469000 | 549469000 | 498529000 | 498529000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 17386000 | 17386000 | 18214000 | 18214000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 544274000 | 544274000 | 500967000 | 500967000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 129749000 | 129749000 | 107979000 | 107979000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 414525000 | 414525000 | 392988000 | 392988000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income per share — basic (in dollars per share) | 11.09 | 11.09 | 10.26 | 10.26 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income per share — diluted (in dollars per share) | 10.95 | 10.95 | 10.12 | 10.12 | Y | FILING-CHECKED | accn 0000109563-26-000033 R3.htm period ..2026-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R71.htm | SHAREHOLDERS’ EQUITY - Schedule of Earnings Per Share, Basic and Diluted (Details) |  | 37377000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R71.htm 'SHAREHOLDERS’ EQUITY - Schedule of Earnings Per Share, Basic and Diluted (Detail' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R71.htm | SHAREHOLDERS’ EQUITY - Schedule of Earnings Per Share, Basic and Diluted (Details) |  | 37857000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R71.htm 'SHAREHOLDERS’ EQUITY - Schedule of Earnings Per Share, Basic and Diluted (Detail' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsAndShortTermInvestments | R5.htm | Cash and cash equivalents | 127130000 | 127130000 | 388417000 | 388417000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable — net | 831244000 | 831244000 | 769699000 | 769699000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 508979000 | 508979000 | 505337000 | 505337000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1578729000 | 1578729000 | 1747473000 | 1747473000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property — net | 131651000 | 131651000 | 128154000 | 128154000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 704700000 | 704700000 | 699374000 | 699374000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 3009973000 | 3009973000 | 3175544000 | 3175544000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 341094000 | 341094000 | 280124000 | 280124000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 612411000 | 612411000 | 526151000 | 526151000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total Liabilities | 1148224000 | 1148224000 | 1331024000 | 1331024000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Shareholders’ Equity | 1861749000 | 1861749000 | 1844520000 | 1844520000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R5.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash provided by Operating Activities | 484082000 | 484082000 | 492385000 | 492385000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Cash used in Investing Activities | -33899000 | -33899000 | -318752000 | -318752000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Cash used in Financing Activities | -711539000 | -711539000 | -245607000 | -245607000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -23565000 | 23565000 | -27187000 | 27187000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| depreciation_and_amortization | mapped | us-gaap:Depreciation | R7.htm | Depreciation and amortization of property | 25875000 | 25875000 | 24899000 | 24899000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:RestrictedStockExpense | R7.htm | Other share-based compensation expense | 7385000 | 7385000 | 7289000 | 7289000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -72598000 | 72598000 | -63702000 | 63702000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchases of treasury shares | -317218000 | 317218000 | -152837000 | 152837000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest (includes interest rate swap settlements) | 18954000 | 18954000 | 21826000 | 21826000 | Y | FILING-CHECKED | accn 0000109563-26-000033 R7.htm period ..2026-06-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R64.htm | INCOME TAXES - Schedule of Components of Income Taxes Paid (Details) |  | 108946000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'INCOME TAXES - Schedule of Components of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | Long-term debt | 262300000 | 262300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 36803000 | 36803000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-06-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueNet = 2751561000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Cost of Sales' on us-gaap:CostOfGoodsAndServicesSold = 1981747000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Gross Profit' on us-gaap:GrossProfit = 769814000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Selling, Distribution and Administrative, including depreciation' on us-gaap:SellingGeneralAndAdministrativeExpense = 585195000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Selling, Distribution and Administrative, including depreciation' on us-gaap:SellingGeneralAndAdministrativeExpense = 585195000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 184619000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Interest Expense' on us-gaap:InterestExpense = 8121000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 175871000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Income Tax Expense' on us-gaap:IncomeTaxExpenseBenefit = 60387000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Net Income' on us-gaap:NetIncomeLoss = 115484000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Net Income Per Share — Basic' on us-gaap:EarningsPerShareBasic = 2.82 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000109563-15-000129 R2.htm prints 'Net Income Per Share — Diluted' on us-gaap:EarningsPerShareDiluted = 2.8 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000109563-15-000129 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000109563-15-000129 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashCashEquivalentsAndShortTermInvestments = 69470000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Accounts receivable, less allowances of $10,621 and $10,385' on us-gaap:AccountsReceivableNetCurrent = 376305000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 362419000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 859305000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Property — net' on us-gaap:PropertyPlantAndEquipmentNet = 104447000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 254406000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Total Assets' on us-gaap:Assets = 1434968000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 179825000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 310072000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Total Liabilities' on us-gaap:Liabilities = 693640000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000109563-15-000129 R4.htm prints 'Total Shareholders’ Equity' on us-gaap:StockholdersEquity = 741328000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Cash provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 154538000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Cash used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -173621000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Cash provided by (used in) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 24689000 (FILING-CHECKED)
- capex: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Property purchases' on us-gaap:PaymentsToAcquireProductiveAssets = -14933000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Depreciation and amortization of property' on us-gaap:Depreciation = 16578000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Other share-based compensation expense' on ait:OtherShareBasedCompensation = 2851000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -42663000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Purchases of treasury shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -76515000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Interest' on us-gaap:InterestPaid = 5851000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000109563-15-000129 R6.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 69272000 (FILING-CHECKED)
- revenue: era 10-K 0000109563-16-000283 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueNet = 2519428000 (FILING-CHECKED)
- interest_expense: era 10-K 0000109563-25-000080 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = 18214000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | mapped-sample | agree | page value 3459901000 vs printed 3459901000 |
| gross_profit | mapped-sample | agree | page value 1506785000 vs printed 1506785000 |
| operating_expenses | component sum | agree | page value 957316000 vs printed 957316000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| weighted_basic_shares | NOTE | agree | page value 37377000 vs API 37377000 |
| weighted_diluted_shares | NOTE | agree | page value 37857000 vs API 37857000 |
| cash_and_equivalents | mapped-sample | agree | page value 127130000 vs printed 127130000 |
| cash_flow_financing | mapped-sample | agree | page value -711539000 vs printed -711539000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 108946000 vs API 108946000 |
| total_debt | component sum | agree | page value 262300000 vs printed 262300000 |
