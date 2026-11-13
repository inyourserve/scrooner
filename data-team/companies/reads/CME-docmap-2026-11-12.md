# CME document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001156375-26-000009 (CIK 0001156375, filed 2026-02-26): COVER R1.htm, BS R3.htm, IS R4.htm, CI R5.htm, BSP R7.htm, CF R8.htm
- 10-K 0001156375-16-000116 (CIK 0001156375, filed FY2015 era): COVER R1.htm, BS R2.htm, IS R4.htm, CI R5.htm, BSP R7.htm, CF R8.htm
- 10-K 0001156375-20-000013 (CIK 0001156375, era filing): COVER R1.htm, BS R2.htm, IS R4.htm, CI R5.htm, BSP R7.htm, CF R8.htm
- 10-K 0001156375-19-000010 (CIK 0001156375, era filing): COVER R1.htm, BS R2.htm, IS R4.htm, CI R5.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0001156375.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total Revenues | 6520600000 | 6520600000 | 6130100000 | 6130100000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total Expenses | 2291100000 | 2291100000 | 2198600000 | 2198600000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating Income | 4229500000 | 4229500000 | 3931500000 | 3931500000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest | R4.htm | Income before Income Taxes | 5330500000 | 5330500000 | 4541400000 | 4541400000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax provision | 1258300000 | 1258300000 | 1015600000 | 1015600000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to CME Group | 4072200000 | 4072200000 | 3525800000 | 3525800000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic | 11.18 | 11.18 | 9.69 | 9.69 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted | 11.16 | 11.16 | 9.67 | 9.67 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 359648000 | 359648000 | 359389000 | 359389000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 360310000 | 360310000 | 359944000 | 359944000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 4416900000 | 4416900000 | 2892400000 | 2892400000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance | 639200000 | 639200000 | 573100000 | 573100000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 165359300000 | 165359300000 | 103033500000 | 103033500000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, net of accumulated depreciation and amortization | 362700000 | 362700000 | 386200000 | 386200000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 10514700000 | 10514700000 | 10486900000 | 10486900000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 198424200000 | 198424200000 | 137447000000 | 137447000000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 71800000 | 71800000 | 79900000 | 79900000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 160296700000 | 160296700000 | 102313900000 | 102313900000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 169696000000 | 169696000000 | 110960100000 | 110960100000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total CME Group Shareholders' Equity | 28728200000 | 28728200000 | 26486900000 | 26486900000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net Cash Provided by Operating Activities | 4277100000 | 4277100000 | 3690500000 | 3690500000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net Cash Used in Investing Activities | 1498800000 | 1498800000 | -82600000 | -82600000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Cash Provided by (Used in) Financing Activity, Including Discontinued Operation | 56509500000 | 56509500000 | 5076500000 | 5076500000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, net | -83500000 | 83500000 | -94000000 | 94000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 107500000 | 107500000 | 115100000 | 115100000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 94800000 | 94800000 | 89500000 | 89500000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Cash dividends | -3933000000 | 3933000000 | -3584200000 | 3584200000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (935 tags across all 100 R pages, face and notes) of 0001156375-26-000009; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 135600000 | 135600000 | 129900000 | 129900000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes paid | 1164000000 | 1164000000 | 1196500000 | 1196500000 | Y | FILING-CHECKED | accn 0001156375-26-000009 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings | R3.htm | Short-term debt | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R88.htm | Capital Stock (Capital stock) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R88.htm 'Capital Stock (Capital stock) (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Total Revenues' on us-gaap:Revenues = 3326800000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Total Expenses' on us-gaap:CostsAndExpenses = 1338100000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 1988700000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Income (Loss) from Continuing Operations before Income Taxes, Extraordinary Item' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1956800000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 709800000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Net Income Attributable to CME Group' on us-gaap:NetIncomeLoss = 1247000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 3.71 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 3.69 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 336224000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001156375-16-000116 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 337894000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1692600000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Accounts receivable, net of allowance' on us-gaap:AccountsReceivableNetCurrent = 357800000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 37904500000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Property, net of accumulated depreciation and amortization' on us-gaap:PropertyPlantAndEquipmentNet = 491700000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 7569000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Total Assets' on us-gaap:Assets = 67371500000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 28700000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 36824500000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 46819700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001156375-16-000116 R2.htm prints 'Total Shareholders' Equity' on us-gaap:StockholdersEquity = 20551800000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1515300000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Net Cash Provided by (Used in) Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 17900000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Net Cash Provided by (Used in) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -1206700000 (FILING-CHECKED)
- capex: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Purchases of property, net' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -114200000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 1.292e+08 (FILING-CHECKED)
- sbc: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 60800000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Cash dividends' on us-gaap:PaymentsOfDividends = -1343400000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Interest paid (excluding securities lending program)' on us-gaap:InterestPaid = 89100000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001156375-16-000116 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 716600000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001156375-20-000013 R4.htm prints 'Income from before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 2689600000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001156375-19-000010 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 108300000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:CostsAndExpenses (R4.htm): 2026-11-12 R4.htm: corrected: CME prints no cost of revenue; 'Total Expenses' = 6,520.6 - 4,229.5 OI = 2,291.1 is the opex total
- sga_expense: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- interest_expense: mapped us-gaap:InterestAndDebtExpense (R4.htm): 2026-11-12 R4.htm: corrected: gross borrowing cost line on the face (tool's tag set missed InterestAndDebtExpense)
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- share_buybacks: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:UnsecuredLongTermDebt (R3.htm): 2026-11-12 R3.htm: corrected: the tool left out 'Long-term debt' (UnsecuredLongTermDebt 3,422.3); 0.0 + 3,422.3
- shares_outstanding: review us-gaap:CommonStockSharesOutstanding (R88.htm): 2026-11-12 R88.htm: NOTE R88 row carries no value and the companyfacts has no BS-date fact for this accession; R88 read owed
- revenue: mapped us-gaap:Revenues (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: IS R4.htm 'Total Revenues' is the revenue line, printed 6520600000 = filing XBRL 6520600000; agrees
- income_before_tax: mapped us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: IS R4.htm 'Income before Income Taxes' is the income_before_tax line, printed 5330500000 = filing XBRL 5330500000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: IS R4.htm 'Basic' is the basic_eps line, printed 11.18 = filing XBRL 11.18; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts receivable, net of allowance' is the accounts_receivable line, printed 639200000 = filing XBRL 639200000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current liabilities' is the current_liabilities line, printed 160296700000 = filing XBRL 160296700000; agrees
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Interest paid' is the cash_paid_for_interest line, printed 135600000 = filing XBRL 135600000; agrees
- shares_outstanding (review resolved, Dhairya relay 2026-11-12): mapped us-gaap:CommonStockSharesOutstanding (R88.htm): decided by the filing: R88 Class A 358,950,000 + Class B1-B4 600+800+1,300+400 at 2025-12-31 = 358,953,100 (class sum allowed); the 4,584,000 row sits on the convertible preferred member and is excluded
- total_debt: finance-lease ruling (founder 2026-11-04 item 5, Dhairya 2026-11-12): no face debt line carries leases (UnsecuredLongTermDebt excludes them); note R82 total finance lease liability 50.7 (current 9.0 + non-current 41.7) added: 0.0 + 3,422.3 + 50.7; FY2024 749.8 + 2,678.2 + 59.4
