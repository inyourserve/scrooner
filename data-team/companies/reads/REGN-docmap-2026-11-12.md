# REGN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000872589-26-000008 (CIK 0000872589, filed 2026-02-04): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001532176-16-000045 (CIK 0000872589, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001532176-18-000013 (CIK 0000872589, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001804220-24-000009 (CIK 0000872589, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- companyfacts CIK0000872589.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue from contract with customer | 14342900000 | 14342900000 | 14202000000 | 14202000000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold and of collaboration and contract manufacturing | 1140800000 |  | 1087300000 |  | API missing | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (858 tags across all 105 R pages, face and notes) of 0000872589-26-000008; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total expenses | 10765000000 | 10765000000 | 10211300000 | 10211300000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general, and administrative | 2700000000 | 2700000000 | 2954400000 | 2954400000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 5850200000 | 5850200000 | 5132000000 | 5132000000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 3577900000 | 3577900000 | 3990700000 | 3990700000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -43800000 | 43800000 | -55200000 | 55200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 5230700000 | 5230700000 | 4779900000 | 4779900000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 725800000 | 725800000 | 367300000 | 367300000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 4504900000 | 4504900000 | 4412600000 | 4412600000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income per share - basic (in dollars per share) | 43.07 | 43.07 | 40.9 | 40.9 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income per share - diluted (in dollars per share) | 41.48 | 41.48 | 38.34 | 38.34 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average shares outstanding - basic (in shares) | 104600000 | 104600000 | 107900000 | 107900000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average shares outstanding - diluted (in shares) | 108600000 | 108600000 | 115100000 | 115100000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 3118100000 | 3118100000 | 2488200000 | 2488200000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 5741100000 | 5741100000 | 6211900000 | 6211900000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 3200800000 | 3200800000 | 3087300000 | 3087300000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 18021900000 | 18021900000 | 18660900000 | 18660900000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant, and equipment, net | 5120400000 | 5120400000 | 4599700000 | 4599700000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (858 tags across all 105 R pages, face and notes) of 0000872589-26-000008; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 40558700000 | 40558700000 | 37759400000 | 37759400000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 939000000 | 939000000 | 789500000 | 789500000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4368400000 | 4368400000 | 3944300000 | 3944300000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 9301800000 | 9301800000 | 8.406e+09 | 8405800000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 31256900000 | 31256900000 | 29353600000 | 29353600000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 4978900000 | 4978900000 | 4420500000 | 4420500000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -629100000 | -629100000 | -2468100000 | -2468100000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -3715400000 | -3715400000 | -2200500000 | -2200500000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -898400000 | 898400000 | -755900000 | 755900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 543700000 | 543700000 | 482900000 | 482900000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 993700000 | 993700000 | 982800000 | 982800000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid | -370300000 | 370300000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of Common Stock | -3438600000 | 3438600000 | -2603300000 | 2603300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest (net of amounts capitalized) | 41600000 | 41600000 | 52600000 | 52600000 | Y | FILING-CHECKED | accn 0000872589-26-000008 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R93.htm | Income Taxes - Schedule of cash paid for income taxes (Details) |  | 1253000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R93.htm 'Income Taxes - Schedule of cash paid for income taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Long-term debt | 1985900000 | 1985900000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common Stock, shares outstanding (in shares) | 1800000 |  |  |  | API missing | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Total revenues' on us-gaap:Revenues = 4103728000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 241702000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Total expenses' on us-gaap:CostsAndExpenses = 2851812000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Selling, general, and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 838526000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 1620577000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 1251916000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -14241000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1225097000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -589041000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 636056000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Net income per share - basic' on us-gaap:EarningsPerShareBasic = 6.17 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Net income per share - diluted' on us-gaap:EarningsPerShareDiluted = 5.52 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Weighted average shares outstanding - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 103061000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001532176-16-000045 R4.htm prints 'Weighted average shares outstanding - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 115230000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 809102000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Accounts receivable - trade, net' on us-gaap:AccountsReceivableNetCurrent = 1152489000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 238578000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2915095000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Property, plant, and equipment, at cost, net of accumulated depreciation and amo' on us-gaap:PropertyPlantAndEquipmentNet = 1594120000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Total assets' on us-gaap:Assets = 5609132000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 644112000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 811162000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1954295000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001532176-16-000045 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 3654837000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1330780000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Net cash used in by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -907601000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -262796000 (FILING-CHECKED)
- capex: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -677933000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 74909000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Non-cash compensation expense' on us-gaap:ShareBasedCompensation = 459049000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001532176-16-000045 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001532176-16-000045 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Cash paid for interest (net of amounts capitalized)' on us-gaap:InterestPaidNet = 10582000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001532176-16-000045 R6.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 276092000 (FILING-CHECKED)
- revenue: era 10-K 0001532176-18-000013 R4.htm prints 'Total revenues' on us-gaap:Revenues = 5872227000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001532176-18-000013 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 202507000 (FILING-CHECKED)
- accounts_payable: era 10-K 0001532176-18-000013 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 815078000 (FILING-CHECKED)
- interest_expense: era 10-K 0001804220-24-000009 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -73000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:ResearchAndDevelopmentExpense+regn:AcquiredInProcessResearchAndDevelopment+us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:OtherOperatingIncomeExpenseNet (R5.htm): 2026-11-12 R5.htm: corrected: opex = 5,850.2 + 124.1 + 2,700.0 - 10.0 = 8,664.3 = 14,342.9 - 2,100.7 - 3,577.9
- goodwill: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R93.htm): 2026-11-12 R93.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityNoncurrent (R3.htm): 2026-11-12 R3.htm: corrected: finance-lease ruling (founder 2026-11-04 item 5): R3 prints 'Finance lease liabilities' 720.0 as its own face line: 1,985.9 + 720.0
- operating_income: mapped us-gaap:OperatingIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Income from operations' is the operating_income line, printed 3577900000 = filing XBRL 3577900000; agrees
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Interest expense' is the interest_expense line, printed -43800000 = filing XBRL 43800000; agrees
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Income tax expense' is the income_tax_expense line, printed 725800000 = filing XBRL 725800000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Net income per share - basic (in dollars per share' is the basic_eps line, printed 43.07 = filing XBRL 43.07; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Weighted average shares outstanding - basic (in sh' is the weighted_basic_shares line, printed 104600000 = filing XBRL 104600000; agrees
- depreciation_and_amortization: mapped us-gaap:DepreciationDepletionAndAmortization (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Depreciation and amortization' is the depreciation_and_amortization line, printed 543700000 = filing XBRL 543700000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Repurchases of Common Stock' is the share_buybacks line, printed -3438600000 = filing XBRL 3438600000; agrees
- cost_of_revenue: component sum check: hand 2026-11-12 R5.htm: corrected: R5 prints two cost rows on the same tag (1,140.8 and 959.9); the tool took the first: 2,100.7
