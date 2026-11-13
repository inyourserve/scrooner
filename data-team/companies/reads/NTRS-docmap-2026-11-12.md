# NTRS document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000073124-26-000016 (CIK 0000073124, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000073124-16-000324 (CIK 0000073124, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000073124-19-000088 (CIK 0000073124, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000073124-24-000073 (CIK 0000073124, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0000073124.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Trust, Investment and Other Servicing Fees | 5017800000 | 5017800000 | 4727800000 | 4727800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| cost_of_revenue | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank income statement: noninterest income, interest income/expense, provision, noninterest expense; no cost of revenue line. |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank: no gross profit line. |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total Noninterest Expense | 5754400000 |  | 5633900000 |  |  | FILING-CHECKED | bank opex = total noninterest expense / check: hand R5.htm corrected: Face prints 'Total Noninterest Expense' 5,754.4 / 5,633.9 on NoninterestExpense (compensation, outside services, equipment and software, occupancy, other): the bank's operating expense, excluding interest expense and provision. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1537 tags across all 180 R pages, face and notes) of 0000073124-26-000016; no face row matched / check: hand R5.htm agree |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank: no R&D line. |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1537 tags across all 180 R pages, face and notes) of 0000073124-26-000016; no face row matched / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Interest Expense | 6213600000 | 6213600000 | 7585200000 | 7585200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before Income Taxes | 2339500000 | 2339500000 | 2659500000 | 2659500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for Income Taxes | 602600000 | 602600000 | 628400000 | 628400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME | 1736900000 | 1736900000 | 2031100000 | 2031100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net Income - Basic (in dollars per share) | 8.78 | 8.78 | 9.8 | 9.8 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net Income - Diluted (in dollars per share) | 8.74 | 8.74 | 9.77 | 9.77 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Average Number of Common Shares Outstanding - Basic (in shares) | 191358026 | 191358026 | 201263646 | 201263646 | Y | FILING-CHECKED | accn 0000073124-26-000016 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Average Number of Common Shares Outstanding - Diluted (in shares) | 192246525 | 192246525 | 201870105 | 201870105 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash and Due from Banks | 5873100000 | 5873100000 | 4677200000 | 4677200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1537 tags across all 180 R pages, face and notes) of 0000073124-26-000016; no face row matched / check: hand R3.htm agree |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: no inventory line. |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: unclassified balance sheet. |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Buildings and Equipment | 464600000 | 464600000 | 490300000 | 490300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 712900000 | 712900000 | 694900000 | 694900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 177132700000 | 177132700000 | 155508400000 | 155508400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1537 tags across all 180 R pages, face and notes) of 0000073124-26-000016; no face row matched / check: hand R3.htm agree |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: unclassified balance sheet. |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 164174800000 | 164174800000 | 142720000000 | 142720000000 | Y | FILING-CHECKED | accn 0000073124-26-000016 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Stockholders’ Equity | 12957900000 | 12957900000 | 12788400000 | 12788400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net Cash Provided by (Used in) Operating Activities | 5533500000 | 5533500000 | -486000000 | -486000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net Cash (Used in) Provided by Investing Activities | -20169900000 | -20169900000 | -2563500000 | -2563500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net Cash Provided by (Used in) Financing Activities | 15175900000 | 15175900000 | 3439500000 | 3439500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of Buildings and Equipment | -74000000 | 74000000 | -101500000 | 101500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R9.htm | Depreciation and Amortization | 779100000 | 779100000 | 716800000 | 716800000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R144.htm | Share-Based Compensation Plans - Total Compensation Expense for Share-Based Compensation Arrangements to Employees (Deta | 126500000 | 126500000 | 119400000 |  | Y | FILING-CHECKED | not on the face statement; shown in R144.htm 'Share-Based Compensation Plans - Total Compensation Expense for Share-Based Comp' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R144.htm corrected: No SBC line on CF; note R144 prints Total Share-Based Compensation Expense 126.5 / 119.4 (first, total row); filled printed values. |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash Dividends Paid on Common Stock | -591600000 | 591600000 | -602300000 | 602300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Treasury Stock Purchased | -1273500000 | 1273500000 | -937800000 | 937800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest Paid | 6223700000 | 6223700000 | 7610300000 | 7610300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income Taxes Paid | 426800000 | 426800000 | 268600000 | 268600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000073124-26-000016 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:FederalFundsPurchased+us-gaap:SecuritiesSoldUnderAgreementsToRepurchase+us-gaap:OtherBorrowings+us-gaap:SeniorNotes+ntrs:SubordinatedDebtAndLongTermFederalHomeLoanBankAdvances | R3.htm | Federal funds purchased + Repos + Other borrowings + Senior notes + Long-term debt | 16427500000 |  | 15993500000 |  |  | FILING-CHECKED | all face borrowing lines; Long-Term Debt is extension ntrs:SubordinatedDebtAndLongTermFederalHomeLoanBankAdvances; fed funds purchased and repos included as short-term borrowings (bank); no finance-lease tags / check: hand R3.htm corrected: Row held only Senior Notes 3,351.5. Face also prints borrowings: Federal Funds Purchased 2,141.1 / 2,159.5, Securities Sold Under Agreements to Repurchase 292.2 / 462.0, Other Borrowings 7,158.3 / 6,521.0 and Long-Term Debt (subordinated + FHLB, ntrs extension) 3,484.4 / 4,081.3; total 16,427.5 / 15,993.5. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 186337588 | 186337588 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000073124-16-000324 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Interest Expense' on us-gaap:InterestExpense = 153900000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Income before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1465000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Provision for Income Taxes' on us-gaap:IncomeTaxExpenseBenefit = 491200000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000073124-16-000324 R4.htm prints 'NET INCOME' on us-gaap:NetIncomeLoss = 973800000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Net Income - Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 4.03 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Net Income - Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.99 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Average Number of Common Shares Outstanding - Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 232279849 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000073124-16-000324 R4.htm prints 'Average Number of Common Shares Outstanding - Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 234221729 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000073124-16-000324 R2.htm prints 'Cash and Due from Banks' on us-gaap:CashAndDueFromBanks = 6444600000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000073124-16-000324 R2.htm prints 'Buildings and Equipment' on us-gaap:PropertyPlantAndEquipmentNet = 446900000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000073124-16-000324 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 526400000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000073124-16-000324 R2.htm prints 'Total Assets' on us-gaap:Assets = 116749600000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000073124-16-000324 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 108043700000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000073124-16-000324 R2.htm prints 'Total Stockholders’ Equity' on us-gaap:StockholdersEquity = 8705900000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1834400000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Net Cash Used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -6900700000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Net Cash Provided by Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 8534100000 (FILING-CHECKED)
- capex: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Purchases of Buildings and Equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -98500000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000073124-16-000324 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000073124-16-000324 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Cash Dividends Paid on Common Stock' on us-gaap:PaymentsOfDividendsCommonStock = -321400000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Treasury Stock Purchased' on us-gaap:PaymentsForRepurchaseOfCommonStock = -496900000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Interest Paid' on us-gaap:InterestPaid = 161600000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000073124-16-000324 R7.htm prints 'Income Taxes Paid' on us-gaap:IncomeTaxesPaid = 390000000 (FILING-CHECKED)
- revenue: era 10-K 0000073124-19-000088 R4.htm prints 'Revenue from contract with customer' on us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax = 3753700000 (FILING-CHECKED)
- interest_expense: era 10-K 0000073124-24-000073 R5.htm prints 'Interest Expense' on us-gaap:InterestExpense = 5343000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 15 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 9.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
