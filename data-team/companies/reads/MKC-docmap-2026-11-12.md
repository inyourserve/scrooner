# MKC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000063754-26-000037 (CIK 0000063754, filed 2026-01-22): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000063754-16-000063 (CIK 0000063754, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000063754-18-000008 (CIK 0000063754, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000063754-23-000005 (CIK 0000063754, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000063754.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Net sales | 6840300000 | 6840300000 | 6723700000 | 6723700000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods sold | 4.248e+09 | 4248100000 | 4132700000 | 4132700000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 2592200000 | 2592200000 | 2591000000 | 2591000000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+mkc:SpecialCharges | R3.htm | Selling, general and administrative expense + Special charges | 1.521e+09 |  | 1530700000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expense | 1500300000 | 1500300000 | 1521200000 | 1521200000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R45.htm | Summary Of Significant Accounting Policies - Narrative (Details) |  | 106100000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R45.htm 'Summary Of Significant Accounting Policies - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 1070800000 | 1070800000 | 1060300000 | 1060300000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | 196200000 | 196200000 | 209400000 | 209400000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income from consolidated operations before income taxes | 913000000 | 913000000 | 898300000 | 898300000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 195800000 | 195800000 | 184000000 | 184000000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 789400000 | 789400000 | 788500000 | 788500000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings per share–basic (usd per share) | 2.94 | 2.94 | 2.94 | 2.94 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings per share–diluted (usd per share) | 2.93 | 2.93 | 2.92 | 2.92 | Y | FILING-CHECKED | accn 0000063754-26-000037 R3.htm period ..2025-11-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R90.htm | Capital Stock and Earnings Per Share (Reconciliation Of Average Shares Outstanding) (Details) |  | 268500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Capital Stock and Earnings Per Share (Reconciliation Of Average Shares Outstandi' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R90.htm | Capital Stock and Earnings Per Share (Reconciliation Of Average Shares Outstanding) (Details) |  | 269400000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Capital Stock and Earnings Per Share (Reconciliation Of Average Shares Outstandi' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 95900000 | 95900000 | 186100000 | 186100000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade accounts receivable, net of allowances | 628900000 | 628900000 | 587400000 | 587400000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1272000000 | 1272000000 | 1239900000 | 1239900000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 2138100000 | 2138100000 | 2139000000 | 2139000000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 1448800000 | 1448800000 | 1413000000 | 1413000000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 5301300000 | 5301300000 | 5227500000 | 5227500000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 13200400000 | 13200400000 | 13070300000 | 13070300000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R5.htm | Trade accounts payable | 1259400000 | 1259400000 | 1238100000 | 1238100000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 3062200000 | 3062200000 | 2882800000 | 2882800000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 7432300000 | 7432300000 | 7753500000 | 7753500000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Stockholders' Equity Attributable to Parent | 5736500000 | 5736500000 | 5291000000 | 5291000000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R5.htm period ..2025-11-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash flow provided by operating activities | 962200000 | 962200000 | 921900000 | 921900000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash flow used in investing activities | -255200000 | -255200000 | -269000000 | -269000000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash flow used in financing activities | -840900000 | -840900000 | -583100000 | -583100000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures (including software) | -221800000 | 221800000 | -274900000 | 274900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 231300000 | 231300000 | 208800000 | 208800000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 46200000 | 46200000 | 47400000 | 47400000 | Y | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -483000000 | 483000000 | -451000000 | 451000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Common stock acquired by purchase | -34800000 | 34800000 | -53100000 | 53100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000063754-26-000037 R7.htm period ..2025-11-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R96.htm | Supplemental Financial Statement Data (Supplemental Income Statement, Balance Sheet And Cash Flow Information) (Details) |  | 192800000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R96.htm 'Supplemental Financial Statement Data (Supplemental Income Statement, Balance Sh' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R96.htm | Supplemental Financial Statement Data (Supplemental Income Statement, Balance Sheet And Cash Flow Information) (Details) |  | 239600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R96.htm 'Supplemental Financial Statement Data (Supplemental Income Statement, Balance Sh' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings + Current portion of long-term debt + Long-term debt | 3996300000 | 3996300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in millions) | 2.684e+08 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-11-30; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 4296300000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 2559000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1737300000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Selling, general and administrative expense + Special charges + Loss on voluntar' on us-gaap:SellingGeneralAndAdministrativeExpense+mkc:SpecialCharges+us-gaap:DefinedBenefitPlanRecognizedNetGainLossDueToSe = 1188900000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Selling, general and administrative expense' on us-gaap:SellingGeneralAndAdministrativeExpense = 1127400000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000063754-16-000063 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 548400000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 53300000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Income from consolidated operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 496200000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1.313e+08 (FILING-CHECKED)
- net_income: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 401600000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Earnings per share–basic (usd per share)' on us-gaap:EarningsPerShareBasic = 3.14 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000063754-16-000063 R2.htm prints 'Earnings per share–diluted (usd per share)' on us-gaap:EarningsPerShareDiluted = 3.11 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000063754-16-000063 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000063754-16-000063 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 112600000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Trade accounts receivable, less allowances of $8.0 for 2015 and $4.0 for 2014' on us-gaap:AccountsReceivableNetCurrent = 455200000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Inventories' on us-gaap:InventoryGross = 710800000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1406500000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 618400000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1759300000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Total assets' on us-gaap:Assets = 4507800000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableTradeCurrent = 411900000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1240200000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 2820900000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000063754-16-000063 R4.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1686900000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 590000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -338900000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -199600000 (FILING-CHECKED)
- capex: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -128400000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 105900000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 18700000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -204900000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000063754-16-000063 R6.htm prints 'Common stock acquired by purchase' on us-gaap:PaymentsForRepurchaseOfCommonStock = -145800000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000063754-16-000063 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000063754-16-000063 R6.htm read; no row matched (auto)
- revenue: era 10-K 0000063754-18-000008 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 4834100000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000063754-18-000008 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 2823900000 (FILING-CHECKED)
- capex: era 10-K 0000063754-23-000005 R7.htm prints 'Capital expenditures (including expenditures for capitalized software)' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -262000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+mkc:SpecialCharges)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 1521400000 = printed 1.521e+09 at 4 significant digits; fy0_printed restored to the page value |
| research_and_development | NOTE | agree | page value 106100000 vs API 106100000 |
| basic_eps | mapped-sample | agree | page value 2.94 vs printed 2.94 |
| weighted_basic_shares | NOTE | agree | page value 268500000 vs API 268500000 |
| weighted_diluted_shares | NOTE | agree | page value 269400000 vs API 269400000 |
| total_assets | mapped-sample | agree | page value 13200400000 vs printed 13200400000 |
| cfo | mapped-sample | agree | page value 962200000 vs printed 962200000 |
| cash_paid_for_interest | NOTE | agree | page value 192800000 vs API 192800000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 239600000 vs API 239600000 |
| total_debt | component sum | agree | page value 3996300000 vs printed 3996300000 |
| shares_outstanding | component sum | DISAGREE | page value 14.9 vs printed 2.684e+08 |
