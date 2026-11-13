# EOG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000821189-26-000054 (CIK 0000821189, filed 2026-02-24): COVER R1.htm, IS R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000821189-16-000054 (CIK 0000821189, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R7.htm
- 10-K 0000821189-24-000011 (CIK 0000821189, era filing): COVER R1.htm, IS R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000821189.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total | 22632000000 | 22632000000 | 23698000000 | 23698000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total | 16247000000 | 16247000000 | 15616000000 | 15616000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and Administrative | 820000000 | 820000000 | 669000000 | 669000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 6385000000 | 6385000000 | 8082000000 | 8082000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest Expense, Net | 235000000 | 235000000 | 138000000 | 138000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income Before Income Taxes | 6362000000 | 6362000000 | 8218000000 | 8218000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Tax Provision | 1382000000 | 1382000000 | 1815000000 | 1815000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income | 4980000000 | 4980000000 | 6403000000 | 6403000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic ( in usd per share) | 9.17 | 9.17 | 11.31 | 11.31 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in usd per share) | 9.12 | 9.12 | 11.25 | 11.25 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 543000000 | 543000000 | 566000000 | 566000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 546000000 | 546000000 | 569000000 | 569000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and Cash Equivalents | 3396000000 | 3396000000 | 7092000000 | 7092000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts Receivable, Net | 2681000000 | 2681000000 | 2650000000 | 2650000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories | 1014000000 | 1014000000 | 985000000 | 985000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total | 7656000000 | 7656000000 | 11230000000 | 11230000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Total Property, Plant and Equipment, Net | 42341000000 | 42341000000 | 34212000000 | 34212000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| goodwill | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total Assets | 51799000000 | 51799000000 | 47186000000 | 47186000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts Payable | 2904000000 | 2904000000 | 2464000000 | 2464000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total | 4691000000 | 4691000000 | 5354000000 | 5354000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Total Stockholders' Equity | 29833000000 | 29833000000 | 29351000000 | 29351000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net Cash Provided by Operating Activities | 10044000000 | 10044000000 | 12143000000 | 12143000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net Cash Used in Investing Activities | -10936000000 | -10936000000 | -5967000000 | -5967000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net Cash Used in Financing Activities | -2804000000 | -2804000000 | -4361000000 | -4361000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation, Depletion and Amortization | 4461000000 | 4461000000 | 4108000000 | 4108000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-Based Compensation Expenses | 216000000 | 216000000 | 199000000 | 199000000 | Y | FILING-CHECKED | accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfOrdinaryDividends | R8.htm | Dividends Paid | -2161000000 | 2161000000 | -2087000000 | 2087000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury Stock Purchased | -2564000000 | 2564000000 | -3246000000 | 3246000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000821189-26-000054 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R69.htm | Supplemental Cash Flow Information - Schedule of Computation of Net Income Per Share (Details) |  | 185000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R69.htm 'Supplemental Cash Flow Information - Schedule of Computation of Net Income Per S' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R56.htm | Income Taxes - Schedule of Income Taxes Paid (Net of Refunds) (Details) |  | 1869000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R56.htm 'Income Taxes - Schedule of Income Taxes Paid (Net of Refunds) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R4.htm | Current Portion of Long-Term Debt + Long-Term Debt | 7936000000 | 7936000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (871 tags across all 88 R pages, face and notes) of 0000821189-26-000054; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Total' on us-gaap:Revenues = 8757428000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Total' on us-gaap:CostsAndExpenses = 15443507000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000821189-16-000054 R2.htm prints 'General and Administrative' on us-gaap:GeneralAndAdministrativeExpense = 366594000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Operating Income (Loss)' on us-gaap:OperatingIncomeLoss = -6686079000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Net Interest Expense' on us-gaap:InterestExpense = 237393000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Income (Loss) Before Income Taxes' on eog:IncomeBeforeIncomeTaxes = -6921556000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Income Tax Provision' on us-gaap:IncomeTaxExpenseBenefit = -2397041000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Net Income (Loss)' on us-gaap:NetIncomeLoss = -4524515000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = -8.29 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = -8.29 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 545697000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000821189-16-000054 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 545697000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 718506000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Accounts Receivable, Net' on us-gaap:AccountsReceivableNetCurrent = 930610000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Inventories' on eog:Inventories = 598935000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Total' on us-gaap:AssetsCurrent = 2592244000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Total Property, Plant and Equipment, Net' on us-gaap:PropertyPlantAndEquipmentNet = 24210721000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Total Assets' on us-gaap:Assets = 26975244000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Accounts Payable' on us-gaap:AccountsPayableCurrent = 1471953000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Total' on us-gaap:LiabilitiesCurrent = 1819287000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000821189-16-000054 R3.htm prints 'Total Stockholders' Equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 12943035000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 3595165000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Net Cash Used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -5320256000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Net Cash Provided by (Used in) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 370921000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Depreciation, Depletion and Amortization' on us-gaap:DepreciationDepletionAndAmortization = 3313644000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Stock-Based Compensation Expenses' on us-gaap:ShareBasedCompensation = 130577000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Dividends Paid' on us-gaap:PaymentsOfOrdinaryDividends = -367005000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000821189-16-000054 R7.htm prints 'Treasury Stock Purchased' on us-gaap:PaymentsForRepurchaseOfCommonStock = -48791000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000821189-16-000054 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000821189-16-000054 R7.htm read; no row matched (auto)
- interest_expense: era 10-K 0000821189-24-000011 R3.htm prints 'Interest Expense, Net' on us-gaap:InterestExpense = 148000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: corrected: EOG prints no cost of revenue; 'Total' costs = 22,632 - 6,385 OI = 16,247 is the opex total (CME precedent)
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- goodwill: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- capex: component sum us-gaap:PaymentsToAcquireOilAndGasPropertyAndEquipment+us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment (R8.htm): 2026-11-12 R8.htm: corrected: CF R8 prints two capex lines outside the tool's tag set: 6,115 + 479
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R69.htm): 2026-11-12 R69.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R56.htm): 2026-11-12 R56.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R4.htm): 2026-11-12 R4.htm: agree: R4 debt lines; no finance-lease facts in the filing
- shares_outstanding: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating Income' is the operating_income line, printed 6385000000 = filing XBRL 6385000000; agrees
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R3.htm): 2026-11-12 R3.htm: agree: face R3 prints Incurred 321 - Capitalized 86 = 'Interest Expense, Net' 235; interest income sits above in other income; condition (1) holds; company-scope FILING-CHECKED override (net of capital
- inventory: mapped us-gaap:InventoryNet (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: BS R4.htm 'Inventories' is the inventory line, printed 1014000000 = filing XBRL 1014000000; agrees
- total_assets: mapped us-gaap:Assets (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: BS R4.htm 'Total Assets' is the total_assets line, printed 51799000000 = filing XBRL 51799000000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Stock-Based Compensation Expenses' is the sbc line, printed 216000000 = filing XBRL 216000000; agrees
- total_debt: finance-lease ruling (founder 2026-11-04 item 5): R84 places finance leases inside current and long-term debt; no lease added
