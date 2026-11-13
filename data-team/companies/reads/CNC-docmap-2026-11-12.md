# CNC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001071739-26-000049 (CIK 0001071739, filed 2026-02-17): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001071739-16-000192 (CIK 0001071739, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- 10-K 0001071739-18-000030 (CIK 0001071739, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001071739-24-000037 (CIK 0001071739, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001071739.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 194777000000 | 194777000000 | 163071000000 | 163071000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of services | 2670000000 | 2670000000 | 2729000000 | 2729000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R100.htm | Segment Information (Details) | 14209000000 | 14209000000 | 17069000000 |  | Y | FILING-CHECKED | note-only: R100 'Segment gross margin' consolidated total (premium and service revenues less medical costs and cost of services; premium tax revenue excluded) / check: hand R100.htm corrected: R100 segment note prints consolidated 'Segment gross margin' (GrossProfit) 14,209 / 17,069 = sum of the four segments (5,690+2,983+5,101+435) = premium and service revenues 174,581 - medical costs 157,702 - cost of services 2,670 (excludes premium tax); not on the face; values were blank. |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 202400000000 | 202400000000 | 159896000000 | 159896000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001071739-26-000049 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 12904000000 | 12904000000 | 12400000000 | 12400000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | insurer (managed care): R&D not printed -> OUT / check: hand R5.htm corrected: Health insurer; no R&D line on R5; per the bank/insurer rule an unprinted R&D is OUT, not not_presented. |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Earnings (loss) from operations | -7623000000 | -7623000000 | 3175000000 | 3175000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -678000000 | 678000000 | -702000000 | 702000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001071739-26-000049 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Earnings (loss) before income tax | -6728000000 | -6728000000 | 4257000000 | 4257000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax (benefit) expense | -51000000 | -51000000 | 963000000 | 963000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net earnings (loss) attributable to Centene Corporation | -6674000000 | -6674000000 | 3305000000 | 3305000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings (loss) per common share (in usd per share) | -13.53 | -13.53 | 6.33 | 6.33 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings (loss) per common share (in usd per share) | -13.53 | -13.53 | 6.31 | 6.31 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 493116000 | 493116000 | 521790000 | 521790000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 493116000 | 493116000 | 523744000 | 523744000 | Y | FILING-CHECKED | accn 0001071739-26-000049 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 17888000000 | 17888000000 | 14063000000 | 14063000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:PremiumsAndOtherReceivablesNet | R3.htm | Premium and trade receivables | 18105000000 | 18105000000 | 19713000000 | 19713000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001071739-26-000049 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | insurer (managed care): inventory not printed -> OUT / check: hand R3.htm corrected: Health insurer; no inventory line on R3; per the bank/insurer rule this is OUT, not not_presented. |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 40370000000 | 40370000000 | 37999000000 | 37999000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, software and equipment, net | 2037000000 | 2037000000 | 2067000000 | 2067000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 10835000000 | 10835000000 | 17558000000 | 17558000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 76747000000 | 76747000000 | 82445000000 | 82445000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 13774000000 | 13774000000 | 13174000000 | 13174000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 36696000000 | 36696000000 | 34261000000 | 34261000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 56691000000 | 56691000000 | 55935000000 | 55935000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Centene stockholders' equity | 19953000000 | 19953000000 | 26410000000 | 26410000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 5088000000 | 5088000000 | 154000000 | 154000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | 472000000 | 472000000 | -1052000000 | -1052000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -1621000000 | -1621000000 | -2406000000 | -2406000000 | Y | FILING-CHECKED | accn 0001071739-26-000049 R9.htm period ..2025-12-31 / check: hand R9.htm agree |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -767000000 | 767000000 | -644000000 | 644000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 1275000000 | 1275000000 | 1241000000 | 1241000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock compensation expense | 204000000 | 204000000 | 212000000 | 212000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (895 tags across all 105 R pages, face and notes) of 0001071739-26-000049; no face row matched / check: hand R9.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Common stock repurchases | -475000000 | 475000000 | -3124000000 | 3124000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 647000000 | 647000000 | 688000000 | 688000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid, net | 448000000 | 448000000 | 1002000000 | 1002000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001071739-26-000049 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of long-term debt + Long-term debt | 17401000000 | 17401000000 | 18533000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) / check: hand R3.htm corrected: R3 Current portion of LTD 50 + Long-term debt 17,351 = 17,401; no finance-lease tags; FY24 110 + 18,423 = 18,533 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 491757000 | 491757000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Total revenues' on us-gaap:Revenues = 22760000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Cost of services' on us-gaap:CostOfServices = 1621000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001071739-16-000192 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 22055000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001071739-16-000192 R4.htm prints 'General and administrative expenses' on us-gaap:GeneralAndAdministrativeExpense = 1826000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Earnings from operations' on us-gaap:OperatingIncomeLoss = 705000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -43000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Earnings from continuing operations, before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 697000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 339000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Net earnings attributable to Centene Corporation' on us-gaap:NetIncomeLoss = 355000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Basic earnings per common share (in usd per share)' on us-gaap:EarningsPerShareBasic = 2.98 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Diluted earnings per common share (in usd per share)' on us-gaap:EarningsPerShareDiluted = 2.88 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 119100744 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001071739-16-000192 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 123066370 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1760000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Premium and related receivables' on us-gaap:PremiumsAndOtherReceivablesNet = 1279000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3605000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Property, software and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 518000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 842000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Total assets' on us-gaap:Assets = 7339000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 976000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 3629000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 5015000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001071739-16-000192 R2.htm prints 'Total Centene stockholders’ equity' on us-gaap:StockholdersEquity = 2157000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 658000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -813000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 305000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -150000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 111000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Stock compensation expense' on us-gaap:ShareBasedCompensation = 71000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Common stock repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -53000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Interest paid' on us-gaap:InterestPaidNet = 55000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001071739-16-000192 R9.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaidNet = 328000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001071739-18-000030 R4.htm prints 'Cost of services' on us-gaap:CostOfServices = 1847000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001071739-24-000037 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -725000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 10 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 4.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
