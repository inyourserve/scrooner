# DDS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000028917-26-000006 (CIK 0000028917, filed 2026-03-27): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0000028917-16-000262 (CIK 0000028917, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0000028917-18-000159 (CIK 0000028917, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0000028917-22-000009 (CIK 0000028917, era filing): COVER R1.htm, IS R5.htm, CI R6.htm, CF R10.htm
- companyfacts CIK0000028917.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total net sales and service charges and other income | 6563336000 | 6563336000 | 6590231000 | 6590231000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Cost of sales | 3916862000 | 3916862000 | 3919549000 | 3919549000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R44.htm | Business Segments - Information by segment (Details) |  | 2556761000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R44.htm 'Business Segments - Information by segment (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (720 tags across all 74 R pages, face and notes) of 0000028917-26-000006; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative expenses | 1759236000 | 1759236000 | 1731234000 | 1731234000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (720 tags across all 74 R pages, face and notes) of 0000028917-26-000006; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (720 tags across all 74 R pages, face and notes) of 0000028917-26-000006; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R44.htm | Business Segments - Information by segment (Details) |  | 40982000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R44.htm 'Business Segments - Information by segment (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R4.htm | Income before income taxes and equity in earnings of joint ventures | 694480000 | 694480000 | 729701000 | 729701000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income taxes | 124700000 | 124700000 | 136225000 | 136225000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 570187000 | 570187000 | 593476000 | 593476000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Earnings per share - Basic | 36.42 | 36.42 | 36.82 | 36.82 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Earnings per share - Diluted | 36.42 | 36.42 | 36.82 | 36.82 | Y | FILING-CHECKED | accn 0000028917-26-000006 R4.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R65.htm | Earnings Per Share (Details) |  | 15655 |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R65.htm | Earnings Per Share (Details) |  | 15655 |  |  |  | FILING-CHECKED | not on the face statement; shown in R65.htm 'Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 861460000 | 861460000 | 717854000 | 717854000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable | 39724000 | 39724000 | 55700000 | 55700000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| inventory | mapped | us-gaap:RetailRelatedInventoryMerchandise | R2.htm | Merchandise inventories | 1201098000 | 1201098000 | 1172047000 | 1172047000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 2386571000 | 2386571000 | 2368070000 | 2368070000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R2.htm | Property and equipment, net | 911806000 | 911806000 | 1002248000 | 1002248000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| goodwill | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (720 tags across all 74 R pages, face and notes) of 0000028917-26-000006; no face row matched |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 3505023000 | 3505023000 | 3531054000 | 3531054000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R2.htm | Trade accounts payable and accrued expenses | 772398000 | 772398000 | 795023000 | 795023000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 902084000 | 902084000 | 834906000 | 834906000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| total_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (720 tags across all 74 R pages, face and notes) of 0000028917-26-000006; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 1778970000 | 1778970000 | 1796160000 | 1796160000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R2.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 717008000 | 717008000 | 714127000 | 714127000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | 22537000 | 22537000 | -269731000 | -269731000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -595939000 | -595939000 | -534829000 | -534829000 | Y | FILING-CHECKED | accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchase of property and equipment and capitalized software | -93382000 | 93382000 | -104552000 | 104552000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | dds:DepreciationAndAmortizationOfPropertyAndOtherDeferredCosts | R9.htm | Depreciation and amortization of property and other deferred costs | 180862000 |  | 179522000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| sbc | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ShareBasedCompensation, AllocatedShareBasedCompensationExpense in MetaLinks.json (720 tags across all 74 R pages, face and notes) of 0000028917-26-000006; no face row matched |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends paid | -484876000 | 484876000 | -413795000 | 413795000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchase of treasury stock | -107756000 | 107756000 | -121034000 | 121034000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000028917-26-000006 R9.htm period ..2026-01-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R47.htm | Long-Term Debt - Narratives (Details) |  | 40900000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R47.htm 'Long-Term Debt - Narratives (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R57.htm | Income Taxes - Income taxes pad, net of refund (Details) (Imported) |  | 134300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R57.htm 'Income Taxes - Income taxes pad, net of refund (Details) (Imported)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:OtherLongTermDebtNoncurrent | R2.htm | Long-term debt | 225674000 | 225674000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 15617071 |  |  |  |  | FILING-CHECKED | balance-sheet date 2026-01-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Total net sales, service charges and other income' on us-gaap:Revenues = 6754545000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 4350805000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000028917-16-000262 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Selling, general and administrative expenses' on dds:AdvertisingSellingAdministrativeAndGeneralExpenses = 1669916000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000028917-16-000262 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Income before income taxes and income on and equity in losses of joint ventures' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 408784000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 140770000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 269370000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 6.91 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000028917-16-000262 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 6.91 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000028917-16-000262 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000028917-16-000262 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 202869000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Accounts receivable' on us-gaap:ReceivablesNetCurrent = 47138000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Merchandise inventories' on us-gaap:RetailRelatedInventoryMerchandise = 1374505000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1668883000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1939832000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Total assets' on us-gaap:Assets = 3865625000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Trade accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 691310000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 751216000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000028917-16-000262 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1795305000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 450226000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -132939000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -518170000 (FILING-CHECKED)
- capex: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Purchase of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -165788000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Depreciation and amortization of property and other deferred cost' on us-gaap:DepreciationDepletionAndAmortization = 252147000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -10008000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000028917-16-000262 R9.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -500000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000028917-16-000262 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000028917-16-000262 R9.htm read; no row matched (auto)
- cost_of_revenue: era 10-K 0000028917-18-000159 R4.htm prints 'Cost of sales' on us-gaap:CostOfRevenue = 4199718000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000028917-22-000009 R5.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 3747665000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0000028917-22-000009 R10.htm read; no row matched (auto)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (dds:DepreciationAndAmortizationOfPropertyAndOtherDeferredCosts)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | NOTE | agree | page value 2556761000 vs API 2556761000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | NOTE | agree | page value 40982000 vs API 40982000 |
| weighted_basic_shares | NOTE | agree | page value 15655 vs API 15655 |
| weighted_diluted_shares | NOTE | agree | page value 15655 vs API 15655 |
| cash_and_equivalents | mapped-sample | agree | page value 861460000 vs printed 861460000 |
| inventory | mapped-sample | agree | page value 1201098000 vs printed 1201098000 |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | mapped-sample | agree | page value 902084000 vs printed 902084000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sbc | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 40900000 vs API 40900000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 134300000 vs API 134300000 |
| total_debt | component sum | agree | page value 225674000 vs printed 225674000 |
| shares_outstanding | component sum | agree | page value 15617071 vs printed 15617071 |
