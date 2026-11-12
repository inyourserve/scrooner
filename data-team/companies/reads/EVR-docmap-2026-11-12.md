# EVR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-010273 (CIK 0001360901, filed 2026-02-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001360901-16-000017 (CIK 0001360901, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001360901-19-000006 (CIK 0001360901, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001360901-25-000005 (CIK 0001360901, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001360901.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total Revenues | 3880084000 | 3880084000 | 2996361000 | 2996361000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1098 tags across all 119 R pages, face and notes) of 0001628280-26-010273; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1098 tags across all 119 R pages, face and notes) of 0001628280-26-010273; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total Expenses | 3065878000 | 3065878000 | 2452679000 | 2452679000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1098 tags across all 119 R pages, face and notes) of 0001628280-26-010273; no face row matched |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1098 tags across all 119 R pages, face and notes) of 0001628280-26-010273; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R117.htm | Evercore Inc. (Parent Company Only) Financial Statements - Condensed Statements of Operations (Parent Company Only) (Det |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R117.htm 'Evercore Inc. (Parent Company Only) Financial Statements - Condensed Statements ' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest Expense | 24264000 | 24264000 | 16768000 | 16768000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income Before Income Taxes | 793814000 | 793814000 | 533145000 | 533145000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for Income Taxes | 153107000 | 153107000 | 115408000 | 115408000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income Attributable to Evercore Inc. | 591922000 | 591922000 | 378279000 | 378279000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 15.29 | 15.29 | 9.86 | 9.86 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 14.05 | 14.05 | 9.08 | 9.08 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 38712000 | 38712000 | 38365000 | 38365000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 42131000 | 42131000 | 41646000 | 41646000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and Cash Equivalents | 1426020000 | 1426020000 | 873045000 | 873045000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1098 tags across all 119 R pages, face and notes) of 0001628280-26-010273; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1098 tags across all 119 R pages, face and notes) of 0001628280-26-010273; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total Current Assets | 3858241000 | 3858241000 | 2987901000 | 2987901000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Furniture, Equipment and Leasehold Improvements (net of accumulated depreciation and amortization of $170,272 and $151,4 | 190064000 | 190064000 | 144756000 | 144756000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 230783000 | 230783000 | 124452000 | 124452000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 5358097000 | 5358097000 | 4173971000 | 4173971000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts Payable and Accrued Expenses | 44562000 | 44562000 | 29041000 | 29041000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total Current Liabilities | 1783421000 | 1783421000 | 1229801000 | 1229801000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 3038231000 | 3038231000 | 2232163000 | 2232163000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Evercore Inc. Stockholders' Equity | 2031576000 | 2031576000 | 1707642000 | 1707642000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net Cash Provided by Operating Activities | 1256464000 | 1256464000 | 988151000 | 988151000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net Cash Provided by (Used in) Investing Activities | -98325000 | -98325000 | -67431000 | -67431000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net Cash Provided by (Used in) Financing Activities | -635623000 | -635623000 | -628552000 | -628552000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R8.htm | Purchase of Furniture, Equipment and Leasehold Improvements | -74002000 | 74002000 | -30101000 | 30101000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R8.htm | Depreciation, Amortization and Accretion, net | 10537000 | 10537000 | -387000 | -387000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Equity-Based and Other Deferred Compensation | 675100000 | 675100000 | 569734000 | 569734000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends | -144410000 | 144410000 | -135832000 | 135832000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | evr:PaymentsForRepurchaseOfCommonStockAndPartnershipUnits | R8.htm | Purchase of Treasury Stock and Noncontrolling Interests | -661780000 |  | -450530000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Payments for Interest | 19896000 | 19896000 | 16214000 | 16214000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Payments for Income Taxes | 117312000 | 117312000 | 98201000 | 98201000 | Y | FILING-CHECKED | accn 0001628280-26-010273 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R81.htm | Notes Payable - Schedule of Debt (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R81.htm 'Notes Payable - Schedule of Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common Stock, Shares, Outstanding (in shares) | 38522835 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Total Revenues' on us-gaap:Revenues = 1240248000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Total Expenses' on us-gaap:OperatingExpenses = 1094603000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001360901-16-000017 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Interest Expense' on us-gaap:InterestExpense = 16975000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 134720000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Provision for Income Taxes' on us-gaap:IncomeTaxExpenseBenefit = 77030000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Net Income Attributable to Evercore Partners Inc.' on us-gaap:NetIncomeLoss = 42863000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Net Income Per Share Attributable to Evercore Partners Inc. Common Shareholders ' on us-gaap:EarningsPerShareBasic = 1.15 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Net Income Per Share Attributable to Evercore Partners Inc. Common Shareholders ' on us-gaap:EarningsPerShareDiluted = 0.98 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 37161000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001360901-16-000017 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 43699000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 448764000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 749464000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Furniture, Equipment and Leasehold Improvements (net of accumulated depreciation' on us-gaap:PropertyPlantAndEquipmentNet = 47980000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 166461000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Total Assets' on us-gaap:Assets = 1479171000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Accounts Payable and Accrued Expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 43878000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 408049000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 771955000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001360901-16-000017 R2.htm prints 'Total Evercore Partners Inc. Stockholders' Equity' on us-gaap:StockholdersEquity = 504552000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 356851000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Net Cash Provided by (Used in) Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -26117000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Net Cash Provided by (Used in) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -223803000 (FILING-CHECKED)
- capex: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Purchase of Furniture, Equipment and Leasehold Improvements' on us-gaap:PaymentsToAcquireProductiveAssets = -16189000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Depreciation, Amortization and Accretion' on us-gaap:DepreciationAmortizationAndAccretionNet = 29636000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001360901-16-000017 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Dividends - Class A Stockholders' on us-gaap:PaymentsOfDividendsCommonStock = -46132000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Securities Sold Under Agreements to Repurchase' on us-gaap:ProceedsFromPaymentsForInSecuritiesSoldUnderAgreementsToRepurchase = -50803000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Payments for Interest' on us-gaap:InterestPaid = 16035000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001360901-16-000017 R7.htm prints 'Payments for Income Taxes' on us-gaap:IncomeTaxesPaid = 47820000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001360901-19-000006 R7.htm prints 'Payments for Interest' on us-gaap:InterestPaid = 17818000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001360901-25-000005 R8.htm prints 'Payments for Income Taxes' on us-gaap:IncomeTaxesPaid = 98201000 (FILING-CHECKED)

## Mismatches (printed vs API)
- share_buybacks: API missing (evr:PaymentsForRepurchaseOfCommonStockAndPartnershipUnits)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | NOTE | agree | value 0 read off its own R page (no companyfacts fact to compare) |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | mapped-sample | agree | page value 1783421000 vs printed 1783421000 |
| depreciation_and_amortization | combined | agree | page value 10537000 vs printed 10537000 |
| dividends_paid | mapped-sample | agree | page value -144410000 vs printed -144410000 |
| cash_paid_for_interest | mapped-sample | agree | page value 19896000 vs printed 19896000 |
| total_debt | NOTE | agree | value 47981000 read off its own R page (no companyfacts fact to compare) |
| shares_outstanding | component sum | agree | page value 38522835 vs printed 38522835 |
