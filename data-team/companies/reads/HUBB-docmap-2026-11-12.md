# HUBB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-007500 (CIK 0000048898, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001628280-16-011342 (CIK 0000048898, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001628280-18-001740 (CIK 0000048898, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001628280-21-001868 (CIK 0000048898, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000048898.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 5844600000 | 5844600000 | 5628500000 | 5628500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods sold | 3780500000 | 3780500000 | 3722900000 | 3722900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 2064100000 | 2064100000 | 1905600000 | 1905600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling & administrative expenses | 855300000 | 855300000 | 812500000 | 812500000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001628280-26-007500 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling & administrative expenses | 855300000 | 855300000 | 812500000 | 812500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1089 tags across all 129 R pages, face and notes) of 0001628280-26-007500; no face row matched / check: hand R3.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 1208800000 | 1208800000 | 1093100000 | 1093100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest expense, net | -64100000 | -64100000 | -73800000 | -73800000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 1119100000 | 1119100000 | 1006800000 | 1006800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 227200000 | 227200000 | 222100000 | 222100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Hubbell Incorporated | 887100000 | 887100000 | 779000000 | 779000000 | Y | FILING-CHECKED | accn 0001628280-26-007500 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per share (USD per share) | 16.63 | 16.63 | 14.49 | 14.49 | Y | FILING-CHECKED | accn 0001628280-26-007500 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per share (USD per share) | 16.54 | 16.54 | 14.39 | 14.39 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R115.htm | Earnings Per Share (Details) | 53200000 | 53200000 | 53700000 |  | Y | FILING-CHECKED | not on the face statement; shown in R115.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R115.htm corrected: EPS note R115 prints Average number of common shares outstanding 53.2M (FY1 53.7M). |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R115.htm | Earnings Per Share (Details) | 53500000 | 53500000 | 54000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R115.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R115.htm corrected: EPS note R115 prints Average number of diluted shares outstanding 53.5M (FY1 54.0M). |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 482500000 | 482500000 | 329100000 | 329100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R6.htm | Accounts receivable (net of allowances of $13.9 and $11.3) | 856900000 | 856900000 | 756000000 | 756000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories, net | 1083800000 | 1083800000 | 1010400000 | 1010400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total Current Assets | 2594000000 | 2594000000 | 2257900000 | 2257900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, Plant, and Equipment, net | 841200000 | 841200000 | 726600000 | 726600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 3060800000 | 3060800000 | 2500800000 | 2500800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | TOTAL ASSETS | 8228800000 | 8228800000 | 6847700000 | 6847700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 570500000 | 570500000 | 541700000 | 541700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total Current Liabilities | 1508700000 | 1508700000 | 1274200000 | 1274200000 | Y | FILING-CHECKED | accn 0001628280-26-007500 R6.htm period ..2025-12-31 / check: hand R6.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | TOTAL LIABILITIES | 4370900000 | 4370900000 | 3437100000 | 3437100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Hubbell Incorporated Shareholders’ Equity | 3847900000 | 3847900000 | 3396200000 | 3396200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1029800000 | 1029800000 | 991200000 | 991200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | NET CASH USED IN INVESTING ACTIVITIES | -1094600000 | -1094600000 | -59100000 | -59100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | NET CASH PROVIDED BY (USED IN) FINANCING ACTIVITIES | 203600000 | 203600000 | -923400000 | -923400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Capital expenditures | -155100000 | 155100000 | -180400000 | 180400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 206100000 | 206100000 | 212100000 | 212100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 33000000 | 33000000 | 30600000 | 30600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsMinorityInterest | R8.htm | Payment of dividends | -286600000 | 286600000 | -267300000 | 267300000 | Y (sign differs: printed in parentheses) | FILING-CHECKED | common dividends mis-tagged as PaymentsOfDividendsMinorityInterest; label 'Payment of dividends', only dividend line, amount consistent with common dividends / check: hand R8.htm corrected: CF prints 'Payment of dividends' (286.6), FY1 (267.3), the only dividend line; tagged PaymentsOfDividendsMinorityInterest but the size fits common dividends (~53M shares x ~$5.4) while NCI earns only 4.8 -> printed line wins (rule 1). |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Acquisition of common shares | -225000000 | 225000000 | -40000000 | 40000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007500 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (1089 tags across all 129 R pages, face and notes) of 0001628280-26-007500; no face row matched / check: hand R8.htm agree |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R101.htm | Income Taxes - Schedule of Income Taxes Paid (Details) | 214300000 | 214300000 | 225300000 |  | Y | FILING-CHECKED | not on the face statement; shown in R101.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R101.htm corrected: Tax note R101 prints TOTAL CASH TAXES PAID 214.3M (FY1 225.3M). |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Short-term debt + Long-term Debt | 2325400000 | 2325400000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R6.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares, outstanding (in shares) | 53253805 | 53253805 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3390400000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsAndServicesSold = 2298600000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1091800000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Selling & administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 617200000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Selling & administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 617200000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 474600000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -31000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 418600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 136500000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-16-011342 R2.htm prints 'NET INCOME ATTRIBUTABLE TO HUBBELL' on us-gaap:NetIncomeLoss = 277300000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Basic (USD per share)' on us-gaap:EarningsPerShareBasic = 4.79 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-16-011342 R2.htm prints 'Diluted (USD per share)' on us-gaap:EarningsPerShareDiluted = 4.77 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-16-011342 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001628280-16-011342 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 343500000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 466600000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Inventories, net' on us-gaap:InventoryNet = 540000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 1387800000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Property, Plant, and Equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 419700000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 928500000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-16-011342 R5.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 3208700000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 289500000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 603100000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001628280-16-011342 R5.htm prints 'TOTAL LIABILITIES' on us-gaap:Liabilities = 1459700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-011342 R5.htm prints 'Total Hubbell Shareholders’ Equity' on us-gaap:StockholdersEquity = 1740600000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-011342 R7.htm prints 'NET CASH PROVIDED BY OPERATING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 331100000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-011342 R7.htm prints 'NET CASH USED IN INVESTING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -249200000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-011342 R7.htm prints 'NET CASH USED IN FINANCING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -371100000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-011342 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -77100000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-011342 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 85200000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-16-011342 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 17000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001628280-16-011342 R7.htm prints 'Acquisition of common shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -79100000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-011342 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001628280-18-001740 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3668800000 (FILING-CHECKED)
- interest_expense: era 10-K 0001628280-21-001868 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -60300000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001628280-21-001868 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 453500000 (FILING-CHECKED)
- cfo: era 10-K 0001628280-21-001868 R7.htm prints 'NET CASH PROVIDED BY OPERATING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 648000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001628280-21-001868 R7.htm prints 'NET CASH USED IN INVESTING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -328800000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 11 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 4.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
