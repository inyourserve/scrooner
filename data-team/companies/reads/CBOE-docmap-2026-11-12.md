# CBOE document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-010013 (CIK 0001374310, filed 2026-02-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001374310-16-000038 (CIK 0001374310, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001558370-18-000953 (CIK 0001374310, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001558370-24-001277 (CIK 0001374310, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001374310.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R5.htm | Total revenues | 4714200000 | 4714200000 | 4094500000 | 4094500000 | Y | FILING-CHECKED | accn 0001628280-26-010013 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenues | 2285100000 | 2285100000 | 2022100000 | 2022100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Revenues less cost of revenues | 2429100000 | 2429100000 | 2072400000 | 2072400000 | Y | FILING-CHECKED | accn 0001628280-26-010013 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 962000000 | 962000000 | 974000000 | 974000000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1007 tags across all 107 R pages, face and notes) of 0001628280-26-010013; no face row matched / check: hand R5.htm agree |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1007 tags across all 107 R pages, face and notes) of 0001628280-26-010013; no face row matched / check: hand R5.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 1467100000 | 1467100000 | 1098400000 | 1098400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -52300000 | 52300000 | -51500000 | 51500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income tax provision | 1566600000 | 1566600000 | 1083800000 | 1083800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax provision | 466600000 | 466600000 | 318900000 | 318900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 1100000000 | 1100000000 | 764900000 | 764900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per share (in dollars per share) | 10.46 | 10.46 | 7.24 | 7.24 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per share (in dollars per share) | 10.42 | 10.42 | 7.21 | 7.21 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted average shares outstanding (in shares) | 104700000 | 104700000 | 105100000 | 105100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted average shares outstanding (in shares) | 105100000 | 105100000 | 105500000 | 105500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2216500000 | 2216500000 | 920300000 | 920300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of $6.8 allowance for credit losses at December 31, 2025 and $6.6 at December 31, 2024 | 391400000 | 391400000 | 444600000 | 444600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1007 tags across all 107 R pages, face and notes) of 0001628280-26-010013; no face row matched / check: hand R3.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4421400000 | 4421400000 | 2479100000 | 2479100000 | Y | FILING-CHECKED | accn 0001628280-26-010013 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| ppe_net | mapped | cboe:PropertyPlantAndEquipmentExcludingLandNet | R3.htm | Property and equipment, net | 133100000 |  | 118000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001628280-26-010013 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 3150500000 | 3150500000 | 3124200000 | 3124200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9305300000 | 9305300000 | 7789100000 | 7789100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued liabilities | 686900000 | 686900000 | 359700000 | 359700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 2362300000 | 2362300000 | 1395200000 | 1395200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4167000000 | 4167000000 | 3509500000 | 3509500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 5138300000 | 5138300000 | 4279600000 | 4279600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash flows provided by operating activities | 1752600000 | 1752600000 | 1100600000 | 1100600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash flows provided by (used in) investing activities | 450200000 | 450200000 | -141800000 | -141800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash flows used in financing activities | -371600000 | -371600000 | -495000000 | -495000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment and leasehold improvements, net | -71000000 | 71000000 | -60900000 | 60900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 122400000 | 122400000 | 133000000 | 133000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 50400000 | 50400000 | 41800000 | 41800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends on common stock | -284300000 | 284300000 | -249400000 | 249400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchase of common stock, including commissions and excise taxes | -66700000 | 66700000 | -204800000 | 204800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 91700000 | 91700000 | 100100000 | 100100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid for income taxes, net | 391600000 | 391600000 | 362400000 | 362400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-010013 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Long-term debt | 1442900000 | 1442900000 | 1441000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm corrected: Only debt line is Long-term debt 1,442.9 / 1,441.0 (LongTermDebtNoncurrent); no current debt, no finance-lease tags in filing; filled missing FY1. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 104647739 | 104647739 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Total Operating Revenues' on us-gaap:Revenues = 634545000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001374310-16-000038 R4.htm read; no row matched (auto)
- gross_profit: FY2015 10-K 0001374310-16-000038 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Total Operating Expenses' on us-gaap:OperatingExpenses = 314617000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Operating Income' on us-gaap:OperatingIncomeLoss = 319928000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Interest Expense' on us-gaap:InterestExpense = -43000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Income Before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 324024000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Income tax provision' on us-gaap:IncomeTaxExpenseBenefit = 119001000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Net Income' on us-gaap:NetIncomeLoss = 205023000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.46 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Diluted—net income per share to common stockholders' on us-gaap:EarningsPerShareDiluted = 2.46 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Weighted Average Number of Shares Outstanding, Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 83081000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001374310-16-000038 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 83081000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 102253000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Accounts receivable—net allowances of 2015 - $150 and 2014 - $285' on us-gaap:AccountsReceivableNetCurrent = 62535000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 204118000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Total Property and Equipment—Net' on us-gaap:PropertyPlantAndEquipmentNet = 60360000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 7655000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Total' on us-gaap:Assets = 384788000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 60104000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 73997000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 125143000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001374310-16-000038 R2.htm prints 'Stockholders' Equity Attributable to Parent' on us-gaap:StockholdersEquity = 259645000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Net Cash Flows provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 245278000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Net Cash Flows used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -79421000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Net Cash Flows used in Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -211531000 (FILING-CHECKED)
- capex: FY2015 10-K 0001374310-16-000038 R6.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 46274000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 12181000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001374310-16-000038 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Purchase of common stock under announced program' on us-gaap:PaymentsForRepurchaseOfCommonStock = -132167000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001374310-16-000038 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001374310-16-000038 R6.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 133460000 (FILING-CHECKED)
- revenue: era 10-K 0001558370-18-000953 R4.htm prints 'Total revenues' on us-gaap:Revenues = 2229100000 (FILING-CHECKED)
- interest_expense: era 10-K 0001558370-24-001277 R4.htm prints 'Interest expense' on cboe:InterestExpenseNonoperating = -62400000 (FILING-CHECKED)

## Mismatches (printed vs API)
- ppe_net: API missing (cboe:PropertyPlantAndEquipmentExcludingLandNet)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 8 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 1.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
