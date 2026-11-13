# MTB document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000036270-26-000010 (CIK 0000036270, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001193125-16-469957 (CIK 0000036270, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000950170-24-017990 (CIK 0000036270, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001564590-19-003467 (CIK 0000036270, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- companyfacts CIK0000036270.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R136.htm | Segment Information - Information about Company's Segments (Detail) | 9690000000 |  | 9279000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R136.htm 'Segment Information - Information about Company's Segments (Detail)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) / check: hand R136.htm corrected: No total revenue on the face (bank); segment note R136 prints consolidated Total revenue 9,690 / 9,279 (net interest income 6,948 + noninterest income 2,742); filled printed values. |
| cost_of_revenue | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank income statement: interest income, interest expense, provision, noninterest income/expense; no cost of revenue line. |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank: no gross profit line; net interest income is not gross profit. |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total other expense | 5493000000 |  | 5359000000 |  |  | FILING-CHECKED | bank opex = total noninterest expense (no cost of revenue on a bank statement) / check: hand R5.htm corrected: Face prints 'Total other expense' 5,493 / 5,359 on NoninterestExpense (salaries, occupancy, data processing, professional, FDIC, advertising, amortization, other): the bank's total operating expense, excluding interest expense and provision. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1397 tags across all 144 R pages, face and notes) of 0000036270-26-000010; no face row matched / check: hand R5.htm agree |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R5.htm corrected: Bank: no R&D line. |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1397 tags across all 144 R pages, face and notes) of 0000036270-26-000010; no face row matched / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Total interest expense | 3538000000 | 3538000000 | 4174000000 | 4174000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before taxes | 3692000000 | 3692000000 | 3310000000 | 3310000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income taxes | 841000000 | 841000000 | 722000000 | 722000000 | Y | FILING-CHECKED | accn 0000036270-26-000010 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 2851000000 | 2851000000 | 2588000000 | 2588000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Earnings per share, basic (in USD per share) | 17.1 | 17.1 | 14.71 | 14.71 | Y | FILING-CHECKED | accn 0000036270-26-000010 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Earnings per share, diluted (in USD per share) | 17 | 17 | 14.64 | 14.64 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted-average shares outstanding (in shares) | 157875000 | 157875000 | 166479000 | 166479000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted-average shares outstanding (in shares) | 158791000 | 158791000 | 167319000 | 167319000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash and due from banks | 1701000000 | 1701000000 | 1909000000 | 1909000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1397 tags across all 144 R pages, face and notes) of 0000036270-26-000010; no face row matched / check: hand R3.htm agree |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: no inventory line on the balance sheet. |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: unclassified balance sheet, no current assets total. |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Premises and equipment | 1629000000 | 1629000000 | 1705000000 | 1705000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 8465000000 | 8465000000 | 8465000000 | 8465000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 213510000000 | 213510000000 | 208105000000 | 208105000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1397 tags across all 144 R pages, face and notes) of 0000036270-26-000010; no face row matched / check: hand R3.htm agree |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | bank: rule 15, not printed / check: hand R3.htm corrected: Bank: unclassified balance sheet, no current liabilities total. |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 184333000000 | 184333000000 | 179078000000 | 179078000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders’ equity | 29177000000 | 29177000000 | 29027000000 | 29027000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash from operating activities | 3003000000 | 3003000000 | 3610000000 | 3610000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash from investing activities | -6816000000 | -6816000000 | -9746000000 | -9746000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash from financing activities | 1800000000 | 1800000000 | -2882000000 | -2882000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsForProceedsFromProductiveAssets | R7.htm | Capital expenditures, net | -143000000 | 143000000 | -216000000 | 216000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000036270-26-000010 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization of premises and equipment | 323000000 | 323000000 | 316000000 | 316000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R97.htm | Stock-Based Compensation Plans - Additional Information (Detail) | 136000000 | 136000000 | 116000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R97.htm 'Stock-Based Compensation Plans - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R97.htm corrected: No SBC line on CF; note R97 prints Stock-based compensation expense 136 / 116; filled printed values. |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid — common | -899000000 | 899000000 | -895000000 | 895000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchases of treasury stock | -2631000000 | 2631000000 | -396000000 | 396000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid during the period | 3524000000 | 3524000000 | 4319000000 | 4319000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes paid during the period | 529000000 | 529000000 | 236000000 | 236000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000036270-26-000010 R7.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R3.htm | Short-term borrowings + Long-term borrowings (a) | 13060000000 | 13060000000 | 13665000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm corrected: Short-term borrowings 2,149 / 1,060 + Long-term borrowings 10,911 / 12,605 = 13,060 / 13,665; no finance-lease tags in filing; filled FY1. |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1397 tags across all 144 R pages, face and notes) of 0000036270-26-000010; no face row matched / check: hand R4.htm agree |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-469957 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-469957 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 328257000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-469957 R4.htm prints 'Income (loss) before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1674692000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-469957 R4.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 595025000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-469957 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 1079667000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-469957 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 7.22 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-469957 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 7.18 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-469957 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-469957 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-469957 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 1368040000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-469957 R2.htm prints 'Premises and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 666682000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-469957 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 4593112000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-469957 R2.htm prints 'Total assets' on us-gaap:Assets = 122787884000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-469957 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 106614595000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-469957 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 16173289000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 1742408000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Net cash provided (used) by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = 7714282000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -9462007000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Capital expenditures, net' on us-gaap:PaymentsForProceedsFromProductiveAssets = -81936000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Depreciation and amortization of premises and equipment' on us-gaap:DepreciationAndAmortization = 99019000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-469957 R6.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Dividends paid - common' on us-gaap:PaymentsOfDividendsCommonStock = -375017000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-469957 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Interest paid during the year' on us-gaap:InterestPaid = 400329000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-469957 R6.htm prints 'Income taxes paid during the year' on us-gaap:IncomeTaxesPaidNet = 378660000 (FILING-CHECKED)
- revenue: era 10-K 0000950170-24-017990 R4.htm prints 'Revenue from contract with customer' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 409000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000950170-24-017990 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 3109000000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001564590-19-003467 R6.htm prints 'Depreciation and amortization of premises and equipment' on us-gaap:DepreciationAndAmortization = 104864000 (FILING-CHECKED)

## Mismatches (printed vs API)
- revenue: API missing (us-gaap:Revenues)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 18 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 10.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
