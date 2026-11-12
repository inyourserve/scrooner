# BNY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001390777-26-000033 (CIK 0001390777, filed 2026-02-25): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001390777-16-000204 (CIK 0001390777, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001390777-24-000051 (CIK 0001390777, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- 10-K 0001390777-22-000043 (CIK 0001390777, era filing): COVER R1.htm, IS R4.htm, BS R6.htm, BSP R7.htm, CF R8.htm
- companyfacts CIK0001390777.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | bk:TotalRevenuesIncludingRevenueGeneratedByVariableInterestEntities | R3.htm | Total revenue | 20080000000 |  | 18619000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R3.htm | Interest expense | 20682000000 | 20682000000 | 21295000000 | 21295000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | bk:IncomeLossFromContinuingOperationsBeforeIncomeTaxes | R3.htm | Income before income taxes | 7058000000 |  | 5848000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | 1475000000 | 1475000000 | 1305000000 | 1305000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income applicable to shareholders of The Bank of New York Mellon Corporation | 5549000000 | 5549000000 | 4530000000 | 4530000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (usd per share) | 7.47 | 7.47 | 5.84 | 5.84 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (usd per share) | 7.4 | 7.4 | 5.8 | 5.8 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (shares) | 710177000 | 710177000 | 742588000 | 742588000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (shares) | 716718000 | 716718000 | 748101000 | 748101000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R6.htm | Cash and due from banks, net of allowance for credit losses of $19 and $23 | 5111000000 | 5111000000 | 4178000000 | 4178000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R6.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| current_assets | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Premises and equipment | 3581000000 | 3581000000 | 3266000000 | 3266000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 16767000000 | 16767000000 | 16598000000 | 16598000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 472300000000 | 472300000000 | 416064000000 | 416064000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R6.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| current_liabilities | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1661 tags across all 157 R pages, face and notes) of 0001390777-26-000033; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 427492000000 | 427492000000 | 374300000000 | 374300000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total The Bank of New York Mellon Corporation shareholders’ equity | 44313000000 | 44313000000 | 41318000000 | 41318000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 6730000000 | 6730000000 | 687000000 | 687000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash (used for) provided by investing activities | -44283000000 | -44283000000 | -9479000000 | -9479000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used for) financing activities | 39714000000 | 39714000000 | 6338000000 | 6338000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of premises and equipment/capitalized software | -1553000000 | 1553000000 | -1469000000 | 1469000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R8.htm | Depreciation and amortization | 1852000000 | 1852000000 | 1803000000 | 1803000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R119.htm | Stock-based compensation - Narrative (Details) |  | 1000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R119.htm 'Stock-based compensation - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Common cash dividends paid | -1447000000 | 1447000000 | -1348000000 | 1348000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury stock acquired | -3535000000 | 3535000000 | -3064000000 | 3064000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 20629000000 | 20629000000 | 21374000000 | 21374000000 | Y | FILING-CHECKED | accn 0001390777-26-000033 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R156.htm | Supplemental information to the Consolidated Statement of Cash Flows - Narrative (Details) |  | 991000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R156.htm 'Supplemental information to the Consolidated Statement of Cash Flows - Narrative' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:CommercialPaper+us-gaap:LongTermDebt | R6.htm | Commercial paper + Long-term debt | 33876000000 | 33876000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R109.htm | Shareholders' equity - Narrative (Details) |  | 688236337 |  |  |  | FILING-CHECKED | not on the face statement; shown in R109.htm 'Shareholders' equity - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001390777-16-000204 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 300000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Income before income taxes' on bk:IncomeLossFromContinuingOperationsBeforeIncomeTaxes = 4235000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1013000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Net income applicable to shareholders of The Bank of New York Mellon Corporation' on us-gaap:NetIncomeLoss = 3158000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Basic (usd per share)' on us-gaap:EarningsPerShareBasic = 2.73 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Diluted (usd per share)' on us-gaap:EarningsPerShareDiluted = 2.71 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 1104719000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001390777-16-000204 R2.htm prints 'Diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 1112511000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001390777-16-000204 R6.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001390777-16-000204 R6.htm prints 'Premises and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 1379000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001390777-16-000204 R6.htm prints 'Goodwill' on us-gaap:Goodwill = 17618000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001390777-16-000204 R6.htm prints 'Total assets' on us-gaap:Assets = 393780000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001390777-16-000204 R6.htm prints 'Total liabilities' on us-gaap:Liabilities = 354805000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001390777-16-000204 R6.htm prints 'Total The Bank of New York Mellon Corporation shareholders’ equity' on us-gaap:StockholdersEquity = 38037000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Net cash provided by (used for) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 4127000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Net cash (used for) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -19787000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 15185000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Purchases of premises and equipment/capitalized software' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -601000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 1457000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001390777-16-000204 R8.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Common cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -760000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Treasury stock acquired' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2355000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 295000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001390777-16-000204 R8.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 1015000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001390777-24-000051 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = 16303000000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001390777-22-000043 R6.htm prints 'Cash and due from banks, net of allowance for credit losses of $3 and $4' on us-gaap:CashAndDueFromBanks = 6061000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- revenue: API missing (bk:TotalRevenuesIncludingRevenueGeneratedByVariableInterestEntities)
- income_before_tax: API missing (bk:IncomeLossFromContinuingOperationsBeforeIncomeTaxes)

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- gross_profit: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_expenses: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- sga_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: OUT  (R3.htm): 2026-11-12 R3.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- operating_income: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- accounts_receivable: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- inventory: OUT  (R6.htm): 2026-11-12 R6.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- current_assets: OUT  (R6.htm): 2026-11-12 R6.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- accounts_payable: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- current_liabilities: OUT  (R6.htm): 2026-11-12 R6.htm: OUT of the bank template (Dhairya ruling 2026-11-12); whole-filing check agrees; nothing printed
- sbc: review us-gaap:AllocatedShareBasedCompensationExpense (R119.htm): 2026-11-12 R119.htm: R119 AllocatedShareBasedCompensationExpense is 1,000,000 (0 in 2023 and 2024): not total stock-based compensation; R119 read owed
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R156.htm): 2026-11-12 R156.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:CommercialPaper+us-gaap:OtherBorrowings+us-gaap:LongTermDebt (R6.htm): 2026-11-12 R6.htm: corrected: the tool left out 'Other borrowed funds' (422); 2,003 + 422 + 31,873
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R109.htm): 2026-11-12 R109.htm: agree: R109 688,236,337 at the BS date
- interest_expense: mapped us-gaap:InterestExpenseOperating (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Interest expense' is the interest_expense line, printed 20682000000 = filing XBRL 20682000000; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Net income applicable to shareholders of The Bank ' is the net_income line, printed 5549000000 = filing XBRL 5549000000; agrees
- total_assets: mapped us-gaap:Assets (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total assets' is the total_assets line, printed 472300000000 = filing XBRL 472300000000; agrees
- capex: mapped us-gaap:PaymentsToAcquirePropertyPlantAndEquipment (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Purchases of premises and equipment/capitalized so' is the capex line, printed -1553000000 = filing XBRL 1553000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Treasury stock acquired' is the share_buybacks line, printed -3535000000 = filing XBRL 3535000000; agrees
- sbc (review resolved, Dhairya relay 2026-11-12): mapped us-gaap:AllocatedShareBasedCompensationExpense (R119.htm): decided by the filing: R119 total stock-based compensation cost 508,000,000 (FY2024 386,000,000); the 1,000,000 row the tool took is a single award-plan member
