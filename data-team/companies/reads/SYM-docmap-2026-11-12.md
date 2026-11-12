# SYM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001837240-25-000278 (CIK 0001837240, filed 2025-11-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001837240-23-000189 (CIK 0001837240, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- 10-K 0001193125-22-082751 (CIK 0001837240, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0001837240.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 2246922000 | 2246922000 | 1788179000 | 1788179000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Total cost of revenue | 1824312000 | 1824312000 | 1542513000 | 1542513000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 422610000 | 422610000 | 245666000 | 245666000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 537616000 | 537616000 | 362391000 | 362391000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general, and administrative expenses | 298730000 | 298730000 | 188934000 | 188934000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development expenses | 216013000 | 216013000 | 173457000 | 173457000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating loss | -115006000 | -115006000 | -116725000 | -116725000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (836 tags across all 102 R pages, face and notes) of 0001837240-25-000278; no face row matched |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Loss before income tax and equity method investment | -78943000 | -78943000 | -79683000 | -79683000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax benefit (expense) | 1627000 | -1627000 | -4212000 | 4212000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net loss attributable to common stockholders | -16937000 | -16937000 | -13490000 | -13490000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | -0.16 | -0.16 | -0.14 | -0.14 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | -0.16 | -0.16 | -0.14 | -0.14 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 108670159 | 108670159 | 95697368 | 95697368 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 108670159 | 108670159 | 95697368 | 95697368 | Y | FILING-CHECKED | accn 0001837240-25-000278 R5.htm period ..2025-09-27 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1244993000 | 1244993000 | 727310000 | 727310000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable | 186705000 | 186705000 | 201548000 | 201548000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 164390000 | 164390000 | 106136000 | 106136000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1890328000 | 1890328000 | 1355537000 | 1355537000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 117649000 | 117649000 | 97109000 | 97109000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 59871000 | 59871000 | 0 | 0 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2401197000 | 2401197000 | 1578552000 | 1578552000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 286669000 | 286669000 | 175188000 | 175188000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1729423000 | 1729423000 | 1017146000 | 1017146000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1917984000 | 1917984000 | 1188422000 | 1188422000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 221318000 | 221318000 | 197233000 | 197233000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R3.htm period ..2025-09-27 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 866939000 | 866939000 | -58077000 | -58077000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R9.htm period ..2025-09-27 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | -350742000 | -350742000 | 156481000 | 156481000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R9.htm period ..2025-09-27 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 668000 | 668000 | 371036000 | 371036000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R9.htm period ..2025-09-27 |
| capex | mapped | sym:PaymentsToAcquirePropertyPlantAndEquipmentAndDevelopSoftware | R9.htm | Purchases of property and equipment and capitalization of internal use software development costs | -79030000 |  | -44374000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001837240-25-000278 R9.htm period ..2025-09-27 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 39604000 | 39604000 | 20847000 | 20847000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R9.htm period ..2025-09-27 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 183936000 | 183936000 | 112208000 | 112208000 | Y | FILING-CHECKED | accn 0001837240-25-000278 R9.htm period ..2025-09-27 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (836 tags across all 102 R pages, face and notes) of 0001837240-25-000278; no face row matched |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (836 tags across all 102 R pages, face and notes) of 0001837240-25-000278; no face row matched |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (836 tags across all 102 R pages, face and notes) of 0001837240-25-000278; no face row matched |
| cash_paid_for_income_taxes | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of IncomeTaxesPaidNet, IncomeTaxesPaid in MetaLinks.json (836 tags across all 102 R pages, face and notes) of 0001837240-25-000278; no face row matched |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (836 tags across all 102 R pages, face and notes) of 0001837240-25-000278; no face row matched |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 1181776878 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-09-27; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- sga_expense: era 10-K 0001837240-23-000189 R5.htm prints 'Selling, general, and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 217927000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001837240-23-000189 R5.htm prints 'Loss before income tax' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -212514000 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001837240-23-000189 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 258770000 (FILING-CHECKED)
- sga_expense: era 10-K 0001193125-22-082751 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense =  (FILING-CHECKED)

## Mismatches (printed vs API)
- capex: API missing (sym:PaymentsToAcquirePropertyPlantAndEquipmentAndDevelopSoftware)
