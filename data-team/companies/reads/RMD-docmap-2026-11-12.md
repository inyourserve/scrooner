# RMD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000943819-26-000047 (CIK 0000943819, filed 2026-08-13): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001193125-15-281887 (CIK 0000943819, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000943819-18-000013 (CIK 0000943819, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000943819-21-000017 (CIK 0000943819, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0000943819.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net revenue | 5653443000 | 5653443000 | 5146327000 | 5146327000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Total cost of sales | 2201704000 | 2201704000 | 2091357000 | 2091357000 | Y | FILING-CHECKED | accn 0000943819-26-000047 R5.htm period ..2026-06-30 / check: hand R5.htm agree |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 3451739000 | 3451739000 | 3054970000 | 3054970000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1565024000 | 1565024000 | 1369607000 | 1369607000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general, and administrative | 1119528000 | 1119528000 | 993050000 | 993050000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 378285000 | 378285000 | 331284000 | 331284000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 1886715000 | 1886715000 | 1685363000 | 1685363000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R5.htm | Interest income (expense), net | 49914000 | 49914000 | 4114000 | 4114000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1919416000 | 1919416000 | 1677566000 | 1677566000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income taxes (note 12) | 396123000 | 396123000 | 276843000 | 276843000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1523293000 | 1523293000 | 1400723000 | 1400723000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share (note 11) (in dollars per share) | 10.47 | 10.47 | 9.55 | 9.55 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share (note 11) (in dollars per share) | 10.43 | 10.43 | 9.51 | 9.51 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic shares outstanding (000's) (in shares) | 145523000 | 145523000 | 146716000 | 146716000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted shares outstanding (000's) (in shares) | 146054000 | 146054000 | 147340000 | 147340000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R5.htm period ..2026-06-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1469234000 | 1469234000 | 1209450000 | 1209450000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances of $25,839 and $22,424 ‎at June 30, 2026 and June 30, 2025, respectively | 1036233000 | 1036233000 | 939492000 | 939492000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories (note 4) | 945805000 | 945805000 | 927711000 | 927711000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4324739000 | 4324739000 | 3505605000 | 3505605000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net (note 4) | 581829000 | 581829000 | 550790000 | 550790000 | Y | FILING-CHECKED | accn 0000943819-26-000047 R3.htm period ..2026-06-30 / check: hand R3.htm agree |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill (note 5) | 2909575000 | 2909575000 | 3046680000 | 3046680000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 8965950000 | 8965950000 | 8174391000 | 8174391000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 308923000 | 308923000 | 278157000 | 278157000 | Y | FILING-CHECKED | accn 0000943819-26-000047 R3.htm period ..2026-06-30 / check: hand R3.htm agree |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1395110000 | 1395110000 | 1019120000 | 1019120000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2380557000 | 2380557000 | 2206532000 | 2206532000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 6585393000 | 6585393000 | 5967859000 | 5967859000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R3.htm period ..2026-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 1805829000 | 1805829000 | 1751588000 | 1751588000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -545199000 | -545199000 | -200045000 | -200045000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | -1007029000 | -1007029000 | -606253000 | -606253000 | Y | FILING-CHECKED | accn 0000943819-26-000047 R9.htm period ..2026-06-30 / check: hand R9.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property, plant and equipment | -156285000 | 156285000 | -89865000 | 89865000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 201342000 | 201342000 | 198473000 | 198473000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation costs (note 10) | 104348000 | 104348000 | 91661000 | 91661000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Dividends paid | -349662000 | 349662000 | -310880000 | 310880000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchases of treasury stock | -700037000 | 700037000 | -300025000 | 300025000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 27057000 | 27057000 | 28415000 | 28415000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid, net of refunds | 357167000 | 357167000 | 214013000 | 214013000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000943819-26-000047 R9.htm period ..2026-06-30 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R3.htm | Short-term debt, net (note 8) + Long-term debt, net (note 8) | 659365000 | 659365000 | 668292000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm corrected: R3 Short-term debt, net 259,950 + Long-term debt, net 399,415 = 659,365; no finance-lease tags in filing; FY25 9,900 + 658,392 = 668,292 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 144239563 | 144239563 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-06-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Net revenue' on us-gaap:SalesRevenueNet = 1678912000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Cost of sales (excluding amortization of acquired intangible assets)' on us-gaap:CostOfGoodsSold = 667516000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 1011396000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 602160000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 478627000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 114865000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 409236000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -5778000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 435916000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Income taxes (note 14)' on us-gaap:IncomeTaxExpenseBenefit = 83030000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 352886000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic = 2.51 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Diluted earnings per share (note 4)' on us-gaap:EarningsPerShareDiluted = 2.47 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Basic shares outstanding (000's)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 140468000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-15-281887 R4.htm prints 'Diluted shares outstanding (000's)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 142687000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 717249000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $12,276 and $10,9' on us-gaap:AccountsReceivableNetCurrent = 362568000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Inventories (note 5)' on us-gaap:InventoryNet = 246859000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1444182000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Property, plant and equipment, net (note 6)' on us-gaap:PropertyPlantAndEquipmentNet = 387758000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Goodwill and other intangible assets, net (note 7)' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 311403000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Total assets' on us-gaap:Assets = 2184260000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 81112000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 267259000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 596953000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-15-281887 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1587307000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 383180000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -143071000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -255791000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -62502000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 73056000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Stock-based compensation costs' on us-gaap:ShareBasedCompensation = 47855000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -157262000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -160300000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 5778000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-15-281887 R7.htm prints 'Income taxes paid, net of refunds' on us-gaap:IncomeTaxesPaidNet = 48533000 (FILING-CHECKED)
- revenue: era 10-K 0000943819-18-000013 R4.htm prints 'Net revenue' on us-gaap:SalesRevenueGoodsNet = 2340196000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000943819-18-000013 R4.htm prints 'Cost of sales (excluding amortization of acquired intangible assets)' on us-gaap:CostOfGoodsSold = 978032000 (FILING-CHECKED)
- interest_expense: era 10-K 0000943819-21-000017 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -23989000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 5 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 1.
- Random mapped sample: 4 rows, 0 disagreements (0.0%).
