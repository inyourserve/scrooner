# JEF document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000096223-26-000009 (CIK 0000096223, filed 2026-01-28): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R7.htm, CF R11.htm
- 10-K 0000096223-16-000049 (CIK 0000096223, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R8.htm
- 10-K 0000096223-18-000009 (CIK 0000096223, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R8.htm
- 10-K 0000096223-24-000006 (CIK 0000096223, era filing): COVER R1.htm, BS R4.htm, BSP R5.htm, IS R6.htm, CI R7.htm, CF R10.htm
- companyfacts CIK0000096223.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenues | 10823677000 | 10823677000 | 10515069000 | 10515069000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 190934000 | 190934000 | 206283000 | 206283000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R159.htm | Segment Reporting - Reconciliation of Reportable Segment Information (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R159.htm 'Segment Reporting - Reconciliation of Reportable Segment Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Interest expense | 3479926000 | 3479926000 | 3480266000 | 3480266000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Earnings from continuing operations before income taxes | 870989000 | 870989000 | 1005546000 | 1005546000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 184570000 | 184570000 | 293194000 | 293194000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| net_income | mapped | us-gaap:ProfitLoss | R5.htm | Net earnings | 682045000 | 682045000 | 716019000 | 716019000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 2.93 | 2.93 | 3.08 | 3.08 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 2.83 | 2.83 | 2.99 | 2.99 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 215096000 | 215096000 | 217079000 | 217079000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 222746000 | 222746000 | 223650000 | 223650000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R5.htm period ..2025-11-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 14043889000 | 14043889000 | 12153414000 | 12153414000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R3.htm period ..2025-11-30 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1837570000 | 1837570000 | 1827938000 | 1827938000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R3.htm period ..2025-11-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 76012347000 | 76012347000 | 64360309000 | 64360309000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R3.htm period ..2025-11-30 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1497 tags across all 170 R pages, face and notes) of 0000096223-26-000009; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 65369738000 | 65369738000 | 54134916000 | 54134916000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R3.htm period ..2025-11-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Jefferies Financial Group Inc. shareholders' equity | 10574696000 | 10574696000 | 10156772000 | 10156772000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R3.htm period ..2025-11-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | R11.htm | Net cash used in operating activities from continuing operations | -1495143000 | -1495143000 | -140466000 | -140466000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R11.htm | Net cash (used in) provided by investing activities from continuing operations | -298806000 | -298806000 | 210313000 | 210313000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations | R11.htm | Net cash provided by financing activities from continuing operations | 3591923000 | 3591923000 | 3519897000 | 3519897000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R11.htm | Net payments on premises and equipment | -207467000 | 207467000 | -250584000 | 250584000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| depreciation_and_amortization | mapped | jef:DepreciationAndOtherAmortization | R11.htm | Depreciation and amortization | 201906000 |  | 197850000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R11.htm | Share-based compensation | 88227000 | 88227000 | 63119000 | 63119000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R11.htm | Dividends paid to common and preferred shareholders | -374130000 | 374130000 | -302964000 | 302964000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R11.htm | Purchase of common shares for treasury | -58515000 | 58515000 | -44312000 | 44312000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R11.htm | Interest | 3478237000 | 3478237000 | 3440878000 | 3440878000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R11.htm | Income taxes, net | 291970000 | 291970000 | 257503000 | 257503000 | Y | FILING-CHECKED | accn 0000096223-26-000009 R11.htm period ..2025-11-30 |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Long-term debt (includes $3,734,843 and $2,351,346 at fair value) | 15895891000 | 15895891000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common shares, outstanding after deducting shares held in treasury (in shares) | 206296167 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-11-30; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Total revenues' on us-gaap:Revenues = 11683927000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 7677233000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000096223-16-000049 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 111412000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 356536000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 109947000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Net income attributable to Leucadia National Corporation common shareholders' on us-gaap:NetIncomeLoss = 279587000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Net income (USD per share)' on us-gaap:EarningsPerShareBasic = 0.74 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000096223-16-000049 R4.htm prints 'Net income (USD per share)' on us-gaap:EarningsPerShareDiluted = 0.74 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000096223-16-000049 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000096223-16-000049 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000096223-16-000049 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3638648000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000096223-16-000049 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0000096223-16-000049 R2.htm prints 'Total' on us-gaap:Assets = 46339812000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000096223-16-000049 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 35557289000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000096223-16-000049 R2.htm prints 'Total Leucadia National Corporation shareholders’ equity' on us-gaap:StockholdersEquity = 10401211000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Net cash provided by (used for) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = -761755000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Net cash provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 781165000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Net cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -651983000 (FILING-CHECKED)
- capex: FY2015 10-K 0000096223-16-000049 R8.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Depreciation and amortization of property, equipment and leasehold improvements' on luk:DepreciationAndAmortizationOfPropertyEquipmentAndLeaseholdImprovements = 164067000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 74087000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -92550000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Purchase of common shares for treasury' on us-gaap:PaymentsForRepurchaseOfCommonStock = -125754000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Interest' on us-gaap:InterestPaidNet = 980266000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000096223-16-000049 R8.htm prints 'Income tax payments, net' on us-gaap:IncomeTaxesPaidNet = 510000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000096223-18-000009 R4.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 7045007000 (FILING-CHECKED)
- cfo: era 10-K 0000096223-18-000009 R8.htm prints 'Net cash provided by (used for) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1072832000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000096223-18-000009 R8.htm prints 'Net cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 434801000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0000096223-18-000009 R8.htm prints 'Depreciation and amortization of property, equipment and leasehold improvements' on luk:DepreciationAndAmortizationOfPropertyEquipmentAndLeaseholdImprovements = 146179000 (FILING-CHECKED)
- interest_expense: era 10-K 0000096223-24-000006 R6.htm prints 'Interest expense' on us-gaap:InterestExpense = 2740982000 (FILING-CHECKED)
- cfo: era 10-K 0000096223-24-000006 R10.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = -1933626000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0000096223-24-000006 R10.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1060124000 (FILING-CHECKED)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (jef:DepreciationAndOtherAmortization)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | NOTE | agree | value 845500000 read off its own R page (no companyfacts fact to compare) |
| interest_expense | mapped-sample | agree | page value 3479926000 vs printed 3479926000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_investing | mapped-sample | agree | page value -298806000 vs printed -298806000 |
| cash_paid_for_income_taxes | mapped-sample | agree | page value 291970000 vs printed 291970000 |
| total_debt | component sum | agree | page value 15897190000 vs printed 15897190000 |
| shares_outstanding | component sum | agree | page value 206296167 vs printed 206296167 |
