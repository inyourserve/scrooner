# JKHY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000779152-26-000067 (CIK 0000779152, filed 2026-08-28): COVER R1.htm, IS R2.htm, BS R3.htm, CF R5.htm
- 10-K 0000779152-15-000056 (CIK 0000779152, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R6.htm
- 10-K 0000779152-18-000060 (CIK 0000779152, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R6.htm
- 10-K 0000779152-17-000040 (CIK 0000779152, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R6.htm
- companyfacts CIK0000779152.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | REVENUE | 2544339000 | 2544339000 | 2375288000 | 2375288000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R2.htm | Cost of Revenue | 1433651000 | 1433651000 | 1360747000 | 1360747000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R69.htm | Reportable Segment Information Reconciliation of Operating Profit by Segment to Consolidated (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Reportable Segment Information Reconciliation of Operating Profit by Segment to ' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R2.htm | Total Expenses | 1909306000 | 1909306000 | 1806573000 | 1806573000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, General, and Administrative | 299210000 | 299210000 | 283055000 | 283055000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R2.htm | Research and Development | 176445000 | 176445000 | 162771000 | 162771000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | OPERATING INCOME | 635033000 | 635033000 | 568715000 | 568715000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R2.htm | Interest Expense | 5387000 | 5387000 | 10438000 | 10438000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | INCOME BEFORE INCOME TAXES | 652790000 | 652790000 | 586036000 | 586036000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | PROVISION FOR INCOME TAXES | 150014000 | 150014000 | 130288000 | 130288000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | NET INCOME | 502776000 | 502776000 | 455748000 | 455748000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic earnings per share | 7 | 7 | 6.25 | 6.25 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted earnings per share | 6.98 | 6.98 | 6.24 | 6.24 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Weighted average shares outstanding for basic earnings per share | 71866000 | 71866000 | 72874000 | 72874000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Weighted average shares outstanding for diluted earnings per share | 72043000 | 72043000 | 73045000 | 73045000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R2.htm period ..2026-06-30 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and cash equivalents | 12056000 | 12056000 | 101953000 | 101953000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Receivables, net | 349111000 | 349111000 | 317977000 | 317977000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (709 tags across all 70 R pages, face and notes) of 0000779152-26-000067; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 649095000 | 649095000 | 681464000 | 681464000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | PROPERTY AND EQUIPMENT, net | 220470000 | 220470000 | 220964000 | 220964000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 827740000 | 827740000 | 804797000 | 804797000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3145711000 | 3145711000 | 3043970000 | 3043970000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 34935000 | 34935000 | 28186000 | 28186000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 556239000 | 556239000 | 535784000 | 535784000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1093762000 | 1093762000 | 913138000 | 913138000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 2051949000 | 2051949000 | 2130832000 | 2130832000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R3.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R5.htm | Net cash from operating activities | 761960000 | 761960000 | 641504000 | 641504000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash from investing activities | -277738000 | -277738000 | -232163000 | -232163000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash from financing activities | -574119000 | -574119000 | -345672000 | -345672000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R5.htm | Capital expenditures | -67103000 | 67103000 | -53358000 | 53358000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R5.htm | Depreciation | 42103000 | 42103000 | 43700000 | 43700000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Expense for stock-based compensation | 32460000 | 32460000 | 28392000 | 28392000 | Y | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R5.htm | Dividends paid | -170405000 | 170405000 | -164644000 | 164644000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R5.htm | Purchase of treasury stock | -448173000 | 448173000 | -35051000 | 35051000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000779152-26-000067 R5.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R53.htm | Debt Narrative (Details) |  | 4606000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R53.htm 'Debt Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R57.htm | Income Taxes - Income Taxes Paid (Details) |  | 38868000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R57.htm 'Income Taxes - Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Long-term debt | 40000000 | 40000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | CONSOLIDATED STATEMENTS OF CHANGES IN STOCKHOLDERS' EQUITY |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'CONSOLIDATED STATEMENTS OF CHANGES IN STOCKHOLDERS' EQUITY' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Total revenue' on us-gaap:Revenues = 1256190000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Total cost of sales' on us-gaap:CostOfRevenue = 720336000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000779152-15-000056 R2.htm prints 'GROSS PROFIT' on us-gaap:GrossProfit = 535854000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 217989000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000779152-15-000056 R2.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 57490000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 71495000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000779152-15-000056 R2.htm prints 'OPERATING INCOME' on us-gaap:OperatingIncomeLoss = 317865000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -1594000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000779152-15-000056 R2.htm prints 'INCOME BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 316440000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000779152-15-000056 R2.htm prints 'PROVISION FOR INCOME TAXES' on us-gaap:IncomeTaxExpenseBenefit = 105219000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000779152-15-000056 R2.htm prints 'NET INCOME' on us-gaap:NetIncomeLoss = 211221000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 2.6 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted = 2.59 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Basic weighted average shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 81353000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000779152-15-000056 R2.htm prints 'Diluted weighted average shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 81601000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 148313000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 245387000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 493499000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000779152-15-000056 R3.htm prints 'PROPERTY AND EQUIPMENT, net' on us-gaap:PropertyPlantAndEquipmentNet = 296332000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Goodwill' on us-gaap:Goodwill = 550366000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Total assets' on us-gaap:Assets = 1836835000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 9933000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 443611000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Total liabilities' on us-gaap:Liabilities = 845301000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000779152-15-000056 R3.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 991534000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Net cash from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 373790000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Net cash from investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -136984000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Net cash from financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -158870000 (FILING-CHECKED)
- capex: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -54409000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000779152-15-000056 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Expense for stock-based compensation' on us-gaap:ShareBasedCompensation = 10112000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -76410000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000779152-15-000056 R6.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -122691000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000779152-15-000056 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000779152-15-000056 R6.htm read; no row matched (auto)
- revenue: era 10-K 0000779152-18-000060 R2.htm prints 'REVENUE' on us-gaap:Revenues = 1536603000 (FILING-CHECKED)
- operating_expenses: era 10-K 0000779152-17-000040 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 244381000 (FILING-CHECKED)
- sga_expense: era 10-K 0000779152-17-000040 R2.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 69601000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | mapped-sample | agree | page value 1433651000 vs printed 1433651000 |
| gross_profit | NOTE | agree | value 463566000 read off its own R page (no companyfacts fact to compare) |
| operating_expenses | combined | agree | page value 1909306000 vs printed 1909306000 |
| weighted_diluted_shares | mapped-sample | agree | page value 72043000 vs printed 72043000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | mapped-sample | agree | page value 827740000 vs printed 827740000 |
| cash_flow_investing | mapped-sample | agree | page value -277738000 vs printed -277738000 |
| depreciation_and_amortization | component sum | agree | page value 42103000 vs printed 42103000 |
| cash_paid_for_interest | NOTE | agree | page value 4606000 vs API 4606000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 38868000 vs API 38868000 |
| total_debt | component sum | agree | page value 40000000 vs printed 40000000 |
