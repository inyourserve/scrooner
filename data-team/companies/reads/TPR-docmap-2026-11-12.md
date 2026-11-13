# TPR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001116132-26-000018 (CIK 0001116132, filed 2026-08-13): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001116132-15-000010 (CIK 0001116132, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001116132-17-000011 (CIK 0001116132, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001116132-18-000021 (CIK 0001116132, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001116132.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net sales | 8004200000 | 8004200000 | 7010700000 | 7010700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of sales | 1775200000 | 1775200000 | 1721800000 | 1721800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 6229000000 | 6229000000 | 5288900000 | 5288900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GoodwillAndIntangibleAssetImpairment | R5.htm | Other selling, general and administrative expenses + Impairment of goodwill and intangible assets | 4314600000 | 4314600000 | 4873900000 | 4873900000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001116132-26-000018 R5.htm period ..2026-06-27 / check: hand R5.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Other selling, general and administrative expenses | 4314600000 | 4314600000 | 4019100000 | 4019100000 | Y | FILING-CHECKED | accn 0001116132-26-000018 R5.htm period ..2026-06-27 / check: hand R5.htm agree |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (940 tags across all 101 R pages, face and notes) of 0001116132-26-000018; no face row matched / check: hand R5.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income (loss) | 1914400000 | 1914400000 | 415000000 | 415000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNet | R5.htm | Interest expense, net | 55200000 | -55200000 | 85400000 | -85400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | net interest line 'Interest expense, net' (InterestIncomeExpenseNet); no gross interest expense line on the face / check: hand R5.htm corrected: Face line is 'Interest expense, net' 55.2 (FY1 85.4) tagged InterestIncomeExpenseNet: a net line -> combined (rule 6). |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before provision for income taxes | 1860600000 | 1860600000 | 216100000 | 216100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision (benefit) for income taxes | 332900000 | 332900000 | 32900000 | 32900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) | 1527700000 | 1527700000 | 183200000 | 183200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (USD per share) | 7.49 | 7.49 | 0.84 | 0.84 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (USD per share) | 7.27 | 7.27 | 0.82 | 0.82 | Y | FILING-CHECKED | accn 0001116132-26-000018 R5.htm period ..2026-06-27 / check: hand R5.htm agree |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (shares) | 204000000 | 204000000 | 216800000 | 216800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (shares) | 210200000 | 210200000 | 222500000 | 222500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R5.htm period ..2026-06-27 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 974700000 | 974700000 | 1100000000 | 1100000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade accounts receivable, less allowances for credit losses of $6.1 and $5.7, respectively | 237100000 | 237100000 | 239300000 | 239300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 826200000 | 826200000 | 860700000 | 860700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2882300000 | 2882300000 | 2905600000 | 2905600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net of accumulated depreciation of $1,264.2 and $1,215.0, respectively | 502100000 | 502100000 | 489500000 | 489500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 957700000 | 957700000 | 983300000 | 983300000 | Y | FILING-CHECKED | accn 0001116132-26-000018 R3.htm period ..2026-06-27 / check: hand R3.htm agree |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 6691700000 | 6691700000 | 6580500000 | 6580500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 582300000 | 582300000 | 456100000 | 456100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1645000000 | 1645000000 | 1556900000 | 1556900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 5999600000 | 5999600000 | 5722700000 | 5722700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 692100000 | 692100000 | 857800000 | 857800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R3.htm period ..2026-06-27 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 1978500000 | 1978500000 | 1216600000 | 1216600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -218300000 | -218300000 | 914000000 | 914000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | -1860900000 | -1860900000 | -7175200000 | -7175200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment | -166000000 | 166000000 | -122700000 | 122700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 160800000 | 160800000 | 162900000 | 162900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based compensation | 104500000 | 104500000 | 87300000 | 87300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Payment of dividends | -326100000 | 326100000 | -299300000 | 299300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of common stock | -1554600000 | 1554600000 | -1718700000 | 1718700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 241600000 | 241600000 | 394900000 | 394900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid for income taxes, net | 200700000 | 200700000 | 189500000 | 189500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001116132-26-000018 R9.htm period ..2026-06-27 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebt | R3.htm | Current debt + Long-term debt | 2379000000 | 2379000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (shares) | 200400000 | 200400000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-06-27; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 4.192e+09 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 1283000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 2908600000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 2290600000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 2290600000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 618000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001116132-15-000010 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 611600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 209200000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 402400000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Basic (USD per share)' on us-gaap:EarningsPerShareBasic = 1.46 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Diluted (USD per share)' on us-gaap:EarningsPerShareDiluted = 1.45 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 275700000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001116132-15-000010 R4.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 277200000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1291800000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Trade accounts receivable, less allowances of $3.1 and $1.4, respectively' on us-gaap:AccountsReceivableNetCurrent = 219500000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 485100000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2506500000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 732600000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 434200000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Total assets' on us-gaap:Assets = 4666900000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 222800000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 834700000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2177000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001116132-15-000010 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 2489900000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 937400000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -612900000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 389300000 (FILING-CHECKED)
- capex: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -199300000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Depreciation and amortization' on coh:DepreciationDepletionAndAmortizationExcludingTransformationCharges = 191800000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 88900000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Dividend payments' on us-gaap:PaymentsOfDividends = -371800000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 1400000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001116132-15-000010 R8.htm prints 'Cash paid for income taxes, net' on us-gaap:IncomeTaxesPaid = 180300000 (FILING-CHECKED)
- revenue: era 10-K 0001116132-17-000011 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 4488300000 (FILING-CHECKED)
- revenue: era 10-K 0001116132-18-000021 R4.htm prints 'Net sales' on us-gaap:Revenues = 5880000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001116132-18-000021 R8.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 63000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 1.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
