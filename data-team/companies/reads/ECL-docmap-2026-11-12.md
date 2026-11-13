# ECL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-018357 (CIK 0000031462, filed 2026-02-23): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001558370-16-003581 (CIK 0000031462, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001558370-18-000999 (CIK 0000031462, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001558370-21-001916 (CIK 0000031462, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000031462.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net sales | 16081200000 | 16081200000 | 15741400000 | 15741400000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of sales (including special charges (a)) | 8930800000 | 8930800000 | 8899700000 | 8899700000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1216 tags across all 97 R pages, face and notes) of 0001104659-26-018357; no face row matched |
| operating_expenses | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1216 tags across all 97 R pages, face and notes) of 0001104659-26-018357; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 4257900000 | 4257900000 | 4228200000 | 4228200000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R84.htm | RESEARCH AND DEVELOPMENT EXPENDITURES (Details) |  | 202000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'RESEARCH AND DEVELOPMENT EXPENDITURES (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income | 2737600000 | 2737600000 | 2802400000 | 2802400000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| interest_expense | mapped | ecl:InterestExpenseNet | R2.htm | Interest expense, net | 241100000 |  | 282500000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income taxes | 2547900000 | 2547900000 | 2571200000 | 2571200000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 454600000 | 454600000 | 439300000 | 439300000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income attributable to Ecolab | 2075600000 | 2075600000 | 2112400000 | 2112400000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic (in dollars per share) | 7.33 | 7.33 | 7.43 | 7.43 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted EPS (in dollars per share) | 7.28 | 7.28 | 7.37 | 7.37 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic (in shares) | 283300000 | 283300000 | 284300000 | 284300000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted (in shares) | 285200000 | 285200000 | 286600000 | 286600000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 646200000 | 646200000 | 1256800000 | 1256800000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 3249400000 | 3249400000 | 2865000000 | 2865000000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1490400000 | 1490400000 | 1464900000 | 1464900000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 5955600000 | 5955600000 | 6025700000 | 6025700000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 4276600000 | 4276600000 | 3752400000 | 3752400000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 9227000000 | 9227000000 | 7907300000 | 7907300000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 24696300000 | 24696300000 | 22387800000 | 22387800000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2071000000 | 2071000000 | 1810000000 | 1810000000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 5534700000 | 5534700000 | 4792800000 | 4792800000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 14891800000 | 14891800000 | 13598600000 | 13598600000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Ecolab shareholders' equity | 9770800000 | 9770800000 | 8757300000 | 8757300000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash provided by operating activities | 2952600000 | 2952600000 | 2813900000 | 2813900000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Cash used for investing activities | -2707200000 | -2707200000 | -433800000 | -433800000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Cash used for financing activities | -853300000 | -853300000 | -2024100000 | -2024100000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -1048300000 | 1048300000 | -994500000 | 994500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation | 672600000 | 672600000 | 634900000 | 634900000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 136600000 | 136600000 | 134800000 | 134800000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -753600000 | 753600000 | -664300000 | 664300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Reacquired shares | -783800000 | 783800000 | -986500000 | 986500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Net interest paid | 302600000 | 302600000 | 342600000 | 342600000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R7.htm | Income taxes paid | 548100000 | 548100000 | 647400000 | 647400000 | Y | FILING-CHECKED | accn 0001104659-26-018357 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Short-term debt + Long-term debt | 8236300000 | 8236300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding | 282000000 | 282000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 13545100000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Cost of sales (including special charges of $80.6 in 2015, $14.3 in 2014 and $43' on us-gaap:CostOfGoodsAndServicesSold = 7223500000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 4345500000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001558370-16-003581 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1561300000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Interest expense, net (including special charges of $2.5 in 2013)' on ecl:InterestExpenseNet = 243600000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1317700000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 300500000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Net income attributable to Ecolab' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 1002100000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.38 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.32 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 296400000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001558370-16-003581 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 301400000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 92800000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 2390200000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 1388200000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 4447500000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 3228300000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 6490800000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Total assets' on us-gaap:Assets = 18641700000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 1.05e+09 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 4764400000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 11661300000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001558370-16-003581 R5.htm prints 'Total Ecolab shareholders' equity' on us-gaap:StockholdersEquity = 6909900000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1999800000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -915800000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -1150900000 (FILING-CHECKED)
- capex: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -771000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001558370-16-003581 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 78200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -400700000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Reacquired shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -755100000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 237200000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001558370-16-003581 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 533100000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-18-000999 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 13838300000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001558370-21-001916 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1161400000 (FILING-CHECKED)

## Mismatches (printed vs API)
- interest_expense: API missing (ecl:InterestExpenseNet)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:OtherNonrecurringIncomeExpense (R2.htm): 2026-11-12 R2.htm: corrected: 4,257.9 + 154.9 = 4,412.8 = 16,081.2 - 8,930.8 - 2,737.6
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R84.htm): 2026-11-12 R84.htm: agree: R84 'Research and development expenditures' 202, the total
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AdjustmentForAmortization (R7.htm): 2026-11-12 R7.htm: corrected: the tool took depreciation alone; CF R7 also prints amortization 303.8
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: agree: R5 lines on LongTermDebtAndCapitalLeaseObligations (leases inside by tag, finance-lease ruling (founder 2026-11-04 item 5))
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R2.htm): 2026-11-12 R2.htm: 20% mapped sample: IS R2.htm 'Net sales' is the revenue line, printed 16081200000 = filing XBRL 16081200000; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R2.htm): 2026-11-12 R2.htm: 20% mapped sample: IS R2.htm 'Basic (in shares)' is the weighted_basic_shares line, printed 283300000 = filing XBRL 283300000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current assets' is the current_assets line, printed 5955600000 = filing XBRL 5955600000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Cash used for investing activities' is the cash_flow_investing line, printed -2707200000 = filing XBRL -2707200000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Cash used for financing activities' is the cash_flow_financing line, printed -853300000 = filing XBRL -853300000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Share-based compensation expense' is the sbc line, printed 136600000 = filing XBRL 136600000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Dividends paid' is the dividends_paid line, printed -753600000 = filing XBRL 753600000; agrees
- interest_expense: combined: 'Interest expense, net' (custom ecl:InterestExpenseNet) is a net line: combined
