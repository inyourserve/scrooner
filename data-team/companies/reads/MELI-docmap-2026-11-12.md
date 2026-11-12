# MELI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001099590-26-000006 (CIK 0001099590, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001562762-16-000352 (CIK 0001099590, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001562762-19-000047 (CIK 0001099590, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001099590-23-000007 (CIK 0001099590, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R10.htm
- companyfacts CIK0001099590.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Net revenues and financial income | 28893000000 | 28893000000 | 20777000000 | 20777000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of net revenues and financial expenses | -16035000000 | 16035000000 | -11200000000 | 11200000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 12858000000 | 12858000000 | 9577000000 | 9577000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | -9657000000 | 9657000000 | -6946000000 | 6946000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | -1078000000 | 1078000000 | -963000000 | 963000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Product and technology development | -2269000000 | 2269000000 | -1934000000 | 1934000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 3201000000 | 3201000000 | 2631000000 | 2631000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| interest_expense | mapped | meli:InterestExpenseAndOtherFinancialCharges | R5.htm | Interest expense and other financial losses | -160000000 |  | -165000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Net income before income tax expense and equity in earnings of unconsolidated entity | 2842000000 | 2842000000 | 2432000000 | 2432000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -845000000 | 845000000 | -521000000 | 521000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1997000000 | 1997000000 | 1911000000 | 1911000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income available to shareholders per common share (in dollars per share) | 39.4 | 39.4 | 37.69 | 37.69 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income available to shareholders per common share (in dollars per share) | 39.4 | 39.4 | 37.69 | 37.69 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average of outstanding common shares (in shares) | 50697299 | 50697299 | 50697428 | 50697428 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average of outstanding common shares (in shares) | 50697320 | 50697320 | 50697428 | 50697428 | Y | FILING-CHECKED | accn 0001099590-26-000006 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 3670000000 | 3670000000 | 2635000000 | 2635000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 369000000 | 369000000 | 255000000 | 255000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 570000000 | 570000000 | 296000000 | 296000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 33573000000 | 33573000000 | 20142000000 | 20142000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 2303000000 | 2303000000 | 1380000000 | 1380000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 163000000 | 163000000 | 149000000 | 149000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 42667000000 | 42667000000 | 25196000000 | 25196000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 4502000000 | 4502000000 | 3196000000 | 3196000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 28633000000 | 28633000000 | 16603000000 | 16603000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 35919000000 | 35919000000 | 20845000000 | 20845000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total equity | 6748000000 | 6748000000 | 4351000000 | 4351000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 12116000000 | 12116000000 | 7918000000 | 7918000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -6179000000 | -6179000000 | -8287000000 | -8287000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 2904000000 | 2904000000 | 1959000000 | 1959000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Investments in property and equipment, intangible assets and intangible assets at fair value | -1343000000 | 1343000000 | -860000000 | 860000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 818000000 | 818000000 | 617000000 | 617000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| sbc | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ShareBasedCompensation, AllocatedShareBasedCompensationExpense in MetaLinks.json (1220 tags across all 122 R pages, face and notes) of 0001099590-26-000006; no face row matched |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1220 tags across all 122 R pages, face and notes) of 0001099590-26-000006; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Common Stock repurchased | -1000000 | 1000000 | -1000000 | 1000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 611000000 | 611000000 | 456000000 | 456000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income tax | 1013000000 | 1013000000 | 1052000000 | 1052000000 | Y | FILING-CHECKED | accn 0001099590-26-000006 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R106.htm | LOANS PAYABLE AND OTHER FINANCIAL LIABILITIES - Summary Of Loans Payable And Other Financial Liabilities (Details) |  | 9193000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R106.htm 'LOANS PAYABLE AND OTHER FINANCIAL LIABILITIES - Summary Of Loans Payable And Oth' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 50697182 | 50697182 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Net revenues' on us-gaap:SalesRevenueServicesNet = 651790000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Cost of net revenues' on us-gaap:CostOfRevenue = -214994000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 436796000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = -297600000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001562762-16-000352 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = -76342000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001562762-16-000352 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 139196000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Interest expense and other financial losses' on meli:InterestExpenseAndOtherFinancialCharges = -20391000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Net income before income / asset tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 150491000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Income / asset tax expense' on us-gaap:IncomeTaxExpenseBenefit = -44702000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Net income attributable to MercadoLibre, Inc. shareholders' on us-gaap:NetIncomeLoss = 105789000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Basic net income attributable to MercadoLibre, Inc. Shareholders per common shar' on us-gaap:EarningsPerShareBasic = 2.4 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Diluted net income attributable to MercadoLibre, Inc. Shareholders per common sh' on us-gaap:EarningsPerShareDiluted = 2.4 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Weighted average of outstanding common shares' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 44155680 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001562762-16-000352 R4.htm prints 'Weighted average of outstanding common shares' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 44155680 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 166881000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 28428000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 222000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 557463000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 81633000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 86545000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Total assets' on us-gaap:Assets = 1003606000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 62038000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 325026000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 664148000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001562762-16-000352 R2.htm prints 'Total Equity' on us-gaap:StockholdersEquity = 339458000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 221370000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -183538000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -27714000 (FILING-CHECKED)
- capex: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -39150000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 23209000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Repurchase of Common Stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2714000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 7977000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001562762-16-000352 R7.htm prints 'Cash paid for income and asset taxes' on us-gaap:IncomeTaxesPaid = 65550000 (FILING-CHECKED)
- revenue: era 10-K 0001562762-19-000047 R4.htm prints 'Net revenues' on us-gaap:Revenues = 1439653000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001562762-19-000047 R4.htm prints 'Cost of net revenues' on us-gaap:CostOfRevenue = -742645000 (FILING-CHECKED)
- revenue: era 10-K 0001099590-23-000007 R5.htm prints 'Net revenues' on us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax = 10537000000 (FILING-CHECKED)
- ppe_net: era 10-K 0001099590-23-000007 R3.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 993000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- interest_expense: API missing (meli:InterestExpenseAndOtherFinancialCharges)

## Hand checks 2026-11-12 (Ritwik cloud)
- sbc: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LoansPayableCurrent+us-gaap:LongTermLoansPayable (R3.htm): 2026-11-12 R3.htm: corrected: both lines are on the BS face (4,623 + 4,570), not only in note R106
- cost_of_revenue: mapped us-gaap:CostOfGoodsAndServicesSold (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Cost of net revenues and financial expenses' is the cost_of_revenue line, printed -16035000000 = filing XBRL 16035000000; agrees
- sga_expense: component sum us-gaap:SellingAndMarketingExpense+us-gaap:GeneralAndAdministrativeExpense (R5.htm): 2026-11-12 R5.htm: sample DISAGREES (key-error class): G&A alone while S&M is printed; 3,219 + 1,078
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Product and technology development' is the research_and_development line, printed -2269000000 = filing XBRL 2269000000; agrees
- inventory: mapped us-gaap:InventoryNet (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Inventories' is the inventory line, printed 570000000 = filing XBRL 570000000; agrees
- accounts_payable: combined us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: 'Accounts payable and accrued expenses' bundles accrued expenses: combined
- total_liabilities: mapped us-gaap:Liabilities (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total liabilities' is the total_liabilities line, printed 35919000000 = filing XBRL 35919000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Common Stock repurchased' is the share_buybacks line, printed -1000000 = filing XBRL 1000000; agrees
