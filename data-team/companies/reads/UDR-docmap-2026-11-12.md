# UDR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000074208-26-000013 (CIK 0000074208, filed 2026-02-17): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000074208-16-000140 (CIK 0000074208, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000074208.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total revenues | 1712317000 | 1712317000 | 1671842000 | 1671842000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total operating expenses | 1401624000 | 1401624000 | 1404140000 | 1404140000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 85104000 | 85104000 | 84305000 | 84305000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Operating income | 553606000 | 553606000 | 284569000 | 284569000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R4.htm | Interest expense | -196619000 | 196619000 | -195712000 | 195712000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income/(loss) before income taxes | 404550000 | 404550000 | 96756000 | 96756000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Tax (provision)/benefit, net | -835000 | 835000 | -879000 | 879000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income/(loss) attributable to UDR, Inc. | 377704000 | 377704000 | 89585000 | 89585000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Income/(loss) per weighted average common share - basic | 1.13 | 1.13 | 0.26 | 0.26 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Income/(loss) per weighted average common share - diluted | 1.13 | 1.13 | 0.26 | 0.26 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average number of common shares outstanding - basic | 330322000 | 330322000 | 329290000 | 329290000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average number of common shares outstanding - diluted | 331053000 | 331053000 | 330116000 | 330116000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 1222000 | 1222000 | 1326000 | 1326000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:NotesReceivableNet | R2.htm | Notes receivable, net | 149979000 | 149979000 | 247849000 | 247849000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000074208-26-000013 R2.htm period ..2025-12-31 |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| ppe_net | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| goodwill | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 10605674000 | 10605674000 | 10897586000 | 10897586000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R2.htm | Accounts payable, accrued expenses, and other liabilities | 142102000 | 142102000 | 115105000 | 115105000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000074208-26-000013 R2.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1266 tags across all 85 R pages, face and notes) of 0000074208-26-000013; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 6456911000 | 6456911000 | 6436691000 | 6436691000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders' equity | 3288462000 | 3288462000 | 3443205000 | 3443205000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by/(used in) operating activities | 902887000 | 902887000 | 876848000 | 876848000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by/(used in) investing activities | -150990000 | -150990000 | -276351000 | -276351000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by/(used in) financing activities | -750392000 | -750392000 | -599936000 | -599936000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsForCapitalImprovements | R8.htm | Capital expenditures and other major improvements - real estate assets | -252857000 | 252857000 | -249886000 | 249886000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 680035000 | 680035000 | 695473000 | 695473000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Amortization of share-based compensation | 26484000 | 26484000 | 32625000 | 32625000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Distributions paid to common stockholders | -567864000 | 567864000 | -558482000 | 558482000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common shares | -117811000 | 117811000 |  |  | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid during the period, net of amounts capitalized | 190511000 | 190511000 | 192101000 | 192101000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid/(refunds received) for income taxes | 1373000 | 1373000 | 1044000 | 1044000 | Y | FILING-CHECKED | accn 0000074208-26-000013 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R60.htm | SECURED AND UNSECURED DEBT, NET - Summary (Details) |  | 5821369000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R60.htm 'SECURED AND UNSECURED DEBT, NET - Summary (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 328273044 | 328273044 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Total revenues' on us-gaap:Revenues = 894638000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 735047000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000074208-16-000140 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 59690000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 159591000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Interest Expense' on us-gaap:InterestExpense = -121875000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Income/(loss) before income taxes, discontinued operations and gain/(loss) on sa' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 101596000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Tax benefit/(provision), net' on us-gaap:IncomeTaxExpenseBenefit = 3886000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Net income/(loss) attributable to Entity' on us-gaap:NetIncomeLoss = 340383000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Net income/(loss) attributable to common stockholders' on us-gaap:EarningsPerShareBasic = 1.3 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Net income(loss) attributable to common stockholders' on us-gaap:EarningsPerShareDiluted = 1.29 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Weighted average number of common shares outstanding — basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 258669000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000074208-16-000140 R4.htm prints 'Weighted average number of common shares outstanding — diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 263752000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000074208-16-000140 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 6742000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000074208-16-000140 R2.htm prints 'Notes receivable, net' on us-gaap:NotesReceivableNet = 16694000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000074208-16-000140 R2.htm prints 'Total assets' on us-gaap:Assets = 7663844000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000074208-16-000140 R2.htm prints 'Accounts payable, accrued expenses, and other liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 81356000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000074208-16-000140 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 3816797000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000074208-16-000140 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 2899755000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 431615000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Net cash provided by/(used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -238449000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Net cash (used in)/provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -201648000 (FILING-CHECKED)
- capex: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Capital expenditures - non-real estate assets' on us-gaap:PaymentsToAcquireProductiveAssets = -4049000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Deprecation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 381277000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Amortization of share-based compensation' on us-gaap:ShareBasedCompensation = 18017000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Distributions paid to common stockholders' on us-gaap:PaymentsOfDividendsCommonStock = -283168000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000074208-16-000140 R8.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000074208-16-000140 R8.htm prints 'Interest paid during the period, net of amounts capitalized' on us-gaap:InterestPaidNet = 130240000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000074208-16-000140 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1401624000 vs printed 1401624000 |
| sga_expense | mapped-sample | agree | page value 85104000 vs printed 85104000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cfo | mapped-sample | agree | page value 902887000 vs printed 902887000 |
| total_debt | NOTE | agree | page value 5821369000 vs API 5821369000 |
| shares_outstanding | mapped-sample | agree | page value 328273044 vs printed 328273044 |
