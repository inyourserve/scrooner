# CSX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000277948-26-000006 (CIK 0000277948, filed 2026-02-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000277948-16-000046 (CIK 0000277948, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000277948-18-000009 (CIK 0000277948, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000277948-24-000010 (CIK 0000277948, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- companyfacts CIK0000277948.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 14092000000 | 14092000000 | 14540000000 | 14540000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (993 tags across all 120 R pages, face and notes) of 0000277948-26-000006; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (993 tags across all 120 R pages, face and notes) of 0000277948-26-000006; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (993 tags across all 120 R pages, face and notes) of 0000277948-26-000006; no face row matched |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (993 tags across all 120 R pages, face and notes) of 0000277948-26-000006; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (993 tags across all 120 R pages, face and notes) of 0000277948-26-000006; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 4521000000 | 4521000000 | 5245000000 | 5245000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest Expense | -844000000 | 844000000 | -832000000 | 832000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings Before Income Taxes | 3769000000 | 3769000000 | 4555000000 | 4555000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Tax Expense (Note 12) | -880000000 | 880000000 | -1085000000 | 1085000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Earnings | 2889000000 | 2889000000 | 3470000000 | 3470000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 1.54 | 1.54 | 1.79 | 1.79 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Assuming Dilution (in dollars per share) | 1.54 | 1.54 | 1.79 | 1.79 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 1870000000 | 1870000000 | 1939000000 | 1939000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Assuming Dilution (in shares) | 1873000000 | 1873000000 | 1943000000 | 1943000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R5.htm | Cash and Cash Equivalents | 670000000 | 670000000 | 933000000 | 933000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts Receivable - Net (Note 11) | 1298000000 | 1298000000 | 1326000000 | 1326000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (993 tags across all 120 R pages, face and notes) of 0000277948-26-000006; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total Current Assets | 2550000000 | 2550000000 | 2820000000 | 2820000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Properties - Net (Note 6) | 36811000000 | 36811000000 | 35658000000 | 35658000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R5.htm | Goodwill and Other Intangible Assets - Net (Note 18) | 267000000 | 267000000 | 433000000 | 433000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 43682000000 | 43682000000 | 42764000000 | 42764000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts Payable | 1149000000 | 1149000000 | 1118000000 | 1118000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total Current Liabilities | 3133000000 | 3133000000 | 3276000000 | 3276000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total Liabilities | 30522000000 | 30522000000 | 30257000000 | 30257000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R5.htm | Total Shareholders' Equity | 13160000000 | 13160000000 | 12507000000 | 12507000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000277948-26-000006 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net Cash Provided by Operating Activities | 4613000000 | 4613000000 | 5247000000 | 5247000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash Used in Investing Activities | -2851000000 | -2851000000 | -2605000000 | -2605000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net Cash Used in Financing Activities | -2025000000 | -2025000000 | -3062000000 | -3062000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Property Additions | -2902000000 | 2902000000 | -2529000000 | 2529000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and Amortization | 1680000000 | 1680000000 | 1658000000 | 1658000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R56.htm | Stock Plans and Share-Based Compensation - Schedule of Share-Based Compensation and Related Income Tax Benefit (Details) |  | 54000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R56.htm 'Stock Plans and Share-Based Compensation - Schedule of Share-Based Compensation ' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends Paid | -972000000 | 972000000 | -930000000 | 930000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Shares Repurchased | -1396000000 | 1396000000 | -2237000000 | 2237000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest Paid - Net of Amounts Capitalized | 870000000 | 870000000 | 850000000 | 850000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income Taxes Paid (Note 12) | 1102000000 | 1102000000 | 1076000000 | 1076000000 | Y | FILING-CHECKED | accn 0000277948-26-000006 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current Maturities of Long-term Debt (Note 10) + Long-term Debt (Note 10) | 18873000000 | 18873000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R54.htm | Shareholders' Equity - Schedule of Common and Preferred Stock (Details) |  | 1860000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R54.htm 'Shareholders' Equity - Schedule of Common and Preferred Stock (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 11811000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 3584000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Interest Expense' on us-gaap:InterestExpense = -544000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Earnings Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 3138000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Income Tax Expense' on us-gaap:IncomeTaxExpenseBenefit = -1170000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Net Earnings' on us-gaap:NetIncomeLoss = 1968000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Net Earnings Per Share, Basic (dollars per share)' on us-gaap:EarningsPerShareBasic = 2 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Net Earnings Per Share, Assuming Dilution (dollars per share)' on us-gaap:EarningsPerShareDiluted = 2 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Average Common Shares Outstanding, Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 983000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000277948-16-000046 R2.htm prints 'Average Common Shares Outstanding, Assuming Dilution (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 984000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 628000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Accounts Receivable - Net' on us-gaap:AccountsReceivableNetCurrent = 982000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 2966000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Properties - Net' on us-gaap:PropertyPlantAndEquipmentNet = 30174000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000277948-16-000046 R4.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Total Assets' on us-gaap:Assets = 35039000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Accounts Payable' on us-gaap:AccountsPayableCurrent = 764000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 1952000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Total Liabilities' on us-gaap:Liabilities = 23371000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000277948-16-000046 R4.htm prints 'Total Shareholders' Equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 11668000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 3370000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Net Cash Used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -2892000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Net Cash Used in Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -519000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Property Additions' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -2562000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000277948-16-000046 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000277948-16-000046 R6.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Dividends Paid' on us-gaap:PaymentsOfDividendsCommonStock = -686000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Shares Repurchased' on us-gaap:PaymentsForRepurchaseOfCommonStock = -804000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Interest Paid - Net of Amounts Capitalized' on us-gaap:InterestPaidNet = 566000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000277948-16-000046 R6.htm prints 'Income Taxes Paid' on us-gaap:IncomeTaxesPaid = 768000000 (FILING-CHECKED)
- revenue: era 10-K 0000277948-18-000009 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 11408000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000277948-18-000009 R2.htm prints 'Interest Expense' on us-gaap:InterestExpense = -546000000 (FILING-CHECKED)
- goodwill: era 10-K 0000277948-18-000009 R4.htm read; no row matched (auto)
- interest_expense: era 10-K 0000277948-24-000010 R3.htm prints 'Interest Expense' on us-gaap:InterestIncomeExpenseNet = -809000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:OperatingCostsAndExpenses (R3.htm): 2026-11-12 R3.htm: corrected: CSX prints no cost of revenue; 'Total Expense' = 14,092 - 4,521 OI = 9,571 is the opex total (CME precedent)
- sga_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R56.htm): 2026-11-12 R56.htm: agree: R56 'Total Share-based Compensation Expense' 54
- total_debt: component sum us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: agree: R5 lines on LongTermDebtAndCapitalLeaseObligations (leases inside by tag, finance-lease ruling (founder 2026-11-04 item 5))
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R54.htm): 2026-11-12 R54.htm: agree: R54 table 'Common Shares Outstanding' 1,860 (shares in millions) at 2025-12-31; table value, PEP precedent
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Revenue' is the revenue line, printed 14092000000 = filing XBRL 14092000000; agrees
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Interest Expense' is the interest_expense line, printed -844000000 = filing XBRL 844000000; agrees
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Earnings Before Income Taxes' is the income_before_tax line, printed 3769000000 = filing XBRL 3769000000; agrees
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income Tax Expense (Note 12)' is the income_tax_expense line, printed -880000000 = filing XBRL 880000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total Current Assets' is the current_assets line, printed 2550000000 = filing XBRL 2550000000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total Current Liabilities' is the current_liabilities line, printed 3133000000 = filing XBRL 3133000000; agrees
