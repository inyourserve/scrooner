# ALB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000915913-26-000018 (CIK 0000915913, filed 2026-02-11): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000915913-16-000041 (CIK 0000915913, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000915913-18-000005 (CIK 0000915913, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000915913-20-000040 (CIK 0000915913, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000915913.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenues | 5142733000 | 5142733000 | 5377526000 | 5377526000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of goods sold | 4474014000 | 4474014000 | 5314987000 | 5314987000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 668719000 | 668719000 | 62539000 | 62539000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GoodwillImpairmentLoss+us-gaap:ImpairmentOfLongLivedAssetsToBeDisposedOf+alb:RestructuringChargesAndAssetWriteOffs+us-gaap:ResearchAndDevelopmentExpense+us-gaap:GainLossOnSaleOfBusiness | R3.htm | Selling, general and administrative expenses + Goodwill impairment + Long-lived asset impairment charges + Restructuring | 1035803000 |  | 1839084000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 550036000 | 550036000 | 618048000 | 618048000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development expenses | 51398000 | 51398000 | 86720000 | 86720000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating (loss) profit | -367084000 | -367084000 | -1776545000 | -1776545000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R90.htm | Long-Term Debt - Additional Information (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Long-Term Debt - Additional Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | (Loss) income before income taxes and equity in net income of unconsolidated investments | -552073000 | -552073000 | -1763825000 | -1763825000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 156881000 | 156881000 | 87085000 | 87085000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net (loss) income attributable to Albemarle Corporation | -510628000 | -510628000 | -1179449000 | -1179449000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings (loss) per share attributable to common shareholders (in dollars per share) | -5.76 | -5.76 | -11.2 | -11.2 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings (loss) per share attributable to common shareholders (in dollars per share) | -5.76 | -5.76 | -11.2 | -11.2 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted-average common shares outstanding—basic (in shares) | 117664000 | 117664000 | 117516000 | 117516000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted-average common shares outstanding—diluted (in shares) | 117664000 | 117664000 | 117516000 | 117516000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R6.htm | Cash and cash equivalents | 1618001000 | 1618001000 | 1192230000 | 1192230000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Trade accounts receivable, less allowance for credit losses (2025—$4,578; 2024—$5,201) | 593502000 | 593502000 | 742201000 | 742201000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 1179271000 | 1179271000 | 1502531000 | 1502531000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 4008139000 | 4008139000 | 3842262000 | 3842262000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R6.htm | Net property, plant and equipment | 8612411000 | 8612411000 | 9331470000 | 9331470000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1499657000 | 1499657000 | 1582714000 | 1582714000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 16374211000 | 16374211000 | 16609649000 | 16609649000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 779160000 |  | 793455000 |  | API missing | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1798044000 | 1798044000 | 1966464000 | 1966464000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R82.htm | Investments - Summary of Assets, Liabilities and Results of Operations for Significant Unconsolidated Joint Ventures (De |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R82.htm 'Investments - Summary of Assets, Liabilities and Results of Operations for Signi' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Albemarle Corporation shareholders’ equity | 9533365000 | 9533365000 | 9961517000 | 9961517000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided by operating activities | 1282267000 | 1282267000 | 687876000 | 687876000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash used in investing activities | -146007000 | -146007000 | -1584772000 | -1584772000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash (used in) provided by financing activities | -834187000 | -834187000 | 1241735000 | 1241735000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Capital expenditures | -589801000 | 589801000 | -1680529000 | 1680529000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation and amortization | 658678000 | 658678000 | 588638000 | 588638000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation and other | 40271000 | 40271000 | 32141000 | 32141000 | Y | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Dividends paid to common shareholders | -190530000 | 190530000 | -188530000 | 188530000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000915913-26-000018 R10.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R10.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1278 tags across all 143 R pages, face and notes) of 0000915913-26-000018; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R69.htm | Supplemental Cash Flow Information - Supplemental Information Related to Consolidated Statements of Cash Flows (Details) |  | 180705000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Supplemental Cash Flow Information - Supplemental Information Related to Consoli' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R69.htm | Supplemental Cash Flow Information - Supplemental Information Related to Consolidated Statements of Cash Flows (Details) |  | 152482000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Supplemental Cash Flow Information - Supplemental Information Related to Consoli' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current portion of long-term debt + Long-term debt | 3193541000 | 3193541000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, outstanding (in shares) | 117716000 | 117716000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3651335000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 2454463000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1196872000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Selling, general and administrative expenses + Research and development expenses' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:RestructuringSettlementAndI = 754437000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 512274000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Research and development expenses' on us-gaap:ResearchAndDevelopmentExpense = 102871000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Operating profit' on us-gaap:OperatingIncomeLoss = 442435000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000915913-16-000041 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Income from continuing operations before income taxes and equity in net income o' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 358187000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 29122000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Net income attributable to Albemarle Corporation' on us-gaap:NetIncomeLoss = 334906000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Basic earnings per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.01 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Diluted earnings per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Weighted-average common shares outstanding—basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 111182000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000915913-16-000041 R2.htm prints 'Weighted-average common shares outstanding—diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 111556000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 213734000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Trade accounts receivable, less allowance for doubtful accounts (2015—$4,148; 20' on us-gaap:AccountsReceivableNetCurrent = 552828000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 508728000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1831003000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 2484738000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 2893811000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Total assets' on us-gaap:Assets = 9615014000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 306517000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1616685000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000915913-16-000041 R4.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0000915913-16-000041 R4.htm prints 'Total Albemarle Corporation shareholders’ equity' on us-gaap:StockholdersEquity = 3254392000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 360689000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -2160552000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -478325000 (FILING-CHECKED)
- capex: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -227649000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 260076000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 15188000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000915913-16-000041 R7.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -119302000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000915913-16-000041 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000915913-16-000041 R7.htm read; no row matched (auto)
- revenue: era 10-K 0000915913-18-000005 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3071976000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000915913-18-000005 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 1961996000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000915913-20-000040 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 613110000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GoodwillImpairmentLoss+us-gaap:ImpairmentOfLongLivedAssetsToBeDisposedOf+alb:RestructuringChargesAndAssetWriteOffs+us-gaap:ResearchAndDevelopmentExpense+us-gaap:GainLossOnSaleOfBusiness)
- accounts_payable: API missing (us-gaap:AccountsPayableCurrent)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 1035803000 vs printed 1035803000 |
| research_and_development | mapped-sample | agree | page value 51398000 vs printed 51398000 |
| interest_expense | NOTE | agree | value 1100000 read off its own R page (no companyfacts fact to compare) |
| weighted_basic_shares | mapped-sample | agree | page value 117664000 vs printed 117664000 |
| accounts_receivable | mapped-sample | agree | page value 593502000 vs printed 593502000 |
| accounts_payable | mapped-sample | agree | page value 779160000 vs printed 779160000 |
| total_liabilities | NOTE | agree | value 2057303000 read off its own R page (no companyfacts fact to compare) |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 180705000 vs API 180705000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 152482000 vs API 152482000 |
| total_debt | component sum | agree | page value 3300337000 vs printed 3300337000 |
