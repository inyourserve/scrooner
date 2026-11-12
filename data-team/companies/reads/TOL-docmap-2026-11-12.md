# TOL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000794170-25-000112 (CIK 0000794170, filed 2025-12-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0000794170-15-000059 (CIK 0000794170, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000794170-20-000066 (CIK 0000794170, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0000794170.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R5.htm | Revenues: | 10966723000 | 10966723000 | 10846740000 | 10846740000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenues: | 8212487000 | 8212487000 | 7824262000 | 7824262000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R111.htm | Summary Consolidated Quarterly Financial Data (Unaudited) (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Summary Consolidated Quarterly Financial Data (Unaudited) (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1033622000 | 1033622000 | 982291000 | 982291000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 1720614000 | 1720614000 | 2040187000 | 2040187000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic | R5.htm | Income before income taxes | 1791371000 | 1791371000 | 2085640000 | 2085640000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | 444885000 | 444885000 | 514445000 | 514445000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1346486000 | 1346486000 | 1571195000 | 1571195000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings (in dollars per share) | 13.6 | 13.6 | 15.16 | 15.16 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings (in dollars per share) | 13.49 | 13.49 | 15.01 | 15.01 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 98978000 | 98978000 | 103653000 | 103653000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 99779000 | 99779000 | 104690000 | 104690000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R5.htm period ..2025-10-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1258997000 | 1258997000 | 1303039000 | 1303039000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| accounts_receivable | mapped | tol:Receivablesprepaidexpensesandotherassets | R3.htm | Receivables, prepaid expenses, and other assets | 554720000 |  | 590611000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| inventory | mapped | us-gaap:InventoryOperativeBuilders | R3.htm | Inventory | 10678460000 | 10678460000 | 9712925000 | 9712925000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, construction, and office equipment – net | 273397000 | 273397000 | 453007000 | 453007000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 14519866000 | 14519866000 | 13367932000 | 13367932000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrentAndNoncurrent | R3.htm | Accounts payable | 615771000 | 615771000 | 492213000 | 492213000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 6233802000 | 6233802000 | 5681217000 | 5681217000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 8270663000 | 8270663000 | 7670928000 | 7670928000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R3.htm period ..2025-10-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1112411000 | 1112411000 | 1010167000 | 1010167000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -310033000 | -310033000 | -167618000 | -167618000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -833875000 | -833875000 | -816455000 | -816455000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchase of property, construction, and office equipment – net | -86195000 | 86195000 | -73643000 | 73643000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 82085000 | 82085000 | 81201000 | 81201000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 30834000 | 30834000 | 29558000 | 29558000 | Y | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid | -97075000 | 97075000 | -93401000 | 93401000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchase of treasury stock and excise tax payment | -651016000 | 651016000 | -627061000 | 627061000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000794170-25-000112 R7.htm period ..2025-10-31 |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (960 tags across all 111 R pages, face and notes) of 0000794170-25-000112; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R110.htm | Supplemental Disclosure to Consolidated Statements of Cash Flows (Details) |  | 372355000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R110.htm 'Supplemental Disclosure to Consolidated Statements of Cash Flows (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:SeniorNotes | R3.htm | Senior notes | 1741525000 | 1741525000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R78.htm | Stockholders' Equity - Narrative (Details) |  | 94800000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R78.htm 'Stockholders' Equity - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Revenues' on us-gaap:HomeBuildingRevenue = 4171248000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Cost of revenues' on us-gaap:HomeBuildingCosts = 3269270000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000794170-15-000059 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 455108000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 446870000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic = 535562000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 172395000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 363167000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 2.06 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 1.97 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 176425000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000794170-15-000059 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 184703000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 918993000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Receivables, prepaid expenses, and other assets' on tol:Receivablesprepaidexpensesandotherassets = 284130000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Inventory' on us-gaap:InventoryOperativeBuilders = 6997516000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Property, construction and office equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 136755000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Total assets' on us-gaap:Assets = 9206515000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrentAndNoncurrent = 236953000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 4978436000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000794170-15-000059 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 4222557000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 60182000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -52772000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 325268000 (FILING-CHECKED)
- capex: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Purchase of property and equipment - net' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -9447000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 23557000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 22903000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000794170-15-000059 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0000794170-15-000059 R6.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -56888000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000794170-15-000059 R6.htm read; no row matched (auto)
- cfo: era 10-K 0000794170-20-000066 R6.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1008117000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0000794170-20-000066 R6.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -177845000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000794170-20-000066 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -753311000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_receivable: API missing (tol:Receivablesprepaidexpensesandotherassets)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 10966723000 vs printed 10966723000 |
| gross_profit | NOTE | agree | value 870724000 read off its own R page (no companyfacts fact to compare) |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| basic_eps | mapped-sample | agree | page value 13.6 vs printed 13.6 |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -310033000 vs printed -310033000 |
| cash_paid_for_interest | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 372355000 vs API 372355000 |
| total_debt | component sum | agree | page value 1741525000 vs printed 1741525000 |
| shares_outstanding | NOTE | agree | page value 94800000 vs API 94800000 |
