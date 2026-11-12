# SCI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-007695 (CIK 0000089089, filed 2026-02-12): COVER R1.htm, IS R4.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0000089089-16-000035 (CIK 0000089089, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0000089089.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Revenue | 4309234000 | 4309234000 | 4186379000 | 4186379000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Costs of revenue | -3169160000 | 3169160000 | -3095722000 | 3095722000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profits | 1140074000 | 1140074000 | 1090657000 | 1090657000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R72.htm | Segment Reporting Level 4 (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R72.htm 'Segment Reporting Level 4 (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | Corporate general and administrative expenses | -166158000 | 166158000 | -139019000 | 139019000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1121 tags across all 76 R pages, face and notes) of 0001628280-26-007695; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 978087000 | 978087000 | 927680000 | 927680000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | -255372000 | 255372000 | -257771000 | 257771000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income from continuing operations before income taxes | 729783000 | 729783000 | 675418000 | 675418000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Provision for income taxes | -186938000 | 186938000 | -156665000 | 156665000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to common stockholders | 542614000 | 542614000 | 518648000 | 518648000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income attributable to common stockholders, basic | 3.83 | 3.83 | 3.57 | 3.57 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income attributable to common stockholders, diluted | 3.8 | 3.8 | 3.53 | 3.53 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic weighted average number of shares | 141603000 | 141603000 | 145271000 | 145271000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted weighted average number of shares | 142689000 | 142689000 | 146782000 | 146782000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 243581000 | 243581000 | 218766000 | 218766000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R6.htm | Receivables, net | 100415000 | 100415000 | 94341000 | 94341000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 35246000 | 35246000 | 33318000 | 33318000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 411793000 | 411793000 | 377330000 | 377330000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property and equipment, net | 2751761000 | 2751761000 | 2581069000 | 2581069000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 2169055000 | 2169055000 | 2081015000 | 2081015000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 18654512000 | 18654512000 | 17379438000 | 17379438000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R6.htm | Accounts payable and accrued liabilities | 685156000 | 685156000 | 639274000 | 639274000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 745704000 | 745704000 | 723839000 | 723839000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1121 tags across all 76 R pages, face and notes) of 0001628280-26-007695; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total common stockholders’ equity | 1638271000 | 1638271000 | 1678005000 | 1678005000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 942798000 | 942798000 | 944912000 | 944912000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -548284000 | -548284000 | -620949000 | -620949000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Cash Provided by (Used in) Financing Activity, Including Discontinued Operation | -374726000 | -374726000 | -319641000 | -319641000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Capital expenditures | -388553000 | 388553000 | -373659000 | 373659000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:Depreciation | R8.htm | Depreciation and amortization | 219654000 | 219654000 | 208211000 | 208211000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 17633000 | 17633000 | 18783000 | 18783000 | Y | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Payments of dividends | -183571000 | 183571000 | -174282000 | 174282000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchase of Company common stock | -461015000 | 461015000 | -253733000 | 253733000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007695 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R63.htm | Debt Level 4 (Details) |  | 252901000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R63.htm 'Debt Level 4 (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R56.htm | Income Taxes Income Taxes Details 4 (Details) |  | 140065000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R56.htm 'Income Taxes Income Taxes Details 4 (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Current maturities of long-term debt + Long-term debt | 5139817000 | 5139817000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding | 139678199 | 139678199 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet =  (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Costs and expenses' on us-gaap:CostOfRevenue =  (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Gross profit' on us-gaap:GrossProfit =  (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000089089-16-000035 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000089089-16-000035 R2.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense =  (FILING-CHECKED)
- operating_income: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss =  (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Interest expense' on us-gaap:InterestExpense =  (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest =  (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit =  (FILING-CHECKED)
- net_income: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Net income attributable to common stockholders' on us-gaap:NetIncomeLoss =  (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Net income attributable to common stockholders, basic' on us-gaap:EarningsPerShareBasic =  (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Net income attributable to common stockholders, diluted' on us-gaap:EarningsPerShareDiluted =  (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Basic weighted average number of shares' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic =  (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000089089-16-000035 R2.htm prints 'Diluted weighted average number of shares' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding =  (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 134599000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 90462000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 27835000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 308409000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1846722000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1796340000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Total assets' on us-gaap:Assets = 11718888000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 422842000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 519396000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000089089-16-000035 R4.htm prints 'Total common stockholders’ equity' on us-gaap:StockholdersEquity = 1184692000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 472186000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -166419000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -338478000 (FILING-CHECKED)
- capex: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -150986000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Depreciation and amortization' on us-gaap:Depreciation = 141456000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 13843000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Payments of dividends' on us-gaap:PaymentsOfDividendsCommonStock = 87570000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000089089-16-000035 R6.htm prints 'Purchase of Company common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -345261000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000089089-16-000035 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000089089-16-000035 R6.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | NOTE | agree | value -1259397000 read off its own R page (no companyfacts fact to compare) |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value 978087000 vs printed 978087000 |
| basic_eps | mapped-sample | agree | page value 3.83 vs printed 3.83 |
| ppe_net | mapped-sample | agree | page value 2751761000 vs printed 2751761000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sbc | mapped-sample | agree | page value 17633000 vs printed 17633000 |
| cash_paid_for_interest | NOTE | agree | page value 252901000 vs API 252901000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 140065000 vs API 140065000 |
| total_debt | component sum | agree | page value 5139817000 vs printed 5139817000 |
