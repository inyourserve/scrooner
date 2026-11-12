# CEG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001868275-26-000032 (CIK 0001868275, filed 2026-02-24): COVER R1.htm, IS R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm, CI R9.htm
- 10-K 0001868275-24-000014 (CIK 0001868275, era filing): COVER R1.htm, IS R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm, CI R9.htm
- 10-K 0001868275-23-000014 (CIK 0001868275, era filing): COVER R1.htm, IS R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm, CI R9.htm
- companyfacts CIK0001868275.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Operating revenues | 25533000000 | 25533000000 | 23568000000 | 23568000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1337 tags across all 149 R pages, face and notes) of 0001868275-26-000032; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1337 tags across all 149 R pages, face and notes) of 0001868275-26-000032; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total operating expenses | 22447000000 | 22447000000 | 19287000000 | 19287000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1337 tags across all 149 R pages, face and notes) of 0001868275-26-000032; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1337 tags across all 149 R pages, face and notes) of 0001868275-26-000032; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income (loss) | 3086000000 | 3086000000 | 4352000000 | 4352000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense, net | -511000000 | 511000000 | -506000000 | 506000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income (loss) before income taxes | 3511000000 | 3511000000 | 4516000000 | 4516000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax (benefit) expense | 1187000000 | 1187000000 | 774000000 | 774000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income (loss) attributable to membership interest | 2319000000 | 2319000000 | 3749000000 | 3749000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 7.4 | 7.4 | 11.91 | 11.91 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 7.4 | 7.4 | 11.89 | 11.89 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 313000000 | 313000000 | 315000000 | 315000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 314000000 | 314000000 | 315000000 | 315000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 3641000000 | 3641000000 | 3022000000 | 3022000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, net | 4266000000 | 4266000000 | 3718000000 | 3718000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories, net | 1736000000 | 1736000000 | 1600000000 | 1600000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 12119000000 | 12119000000 | 10776000000 | 10776000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment (net of accumulated depreciation and amortization of $19,072 and $18,088, respectively) | 22474000000 | 22474000000 | 21235000000 | 21235000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 420000000 | 420000000 | 420000000 | 420000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 57249000000 | 57249000000 | 52926000000 | 52926000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued expenses | 4294000000 | 4294000000 | 3943000000 | 3943000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 7944000000 | 7944000000 | 6846000000 | 6846000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 42396000000 | 42396000000 | 39387000000 | 39387000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total shareholders’ equity | 14517000000 | 14517000000 | 13166000000 | 13166000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R4.htm | Net cash flows provided by (used in) operating activities | 4237000000 | 4237000000 | -2464000000 | -2464000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R4.htm | Net cash flows provided by (used in) investing activities | -3198000000 | -3198000000 | 7428000000 | 7428000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R4.htm | Net cash flows provided by (used in) financing activities | -420000000 | -420000000 | -2289000000 | -2289000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R4.htm | Capital expenditures | -2949000000 | 2949000000 | -2565000000 | 2565000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R4.htm | Depreciation, amortization, and accretion, including nuclear fuel and energy contract amortization | 2601000000 | 2601000000 | 2700000000 | 2700000000 | Y | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R139.htm | Stock-Based Compensation Plans - Schedule of Stock-based Compensation Expense (Details) |  | 385000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R139.htm 'Stock-Based Compensation Plans - Schedule of Stock-based Compensation Expense (D' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R4.htm | Dividends paid on common stock | -486000000 | 486000000 | -444000000 | 444000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R4.htm | Repurchases of common stock | -400000000 | 400000000 | -999000000 | 999000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001868275-26-000032 R4.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R147.htm | Supplemental Financial Information - Supplemental Cash Flow Information (Details) |  | 412000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R147.htm 'Supplemental Financial Information - Supplemental Cash Flow Information (Details' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R92.htm | Income Taxes - Income Taxes Paid (Details) |  | 446000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Income Taxes - Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Short-term borrowings + Long-term debt due within one year + Long-term debt | 8992000000 | 8992000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 312000000 | 312000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- interest_expense: era 10-K 0001868275-24-000014 R3.htm prints 'Interest expense, net' on us-gaap:InterestExpense = -431000000 (FILING-CHECKED)
- accounts_payable: era 10-K 0001868275-23-000014 R5.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 2828000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: combined us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: agree: 'Total operating expenses' includes purchased power and fuel: combined
- sga_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R139.htm): 2026-11-12 R139.htm: agree: value in the note is the full data point; agree
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R147.htm): 2026-11-12 R147.htm: agree: value in the note is the full data point; agree
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R92.htm): 2026-11-12 R92.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: agree: R5 1,650 + 92 + 7,250
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating income (loss)' is the operating_income line, printed 3086000000 = filing XBRL 3086000000; agrees
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Income (loss) before income taxes' is the income_before_tax line, printed 3511000000 = filing XBRL 3511000000; agrees
- inventory: mapped us-gaap:InventoryNet (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Inventories, net' is the inventory line, printed 1736000000 = filing XBRL 1736000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: BS R5.htm 'Total shareholders’ equity' is the stockholders_equity line, printed 14517000000 = filing XBRL 14517000000; agrees
- cfo: mapped us-gaap:NetCashProvidedByUsedInOperatingActivities (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: CF R4.htm 'Net cash flows provided by (used in) operating act' is the cfo line, printed 4237000000 = filing XBRL 4237000000; agrees
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: CF R4.htm 'Net cash flows provided by (used in) financing act' is the cash_flow_financing line, printed -420000000 = filing XBRL -420000000; agrees
