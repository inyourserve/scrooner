# ELV document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001156039-26-000013 (CIK 0001156039, filed 2026-02-06): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001156039-16-000018 (CIK 0001156039, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001156039-24-000015 (CIK 0001156039, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0001156039.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 199125000000 | 199125000000 | 177011000000 | 177011000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of products sold | 21178000000 | 21178000000 | 19750000000 | 19750000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1206 tags across all 123 R pages, face and notes) of 0001156039-26-000013; no face row matched |
| operating_expenses | combined | us-gaap:BenefitsLossesAndExpenses | R5.htm | Total expenses | 192415000000 | 192415000000 | 169107000000 | 169107000000 | Y | FILING-CHECKED | printed total includes cost of revenue: combined, never opex / accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Operating expense | 20984000000 | 20984000000 | 20025000000 | 20025000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1206 tags across all 123 R pages, face and notes) of 0001156039-26-000013; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R114.htm | Segment Information - Financial Data by Reportable Segment (Details) |  | 7199000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R114.htm 'Segment Information - Financial Data by Reportable Segment (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | 1402000000 | 1402000000 | 1185000000 | 1185000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income tax expense | 6710000000 | 6710000000 | 7904000000 | 7904000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 1049000000 | 1049000000 | 1933000000 | 1933000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Shareholders’ net income | 5662000000 | 5662000000 | 5980000000 | 5980000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 25.28 | 25.28 | 25.81 | 25.81 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 25.21 | 25.21 | 25.68 | 25.68 | Y | FILING-CHECKED | accn 0001156039-26-000013 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R111.htm | Shareholders’ Earnings per Share - Denominator for Basic and Diluted Earnings Per Share (Details) |  | 224000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Shareholders’ Earnings per Share - Denominator for Basic and Diluted Earnings Pe' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R111.htm | Shareholders’ Earnings per Share - Denominator for Basic and Diluted Earnings Per Share (Details) |  | 224600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Shareholders’ Earnings per Share - Denominator for Basic and Diluted Earnings Pe' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 9491000000 | 9491000000 | 8288000000 | 8288000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1206 tags across all 123 R pages, face and notes) of 0001156039-26-000013; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1206 tags across all 123 R pages, face and notes) of 0001156039-26-000013; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 63001000000 | 63001000000 | 58942000000 | 58942000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 4679000000 | 4679000000 | 4652000000 | 4652000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 28344000000 | 28344000000 | 28277000000 | 28277000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 121494000000 | 121494000000 | 116889000000 | 116889000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 7322000000 | 7322000000 | 6927000000 | 6927000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 41035000000 | 41035000000 | 40581000000 | 40581000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 77468000000 | 77468000000 | 75463000000 | 75463000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders’ equity | 43882000000 | 43882000000 | 41315000000 | 41315000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 4290000000 | 4290000000 | 5808000000 | 5808000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1344000000 | -1344000000 | -5167000000 | -5167000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | -1738000000 | -1738000000 | 1193000000 | 1193000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -1116000000 | 1116000000 | -1256000000 | 1256000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation and amortization | 1546000000 | 1546000000 | 1393000000 | 1393000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 276000000 | 276000000 | 191000000 | 191000000 | Y | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Cash dividends | -1529000000 | 1529000000 | -1508000000 | 1508000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase and retirement of common stock | -2605000000 | 2605000000 | -2900000000 | 2900000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001156039-26-000013 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R94.htm | Debt - Narrative (Details) |  | 1410000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R94.htm 'Debt - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R74.htm | Income Taxes - Narrative (Details) |  | 1367000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Short-term borrowings + Current portion of long-term debt + Long-term debt, less current portion | 32046000000 | 32046000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 220723898 | 220723898 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Total revenues' on us-gaap:Revenues = 79156500000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001156039-16-000018 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Total expenses' on us-gaap:BenefitsLossesAndExpenses = 74525500000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Total selling, general and administrative expense' on us-gaap:SellingGeneralAndAdministrativeExpense = 12534800000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001156039-16-000018 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 653000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Income from continuing operations before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4631000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 2071000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 2560000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Basic net income per share' on us-gaap:EarningsPerShareBasic = 9.73 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001156039-16-000018 R4.htm prints 'Diluted net income per share' on us-gaap:EarningsPerShareDiluted = 9.38 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001156039-16-000018 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001156039-16-000018 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2113500000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 30862100000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2019800000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 17562200000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Total assets' on us-gaap:Assets = 61717800000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 3318800000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 19092600000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 38673700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001156039-16-000018 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 23044100000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 4116000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1151500000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2997400000 (FILING-CHECKED)
- capex: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -638200000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001156039-16-000018 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 148200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Cash dividends' on us-gaap:PaymentsOfDividends = -656600000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001156039-16-000018 R6.htm prints 'Repurchase and retirement of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1515800000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001156039-16-000018 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001156039-16-000018 R6.htm read; no row matched (auto)
- interest_expense: era 10-K 0001156039-24-000015 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = 1030000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: combined us-gaap:BenefitsLossesAndExpenses (R5.htm): 2026-11-12 R5.htm: agree: 'Total expenses' includes benefit expense and cost of products: combined
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_income: mapped us-gaap:OperatingIncomeLoss (R114.htm): 2026-11-12 R114.htm: agree: R114 consolidated (non-dimensional) OperatingIncomeLoss 7,199,000,000; not printed on the IS
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R111.htm): 2026-11-12 R111.htm: agree: value in the note is the full data point; agree
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R111.htm): 2026-11-12 R111.htm: agree: value in the note is the full data point; agree
- accounts_receivable: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaid (R94.htm): 2026-11-12 R94.htm: agree: value in the note is the full data point; agree
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaid (R74.htm): 2026-11-12 R74.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: agree: R3 three debt lines
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServicesSold (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Cost of products sold' is the cost_of_revenue line, printed 21178000000 = filing XBRL 21178000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in dollars per share)' is the basic_eps line, printed 25.28 = filing XBRL 25.28; agrees
- total_liabilities: mapped us-gaap:Liabilities (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total liabilities' is the total_liabilities line, printed 77468000000 = filing XBRL 77468000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Purchases of property and equipment' is the capex line, printed -1116000000 = filing XBRL 1116000000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividends (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Cash dividends' is the dividends_paid line, printed -1529000000 = filing XBRL 1529000000; agrees
