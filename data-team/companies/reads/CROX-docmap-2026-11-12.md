# CROX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001334036-26-000006 (CIK 0001334036, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001047469-16-010591 (CIK 0001334036, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001628280-18-002437 (CIK 0001334036, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001334036-24-000025 (CIK 0001334036, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0001334036.json (one call); submissions CIK0001334036.json (SIC 3021).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 4040647000 | 4040647000 | 4102108000 | 4102108000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 1683592000 | 1683592000 | 1691850000 | 1691850000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 2357055000 | 2357055000 | 2410258000 | 2410258000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GoodwillImpairmentLoss+us-gaap:OtherAssetImpairmentCharges | R3.htm | Selling, general and administrative expense + Goodwill impairment + Asset impairments | 2207540000 | 2207540000 | 1388347000 | 1388347000 | Y | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expense | 1469425000 | 1469425000 | 1364265000 | 1364265000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R44.htm | Research, design and development expense | 29600000 | 29600000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R44.htm 'BASIS OF PRESENTATION AND SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES - Narrative' (MetaLinks.json presentation) |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Income from operations | 149515000 | 149515000 | 1021911000 | 1021911000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -88287000 | 88287000 | -109264000 | 109264000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 72978000 | 72978000 | 910585000 | 910585000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense (benefit) | 154176000 | 154176000 | -39486000 | -39486000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (loss) | -81198000 | -81198000 | 950071000 | 950071000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | -1.5 | -1.5 | 16 | 16 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | -1.5 | -1.5 | 15.88 | 15.88 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 54208000 | 54208000 | 59381000 | 59381000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 54208000 | 54208000 | 59832000 | 59832000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 130354000 | 130354000 | 180485000 | 180485000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowances of $28,136 and $31,579, respectively | 278191000 | 278191000 | 257657000 | 257657000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 368687000 | 368687000 | 356254000 | 356254000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 885883000 | 885883000 | 872269000 | 872269000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 238191000 | 238191000 | 244335000 | 244335000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 404689000 | 404689000 | 711491000 | 711491000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 4174750000 | 4174750000 | 4812153000 | 4812153000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 266090000 | 266090000 | 264901000 | 264901000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 700129000 | 700129000 | 740208000 | 740208000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 2881467000 | 2881467000 | 2976421000 | 2976421000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 1293283000 | 1293283000 | 1835732000 | 1835732000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Cash provided by operating activities | 710431000 | 710431000 | 992486000 | 992486000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Cash used in investing activities | -51231000 | -51231000 | -69347000 | -69347000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Cash used in financing activities | -714565000 | -714565000 | -886048000 | -886048000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, equipment, and software | -51231000 | 51231000 | -69347000 | 69347000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 79282000 | 79282000 | 69840000 | 69840000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 36701000 | 36701000 | 33053000 | 33053000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (833 tags across all 87 R pages, face and notes) of 0001334036-26-000006; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock, including excise taxes paid | -582320000 | 582320000 | -552451000 | 552451000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 77684000 | 77684000 | 99463000 | 99463000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001334036-26-000006 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R79.htm | Total | 185066000 | 185066000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R79.htm 'INCOME TAXES - Cash Paid For Income Taxes, Net of Refunds (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | Long-term borrowings | 1230885000 | 1230885000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common shares outstanding (in shares) | 50200000 | 50200000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Revenues' on us-gaap:SalesRevenueNet = 1090630000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 579825000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 510805000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Selling, general and administrative expenses + Restructuring charges + Asset imp' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringCharges+us-gaap:AssetImpairmentCharges = 583129000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 559095000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047469-16-010591 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Income (loss) from operations' on us-gaap:OperatingIncomeLoss = -72324000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -969000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -74744000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Income tax benefit (expense)' on us-gaap:IncomeTaxExpenseBenefit = -8452000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Net income (loss)' on us-gaap:NetIncomeLoss = -83196000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = -1.3 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-16-010591 R2.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = -1.3 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-16-010591 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001047469-16-010591 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 143341000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Accounts receivable, net of allowances of $49,364 and $32,392, respectively' on us-gaap:AccountsReceivableNetCurrent = 83616000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 168192000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 445949000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 49490000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 1973000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Total assets' on us-gaap:Assets = 608020000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 63336000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 167097000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 186391000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-16-010591 R5.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 245972000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 9698000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -18627000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -101260000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Cash paid for purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -12826000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 35993000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 11236000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Purchase of treasury stock, net of issuances' on us-gaap:PaymentsForRepurchaseOfCommonStock = -85926000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Interest, net of capitalized interest' on us-gaap:InterestPaid = 917000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-16-010591 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 19923000 (FILING-CHECKED)
- revenue: era 10-K 0001628280-18-002437 R2.htm prints 'Revenues' on us-gaap:SalesRevenueNet = 1023513000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001628280-18-002437 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 506292000 (FILING-CHECKED)
- interest_expense: era 10-K 0001334036-24-000025 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -161351000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
