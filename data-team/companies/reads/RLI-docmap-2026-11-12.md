# RLI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001104659-26-018013 (CIK 0000084246, filed 2026-02-20): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001558370-16-003590 (CIK 0000084246, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0000084246-18-000011 (CIK 0000084246, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001564590-22-005648 (CIK 0000084246, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0000084246.json (one call); submissions CIK0000084246.json (SIC 6331).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Consolidated revenue | 1882448000 | 1882448000 | 1770384000 | 1770384000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| cost_of_revenue | OUT |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| gross_profit | OUT |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Insurance operating expenses | 115815000 | 115815000 | 112460000 | 112460000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line; no cost-of-revenue line above it / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| sga_expense | combined | us-gaap:OperatingExpenses | R4.htm | Insurance operating expenses | 115815000 |  |  |  |  | FILING-CHECKED | check: hand / No consolidated SG&A line: SG&A-type cost sits in 'Insurance operating expenses' ($115,815K) and 'General corporate expenses' ($17,028K); the SG&A tag appears only in parent-only Schedule II (R95), which cannot be used. / pages opened: R4, R90, R95, R19, R63, R65 |
| research_and_development | OUT |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Insurer face goes from total expenses to earnings before income taxes; segment pages give segment earnings/underwriting results, not consolidated operating income. / pages opened: R18, R38, R88, R89, R90, R91 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R4.htm | Interest expense on debt | 5358000 | 5358000 | 6331000 | 6331000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Earnings before income taxes | 505981000 | 505981000 | 427551000 | 427551000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | 102644000 | 102644000 | 81772000 | 81772000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net earnings | 403337000 | 403337000 | 345779000 | 345779000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic net earnings per share | 4.39 | 4.39 | 3.78 | 3.78 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted net earnings per share | 4.37 | 4.37 | 3.74 | 3.74 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic | 91829000 | 91829000 | 91529000 | 91529000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted | 92391000 | 92391000 | 92451000 | 92451000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:Cash | R2.htm | Cash | 51565000 | 51565000 | 39790000 | 39790000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | rli:PremiumsAndReinsuranceBalancesReceivable | R2.htm | Premiums and reinsurance balances receivable, net of allowances for uncollectible amounts of $23,673 in 2025 and $22,932 | 212226000 |  | 230534000 |  | API missing | FILING-CHECKED | check: machine-full-filing / company extension tag, matched by printed label / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| inventory | OUT |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| current_assets | OUT |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, at cost, net of accumulated depreciation of $84,459 in 2025 and $76,330 in 2024 | 40733000 | 40733000 | 43172000 | 43172000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R2.htm | Goodwill and intangibles | 53562000 | 53562000 | 53562000 | 53562000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | TOTAL ASSETS | 6161486000 | 6161486000 | 5628802000 | 5628802000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet shows only reinsurance balances payable (an insurance liability, not trade payables); no accounts payable line. / pages opened: R16, R68, R76, R85, R2 |
| current_liabilities | OUT |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | TOTAL LIABILITIES | 4383290000 | 4383290000 | 4106835000 | 4106835000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | TOTAL SHAREHOLDERS' EQUITY | 1778196000 | 1778196000 | 1521967000 | 1521967000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 614221000 | 614221000 | 560219000 | 560219000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -362128000 | -362128000 | -318870000 | -318870000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -240318000 | -240318000 | -237983000 | -237983000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Property and equipment | -5523000 | 5523000 | -4710000 | 4710000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation | 8129000 | 8129000 | 7664000 | 7664000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R78.htm | Stock-based compensation expenses | 8000000 |  |  |  |  | FILING-CHECKED | check: hand / Stock plans note reports stock-based compensation expense of $8M (rounded, $ in millions) for 2025, tagged on the all-plans 'RLI Corp. Long-Term Incentive Plans' member (not an entity or segment); no other SBC expense li / pages opened: R5, R73, R76, R78, R79, R80 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Cash dividends paid | -241562000 | 241562000 | -235656000 | 235656000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001104659-26-018013 R7.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Treasury shares unchanged at 45,860,428 in 2024 and 2025; equity statement and cash flow show no repurchases (only deferred-compensation transfers). / pages opened: R2, R3, R60, R93, R94, R5, R7 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaid | R61.htm | Interest paid | 5000000 | 5000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R61.htm 'Debt (Details)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R75.htm | Total taxes paid | 60648000 | 60648000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R75.htm 'Income Taxes - Income Taxes Paid (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:ShortTermBorrowings | R2.htm | Short-term debt | 100000000 | 100000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; no finance lease liability fact in the filing; operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding (in shares) | 91878651 | 91878651 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Consolidated revenue' on us-gaap:Revenues = 794634000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Insurance operating expenses' on us-gaap:OperatingExpenses = 51480000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Interest expense on debt' on us-gaap:InterestExpenseDebt = 7426000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 196682000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Total tax expense' on us-gaap:IncomeTaxExpenseBenefit = 59138000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Net earnings' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 137544000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Net earnings per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.18 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Net earnings per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.12 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 43299000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001558370-16-003590 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 44131000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001558370-16-003590 R2.htm prints 'Cash' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 11081000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001558370-16-003590 R2.htm prints 'Premiums and reinsurance balances receivable, net of allowances for uncollectibl' on rli:PremiumsAndReinsuranceBalancesReceivable = 143662000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001558370-16-003590 R2.htm prints 'Property and equipment, at cost, net of accumulated depreciation of $38,447 in 2' on us-gaap:PropertyPlantAndEquipmentNet = 47102000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001558370-16-003590 R2.htm prints 'Goodwill and intangibles' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 71294000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001558370-16-003590 R2.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 2736579000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001558370-16-003590 R2.htm prints 'TOTAL LIABILITIES' on us-gaap:Liabilities = 1913110000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001558370-16-003590 R2.htm prints 'TOTAL SHAREHOLDERS’ EQUITY' on us-gaap:StockholdersEquity = 823469000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001558370-16-003590 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 152586000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001558370-16-003590 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -60597000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001558370-16-003590 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -111528000 (FILING-CHECKED)
- capex: FY2015 10-K 0001558370-16-003590 R7.htm prints 'Property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -10035000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001558370-16-003590 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001558370-16-003590 R7.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -119577000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001558370-16-003590 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001558370-16-003590 R7.htm read; no row matched (auto)
- net_income: era 10-K 0000084246-18-000011 R4.htm prints 'Net earnings' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = 105028000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001564590-22-005648 R2.htm prints 'Cash' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 88804000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_receivable: API missing (rli:PremiumsAndReinsuranceBalancesReceivable)
