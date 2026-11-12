# AMG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008665 (CIK 0001004434, filed 2026-02-17): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001004434-16-000035 (CIK 0001004434, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001004434-24-000010 (CIK 0001004434, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001004434-21-000014 (CIK 0001004434, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0001004434.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Consolidated revenue | 2074400000 | 2074400000 | 2040900000 | 2040900000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total consolidated expenses | 1805400000 | 1805400000 | 1507800000 | 1507800000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative | 408600000 | 408600000 | 376500000 | 376500000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R3.htm | Interest expense | 136500000 | 136500000 | 1.333e+08 | 133300000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 1186300000 | 1186300000 | 923200000 | 923200000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | 282300000 | 282300000 | 182600000 | 182600000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (controlling interest) | 716600000 | 716600000 | 511600000 | 511600000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Earnings per share (basic) (in dollars per share) | 25.18 | 25.18 | 16.45 | 16.45 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Earnings per share (diluted) (in dollars per share) | 22.74 | 22.74 | 15.13 | 15.13 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Average shares outstanding (basic) (in shares) | 28500000 | 28500000 | 31100000 | 31100000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Average shares outstanding (diluted) (in shares) | 33000000 | 33000000 | 36100000 | 36100000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 586000000 | 586000000 | 950000000 | 950000000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R5.htm | Receivables | 496200000 | 496200000 | 409700000 | 409700000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| current_assets | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Fixed assets (net) | 54400000 | 54400000 | 57600000 | 57600000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2531200000 | 2531200000 | 2504900000 | 2504900000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 9207400000 | 9207400000 | 8830900000 | 8830900000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| current_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 4785300000 | 4785300000 | 4182200000 | 4182200000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity | 3238400000 | 3238400000 | 3345300000 | 3345300000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Cash flow from operating activities | 973200000 | 973200000 | 932100000 | 932100000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Cash flow from (used in) investing activities | -206100000 | -206100000 | 379100000 | 379100000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Cash flow used in financing activities | -1148700000 | -1148700000 | -1175900000 | -1175900000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of fixed assets | -6100000 | 6100000 | -3400000 | 3400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | amg:DepreciationAndOtherAmortization | R9.htm | Depreciation and other amortization | 10400000 |  | 13400000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| sbc | mapped | amg:ShareBasedCompensationAndAffiliateEquityExpense | R9.htm | Share-based compensation and Affiliate equity expense | 202800000 |  | 111600000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid on common stock | -1000000 | 1000000 | -1400000 | 1400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchases of common stock, net | -706300000 | 706300000 | -709800000 | 709800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 137900000 | 137900000 | 138200000 | 138200000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid, net | 110700000 | 110700000 | 142500000 | 142500000 | Y | FILING-CHECKED | accn 0001628280-26-008665 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebt | R5.htm | Debt | 2691300000 | 2691300000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (947 tags across all 107 R pages, face and notes) of 0001628280-26-008665; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Revenue' on us-gaap:AssetManagementFees1 = 2484500000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 1649500000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 443800000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 88900000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1090600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 2.569e+08 (FILING-CHECKED)
- net_income: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Net income (controlling interest)' on us-gaap:NetIncomeLoss = 516000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Earnings per share - basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 9.49 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Earnings per share - diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 9.28 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Average shares outstanding - basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 54300000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001004434-16-000035 R2.htm prints 'Average shares outstanding - diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 57200000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 563800000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Receivables' on us-gaap:AccountsReceivableNet = 391200000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 114100000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 2668400000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Total assets' on us-gaap:Assets = 7784800000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 3403200000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001004434-16-000035 R4.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 2837100000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Cash flow from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1204800000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Cash flow used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -324500000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Cash flow used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -854100000 (FILING-CHECKED)
- capex: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Purchase of fixed assets' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -38200000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Depreciation and other amortization' on amg:DepreciationAndOtherAmortization = 18800000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Share-based compensation and Affiliate equity expense' on us-gaap:ShareBasedCompensation = 102700000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001004434-16-000035 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -413700000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 76400000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001004434-16-000035 R7.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 89600000 (FILING-CHECKED)
- interest_expense: era 10-K 0001004434-24-000010 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = 123800000 (FILING-CHECKED)
- sbc: era 10-K 0001004434-21-000014 R8.htm prints 'Share-based compensation and Affiliate equity expense' on amg:SharebasedCompensationandAffiliateEquityExpense = 119200000 (FILING-CHECKED)

## Mismatches (printed vs API)
- depreciation_and_amortization: API missing (amg:DepreciationAndOtherAmortization)
- sbc: API missing (amg:ShareBasedCompensationAndAffiliateEquityExpense)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | mapped-sample | agree | page value 1805400000 vs printed 1805400000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| weighted_diluted_shares | mapped-sample | agree | page value 33000000 vs printed 33000000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | mapped-sample | agree | page value 10400000 vs printed 10400000 |
| total_debt | component sum | agree | page value 2691300000 vs printed 2691300000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
