# KKR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001404912-26-000007 (CIK 0001404912, filed 2026-02-27): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R6.htm, CI R8.htm, CF R11.htm
- 10-K 0001404912-16-000009 (CIK 0001404912, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001404912-24-000005 (CIK 0001404912, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R6.htm, CI R8.htm, CF R11.htm
- 10-K 0001404912-21-000008 (CIK 0001404912, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001404912.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R6.htm | Total Revenues | 19464307000 | 19464307000 | 21878698000 | 21878698000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| gross_profit | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R6.htm | Total Expenses | 19012315000 | 19012315000 | 20985860000 | 20985860000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| research_and_development | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R171.htm | SEGMENT REPORTING - Information Regarding Segment Results (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R171.htm 'SEGMENT REPORTING - Information Regarding Segment Results (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R6.htm | Interest Expense | -2776946000 | 2776946000 | -3034145000 | 3034145000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R6.htm | Income (Loss) Before Taxes | 7099160000 | 7099160000 | 5860433000 | 5860433000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R6.htm | Income Tax Expense (Benefit) | 953748000 | 953748000 | 954396000 | 954396000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R6.htm | Net Income (Loss) Attributable to KKR & Co. Inc. | 2370463000 | 2370463000 | 3076245000 | 3076245000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R6.htm | Basic (in dollars per share) | 2.51 |  | 3.47 |  | API missing | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R6.htm | Diluted (in dollars per share) | 2.34 |  | 3.28 |  | API missing | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R6.htm | Basic (in shares) | 890342060 |  | 887021433 |  | API missing | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R6.htm | Diluted (in shares) | 955756926 |  | 938904600 |  | API missing | FILING-CHECKED | accn 0001404912-26-000007 R6.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and Cash Equivalents | 9380874000 |  | 8535048000 |  | API missing | FILING-CHECKED | accn 0001404912-26-000007 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R126.htm | OTHER ASSETS AND ACCRUED EXPENSES AND OTHER LIABILITIES - Other Assets (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R126.htm 'OTHER ASSETS AND ACCRUED EXPENSES AND OTHER LIABILITIES - Other Assets (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| goodwill | mapped | us-gaap:Goodwill | R126.htm | OTHER ASSETS AND ACCRUED EXPENSES AND OTHER LIABILITIES - Other Assets (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R126.htm 'OTHER ASSETS AND ACCRUED EXPENSES AND OTHER LIABILITIES - Other Assets (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 410144072000 | 410144072000 | 360099411000 | 360099411000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 328512161000 | 328512161000 | 298114719000 | 298114719000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total KKR & Co. Inc. Stockholders' Equity | 30902561000 | 30902561000 | 23651568000 | 23651568000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R11.htm | Net Cash Provided (Used) by Operating Activities | 477760000 | 477760000 | 6649878000 | 6649878000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R11.htm | Net Cash Provided (Used) by Investing Activities | -16281797000 | -16281797000 | -19047424000 | -19047424000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R11.htm | Net Cash Provided (Used) by Financing Activities | 17432306000 | 17432306000 | 7076330000 | 7076330000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| capex | not_presented |  | R11.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1908 tags across all 188 R pages, face and notes) of 0001404912-26-000007; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R11.htm | Net Accretion and Amortization | -162529000 | -162529000 | -119315000 | -119315000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R11.htm | Equity-Based Compensation | 722109000 | 722109000 | 746443000 | 746443000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R11.htm | Common Stock Dividends | -649942000 | 649942000 | -612068000 | 612068000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R11.htm | Repurchases of Common Stock | -3362000 | 3362000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R11.htm | Payments for Interest | 2661394000 | 2661394000 | 2937009000 | 2937009000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R11.htm | Payments for Income Taxes, Net of Refunds | 1209216000 | 1209216000 | 781552000 | 781552000 | Y | FILING-CHECKED | accn 0001404912-26-000007 R11.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebt+us-gaap:LongTermDebt | R3.htm | Debt Obligations + Debt Obligations | 52938151000 |  |  |  | API missing | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 891451844 | 891451844 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001404912-16-000009 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Total Expenses' on us-gaap:NoninterestExpense = 1871225000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001404912-16-000009 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Interest Expense' on us-gaap:InterestExpense = -573226000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Income (Loss) Before Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 5341668000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Income Tax / (Benefit)' on us-gaap:IncomeTaxExpenseBenefit = 66636000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Net Income (Loss) Attributable to KKR & Co. L.P.' on us-gaap:NetIncomeLoss = 488482000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Basic (in dollars per unit)' on us-gaap:NetIncomeLossPerOutstandingLimitedPartnershipUnitBasicNetOfTax = 1.09 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001404912-16-000009 R4.htm prints 'Diluted (in dollars per unit)' on us-gaap:NetIncomeLossNetOfTaxPerOutstandingLimitedPartnershipUnitDiluted = 1.01 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001404912-16-000009 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001404912-16-000009 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001404912-16-000009 R2.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1047740000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001404912-16-000009 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001404912-16-000009 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001404912-16-000009 R2.htm prints 'Total Assets' on us-gaap:Assets = 71057759000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001404912-16-000009 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 21590174000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001404912-16-000009 R2.htm read; no row matched (auto)
- cfo: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Net Cash Provided (Used) by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 385404000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Net Cash Provided (Used) by Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -425152000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Net Cash Provided (Used) by Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 169408000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001404912-16-000009 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Equity Based Compensation' on us-gaap:ShareBasedCompensation = 261579000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Distributions to Partners' on us-gaap:PaymentsOfDividends = -706611000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Unit Repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -161929000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Payments for Interest' on us-gaap:InterestPaidNet = 485739000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001404912-16-000009 R7.htm prints 'Payments for Income Taxes' on us-gaap:IncomeTaxesPaidNet = 40468000 (FILING-CHECKED)
- interest_expense: era 10-K 0001404912-24-000005 R6.htm prints 'Interest Expense' on us-gaap:InterestExpense = -2772088000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001404912-21-000008 R4.htm prints 'Income (Loss) Before Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 5726695000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001404912-21-000008 R2.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 5363009000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001404912-21-000008 R8.htm read; no row matched (auto)

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: API missing (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)
- cash_and_equivalents: API missing (us-gaap:CashAndCashEquivalentsAtCarryingValue)
- total_debt: API missing (us-gaap:LongTermDebt+us-gaap:LongTermDebt)

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- sga_expense: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- operating_income: component_in_note us-gaap:OperatingIncomeLoss (R171.htm): 2026-11-12 R171.htm: R171 carries operating income by segment only (no consolidated value); KKR prints no OI line
- accounts_receivable: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- current_assets: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R126.htm): 2026-11-12 R126.htm: decided by R126: 'Fixed Assets, net' 975,498k inside other assets: the full balance
- goodwill: mapped us-gaap:Goodwill (R126.htm): 2026-11-12 R126.htm: decided by R126: 'Goodwill' 519,582k inside other assets: the consolidated balance
- accounts_payable: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- current_liabilities: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- capex: mapped us-gaap:PaymentsToAcquireFurnitureAndFixtures (R11.htm): 2026-11-12 R11.htm: corrected: the CF prints 'Purchases of Fixed Assets' 160,765k on a tag outside the tool's set
- total_debt: component sum us-gaap:LongTermDebt+us-gaap:LongTermDebt (R3.htm): 2026-11-12 R3.htm: agree: R3 'Debt Obligations' in both BS sections (Asset Management and Strategic Holdings 49,117,744 + Insurance 3,820,407): two different lines, not a double count; no finance-lease facts in the filin
- revenue: mapped us-gaap:Revenues (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: IS R6.htm 'Total Revenues' is the revenue line, printed 19464307000 = filing XBRL 19464307000; agrees
- diluted_eps: mapped us-gaap:EarningsPerShareDiluted (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: IS R6.htm 'Diluted (in dollars per share)' is the diluted_eps line, printed 2.34 = filing XBRL ; agrees
- total_liabilities: mapped us-gaap:Liabilities (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total Liabilities' is the total_liabilities line, printed 328512161000 = filing XBRL 328512161000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividendsCommonStock (R11.htm): 2026-11-12 R11.htm: 20% mapped sample: CF R11.htm 'Common Stock Dividends' is the dividends_paid line, printed -649942000 = filing XBRL 649942000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R11.htm): 2026-11-12 R11.htm: 20% mapped sample: CF R11.htm 'Repurchases of Common Stock' is the share_buybacks line, printed -3362000 = filing XBRL 3362000; agrees
