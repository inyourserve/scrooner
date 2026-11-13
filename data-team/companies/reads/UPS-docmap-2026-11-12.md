# UPS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008432 (CIK 0001090727, filed 2026-02-17): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001090727-16-000053 (CIK 0001090727, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001090727-18-000009 (CIK 0001090727, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001090727-24-000008 (CIK 0001090727, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0001090727.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 88661000000 | 88661000000 | 91070000000 | 91070000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1336 tags across all 115 R pages, face and notes) of 0001628280-26-008432; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1336 tags across all 115 R pages, face and notes) of 0001628280-26-008432; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total Operating Expenses | 80794000000 | 80794000000 | 82602000000 | 82602000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1336 tags across all 115 R pages, face and notes) of 0001628280-26-008432; no face row matched |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1336 tags across all 115 R pages, face and notes) of 0001628280-26-008432; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating Profit | 7867000000 | 7867000000 | 8468000000 | 8468000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -1017000000 | 1017000000 | -866000000 | 866000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income Before Income Taxes | 7164000000 | 7164000000 | 7442000000 | 7442000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income Tax Expense | 1592000000 | 1592000000 | 1660000000 | 1660000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income | 5572000000 | 5572000000 | 5782000000 | 5782000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic Earnings Per Share (in dollars per share) | 6.56 | 6.56 | 6.76 | 6.76 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted Earnings Per Share (in dollars per share) | 6.56 | 6.56 | 6.75 | 6.75 | Y | FILING-CHECKED | accn 0001628280-26-008432 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R104.htm | EARNINGS PER SHARE - Computation of Basic and Diluted Earnings Per Share (Details) |  | 849000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R104.htm 'EARNINGS PER SHARE - Computation of Basic and Diluted Earnings Per Share (Detail' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R104.htm | EARNINGS PER SHARE - Computation of Basic and Diluted Earnings Per Share (Details) |  | 850000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R104.htm 'EARNINGS PER SHARE - Computation of Basic and Diluted Earnings Per Share (Detail' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 5887000000 | 5887000000 | 6112000000 | 6112000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 11209000000 | 11209000000 | 10871000000 | 10871000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R47.htm | SUMMARY OF ACCOUNTING POLICIES - Narrative (Details) |  | 739000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R47.htm 'SUMMARY OF ACCOUNTING POLICIES - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total Current Assets | 19045000000 | 19045000000 | 19310000000 | 19310000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, Plant and Equipment, Net | 37731000000 | 37731000000 | 37179000000 | 37179000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5837000000 | 5837000000 | 4300000000 | 4300000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 73090000000 | 73090000000 | 70070000000 | 70070000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 6633000000 | 6633000000 | 6302000000 | 6302000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total Current Liabilities | 15620000000 | 15620000000 | 16441000000 | 16441000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1336 tags across all 115 R pages, face and notes) of 0001628280-26-008432; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Equity for Controlling Interests | 16227000000 | 16227000000 | 16718000000 | 16718000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash from operating activities | 8450000000 | 8450000000 | 10122000000 | 10122000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -4735000000 | -4735000000 | -217000000 | -217000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -4141000000 | -4141000000 | -6850000000 | -6850000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -3685000000 | 3685000000 | -3909000000 | 3909000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 3746000000 | 3746000000 | 3609000000 | 3609000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock compensation expense | 73000000 | 73000000 | 24000000 | 24000000 | Y | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends | -5398000000 | 5398000000 | -5399000000 | 5399000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchases of common stock | -1000000000 | 1000000000 | -500000000 | 500000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008432 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R48.htm | SUMMARY OF ACCOUNTING POLICIES - Supplemental Cash Flow Information (Details) |  | 990000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R48.htm 'SUMMARY OF ACCOUNTING POLICIES - Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R48.htm | SUMMARY OF ACCOUNTING POLICIES - Supplemental Cash Flow Information (Details) |  | 1912000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R48.htm 'SUMMARY OF ACCOUNTING POLICIES - Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt and finance leases + Long-Term Debt and Finance Leases | 24127000000 | 24127000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1336 tags across all 115 R pages, face and notes) of 0001628280-26-008432; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Revenue' on us-gaap:Revenues = 58363000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Total Operating Expenses' on us-gaap:CostsAndExpenses = 50695000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Operating Profit' on us-gaap:OperatingIncomeLoss = 7668000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -341000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 7342000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Income Tax Expense' on us-gaap:IncomeTaxExpenseBenefit = 2498000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Net Income' on us-gaap:NetIncomeLoss = 4844000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Basic Earnings Per Share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 5.38 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001090727-16-000053 R4.htm prints 'Diluted Earnings Per Share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 5.35 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001090727-16-000053 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001090727-16-000053 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2730000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 7134000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001090727-16-000053 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 13208000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Property, Plant and Equipment, Net' on us-gaap:PropertyPlantAndEquipmentNet = 18352000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 3419000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Total Assets' on us-gaap:Assets = 38311000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 2587000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 10696000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001090727-16-000053 R2.htm prints 'Total Equity for Controlling Interests' on us-gaap:StockholdersEquity = 2470000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Net cash from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 7430000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -5309000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -1565000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -2379000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 2084000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Stock compensation expense' on us-gaap:ShareBasedCompensation = 574000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Dividends' on us-gaap:PaymentsOfDividends = -2525000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Purchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2702000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Interest (net of amount capitalized)' on us-gaap:InterestPaidNet = 345000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001090727-16-000053 R6.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 1913000000 (FILING-CHECKED)
- revenue: era 10-K 0001090727-18-000009 R4.htm prints 'Revenue' on us-gaap:Revenues = 65872000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001090727-24-000008 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -785000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:CostsAndExpenses (R5.htm): 2026-11-12 R5.htm: corrected: UPS prints no cost of revenue; 'Total Operating Expenses' = 88,661 - 7,867 = 80,794 is the opex total
- sga_expense: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R104.htm): 2026-11-12 R104.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R104.htm): 2026-11-12 R104.htm: agree: carrying sentence read: the note value is the full data point
- inventory: mapped us-gaap:InventoryNet (R47.htm): 2026-11-12 R47.htm: agree: R47 'Inventories' 739 (inside other current assets): the full balance
- total_liabilities: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R48.htm): 2026-11-12 R48.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R48.htm): 2026-11-12 R48.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R3.htm): 2026-11-12 R3.htm: agree: R3 'Current maturities of long-term debt and finance leases' + long-term debt and finance leases: leases inside by label (finance-lease ruling (founder 2026-11-04 item 5))
- shares_outstanding: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Revenue' is the revenue line, printed 88661000000 = filing XBRL 88661000000; agrees
- operating_income: mapped us-gaap:OperatingIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Operating Profit' is the operating_income line, printed 7867000000 = filing XBRL 7867000000; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Cash and cash equivalents' is the cash_and_equivalents line, printed 5887000000 = filing XBRL 5887000000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total Current Liabilities' is the current_liabilities line, printed 15620000000 = filing XBRL 15620000000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Stock compensation expense' is the sbc line, printed 73000000 = filing XBRL 73000000; agrees
- total_debt: finance-lease ruling (founder 2026-11-04 item 5): R82 places finance leases inside the debt lines (label says so); no lease added
