# BWA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000908255-26-000011 (CIK 0000908255, filed 2026-02-11): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000908255-16-000077 (CIK 0000908255, filed FY2015 era): COVER R1.htm, BS R2.htm, IS R3.htm, CI R4.htm, CF R5.htm
- 10-K 0000908255-20-000014 (CIK 0000908255, era filing): COVER R1.htm, BS R2.htm, IS R3.htm, CI R4.htm, CF R5.htm
- 10-K 0000908255-18-000017 (CIK 0000908255, era filing): COVER R1.htm, BS R2.htm, IS R3.htm, CI R4.htm, CF R5.htm
- companyfacts CIK0000908255.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 14316000000 | 14316000000 | 14086000000 | 14086000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 11642000000 | 11642000000 | 11438000000 | 11438000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2674000000 | 2674000000 | 2648000000 | 2648000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringCharges+us-gaap:OtherOperatingIncomeExpenseNet+us-gaap:AssetImpairmentCharges | R5.htm | Selling, general and administrative expenses + Restructuring expense + Other operating expense (income), net + Impairmen | 2138000000 | 1920000000 | 2102000000 | 2038000000 | N (printed 2138000000 vs API 1920000000) | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 1304000000 | 1304000000 | 1350000000 | 1350000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R71.htm | RESEARCH AND DEVELOPMENT COSTS - Schedule of Research and Development Costs (Details) |  | 710000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R71.htm 'RESEARCH AND DEVELOPMENT COSTS - Schedule of Research and Development Costs (Det' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 536000000 | 536000000 | 546000000 | 546000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest expense, net | -39000000 | -39000000 | -20000000 | -20000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Earnings from continuing operations before income taxes and noncontrolling interest | 524000000 | 524000000 | 539000000 | 539000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 189000000 | 189000000 | 111000000 | 111000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net earnings attributable to BorgWarner Inc. | 277000000 | 277000000 | 338000000 | 338000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Earnings per share attributable to BorgWarner Inc. — basic (in dollar per share) | 1.29 | 1.29 | 1.51 | 1.51 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Earnings per share attributable to BorgWarner Inc. — diluted (in dollar per share) | 1.28 | 1.28 | 1.5 | 1.5 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 214200000 | 214200000 | 223500000 | 223500000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 216400000 | 216400000 | 224800000 | 224800000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | bwa:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsContinuingOperations | R3.htm | Cash and cash equivalents | 2313000000 |  | 2094000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Receivables, net | 2962000000 | 2962000000 | 2843000000 | 2843000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 1207000000 | 1207000000 | 1251000000 | 1251000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 6795000000 | 6795000000 | 6521000000 | 6521000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant and equipment, net | 3330000000 | 3330000000 | 3575000000 | 3575000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2055000000 | 2055000000 | 2357000000 | 2357000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 13769000000 | 13769000000 | 13993000000 | 13993000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrentAndNoncurrent | R3.htm | Accounts payable | 1996000000 | 1996000000 | 2032000000 | 2032000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 3282000000 | 3282000000 | 3646000000 | 3646000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 8155000000 | 8155000000 | 8287000000 | 8287000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total BorgWarner Inc. stockholders’ equity | 5442000000 | 5442000000 | 5532000000 | 5532000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R7.htm | Net cash provided by operating activities (see Note 25) | 1648000000 | 1648000000 | 1382000000 | 1382000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations | R7.htm | Net cash used in investing activities from continuing operations | -368000000 | -368000000 | -603000000 | -603000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations | R7.htm | Net cash used in financing activities from continuing operations | -1116000000 | -1116000000 | -167000000 | -167000000 | Y | FILING-CHECKED | accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures, including tooling outlays | -469000000 | 469000000 | -671000000 | 671000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R136.htm | REPORTING SEGMENTS AND RELATED INFORMATION - Schedule of Adjusted Operating Income (loss) (Details) |  | 719000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R136.htm 'REPORTING SEGMENTS AND RELATED INFORMATION - Schedule of Adjusted Operating Inco' (MetaLinks.json presentation); value from companyfacts same accession |
| sbc | mapped | us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation | R7.htm | Payments for stock-based compensation items | -22000000 | 22000000 | -23000000 | 23000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to BorgWarner stockholders | -119000000 | 119000000 | -98000000 | 98000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Payments for purchase of treasury stock | -508000000 | 508000000 | -402000000 | 402000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000908255-26-000011 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R139.htm | OPERATING CASH FLOWS AND OTHER SUPPLEMENTAL FINANCIAL INFORMATION (Details) |  | 133000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R139.htm 'OPERATING CASH FLOWS AND OTHER SUPPLEMENTAL FINANCIAL INFORMATION (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R80.htm | INCOME TAXES - Schedule of Geographical Information (Details) |  | 372000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R80.htm 'INCOME TAXES - Schedule of Geographical Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Notes payable and other short-term debt + Long-term debt | 3899000000 | 3899000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock outstanding (in shares) | 207057271 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 8023200000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 6320100000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Gross profit' on us-gaap:GrossProfit = 1703100000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Selling, general and administrative expenses + Other expense, net' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:OtherOperatingIncomeExpenseNet = 763400000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 662000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000908255-16-000077 R3.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 939700000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Interest expense and finance charges' on us-gaap:InterestAndDebtExpense = 60400000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Earnings before income taxes and noncontrolling interest' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 926800000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 280400000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Net earnings attributable to BorgWarner Inc.' on us-gaap:NetIncomeLoss = 609700000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Earnings per share — basic' on us-gaap:EarningsPerShareBasic = 2.72 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Earnings per share — diluted' on us-gaap:EarningsPerShareDiluted = 2.7 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 224414000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000908255-16-000077 R3.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 225648000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Cash' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 577700000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 1665000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 723600000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3135300000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2448100000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1757700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Total assets' on us-gaap:Assets = 8841500000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 1866400000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2357300000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000908255-16-000077 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0000908255-16-000077 R2.htm prints 'Total BorgWarner Inc. stockholders’ equity' on us-gaap:StockholdersEquity = 3553700000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 867900000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1759100000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 736600000 (FILING-CHECKED)
- capex: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Capital expenditures, including tooling outlays' on us-gaap:PaymentsToAcquireProductiveAssets = -577300000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 320200000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 40200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Dividends paid to BorgWarner stockholders' on us-gaap:PaymentsOfDividendsCommonStock = -116700000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Payments for purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -349800000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Interest' on us-gaap:InterestPaidNet = 70200000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000908255-16-000077 R5.htm prints 'Income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 183800000 (FILING-CHECKED)
- revenue: era 10-K 0000908255-20-000014 R3.htm prints 'Net sales' on us-gaap:Revenues = 10168000000 (FILING-CHECKED)
- ppe_net: era 10-K 0000908255-20-000014 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2925000000 (FILING-CHECKED)
- accounts_payable: era 10-K 0000908255-20-000014 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 1977000000 (FILING-CHECKED)
- sbc: era 10-K 0000908255-20-000014 R5.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 42000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000908255-18-000017 R3.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 7679200000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: N (printed 2138000000 vs API 1920000000) (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringCharges+us-gaap:OtherOperatingIncomeExpenseNet+us-gaap:AssetImpairmentCharges)
- cash_and_equivalents: API missing (bwa:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsContinuingOperations)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 2138000000 vs printed 2138000000 |
| research_and_development | NOTE | agree | page value 710000000 vs API 710000000 |
| interest_expense | combined | agree | page value -39000000 vs printed -39000000 |
| weighted_basic_shares | mapped-sample | agree | page value 214200000 vs printed 214200000 |
| goodwill | mapped-sample | agree | page value 2055000000 vs printed 2055000000 |
| cash_flow_investing | mapped-sample | agree | page value -368000000 vs printed -368000000 |
| capex | mapped-sample | agree | page value -469000000 vs printed -469000000 |
| depreciation_and_amortization | NOTE | agree | page value 719000000 vs API 719000000 |
| cash_paid_for_interest | NOTE | agree | page value 133000000 vs API 133000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 372000000 vs API 372000000 |
| total_debt | component sum | agree | page value 3899000000 vs printed 3899000000 |
| shares_outstanding | component sum | agree | page value 207057271 vs printed 207057271 |
