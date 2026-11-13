# HPQ document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000047217-25-000071 (CIK 0000047217, filed 2025-12-10): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001047469-15-009251 (CIK 0000047217, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000047217-19-000071 (CIK 0000047217, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000047217-16-000093 (CIK 0000047217, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000047217.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total net revenue | 55295000000 | 55295000000 | 53559000000 | 53559000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Total cost of net revenue | 43903000000 | 43903000000 | 41741000000 | 41741000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 11392000000 | 11392000000 | 11818000000 | 11818000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| operating_expenses | mapped | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 8218000000 | 8218000000 | 8000000000 | 8000000000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 5821000000 | 5821000000 | 5658000000 | 5658000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 1602000000 | 1602000000 | 1640000000 | 1640000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Earnings from operations | 3174000000 | 3174000000 | 3818000000 | 3818000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R102.htm | Supplementary Financial Information - Schedule of Interest and other, net (Details) | -430000000 | 430000000 | -452000000 |  | Y (sign differs: printed in parentheses) | FILING-CHECKED | not on the face statement; shown in R102.htm 'Supplementary Financial Information - Schedule of Interest and other, net (Detai' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R102.htm corrected: R3 prints only 'Interest and other, net' (506); note R102 prints gross 'Interest expense on borrowings' InterestExpenseDebt (430) / (452); printed values were blank. |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before taxes | 2668000000 | 2668000000 | 3279000000 | 3279000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | (Provision for) benefit from taxes | -139000000 | 139000000 | -504000000 | 504000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 2529000000 | 2529000000 | 2775000000 | 2775000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 2.67 | 2.67 | 2.83 | 2.83 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 2.65 | 2.65 | 2.81 | 2.81 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 946000000 | 946000000 | 979000000 | 979000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 953000000 | 953000000 | 989000000 | 989000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R3.htm period ..2025-10-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash, cash equivalents and restricted cash | 3705000000 | 3705000000 | 3253000000 | 3253000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net of allowance for credit losses of $83 as of October 31, 2025 and 2024 | 5692000000 | 5692000000 | 5117000000 | 5117000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventory | 8512000000 | 8512000000 | 7720000000 | 7720000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 22453000000 | 22453000000 | 20760000000 | 20760000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 3049000000 | 3049000000 | 2914000000 | 2914000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 8706000000 | 8706000000 | 8627000000 | 8627000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 41769000000 | 41769000000 | 39909000000 | 39909000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 18051000000 | 18051000000 | 16903000000 | 16903000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 29258000000 | 29258000000 | 28687000000 | 28687000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R5.htm period ..2025-10-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1151 tags across all 137 R pages, face and notes) of 0000047217-25-000071; no face row matched / check: hand R5.htm agree |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ deficit | -346000000 | -346000000 | -1323000000 | -1323000000 | Y | FILING-CHECKED | accn 0000047217-25-000071 R5.htm period ..2025-10-31 / check: hand R5.htm agree |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 3697000000 | 3697000000 | 3749000000 | 3749000000 | Y | FILING-CHECKED | accn 0000047217-25-000071 R7.htm period ..2025-10-31 / check: hand R7.htm agree |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -1177000000 | -1177000000 | -646000000 | -646000000 | Y | FILING-CHECKED | accn 0000047217-25-000071 R7.htm period ..2025-10-31 / check: hand R7.htm agree |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -2060000000 | -2060000000 | -3082000000 | -3082000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Investment in property, plant, equipment and purchased intangibles, net | -897000000 | 897000000 | -592000000 | 592000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation, amortization and impairment | 916000000 | 916000000 | 830000000 | 830000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 522000000 | 522000000 | 452000000 | 452000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Cash dividends paid | -1088000000 | 1088000000 | -1075000000 | 1075000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -850000000 | 850000000 | -2100000000 | 2100000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest expense paid | 437000000 | 437000000 | 441000000 | 441000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000047217-25-000071 R7.htm period ..2025-10-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid, net of refunds | 535000000 | 535000000 | 649000000 | 649000000 | Y | FILING-CHECKED | accn 0000047217-25-000071 R7.htm period ..2025-10-31 / check: hand R7.htm agree |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Notes payable and short-term borrowings + Long-term debt | 9666000000 | 9666000000 | 9669000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R5.htm corrected: R5 'Notes payable and short-term borrowings' 845 + 'Long-term debt' 8,821 = 9,666 (FY1 1,406 + 8,263 = 9,669); no finance lease tags in filing. FY1 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 921000000 | 921000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-10-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Total net revenue' on us-gaap:Revenues = 103355000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Cost of products' on us-gaap:CostOfGoodsSold = 53081000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001047469-15-009251 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 97884000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 12185000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 3502000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Earnings from operations' on us-gaap:OperatingIncomeLoss = 5471000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001047469-15-009251 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Earnings before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4732000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Provision for taxes' on us-gaap:IncomeTaxExpenseBenefit = -178000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 4554000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.51 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.48 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 1814000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001047469-15-009251 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 1836000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 17433000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Accounts receivable' on us-gaap:AccountsReceivableNetCurrent = 13363000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Inventory' on us-gaap:InventoryNet = 6485000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 51787000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 11090000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 32941000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Total assets' on us-gaap:Assets = 106882000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 15956000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 42191000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001047469-15-009251 R4.htm prints 'Total HP stockholders' equity' on us-gaap:StockholdersEquity = 27768000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 6490000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -5534000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 1344000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Investment in property, plant and equipment' on us-gaap:PaymentsToAcquireProductiveAssets = -3603000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 4061000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 709000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -1250000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2883000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Interest expense paid' on us-gaap:InterestPaid = 532000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001047469-15-009251 R6.htm prints 'Income taxes paid, net of refunds' on us-gaap:IncomeTaxesPaidNet = 1012000000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000047217-19-000071 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 4537000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000047217-16-000093 R6.htm prints 'Interest expense paid' on us-gaap:InterestPaid = 318000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 4 rows, 0 disagreements (0.0%).
