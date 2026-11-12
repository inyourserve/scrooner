# MOH document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001179929-26-000005 (CIK 0001179929, filed 2026-02-10): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001179929-16-000231 (CIK 0001179929, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R8.htm
- 10-K 0001179929-24-000033 (CIK 0001179929, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0001179929-21-000024 (CIK 0001179929, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0001179929.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Total revenue | 45426000000 | 45426000000 | 40650000000 | 40650000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Medical care costs | 39488000000 | 39488000000 | 34428000000 | 34428000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R91.htm | Segments - Reconciliation of Gross Margin to Consolidated Income (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'Segments - Reconciliation of Gross Margin to Consolidated Income (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 44645000000 | 44645000000 | 38943000000 | 38943000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative expenses | 3009000000 | 3009000000 | 2743000000 | 2743000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (858 tags across all 97 R pages, face and notes) of 0001179929-26-000005; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 781000000 | 781000000 | 1707000000 | 1707000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | 192000000 | 192000000 | 118000000 | 118000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income tax expense | 589000000 | 589000000 | 1589000000 | 1589000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 117000000 | 117000000 | 410000000 | 410000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income | 472000000 | 472000000 | 1179000000 | 1179000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 8.93 | 8.93 | 20.52 | 20.52 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 8.92 | 8.92 | 20.42 | 20.42 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 52800000 | 52800000 | 57400000 | 57400000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 52900000 | 52900000 | 57700000 | 57700000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 4248000000 | 4248000000 | 4662000000 | 4662000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables | 3533000000 | 3533000000 | 3299000000 | 3299000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (858 tags across all 97 R pages, face and notes) of 0001179929-26-000005; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 12444000000 | 12444000000 | 12773000000 | 12773000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Property, equipment, and capitalized software, net | 301000000 | 301000000 | 288000000 | 288000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R5.htm | Goodwill and intangible assets, net | 2195000000 | 2195000000 | 1938000000 | 1938000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 15564000000 | 15564000000 | 15630000000 | 15630000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable, accrued liabilities and other | 1093000000 | 1093000000 | 1331000000 | 1331000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 7372000000 | 7372000000 | 7896000000 | 7896000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 11495000000 | 11495000000 | 11134000000 | 11134000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 4069000000 | 4069000000 | 4496000000 | 4496000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash (used in) provided by operating activities | -535000000 | -535000000 | 644000000 | 644000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | 312000000 | 312000000 | -464000000 | -464000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -170000000 | -170000000 | -347000000 | -347000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, equipment and capitalized software | -101000000 | 101000000 | -100000000 | 100000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 195000000 | 195000000 | 186000000 | 186000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 47000000 | 47000000 | 116000000 | 116000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (858 tags across all 97 R pages, face and notes) of 0001179929-26-000005; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Common stock purchases | -1000000000 | 1000000000 | -1000000000 | 1000000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid during the period for interest | 181000000 | 181000000 | 121000000 | 121000000 | Y | FILING-CHECKED | accn 0001179929-26-000005 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R80.htm | Income Taxes - Schedule of Income Taxes Paid (Details) |  | 275000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R80.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R5.htm | Long-term debt | 3766000000 | 3766000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares, outstanding (in shares) | 51000000 | 51000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Total revenue' on us-gaap:Revenues = 14178000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001179929-16-000231 R4.htm read; no row matched (auto)
- gross_profit: FY2015 10-K 0001179929-16-000231 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 13791000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001179929-16-000231 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 1146000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 387000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 66000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Income from continuing operations before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 322000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 179000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 143000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Basic net income per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.75 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Diluted net income per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.58 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 52000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001179929-16-000231 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 56000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2329000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Receivables' on us-gaap:ReceivablesNetCurrent = 597000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 5306000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Property, equipment, and capitalized software, net' on us-gaap:PropertyPlantAndEquipmentNet = 393000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 519000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Total assets' on us-gaap:Assets = 6576000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 362000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 3822000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 5019000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001179929-16-000231 R2.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 1557000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1125000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1420000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1085000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001179929-16-000231 R8.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 126000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 23000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Treasury stock purchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Interest' on us-gaap:InterestPaid = 38000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001179929-16-000231 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaidNet = 197000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001179929-24-000033 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = 109000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001179929-21-000024 R2.htm prints 'Income before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 961000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | NOTE | agree | value 3564000000 read off its own R page (no companyfacts fact to compare) |
| operating_expenses | combined | agree | page value 44645000000 vs printed 44645000000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_and_equivalents | mapped-sample | agree | page value 4248000000 vs printed 4248000000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_financing | mapped-sample | agree | page value -170000000 vs printed -170000000 |
| depreciation_and_amortization | mapped-sample | agree | page value 195000000 vs printed 195000000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | mapped-sample | agree | page value -1000000000 vs printed -1000000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 275000000 vs API 275000000 |
| total_debt | component sum | agree | page value 3950000000 vs printed 3950000000 |
