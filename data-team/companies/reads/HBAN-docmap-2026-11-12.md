# HBAN document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000049196-26-000015 (CIK 0000049196, filed 2026-02-13): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000049196-16-000032 (CIK 0000049196, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000049196-24-000020 (CIK 0000049196, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000049196-21-000018 (CIK 0000049196, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000049196.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | component sum | us-gaap:InterestIncomeExpenseNet+us-gaap:NoninterestIncome | R5.htm | Net interest income + Noninterest income | 8166000000 |  | 7385000000 |  |  | FILING-CHECKED | bank revenue = net interest income + total noninterest income (R5 face); R103 contract revenue is a component only / check: hand R5.htm corrected: Row held R103 'Wealth and asset management revenue' 1,562, only the ASC 606 slice of noninterest income. Bank revenue = Net interest income 5,991 + Noninterest income 2,175 = 8,166; FY1 5,345 + 2,040 = 7,385 (no total revenue line printed). |
| cost_of_revenue | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank income statement: interest income/expense, provision, noninterest income/expense; no cost of revenue line. |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank: no gross profit line. |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total noninterest expense | 5015000000 |  | 4562000000 |  |  | FILING-CHECKED | bank opex = total noninterest expense / check: hand R5.htm corrected: Face prints 'Total noninterest expense' 5,015 / 4,562 on NoninterestExpense (personnel, data processing, equipment, occupancy, professional, marketing, FDIC, amortization, other): the bank's operating expense, excluding interest expense and provision. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1488 tags across all 151 R pages, face and notes) of 0000049196-26-000015; no face row matched / check: hand R5.htm agree |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank: no R&D line. |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1488 tags across all 151 R pages, face and notes) of 0000049196-26-000015; no face row matched / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Total interest expense | 4319000000 | 4319000000 | 4576000000 | 4576000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 2688000000 | 2688000000 | 2403000000 | 2403000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 459000000 | 459000000 | 443000000 | 443000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Huntington | 2211000000 | 2211000000 | 1940000000 | 1940000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income—basic (in USD per share) | 1.41 | 1.41 | 1.24 | 1.24 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income—diluted (in USD per share) | 1.39 | 1.39 | 1.22 | 1.22 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Average common shares—basic (in shares) | 1478945000 | 1478945000 | 1451421000 | 1451421000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Average common shares—diluted (in shares) | 1504836000 | 1504836000 | 1476442000 | 1476442000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash and due from banks | 1783000000 | 1783000000 | 1685000000 | 1685000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank; only 'Accrued income and other receivables' (interest receivable) is printed, excluded by rule 9 / check: hand R3.htm corrected: Row keyed on hban:InterestAndOtherReceivables 'Accrued income and other receivables' 2,621: accrued interest receivable on a bank, never AR (rule 9); no trade receivables line. |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: no inventory line. |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: unclassified balance sheet. |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Premises and equipment | 1321000000 | 1321000000 | 1066000000 | 1066000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5997000000 | 5997000000 | 5561000000 | 5561000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 225106000000 | 225106000000 | 204230000000 | 204230000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1488 tags across all 151 R pages, face and notes) of 0000049196-26-000015; no face row matched / check: hand R3.htm agree |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: unclassified balance sheet. |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 200727000000 | 200727000000 | 184448000000 | 184448000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Huntington shareholders’ equity | 24342000000 | 24342000000 | 19740000000 | 19740000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 2482000000 | 2482000000 | 1836000000 | 1836000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -6347000000 | -6347000000 | -12119000000 | -12119000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by financing activities | 4513000000 | 4513000000 | 13001000000 | 13001000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of premises and equipment | -267000000 | 267000000 | -143000000 | 143000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R9.htm | Depreciation, amortization, and accretion | 762000000 | 762000000 | 622000000 | 622000000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-based compensation expense | 113000000 | 113000000 | 106000000 | 106000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid on common stock | -908000000 | 908000000 | -903000000 | 903000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | only preferred stock repurchase/redemption printed (PaymentsForRepurchaseOfPreferredStockAndPreferenceStock); not a common buyback / check: hand R9.htm corrected: Row keyed on 'Repurchase/redemption of preferred stock' 0 / (410): preferred, not common; no common share repurchase line in financing. |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 4267000000 | 4267000000 | 4547000000 | 4547000000 | Y | FILING-CHECKED | accn 0000049196-26-000015 R9.htm period ..2025-12-31 / check: hand R9.htm agree |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid | 274000000 | 274000000 | 123000000 | 123000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000049196-26-000015 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R3.htm | Short-term borrowings + Long-term debt | 18482000000 | 18482000000 | 16573000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm corrected: Short-term borrowings 1,261 / 199 + Long-term debt 17,221 / 16,374 = 18,482 / 16,573; no finance-lease tags; filled FY1. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common shares outstanding (in shares) | 1567732506 | 1567732506 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row / check: hand R3.htm agree |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000049196-16-000032 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 163784000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 913605000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 220648000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 692957000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Net income - basic (in USD per share)' on us-gaap:EarningsPerShareBasic = 0.82 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Net income - diluted (in USD per share)' on us-gaap:EarningsPerShareDiluted = 0.81 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Average common shares—basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 803412000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000049196-16-000032 R4.htm prints 'Average common shares—diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 817129000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000049196-16-000032 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 847156000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000049196-16-000032 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0000049196-16-000032 R2.htm prints 'Premises and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 620540000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000049196-16-000032 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 676869000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000049196-16-000032 R2.htm prints 'Total assets' on us-gaap:Assets = 71044551000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000049196-16-000032 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 64449945000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000049196-16-000032 R2.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquity = 6594606000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Net cash provided by (used for) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1033362000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Net cash provided by (used for) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -4928654000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Net cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 3521883000 (FILING-CHECKED)
- capex: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Purchases of premises and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -93097000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 341281000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Share-based compensation expense' on us-gaap:ShareBasedCompensation = 51415000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Dividends paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -192518000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -251844000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Interest paid' on us-gaap:InterestPaid = 150403000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000049196-16-000032 R8.htm prints 'Income taxes paid (refunded)' on us-gaap:IncomeTaxesPaidNet = 153590000 (FILING-CHECKED)
- interest_expense: era 10-K 0000049196-24-000020 R5.htm prints 'Total interest expense' on us-gaap:InterestExpense = 3477000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000049196-21-000018 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 972000000 (FILING-CHECKED)
- share_buybacks: era 10-K 0000049196-21-000018 R8.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -92000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_receivable: API missing (hban:InterestAndOtherReceivables)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 16 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 11.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
