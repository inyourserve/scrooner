# HII document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001501585-26-000006 (CIK 0001501585, filed 2026-02-05): COVER R1.htm, IS R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001501585-16-000038 (CIK 0001501585, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- 10-K 0001501585-18-000006 (CIK 0001501585, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- 10-K 0001501585-22-000007 (CIK 0001501585, era filing): COVER R1.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001501585.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Sales and service revenues | 12484000000 | 12484000000 | 11535000000 | 11535000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales and services revenues | 7081000000 |  | 6500000000 |  | API missing | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (971 tags across all 96 R pages, face and notes) of 0001501585-26-000006; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (971 tags across all 96 R pages, face and notes) of 0001501585-26-000006; no face row matched |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative expenses | 977000000 | 977000000 | 973000000 | 973000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R46.htm | Summary of Significant Accounting Policies (Narrative) (Details) |  | 26000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R46.htm 'Summary of Significant Accounting Policies (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | 657000000 | 657000000 | 535000000 | 535000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | -105000000 | 105000000 | -95000000 | 95000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings (loss) before income taxes | 777000000 | 777000000 | 643000000 | 643000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Federal and foreign income taxes | 172000000 | 172000000 | 93000000 | 93000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings (loss) | 605000000 | 605000000 | 550000000 | 550000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings (loss) per share | 15.39 | 15.39 | 13.96 | 13.96 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings (loss) per share | 15.39 | 15.39 | 13.96 | 13.96 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted-average common shares outstanding (in shares) | 39300000 | 39300000 | 39400000 | 39400000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted-average diluted shares outstanding (in shares) | 39300000 | 39300000 | 39400000 | 39400000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R4.htm | Cash and cash equivalents | 774000000 | 774000000 | 831000000 | 831000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable, net | 339000000 | 339000000 | 212000000 | 212000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings | R4.htm | Inventoried costs | 219000000 | 219000000 | 208000000 | 208000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 3451000000 | 3451000000 | 3228000000 | 3228000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property, plant, and equipment, net | 3726000000 | 3726000000 | 3450000000 | 3450000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R4.htm | Goodwill | 2650000000 | 2650000000 | 2618000000 | 2618000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 12749000000 | 12749000000 | 12141000000 | 12141000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Trade accounts payable | 556000000 | 556000000 | 598000000 | 598000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 3045000000 | 3045000000 | 2991000000 | 2991000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R4.htm | Total liabilities | 7676000000 | 7676000000 | 7475000000 | 7475000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R4.htm | Total stockholders' equity | 5073000000 | 5073000000 | 4666000000 | 4666000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001501585-26-000006 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by (used in) operating activities | 1196000000 | 1196000000 | 393000000 | 393000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash provided by (used in) investing activities | -521000000 | -521000000 | -348000000 | -348000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used in) financing activities | -732000000 | -732000000 | 356000000 | 356000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Capital expenditure additions | -402000000 | 402000000 | -367000000 | 367000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R6.htm | Depreciation + Amortization of purchased intangibles | 329000000 | 329000000 | 326000000 | 326000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock-based compensation | 54000000 | 54000000 | 23000000 | 23000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Dividends paid | -213000000 | 213000000 | -206000000 | 206000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchases of common stock |  |  | -162000000 | 162000000 |  | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Cash paid for interest | 108000000 | 108000000 | 101000000 | 101000000 | Y | FILING-CHECKED | accn 0001501585-26-000006 R6.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R69.htm | Schedule of Income Taxes Paid (Refunded) (Table) (Details) |  | 96000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Schedule of Income Taxes Paid (Refunded) (Table) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R4.htm | Current portion of long-term debt + Long-term debt | 2700000000 |  |  |  | API missing | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Common stock, shares outstanding | 39241527 | 39241527 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Total sales and service revenues' on us-gaap:SalesRevenueNet = 7020000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Cost of product sales' on us-gaap:CostOfGoodsSold = 4319000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001501585-16-000038 R2.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 669000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001501585-16-000038 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Operating income (loss)' on us-gaap:OperatingIncomeLoss = 769000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -137000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Earnings (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 632000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Federal income taxes' on us-gaap:IncomeTaxExpenseBenefit = 228000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Net earnings (loss)' on us-gaap:NetIncomeLoss = 404000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Basic earnings (loss) per share' on us-gaap:EarningsPerShareBasic = 8.43 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Diluted earnings (loss) per share' on us-gaap:EarningsPerShareDiluted = 8.36 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Weighted-average common shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 47900000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001501585-16-000038 R2.htm prints 'Weighted-average diluted shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 48300000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 894000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 1074000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Inventoried costs, net' on us-gaap:InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings = 285000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2284000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Property, plant, and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1827000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Goodwill' on us-gaap:Goodwill = 956000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Total assets' on us-gaap:Assets = 6024000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableCurrent = 317000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1274000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Total liabilities' on us-gaap:Liabilities = 4534000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001501585-16-000038 R3.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1490000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 828000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -141000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -783000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Additions to property, plant, and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -188000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001501585-16-000038 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 43000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -81000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -232000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 96000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001501585-16-000038 R5.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 242000000 (FILING-CHECKED)
- revenue: era 10-K 0001501585-18-000006 R2.htm prints 'Total sales and service revenues' on us-gaap:SalesRevenueNet = 7441000000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001501585-22-000007 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 627000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001501585-22-000007 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 76000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- total_debt: API missing (us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | NOTE | agree | page value 26000000 vs API 26000000 |
| current_assets | mapped-sample | agree | page value 3451000000 vs printed 3451000000 |
| total_assets | mapped-sample | agree | page value 12749000000 vs printed 12749000000 |
| accounts_payable | mapped-sample | agree | page value 556000000 vs printed 556000000 |
| cash_flow_investing | mapped-sample | agree | page value -521000000 vs printed -521000000 |
| depreciation_and_amortization | component sum | agree | page value 329000000 vs printed 329000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 96000000 vs API 96000000 |
| total_debt | component sum | agree | page value 2700000000 vs printed 2700000000; us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent blank in the 2025-12-31 column on R4.htm (0) |
