# CVLT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001169561-26-000017 (CIK 0001169561, filed 2026-05-11): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001169561-24-000039 (CIK 0001169561, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001169561.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 1183690000 | 1183690000 | 995619000 | 995619000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Total cost of revenues | 223120000 | 223120000 | 179035000 | 179035000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross margin | 960570000 | 960570000 | 816584000 | 816584000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 886580000 | 886580000 | 742846000 | 742846000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 162722000 | 162722000 | 138375000 | 138375000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 162213000 | 162213000 | 146286000 | 146286000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 73990000 | 73990000 | 73738000 | 73738000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -3795000 | 3795000 | -416000 | 416000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 92124000 | 92124000 | 81053000 | 81053000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense (benefit) | 21467000 | 21467000 | 4947000 | 4947000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 70657000 | 70657000 | 76106000 | 76106000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.61 | 1.61 | 1.74 | 1.74 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.58 | 1.58 | 1.68 | 1.68 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 43976000 | 43976000 | 43850000 | 43850000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 44654000 | 44654000 | 45187000 | 45187000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 899987000 | 899987000 | 302103000 | 302103000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade accounts receivable, net | 330483000 | 330483000 | 251995000 | 251995000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1286510000 | 1286510000 | 635057000 | 635057000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 9750000 | 9750000 | 8294000 | 8294000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 209322000 | 209322000 | 185255000 | 185255000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1886305000 | 1886305000 | 1118266000 | 1118266000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 651000 | 651000 | 373000 | 373000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 658170000 | 658170000 | 555050000 | 555050000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 7494000 | 7494000 | 325122000 | 325122000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 244680000 | 244680000 | 207382000 | 207382000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -5446000 | -5446000 | -70400000 | -70400000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 345301000 | 345301000 | -147818000 | -147818000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property and equipment | -7529000 | 7529000 | -3756000 | 3756000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 10348000 | 10348000 | 9072000 | 9072000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Noncash stock-based compensation | 123425000 | 123425000 | 113262000 | 113262000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -446106000 | 446106000 | -165015000 | 165015000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid | 13612000 | 13612000 | 42185000 | 42185000 | Y | FILING-CHECKED | accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: no standard debt line on the BS face; not hand-verified |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 41255000 | 41255000 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-03-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001169561-24-000039 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -415000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
