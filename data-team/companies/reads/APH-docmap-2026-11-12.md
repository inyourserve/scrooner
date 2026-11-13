# APH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-013549 (CIK 0000820313, filed 2026-02-11): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001104659-16-098503 (CIK 0000820313, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001558370-18-000871 (CIK 0000820313, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001558370-24-000866 (CIK 0000820313, era filing): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- companyfacts CIK0000820313.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 23094700000 | 23094700000 | 15222700000 | 15222700000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 14577000000 | 14577000000 | 10083000000 | 10083000000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 8517700000 | 8517700000 | 5139700000 | 5139700000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | aph:AcquisitionRelatedExpenses+us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Acquisition-related expenses + Selling, general and administrative expenses | 2649100000 |  | 1982800000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI; company extension tag, matched by printed label / accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 2545700000 | 2545700000 | 1855400000 | 1855400000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R50.htm | Summary of Significant Accounting Policies, Research and Development (Details) |  | 647000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R50.htm 'Summary of Significant Accounting Policies, Research and Development (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 5868600000 | 5868600000 | 3156900000 | 3156900000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -367800000 | 367800000 | -217000000 | 217000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 5600700000 | 5600700000 | 3011900000 | 3011900000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | -1295400000 | 1295400000 | -570300000 | 570300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Amphenol Corporation | 4270300000 | 4270300000 | 2424000000 | 2424000000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income attributable to Amphenol Corporation per common share - Basic (in dollars per share) | 3.51 | 3.51 | 2.01 | 2.01 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income attributable to Amphenol Corporation per common share - Diluted (in dollars per share) | 3.34 | 3.34 | 1.92 | 1.92 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted average common shares outstanding - Basic (in shares) | 1218200000 | 1218200000 | 1203800000 | 1203800000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted average common shares outstanding - Diluted (in shares) | 1277500000 | 1277500000 | 1263600000 | 1263600000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 11130600000 | 11130600000 | 3317000000 | 3317000000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, less allowance for doubtful accounts of $99.3 and $66.5, respectively | 4717100000 | 4717100000 | 3287900000 | 3287900000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 3424900000 | 3424900000 | 2545700000 | 2545700000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 20267200000 | 20267200000 | 9686000000 | 9686000000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 2305600000 | 2305600000 | 1711800000 | 1711800000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 10575400000 | 10575400000 | 8236200000 | 8236200000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 36236900000 | 36236900000 | 21440200000 | 21440200000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2661900000 | 2661900000 | 1819400000 | 1819400000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 6802800000 | 6802800000 | 4083800000 | 4083800000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total Liabilities | 22727200000 | 22727200000 | 11584100000 | 11584100000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity attributable to Amphenol Corporation | 13413100000 | 13413100000 | 9792000000 | 9792000000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 5374700000 | 5374700000 | 2814700000 | 2814700000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -5082100000 | -5082100000 | -2648600000 | -2648600000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 7423200000 | 7423200000 | 1729900000 | 1729900000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -996600000 | 996600000 | -665400000 | 665400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 922400000 | 922400000 | 572500000 | 572500000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 135400000 | 135400000 | 109500000 | 109500000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividend payments | -802200000 | 802200000 | -595100000 | 595100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchase of treasury stock | -665200000 | 665200000 | -689300000 | 689300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 288100000 | 288100000 | 179500000 | 179500000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes, net | 1084100000 | 1084100000 | 650000000 | 650000000 | Y | FILING-CHECKED | accn 0001104659-26-013549 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt + Long-term debt, less current portion | 15502000000 | 15502000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Class A Common Stock, shares outstanding | 1226600000 | 1226600000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Net sales' on us-gaap:SalesRevenueGoodsNet = 5568700000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 3789200000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1779500000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Acquisition-related expenses + Selling, general and administrative expense' on us-gaap:BusinessCombinationAcquisitionRelatedCosts+us-gaap:SellingGeneralAndAdministrativeExpense = 6.748e+08 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Selling, general and administrative expense' on us-gaap:SellingGeneralAndAdministrativeExpense = 669100000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001104659-16-098503 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1104700000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -68300000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1052800000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = -280500000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Net income attributable to Amphenol Corporation' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 763500000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Net income per common share - Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.47 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Net income per common share - Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.41 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Weighted average common shares outstanding - Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 309100000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001104659-16-098503 R2.htm prints 'Weighted average common shares outstanding - Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 316500000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1737200000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Accounts receivable, less allowance for doubtful accounts of $25.6 and $20.2, re' on us-gaap:AccountsReceivableNetCurrent = 1104600000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 851800000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3850000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Land and depreciable assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 609500000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 2692900000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Total assets' on us-gaap:Assets = 7458400000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 587800000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1008400000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001104659-16-098503 R4.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001104659-16-098503 R4.htm prints 'Total shareholders' equity attributable to Amphenol Corporation' on us-gaap:StockholdersEquity = 3238500000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1030500000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -27300000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -180100000 (FILING-CHECKED)
- capex: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Purchases of land and depreciable assets' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -172100000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 171600000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 44200000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Dividend payments' on us-gaap:PaymentsOfDividendsCommonStock = -159300000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Purchase and retirement of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -248900000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Interest' on us-gaap:InterestPaidNet = 6.41e+07 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001104659-16-098503 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 250700000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001558370-18-000871 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 4701400000 (FILING-CHECKED)
- interest_expense: era 10-K 0001558370-24-000866 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -139500000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (aph:AcquisitionRelatedExpenses+us-gaap:SellingGeneralAndAdministrativeExpense)

## Hand checks 2026-11-12 (Ritwik cloud)
- operating_expenses: component sum aph:AcquisitionRelatedExpenses+us-gaap:SellingGeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: agree: 103.4 + 2,545.7 = 8,517.7 GP - 5,868.6 OI (R3)
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R50.htm): 2026-11-12 R50.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: agree: R5 current + long-term debt lines
- gross_profit: mapped us-gaap:GrossProfit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Gross profit' is the gross_profit line, printed 8517700000 = filing XBRL 8517700000; agrees
- sga_expense: mapped us-gaap:SellingGeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Selling, general and administrative expenses' is the sga_expense line, printed 2545700000 = filing XBRL 2545700000; agrees
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income before income taxes' is the income_before_tax line, printed 5600700000 = filing XBRL 5600700000; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Cash and cash equivalents' is the cash_and_equivalents line, printed 11130600000 = filing XBRL 11130600000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Net cash used in investing activities' is the cash_flow_investing line, printed -5082100000 = filing XBRL -5082100000; agrees
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Interest' is the cash_paid_for_interest line, printed 288100000 = filing XBRL 288100000; agrees
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Income taxes, net' is the cash_paid_for_income_taxes line, printed 1084100000 = filing XBRL 1084100000; agrees
