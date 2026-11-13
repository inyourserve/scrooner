# FCNCA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000798941-26-000015 (CIK 0000798941, filed 2026-02-24): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000798941-16-000034 (CIK 0000798941, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000798941-24-000018 (CIK 0000798941, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0000798941-22-000014 (CIK 0000798941, era filing): COVER R1.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0000798941.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | component sum | us-gaap:InterestAndDividendIncomeOperating+us-gaap:NoninterestIncome | R5.htm | Noninterest income | 14505000000 |  | 14968000000 |  |  | FILING-CHECKED | bank gross revenue = Total interest income + Total noninterest income (R5); no total revenue line; the 266 row was a dimensioned contract-revenue member / check: hand R5.htm corrected: 266 is one member row of RevenueFromContractWithCustomer (a noninterest-income breakdown), not total revenue; the bank prints Total interest income 11,778 and Total noninterest income 2,727 and no total revenue line -> component sum 14,505 (FY1 12,353 + 2,615 = 14,968). |
| cost_of_revenue | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | bank: not printed; OUT per rule 15 / check: hand R5.htm corrected: Bank income statement has no cost of revenue line (interest income, interest expense, provision, noninterest income/expense). |
| gross_profit | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | bank: not printed; OUT per rule 15 / check: hand R5.htm corrected: Bank: no gross profit line. |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total noninterest expense | 6056000000 |  | 5735000000 |  |  | FILING-CHECKED | bank opex = Total noninterest expense (includes depreciation and maintenance on operating lease equipment 398 + 244) / check: hand R5.htm corrected: Face prints 'Total noninterest expense' 6,056 (FY1 5,735), the bank's total operating expense line, with no COGS inside -> mapped. |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1399 tags across all 154 R pages, face and notes) of 0000798941-26-000015; no face row matched / check: hand R5.htm agree |
| research_and_development | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | bank: not printed; OUT per rule 15 / check: hand R5.htm corrected: Bank: no R&D line. |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1399 tags across all 154 R pages, face and notes) of 0000798941-26-000015; no face row matched / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Total interest expense | 4964000000 | 4964000000 | 5210000000 | 5210000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 2971000000 | 2971000000 | 3592000000 | 3592000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 765000000 | 765000000 | 815000000 | 815000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 2206000000 | 2206000000 | 2777000000 | 2777000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 165.2 | 165.2 | 189.4 | 189.4 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 165.2 | 165.2 | 189.4 | 189.4 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 13002455 | 13002455 | 14341872 | 14341872 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 13002455 | 13002455 | 14342655 | 14342655 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash and due from banks | 801000000 | 801000000 | 814000000 | 814000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1399 tags across all 154 R pages, face and notes) of 0000798941-26-000015; no face row matched / check: hand R3.htm agree |
| inventory | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | bank: not printed; OUT per rule 15 / check: hand R3.htm corrected: Bank: no inventory line. |
| current_assets | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | bank: not printed; OUT per rule 15 / check: hand R3.htm corrected: Bank: unclassified BS, no total current assets. |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Premises and equipment, net | 2447000000 | 2447000000 | 2006000000 | 2006000000 | Y | FILING-CHECKED | accn 0000798941-26-000015 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 346000000 | 346000000 | 346000000 | 346000000 | Y | FILING-CHECKED | accn 0000798941-26-000015 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 229698000000 | 229698000000 | 223720000000 | 223720000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1399 tags across all 154 R pages, face and notes) of 0000798941-26-000015; no face row matched / check: hand R3.htm agree |
| current_liabilities | OUT |  |  |  |  |  |  |  |  | FILING-CHECKED | bank: not printed; OUT per rule 15 / check: hand R3.htm corrected: Bank: unclassified BS, no total current liabilities. |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 207460000000 | 207460000000 | 201492000000 | 201492000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 22238000000 | 22238000000 | 22228000000 | 22228000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 2923000000 | 2923000000 | 2988000000 | 2988000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -5611000000 | -5611000000 | -10155000000 | -10155000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | 2675000000 | 2675000000 | 7073000000 | 7073000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of premises and equipment | -710000000 | 710000000 | -429000000 | 429000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R9.htm | Depreciation, amortization, and accretion, net | 405000000 | 405000000 | 130000000 | 130000000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock based compensation expense | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Cash dividends paid | -161000000 | 161000000 | -158000000 | 158000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of Class A common stock | -3027000000 | 3027000000 | -1648000000 | 1648000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 4810000000 | 4810000000 | 5079000000 | 5079000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes | 315000000 | 315000000 | 763000000 | 763000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000798941-26-000015 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebt | R3.htm | Short-term borrowings + Long-term borrowings | 36008000000 | 36008000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm agree |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 12139159 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) / check: hand R4.htm agree |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000798941-16-000034 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0000798941-16-000034 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 44304000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000798941-16-000034 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 332414000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000798941-16-000034 R4.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 122028000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000798941-16-000034 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 210386000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000798941-16-000034 R4.htm prints 'Net income per share' on us-gaap:EarningsPerShareBasic = 17.52 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000798941-16-000034 R4.htm read; no row matched (auto)
- weighted_basic_shares: FY2015 10-K 0000798941-16-000034 R4.htm prints 'Average shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 12010405 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000798941-16-000034 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000798941-16-000034 R2.htm prints 'Cash and due from banks' on us-gaap:CashAndDueFromBanks = 534086000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000798941-16-000034 R2.htm prints 'Premises and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 1135829000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000798941-16-000034 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 139773000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000798941-16-000034 R2.htm prints 'Total assets' on us-gaap:Assets = 31475934000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000798941-16-000034 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 28603825000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000798941-16-000034 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 2872109000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 233056000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Net cash (used) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -1248003000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Net cash provided (used) by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 944851000 (FILING-CHECKED)
- capex: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Additions to premises and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -89734000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Depreciation' on us-gaap:DepreciationAmortizationAndAccretionNet = 87717000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000798941-16-000034 R8.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -18015000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Interest' on us-gaap:InterestPaid = 46785000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000798941-16-000034 R8.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 136900000 (FILING-CHECKED)
- interest_expense: era 10-K 0000798941-24-000018 R5.htm prints 'Total interest expense' on us-gaap:InterestExpense = 3679000000 (FILING-CHECKED)
- ppe_net: 10-K 0000798941-22-000014 statement not identified (auto)
- dividends_paid: era 10-K 0000798941-22-000014 R9.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -41612000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000798941-22-000014 R9.htm prints 'Interest' on us-gaap:InterestPaid = 62169000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0000798941-22-000014 R9.htm prints 'Income taxes' on us-gaap:IncomeTaxesPaid = 870467000 (FILING-CHECKED)

## Mismatches (printed vs API)
- revenue: API missing (us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 16 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 8.
- Random mapped sample: 2 rows, 0 disagreements (0.0%).
