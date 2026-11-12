# EMR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000032604-26-000054 (CIK 0000032604, filed 2026-11-09): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- 10-K 0000032604-15-000051 (CIK 0000032604, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000032604-16-000105 (CIK 0000032604, era filing): COVER R1.htm, IS R2.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000032604-22-000041 (CIK 0000032604, era filing): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R10.htm
- companyfacts CIK0000032604.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 18982000000 | 18982000000 | 18016000000 | 18016000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | 8854000000 | 8854000000 | 8497000000 | 8497000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R77.htm | EQUITY METHOD INVESTMENT AND NOTE RECEIVABLE - Schedule of Financial Information (Details) |  | 10128000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R77.htm 'EQUITY METHOD INVESTMENT AND NOTE RECEIVABLE - Schedule of Financial Information' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1051 tags across all 124 R pages, face and notes) of 0000032604-26-000054; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 5296000000 | 5296000000 | 5103000000 | 5103000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R119.htm | OTHER FINANCIAL DATA - Schedule of Other Items Reported In Earnings (Details) |  | 812000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R119.htm 'OTHER FINANCIAL DATA - Schedule of Other Items Reported In Earnings (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1051 tags across all 124 R pages, face and notes) of 0000032604-26-000054; no face row matched |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R3.htm | Interest expense, net of interest income of: 2024, $148; 2025, $150; 2026, $104 | 334000000 | -334000000 | 237000000 | -237000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings from continuing operations before income taxes | 3489000000 | 3489000000 | 2905000000 | 2905000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 796000000 | 796000000 | 690000000 | 690000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings common stockholders | 2691000000 | 2691000000 | 2270000000 | 2270000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per common share (in dollars per share) | 4.81 | 4.81 | 4.02 | 4.02 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per common share (in dollars per share) | 4.79 | 4.79 | 4 | 4 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 559600000 | 559600000 | 564000000 | 564000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 562000000 | 562000000 | 566700000 | 566700000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R3.htm period ..2026-09-30 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R6.htm | Cash and equivalents | 1806000000 | 1806000000 | 1544000000 | 1544000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Receivables, less allowances of $123 in 2025 and $134 in 2026 | 3317000000 | 3317000000 | 3101000000 | 3101000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 2432000000 | 2432000000 | 2213000000 | 2213000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 9517000000 | 9517000000 | 8583000000 | 8583000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net | 2859000000 | 2859000000 | 2871000000 | 2871000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 18104000000 | 18104000000 | 18193000000 | 18193000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 41814000000 | 41814000000 | 41964000000 | 41964000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Accounts payable | 1698000000 | 1698000000 | 1384000000 | 1384000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 10118000000 | 10118000000 | 9797000000 | 9797000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1051 tags across all 124 R pages, face and notes) of 0000032604-26-000054; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Common stockholders’ equity | 20740000000 | 20740000000 | 20282000000 | 20282000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R6.htm period ..2026-09-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R10.htm | Cash provided by operating activities | 3978000000 | 3978000000 | 3098000000 | 3098000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R10.htm | Cash used in investing activities | -455000000 | -455000000 | -593000000 | -593000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R10.htm | Cash used in financing activities | -3222000000 | -3222000000 | -4510000000 | -4510000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R10.htm | Capital expenditures | -443000000 | 443000000 | -431000000 | 431000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R10.htm | Depreciation and amortization | 1478000000 | 1478000000 | 1518000000 | 1518000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R10.htm | Stock compensation | 237000000 | 237000000 | 263000000 | 263000000 | Y | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R10.htm | Dividends paid | -1244000000 | 1244000000 | -1192000000 | 1192000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R10.htm | Purchases of common stock | -1000000000 | 1000000000 | -1167000000 | 1167000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000032604-26-000054 R10.htm period ..2026-09-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R91.htm | LONG-TERM DEBT - Narrative (Details) |  | 249000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'LONG-TERM DEBT - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R105.htm | INCOME TAXES - Schedule of Income Taxes Paid Net of Refunds Received (Details) |  | 960000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R105.htm 'INCOME TAXES - Schedule of Income Taxes Paid Net of Refunds Received (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Short-term borrowings and current maturities of long-term debt + Long-term debt | 12175000000 | 12175000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 557300000 | 557300000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-09-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 22304000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 13256000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000032604-15-000051 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 5184000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000032604-15-000051 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Interest expense, net of interest income of: 2015, $29; 2014, $24; 2013, $16' on us-gaap:InterestIncomeExpenseNonoperatingNet = 171000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 4161000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1428000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Net earnings common stockholders' on us-gaap:NetIncomeLoss = 2710000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Basic earnings per share common stockholders' on us-gaap:EarningsPerShareBasic = 4.01 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000032604-15-000051 R2.htm prints 'Diluted earnings per share common stockholders' on us-gaap:EarningsPerShareDiluted = 3.99 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000032604-15-000051 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000032604-15-000051 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Cash and equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3054000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Receivables, less allowances of $128 in 2015 and $114 in 2014' on us-gaap:AccountsReceivableNetCurrent = 4319000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 1847000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 10049000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 3585000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 6653000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Total assets' on us-gaap:Assets = 22088000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 2358000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 7800000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000032604-15-000051 R5.htm prints 'Common stockholders’ equity' on us-gaap:StockholdersEquity = 8081000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 2529000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Net cash provided (used) by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 591000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Net cash used by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2948000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -685000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 815000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000032604-15-000051 R9.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -1269000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Purchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2501000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000032604-15-000051 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000032604-15-000051 R9.htm prints 'Income taxes paid on divestiture gains' on emr:TaxesPaidonGainonSaleofBusiness = -424000000 (FILING-CHECKED)
- revenue: era 10-K 0000032604-16-000105 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 14522000000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000032604-22-000041 R6.htm prints 'Cash, Cash Equivalents, Restricted Cash and Restricted Cash Equivalents' on us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents = 1804000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: mapped us-gaap:GrossProfit (R77.htm): 2026-11-12 R77.htm: agree: R77 carrying table is Emerson's own (undimensioned) quarterly and annual data, not the Copeland member; 10,128 = net sales 18,982 - cost of sales 8,854 (R3)
- operating_expenses: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed; no OI line to tie
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R119.htm): 2026-11-12 R119.htm: agree: R119 'Research and development expense' 812, the total
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaid (R91.htm): 2026-11-12 R91.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R105.htm): 2026-11-12 R105.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R6.htm): 2026-11-12 R6.htm: agree: R6 debt lines; no finance-lease facts in the filing
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Basic earnings per common share (in dollars per sh' is the basic_eps line, printed 4.81 = filing XBRL 4.81; agrees
- cash_and_equivalents: mapped us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Cash and equivalents' is the cash_and_equivalents line, printed 1806000000 = filing XBRL 1806000000; agrees
- inventory: mapped us-gaap:InventoryNet (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Inventories' is the inventory line, printed 2432000000 = filing XBRL 2432000000; agrees
- goodwill: mapped us-gaap:Goodwill (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Goodwill' is the goodwill line, printed 18104000000 = filing XBRL 18104000000; agrees
- total_assets: mapped us-gaap:Assets (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total assets' is the total_assets line, printed 41814000000 = filing XBRL 41814000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R10.htm): 2026-11-12 R10.htm: 20% mapped sample: CF R10.htm 'Purchases of common stock' is the share_buybacks line, printed -1000000000 = filing XBRL 1000000000; agrees
- interest_expense: combined check: hand 2026-11-12 R3.htm: 'Interest expense, net of interest income' is a net line: combined
