# MUR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-011709 (CIK 0000717423, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000717423-16-000064 (CIK 0000717423, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000717423-24-000008 (CIK 0000717423, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000717423-21-000014 (CIK 0000717423, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- companyfacts CIK0000717423.json (one call); submissions CIK0000717423.json (SIC 1311).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues and other income | 2718823000 | 2718823000 | 3028474000 | 3028474000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Costs of purchased natural gas | 0 | 0 | 3147000 | 3147000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Income statement shows revenues then total costs and expenses with no gross profit; revenue and segment notes show none. / pages opened: R5, R12, R28, R37, R51, R56, R57 |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 2417586000 | 2417586000 | 2425881000 | 2425881000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling and general expenses | 137332000 | 137332000 | 110085000 | 110085000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No R&D expense line; only R&D tax credits appear in the tax rate reconciliation. / pages opened: R5, R69, R68, R80, R82, R84, R111 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income from continuing operations | 301237000 | 301237000 | 602593000 | 602593000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense, net | -96072000 | 96072000 | -105926000 | 105926000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income from continuing operations before income taxes | 182866000 | 182866000 | 567569000 | 567569000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 44552000 | 44552000 | 78272000 | 78272000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME ATTRIBUTABLE TO MURPHY | 104234000 | 104234000 | 407171000 | 407171000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income (in USD per share) | 0.73 | 0.73 | 2.71 | 2.71 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income (in USD per share) | 0.72 | 0.72 | 2.7 | 2.7 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 143124118 | 143124118 | 150011458 | 150011458 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 144025322 | 144025322 | 151027352 | 151027352 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 377196000 | 377196000 | 423569000 | 423569000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 346759000 | 346759000 | 272530000 | 272530000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 57284000 | 57284000 | 54858000 | 54858000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 816712000 | 816712000 | 785279000 | 785279000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, at cost less accumulated depreciation, depletion and amortization of $15,068,149 in 2025  | 8136346000 | 8136346000 | 8054653000 | 8054653000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet has no goodwill; R55 and R119 cover asset impairments and oil and gas results only. / pages opened: R3, R55, R119 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9832626000 | 9832626000 | 9667479000 | 9667479000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 572183000 | 572183000 | 472165000 | 472165000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1062749000 | 1062749000 | 942814000 | 942814000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4595929000 | 4595929000 | 4325636000 | 4325636000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Murphy Shareholders' Equity | 5118380000 | 5118380000 | 5194250000 | 5194250000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R7.htm | Net cash provided by continuing operations activities | 1247808000 | 1247808000 | 1728990000 | 1728990000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash required by investing activities | -1028926000 | -1028926000 | -908164000 | -908164000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash required by financing activities | -264065000 | -264065000 | -716541000 | -716541000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireOtherProductiveAssets | R7.htm | Property additions and dry hole costs | 1020611000 |  |  |  |  | FILING-CHECKED | check: hand / Cash flow investing line for property additions and dry hole costs is the capital expenditure line (acquisitions of oil and gas properties 29,034k shown separately). / pages opened: R7 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation, depletion and amortization | 977753000 | 977753000 | 865753000 | 865753000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R75.htm | Compensation charged against income before income tax benefit | 50107000 | 50107000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R75.htm 'Incentive Plans - Schedule of Share-Based Plans, Amounts Recognized in the Finan' (MetaLinks.json presentation) |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Cash dividends paid | -186205000 | 186205000 | -179961000 | 179961000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -102620000 | 102620000 | -301350000 | 301350000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-011709 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R96.htm | Interest paid, net of amounts capitalized | 88119000 | 88119000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R96.htm 'Other Financial Information - Schedule of Noncash Operating Working Capital (Inc' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R70.htm | Total | 6101000 | 6101000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R70.htm 'Income Taxes - Schedule of Cash Taxes Paid, Net of Refunds (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt, finance lease + Long-term debt, including finance lease obligation | 1385080000 | 1385080000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; finance leases already inside a debt line (tag/label): not added again; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R104.htm | End of year (in shares) | 142785152 | 142785152 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R104.htm 'Common Stock Issued and Outstanding - Schedule of Number of Shares of Common Sto' (MetaLinks.json presentation) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Total revenues' on us-gaap:Revenues = 3033080000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000717423-16-000064 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 6315342000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Selling and general expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 306663000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000717423-16-000064 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Interest expense' on us-gaap:InterestCostsIncurred = 124665000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Income (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -3282262000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Income tax expense (benefit)' on us-gaap:IncomeTaxExpenseBenefit = -1026490000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Net Income (Loss)' on us-gaap:NetIncomeLoss = -2270833000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Net income (loss)' on us-gaap:EarningsPerShareBasic = -13.03 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Net income (loss)' on us-gaap:EarningsPerShareDiluted = -13.03 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Average Common shares outstanding - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 174351227 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000717423-16-000064 R4.htm prints 'Average Common shares outstanding - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 174351227 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 283183000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Accounts receivable, less allowance for doubtful accounts of $1,605 in 2015 and ' on us-gaap:AccountsReceivableNetCurrent = 522672000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Inventories, at lower of cost or market' on us-gaap:InventoryNet = 166788000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1448416000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Property, plant and equipment, at cost less accumulated depreciation, depletion ' on us-gaap:PropertyPlantAndEquipmentNet = 9818365000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Total assets' on us-gaap:Assets = 11493812000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 1529848000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1674629000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000717423-16-000064 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0000717423-16-000064 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 5306728000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000717423-16-000064 R6.htm prints 'Net cash provided by continuing operations activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1183369000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000717423-16-000064 R6.htm prints 'Net cash required by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1922121000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000717423-16-000064 R6.htm prints 'Net cash provided (required) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -364561000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000717423-16-000064 R6.htm prints 'Depreciation, depletion and amortization' on us-gaap:DepreciationDepletionAndAmortization = 1619824000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000717423-16-000064 R6.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000717423-16-000064 R6.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -244998000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000717423-16-000064 R6.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -250000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000717423-16-000064 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000717423-16-000064 R6.htm read; no row matched (auto)
- interest_expense: era 10-K 0000717423-24-000008 R5.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -112373000 (FILING-CHECKED)
- ppe_net: era 10-K 0000717423-21-000014 R2.htm prints 'Property, plant and equipment, at cost less accumulated depreciation, depletion ' on us-gaap:PropertyPlantAndEquipmentNet = 8269038000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
