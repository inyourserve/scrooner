# DDOG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-008819 (CIK 0001561550, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001564590-21-009770 (CIK 0001561550, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001561550-24-000009 (CIK 0001561550, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001561550.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 3427158000 | 3427158000 | 2684275000 | 2684275000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenue | 686957000 | 686957000 | 515531000 | 515531000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2740201000 | 2740201000 | 2168744000 | 2168744000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 2784574000 | 2784574000 | 2114460000 | 2114460000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 279700000 | 279700000 | 205152000 | 205152000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 1548451000 | 1548451000 | 1152703000 | 1152703000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating (loss) income | -44373000 | -44373000 | 54284000 | 54284000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -11059000 | 11059000 | -7068000 | 7068000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 127021000 | 127021000 | 203940000 | 203940000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 19280000 | 19280000 | 20194000 | 20194000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 107741000 | 107741000 | 183746000 | 183746000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in dollars per share) | 0.31 | 0.31 | 0.55 | 0.55 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in dollars per share) | 0.31 | 0.31 | 0.52 | 0.52 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average shares used in calculating basic net income per share (in shares) | 347309000 | 347309000 | 336172000 | 336172000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average shares used in calculating diluted net income per share (in shares) | 363472000 | 363472000 | 358636000 | 358636000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 401305000 | 401305000 | 1246983000 | 1246983000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for credit losses of $19,292 and $16,302 as of December 31, 2025 and 2024, respect | 741262000 | 741262000 | 598919000 | 598919000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (771 tags across all 80 R pages, face and notes) of 0001628280-26-008819; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 5382280000 | 5382280000 | 4911115000 | 4911115000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 338093000 | 338093000 | 226970000 | 226970000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 530568000 | 530568000 | 360381000 | 360381000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 6643844000 | 6643844000 | 5785339000 | 5785339000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 148791000 | 148791000 | 107731000 | 107731000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1591401000 | 1591401000 | 1862713000 | 1862713000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 2911638000 | 2911638000 | 3070976000 | 3070976000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 3732206000 | 3732206000 | 2714363000 | 2714363000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1050135000 | 1050135000 | 870603000 | 870603000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -1334480000 | -1334480000 | -736840000 | -736840000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash (used in) provided by financing activities | -572483000 | -572483000 | 787083000 | 787083000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -49578000 | 49578000 | -34719000 | 34719000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 55756000 | 55756000 | 54933000 | 54933000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation, net of amounts capitalized | 750671000 | 750671000 | 570336000 | 570336000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (771 tags across all 80 R pages, face and notes) of 0001628280-26-008819; no face row matched |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (771 tags across all 80 R pages, face and notes) of 0001628280-26-008819; no face row matched |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (771 tags across all 80 R pages, face and notes) of 0001628280-26-008819; no face row matched |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income taxes | 17649000 | 17649000 | 20993000 | 20993000 | Y | FILING-CHECKED | accn 0001628280-26-008819 R8.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R55.htm | Convertible Senior Notes - Schedule of Net Carrying Amount of Notes (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R55.htm 'Convertible Senior Notes - Schedule of Net Carrying Amount of Notes (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 352525971 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001564590-21-009770 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -30434000 (FILING-CHECKED)
- interest_expense: era 10-K 0001561550-24-000009 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -6302000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- share_buybacks: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:ConvertibleNotesPayableCurrent+us-gaap:ConvertibleLongTermNotesPayable (R3.htm): 2026-11-12 R3.htm: corrected: the debt is on the BS face (R3): 0 + 983,449 (thousands); the NOTE row had no value; no finance-lease facts
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: class rows at the BS date (R4)
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Interest expense' is the interest_expense line, printed -11059000 = filing XBRL 11059000; agrees
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Income before provision for income taxes' is the income_before_tax line, printed 127021000 = filing XBRL 127021000; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts receivable, net of allowance for credit l' is the accounts_receivable line, printed 741262000 = filing XBRL 741262000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Net cash used in investing activities' is the cash_flow_investing line, printed -1334480000 = filing XBRL -1334480000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Net cash (used in) provided by financing activitie' is the cash_flow_financing line, printed -572483000 = filing XBRL -572483000; agrees
- depreciation_and_amortization: mapped us-gaap:DepreciationAndAmortization (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Depreciation and amortization' is the depreciation_and_amortization line, printed 55756000 = filing XBRL 55756000; agrees
