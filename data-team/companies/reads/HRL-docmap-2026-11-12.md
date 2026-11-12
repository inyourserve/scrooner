# HRL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000048465-25-000059 (CIK 0000048465, filed 2025-12-05): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001104659-15-085151 (CIK 0000048465, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000048465-23-000083 (CIK 0000048465, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000048465-20-000043 (CIK 0000048465, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000048465.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Net Sales | 12106160000 | 12106160000 | 11920797000 | 11920797000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of Products Sold | 10214344000 | 10214344000 | 9898659000 | 9898659000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross Profit | 1891816000 | 1891816000 | 2022138000 | 2022138000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1047 tags across all 117 R pages, face and notes) of 0000048465-25-000059; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, General, and Administrative | 996624000 | 996624000 | 1005294000 | 1005294000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R54.htm | Summary of Significant Accounting Policies - Research and Development Expenses (Details) |  | 35200000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R54.htm 'Summary of Significant Accounting Policies - Research and Development Expenses (' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income | 718603000 | 718603000 | 1067932000 | 1067932000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest Expense | 78038000 | 78038000 | 80894000 | 80894000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings Before Income Taxes | 663449000 | 663449000 | 1035434000 | 1035434000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for Income Taxes | 185684000 | 185684000 | 230803000 | 230803000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Earnings Attributable to Hormel Foods Corporation | 478197000 | 478197000 | 805038000 | 805038000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 0.87 | 0.87 | 1.47 | 1.47 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 0.87 | 0.87 | 1.47 | 1.47 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 550164000 | 550164000 | 548129000 | 548129000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 550496000 | 550496000 | 548832000 | 548832000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R3.htm period ..2025-10-26 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and Cash Equivalents | 670679000 | 670679000 | 741881000 | 741881000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts Receivable (Net of Allowance of $3,743 and $3,712, respectively) | 784812000 | 784812000 | 817908000 | 817908000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1747279000 | 1747279000 | 1576300000 | 1576300000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total Current Assets | 3405656000 | 3405656000 | 3246476000 | 3246476000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, Plant, and Equipment, Net | 2238770000 | 2238770000 | 2194728000 | 2194728000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 4924087000 | 4924087000 | 4923487000 | 4923487000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 13393119000 | 13393119000 | 13434729000 | 13434729000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts Payable | 731578000 | 731578000 | 735604000 | 735604000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total Current Liabilities | 1380796000 | 1380796000 | 1399299000 | 1399299000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1047 tags across all 117 R pages, face and notes) of 0000048465-25-000059; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Hormel Foods Corporation Shareholders’ Investment | 7901171000 | 7901171000 | 7993420000 | 7993420000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R5.htm period ..2025-10-26 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net Cash Provided by (Used in) Operating Activities | 845251000 | 845251000 | 1266738000 | 1266738000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net Cash Provided by (Used in) Investing Activities | -298592000 | -298592000 | -236907000 | -236907000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net Cash Provided by (Used in) Financing Activities | -613996000 | -613996000 | -1030096000 | -1030096000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of Property, Plant, and Equipment | -310902000 | 310902000 | -256441000 | 256441000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 241174000 | 241174000 | 233827000 | 233827000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based Compensation Expense | 25602000 | 25602000 | 23233000 | 23233000 | Y | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends Paid on Common Stock | -633192000 | 633192000 | -614960000 | 614960000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Share Repurchase | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0000048465-25-000059 R9.htm period ..2025-10-26 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R98.htm | Long-term Debt and Other Borrowing Arrangements - Schedule of Interest Paid (Details) |  | 74579000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R98.htm 'Long-term Debt and Other Borrowing Arrangements - Schedule of Interest Paid (Det' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R106.htm | Income Taxes - Narrative (Details) |  | 183500000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R106.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current Maturities of Long-term Debt + Long-term Debt Less Current Maturities | 2857424000 | 2857424000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1047 tags across all 117 R pages, face and notes) of 0000048465-25-000059; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001104659-15-085151 R4.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 9263863000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001104659-15-085151 R4.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 7455282000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001104659-15-085151 R4.htm prints 'GROSS PROFIT' on us-gaap:GrossProfit = 1808581000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001104659-15-085151 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 743611000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001104659-15-085151 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001104659-15-085151 R4.htm prints 'OPERATING INCOME' on us-gaap:OperatingIncomeLoss = 1067320000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001104659-15-085151 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -13111000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001104659-15-085151 R4.htm prints 'EARNINGS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1057143000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001104659-15-085151 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 369879000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001104659-15-085151 R4.htm prints 'NET EARNINGS ATTRIBUTABLE TO HORMEL FOODS CORPORATION' on us-gaap:NetIncomeLoss = 686088000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001104659-15-085151 R4.htm prints 'BASIC (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.6 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001104659-15-085151 R4.htm prints 'DILUTED (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.54 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001104659-15-085151 R4.htm prints 'BASIC (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 264072000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001104659-15-085151 R4.htm prints 'DILUTED (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 270501000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001104659-15-085151 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 347239000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001104659-15-085151 R2.htm prints 'Accounts receivable (net of allowance for doubtful accounts of $4,086 at October' on us-gaap:AccountsReceivableNetCurrent = 605689000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001104659-15-085151 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 993265000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001104659-15-085151 R2.htm prints 'TOTAL CURRENT ASSETS' on us-gaap:AssetsCurrent = 2063032000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001104659-15-085151 R2.htm prints 'Property, Plant and Equipment, Net' on us-gaap:PropertyPlantAndEquipmentNet = 1011739000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001104659-15-085151 R2.htm prints 'GOODWILL' on us-gaap:Goodwill = 1699484000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001104659-15-085151 R2.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 6139831000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001104659-15-085151 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 495317000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001104659-15-085151 R2.htm prints 'TOTAL CURRENT LIABILITIES' on us-gaap:LiabilitiesCurrent = 1214025000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001104659-15-085151 R2.htm prints 'HORMEL FOODS CORPORATION SHAREHOLDERS' INVESTMENT' on us-gaap:StockholdersEquity = 3998198000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001104659-15-085151 R8.htm prints 'NET CASH PROVIDED BY OPERATING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 991992000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001104659-15-085151 R8.htm prints 'NET CASH USED IN INVESTING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -900947000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001104659-15-085151 R8.htm prints 'NET CASH USED IN FINANCING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -70627000 (FILING-CHECKED)
- capex: FY2015 10-K 0001104659-15-085151 R8.htm prints 'Purchases of property/equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -144063000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001104659-15-085151 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001104659-15-085151 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 15717000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001104659-15-085151 R8.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -250834000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001104659-15-085151 R8.htm prints 'Share repurchase' on us-gaap:PaymentsForRepurchaseOfCommonStock = -24928000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001104659-15-085151 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001104659-15-085151 R8.htm read; no row matched (auto)
- interest_expense: era 10-K 0000048465-23-000083 R3.htm prints 'Interest Expense' on us-gaap:InterestExpense = 73402000 (FILING-CHECKED)
- ppe_net: era 10-K 0000048465-20-000043 R2.htm prints 'Net Property, Plant, and Equipment' on us-gaap:PropertyPlantAndEquipmentNet =  (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | NOTE | agree | page value 35200000 vs API 35200000 |
| cash_and_equivalents | mapped-sample | agree | page value 670679000 vs printed 670679000 |
| current_liabilities | mapped-sample | agree | page value 1380796000 vs printed 1380796000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -298592000 vs printed -298592000 |
| depreciation_and_amortization | component sum | agree | page value 241174000 vs printed 241174000 |
| cash_paid_for_interest | NOTE | agree | page value 74579000 vs API 74579000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 183500000 vs API 183500000 |
| total_debt | component sum | agree | page value 2857424000 vs printed 2857424000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
