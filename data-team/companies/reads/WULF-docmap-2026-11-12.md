# WULF document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001083301-26-000031 (CIK 0001083301, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R9.htm
- 10-K 0001558370-16-003779 (CIK 0001083301, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001437749-21-004835 (CIK 0001083301, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001083301-25-000018 (CIK 0001083301, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- companyfacts CIK0001083301.json (one call); submissions CIK0001083301.json (SIC 6199).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenue | 168455000 | 168455000 | 140051000 | 140051000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenue (exclusive of depreciation shown below) | 82663000 | 82663000 | 62608000 | 62608000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1148 tags across all 90 R pages, face and notes) of 0001083301-26-000031; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:GrossProfit 'Segment profit (loss) / Gross Profit / Aggregate revenue les' R89 |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 354668000 | 354668000 | 216267000 | 216267000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 139465000 |  | 57883000 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1148 tags across all 90 R pages, face and notes) of 0001083301-26-000031; HAND REVIEW: 4 label candidate(s) incl. custom tags: wulf:DeferredTaxAssetsFederalTaxCreditCarryforwardsResearch 'Federal research development tax credit carryforwards / Defe' R73; wulf:DeferredTaxAssetsStateTaxCreditCarryforwardsResearch 'State research development tax credit carryforwards / Deferr' R73; us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R71; us-gaap:IncomeTaxReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R71 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating loss | -186213000 | -186213000 | -76216000 | -76216000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -80248000 | 80248000 | -19794000 | 19794000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Loss before income tax and equity in net (loss) income of investee | -657210000 | -657210000 | -98383000 | -98383000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | -76000 | 76000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -661416000 | -661416000 | -72418000 | -72418000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Earnings per share, basic (in dollars per share) | -1.66 | -1.66 | -0.21 | -0.21 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Earnings per share, diluted (in dollars per share) | -1.66 | -1.66 | -0.21 | -0.21 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 397608216 | 397608216 | 351315476 | 351315476 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 397608216 | 397608216 | 351315476 | 351315476 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 3266389000 | 3266389000 | 274065000 | 274065000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable | 1212000 | 1212000 | 475000 | 475000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1148 tags across all 90 R pages, face and notes) of 0001083301-26-000031; label search over every tag in the filing (custom included) found no candidate |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 3478273000 | 3478273000 | 281431000 | 281431000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 1507699000 | 1507699000 | 411869000 | 411869000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 55457000 | 55457000 | 0 | 0 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 6558182000 | 6558182000 | 787511000 | 787511000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 65139000 | 65139000 | 24382000 | 24382000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1735848000 | 1735848000 | 51845000 | 51845000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | TOTAL LIABILITIES | 6417737000 | 6417737000 | 543066000 | 543066000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 140445000 | 140445000 | 244445000 | 244445000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash (used in) provided by operating activities | -123180000 | -123180000 | -24422000 | -24422000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -1368945000 | -1368945000 | -91159000 | -91159000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by financing activities | 4940835000 | 4940835000 | 335207000 | 335207000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchase of and deposits on plant and equipment | -1060189000 | 1060189000 | -267940000 | 267940000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 88597000 | 88597000 | 59808000 | 59808000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 50909000 | 50909000 | 30927000 | 30927000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends, PaymentsOfOrdinaryDividends, PaymentsOfCapitalDistribution in MetaLinks.json (1148 tags across all 90 R pages, face and notes) of 0001083301-26-000031; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchase of treasury stock | -33292000 | 33292000 | -118217000 | 118217000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 13999000 | 13999000 | 6957000 | 6957000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Income taxes | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001083301-26-000031 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:OtherLongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent | R3.htm | Long-term debt + Current portion of finance lease liability + Finance lease liability, net of current portion | 3052531000 | 3052531000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; finance lease liabilities printed on the BS face added; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock shares outstanding (in shares) | 420065944 | 420065944 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001558370-16-003779 R4.htm prints 'NET SALES' on us-gaap:SalesRevenueGoodsNet = 17562066 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001558370-16-003779 R4.htm prints 'COST OF GOODS SOLD' on us-gaap:CostOfGoodsSold = 11417474 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001558370-16-003779 R4.htm prints 'SELLING, GENERAL AND ADMINISTRATIVE EXPENSES + RESEARCH AND DEVELOPMENT EXPENSES' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense = 5923774 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001558370-16-003779 R4.htm prints 'SELLING, GENERAL AND ADMINISTRATIVE EXPENSES' on us-gaap:SellingGeneralAndAdministrativeExpense = 5263372 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001558370-16-003779 R4.htm prints 'INCOME FROM OPERATIONS' on us-gaap:OperatingIncomeLoss = 220818 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001558370-16-003779 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001558370-16-003779 R4.htm prints 'INCOME BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 225007 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001558370-16-003779 R4.htm prints 'FEDERAL AND STATE INCOME TAXES (Note 2)' on us-gaap:IncomeTaxExpenseBenefit = 90000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001558370-16-003779 R4.htm prints 'NET INCOME' on us-gaap:NetIncomeLoss = 135007 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001558370-16-003779 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 0.07 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001558370-16-003779 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.07 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001558370-16-003779 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 2018253 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001558370-16-003779 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 2018591 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Cash and cash equivalents (Note 7)' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2248466 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Trade receivables, less allowance of $122,000 in 2015 and $49,000 in 2014 (Notes' on us-gaap:AccountsReceivableNetCurrent = 2165194 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 6916891 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Net property, plant, and equipment, at cost' on us-gaap:PropertyPlantAndEquipmentNet = 7957330 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001558370-16-003779 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Total assets' on us-gaap:Assets = 15210317 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Accounts payable - Trade' on us-gaap:AccountsPayableTradeCurrent = 420245 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1135102 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1715102 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001558370-16-003779 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 13495215 (FILING-CHECKED)
- cfo: FY2015 10-K 0001558370-16-003779 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1466061 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001558370-16-003779 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1153809 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001558370-16-003779 R6.htm read; no row matched (auto)
- capex: FY2015 10-K 0001558370-16-003779 R6.htm prints 'Purchases of property, plant, equipment and construction in progress' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -2866671 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001558370-16-003779 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001558370-16-003779 R6.htm prints 'Stock based compensation' on us-gaap:ShareBasedCompensation = 21743 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001558370-16-003779 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001558370-16-003779 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001558370-16-003779 R6.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaidNet = 11127 (FILING-CHECKED)
- revenue: era 10-K 0001437749-21-004835 R4.htm prints 'Net sales' on us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax = 13432220 (FILING-CHECKED)
- interest_expense: era 10-K 0001437749-21-004835 R4.htm prints 'INTEREST EXPENSE' on us-gaap:InterestExpense = -86561 (FILING-CHECKED)
- income_before_tax: era 10-K 0001437749-21-004835 R4.htm prints 'LOSS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -649320 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001437749-21-004835 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3693845 (FILING-CHECKED)
- accounts_payable: era 10-K 0001437749-21-004835 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableTradeCurrent = 459836 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001437749-21-004835 R6.htm prints 'Cash paid for income taxes, net' on us-gaap:IncomeTaxesPaidNet = 8082 (FILING-CHECKED)
- revenue: era 10-K 0001083301-25-000018 R5.htm prints 'Revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 140051000 (FILING-CHECKED)

## Mismatches (printed vs API)
- sga_expense: API missing (us-gaap:SellingGeneralAndAdministrativeExpense)
