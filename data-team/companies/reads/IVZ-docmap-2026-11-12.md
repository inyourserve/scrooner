# IVZ document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000914208-26-000079 (CIK 0000914208, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0000914208-16-000846 (CIK 0000914208, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000914208-18-000255 (CIK 0000914208, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000914208-24-000219 (CIK 0000914208, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0000914208.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total operating revenues | 6377100000 | 6377100000 | 6067000000 | 6067000000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (899 tags across all 102 R pages, face and notes) of 0000914208-26-000079; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (899 tags across all 102 R pages, face and notes) of 0000914208-26-000079; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 7072800000 | 7072800000 | 5234900000 | 5234900000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 576500000 | 576500000 | 594700000 | 594700000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (899 tags across all 102 R pages, face and notes) of 0000914208-26-000079; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income/(loss) | -695700000 | -695700000 | 832100000 | 832100000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -82500000 | 82500000 | -58000000 | 58000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income/(loss) before income taxes | -379400000 | -379400000 | 1005300000 | 1005300000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax benefit/(provision) | 204600000 | -204600000 | -252900000 | 252900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R5.htm | Net income/(loss) attributable to Invesco Ltd. | -726300000 | -726300000 | 538000000 | 538000000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | -basic (in usd per share) | -1.6 | -1.6 | 1.18 | 1.18 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | -diluted (usd per share) | -1.6 | -1.6 | 1.18 | 1.18 | Y | FILING-CHECKED | accn 0000914208-26-000079 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R91.htm | EARNINGS PER COMMON SHARE - Calculation of Earnings Per Share (Details) |  | 452600000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'EARNINGS PER COMMON SHARE - Calculation of Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R91.htm | EARNINGS PER COMMON SHARE - Calculation of Earnings Per Share (Details) |  | 455000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'EARNINGS PER COMMON SHARE - Calculation of Earnings Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1037500000 | 1037500000 | 986500000 | 986500000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R3.htm | Accounts receivable | 884700000 | 884700000 | 740800000 | 740800000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (899 tags across all 102 R pages, face and notes) of 0000914208-26-000079; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (899 tags across all 102 R pages, face and notes) of 0000914208-26-000079; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, equipment and software, net | 378900000 | 378900000 | 479000000 | 479000000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 8477100000 | 8477100000 | 8318100000 | 8318100000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 27094000000 | 27094000000 | 27008900000 | 27008900000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 1303700000 | 1303700000 | 1285300000 | 1285300000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (899 tags across all 102 R pages, face and notes) of 0000914208-26-000079; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 14089100000 | 14089100000 | 11340100000 | 11340100000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total equity attributable to Invesco Ltd. | 12231000000 | 12231000000 | 14559900000 | 14559900000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by/(used in) operating activities | 1525300000 | 1525300000 | 1190000000 | 1190000000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by/(used in) investing activities | -974400000 | -974400000 | 68400000 | 68400000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by/(used in) financing activities | -149500000 | -149500000 | -1661600000 | -1661600000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchase of property, equipment and software | -84300000 | 84300000 | -69100000 | 69100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Amortization and depreciation | 155900000 | 155900000 | 179600000 | 179600000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Common share-based compensation expense | 80000000 | 80000000 | 104600000 | 104600000 | Y | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid - common | -377300000 | 377300000 | -371500000 | 371500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchases of treasury shares | -123600000 | 123600000 | -79300000 | 79300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | -77200000 | 77200000 | -53600000 | 53600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Taxes paid | -238700000 | 238700000 | -236300000 | 236300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000914208-26-000079 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Debt | 1825100000 | 1825100000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R64.htm | SHARE CAPITAL - Movements in Shares Issued and Outstanding (Details) |  | 444000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'SHARE CAPITAL - Movements in Shares Issued and Outstanding (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Total operating revenues' on us-gaap:Revenues = 5122900000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 3764500000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000914208-16-000846 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 361700000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1358400000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -81700000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1362100000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = -398000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Net income attributable to Invesco Ltd.' on us-gaap:NetIncomeLoss = 968100000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Basic earnings per share (usd per share)' on us-gaap:EarningsPerShareBasic = 2.26 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000914208-16-000846 R4.htm prints 'Diluted earnings per share (usd per share)' on us-gaap:EarningsPerShareDiluted = 2.26 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000914208-16-000846 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000914208-16-000846 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1851400000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Unsettled fund receivables' on ivz:UnsettledFundReceivables = 566300000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Property, equipment and software, net' on us-gaap:PropertyPlantAndEquipmentNet = 426900000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 6175700000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Total assets' on us-gaap:Assets = 25073200000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 863100000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 16210200000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000914208-16-000846 R2.htm prints 'Total equity attributable to Invesco Ltd.' on us-gaap:StockholdersEquity = 7885300000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Net cash provided by/(used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1053500000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Net cash provided by/(used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -664800000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Net cash provided by/(used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 23300000 (FILING-CHECKED)
- capex: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Purchase of property, equipment and software' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -124500000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Amortization and depreciation' on us-gaap:DepreciationDepletionAndAmortization = 93600000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 150300000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -454500000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Purchases of treasury shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -548800000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Interest paid' on us-gaap:InterestPaidNet = -67500000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000914208-16-000846 R6.htm prints 'Taxes paid' on us-gaap:IncomeTaxesPaidNet = -388700000 (FILING-CHECKED)
- revenue: era 10-K 0000914208-18-000255 R4.htm prints 'Total operating revenues' on us-gaap:Revenues = 5160300000 (FILING-CHECKED)
- interest_expense: era 10-K 0000914208-24-000219 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -70500000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | mapped-sample | agree | page value -695700000 vs printed -695700000 |
| diluted_eps | mapped-sample | agree | page value -1.6 vs printed -1.6 |
| weighted_basic_shares | NOTE | agree | page value 452600000 vs API 452600000 |
| weighted_diluted_shares | NOTE | agree | page value 455000000 vs API 455000000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | mapped-sample | agree | page value 155900000 vs printed 155900000 |
| total_debt | component sum | agree | page value 1825100000 vs printed 1825100000 |
| shares_outstanding | NOTE | agree | page value 444000000 vs API 444000000 |
