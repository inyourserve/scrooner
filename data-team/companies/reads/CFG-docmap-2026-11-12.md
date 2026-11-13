# CFG document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000759944-26-000028 (CIK 0000759944, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0000759944-16-000099 (CIK 0000759944, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0000759944-24-000039 (CIK 0000759944, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000759944-21-000034 (CIK 0000759944, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0000759944.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R150.htm | BUSINESS SEGMENTS - Schedule of Business Operating Segments (Details) | 8247000000 | 8247000000 | 7809000000 |  | Y | FILING-CHECKED | not on face IS; R150 Business Segments consolidated Total revenue (net interest income + noninterest income) 8,247 / 7,809 $M / check: hand R150.htm corrected: Face IS has no total revenue line; R150 segment note consolidated 'Total revenue' (us-gaap:Revenues) = NII 5,853 + noninterest income 2,394 = 8,247; FY1 7,809 $M. |
| cost_of_revenue | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: cost of revenue not applicable (rule 15) / check: hand R5.htm corrected: Bank; no cost-of-revenue line printed: OUT per rule 15. |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: gross profit not applicable (rule 15) / check: hand R5.htm corrected: Bank; no gross profit line printed: OUT per rule 15. |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total noninterest expense | 5311000000 |  | 5234000000 |  |  | FILING-CHECKED | bank: consolidated total noninterest expense on face IS; R152 OperatingExpenses is parent-company-only and must not be used / check: hand R5.htm corrected: Machine took R152 PARENT-ONLY 'Total operating expense' (417); the consolidated face IS prints Total noninterest expense 5,311 / 5,234 (us-gaap:NoninterestExpense), the bank's operating expense total. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1367 tags across all 153 R pages, face and notes) of 0000759944-26-000028; no face row matched / check: hand R5.htm agree |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: R&D not applicable (rule 15) / check: hand R5.htm corrected: Bank; no R&D line: OUT per rule 15. |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1367 tags across all 153 R pages, face and notes) of 0000759944-26-000028; no face row matched / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Total interest expense | 3810000000 | 3810000000 | 4553000000 | 4553000000 | Y | FILING-CHECKED | accn 0000759944-26-000028 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income tax expense | 2328000000 | 2328000000 | 1888000000 | 1888000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 497000000 | 497000000 | 379000000 | 379000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | NET INCOME | 1831000000 | 1831000000 | 1509000000 | 1509000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings (in dollars per share) | 3.9 | 3.9 | 3.05 | 3.05 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings (in dollars per share) | 3.86 | 3.86 | 3.03 | 3.03 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 433173162 | 433173162 | 450678038 | 450678038 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 436890731 | 436890731 | 453510245 | 453510245 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash and due from banks | 1464000000 | 1464000000 | 1409000000 | 1409000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1367 tags across all 153 R pages, face and notes) of 0000759944-26-000028; no face row matched / check: hand R3.htm agree |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: inventory not applicable (rule 15) / check: hand R3.htm corrected: Bank; no inventory line: OUT per rule 15. |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: unclassified balance sheet (rule 15) / check: hand R3.htm corrected: Bank unclassified BS; no current assets subtotal: OUT per rule 15. |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Premises and equipment, net | 915000000 | 915000000 | 875000000 | 875000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 8187000000 | 8187000000 | 8187000000 | 8187000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 226351000000 | 226351000000 | 217521000000 | 217521000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1367 tags across all 153 R pages, face and notes) of 0000759944-26-000028; no face row matched / check: hand R3.htm agree |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: unclassified balance sheet (rule 15) / check: hand R3.htm corrected: Bank unclassified BS; no current liabilities subtotal: OUT per rule 15. |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | TOTAL LIABILITIES | 200034000000 | 200034000000 | 193267000000 | 193267000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | TOTAL STOCKHOLDERS’ EQUITY | 26317000000 | 26317000000 | 24254000000 | 24254000000 | Y | FILING-CHECKED | accn 0000759944-26-000028 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net change due to operating activities | 2211000000 | 2211000000 | 2001000000 | 2001000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net change due to investing activities | -5967000000 | -5967000000 | 2987000000 | 2987000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net change due to financing activities | 5882000000 | 5882000000 | -6015000000 | -6015000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| capex | combined | us-gaap:PaymentsForProceedsFromProductiveAssets | R8.htm | Capital expenditures, net | -174000000 | 174000000 | -122000000 | 122000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | face CF 'Capital expenditures, net' (PaymentsForProceedsFromProductiveAssets) is net of proceeds from disposals; no gross capex line / check: hand R8.htm corrected: Only line is 'Capital expenditures, net' (174) / (122) under PaymentsForProceedsFromProductiveAssets, i.e. net of disposal proceeds: combined, not gross capex. |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R8.htm | Depreciation, amortization, and accretion | 478000000 | 478000000 | 498000000 | 498000000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R8.htm | Share-based compensation | 120000000 | 120000000 | 97000000 | 97000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid to common stockholders | -755000000 | 755000000 | -769000000 | 769000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury stock purchased | -600000000 | 600000000 | -1050000000 | 1050000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest paid | 4040000000 | 4040000000 | 4375000000 | 4375000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000759944-26-000028 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R142.htm | INCOME TAXES - Income Taxes Paid (Details) | 151000000 | 151000000 | 208000000 |  | Y | FILING-CHECKED | not on face CF; R142 Income Taxes Paid Total 151 / 208 $M / check: hand R142.htm corrected: R142 Total income taxes paid 151 / 208 $M. |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R3.htm | Short-term borrowed funds + Long-term borrowed funds | 11282000000 | 11282000000 | 12401000000 |  | Y | FILING-CHECKED | ST borrowed funds + LT borrowed funds; deposits excluded; no finance leases in filing / check: hand R3.htm corrected: Short-term borrowed funds 58 + Long-term borrowed funds 11,224 = 11,282 (agrees); FY1 blank: 0 + 12,401 = 12,401. No finance lease tags in the filing; deposits excluded. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 429242174 | 429242174 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000759944-16-000099 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000759944-16-000099 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 452000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Income (loss) before income tax expense (benefit)' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1263000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Income tax expense (benefit)' on us-gaap:IncomeTaxExpenseBenefit = 423000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000759944-16-000099 R4.htm prints 'NET INCOME (LOSS)' on us-gaap:NetIncomeLoss = 840000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Basic earnings (loss) (in Dollars per Share)' on us-gaap:EarningsPerShareBasic = 1.55 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Diluted earnings (loss) (in Dollars per Share)' on us-gaap:EarningsPerShareDiluted = 1.55 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Basic (in Shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 535599731 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000759944-16-000099 R4.htm prints 'Diluted (in Shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 538220898 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000759944-16-000099 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 1099000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000759944-16-000099 R2.htm prints 'Premises and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 595000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000759944-16-000099 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 6876000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000759944-16-000099 R2.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 138208000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000759944-16-000099 R2.htm prints 'TOTAL LIABILITIES' on us-gaap:Liabilities = 118562000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000759944-16-000099 R2.htm prints 'TOTAL STOCKHOLDERS’ EQUITY' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 19646000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1229000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -5905000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 4485000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Purchases' on us-gaap:PaymentsToAcquireProductiveAssets = -121000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Depreciation, amortization and accretion' on us-gaap:DepreciationAmortizationAndAccretionNet = 471000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Share-based compensation' on us-gaap:AllocatedShareBasedCompensationExpense = 24000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Dividends declared and paid to RBS' on us-gaap:PaymentsOfDividends = -71000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Treasury stock purchased' on us-gaap:PaymentsForRepurchaseOfCommonStock = -500000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Interest paid' on us-gaap:InterestPaid = 454000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000759944-16-000099 R9.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 157000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000759944-24-000039 R5.htm prints 'Total interest expense' on us-gaap:InterestExpense = 3963000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000759944-21-000034 R4.htm prints 'Income before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1298000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:OperatingExpenses)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 17 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 11.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
