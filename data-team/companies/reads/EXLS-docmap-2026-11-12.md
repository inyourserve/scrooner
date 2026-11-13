# EXLS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001297989-26-000008 (CIK 0001297989, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001628280-16-011841 (CIK 0001297989, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001297989-18-000002 (CIK 0001297989, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001297989-24-000003 (CIK 0001297989, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R9.htm
- companyfacts CIK0001297989.json (one call); submissions CIK0001297989.json (SIC 7389).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues, net | 2087679000 | 2087679000 | 1838372000 | 1838372000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R5.htm | Cost of revenues | 1286603000 | 1286603000 | 1147359000 | 1147359000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 801076000 | 801076000 | 691013000 | 691013000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 487326000 | 487326000 | 427393000 | 427393000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R5.htm | General and administrative expenses + Selling and marketing expenses | 428242000 | 428242000 | 372174000 | 372174000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Only R&D tax credits and a deferred tax asset for capitalized R&D (tax items); no R&D expense reported. / pages opened: R127, R128, R130, R21, R51, R83 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 313750000 | 313750000 | 263620000 | 263620000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -17611000 | 17611000 | -19256000 | 19256000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before income tax expense and earnings from equity affiliates | 315052000 | 315052000 | 261347000 | 261347000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 63728000 | 63728000 | 62936000 | 62936000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 251019000 | 251019000 | 198297000 | 198297000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.56 | 1.56 | 1.22 | 1.22 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.54 | 1.54 | 1.21 | 1.21 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 161028312 | 161028312 | 162718840 | 162718840 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 162481586 | 162481586 | 164321656 | 164321656 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 146326000 | 146326000 | 153355000 | 153355000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 343105000 | 343105000 | 304322000 | 304322000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No pages listed; consolidated balance sheet (R3) has no inventory line for this services company. / pages opened: R3 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 829957000 | 829957000 | 795189000 | 795189000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 111821000 | 111821000 | 101837000 | 101837000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 419654000 | 419654000 | 420387000 | 420387000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1702235000 | 1702235000 | 1618403000 | 1618403000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 4753000 | 4753000 | 5884000 | 5884000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 324125000 | 324125000 | 290116000 | 290116000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 789530000 | 789530000 | 688541000 | 688541000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 912705000 | 912705000 | 929862000 | 929862000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 350717000 | 350717000 | 268525000 | 268525000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -49260000 | -49260000 | -119099000 | -119099000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used for financing activities | -312764000 | -312764000 | -119101000 | -119101000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -52598000 | 52598000 | -46262000 | 46262000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization expense | 59248000 | 59248000 | 55221000 | 55221000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 79469000 | 79469000 | 72658000 | 72658000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:DividendsCommonStockCash | R109.htm | Common stock, dividend paid | 0 |  |  |  |  | FILING-CHECKED | check: hand / Capital structure note reports undimensioned common dividends paid of 0 for FY2025 (explicit zero; no dividends). / pages opened: R109, R7 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Acquisition of treasury stock | -328490000 | 328490000 | -207926000 | 207926000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 16958000 | 16958000 | 19604000 | 19604000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001297989-26-000008 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R128.htm | Income taxes | 77231000 | 77231000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R128.htm 'Income Taxes - Additional Information (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiability(note) | R3.htm | Current portion of long-term borrowings + Long-term borrowings, less current portion + finance lease liabilities (note) | 300758000 | 300758000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; finance lease liabilities 2160000 from the lease note (no face line carries them); operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 156430028 | 156430028 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-16-011841 R4.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Cost of revenues (exclusive of depreciation and amortization)' on us-gaap:CostOfServicesExcludingDepreciationDepletionAndAmortization = 402917000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 225575000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 158232000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-16-011841 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 77293000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 67343000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001628280-16-011841 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 75776000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 24211000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 51565000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.55 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.51 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 33298104 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001628280-16-011841 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 34178340 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 205323000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 92650000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 339199000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 47991000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 171535000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Total assets' on us-gaap:Assets = 650783000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 6401000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 107079000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001628280-16-011841 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 185012000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-011841 R2.htm prints 'ExlService Holdings, Inc. stockholders' equity' on us-gaap:StockholdersEquity = 465592000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 96691000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -73540000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Net cash (used for)/provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 10020000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Purchase of fixed assets' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -25585000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 31465000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 16047000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Acquisition of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -14195000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaidNet = 1188000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-011841 R8.htm prints 'Cash paid for taxes, net of refund' on us-gaap:IncomeTaxesPaidNet = 11505000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001297989-18-000002 R4.htm prints 'Cost of revenues (exclusive of depreciation and amortization)' on us-gaap:CostOfServices = 495586000 (FILING-CHECKED)
- interest_expense: era 10-K 0001297989-24-000003 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -13180000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
