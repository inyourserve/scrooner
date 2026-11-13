# NPO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-009798 (CIK 0001164863, filed 2026-02-19): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0001164863-16-000040 (CIK 0001164863, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm
- 10-K 0001164863-19-000007 (CIK 0001164863, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm
- 10-K 0001164863-24-000015 (CIK 0001164863, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- companyfacts CIK0001164863.json (one call); submissions CIK0001164863.json (SIC 3050).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Net sales | 1143300000 | 1143300000 | 1048700000 | 1048700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 655800000 | 655800000 | 603900000 | 603900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 487500000 | 487500000 | 444800000 | 444800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 325900000 | 325900000 | 302500000 | 302500000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 323400000 | 323400000 | 296300000 | 296300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R52.htm | Total research and development expenditures | 13300000 | 13300000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R52.htm 'Overview, Basis of Presentation, and Significant Accounting Policies (Details)' (MetaLinks.json presentation) |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 161600000 | 161600000 | 142300000 | 142300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -34000000 | 34000000 | -40900000 | 40900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 57600000 | 57600000 | 94400000 | 94400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | -17100000 | 17100000 | -21500000 | 21500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 40500000 | 40500000 | 72900000 | 72900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income per share (in dollars per share) | 1.92 | 1.92 | 3.48 | 3.48 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income per share (in dollars per share) | 1.91 | 1.91 | 3.45 | 3.45 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R67.htm | Weighted-average shares – basic (in shares) | 21000000 | 21000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R67.htm 'Earnings Per Share - Schedule of Computation of Basic and Diluted Earnings Per S' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R67.htm | Weighted-average shares – diluted (in shares) | 21200000 | 21200000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R67.htm 'Earnings Per Share - Schedule of Computation of Basic and Diluted Earnings Per S' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 114700000 | 114700000 | 236300000 | 236300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndNotesReceivableNet | R6.htm | Accounts receivable, less allowance for doubtful accounts of $2.0 in 2025 and of $1.0 in 2024 | 134100000 |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet R6 prints 'Accounts receivable, less allowance' of 134.1M, tagged with the accounts-and-notes receivable element. / pages opened: R5, R6, R7, R54, R57, R63 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 153800000 | 153800000 | 138800000 | 138800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 437700000 | 437700000 | 5.123e+08 | 512300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 221500000 | 221500000 | 193200000 | 193200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1064800000 | 1064800000 | 896200000 | 896200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 2663000000 | 2663000000 | 2491500000 | 2491500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 71600000 | 71600000 | 66000000 | 66000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 188700000 | 188700000 | 198000000 | 198000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 1119100000 | 1119100000 | 1.063e+09 | 1062900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total shareholders’ equity | 1543900000 | 1543900000 | 1428600000 | 1428600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R5.htm | Net cash provided by operating activities of continuing operations | 201200000 | 201200000 | 162900000 | 162900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used in investing activities of continuing operations | -316900000 | -316900000 | -241500000 | -241500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash used in financing activities of continuing operations | -17400000 | -17400000 | -50500000 | -50500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R5.htm | Purchases of property, plant and equipment | -42000000 | 42000000 | -29100000 | 29100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AdjustmentForAmortization | R5.htm | Depreciation + Amortization | 102800000 | 102800000 | 1.003e+08 | 100300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Stock-based compensation | 13500000 | 13500000 | 12000000 | 12000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R5.htm | Dividends paid | -26200000 | 26200000 | -25300000 | 25300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No repurchases in 2025: the cash flow financing section (R5) has no buyback line, treasury stock is essentially unchanged (174,546 shares), and R94 shows only the 50M authorization and a zero-share 2024 figure. / pages opened: R6, R7, R94, R8, R9, R24, R5 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R5.htm | Interest | 33500000 | 33500000 | 38900000 | 38900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R5.htm | Income taxes, net of refunds received | 41400000 | 41400000 | 36100000 | 36100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-009798 R5.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current maturities of long-term debt + Long-term debt | 6.553e+08 | 655300000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R8.htm | Balance (in shares) at Dec. 31, 2025 | 21100000 |  |  |  |  | FILING-CHECKED | check: hand / Equity statement R8 tags the year-end outstanding balance as 21.1 million shares (printed rounded in millions; issued 21,240,597 less treasury 174,546 = 21,066,051). / pages opened: R1, R7, R8, R67, R9, R14 |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 1204400000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 808900000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 395500000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 357900000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 302800000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001164863-16-000040 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 37600000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -52800000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -18600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -2300000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Net income (loss)' on us-gaap:NetIncomeLoss = -20900000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Basic earnings (loss) per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = -0.93 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001164863-16-000040 R2.htm prints 'Diluted earnings (loss) per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = -0.93 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001164863-16-000040 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001164863-16-000040 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 103400000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 178400000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 517900000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 211500000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 195900000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Total assets' on us-gaap:Assets = 1503500000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 101500000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 278700000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 1043700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001164863-16-000040 R5.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 459800000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 86500000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -86500000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -85200000 (FILING-CHECKED)
- capex: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -36800000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001164863-16-000040 R4.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 4099999 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -18000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Interest' on us-gaap:InterestPaid = 36400000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001164863-16-000040 R4.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 20400000 (FILING-CHECKED)
- revenue: era 10-K 0001164863-19-000007 R2.htm prints 'Net sales' on us-gaap:Revenues = 1532000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001164863-19-000007 R4.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -252400000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001164863-19-000007 R4.htm prints 'Interest' on us-gaap:InterestPaid = 3.33e+07 (FILING-CHECKED)
- interest_expense: era 10-K 0001164863-24-000015 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -45000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
