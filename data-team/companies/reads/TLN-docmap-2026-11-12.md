# TLN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001622536-26-000017 (CIK 0001622536, filed 2026-02-26): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001622536-16-000111 (CIK 0001622536, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0001628280-25-008786 (CIK 0001622536, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001622536-26-000017 (CIK 0001622536, era filing): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0001622536.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Operating revenues | 2581000000 | 2581000000 | 2115000000 | 2115000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1295 tags across all 140 R pages, face and notes) of 0001622536-26-000017; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:OperatingExpenses 'Operating Expenses / Operating Expenses / Generally recurrin' R138 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1295 tags across all 140 R pages, face and notes) of 0001622536-26-000017; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R138.htm | Operating Expenses | 0 |  |  |  | API missing | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R138.htm 'Schedule I - Condensed Financial Information of Registrant - Condensed Unconsoli' (MetaLinks.json presentation) |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | General and administrative | -624000000 | 624000000 | -163000000 | 163000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1295 tags across all 140 R pages, face and notes) of 0001622536-26-000017; label search over every tag in the filing (custom included) found no candidate |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating Income (Loss) | -90000000 | -90000000 | 226000000 | 226000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestAndDebtExpense | R3.htm | Interest expense and other finance charges (Note 10) | -302000000 | 302000000 | -238000000 | 238000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (Loss) Before Income Taxes | -166000000 | -166000000 | 1111000000 | 1111000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax benefit (expense) (Note 4) | -53000000 | 53000000 | -98000000 | 98000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income (Loss) Attributable to Stockholders (Successor) / Member (Predecessor) | -219000000 | -219000000 | 998000000 | 998000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net Income (Loss) Attributable to Stockholders - Basic (in dollars per share) | -4.79 | -4.79 | 18.4 | 18.4 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net Income (Loss) Attributable to Stockholders - Diluted (in dollars per share) | -4.79 | -4.79 | 17.67 | 17.67 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Weighted-Average Number of Common Shares Outstanding - Basic (in shares) | 45692000 | 45692000 | 54254000 | 54254000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Weighted-Average Number of Common Shares Outstanding - Diluted (in shares) | 45692000 | 45692000 | 56486000 | 56486000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 689000000 | 689000000 | 328000000 | 328000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndOtherReceivablesNetCurrent | R6.htm | Accounts receivable (Note 3) | 196000000 | 196000000 | 123000000 | 123000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventory, net (Note 5) | 278000000 | 278000000 | 302000000 | 302000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 1349000000 | 1349000000 | 1040000000 | 1040000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment, net (Note 7) | 7546000000 | 7546000000 | 3154000000 | 3154000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| goodwill | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1295 tags across all 140 R pages, face and notes) of 0001622536-26-000017; HAND REVIEW: 3 label candidate(s) incl. custom tags: us-gaap:BusinessCombinationRecognizedIdentifiableAssetsAcquiredAndLiabilitiesAssumedNet 'Aggregate purchase price / Business Combination, Recognized ' R120; us-gaap:DisposalGroupIncludingDiscontinuedOperationIntangibleAssets 'Contract intangible assets and lease right-of-use assets der' R80; us-gaap:OtherAssetImpairmentCharges 'Non-cash impairments and other charges / Other Asset Impairm' R128 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total Assets | 10905000000 | 10905000000 | 6106000000 | 6106000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndOtherAccruedLiabilitiesCurrent | R6.htm | Accounts payable and other accrued liabilities | 281000000 | 281000000 | 266000000 | 266000000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1050000000 | 1050000000 | 455000000 | 455000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total Liabilities | 9812000000 | 9812000000 | 4719000000 | 4719000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total Stockholders' Equity | 1093000000 | 1093000000 | 1387000000 | 1387000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by (used in) operating activities | 704000000 | 704000000 | 256000000 | 256000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | -4003000000 | -4003000000 | 1171000000 | 1171000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 3686000000 | 3686000000 | -1963000000 | -1963000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Property, plant and equipment expenditures (Note 7) | -98000000 | 98000000 | -85000000 | 85000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R8.htm | Depreciation, amortization and accretion (Note 16) | 279000000 | 279000000 | 285000000 | 285000000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation (Note 13) | 526000000 | 526000000 | 33000000 | 33000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1295 tags across all 140 R pages, face and notes) of 0001622536-26-000017; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:MinorityInterestDecreaseFromDistributionsToNoncontrollingInterestHolders 'Cash distributions/ Non-cash distributions / Noncontrolling ' R9; us-gaap:PaymentsToMinorityShareholders 'Repurchase of noncontrolling interest / Repurchase of noncon' R8,R112 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Share repurchases (Note 15) | -103000000 | 103000000 | -1958000000 | 1958000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001622536-26-000017 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R116.htm | Interest and other finance charges, net of capitalized interest | 233000000 | 233000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R116.htm 'Supplemental Cash Flow Information - Schedule of Supplemental Consolidated State' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R70.htm | Total | 71000000 | 71000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R70.htm 'Income Taxes - Schedule of Income Taxes Paid, Net of Refunds (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Long-term debt, due within one year (Notes 10 and 11) + Long-term debt (Notes 10 and 11) | 6811000000 | 6811000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Shares outstanding (in shares) | 45687828 | 45687828 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Total Operating Revenues' on us-gaap:RegulatedAndUnregulatedOperatingRevenue = 4481000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Total Operating Expenses' on us-gaap:UtilitiesOperatingExpense = 4520000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001622536-16-000111 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Operating Income (Loss)' on us-gaap:OperatingIncomeLoss = -39000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Interest Expense' on us-gaap:InterestExpense = 211000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Income (Loss) from Continuing Operations Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -368000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Income Taxes' on us-gaap:IncomeTaxExpenseBenefit = -27000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Net Income (Loss) Attributable to Member' on us-gaap:NetIncomeLoss = -341000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Net Income (Loss) (in dollars per share)' on us-gaap:EarningsPerShareBasic = -3.1 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Net Income (Loss) (in dollars per share)' on us-gaap:EarningsPerShareDiluted = -3.1 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 109898000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001622536-16-000111 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 109898000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 141000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Customer' on us-gaap:AccountsReceivableNetCurrent = 205000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Fuel, materials and supplies' on us-gaap:InventoryNet = 508000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 2762000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Total Property, Plant and Equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 8587000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Total Assets' on us-gaap:Assets = 12826000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 291000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 2088000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001622536-16-000111 R6.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001622536-16-000111 R6.htm prints 'Total Equity' on us-gaap:StockholdersEquity = 4303000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001622536-16-000111 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 768000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001622536-16-000111 R5.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -915000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001622536-16-000111 R5.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -64000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001622536-16-000111 R5.htm prints 'Expenditures for property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -451000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001622536-16-000111 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001622536-16-000111 R5.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001622536-16-000111 R5.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001622536-16-000111 R5.htm prints 'Interest - net of amount capitalized' on us-gaap:InterestPaidNet = 169000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001622536-16-000111 R5.htm prints 'Income taxes - net' on us-gaap:IncomeTaxesPaidNet = 5000000 (FILING-CHECKED)
- net_income: era 10-K 0001628280-25-008786 R3.htm prints 'Net Income (Loss) Attributable to Stockholders (Successor) / Member (Predecessor' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 998000000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001622536-26-000017 R6.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 689000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:OperatingExpenses)

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 13 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:TLN); disagree on the mapped sample: 0/3
- accounts_receivable: agree (R6 'Accounts receivable (Note 3)' AccountsAndOtherReceivablesNetCurrent is the single receivables line)
- cash_paid_for_income_taxes: agree (R70 IncomeTaxesPaidNet total 71)
- cash_paid_for_interest: agree (R116 'Interest and other finance charges, net of capitalized interest' InterestPaidNet 233 (DQC_0065: net of capitalized))
- cost_of_revenue: agree (R3 prints no cost-of-revenue total; custom tln:EnergyExpenses 'Energy Expenses' (fuel + nuclear fuel amortization + derivatives) is a perimeter question for the Tag Expert; the only us-gaap lead is R138 (parent-only Schedule I))
- depreciation_and_amortization: agree (R8 'Depreciation, amortization and accretion' includes accretion: combined)
- diluted_eps: agree (R3 diluted EPS -4.79)
- dividends_paid: agree (R8 prints no dividend line; leads are NCI distributions and the NCI repurchase (not common dividends))
- goodwill: agree (R6 prints no goodwill line; leads are business-combination and impairment facts (R120, R80))
- gross_profit: agree (no gross profit line on R3)
- interest_expense: agree (R3 'Interest expense and other finance charges' InterestAndDebtExpense 302: gross charge)
- operating_expenses: disagree (R138 is Schedule I (parent-only condensed statements), not the consolidated face; R3 prints an 'Operating Expenses' header (OperatingExpensesAbstract) with no total and there is no gross profit line: not_presented)
- research_and_development: agree (no R&D line on R3; none in MetaLinks)
- total_debt: agree (R6 29 + 6,782 = 6,811 (); no other borrowing line)
