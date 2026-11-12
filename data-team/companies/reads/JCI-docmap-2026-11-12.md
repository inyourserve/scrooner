# JCI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000833444-26-000108 (CIK 0000833444, filed 2026-11-12): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0000833444-15-000091 (CIK 0000833444, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000833444-18-000053 (CIK 0000833444, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0000833444-21-000046 (CIK 0000833444, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, CF R5.htm
- companyfacts CIK0000833444.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 25666000000 | 25666000000 | 23596000000 | 23596000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 16151000000 | 16151000000 | 15004000000 | 15004000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 9515000000 | 9515000000 | 8592000000 | 8592000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1077 tags across all 118 R pages, face and notes) of 0000833444-26-000108; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 5510000000 | 5510000000 | 5764000000 | 5764000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R50.htm | Summary of Significant Accounting Policies - Narrative (Details) |  | 265000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R50.htm 'Summary of Significant Accounting Policies - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1077 tags across all 118 R pages, face and notes) of 0000833444-26-000108; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R74.htm | Debt and Financing Arrangements - Components of Net Financing Charges (Details) |  | 223000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Debt and Financing Arrangements - Components of Net Financing Charges (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 3426000000 | 3426000000 | 1969000000 | 1969000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax provision | 536000000 | 536000000 | 245000000 | 245000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Johnson Controls | 2853000000 | 2853000000 | 3291000000 | 3291000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income (in dollars per share) | 4.69 | 4.69 | 5.04 | 5.04 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income (in dollars per share) | 4.68 | 4.68 | 5.03 | 5.03 | Y | FILING-CHECKED | accn 0000833444-26-000108 R3.htm period ..2026-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R84.htm | Weighted Average Shares Outstanding (Details) |  | 609000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'Weighted Average Shares Outstanding (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R84.htm | Weighted Average Shares Outstanding (Details) |  | 611000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R84.htm 'Weighted Average Shares Outstanding (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 618000000 | 618000000 | 379000000 | 379000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, less allowance for expected credit losses of $159 and $205, respectively | 7316000000 | 7316000000 | 6269000000 | 6269000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1999000000 | 1999000000 | 1820000000 | 1820000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Current assets | 11678000000 | 11678000000 | 10162000000 | 10162000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment - net | 2106000000 | 2106000000 | 2193000000 | 2193000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 16640000000 | 16640000000 | 16633000000 | 16633000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 40147000000 | 40147000000 | 37939000000 | 37939000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 4381000000 | 4381000000 | 3614000000 | 3614000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Current liabilities | 12919000000 | 12919000000 | 10941000000 | 10941000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1077 tags across all 118 R pages, face and notes) of 0000833444-26-000108; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Shareholders’ equity attributable to Johnson Controls | 13611000000 | 13611000000 | 12927000000 | 12927000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R5.htm period ..2026-09-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R7.htm | Cash provided by operating activities from continuing operations | 3872000000 | 3872000000 | 2554000000 | 2554000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations | R7.htm | Cash used by investing activities from continuing operations | -468000000 | -468000000 | -412000000 | -412000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations | R7.htm | Cash used by financing activities from continuing operations | -3048000000 | -3048000000 | -6784000000 | -6784000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -465000000 | 465000000 | -434000000 | 434000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 654000000 | 654000000 | 865000000 | 865000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Equity-based compensation expense | 124000000 | 124000000 | 140000000 | 140000000 | Y | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Payment of cash dividends | -976000000 | 976000000 | -976000000 | 976000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Stock repurchases and retirements | -1505000000 | 1505000000 | -5991000000 | 5991000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000833444-26-000108 R7.htm period ..2026-09-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R73.htm | Debt and Financing Arrangements - Narrative (Details) |  | 286000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R73.htm 'Debt and Financing Arrangements - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R103.htm | Income Taxes - Components of Provision for Income Taxes on Continuing Operations (Details) |  | 655000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R103.htm 'Income Taxes - Components of Provision for Income Taxes on Continuing Operations' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Short-term debt + Current portion of long-term debt + Long-term debt | 9277000000 | 9277000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Ordinary shares outstanding (in shares) | 0 |  |  |  | API missing | FILING-CHECKED | balance-sheet date 2026-09-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Net revenue' on us-gaap:Revenues = 9902000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Cost of product sales' on us-gaap:CostOfGoodsSold = 4072000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000833444-15-000091 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 2573000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000833444-15-000091 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -102000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 715000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -100000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Net income attributable to Tyco ordinary shareholders' on us-gaap:NetIncomeLoss = 551000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Net income attributable to Tyco common shareholders (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.31 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Net income attributable to Tyco common shareholders (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.29 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 421000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000833444-15-000091 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 427000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1401000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Accounts receivable, less allowance for doubtful accounts of $71 and $67, respec' on us-gaap:AccountsReceivableNetCurrent = 1775000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 627000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 4653000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1189000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 4236000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Total Assets' on us-gaap:Assets = 12321000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 785000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 3845000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000833444-15-000091 R4.htm prints 'Total Tyco Shareholders' Equity' on us-gaap:StockholdersEquity = 4041000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 542000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -862000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 862000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -246000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 342000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000833444-15-000091 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -324000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Repurchase of ordinary shares by treasury' on us-gaap:PaymentsForRepurchaseOfCommonStock = -417000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 102000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000833444-15-000091 R7.htm prints 'Income taxes paid, net of refunds' on us-gaap:IncomeTaxesPaidNet = 98000000 (FILING-CHECKED)
- revenue: era 10-K 0000833444-18-000053 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 31400000000 (FILING-CHECKED)
- cfo: era 10-K 0000833444-21-000046 R5.htm prints 'Cash provided by operating activities from continuing operations' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2551000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000833444-21-000046 R5.htm prints 'Cash used by financing activities from continuing operations' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2131000000 (FILING-CHECKED)
- dividends_paid: era 10-K 0000833444-21-000046 R5.htm prints 'Payment of cash dividends' on us-gaap:PaymentsOfDividends = -762000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Hand checks 2026-11-12 (Ritwik cloud)
- operating_expenses: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed; no OI line to tie
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R50.htm): 2026-11-12 R50.htm: agree: R50 'Research and development expense' 265, the total
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- interest_expense: mapped us-gaap:InterestExpense (R74.htm): 2026-11-12 R74.htm: agree: R74 'Interest expense, net of capitalized interest costs' 223; interest income (8) is a separate line, so the value is gross of interest income; company-scope override as NEM (net of capitalize
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R84.htm): 2026-11-12 R84.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R84.htm): 2026-11-12 R84.htm: agree: carrying sentence read: the note value is the full data point
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R73.htm): 2026-11-12 R73.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R103.htm): 2026-11-12 R103.htm: agree: R103 'Income taxes paid' 655
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: agree: R5 lines on ShortTermBorrowings + LongTermDebtAndCapitalLeaseObligations* (leases inside by tag, finance-lease ruling (founder 2026-11-04 item 5))
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income from continuing operations before income ta' is the income_before_tax line, printed 3426000000 = filing XBRL 3426000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net income (in dollars per share)' is the basic_eps line, printed 4.69 = filing XBRL 4.69; agrees
- inventory: mapped us-gaap:InventoryNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Inventories' is the inventory line, printed 1999000000 = filing XBRL 1999000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Current assets' is the current_assets line, printed 11678000000 = filing XBRL 11678000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Property, plant and equipment - net' is the ppe_net line, printed 2106000000 = filing XBRL 2106000000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Equity-based compensation expense' is the sbc line, printed 124000000 = filing XBRL 124000000; agrees
