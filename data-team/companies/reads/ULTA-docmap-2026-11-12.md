# ULTA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-035243 (CIK 0001403568, filed 2026-03-26): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001193125-15-115602 (CIK 0001403568, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- 10-K 0001558370-18-002733 (CIK 0001403568, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- 10-K 0001558370-25-003810 (CIK 0001403568, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- companyfacts CIK0001403568.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Net sales | 12392820000 | 12392820000 | 11295654000 | 11295654000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Cost of sales | 7547596000 | 7547596000 | 6908401000 | 6908401000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profit | 4845224000 | 4845224000 | 4387253000 | 4387253000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:PreOpeningCosts | R4.htm | Selling, general and administrative expenses + Pre-opening expenses | 3312232000 | 3312232000 | 2822281000 | 2822281000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001104659-26-035243 R4.htm period ..2026-01-31 / check: hand R4.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative expenses | 3296411000 | 3296411000 | 2808592000 | 2808592000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (808 tags across all 90 R pages, face and notes) of 0001104659-26-035243; no face row matched / check: hand R4.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 1532992000 | 1532992000 | 1564972000 | 1564972000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R4.htm | Interest expense (income), net | 1787000 | -1787000 | -15094000 | 15094000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R4.htm | Income before income taxes and equity net loss of affiliate | 1531205000 | 1531205000 | 1580066000 | 1580066000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | 373869000 | 373869000 | 378948000 | 378948000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 1153479000 | 1153479000 | 1201118000 | 1201118000 | Y | FILING-CHECKED | accn 0001104659-26-035243 R4.htm period ..2026-01-31 / check: hand R4.htm agree |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 25.72 | 25.72 | 25.44 | 25.44 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 25.64 | 25.64 | 25.34 | 25.34 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 44842000 | 44842000 | 47207000 | 47207000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 44991000 | 44991000 | 47404000 | 47404000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R4.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 424243000 | 424243000 | 703201000 | 703201000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R2.htm | Receivables, net | 296217000 | 296217000 | 223334000 | 223334000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| inventory | mapped | us-gaap:InventoryFinishedGoods | R2.htm | Merchandise inventories, net | 2181127000 | 2181127000 | 1968214000 | 1968214000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001104659-26-035243 R2.htm period ..2026-01-31 / check: hand R2.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 3144146000 | 3144146000 | 3028808000 | 3028808000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 1434062000 | 1434062000 | 1239295000 | 1239295000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 226421000 | 226421000 | 10870000 | 10870000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 6999294000 | 6999294000 | 6001693000 | 6001693000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 685887000 | 685887000 | 563761000 | 563761000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 2224342000 | 2224342000 | 1779478000 | 1779478000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 4195843000 | 4195843000 | 3513340000 | 3513340000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 2803451000 | 2803451000 | 2488353000 | 2488353000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R2.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 1502780000 | 1502780000 | 1338605000 | 1338605000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -931346000 | -931346000 | -383089000 | -383089000 | Y | FILING-CHECKED | accn 0001104659-26-035243 R6.htm period ..2026-01-31 / check: hand R6.htm agree |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash used in financing activities | -850666000 | -850666000 | -1018909000 | -1018909000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Capital expenditures | -434829000 | 434829000 | -374458000 | 374458000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 300772000 | 300772000 | 267042000 | 267042000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Share-based Compensation | 37426000 | 37426000 | 42787000 | 42787000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| dividends_paid | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (808 tags across all 90 R pages, face and notes) of 0001104659-26-035243; no face row matched / check: hand R6.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchase of common shares | -901388000 | 901388000 | -1003328000 | 1003328000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-035243 R6.htm period ..2026-01-31 / check: hand R6.htm agree |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Cash paid for interest | 9673000 | 9673000 | 4159000 | 4159000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R6.htm | Income taxes paid, net of refunds | 381812000 | 381812000 | 386059000 | 386059000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-035243 R6.htm period ..2026-01-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings | R2.htm | Short-term debt | 62287000 | 62287000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R2.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 44166000 | 44166000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-01-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 3241369 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 2104582 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 1136787 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Selling, general and administrative expenses + Pre-opening expenses' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:PreOpeningCosts = 726372 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 712006 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 410415 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-15-115602 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 411309 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 154174 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 257135 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 4 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 3.98 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 64335 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-15-115602 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 64651 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 389149 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 52440 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Merchandise inventories, net' on us-gaap:InventoryFinishedGoods = 581229 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1260355 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 717159 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-15-115602 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Total assets' on us-gaap:Assets = 1983170 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 190778 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 359594 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 735661 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-15-115602 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1247509 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 396592 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -399276 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -27643 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -249067 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 131764 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Non-cash stock compensation charges' on us-gaap:ShareBasedCompensation = 14923 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Repurchase of common shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -39923 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-15-115602 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-15-115602 R5.htm prints 'Cash paid for income taxes (net of refunds)' on us-gaap:IncomeTaxesPaidNet = 137180 (FILING-CHECKED)
- revenue: era 10-K 0001558370-18-002733 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 108756000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001558370-18-002733 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold =  (FILING-CHECKED)
- income_before_tax: era 10-K 0001558370-25-003810 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1580066000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 8 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 0.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
