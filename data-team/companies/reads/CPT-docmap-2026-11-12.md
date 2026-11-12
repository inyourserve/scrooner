# CPT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-007697 (CIK 0000906345, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0000906345-16-000044 (CIK 0000906345, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0000906345.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Fee and asset management | 12967000 | 12967000 | 7137000 | 7137000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Total property expenses | 566710000 | 566710000 | 558805000 | 558805000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R58.htm | Segment Reporting (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R58.htm 'Segment Reporting (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 79344000 | 79344000 | 72365000 | 72365000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest | 138239000 | 138239000 | 129815000 | 129815000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic | R5.htm | Income from continuing operations before income taxes | 398917000 | 398917000 | 173766000 | 173766000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic | R5.htm | Income from continuing operations before income taxes | 398917000 | 398917000 | 173766000 | 173766000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to common shareholders | 384462000 | 384462000 | 163293000 | 163293000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Total earnings per common share – basic | 3.54 | 3.54 | 1.5 | 1.5 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Total earnings per common share – diluted | 3.54 | 3.54 | 1.5 | 1.5 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average number of common shares outstanding – basic | 108376000 | 108376000 | 108491000 | 108491000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average number of common shares outstanding – diluted | 108434000 | 108434000 | 108539000 | 108539000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 25203000 | 25203000 | 21045000 | 21045000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | cpt:AccountsReceivableAffiliates | R3.htm | Accounts receivable – affiliates | 8884000 |  | 8991000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-007697 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9042989000 | 9042989000 | 8852144000 | 8852144000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 248087000 | 248087000 | 215179000 | 215179000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-007697 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (887 tags across all 60 R pages, face and notes) of 0001628280-26-007697; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4604736000 | 4604736000 | 4104955000 | 4104955000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total common equity | 4362523000 | 4362523000 | 4675198000 | 4675198000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash from operating activities | 826621000 | 826621000 | 774877000 | 774877000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash from investing activities | -499539000 | -499539000 | -285230000 | -285230000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash from financing activities | -322049000 | -322049000 | -725485000 | -725485000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| capex | mapped | cpt:AccrualAssociatedWithConstructionAndCapitalExpenditures | R8.htm | Accrual associated with construction and capital expenditures | 31487000 |  | 24097000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 611025000 | 611025000 | 582014000 | 582014000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 16959000 | 16959000 | 15166000 | 15166000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Distributions to common shareholders and non-controlling interests | -460950000 | 460950000 | -450965000 | 450965000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common shares | -270654000 | 270654000 | -49997000 | 49997000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest, net of interest capitalized | 139625000 | 139625000 | 129637000 | 129637000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income taxes | 3482000 | 3482000 | 2816000 | 2816000 | Y | FILING-CHECKED | accn 0001628280-26-007697 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R48.htm | Notes Payable (Scheduled Repayments On Outstanding Debt) (Details) |  | 3900800000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R48.htm 'Notes Payable (Scheduled Repayments On Outstanding Debt) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R41.htm | Common Shares (Narrative) (Details) |  | 104300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R41.htm 'Common Shares (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000906345-16-000044 R4.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0000906345-16-000044 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000906345-16-000044 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0000906345-16-000044 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 46233000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Interest' on us-gaap:InterestExpense = 97312000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic = 260134000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic = 260134000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Net income attributable to common shareholders' on us-gaap:NetIncomeLoss = 249315000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Total earnings per common share - basic' on us-gaap:EarningsPerShareBasic = 2.77 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Total earnings per common share - diluted' on us-gaap:EarningsPerShareDiluted = 2.76 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Weighted average number of common shares outstanding - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 89120000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000906345-16-000044 R4.htm prints 'Weighted average number of common shares outstanding - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 89490000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000906345-16-000044 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 10617000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000906345-16-000044 R2.htm prints 'Accounts receivable - affiliates' on us-gaap:AccountsReceivableRelatedParties = 25100000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000906345-16-000044 R2.htm prints 'Total assets' on us-gaap:Assets = 6037612000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000906345-16-000044 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 133353000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000906345-16-000044 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 3065352000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000906345-16-000044 R2.htm prints 'Total common equity' on us-gaap:StockholdersEquity = 2816557000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Net cash from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 423238000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Net cash from investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -293308000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Net cash from financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -273231000 (FILING-CHECKED)
- capex: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Accrual associated with construction and capital expenditures' on cpt:AccrualAssociatedWithConstructionAndCapitalExpenditures = 24175000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 257082000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 17674000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Distributions to common shareholders and non-controlling interests' on us-gaap:PaymentsOfDividends = -253129000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000906345-16-000044 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Cash paid for interest, net of interest capitalized' on us-gaap:InterestPaidNet = 96179000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000906345-16-000044 R7.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 1889000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_receivable: API missing (cpt:AccountsReceivableAffiliates)
- capex: API missing (cpt:AccrualAssociatedWithConstructionAndCapitalExpenditures)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | NOTE | agree | value -72159000 read off its own R page (no companyfacts fact to compare) |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| weighted_diluted_shares | mapped-sample | agree | page value 108434000 vs printed 108434000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sbc | mapped-sample | agree | page value 16959000 vs printed 16959000 |
| dividends_paid | mapped-sample | agree | page value -460950000 vs printed -460950000 |
| total_debt | NOTE | agree | page value 3900800000 vs API 3900800000 |
| shares_outstanding | NOTE | agree | page value 104300000 vs API 104300000 |
