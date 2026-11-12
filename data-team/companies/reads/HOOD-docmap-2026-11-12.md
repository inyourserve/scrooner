# HOOD document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001783879-26-000023 (CIK 0001783879, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001783879-25-000049 (CIK 0001783879, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001783879-23-000045 (CIK 0001783879, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0001783879.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total net revenues | 4473000000 | 4473000000 | 2951000000 | 2951000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 2379000000 | 2379000000 | 1897000000 | 1897000000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 628000000 | 628000000 | 455000000 | 455000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R40.htm | DESCRIPTION OF BUSINESS AND SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES - Narrative (Details) |  | 355000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'DESCRIPTION OF BUSINESS AND SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES - Narrati' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R51.htm | REVENUES - Interest Revenue Earned And Interest Expense Paid From Securities Lending (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R51.htm 'REVENUES - Interest Revenue Earned And Interest Expense Paid From Securities Len' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before income taxes | 2108000000 | 2108000000 | 1064000000 | 1064000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for (benefit from) income taxes | 225000000 | 225000000 | -347000000 | -347000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) attributable to Robinhood | 1883000000 | 1883000000 | 1411000000 | 1411000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 2.12 | 2.12 | 1.6 | 1.6 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 2.05 | 2.05 | 1.56 | 1.56 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 888504958 | 888504958 | 881113156 | 881113156 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 918781846 | 918781846 | 906171504 | 906171504 | Y | FILING-CHECKED | accn 0001783879-26-000023 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 4261000000 | 4261000000 | 4332000000 | 4332000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 36305000000 | 36305000000 | 25103000000 | 25103000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, software, and equipment, net | 154000000 | 154000000 | 139000000 | 139000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 385000000 | 385000000 | 179000000 | 179000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 38137000000 | 38137000000 | 26187000000 | 26187000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 463000000 | 463000000 | 397000000 | 397000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 28771000000 | 28771000000 | 18104000000 | 18104000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 28986000000 | 28986000000 | 18215000000 | 18215000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Total stockholders’ equity | 9151000000 | 9151000000 | 7972000000 | 7972000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001783879-26-000023 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used in) operating activities | 1638000000 | 1638000000 | -157000000 | -157000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | 141000000 | 141000000 | -148000000 | -148000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -590000000 | -590000000 | -345000000 | -345000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireOtherProductiveAssets | R7.htm | Purchases of property, software, and equipment | -15000000 | 15000000 | -13000000 | 13000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 86000000 | 86000000 | 77000000 | 77000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 305000000 | 305000000 | 304000000 | 304000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of Class A common stock | -653000000 | 653000000 | -257000000 | 257000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 31000000 | 31000000 | 16000000 | 16000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes, net of refund received | 95000000 | 95000000 | 18000000 | 18000000 | Y | FILING-CHECKED | accn 0001783879-26-000023 R7.htm period ..2025-12-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (1067 tags across all 98 R pages, face and notes) of 0001783879-26-000023; no face row matched |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 901328432 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- stockholders_equity: era 10-K 0001783879-25-000049 R3.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 7972000000 (FILING-CHECKED)
- capex: era 10-K 0001783879-23-000045 R7.htm prints 'Purchase of property, software, and equipment' on us-gaap:PaymentsToAcquireProductiveAssets = -28000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R40.htm): 2026-11-12 R40.htm: agree: R40 'Research and development expense' 355, the total
- operating_income: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- interest_expense: not_presented  (R51.htm): 2026-11-12 R51.htm: decided by R51: the 414 is interest paid on securities lending, netted inside revenue ('Securities lending, net'); it is not a financing interest charge; no interest-expense line is printed
- accounts_receivable: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- dividends_paid: not_presented  (R7.htm): 2026-11-12 R7.htm: agree: whole-filing check agrees; nothing printed
- total_debt: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: Class A + Class B at the BS date (R4)
- operating_expenses: mapped us-gaap:OperatingExpenses (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Total operating expenses' is the operating_expenses line, printed 2379000000 = filing XBRL 2379000000; agrees
- total_assets: mapped us-gaap:Assets (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total assets' is the total_assets line, printed 38137000000 = filing XBRL 38137000000; agrees
- accounts_payable: combined us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: 'Accounts payable and accrued expenses' bundles accrued expenses: combined
- stockholders_equity: mapped us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total stockholders’ equity' is the stockholders_equity line, printed 9151000000 = filing XBRL 9151000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Repurchase of Class A common stock' is the share_buybacks line, printed -653000000 = filing XBRL 653000000; agrees
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: CF R7.htm 'Cash paid for interest' is the cash_paid_for_interest line, printed 31000000 = filing XBRL 31000000; agrees
