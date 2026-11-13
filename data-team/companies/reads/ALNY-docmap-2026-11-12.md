# ALNY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-007497 (CIK 0001178670, filed 2026-02-12): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0001193125-16-462538 (CIK 0001178670, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- 10-K 0001564590-18-002152 (CIK 0001178670, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, CI R4.htm, CF R7.htm
- 10-K 0001178670-24-000008 (CIK 0001178670, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- companyfacts CIK0001178670.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 3713937000 | 3713937000 | 2248243000 | 2248243000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 677166000 | 677166000 | 306513000 | 306513000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (935 tags across all 103 R pages, face and notes) of 0001628280-26-007497; no face row matched / check: hand R5.htm agree |
| operating_expenses | component sum | us-gaap:ResearchAndDevelopmentExpense+us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Research and development + Selling, general and administrative | 2530488000 |  | 2101758000 |  |  | FILING-CHECKED | every face line after the two cost-of-revenue lines and before operating income; ties to revenue - COGS - cost of collaborations - operating income / check: hand R5.htm corrected: 'Total operating costs and expenses' 3,212,359 includes Cost of goods sold 677,166 and Cost of collaborations and royalties 4,705; opex = R&D 1,319,775 + SG&A 1,210,713 = 2,530,488 = 3,713,937 - 677,166 - 4,705 - 501,578; FY1 1,126,232 + 975,526 = 2,101,758 (ties likewise). |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 1210713000 | 1210713000 | 975526000 | 975526000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 1319775000 | 1319775000 | 1126232000 | 1126232000 | Y | FILING-CHECKED | accn 0001628280-26-007497 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income (loss) from operations | 501578000 | 501578000 | -176885000 | -176885000 | Y | FILING-CHECKED | accn 0001628280-26-007497 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -252627000 | 252627000 | -141858000 | 141858000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before income taxes | 323152000 | 323152000 | -377375000 | -377375000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | (Provision for) benefit from income taxes | -9405000 | 9405000 | 99218000 | -99218000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) | 313747000 | 313747000 | -278157000 | -278157000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income (loss) per common share, basic (in dollars per share) | 2.39 | 2.39 | -2.18 | -2.18 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income (loss) per common share, diluted (in dollars per share) | 2.33 | 2.33 | -2.18 | -2.18 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average common shares, basic (in shares) | 131004000 | 131004000 | 127651000 | 127651000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average common shares, diluted (in shares) | 134684000 | 134684000 | 127651000 | 127651000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1657250000 | 1657250000 | 966428000 | 966428000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 777567000 | 777567000 | 405308000 | 405308000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 82719000 | 82719000 | 78509000 | 78509000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4050662000 | 4050662000 | 3295285000 | 3295285000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 513147000 | 513147000 | 502784000 | 502784000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (935 tags across all 103 R pages, face and notes) of 0001628280-26-007497; no face row matched / check: hand R3.htm agree |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4966331000 | 4966331000 | 4239983000 | 4239983000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 115721000 | 115721000 | 88415000 | 88415000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1466349000 | 1466349000 | 1186272000 | 1186272000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4177155000 | 4177155000 | 4172895000 | 4172895000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 789176000 | 789176000 | 67088000 | 67088000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by (used in) operating activities | 524080000 | 524080000 | -8312000 | -8312000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | 436329000 | 436329000 | -116840000 | -116840000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used in) provided by financing activities | -305190000 | -305190000 | 294159000 | 294159000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property, plant and equipment | -58697000 | 58697000 | -34277000 | 34277000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-007497 R7.htm period ..2025-12-31 / check: hand R7.htm agree |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation and amortization | 55658000 | 55658000 | 56670000 | 56670000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0001628280-26-007497 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 348235000 | 348235000 | 272084000 | 272084000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (935 tags across all 103 R pages, face and notes) of 0001628280-26-007497; no face row matched / check: hand R7.htm agree |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (935 tags across all 103 R pages, face and notes) of 0001628280-26-007497; no face row matched / check: hand R7.htm agree |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 218707000 | 218707000 | 67578000 | 67578000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-007497 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R98.htm | INCOME TAXES - Schedule of Cash Taxes Paid (Details) | 15088000 | 15088000 |  |  | Y | FILING-CHECKED | R98 prints FY0 only (15,088 $K); FY1 not printed on this page / check: hand R98.htm corrected: R98 prints Income taxes, net of amounts refunded 15,088 ($K) for 2025 only (new disclosure; no prior-year column); filled FY0. |
| total_debt | mapped | us-gaap:ConvertibleDebtNoncurrent | R3.htm | Convertible debt | 1007784000 |  | 1024621000 |  |  | FILING-CHECKED | single face debt line; royalty/development funding liabilities (220,068 + 1,470,341) excluded as non-borrowing / check: hand R3.htm corrected: Face prints 'Convertible debt' 1,007,784 / 1,024,621 on ConvertibleDebtNoncurrent (ties to R71 notes 647.2M + 360.5M); no current debt, no finance-lease tags; liabilities from sale of future royalties are not borrowings and excluded. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 132376000 | 132376000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0001193125-16-462538 statement not identified (auto)
- cost_of_revenue: 10-K 0001193125-16-462538 statement not identified (auto)
- operating_expenses: 10-K 0001193125-16-462538 statement not identified (auto)
- sga_expense: 10-K 0001193125-16-462538 statement not identified (auto)
- research_and_development: 10-K 0001193125-16-462538 statement not identified (auto)
- operating_income: 10-K 0001193125-16-462538 statement not identified (auto)
- interest_expense: 10-K 0001193125-16-462538 statement not identified (auto)
- income_before_tax: 10-K 0001193125-16-462538 statement not identified (auto)
- income_tax_expense: 10-K 0001193125-16-462538 statement not identified (auto)
- net_income: 10-K 0001193125-16-462538 statement not identified (auto)
- basic_eps: 10-K 0001193125-16-462538 statement not identified (auto)
- diluted_eps: 10-K 0001193125-16-462538 statement not identified (auto)
- weighted_basic_shares: 10-K 0001193125-16-462538 statement not identified (auto)
- weighted_diluted_shares: 10-K 0001193125-16-462538 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 180895000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Billed and unbilled collaboration receivables' on us-gaap:ReceivablesNetCurrent = 8298000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-462538 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1105388000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 27812000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Total assets' on us-gaap:Assets = 1386510000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 16787000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 62099000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 121796000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-462538 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 1264714000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -189140000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -321321000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 616177000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -12950000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 19050000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Non-cash stock-based compensation' on us-gaap:ShareBasedCompensation = 45783000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-462538 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-462538 R7.htm prints 'Net (cash paid for income taxes) cash proceeds from income tax refunds' on us-gaap:IncomeTaxesPaidNet = -66000 (FILING-CHECKED)
- operating_expenses: 10-K 0001564590-18-002152 statement not identified (auto)
- sga_expense: 10-K 0001564590-18-002152 statement not identified (auto)
- accounts_receivable: era 10-K 0001564590-18-002152 R2.htm prints 'Billed and unbilled collaboration receivables' on us-gaap:ReceivablesNetCurrent = 34002000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-002152 R7.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = -382786000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-002152 R7.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -290361000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-002152 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = 1124891000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001564590-18-002152 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 13367000 (FILING-CHECKED)
- interest_expense: era 10-K 0001178670-24-000008 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -121221000 (FILING-CHECKED)

## Mismatches (printed vs API)
- total_debt: API missing (us-gaap:LongTermDebt)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 10 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 3.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
