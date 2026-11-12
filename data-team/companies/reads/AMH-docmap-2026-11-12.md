# AMH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001562401-26-000010 (CIK 0001562401, filed 2026-02-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001562401-16-000057 (CIK 0001562401, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001562401-25-000013 (CIK 0001562401, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001562401-18-000029 (CIK 0001562401, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R10.htm
- companyfacts CIK0001562401.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, RegulatedAndUnregulatedOperatingRevenue, RegulatedOperatingRevenue in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods and services sold | 663954000 |  | 625883000 |  | API missing | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total expenses | 1583566000 | 1583566000 | 1502231000 | 1502231000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative expense | 83006000 | 83006000 | 83590000 | 83590000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest expense | 185198000 | 185198000 | 165351000 | 165351000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| income_before_tax | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments, IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| income_tax_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxExpenseBenefit in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R5.htm | Net income attributable to common shareholders / unitholders | 439030000 | 439030000 | 398482000 | 398482000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.18 | 1.18 | 1.08 | 1.08 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.18 | 1.18 | 1.08 | 1.08 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 370556400 | 370556400 | 367454012 | 367454012 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 370906582 | 370906582 | 367989537 | 367989537 | Y | FILING-CHECKED | accn 0001562401-26-000010 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 108516000 | 108516000 | 199413000 | 199413000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R3.htm | Rent and other receivables | 43119000 | 43119000 | 48452000 | 48452000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 120279000 | 120279000 | 120279000 | 120279000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 13242120000 | 13242120000 | 13381151000 | 13381151000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 436879000 | 436879000 | 521759000 | 521759000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 5532614000 | 5532614000 | 5532521000 | 5532521000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders' equity | 7033748000 | 7033748000 | 7160016000 | 7160016000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 864327000 | 864327000 | 811535000 | 811535000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used for investing activities | -328167000 | -328167000 | -825876000 | -825876000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash (used for) provided by financing activities | -655686000 | -655686000 | 142696000 | 142696000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsForCapitalImprovements | R9.htm | Renovations to single-family properties | -40645000 | 40645000 | -34052000 | 34052000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 504341000 | 504341000 | 477010000 | 477010000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Noncash share-based compensation | 25815000 | 25815000 | 30984000 | 30984000 | Y | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Distributions to common shareholders | -446292000 | 446292000 | -383535000 | 383535000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of Class A common shares | -150093000 |  | 0 |  | API missing | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash payments for interest, net of amounts capitalized | -172220000 | 172220000 | -128056000 | 128056000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001562401-26-000010 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (969 tags across all 97 R pages, face and notes) of 0001562401-26-000010; no face row matched |
| total_debt | mapped | us-gaap:LongTermDebt | R64.htm | Debt - Schedule of Debt (Details) |  | 5095735000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'Debt - Schedule of Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 366656740 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- cost_of_revenue: FY2015 10-K 0001562401-16-000057 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001562401-16-000057 R4.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 675794000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001562401-16-000057 R4.htm prints 'General and administrative expense' on us-gaap:GeneralAndAdministrativeExpense = 24906000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001562401-16-000057 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 89413000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001562401-16-000057 R4.htm prints 'Net loss attributable to common shareholders' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = -84577000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001562401-16-000057 R4.htm prints 'Net loss attributable to common shareholders per share - basic and diluted (in d' on us-gaap:EarningsPerShareBasicAndDiluted = -0.4 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001562401-16-000057 R4.htm prints 'Net loss attributable to common shareholders per share - basic and diluted (in d' on us-gaap:EarningsPerShareBasicAndDiluted = -0.4 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001562401-16-000057 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001562401-16-000057 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 57686000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Rent and other receivables, net' on amh:AccountsAndOtherReceivablesNet = 13936000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 120655000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Total assets' on us-gaap:Assets = 6807786000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 154751000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2872553000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001562401-16-000057 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 3259345000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 201365000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -884942000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 632476000 (FILING-CHECKED)
- capex: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Initial renovations to single-family properties' on us-gaap:PaymentsForCapitalImprovements = -147583000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 242848000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Noncash share-based compensation' on us-gaap:ShareBasedCompensation = 3125000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Distributions to common shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -42126000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001562401-16-000057 R8.htm prints 'Repurchase of Class A common shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -57383000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001562401-16-000057 R8.htm read; no row matched (auto)
- operating_expenses: era 10-K 0001562401-25-000013 R5.htm prints 'Total expenses' on us-gaap:OperatingExpenses = 1502231000 (FILING-CHECKED)
- basic_eps: era 10-K 0001562401-18-000029 R4.htm prints 'Net loss attributable to common shareholders per share - basic and diluted (in d' on us-gaap:EarningsPerShareBasicAndDiluted = -0.08 (FILING-CHECKED)
- diluted_eps: era 10-K 0001562401-18-000029 R4.htm prints 'Net loss attributable to common shareholders per share - basic and diluted (in d' on us-gaap:EarningsPerShareBasicAndDiluted = -0.08 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)
- share_buybacks: API missing (us-gaap:PaymentsForRepurchaseOfCommonStock)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cost_of_revenue | mapped-sample | agree | page value 663954000 vs printed 663954000 |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1583566000 vs printed 1583566000 |
| sga_expense | mapped-sample | agree | page value 83006000 vs printed 83006000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_and_equivalents | mapped-sample | agree | page value 108516000 vs printed 108516000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | page value 5095735000 vs API 5095735000 |
| shares_outstanding | component sum | agree | page value 366656740 vs printed 366656740 |
