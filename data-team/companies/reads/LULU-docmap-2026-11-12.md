# LULU document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001397187-26-000020 (CIK 0001397187, filed 2026-03-17): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001397187-16-000089 (CIK 0001397187, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001397187-18-000013 (CIK 0001397187, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001397187-19-000011 (CIK 0001397187, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0001397187.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net revenue | 11102600000 | 11102600000 | 10588126000 | 10588126000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 4818468000 | 4818468000 | 4317315000 | 4317315000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 6284132000 | 6284132000 | 6270811000 | 6270811000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:RestructuringCostsAndAssetImpairmentCharges+us-gaap:AmortizationOfIntangibleAssets | R5.htm | Selling, general and administrative expenses + Impairment of assets and restructuring costs + Amortization of intangible | 4073517000 | 4073517000 | 3765114000 | 3765114000 | Y | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 4066556000 | 4066556000 | 3762379000 | 3762379000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (810 tags across all 98 R pages, face and notes) of 0001397187-26-000020; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 2210615000 | 2210615000 | 2505697000 | 2505697000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (810 tags across all 98 R pages, face and notes) of 0001397187-26-000020; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income tax expense | 2238967000 | 2238967000 | 2576077000 | 2576077000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 659784000 | 659784000 | 761461000 | 761461000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1579183000 | 1579183000 | 1814616000 | 1814616000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share (in dollars per share) | 13.27 | 13.27 | 14.67 | 14.67 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share (in dollars per share) | 13.26 | 13.26 | 14.64 | 14.64 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted-average number of shares outstanding (in shares) | 118981000 | 118981000 | 123735000 | 123735000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted-average number of shares outstanding (in shares) | 119068000 | 119068000 | 123935000 | 123935000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R5.htm period ..2026-02-01 |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and cash equivalents | 1807202000 | 1807202000 | 1984336000 | 1984336000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Accounts receivable, net | 190657000 | 190657000 | 120173000 | 120173000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 1700753000 | 1700753000 | 1442081000 | 1442081000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4262701000 | 4262701000 | 3980302000 | 3980302000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 2033720000 | 2033720000 | 1780617000 | 1780617000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 184911000 | 184911000 | 159518000 | 159518000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 8456743000 | 8456743000 | 7603292000 | 7603292000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 331421000 | 331421000 | 271406000 | 271406000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1887548000 | 1887548000 | 1839630000 | 1839630000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3494903000 | 3494903000 | 3279245000 | 3279245000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 4961840000 | 4961840000 | 4324047000 | 4324047000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R3.htm period ..2026-02-01 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1602477000 | 1602477000 | 2272713000 | 2272713000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -662118000 | -662118000 | -798174000 | -798174000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -1208656000 | -1208656000 | -1652508000 | -1652508000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchase of property and equipment | -680802000 | 680802000 | -689232000 | 689232000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 496228000 | 496228000 | 446524000 | 446524000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 62203000 | 62203000 | 90011000 | 90011000 | Y | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (810 tags across all 98 R pages, face and notes) of 0001397187-26-000020; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -1178349000 | 1178349000 | -1636879000 | 1636879000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001397187-26-000020 R7.htm period ..2026-02-01 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R93.htm | Supplementary Financial Information - Schedule of Supplementary Cash Flow (Detail) |  | 1028000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R93.htm 'Supplementary Financial Information - Schedule of Supplementary Cash Flow (Detai' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R88.htm | Income Taxes - Summary of Cash Paid Income Taxes (Details) |  | 1015444000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R88.htm 'Income Taxes - Summary of Cash Paid Income Taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (810 tags across all 98 R pages, face and notes) of 0001397187-26-000020; no face row matched |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 111380000 | 111380000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-02-01; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Net revenue' on us-gaap:SalesRevenueNet = 2060523000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 1063357000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 997166000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 628090000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 628090000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 369076000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Income before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 368495000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 102448000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 266047000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Basic earnings per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.9 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Diluted earnings per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.89 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Basic weighted-average number of shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 140365000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001397187-16-000089 R4.htm prints 'Diluted weighted-average number of shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 140610000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 501482000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Accounts receivable' on us-gaap:ReceivablesNetCurrent = 13108000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 284009000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 917039000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 349605000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Goodwill and intangible assets, net' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 24777000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Total assets' on us-gaap:Assets = 1314077000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 10381000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 225504000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 286595000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001397187-16-000089 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1027482000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 298740000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -143487000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -273693000 (FILING-CHECKED)
- capex: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Purchase of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -143487000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 73383000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 10356000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001397187-16-000089 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -274193000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001397187-16-000089 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001397187-16-000089 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001397187-18-000013 R4.htm prints 'Net revenue' on us-gaap:SalesRevenueNet = 2649181000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001397187-18-000013 R4.htm prints 'Cost of goods sold' on us-gaap:CostOfGoodsSold = 1250391000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001397187-18-000013 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001397187-19-000011 R4.htm prints 'Net revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 3288319000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001397187-19-000011 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 881320000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | component sum | agree | page value 4073517000 vs printed 4073517000 |
| sga_expense | mapped-sample | agree | page value 4066556000 vs printed 4066556000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value 2210615000 vs printed 2210615000 |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_receivable | mapped-sample | agree | page value 190657000 vs printed 190657000 |
| current_assets | mapped-sample | agree | page value 4262701000 vs printed 4262701000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 1028000 vs API 1028000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 1015444000 vs API 1015444000 |
| total_debt | not_presented | agree | none of the candidate elements in MetaLinks.json |
