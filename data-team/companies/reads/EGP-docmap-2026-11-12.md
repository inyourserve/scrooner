# EGP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000049600-26-000010 (CIK 0000049600, filed 2026-02-11): COVER R1.htm, BS R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000049600-16-000047 (CIK 0000049600, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000049600-23-000021 (CIK 0000049600, era filing): COVER R1.htm, BS R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000049600-25-000019 (CIK 0000049600, era filing): COVER R1.htm, BS R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0000049600.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Revenues | 721336000 | 721336000 | 640234000 | 640234000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Expenses | 433774000 | 433774000 | 385027000 | 385027000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 23960000 | 23960000 | 20619000 | 20619000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense | -32113000 | 32113000 | -38956000 | 38956000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| income_before_tax | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments, IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| income_tax_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxExpenseBenefit in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R4.htm | NET INCOME ATTRIBUTABLE TO EASTGROUP PROPERTIES, INC. COMMON STOCKHOLDERS | 257402000 | 257402000 | 227751000 | 227751000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income attributable to common stockholders | 4.88 | 4.88 | 4.67 | 4.67 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income attributable to common stockholders | 4.87 | 4.87 | 4.66 | 4.66 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average shares outstanding (in shares) | 52723000 | 52723000 | 48803000 | 48803000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average shares outstanding (in shares) | 52814000 | 52814000 | 48911000 | 48911000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1007000 | 1007000 | 17529000 | 17529000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000049600-26-000010 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R49.htm | OTHER ASSETS (Details) |  | 990000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R49.htm 'OTHER ASSETS (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 5431807000 | 5431807000 | 5077476000 | 5077476000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 169945000 | 169945000 | 147342000 | 147342000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000049600-26-000010 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 1935219000 | 1935219000 | 1784932000 | 1784932000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Stockholders’ Equity | 3496201000 | 3496201000 | 3292179000 | 3292179000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | NET CASH PROVIDED BY OPERATING ACTIVITIES | 480734000 | 480734000 | 416587000 | 416587000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | NET CASH USED IN INVESTING ACTIVITIES | -576281000 | -576281000 | -724342000 | -724342000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | NET CASH PROVIDED BY FINANCING ACTIVITIES | 79025000 | 79025000 | 285021000 | 285021000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsForCapitalImprovements | R6.htm | Real estate improvements | -75830000 | 75830000 | -59288000 | 59288000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 216732000 | 216732000 | 189411000 | 189411000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R6.htm | Stock-based compensation expense | 11793000 | 11793000 | 10476000 | 10476000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| share_buybacks | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Cash paid for interest, net of amount capitalized | 30558000 | 30558000 | 37185000 | 37185000 | Y | FILING-CHECKED | accn 0000049600-26-000010 R6.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (1435 tags across all 62 R pages, face and notes) of 0000049600-26-000010; no face row matched |
| total_debt | mapped | us-gaap:DebtInstrumentCarryingAmount | R51.htm | UNSECURED DEBT (Details) |  | 1615000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R51.htm 'UNSECURED DEBT (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common shares, outstanding | 53348800 | 53348800 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Revenues' on us-gaap:Revenues = 235008000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Expenses' on us-gaap:CostsAndExpenses = 155947000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000049600-16-000047 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 15091000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -34666000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000049600-16-000047 R4.htm prints 'NET INCOME ATTRIBUTABLE TO EASTGROUP PROPERTIES, INC. COMMON STOCKHOLDERS' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 47866000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Net income attributable to common stockholders' on us-gaap:EarningsPerShareBasic = 1.49 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Net income attributable to common stockholders' on us-gaap:EarningsPerShareDiluted = 1.49 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Weighted average shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 32091000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000049600-16-000047 R4.htm prints 'Weighted average shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 32196000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000049600-16-000047 R2.htm prints 'Cash' on us-gaap:Cash = 48000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000049600-16-000047 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000049600-16-000047 R2.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 1666232000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000049600-16-000047 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 44181000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000049600-16-000047 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 1107031000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000049600-16-000047 R2.htm prints 'Total Stockholders’ Equity' on us-gaap:StockholdersEquity = 554862000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000049600-16-000047 R7.htm prints 'NET CASH PROVIDED BY OPERATING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 131385000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000049600-16-000047 R7.htm prints 'NET CASH USED IN INVESTING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -156418000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000049600-16-000047 R7.htm prints 'NET CASH PROVIDED BY FINANCING ACTIVITIES' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 25070000 (FILING-CHECKED)
- capex: FY2015 10-K 0000049600-16-000047 R7.htm prints 'Real estate improvements' on us-gaap:PaymentsForCapitalImprovements = -24514000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000049600-16-000047 R7.htm prints 'Depreciation and amortization from continuing operations' on us-gaap:DepreciationDepletionAndAmortization = 73290000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000049600-16-000047 R7.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 6733000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000049600-16-000047 R7.htm prints 'Cash paid for interest, net of amount capitalized of $5,257, $4,942, and $5,064 ' on us-gaap:InterestPaidNet = 33164000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000049600-23-000021 R3.htm prints 'Cash' on us-gaap:Cash = 56000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0000049600-25-000019 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents = 17529000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 433774000 vs printed 433774000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | mapped-sample | agree | page value -32113000 vs printed -32113000 |
| income_before_tax | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_and_equivalents | mapped-sample | agree | page value 1007000 vs printed 1007000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | NOTE | agree | page value 990000 vs API 990000 |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -576281000 vs printed -576281000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_debt | NOTE | agree | page value 1615000000 vs API 1615000000 |
