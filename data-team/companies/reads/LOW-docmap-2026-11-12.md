# LOW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000060667-26-000029 (CIK 0000060667, filed 2026-03-23): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000060667-16-000276 (CIK 0000060667, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R6.htm, BSP R8.htm, CF R11.htm
- 10-K 0000060667-18-000051 (CIK 0000060667, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000060667-23-000034 (CIK 0000060667, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0000060667.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 86286000000 | 86286000000 | 83674000000 | 83674000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 57401000000 | 57401000000 | 55797000000 | 55797000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross margin | 28885000000 | 28885000000 | 27877000000 | 27877000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:DepreciationAndAmortization | R3.htm | Selling, general and administrative + Depreciation and amortization | 18732000000 | 18732000000 | 17411000000 | 17411000000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 16791000000 | 16791000000 | 15682000000 | 15682000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (931 tags across all 97 R pages, face and notes) of 0000060667-26-000029; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 10153000000 | 10153000000 | 10466000000 | 10466000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest – net | 1406000000 | -1406000000 | 1313000000 | -1313000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Pre-tax earnings | 8747000000 | 8747000000 | 9153000000 | 9153000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax provision | 2093000000 | 2093000000 | 2196000000 | 2196000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 6654000000 | 6654000000 | 6957000000 | 6957000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per common share (in dollars per share) | 11.87 | 11.87 | 12.25 | 12.25 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per common share (in dollars per share) | 11.85 | 11.85 | 12.23 | 12.23 | Y | FILING-CHECKED | accn 0000060667-26-000029 R3.htm period ..2026-01-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R90.htm | Earnings Per Share - EPS Schedule (Details) |  | 559000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Earnings Per Share - EPS Schedule (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R90.htm | Earnings Per Share - EPS Schedule (Details) |  | 560000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Earnings Per Share - EPS Schedule (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 982000000 | 982000000 | 1761000000 | 1761000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables - net | 1090000000 | 1090000000 | 94000000 | 94000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Merchandise inventory - net | 17300000000 | 17300000000 | 17409000000 | 17409000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 20955000000 | 20955000000 | 20358000000 | 20358000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, less accumulated depreciation | 18362000000 | 18362000000 | 17649000000 | 17649000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 3945000000 | 3945000000 | 311000000 | 311000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 54144000000 | 54144000000 | 43102000000 | 43102000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 9762000000 | 9762000000 | 9290000000 | 9290000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 19463000000 | 19463000000 | 18757000000 | 18757000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 64061000000 | 64061000000 | 57333000000 | 57333000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders’ deficit | -9917000000 | -9917000000 | -14231000000 | -14231000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R5.htm period ..2026-01-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 9864000000 | 9864000000 | 9625000000 | 9625000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -12264000000 | -12264000000 | -1738000000 | -1738000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by/(used in) financing activities | 1621000000 | 1621000000 | -7047000000 | -7047000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -2213000000 | 2213000000 | -1927000000 | 1927000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 2194000000 | 2194000000 | 1972000000 | 1972000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based payment expense | 247000000 | 247000000 | 221000000 | 221000000 | Y | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividend payments | -2636000000 | 2636000000 | -2566000000 | 2566000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock | -211000000 | 211000000 | -4053000000 | 4053000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000060667-26-000029 R9.htm period ..2026-01-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R94.htm | Other Information - Net Interest Expense and Supplemental Cash Flow (Details) |  | 1489000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R94.htm 'Other Information - Net Interest Expense and Supplemental Cash Flow (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R94.htm | Other Information - Net Interest Expense and Supplemental Cash Flow (Details) |  | 2505000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R94.htm 'Other Information - Net Interest Expense and Supplemental Cash Flow (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current maturities of long-term debt + Long-term debt, excluding current maturities | 39921000000 | 39921000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 561000000 | 561000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-01-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 59074000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 38504000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Gross margin' on us-gaap:GrossProfit = 20570000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000060667-16-000276 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 14115000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000060667-16-000276 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000060667-16-000276 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Pre-tax earnings' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4419000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 1873000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 2546000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Basic earnings per common share' on us-gaap:EarningsPerShareBasic = 2.73 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000060667-16-000276 R2.htm prints 'Diluted earnings per common share' on us-gaap:EarningsPerShareDiluted = 2.73 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000060667-16-000276 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000060667-16-000276 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 405000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000060667-16-000276 R6.htm read; no row matched (auto)
- inventory: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Merchandise inventory - net' on us-gaap:InventoryNet = 9458000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 10561000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Property, less accumulated depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 19577000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000060667-16-000276 R6.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Total assets' on us-gaap:Assets = 31266000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 5633000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 10492000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Total liabilities' on us-gaap:Liabilities = 23612000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000060667-16-000276 R6.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 7654000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 4784000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1343000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -3493000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -1197000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 1587000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Share-based payment expense' on us-gaap:ShareBasedCompensation = 117000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Cash dividend payments' on us-gaap:PaymentsOfDividendsCommonStock = -957000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000060667-16-000276 R11.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -3925000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000060667-16-000276 R11.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000060667-16-000276 R11.htm read; no row matched (auto)
- revenue: era 10-K 0000060667-18-000051 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 68619000000 (FILING-CHECKED)
- ppe_net: era 10-K 0000060667-23-000034 R5.htm prints 'Property, less accumulated depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 17567000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:DepreciationAndAmortization (R3.htm): 2026-11-12 R3.htm: R3: SG&A 16,791 + D&A 1,941 are every face line between gross margin and operating income and tie to GP - OI
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: no R&D line on R3; MetaLinks: tags absent
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R90.htm): 2026-11-12 R90.htm: R90 EPS schedule prints basic weighted shares 559 million = XBRL: mapped, stmt NOTE
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R90.htm): 2026-11-12 R90.htm: R90 prints diluted weighted shares 560 million = XBRL: mapped, stmt NOTE
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R94.htm): 2026-11-12 R94.htm: R94 supplemental note prints interest paid (net of capitalized) 1,489 = XBRL: mapped, stmt NOTE
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R94.htm): 2026-11-12 R94.htm: R94 prints income taxes paid 2,505 = XBRL: mapped, stmt NOTE
- total_debt: component sum us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: R5 prints current maturities 2,431 + long-term debt 37,490 = 39,921 = XBRL
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R9.htm): 2026-11-12 R9.htm: 10% mapped sample: CF R9.htm 'Net cash provided by operating activities' is the cfo line, printed 9864000000 = filing XBRL 9864000000; agrees
- depreciation_and_amortization: mapped us-gaap:DepreciationDepletionAndAmortization (R9.htm): 2026-11-12 R9.htm: 10% mapped sample: CF R9.htm 'Depreciation and amortization' is the depreciation_and_amortization line, printed 2194000000 = filing XBRL 2194000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R9.htm): 2026-11-12 R9.htm: 10% mapped sample: CF R9.htm 'Repurchases of common stock' is the share_buybacks line, printed -211000000 = filing XBRL 211000000; agrees

## Loader-reject fixes 2026-11-13 (docmap-load dry run on 669f8477)
- research_and_development: unverified -> re-checked on the R page
- weighted_basic_shares: period/accession added
- weighted_diluted_shares: period/accession added
- cash_paid_for_interest: period/accession added
- cash_paid_for_income_taxes: period/accession added
- total_debt: unverified -> re-checked on the R page
- shares_outstanding: period/accession added
