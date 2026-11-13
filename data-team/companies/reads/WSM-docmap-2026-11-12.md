# WSM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000719955-26-000059 (CIK 0000719955, filed 2026-03-26): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001193125-16-525847 (CIK 0000719955, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001193125-18-102232 (CIK 0000719955, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001193125-19-097973 (CIK 0000719955, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000719955.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net revenues | 7806816000 | 7806816000 | 7711541000 | 7711541000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of goods sold | 4203765000 | 4203765000 | 4129242000 | 4129242000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 3603051000 | 3603051000 | 3582299000 | 3582299000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 2187329000 | 2187329000 | 2152115000 | 2152115000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000719955-26-000059 R3.htm period ..2026-02-01 / check: hand R3.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 2187329000 | 2187329000 | 2152115000 | 2152115000 | Y | FILING-CHECKED | accn 0000719955-26-000059 R3.htm period ..2026-02-01 / check: hand R3.htm agree |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (620 tags across all 64 R pages, face and notes) of 0000719955-26-000059; no face row matched / check: hand R3.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 1415722000 | 1415722000 | 1430184000 | 1430184000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest income, net | 36838000 | 36838000 | 55548000 | 55548000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before income taxes | 1452560000 | 1452560000 | 1485732000 | 1485732000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 364123000 | 364123000 | 360481000 | 360481000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 1088437000 | 1088437000 | 1125251000 | 1125251000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per share (in dollars per share) | 8.96 | 8.96 | 8.91 | 8.91 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per share (in dollars per share) | 8.84 | 8.84 | 8.79 | 8.79 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 121446000 | 121446000 | 126242000 | 126242000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 123153000 | 123153000 | 128041000 | 128041000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R3.htm period ..2026-02-01 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1019801000 | 1019801000 | 1212977000 | 1212977000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Accounts receivable, net | 126821000 | 126821000 | 117678000 | 117678000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Merchandise inventories, net | 1462849000 | 1462849000 | 1332429000 | 1332429000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 2713187000 | 2713187000 | 2754609000 | 2754609000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property and equipment, net | 1095158000 | 1095158000 | 1033934000 | 1033934000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 77398000 | 77398000 | 77260000 | 77260000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 5411912000 | 5411912000 | 5301607000 | 5301607000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 637985000 | 637985000 | 645667000 | 645667000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1954130000 | 1954130000 | 1911974000 | 1911974000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 3329353000 | 3329353000 | 3159188000 | 3159188000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 2082559000 | 2082559000 | 2142419000 | 2142419000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R5.htm period ..2026-02-01 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1314889000 | 1314889000 | 1360222000 | 1360222000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -260576000 | -260576000 | -221207000 | -221207000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1252372000 | -1252372000 | -1184223000 | -1184223000 | Y | FILING-CHECKED | accn 0000719955-26-000059 R9.htm period ..2026-02-01 / check: hand R9.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment | -259438000 | 259438000 | -221567000 | 221567000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 231449000 | 231449000 | 229802000 | 229802000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 106522000 | 106522000 | 98983000 | 98983000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Payment of dividends | -316484000 | 316484000 | -280058000 | 280058000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -853962000 | 853962000 | -807477000 | 807477000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid during the year for interest | 692000 | 692000 | 849000 | 849000 | Y | FILING-CHECKED | accn 0000719955-26-000059 R9.htm period ..2026-02-01 / check: hand R9.htm agree |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash paid during the year for income taxes, net of refunds | 330304000 | 330304000 | 398693000 | 398693000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000719955-26-000059 R9.htm period ..2026-02-01 |
| total_debt | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (620 tags across all 64 R pages, face and notes) of 0000719955-26-000059; no face row matched / check: hand R5.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 118770000 | 118770000 | 123125000 |  | Y | FILING-CHECKED | balance-sheet date 2026-02-01; single row / check: hand R6.htm corrected: R6 'Common stock, shares outstanding' 118,770 / 123,125 thousand; FY0 correct, FY1 was blank. |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 4976090000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Cost of goods sold' on wsm:CostOfGoodsSoldAndOccupancyExpenses = 3131876000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1844214000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1355580000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 1355580000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 488634000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-525847 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 488007000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 177939000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 310068000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 3.42 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted = 3.37 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 90787000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-525847 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 92102000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 193647000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Accounts receivable, net' on us-gaap:ReceivablesNetCurrent = 79304000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Merchandise inventories, net' on us-gaap:InventoryNet = 978138000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1336100000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 886813000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-525847 R4.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Total assets' on us-gaap:Assets = 2417427000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 447412000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 996427000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 1219201000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-525847 R4.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1198226000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 544026000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -202166000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -369383000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -202935000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 167760000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 41357000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Payment of dividends' on us-gaap:PaymentsOfDividends = -127636000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -224995000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Cash paid during the year for interest' on us-gaap:InterestPaid = 1989000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-525847 R7.htm prints 'Cash paid during the year for income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 134478000 (FILING-CHECKED)
- revenue: era 10-K 0001193125-18-102232 R2.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 5292359000 (FILING-CHECKED)
- cfo: era 10-K 0001193125-18-102232 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 499704000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-102232 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -269760000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-102232 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -51707000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001193125-18-102232 R8.htm prints 'Cash paid during the year for interest' on us-gaap:InterestPaid = 2915000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001193125-19-097973 R8.htm prints 'Payment of dividends' on us-gaap:PaymentsOfDividends = -140325000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 1.
- Random mapped sample: 4 rows, 1 disagreements (25.0%).
