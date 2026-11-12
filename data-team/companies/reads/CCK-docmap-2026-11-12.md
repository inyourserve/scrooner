# CCK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-012904 (CIK 0001219601, filed 2026-02-27): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001219601-16-000052 (CIK 0001219601, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001219601-18-000009 (CIK 0001219601, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001219601-20-000006 (CIK 0001219601, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001219601.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 12365000000 | 12365000000 | 11801000000 | 11801000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | R3.htm | Cost of products sold, excluding depreciation and amortization | 9641000000 | 9641000000 | 9262000000 | 9262000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1151 tags across all 143 R pages, face and notes) of 0001628280-26-012904; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1151 tags across all 143 R pages, face and notes) of 0001628280-26-012904; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling and administrative expense | 632000000 | 632000000 | 597000000 | 597000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R66.htm | Summary of Significant Accounting Policies - Research and Development (Details) |  | 33000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R66.htm 'Summary of Significant Accounting Policies - Research and Development (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Income from operations | 1553000000 | 1553000000 | 1419000000 | 1419000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 398000000 | 398000000 | 452000000 | 452000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income before income taxes and equity in net earnings of affiliates | 1160000000 | 1160000000 | 743000000 | 743000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 281000000 | 281000000 | 183000000 | 183000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Crown Holdings | 738000000 | 738000000 | 424000000 | 424000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 6.41 | 6.41 | 3.56 | 3.56 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 6.38 | 6.38 | 3.55 | 3.55 | Y | FILING-CHECKED | accn 0001628280-26-012904 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R137.htm | Earnings Per Share - Schedule of Computation of Basic and Diluted Earnings Per Share (Details) |  | 115220000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R137.htm 'Earnings Per Share - Schedule of Computation of Basic and Diluted Earnings Per S' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R137.htm | Earnings Per Share - Schedule of Computation of Basic and Diluted Earnings Per Share (Details) |  | 115740000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R137.htm 'Earnings Per Share - Schedule of Computation of Basic and Diluted Earnings Per S' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 764000000 | 764000000 | 918000000 | 918000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net | 1768000000 | 1768000000 | 1656000000 | 1656000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1577000000 | 1577000000 | 1440000000 | 1440000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 4388000000 | 4388000000 | 4211000000 | 4211000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment, net | 5187000000 | 5187000000 | 4927000000 | 4927000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 3155000000 | 3155000000 | 2954000000 | 2954000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 14272000000 | 14272000000 | 13848000000 | 13848000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 2643000000 | 2643000000 | 2425000000 | 2425000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 4266000000 | 4266000000 | 3465000000 | 3465000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1151 tags across all 143 R pages, face and notes) of 0001628280-26-012904; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Crown Holdings shareholders’ equity | 2999000000 | 2999000000 | 2756000000 | 2756000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1530000000 | 1530000000 | 1192000000 | 1192000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used for investing activities | -320000000 | -320000000 | -12000000 | -12000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used for) / provided by financing activities | -1361000000 | -1361000000 | -1526000000 | -1526000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Capital expenditures | -413000000 | 413000000 | -403000000 | 403000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:OtherDepreciationAndAmortization | R7.htm | Depreciation and amortization | 456000000 | 456000000 | 448000000 | 448000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 48000000 | 48000000 | 42000000 | 42000000 | Y | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to shareholders | -120000000 | 120000000 | -119000000 | 119000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Common stock repurchased | -505000000 | 505000000 | -217000000 | 217000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-012904 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R90.htm | Debt - Narrative (Details) |  | 372000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Debt - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R123.htm | Income Taxes - Narrative (Details) |  | 286000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R123.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term debt + Current maturities of long-term debt + Long-term debt, excluding current maturities | 5964000000 | 5964000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 113421634 | 113421634 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 8762000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Cost of products sold, excluding depreciation and amortization' on us-gaap:CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization = 7116000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Selling and administrative expense' on us-gaap:SellingGeneralAndAdministrativeExpense = 390000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001219601-16-000052 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 927000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 270000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 639000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 178000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Net income attributable to Crown Holdings' on us-gaap:NetIncomeLoss = 393000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Basic (in usd per share)' on us-gaap:EarningsPerShareBasic = 2.85 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001219601-16-000052 R2.htm prints 'Diluted (in usd per share)' on us-gaap:EarningsPerShareDiluted = 2.82 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001219601-16-000052 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001219601-16-000052 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 717000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 912000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 1213000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3049000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 2699000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Goodwill and intangible assets' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 3580000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Total' on us-gaap:Assets = 10020000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 2645000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2908000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001219601-16-000052 R4.htm prints 'Crown Holdings shareholders’ equity' on us-gaap:StockholdersEquity = 144000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 956000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1548000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Net cash provided by/(used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 406000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -354000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Depreciation and amortization' on us-gaap:CostOfGoodsSoldDepreciationAndAmortization = 237000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 27000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Dividends paid to noncontrolling interests' on us-gaap:PaymentsOfDividendsMinorityInterest = -48000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001219601-16-000052 R6.htm prints 'Common stock repurchased' on us-gaap:PaymentsForRepurchaseOfCommonStock = -9000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001219601-16-000052 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001219601-16-000052 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001219601-18-000009 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 8698000000 (FILING-CHECKED)
- accounts_payable: era 10-K 0001219601-18-000009 R4.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 3124000000 (FILING-CHECKED)
- revenue: era 10-K 0001219601-20-000006 R2.htm prints 'Net Sales' on us-gaap:Revenues = 11665000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | mapped-sample | agree | page value 632000000 vs printed 632000000 |
| research_and_development | NOTE | agree | page value 33000000 vs API 33000000 |
| weighted_basic_shares | NOTE | agree | page value 115220000 vs API 115220000 |
| weighted_diluted_shares | NOTE | agree | page value 115740000 vs API 115740000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -320000000 vs printed -320000000 |
| sbc | mapped-sample | agree | page value 48000000 vs printed 48000000 |
| cash_paid_for_interest | NOTE | agree | page value 372000000 vs API 372000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 286000000 vs API 286000000 |
| total_debt | component sum | agree | page value 5968000000 vs printed 5968000000 |
