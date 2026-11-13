# VRSN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001014473-26-000006 (CIK 0001014473, filed 2026-02-05): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001014473-16-000086 (CIK 0001014473, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R6.htm
- 10-K 0001014473-24-000006 (CIK 0001014473, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001014473-22-000007 (CIK 0001014473, era filing): COVER R1.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001014473.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Revenues | 1656600000 | 1656600000 | 1557400000 |  | Y | FILING-CHECKED | face R5 (combined income / comprehensive income statement) / check: hand R5.htm corrected: Face income statement R5 'Consolidated Statements Of Comprehensive Income' prints 'Revenues' 1,656.6 / 1,557.4; machine used segment note R54. |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenues | 196300000 | 196300000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R5.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation) |
| gross_profit | not_presented |  |  |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (618 tags across all 71 R pages, face and notes) of 0001014473-26-000006; no face row matched / check: hand R5.htm agree |
| operating_expenses | component sum | us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | R&D + SG&A | 339300000 |  | 307800000 |  |  | FILING-CHECKED | every face line between cost of revenues and operating income; segment-note OperatingExpenses (535.6) includes COGS / check: hand R5.htm corrected: 'Total costs and expenses' 535.6 includes cost of revenues 196.3. Non-COGS face lines R&D 103.6 + SG&A 235.7 = 339.3 = revenues 1,656.6 - COGS 196.3 - OI 1,121.0; FY1 96.7 + 211.1 = 307.8 ties. |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Consolidated Statements Of Comprehensive Income | 235700000 | 235700000 | 211100000 |  | Y | FILING-CHECKED | not on the face statement; shown in R5.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R5.htm corrected: Face R5 'Selling, General and Administrative Expense' 235.7 / 211.1; printed values blank and stmt not IS. |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 103600000 | 103600000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R5.htm 'Consolidated Statements Of Comprehensive Income' (MetaLinks.json presentation) |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1121000000 | 1121000000 | 1058200000 |  | Y | FILING-CHECKED | face R5 / check: hand R5.htm corrected: Face R5 'Operating income' 1,121.0 / 1,058.2. |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Interest expense | -77000000 | 77000000 | -75300000 |  | Y (sign differs: printed in parentheses) | FILING-CHECKED | face R5 / check: hand R5.htm corrected: Face R5 'Interest expense' (77.0) / (75.3), gross. |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income from continuing operations before income taxes | 1068500000 | 1068500000 | 1021900000 |  | Y | FILING-CHECKED | face R5 / check: hand R5.htm corrected: Face R5 'Income from Continuing Operations before Income Taxes' 1,068.5; FY1 1,021.9 (= OI 1,058.2 - 75.3 + 39.0 = NI 785.7 + tax 236.2). |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -242800000 | 242800000 | -236200000 |  | Y (sign differs: printed in parentheses) | FILING-CHECKED | face R5 / check: hand R5.htm corrected: Face R5 'Income tax expense' (242.8) / (236.2). |
| net_income | mapped | us-gaap:ProfitLoss | R5.htm | Net income | 825700000 | 825700000 | 785700000 |  | Y | FILING-CHECKED | face R5; ProfitLoss with no NCI = parent net income / check: hand R5.htm corrected: Face R5 'Net income' 825.7 / 785.7 tagged ProfitLoss; VeriSign has no noncontrolling interest line, so ProfitLoss equals net income to the parent. |
| basic_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerBasicShare | R5.htm | Earnings per Share, Basic | 8.83 |  | 8.01 |  |  | FILING-CHECKED | continuing-ops EPS tag on the only EPS line; no discontinued operations / check: hand R5.htm corrected: Face R5 prints 'Earnings per Share, Basic' 8.83 / 8.01 under IncomeLossFromContinuingOperationsPerBasicShare; no discontinued operations, so it is total basic EPS. |
| diluted_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare | R5.htm | Earnings per Share, Diluted | 8.81 |  | 8.00 |  |  | FILING-CHECKED | continuing-ops EPS tag on the only EPS line; no discontinued operations / check: hand R5.htm corrected: Face R5 'Earnings per Share, Diluted' 8.81 / 8.00 under IncomeLossFromContinuingOperationsPerDilutedShare; no discontinued operations. |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic | 93500000 | 93500000 | 98100000 |  | Y | FILING-CHECKED | face R5 / check: hand R5.htm corrected: Face R5 'Basic' 93.5 / 98.1 million (also R52). |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted | 93800000 | 93800000 | 98200000 |  | Y | FILING-CHECKED | face R5 / check: hand R5.htm corrected: Face R5 'Diluted' 93.8 / 98.2 million (also R52). |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 307900000 | 307900000 | 206700000 | 206700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R39.htm | Other Balance Sheet Items (Other Current Assets) (Details) | 7700000 | 7700000 | 5600000 |  | Y | FILING-CHECKED | not on the face statement; shown in R39.htm 'Other Balance Sheet Items (Other Current Assets) (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R39.htm corrected: Not on R3 (inside 'Other' current assets); note R39 prints AccountsReceivableNetCurrent 7.7 / 5.6; printed values were blank. |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (618 tags across all 71 R pages, face and notes) of 0001014473-26-000006; no face row matched / check: hand R3.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 652500000 | 652500000 | 663800000 | 663800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 213700000 | 213700000 | 224500000 | 224500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 52500000 | 52500000 | 52500000 | 52500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1325900000 | 1325900000 | 1406500000 | 1406500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued liabilities | 298000000 | 298000000 | 257800000 | 257800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1333100000 | 1333100000 | 1531100000 | 1531100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3480100000 | 3480100000 | 3364400000 | 3364400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' deficit | -2154200000 | -2154200000 | -1957900000 | -1957900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Cash Provided by (Used in) Operating Activity, Including Discontinued Operation | 1091100000 | 1091100000 | 902600000 | 902600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | 109100000 | 109100000 | 286300000 | 286300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -1102800000 | -1102800000 | -1221500000 | -1221500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -22800000 | 22800000 | -28100000 | 28100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation of property and equipment | 31200000 | 31200000 | 36900000 | 36900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 69700000 | 69700000 | 61100000 | 61100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Payments of Dividends | -215200000 | 215200000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001014473-26-000006 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchases of common stock | -881600000 | 881600000 | -1225600000 | 1225600000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001014473-26-000006 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R47.htm | Debt And Interest Expense (Senior Notes) (Narrative) (Details) | 78700000 | 78700000 | 72800000 |  | Y | FILING-CHECKED | not on the face statement; shown in R47.htm 'Debt And Interest Expense (Senior Notes) (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R47.htm corrected: Debt note R47 'Cash paid for interest, net of capitalized interest' InterestPaidNet 78.7 / 72.8; printed values were blank. |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R63.htm | Income Taxes (Narrative) (Details) | 202400000 | 202400000 | 230500000 |  | Y | FILING-CHECKED | not on the face statement; shown in R63.htm 'Income Taxes (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R63.htm corrected: Tax note R63 'Income Taxes Paid, Net' 202.4 / 230.5; printed values were blank. |
| total_debt | component sum | us-gaap:SeniorNotesCurrent+us-gaap:SeniorLongTermNotes | R3.htm | Senior Notes, Current + Senior Notes, Noncurrent | 1788200000 |  | 1792300000 |  |  | FILING-CHECKED | face senior notes lines; ties to R46 SeniorNotes 1,788.2 / 1,792.3 / check: hand R3.htm corrected: Face R3 prints 'Senior Notes, Current' 0.0 / 299.8 and 'Senior Notes, Noncurrent' 1,788.2 / 1,492.5 = 1,788.2 / 1,792.3 (R46 SeniorNotes total agrees). No finance lease tags in filing. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, outstanding shares | 91900000 | 91900000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0001014473-16-000086 statement not identified (auto)
- cost_of_revenue: 10-K 0001014473-16-000086 statement not identified (auto)
- operating_expenses: 10-K 0001014473-16-000086 statement not identified (auto)
- sga_expense: 10-K 0001014473-16-000086 statement not identified (auto)
- research_and_development: 10-K 0001014473-16-000086 statement not identified (auto)
- operating_income: 10-K 0001014473-16-000086 statement not identified (auto)
- interest_expense: 10-K 0001014473-16-000086 statement not identified (auto)
- income_before_tax: 10-K 0001014473-16-000086 statement not identified (auto)
- income_tax_expense: 10-K 0001014473-16-000086 statement not identified (auto)
- net_income: 10-K 0001014473-16-000086 statement not identified (auto)
- weighted_basic_shares: 10-K 0001014473-16-000086 statement not identified (auto)
- weighted_diluted_shares: 10-K 0001014473-16-000086 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 228659000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Accounts receivable, net' on us-gaap:AccountsReceivableNetCurrent = 12638000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1967924000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 295570000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 52527000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Total assets' on us-gaap:Assets = 2357737000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 188171000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1502980000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 3428184000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001014473-16-000086 R2.htm prints 'Total stockholders' deficit' on us-gaap:StockholdersEquity = -1070447000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 651482000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -496899000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -117778000 (FILING-CHECKED)
- capex: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -40656000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Depreciation of property and equipment and amortization of other intangible asse' on us-gaap:DepreciationAndAmortization = 61491000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 46075000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001014473-16-000086 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -643169000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Cash paid for interest, net of capitalized interest' on us-gaap:InterestPaidNet = 99473000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001014473-16-000086 R6.htm prints 'Cash paid for income taxes, net of refunds received' on us-gaap:IncomeTaxesPaidNet = 39723000 (FILING-CHECKED)
- operating_expenses: 10-K 0001014473-24-000006 statement not identified (auto)
- sga_expense: 10-K 0001014473-22-000007 statement not identified (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 19 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 16.
- Random mapped sample: 2 rows, 1 disagreements (50.0%).
