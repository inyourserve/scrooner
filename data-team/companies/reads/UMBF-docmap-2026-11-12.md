# UMBF document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-076496 (CIK 0000101382, filed 2026-02-26): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001193125-16-477882 (CIK 0000101382, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000950170-24-018456 (CIK 0000101382, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001193125-17-053195 (CIK 0000101382, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000101382.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R122.htm | Parent Company Financial Information - Schedule of Parent Company Statements of Income and Comprehensive Income (Detail) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R122.htm 'Parent Company Financial Information - Schedule of Parent Company Statements of ' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| sga_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R4.htm | Total interest expense | 1492075000 | 1492075000 | 1170117000 | 1170117000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before income taxes | 874955000 | 874955000 | 541273000 | 541273000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | 172557000 | 172557000 | 100030000 | 100030000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | NET INCOME | 702398000 | 702398000 | 441243000 | 441243000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income per common share - basic | 9.35 | 9.35 | 9.05 | 9.05 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income per common share - diluted | 9.29 | 9.29 | 8.99 | 8.99 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average common shares outstanding - basic | 73259082 | 73259082 | 48747814 | 48747814 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average common shares outstanding - diluted | 73670643 | 73670643 | 49056956 | 49056956 | Y | FILING-CHECKED | accn 0001193125-26-076496 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R2.htm | Cash and due from banks | 952547000 | 952547000 | 573175000 | 573175000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Premises and equipment, net | 398271000 | 398271000 | 221773000 | 221773000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 1839825000 | 1839825000 | 207385000 | 207385000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 73094090000 | 73094090000 | 50409664000 | 50409664000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1407 tags across all 128 R pages, face and notes) of 0001193125-26-076496; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 65400522000 | 65400522000 | 46943123000 | 46943123000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total shareholders' equity | 7693568000 | 7693568000 | 3466541000 | 3466541000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1026693000 | 1026693000 | 225286000 | 225286000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -5620098000 | -5620098000 | -3262501000 | -3262501000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 3916687000 | 3916687000 | 5957648000 | 5957648000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Net purchases of bank premises and equipment | -48584000 | 48584000 | -20009000 | 20009000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 141770000 | 141770000 | 52771000 | 52771000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Equity-based compensation | 37745000 | 37745000 | 22579000 | 22579000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Cash dividends paid | -135620000 | 135620000 | -77127000 | 77127000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Purchases of treasury stock | -17628000 | 17628000 | -7738000 | 7738000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Total interest payments | 1466097000 | 1466097000 | 1204688000 | 1204688000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income tax payments | 63242000 | 63242000 | 76930000 | 76930000 | Y | FILING-CHECKED | accn 0001193125-26-076496 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebt | R2.htm | Long-term debt | 474229000 | 474229000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 75960675 | 75960675 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-477882 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 18614000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 159285000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 43212000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 116073000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Net income - basic' on us-gaap:EarningsPerShareBasic = 2.46 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Net income - diluted' on us-gaap:EarningsPerShareDiluted = 2.44 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Weighted average shares outstanding - basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 47126252 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-477882 R4.htm prints 'Weighted average shares outstanding - diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 47579334 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-477882 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 458217000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-477882 R2.htm prints 'Premises and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 281471000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-477882 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 228346000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-477882 R2.htm prints 'Total assets' on us-gaap:Assets = 19094245000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-477882 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 17200551000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-477882 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 1893694000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 210961000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1330237000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 151158000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Purchases of premises and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -53760000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Net accretion of premiums and discounts from acquisition' on us-gaap:DepreciationAmortizationAndAccretionNet = -2727000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Equity based compensation' on us-gaap:ShareBasedCompensation = 10751000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividends = -45967000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -8457000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Total interest paid' on us-gaap:InterestPaid = 17812000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-477882 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 47086000 (FILING-CHECKED)
- interest_expense: era 10-K 0000950170-24-018456 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 918589000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001193125-17-053195 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 44076000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | value 338674000 read off its own R page (no companyfacts fact to compare) |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | mapped-sample | agree | page value 65400522000 vs printed 65400522000 |
| cfo | mapped-sample | agree | page value 1026693000 vs printed 1026693000 |
| dividends_paid | mapped-sample | agree | page value -135620000 vs printed -135620000 |
| total_debt | component sum | agree | page value 474229000 vs printed 474229000 |
