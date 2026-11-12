# AFG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001042046-26-000010 (CIK 0001042046, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001042046-16-000074 (CIK 0001042046, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001042046.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 8174000000 | 8174000000 | 8324000000 | 8324000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| operating_expenses | mapped | us-gaap:BenefitsLossesAndExpenses | R5.htm | Total costs and expenses | 7101000000 | 7101000000 | 7200000000 | 7200000000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Commissions and other underwriting expenses | 2059000000 | 2059000000 | 2007000000 | 2007000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Earnings before income taxes | 1073000000 | 1073000000 | 1124000000 | 1124000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest charges on borrowed money | 80000000 | 80000000 | 76000000 | 76000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Earnings before income taxes | 1073000000 | 1073000000 | 1124000000 | 1124000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 231000000 | 231000000 | 237000000 | 237000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Earnings | 842000000 | 842000000 | 887000000 | 887000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (USD per share) | 10.08 | 10.08 | 10.57 | 10.57 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (USD per share) | 10.08 | 10.08 | 10.57 | 10.57 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (shares) | 83500000 | 83500000 | 83900000 | 83900000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (shares) | 83500000 | 83500000 | 83900000 | 83900000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1727000000 | 1727000000 | 1406000000 | 1406000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 327000000 | 327000000 | 305000000 | 305000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 32642000000 | 32642000000 | 30836000000 | 30836000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 27822000000 | 27822000000 | 26370000000 | 26370000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Shareholders’ equity | 4820000000 | 4820000000 | 4466000000 | 4466000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 1533000000 | 1533000000 | 1152000000 | 1152000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -835000000 | -835000000 | 95000000 | 95000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -377000000 | -377000000 | -1066000000 | -1066000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R9.htm period ..2025-12-31 |
| capex | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1083 tags across all 107 R pages, face and notes) of 0001042046-26-000010; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R9.htm | Depreciation and amortization | 86000000 | 86000000 | 81000000 | 81000000 | Y | FILING-CHECKED | accn 0001042046-26-000010 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R82.htm | Shareholders' Equity - Narrative (Details) |  | 18000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R82.htm 'Shareholders' Equity - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends paid on Common Stock | -606000000 | 606000000 | -788000000 | 788000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001042046-26-000010 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of Common Stock | -99000000 | 99000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001042046-26-000010 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R75.htm | Long-Term Debt - Narrative (Details) |  | 74000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R75.htm 'Long-Term Debt - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R91.htm | Income Taxes - Cash payments for income taxes (Details) |  | 168000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R91.htm 'Income Taxes - Cash payments for income taxes (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Long-term debt | 1820000000 | 1820000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common Stock, shares outstanding | 83422202 | 83422202 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Total revenues' on us-gaap:Revenues = 6145000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Total costs and expenses' on us-gaap:BenefitsLossesAndExpenses = 5580000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001042046-16-000074 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Earnings before income taxes' on us-gaap:OperatingIncomeLoss = 565000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Interest charges on borrowed money' on us-gaap:InterestExpense = 74000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Earnings before income taxes' on us-gaap:OperatingIncomeLoss = 565000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 195000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Net Earnings Attributable to Shareholders' on us-gaap:NetIncomeLoss = 352000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Basic (USD per share)' on us-gaap:EarningsPerShareBasic = 4.02 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Diluted (USD per share)' on us-gaap:EarningsPerShareDiluted = 3.94 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 87600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001042046-16-000074 R4.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 89400000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001042046-16-000074 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1220000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001042046-16-000074 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 199000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001042046-16-000074 R2.htm prints 'Total assets' on us-gaap:Assets = 49859000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001042046-16-000074 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 45089000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001042046-16-000074 R2.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 4592000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001042046-16-000074 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1357000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001042046-16-000074 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -4577000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001042046-16-000074 R7.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 3097000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001042046-16-000074 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 132000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001042046-16-000074 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001042046-16-000074 R7.htm prints 'Cash dividends paid on Common Stock' on us-gaap:PaymentsOfDividendsCommonStock = -176000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001042046-16-000074 R7.htm prints 'Repurchases of Common Stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -126000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001042046-16-000074 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001042046-16-000074 R7.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_income | mapped-sample | agree | page value 1073000000 vs printed 1073000000 |
| diluted_eps | mapped-sample | agree | page value 10.08 vs printed 10.08 |
| weighted_basic_shares | mapped-sample | agree | page value 83500000 vs printed 83500000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| capex | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | combined | agree | page value 86000000 vs printed 86000000 |
| sbc | NOTE | agree | page value 18000000 vs API 18000000 |
| cash_paid_for_interest | NOTE | agree | page value 74000000 vs API 74000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 168000000 vs API 168000000 |
| total_debt | component sum | agree | page value 1820000000 vs printed 1820000000 |
