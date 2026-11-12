# MRNA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001682852-26-000033 (CIK 0001682852, filed 2026-02-20): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001682852-21-000006 (CIK 0001682852, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001682852-20-000006 (CIK 0001682852, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0001682852.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 1944000000 | 1944000000 | 3236000000 | 3236000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of sales | 868000000 | 868000000 | 1464000000 | 1464000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (916 tags across all 94 R pages, face and notes) of 0001682852-26-000033; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 5018000000 | 5018000000 | 7181000000 | 7181000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1018000000 | 1018000000 | 1174000000 | 1174000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 3132000000 | 3132000000 | 4543000000 | 4543000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -3074000000 | -3074000000 | -3945000000 | -3945000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (916 tags across all 94 R pages, face and notes) of 0001682852-26-000033; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -2768000000 | -2768000000 | -3607000000 | -3607000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) tax provision | 54000000 | 54000000 | -46000000 | -46000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -2822000000 | -2822000000 | -3561000000 | -3561000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in usd per share) | -7.26 | -7.26 | -9.28 | -9.28 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in usd per share) | -7.26 | -7.26 | -9.28 | -9.28 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 389000000 | 389000000 | 384000000 | 384000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 389000000 | 389000000 | 384000000 | 384000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2595000000 | 2595000000 | 1927000000 | 1927000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 184000000 | 184000000 | 358000000 | 358000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 153000000 | 153000000 | 117000000 | 117000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 6544000000 | 6544000000 | 8099000000 | 8099000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant and equipment, net | 2134000000 | 2134000000 | 2196000000 | 2196000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R64.htm | Other Balance Sheet Components - Other Non-Current Assets (Details) |  | 52000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R64.htm 'Other Balance Sheet Components - Other Non-Current Assets (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 12338000000 | 12338000000 | 14142000000 | 14142000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 317000000 | 317000000 | 405000000 | 405000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1987000000 | 1987000000 | 2206000000 | 2206000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3688000000 | 3688000000 | 3241000000 | 3241000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 8650000000 | 8650000000 | 10901000000 | 10901000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash used in operating activities | -1873000000 | -1873000000 | -3004000000 | -3004000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by investing activities | 1946000000 | 1946000000 | 1949000000 | 1949000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 593000000 | 593000000 | 56000000 | 56000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, plant and equipment | -192000000 | 192000000 | -1051000000 | 1051000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:OtherDepreciationAndAmortization | R8.htm | Depreciation and amortization | 215000000 | 215000000 | 189000000 | 189000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 483000000 | 483000000 | 429000000 | 429000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (916 tags across all 94 R pages, face and notes) of 0001682852-26-000033; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Tax payments related to net share settlements on equity awards | -2000000 | 2000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 10000000 | 10000000 | 24000000 | 24000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid (received) for income taxes | 26000000 | 26000000 | 197000000 | 197000000 | Y | FILING-CHECKED | accn 0001682852-26-000033 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Long-term debt | 590000000 | 590000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares, outstanding (in shares) | 394000000 | 394000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- revenue: era 10-K 0001682852-21-000006 R4.htm prints 'Revenues' on us-gaap:Revenues = 803395000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001682852-21-000006 R4.htm prints 'Loss before provision for (benefit from) income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -744513000 (FILING-CHECKED)
- basic_eps: era 10-K 0001682852-21-000006 R4.htm prints 'Net loss per share attributable to common stockholders, basic and diluted (usd p' on us-gaap:EarningsPerShareBasicAndDiluted = -1.96 (FILING-CHECKED)
- diluted_eps: era 10-K 0001682852-21-000006 R4.htm prints 'Net loss per share attributable to common stockholders, basic and diluted (usd p' on us-gaap:EarningsPerShareBasicAndDiluted = -1.96 (FILING-CHECKED)
- revenue: era 10-K 0001682852-20-000006 R4.htm prints 'Total revenue' on us-gaap:Revenues = 60209000 (FILING-CHECKED)
- operating_expenses: era 10-K 0001682852-20-000006 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 605929000 (FILING-CHECKED)
- ppe_net: era 10-K 0001682852-20-000006 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet =  (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:ResearchAndDevelopmentExpense+us-gaap:GeneralAndAdministrativeExpense (R5.htm): 2026-11-12 R5.htm: corrected: opex = 3,132 + 1,018 = 4,150 = 1,944 - 868 + 3,074
- interest_expense: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- goodwill: mapped us-gaap:Goodwill (R64.htm): 2026-11-12 R64.htm: agree: R64 'Goodwill' 52 inside other non-current assets: the full goodwill balance, not on the face
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent (R3.htm): 2026-11-12 R3.htm: corrected: finance-lease ruling (founder 2026-11-04 item 5): R70 places financing leases in other current liabilities (25) and lease liabilities non-current (20), outside the debt line: 590 + 25 + 20
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in shares)' is the weighted_basic_shares line, printed 389000000 = filing XBRL 389000000; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts receivable, net' is the accounts_receivable line, printed 184000000 = filing XBRL 184000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current assets' is the current_assets line, printed 6544000000 = filing XBRL 6544000000; agrees
- total_assets: mapped us-gaap:Assets (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total assets' is the total_assets line, printed 12338000000 = filing XBRL 12338000000; agrees
- total_liabilities: mapped us-gaap:Liabilities (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total liabilities' is the total_liabilities line, printed 3688000000 = filing XBRL 3688000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total stockholders’ equity' is the stockholders_equity line, printed 8650000000 = filing XBRL 8650000000; agrees
