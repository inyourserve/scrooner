# CTAS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000723254-26-000028 (CIK 0000723254, filed 2026-07-29): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0000723254-15-000017 (CIK 0000723254, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000723254-18-000015 (CIK 0000723254, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0000723254-23-000025 (CIK 0000723254, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- companyfacts CIK0000723254.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 11264761000 | 11264761000 | 10340181000 | 10340181000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 5556968000 | 5556968000 | 5166017000 | 5166017000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R85.htm | Operating Segment Information - Schedule of Information Related to Operating Segments (Details) |  | 5707793000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R85.htm 'Operating Segment Information - Schedule of Information Related to Operating Seg' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (810 tags across all 87 R pages, face and notes) of 0000723254-26-000028; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling and administrative expenses | 3086145000 | 3086145000 | 2814438000 | 2814438000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (810 tags across all 87 R pages, face and notes) of 0000723254-26-000028; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 2606512000 | 2606512000 | 2359726000 | 2359726000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 106285000 | 106285000 | 101108000 | 101108000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 2505334000 | 2505334000 | 2264202000 | 2264202000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 505366000 | 505366000 | 451921000 | 451921000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 1999968000 | 1999968000 | 1812281000 | 1812281000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per share (in dollars per share) | 4.97 | 4.97 | 4.48 | 4.48 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per share (in dollars per share) | 4.91 | 4.91 | 4.4 | 4.4 | Y | FILING-CHECKED | accn 0000723254-26-000028 R3.htm period ..2026-05-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R74.htm | Earnings per Share - Schedule of Computation of EPS (Details) |  | 401267000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Earnings per Share - Schedule of Computation of EPS (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R74.htm | Earnings per Share - Schedule of Computation of EPS (Details) |  | 406197000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Earnings per Share - Schedule of Computation of EPS (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 289018000 | 289018000 | 263973000 | 263973000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, principally trade, less allowance of $31,648 and $26,357, respectively | 1555190000 | 1555190000 | 1417381000 | 1417381000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories, net | 446435000 | 446435000 | 447408000 | 447408000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 3853042000 | 3853042000 | 3436169000 | 3436169000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property and equipment, net | 1740501000 | 1740501000 | 1652474000 | 1652474000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 3544212000 | 3544212000 | 3400227000 | 3400227000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 10529140000 | 10529140000 | 9825241000 | 9825241000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 461157000 | 461157000 | 485109000 | 485109000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 2686959000 | 2686959000 | 1644502000 | 1644502000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (810 tags across all 87 R pages, face and notes) of 0000723254-26-000028; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total shareholders' equity | 5139887000 | 5139887000 | 4684481000 | 4684481000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R6.htm period ..2026-05-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 2276280000 | 2276280000 | 2165905000 | 2165905000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -568428000 | -568428000 | -623638000 | -623638000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1682072000 | -1682072000 | -1619011000 | -1619011000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -395105000 | 395105000 | -408884000 | 408884000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 318637000 | 318637000 | 303377000 | 303377000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 128076000 | 128076000 | 128329000 | 128329000 | Y | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -701485000 | 701485000 | -611627000 | 611627000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common stock | -952104000 | 952104000 | -934800000 | 934800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000723254-26-000028 R9.htm period ..2026-05-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R58.htm | Debt, Derivatives and Hedging Activities - Narrative (Details) |  | 106200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R58.htm 'Debt, Derivatives and Hedging Activities - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R66.htm | Income Taxes - Narrative (Details) |  | 402100000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R66.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Debt due within one year + Debt due after one year | 2428073000 | 2428073000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 400147000 | 400147000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-05-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Total revenue' on us-gaap:Revenues = 4476886000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000723254-15-000017 R2.htm read; no row matched (auto)
- gross_profit: FY2015 10-K 0000723254-15-000017 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Selling and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1224930000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 696407000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 65161000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 658276000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 658276000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 430618000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Basic earnings per share (dollars per share)' on us-gaap:EarningsPerShareBasic = 3.68 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000723254-15-000017 R2.htm prints 'Diluted earnings per share (dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.63 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000723254-15-000017 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000723254-15-000017 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 417073000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Accounts receivable, principally trade, less allowance of $15,674 and $14,906, r' on us-gaap:AccountsReceivableNetCurrent = 496130000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Inventories, net' on us-gaap:InventoryNet = 226211000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1735807000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Property and equipment, at cost, net' on us-gaap:PropertyPlantAndEquipmentNet = 871421000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 1195612000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Total assets' on us-gaap:Assets = 4192460000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 109607000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 621058000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000723254-15-000017 R5.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 1932455000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 580276000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 44987000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -712560000 (FILING-CHECKED)
- capex: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -217720000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000723254-15-000017 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 47002000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -201891000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000723254-15-000017 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -551970000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000723254-15-000017 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000723254-15-000017 R8.htm read; no row matched (auto)
- revenue: era 10-K 0000723254-18-000015 R2.htm prints 'Total revenue' on us-gaap:Revenues = 6476632000 (FILING-CHECKED)
- interest_expense: era 10-K 0000723254-23-000025 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = 111232000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: mapped us-gaap:GrossProfit (R85.htm): 2026-11-12 R85.htm: agree: R85 undimensioned total 5,707,793 = revenue 11,264,761 - cost of sales 5,556,968 (R3); not printed on the face
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:BusinessCombinationAcquisitionRelatedCosts (R3.htm): 2026-11-12 R3.htm: corrected: opex = 3,086,145 + 15,136 = 3,101,281 = 11,264,761 - 5,556,968 - 2,606,512 (thousands)
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R74.htm): 2026-11-12 R74.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R74.htm): 2026-11-12 R74.htm: agree: carrying sentence read: the note value is the full data point
- total_liabilities: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- depreciation_and_amortization: combined us-gaap:Depreciation (R9.htm): 2026-11-12 R9.htm: CF R9 prints depreciation 318,637 and 'Amortization of intangible assets and capitalized contract costs' 194,209; the second line bundles contract-cost amortization, which is not D&A: combined
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R58.htm): 2026-11-12 R58.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R66.htm): 2026-11-12 R66.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R6.htm): 2026-11-12 R6.htm: agree: R6 debt lines; no finance-lease facts in the filing
- sga_expense: mapped us-gaap:SellingGeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Selling and administrative expenses' is the sga_expense line, printed 3086145000 = filing XBRL 3086145000; agrees
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income taxes' is the income_tax_expense line, printed 505366000 = filing XBRL 505366000; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net income' is the net_income line, printed 1999968000 = filing XBRL 1999968000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total current assets' is the current_assets line, printed 3853042000 = filing XBRL 3853042000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Property and equipment, net' is the ppe_net line, printed 1740501000 = filing XBRL 1740501000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash used in investing activities' is the cash_flow_investing line, printed -568428000 = filing XBRL -568428000; agrees
