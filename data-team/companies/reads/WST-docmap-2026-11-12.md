# WST document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000105770-26-000010 (CIK 0000105770, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000105770-16-000060 (CIK 0000105770, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000105770-18-000006 (CIK 0000105770, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000105770-20-000015 (CIK 0000105770, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000105770.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 3074100000 | 3074100000 | 2893200000 | 2893200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of goods and services sold | 1970100000 | 1970100000 | 1894700000 | 1894700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1104000000 | 1104000000 | 998500000 | 998500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingGeneralAndAdministrativeExpense+wst:OtherIncomeExpense | R3.htm | Research and development + Selling, general and administrative expenses + Other expense (income) (Note 16) | 519100000 |  | 428600000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000105770-26-000010 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 393600000 | 393600000 | 338500000 | 338500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development | 74300000 | 74300000 | 69100000 | 69100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating profit | 584900000 | 584900000 | 569900000 | 569900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 500000 | 500000 | 3000000 | 3000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income before income taxes and equity in net income of affiliated companies | 600900000 | 600900000 | 585500000 | 585500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 121600000 | 121600000 | 107500000 | 107500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 493700000 | 493700000 | 492700000 | 492700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 6.83 | 6.83 | 6.75 | 6.75 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 6.79 | 6.79 | 6.69 | 6.69 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 72300000 | 72300000 | 73000000 | 73000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 72700000 | 72700000 | 73700000 | 73700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 791300000 | 791300000 | 484600000 | 484600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Accounts receivable, net | 574400000 | 574400000 | 552500000 | 552500000 | Y | FILING-CHECKED | accn 0000105770-26-000010 R6.htm period ..2025-12-31 / check: hand R6.htm agree |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 443900000 | 443900000 | 377000000 | 377000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 1978200000 | 1978200000 | 1538100000 | 1538100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 1726400000 | 1726400000 | 1581600000 | 1581600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 109900000 | 109900000 | 106000000 | 106000000 | Y | FILING-CHECKED | accn 0000105770-26-000010 R6.htm period ..2025-12-31 / check: hand R6.htm agree |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total Assets | 4270000000 | 4270000000 | 3643400000 | 3643400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 253700000 | 253700000 | 239300000 | 239300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 654900000 | 654900000 | 550400000 | 550400000 | Y | FILING-CHECKED | accn 0000105770-26-000010 R6.htm period ..2025-12-31 / check: hand R6.htm agree |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total Liabilities | 1094000000 | 1094000000 | 961100000 | 961100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Equity | 3176000000 | 3176000000 | 2682300000 | 2682300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Net cash provided by operating activities | 754800000 | 754800000 | 653400000 | 653400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Net cash used in investing activities | -285900000 | -285900000 | -378700000 | -378700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Net cash used in financing activities | -185100000 | -185100000 | -622600000 | -622600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Capital expenditures | -285900000 | 285900000 | -377000000 | 377000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AdjustmentForAmortization | R10.htm | Depreciation | 171400000 |  | 155400000 |  |  | FILING-CHECKED | Depreciation + Amortization lines on R10 (rule 7) / check: hand R10.htm corrected: R10 prints 'Depreciation' 168.6 and 'Amortization' 2.8 (AdjustmentForAmortization) as separate lines; row held depreciation only. Sum 171.4 / 155.4 (151.8 + 3.6). |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock-based compensation | 23800000 | 23800000 | 18700000 | 18700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Dividend payments | -61200000 | 61200000 | -59100000 | 59100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Shares purchased under share repurchase programs | -134000000 | 134000000 | -560900000 | 560900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R10.htm | Interest paid, net of amounts capitalized | 300000 | 300000 | 500000 | 500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000105770-26-000010 R10.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R10.htm | Income taxes paid, net | 125200000 | 125200000 | 71400000 | 71400000 | Y | FILING-CHECKED | accn 0000105770-26-000010 R10.htm period ..2025-12-31 / check: hand R10.htm agree |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R6.htm | Long-term debt | 202800000 | 202800000 | 202600000 |  | Y | FILING-CHECKED | BS long-term debt only; finance lease liabilities exist in filing (FinanceLeaseLiabilityCurrent/Noncurrent) but lease note R64 not fetched - note page not fetched, lease add pending / check: hand R6.htm corrected: R6 prints only 'Long-term debt' 202.8 / 202.6 (no current debt line). The filing has FinanceLeaseLiability current/noncurrent tags, but the lease note page R64 is NOT FETCHED, so the finance lease amount cannot be read and added. FY1 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 72000000 | 72000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 1399800000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Cost of goods and services sold' on us-gaap:CostOfGoodsAndServicesSold = 944000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 455800000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Research and development + Selling, general and administrative expenses + Other ' on us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingGeneralAndAdministrativeExpense+wst:OtherIncomeExpense = 327200000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 233000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 34100000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Operating profit' on us-gaap:OperatingIncomeLoss = 128600000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 14100000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 116100000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 26300000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Net income' on us-gaap:ProfitLoss = 95600000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.33 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.3 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 72000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000105770-16-000060 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 73800000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Cash, including cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 274600000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 181400000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 181100000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 673700000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 721000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 104600000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Total Assets' on us-gaap:Assets = 1695100000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 119800000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 314300000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000105770-16-000060 R5.htm prints 'Total Liabilities' on us-gaap:Liabilities = 671200000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000105770-16-000060 R5.htm read; no row matched (auto)
- cfo: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 212400000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -129500000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -41500000 (FILING-CHECKED)
- capex: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -131600000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000105770-16-000060 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 29600000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Dividend payments' on us-gaap:PaymentsOfDividendsCommonStock = -32400000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Shares repurchased for employee tax withholdings' on us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation = -5600000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Interest paid, net of amounts capitalized' on us-gaap:InterestPaidNet = 14700000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000105770-16-000060 R8.htm prints 'Income taxes paid, net' on us-gaap:IncomeTaxesPaidNet = 33100000 (FILING-CHECKED)
- revenue: era 10-K 0000105770-18-000006 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 1599100000 (FILING-CHECKED)
- revenue: era 10-K 0000105770-20-000015 R2.htm prints 'Net sales' on us-gaap:Revenues = 1839900000 (FILING-CHECKED)
- net_income: era 10-K 0000105770-20-000015 R2.htm prints 'Net income' on us-gaap:ProfitLoss = 241700000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingGeneralAndAdministrativeExpense+wst:OtherIncomeExpense)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 2.
- Random mapped sample: 4 rows, 0 disagreements (0.0%).
