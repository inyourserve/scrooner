# SXT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001140361-26-005311 (CIK 0000310142, filed 2026-02-13): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001140361-16-054898 (CIK 0000310142, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001140361-18-009754 (CIK 0000310142, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001140361-21-005623 (CIK 0000310142, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000310142.json (one call); submissions CIK0000310142.json (SIC 2860).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Revenue | 1612111000 | 1612111000 | 1557228000 | 1557228000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of products sold | 1072811000 | 1072811000 | 1050135000 | 1050135000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Face (R2) lists revenue, cost of products sold and S&A with no gross profit line; segment pages give only revenue and operating income. / pages opened: R21, R39, R66, R67, R68 |
| operating_expenses | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Face shows cost of products sold and selling and administrative expenses separately with no total operating expenses line; segment pages have no total either. / pages opened: R2, R66, R21, R39, R64, R67 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling and administrative expenses | 332172000 | 332172000 | 315514000 | 315514000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R47.htm | Research and development costs | 52900000 | 52900000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R47.htm 'Summary of Significant Accounting Policies, Research and Development (Details)' (MetaLinks.json presentation) |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Operating income | 207128000 | 207128000 | 191579000 | 191579000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R2.htm | Interest expense | 29581000 | 29581000 | 28781000 | 28781000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Earnings before income taxes | 177547000 | 177547000 | 162798000 | 162798000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income taxes | 43058000 | 43058000 | 38132000 | 38132000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net earnings | 134489000 | 134489000 | 124666000 | 124666000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic (in dollars per share) | 3.18 | 3.18 | 2.96 | 2.96 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted (in dollars per share) | 3.16 | 3.16 | 2.94 | 2.94 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic (in shares) | 42236000 | 42236000 | 42145000 | 42145000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted (in shares) | 42595000 | 42595000 | 42396000 | 42396000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 36533000 | 36533000 | 26626000 | 26626000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade accounts receivable | 305380000 | 305380000 | 290087000 | 290087000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 678220000 | 678220000 | 600302000 | 600302000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1081448000 | 1081448000 | 961886000 | 961886000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment, net | 539296000 | 539296000 | 491587000 | 491587000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 439706000 | 439706000 | 411775000 | 411775000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 2244137000 | 2244137000 | 2023794000 | 2023794000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R5.htm | Trade accounts payable | 138344000 | 138344000 | 139052000 | 139052000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 263583000 | 263583000 | 270639000 | 270639000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet (R5) has total current liabilities and total liabilities and shareholders' equity but no total liabilities line; R64 is deferred taxes. / pages opened: R64, R5 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders' equity | 1193514000 | 1193514000 | 1060986000 | 1060986000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 127826000 | 127826000 | 157151000 | 157151000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -92682000 | -92682000 | -59209000 | -59209000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -35035000 | -35035000 | -81546000 | -81546000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Acquisition of property, plant, and equipment | -89409000 | 89409000 | -59212000 | 59212000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 61098000 | 61098000 | 60329000 | 60329000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation expense | 13946000 | 13946000 | 10084000 | 10084000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -69614000 | 69614000 | -69399000 | 69399000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Equity statement shows only treasury-share movements for vesting, benefit plans and 'Other' shares; no repurchase amount is reported. / pages opened: R5, R6, R8, R9 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest | 29356000 | 29356000 | 29107000 | 29107000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes | 48806000 | 48806000 | 56744000 | 56744000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001140361-26-005311 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings + Long-term debt | 709584000 | 709584000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | component_in_note | us-gaap:CommonStockSharesIssued | R6.htm | Common stock, shares issued (in shares) | 53954874 |  |  |  |  | FILING-CHECKED | check: hand / Year-end outstanding is not printed: only issued 53,954,874 and treasury 11,685,819 shares at 2025-12-31 (implied 42,269,055); cover count 42,506,700 is as of 2026-02-03. / pages opened: R1, R2, R6, R46, R8, R9 |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Revenue' on us-gaap:SalesRevenueGoodsNet = 1375964000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 921531000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Selling and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 288092000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001140361-16-054898 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 166341000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 16945000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 149396000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 42149000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 106785000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Earnings per common share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.33 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Earnings per common share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.31 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 45910000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001140361-16-054898 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 46204000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 11997000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Trade accounts receivable, less allowance for losses of $3,871 and $3,838, respe' on us-gaap:AccountsReceivableNetCurrent = 232047000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 409159000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 753343000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Property, Plant and Equipment, Net, Total' on us-gaap:PropertyPlantAndEquipmentNet = 469678000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 399646000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Total assets' on us-gaap:Assets = 1711437000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableTradeCurrent = 95442000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 212922000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001140361-16-054898 R5.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 845127000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 128047000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -75794000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -50134000 (FILING-CHECKED)
- capex: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Acquisition of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -79941000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 47939000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 1598000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -48110000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Interest' on us-gaap:InterestPaid = 16839000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001140361-16-054898 R7.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 46281000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001140361-18-009754 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 886775000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001140361-21-005623 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 137845000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
