# FHN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000036966-26-000051 (CIK 0000036966, filed 2026-02-26): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000930413-16-005653 (CIK 0000036966, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R10.htm
- 10-K 0000036966-24-000015 (CIK 0000036966, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000930413-17-000713 (CIK 0000036966, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000036966.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R132.htm | Business Segment Information - Schedule of Amounts of Consolidated Revenue, Expense, Tax and Assets by Segment (Details) |  | 3419000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R132.htm 'Business Segment Information - Schedule of Amounts of Consolidated Revenue, Expe' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R4.htm | Total interest expense | 1564000000 | 1564000000 | 1841000000 | 1841000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 1280000000 | 1280000000 | 1005000000 | 1005000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | 282000000 | 282000000 | 211000000 | 211000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to controlling interest | 982000000 | 982000000 | 775000000 | 775000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic earnings per share (in dollars per share) | 1.89 | 1.89 | 1.37 | 1.37 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted earnings per share (in dollars per share) | 1.87 | 1.87 | 1.36 | 1.36 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average common shares (in shares) | 505130000 | 505130000 | 540317000 | 540317000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted average common shares (in shares) | 511107000 | 511107000 | 544285000 | 544285000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R2.htm | Cash and due from banks | 961000000 | 961000000 | 906000000 | 906000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Premises and equipment | 544000000 | 544000000 | 574000000 | 574000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1510000000 | 1510000000 | 1510000000 | 1510000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 83876000000 | 83876000000 | 82152000000 | 82152000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1544 tags across all 159 R pages, face and notes) of 0000036966-26-000051; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 74734000000 | 74734000000 | 73041000000 | 73041000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | FHN shareholders' equity | 8847000000 | 8847000000 | 8816000000 | 8816000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 628000000 | 628000000 | 1268000000 | 1268000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -1094000000 | -1094000000 | -1058000000 | -1058000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 524000000 | 524000000 | -404000000 | -404000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of premises and equipment | -33000000 | 33000000 | -44000000 | 44000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | fhn:DepreciationPremisesAndEquipment | R8.htm | Depreciation and amortization of premises and equipment | 56000000 |  | 55000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 61000000 | 61000000 | 59000000 | 59000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Cash dividends paid | -314000000 | 314000000 | -332000000 | 332000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of shares | -918000000 | 918000000 | -626000000 | 626000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Total interest paid | 1584000000 | 1584000000 | 1869000000 | 1869000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Total taxes paid | 62000000 | 62000000 | 106000000 | 106000000 | Y | FILING-CHECKED | accn 0000036966-26-000051 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings | R2.htm | Short-term borrowings | 3254000000 | 3254000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Consolidated Statements of Changes in Equity |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R6.htm 'Consolidated Statements of Changes in Equity' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Adjusted gross income after provision for loan losses' on us-gaap:Revenues = 1162045000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 82685000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Income/(loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 108254000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Provision/(benefit) for income taxes (2015 includes $.5 million of tax expense a' on us-gaap:IncomeTaxExpenseBenefit = 10941000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Net income/(loss) attributable to controlling interest' on us-gaap:NetIncomeLoss = 85879000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Basic earnings/(loss) per share available to common shareholders (Note 16)' on us-gaap:EarningsPerShareBasic = 0.34 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Diluted earnings/(loss) per share available to common shareholders (Note 16)' on us-gaap:EarningsPerShareDiluted = 0.34 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Weighted average common shares (Note 16)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 234189000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000930413-16-005653 R4.htm prints 'Diluted average common shares (Note 16)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 236266000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000930413-16-005653 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 300811000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000930413-16-005653 R2.htm prints 'Premises and equipment, net (Note 6)' on us-gaap:PropertyPlantAndEquipmentNet = 275619000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000930413-16-005653 R2.htm prints 'Goodwill (Note 7)' on us-gaap:Goodwill = 191307000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000930413-16-005653 R2.htm prints 'Total assets' on us-gaap:Assets = 26195136000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000930413-16-005653 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 23555550000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000930413-16-005653 R2.htm prints 'Total First Horizon National Corporation Shareholders' Equity' on us-gaap:StockholdersEquity = 2344155000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Net cash provided/(used) by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 367163000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Net cash provided/(used) by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -520014000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Net cash provided/(used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 112509000 (FILING-CHECKED)
- capex: FY2015 10-K 0000930413-16-005653 R10.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Depreciation and amortization of premises and equipment' on fhn:DepreciationPremisesAndEquipmentIncludingAmountAttributableToDiscontinuedOperations = 35780000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 13796000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -53947000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Repurchase of shares' on us-gaap:PaymentsForRepurchaseOfCommonStock = -32648000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Total interest paid' on us-gaap:InterestPaidNet = 90722000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000930413-16-005653 R10.htm prints 'Total taxes paid' on us-gaap:IncomeTaxesPaid = 14990000 (FILING-CHECKED)
- interest_expense: era 10-K 0000036966-24-000015 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 1560000000 (FILING-CHECKED)
- capex: era 10-K 0000036966-24-000015 R8.htm read; no row matched (auto)
- capex: era 10-K 0000930413-17-000713 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (fhn:DepreciationPremisesAndEquipment)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 3419000000 vs API 3419000000 |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| diluted_eps | mapped-sample | agree | page value 1.87 vs printed 1.87 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cfo | mapped-sample | agree | page value 628000000 vs printed 628000000 |
| total_debt | component sum | agree | page value 3254000000 vs printed 3254000000 |
| shares_outstanding | mapped-sample | DISAGREE | us-gaap:CommonStockSharesOutstanding not found with a value in the 2025-12-31 column on R6.htm |
