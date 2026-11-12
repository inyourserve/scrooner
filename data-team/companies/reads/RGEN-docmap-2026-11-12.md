# RGEN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-076528 (CIK 0000730272, filed 2026-02-26): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- 10-K 0001193125-16-478518 (CIK 0000730272, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0001193125-18-054262 (CIK 0000730272, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000950170-24-018809 (CIK 0000730272, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- companyfacts CIK0000730272.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R38.htm | Summary of Significant Accounting Policies - Additional Information (Detail) |  | 738256000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R38.htm 'Summary of Significant Accounting Policies - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R42.htm | Summary of Significant Accounting Policies - Schedule of Information about Reportable Segments (Detail) |  | 352011000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R42.htm 'Summary of Significant Accounting Policies - Schedule of Information about Repor' (MetaLinks.json presentation); value from companyfacts same accession |
| gross_profit | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1107 tags across all 94 R pages, face and notes) of 0001193125-26-076528; no face row matched |
| operating_expenses | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1107 tags across all 94 R pages, face and notes) of 0001193125-26-076528; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS) |  | 290508000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS)' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R42.htm | Summary of Significant Accounting Policies - Schedule of Information about Reportable Segments (Detail) |  | 54177000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R42.htm 'Summary of Significant Accounting Policies - Schedule of Information about Repor' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS) |  | 55167000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS)' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R4.htm | CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS) |  | 21513000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R4.htm 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R74.htm | Income Taxes - Income (Loss) Before Income Taxes (Detail) |  | 62383000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R74.htm 'Income Taxes - Income (Loss) Before Income Taxes (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R42.htm | Summary of Significant Accounting Policies - Schedule of Information about Reportable Segments (Detail) |  | 13489000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R42.htm 'Summary of Significant Accounting Policies - Schedule of Information about Repor' (MetaLinks.json presentation); value from companyfacts same accession |
| net_income | mapped | us-gaap:NetIncomeLoss | R7.htm | Pay vs Performance Disclosure |  | 48894000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R7.htm 'Pay vs Performance Disclosure' (MetaLinks.json presentation); value from companyfacts same accession |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R40.htm | Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted Shares Amounts (Detail) |  | 0.87 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted' (MetaLinks.json presentation); value from companyfacts same accession |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R40.htm | Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted Shares Amounts (Detail) |  | 0.86 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R40.htm | Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted Shares Amounts (Detail) |  | 56234 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R40.htm | Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted Shares Amounts (Detail) |  | 56561 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'Summary of Significant Accounting Policies - Reconciliation of Basic and Diluted' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 566021000 | 566021000 | 757355000 | 757355000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net of allowances of $2,767 and $1,832 at December 31, 2025 and December 31, 2024, respectively | 158587000 | 158587000 | 134115000 | 134115000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories, net | 170458000 | 170458000 | 142964000 | 142964000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 1137385000 | 1137385000 | 1066041000 | 1066041000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property, plant and equipment, net | 186614000 | 186614000 | 197738000 | 197738000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1114408000 | 1114408000 | 1030995000 | 1030995000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 2949699000 | 2949699000 | 2829666000 | 2829666000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 30010000 | 30010000 | 32134000 | 32134000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 135826000 | 135826000 | 126787000 | 126787000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 843570000 | 843570000 | 856948000 | 856948000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 2106129000 | 2106129000 | 1972718000 | 1972718000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Total cash provided by operating activities | 117417000 | 117417000 | 175394000 | 175394000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Total cash used in investing activities | -298474000 | -298474000 | -86383000 | -86383000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Total cash (used in) provided by financing activities | -15205000 | -15205000 | -82902000 | -82902000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Purchases of property, plant and equipment | -23519000 | 23519000 | -25677000 | 25677000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R6.htm | Depreciation and amortization | 78745000 | 78745000 | 69673000 | 69673000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock-based compensation | 32605000 | 32605000 | 48070000 | 48070000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1107 tags across all 94 R pages, face and notes) of 0001193125-26-076528; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchase of common stock | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | CONSOLIDATED STATEMENTS OF CASH FLOWS |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R6.htm 'CONSOLIDATED STATEMENTS OF CASH FLOWS' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R6.htm | Income taxes paid | 20925000 | 20925000 | 19300000 | 19300000 | Y | FILING-CHECKED | accn 0001193125-26-076528 R6.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebt | R2.htm | Convertible Senior Notes due 2028, net | 542213000 | 542213000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 56325429 | 56325429 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Total revenue' on us-gaap:Revenues = 83537000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Cost of product revenue' on us-gaap:CostOfGoodsSold = 35251000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 24699000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 5740000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 13764000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -32000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 13423000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Income tax (benefit) provision' on us-gaap:IncomeTaxExpenseBenefit = 4078000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 9345000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 0.28 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 0.28 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 32881940 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-478518 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 33577091 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 54092000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Accounts receivable, less reserve for doubtful accounts of $31 and $41, respecti' on us-gaap:AccountsReceivableNetCurrent = 11300000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Inventories, net' on us-gaap:InventoryNet = 17998000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 103252000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 13801000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 14346000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Total assets' on us-gaap:Assets = 146237000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 6724000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 18781000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-478518 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001193125-16-478518 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 122748000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 15053000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 4791000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 767000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -2628000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 4594000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 3598000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-478518 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-478518 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-478518 R6.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 4948000 (FILING-CHECKED)
- revenue: era 10-K 0001193125-18-054262 R4.htm prints 'Total revenue' on us-gaap:Revenues = 141236000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001193125-18-054262 R4.htm prints 'Cost of product revenue' on us-gaap:CostOfGoodsSold = 67050000 (FILING-CHECKED)
- cfo: era 10-K 0001193125-18-054262 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 17451000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-054262 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -98246000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-054262 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 129945000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001193125-18-054262 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 4021000 (FILING-CHECKED)
- interest_expense: 10-K 0000950170-24-018809 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 738256000 vs API 738256000 |
| cost_of_revenue | NOTE | agree | page value 352011000 vs API 352011000 |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | NOTE | agree | page value 54177000 vs API 54177000 |
| income_before_tax | NOTE | agree | page value 62383000 vs API 62383000 |
| income_tax_expense | NOTE | agree | page value 13489000 vs API 13489000 |
| net_income | NOTE | agree | page value 48894000 vs API 48894000 |
| basic_eps | NOTE | agree | page value 0.87 vs API 0.87 |
| diluted_eps | NOTE | agree | page value 0.86 vs API 0.86 |
| weighted_basic_shares | NOTE | agree | page value 56234 vs API 56234 |
| weighted_diluted_shares | NOTE | agree | page value 56561 vs API 56561 |
| current_liabilities | mapped-sample | agree | page value 135826000 vs printed 135826000 |
| cfo | mapped-sample | agree | page value 117417000 vs printed 117417000 |
| sbc | mapped-sample | agree | page value 32605000 vs printed 32605000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | component sum | agree | page value 542213000 vs printed 542213000 |
