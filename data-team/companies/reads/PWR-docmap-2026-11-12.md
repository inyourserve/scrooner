# PWR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001050915-26-000006 (CIK 0001050915, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001193125-16-485494 (CIK 0001050915, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001050915-18-000003 (CIK 0001050915, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001050915-24-000009 (CIK 0001050915, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0001050915.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues | 28479697000 | 28479697000 | 23672795000 | 23672795000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of services | 24204616000 | 24204616000 | 20162034000 | 20162034000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 4275081000 | 4275081000 | 3510761000 | 3510761000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| operating_expenses | component sum | pwr:IncomeLossFromEquityMethodInvestmentsIntegralUnconsolidatedAffiliates+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:BusinessCombinationContingentConsiderationArrangementsChangeInAmountOfContingentConsiderationLiability1 | R5.htm | Equity in earnings of integral unconsolidated affiliates + Selling, general and administrative expenses + Amortization o | -2663572000 |  | -2164293000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI; company extension tag, matched by printed label / accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | -2189209000 | 2189209000 | -1824754000 | 1824754000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1051 tags across all 112 R pages, face and notes) of 0001050915-26-000006; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1611509000 | 1611509000 | 1346468000 | 1346468000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest and other financing expenses | -261445000 | 261445000 | -202687000 | 202687000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1389505000 | 1389505000 | 1212030000 | 1212030000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 347588000 | 347588000 | 284747000 | 284747000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to common stock | 1028378000 | 1028378000 | 904824000 | 904824000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 6.91 | 6.91 | 6.16 | 6.16 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 6.8 | 6.8 | 6.03 | 6.03 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average basic shares outstanding (in shares) | 148790000 | 148790000 | 146929000 | 146929000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average diluted shares outstanding (in shares) | 151291000 | 151291000 | 150056000 | 150056000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 439508000 | 439508000 | 741960000 | 741960000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 6847091000 | 6847091000 | 5170935000 | 5170935000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 370372000 | 370372000 | 260181000 | 260181000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 9903417000 | 9903417000 | 7851033000 | 7851033000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 3455204000 | 3455204000 | 2700277000 | 2700277000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 7317228000 | 7317228000 | 5316443000 | 5316443000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 24926901000 | 24926901000 | 18683894000 | 18683894000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 4579458000 | 4579458000 | 3722343000 | 3722343000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 8716198000 | 8716198000 | 6028513000 | 6028513000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 15899027000 | 15899027000 | 11354177000 | 11354177000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 8938249000 | 8938249000 | 7317731000 | 7317731000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 2229970000 | 2229970000 | 2081196000 | 2081196000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -3830974000 | -3830974000 | -2294319000 | -2294319000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | 1274984000 | 1274984000 | -305636000 | -305636000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -609154000 | 609154000 | -604078000 | 604078000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R7.htm | Depreciation + Amortization of intangible assets | 910333000 | 910333000 | 742322000 | 742322000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Non-cash stock-based compensation | 181947000 | 181947000 | 150526000 | 150526000 | Y | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Payments of dividends | -60416000 | 60416000 | -54196000 | 54196000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -134555000 | 134555000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001050915-26-000006 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R111.htm | SUPPLEMENTAL CASH FLOW INFORMATION - Additional Supplemental Cash Flow Information (Details) |  | 217358000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'SUPPLEMENTAL CASH FLOW INFORMATION - Additional Supplemental Cash Flow Informati' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R111.htm | SUPPLEMENTAL CASH FLOW INFORMATION - Additional Supplemental Cash Flow Information (Details) |  | 347197000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'SUPPLEMENTAL CASH FLOW INFORMATION - Additional Supplemental Cash Flow Informati' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt + Long-term debt, net of current maturities | 5994906000 | 5994906000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 149577564 | 149577564 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Revenues' on us-gaap:SalesRevenueServicesNet = 7572436000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Cost of services (including depreciation)' on us-gaap:CostOfServices = 6648771000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 923665000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Selling, general and administrative expenses + Amortization of intangible assets' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:AssetImpairmentCharges = 686162000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 592863000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 237503000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -8024000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 228675000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 97472000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Net income attributable to common stock' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 310907000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Net income attributable to common stock' on us-gaap:EarningsPerShareBasicAndDiluted = 1.59 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Net income attributable to common stock' on us-gaap:EarningsPerShareBasicAndDiluted = 1.59 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Weighted average basic shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 195113000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-485494 R4.htm prints 'Weighted average diluted shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 195120000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 128771000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Accounts receivable, net of allowances of $5,226 and $6,174' on us-gaap:AccountsReceivableNetCurrent = 1621133000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 75285000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2277519000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Property and equipment, net of accumulated depreciation of $755,272 and $651,559' on us-gaap:PropertyPlantAndEquipmentNet = 1101959000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1552658000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Total assets' on us-gaap:Assets = 5213543000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 782134000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1203744000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2125728000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-485494 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 3085494000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Net cash provided by operating activities of continuing operations' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 618183000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Net cash used in investing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -307113000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Net cash used in financing activities of continuing operations' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -1217378000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Additions of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -209968000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-485494 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Non-cash stock-based compensation' on us-gaap:ShareBasedCompensation = 36939000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-485494 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Repurchase of common stock, including accelerated stock repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -1606361000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Interest paid related to continuing operations' on us-gaap:InterestPaid = -7087000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-485494 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = -130921000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001050915-18-000003 R4.htm prints 'Cost of services (including depreciation)' on us-gaap:CostOfServices = 8224618000 (FILING-CHECKED)
- interest_expense: era 10-K 0001050915-24-000009 R5.htm prints 'Interest and other financing expenses' on us-gaap:InterestExpense = -186913000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (pwr:IncomeLossFromEquityMethodInvestmentsIntegralUnconsolidatedAffiliates+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:BusinessCombinationContingentConsiderationArrangementsChangeInAmountOfContingentConsiderationLiability1)

## Hand checks 2026-11-12 (Ritwik cloud)
- operating_expenses: component sum pwr:IncomeLossFromEquityMethodInvestmentsIntegralUnconsolidatedAffiliates+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:AmortizationOfIntangibleAssets+us-gaap:BusinessCombinationContingentConsiderationArrangementsChangeInAmountOfContingentConsiderationLiability1 (R5.htm): 2026-11-12 R5.htm: agree: every face line between GP and OI; ties GP 4,275,081 - OI 1,611,509 (R5)
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets (R7.htm): 2026-11-12 R7.htm: agree: CF R7 depreciation + amortization of intangibles
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R111.htm): 2026-11-12 R111.htm: agree: value in the note is the full data point; agree
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R111.htm): 2026-11-12 R111.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R3.htm): 2026-11-12 R3.htm: agree: R3 current + long-term debt
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServicesSold (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Cost of services' is the cost_of_revenue line, printed 24204616000 = filing XBRL 24204616000; agrees
- gross_profit: mapped us-gaap:GrossProfit (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Gross profit' is the gross_profit line, printed 4275081000 = filing XBRL 4275081000; agrees
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Interest and other financing expenses' is the interest_expense line, printed -261445000 = filing XBRL 261445000; agrees
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Weighted average diluted shares outstanding (in sh' is the weighted_diluted_shares line, printed 151291000 = filing XBRL 151291000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total stockholders’ equity' is the stockholders_equity line, printed 8938249000 = filing XBRL 8938249000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Net cash provided by (used in) financing activitie' is the cash_flow_financing line, printed 1274984000 = filing XBRL 1274984000; agrees
