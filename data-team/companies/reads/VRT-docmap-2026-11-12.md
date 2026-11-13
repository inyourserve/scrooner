# VRT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001674101-26-000008 (CIK 0001674101, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001104659-20-032055 (CIK 0001674101, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001193125-19-072362 (CIK 0001674101, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0001674101.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 10229900000 | 10229900000 | 8011800000 | 8011800000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 6514700000 | 6514700000 | 5077600000 | 5077600000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (927 tags across all 103 R pages, face and notes) of 0001674101-26-000008; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (927 tags across all 103 R pages, face and notes) of 0001674101-26-000008; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 1617800000 | 1617800000 | 1374000000 | 1374000000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R86.htm | OTHER FINANCIAL INFORMATION - Schedule of Expense in Earnings (Details) |  | 441700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R86.htm 'OTHER FINANCIAL INFORMATION - Schedule of Expense in Earnings (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating profit (loss) | 1829700000 | 1829700000 | 1367400000 | 1367400000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense, net | 86100000 | 86100000 | 150400000 | 150400000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (loss) before income taxes | 1741900000 | 1741900000 | 765400000 | 765400000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 409100000 | 409100000 | 269600000 | 269600000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (loss) | 1332800000 | 1332800000 | 495800000 | 495800000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (USD per share) | 3.49 | 3.49 | 1.32 | 1.32 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (USD per share) | 3.41 | 3.41 | 1.28 | 1.28 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 381712181 | 381712181 | 376418933 | 376418933 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 390652824 | 390652824 | 386325058 | 386325058 | Y | FILING-CHECKED | accn 0001674101-26-000008 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1728400000 | 1728400000 | 1227600000 | 1227600000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, less allowances of $25.6 and $22.4, respectively | 3109000000 | 3109000000 | 2362700000 | 2362700000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1456500000 | 1456500000 | 1244400000 | 1244400000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 6819500000 | 6819500000 | 5101800000 | 5101800000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 921800000 | 921800000 | 625100000 | 625100000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2033700000 | 2033700000 | 1321100000 | 1321100000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 12212400000 | 12212400000 | 9132500000 | 9132500000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 1756400000 | 1756400000 | 1316400000 | 1316400000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 4407000000 | 4407000000 | 3097000000 | 3097000000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 8271100000 | 8271100000 | 6698200000 | 6698200000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total equity | 3941300000 | 3941300000 | 2434300000 | 2434300000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used for) operating activities | 2113800000 | 2113800000 | 1319300000 | 1319300000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used for) investing activities | -1500800000 | -1500800000 | -201700000 | -201700000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used for) financing activities | -72300000 | -72300000 | -652100000 | -652100000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -220000000 | 220000000 | -167000000 | 167000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets | R7.htm | Depreciation + Amortization | 308600000 | 308600000 | 277000000 | 277000000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 45900000 | 45900000 | 34600000 | 34600000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividend payment | -66600000 | 66600000 | -42200000 | 42200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | 0 | 0 | -599900000 | 599900000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid during the year for interest | 126700000 | 126700000 | 155500000 | 155500000 | Y | FILING-CHECKED | accn 0001674101-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R84.htm | INCOME TAXES - Schedule of Income Taxes Paid Net of Refunds Received (Details) |  | 428200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'INCOME TAXES - Schedule of Income Taxes Paid Net of Refunds Received (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current portion of long-term debt + Long-term debt, net | 2913000000 | 2913000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock shares outstanding (in shares) | 382553680 | 382553680 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- revenue: era 10-K 0001104659-20-032055 R4.htm prints 'Revenues' on us-gaap:Revenues = 0 (FILING-CHECKED)
- sga_expense: era 10-K 0001104659-20-032055 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = -7743002 (FILING-CHECKED)
- net_income: era 10-K 0001193125-19-072362 R4.htm prints 'Net Income/ (loss)' on us-gaap:NetIncomeLoss = 5030748 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+vrt:AmortizationOfIntangibleAssetsExcludingCostsOfSales+us-gaap:RestructuringCharges+us-gaap:ForeignCurrencyTransactionGainLossBeforeTax+us-gaap:OtherOperatingIncomeExpenseNet (R3.htm): 2026-11-12 R3.htm: corrected: 1,617.8 + 200.4 + 54.5 + 12.0 + 0.8 = 1,885.5 = 10,229.9 - 6,514.7 - 1,829.7
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R86.htm): 2026-11-12 R86.htm: agree: R86 'Research and development' expense in earnings, the total
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AmortizationOfIntangibleAssets (R7.htm): 2026-11-12 R7.htm: agree: CF R7 depreciation + amortization
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R84.htm): 2026-11-12 R84.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: not_presented  (R5.htm): 2026-11-12 R5.htm: HELD per finance-lease ruling (founder 2026-11-04 item 5) and Dhairya 2026-11-12: reason finance_lease_total_not_disclosed; R16 says 'Finance leases are immaterial' and gives no amount; the BS line 'Op
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic (USD per share)' is the basic_eps line, printed 3.49 = filing XBRL 3.49; agrees
- inventory: mapped us-gaap:InventoryNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Inventories' is the inventory line, printed 1456500000 = filing XBRL 1456500000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total current liabilities' is the current_liabilities line, printed 4407000000 = filing XBRL 4407000000; agrees
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Net cash provided by (used for) operating activiti' is the cfo line, printed 2113800000 = filing XBRL 2113800000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Net cash provided by (used for) financing activiti' is the cash_flow_financing line, printed -72300000 = filing XBRL -72300000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Capital expenditures' is the capex line, printed -220000000 = filing XBRL 220000000; agrees
