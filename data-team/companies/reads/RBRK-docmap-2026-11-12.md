# RBRK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001943896-26-000013 (CIK 0001943896, filed 2026-03-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001943896-25-000012 (CIK 0001943896, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001943896-26-000013 (CIK 0001943896, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001943896.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 1316191000 | 1316191000 | 886544000 | 886544000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenue | 261877000 | 261877000 | 265748000 | 265748000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 1054314000 | 1054314000 | 620796000 | 620796000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 1399730000 | 1399730000 | 1754828000 | 1754828000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 257029000 | 257029000 | 355695000 | 355695000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 373682000 | 373682000 | 531615000 | 531615000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Loss from operations | -345416000 | -345416000 | -1134032000 | -1134032000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R5.htm | Interest expense | -17227000 | 17227000 | -41253000 | 41253000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -326473000 | -326473000 | -1148452000 | -1148452000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 22355000 | 22355000 | 6368000 | 6368000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss | -348828000 | -348828000 | -1154820000 | -1154820000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net loss per share, basic (in dollars per share) | -1.78 | -1.78 | -7.48 | -7.48 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net loss per share, diluted (in dollars per share) | -1.78 | -1.78 | -7.48 | -7.48 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted-average shares used in computing net loss per share, basic (in shares) | 196468000 | 196468000 | 154294000 | 154294000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted-average shares used in computing net loss per share, diluted (in shares) | 196468000 | 196468000 | 154294000 | 154294000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R5.htm period ..2026-01-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 380196000 | 380196000 | 186331000 | 186331000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances of $299 and $499 | 256773000 | 256773000 | 177627000 | 177627000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| inventory | mapped | us-gaap:InventoryNet | R50.htm | Balance Sheet Components - Schedule of Prepaid Expenses and Other Current Assets (Details) |  | 5676000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R50.htm 'Balance Sheet Components - Schedule of Prepaid Expenses and Other Current Assets' (MetaLinks.json presentation); value from companyfacts same accession |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2223564000 | 2223564000 | 1077641000 | 1077641000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 83830000 | 83830000 | 53194000 | 53194000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 199606000 | 199606000 | 100343000 | 100343000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2766536000 | 2766536000 | 1422974000 | 1422974000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 15329000 | 15329000 | 10439000 | 10439000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1314059000 | 1314059000 | 950176000 | 950176000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3286098000 | 3286098000 | 1976708000 | 1976708000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ deficit | -519562000 | -519562000 | -553734000 | -553734000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R3.htm period ..2026-01-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by (used in) operating activities | 282908000 | 282908000 | 48228000 | 48228000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -830089000 | -830089000 | -383442000 | -383442000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 736501000 | 736501000 | 398023000 | 398023000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -29631000 | 29631000 | -16885000 | 16885000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 37115000 | 37115000 | 28868000 | 28868000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 329374000 | 329374000 | 913913000 | 913913000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (849 tags across all 89 R pages, face and notes) of 0001943896-26-000013; no face row matched |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (849 tags across all 89 R pages, face and notes) of 0001943896-26-000013; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 11807000 | 11807000 | 15026000 | 15026000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes, net of refunds | 12005000 | 12005000 | 11938000 | 11938000 | Y | FILING-CHECKED | accn 0001943896-26-000013 R8.htm period ..2026-01-31 |
| total_debt | component sum | us-gaap:OtherLongTermDebtNoncurrent | R3.htm | Debt, noncurrent | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 202242140 |  |  |  |  | FILING-CHECKED | balance-sheet date 2026-01-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001943896-25-000012 R5.htm prints 'Interest expense' on us-gaap:InterestExpenseNonoperating = -41253000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001943896-26-000013 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 380196000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
