# CACC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000885550-26-000047 (CIK 0000885550, filed 2026-02-13): COVER R1.htm, BS R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000885550-16-000083 (CIK 0000885550, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000885550-23-000023 (CIK 0000885550, era filing): COVER R1.htm, BS R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0000885550-21-000034 (CIK 0000885550, era filing): COVER R1.htm, BS R2.htm, IS R3.htm, CI R4.htm, CF R6.htm
- companyfacts CIK0000885550.json (one call); submissions CIK0000885550.json (SIC 6141).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | Total revenue | 2317200000 | 2317200000 | 2162400000 | 2162400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| cost_of_revenue | OUT |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the lender_nonbank template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: not_presented |
| gross_profit | OUT |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the lender_nonbank template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: not_presented |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R4.htm | Operating Expenses | 599900000 | 599900000 | 501500000 | 501500000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line; no cost-of-revenue line above it / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R4.htm | General and administrative + Sales and marketing | 262800000 | 262800000 | 192300000 | 192300000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| research_and_development | OUT |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the lender_nonbank template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: not_presented |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Face R4 has an 'Operating Expenses' subtotal (599.9M) but no operating income line; it goes from total costs and expenses to income before income taxes. / pages opened: R90, R21, R60, R4 |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest | 462900000 | 462900000 | 419500000 | 419500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest, Total | 565400000 | 565400000 | 329500000 | 329500000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Effective tax rate, amount | 141500000 | 141500000 | 81600000 | 81600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 423900000 | 423900000 | 247900000 | 247900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (in usd per share) | 37.02 | 37.02 | 20.12 | 20.12 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (in usd per share) | 36.38 | 36.38 | 19.88 | 19.88 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 11451578 | 11451578 | 12323261 | 12323261 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 11650773 | 11650773 | 12469283 | 12469283 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 22800000 | 22800000 | 343700000 | 343700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:IncomeTaxReceivable | R3.htm | Income taxes receivable | 67200000 | 67200000 | 4200000 | 4200000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the lender_nonbank template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: not_presented |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the lender_nonbank template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: not_presented |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 12600000 | 12600000 | 14700000 | 14700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Balance sheet R3 has no goodwill line and no goodwill tag exists in the filing. / pages opened: R3 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total Assets | 8631700000 | 8631700000 | 8854600000 | 8854600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued liabilities | 400200000 | 400200000 | 315800000 | 315800000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the lender_nonbank template group (group_assignment_v2.csv; Dhairya ruling 2026-11-13, SYF CA/CL); was: not_presented |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total Liabilities | 7108100000 | 7108100000 | 7105000000 | 7105000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Shareholders' Equity | 1523600000 | 1523600000 | 1749600000 | 1749600000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1054600000 | 1054600000 | 1137900000 | 1137900000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -674300000 | -674300000 | -1721100000 | -1721100000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by financing activities | -724600000 | -724600000 | 957300000 | 957300000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchases of property and equipment | -1600000 | 1600000 | -1800000 | 1800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R7.htm | Depreciation | 3600000 | 3600000 | 6700000 | 6700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation | 50700000 | 50700000 | 45000000 | 45000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Credit Acceptance pays no dividends; the equity statement shows only repurchases and stock-comp activity. / pages opened: R80, R6 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -725400000 | 725400000 | -313300000 | 313300000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid during the period for interest | 438400000 | 438400000 | 393400000 | 393400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Cash paid during the period for income taxes | 279300000 | 279300000 | 103700000 | 103700000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000885550-26-000047 R7.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:DebtInstrumentCarryingAmount | R75.htm | Total | 6387900000 | 6387900000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R75.htm 'Debt (Scheduled Principal Maturities Of Debt) (Details)' (MetaLinks.json presentation) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 10680143 | 10680143 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Total revenue' on us-gaap:Revenues = 825300000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 350800000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000885550-16-000083 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 37800000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Interest' on us-gaap:InterestExpense = 76000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 474500000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 174800000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 299700000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 14.35 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 14.28 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 20891695 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000885550-16-000083 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 20980753 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 6300000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Income taxes receivable' on us-gaap:IncomeTaxReceivable = 10000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 18900000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Total Assets' on us-gaap:Assets = 3389400000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 127800000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Total Liabilities' on us-gaap:Liabilities = 2461300000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000885550-16-000083 R2.htm prints 'Total Shareholders' Equity' on us-gaap:StockholdersEquity = 928100000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 404200000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -639500000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 235200000 (FILING-CHECKED)
- capex: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -4000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000885550-16-000083 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 12400000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -86500000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Cash paid during the period for interest' on us-gaap:InterestPaidNet = 61800000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000885550-16-000083 R7.htm prints 'Cash paid during the period for income taxes' on us-gaap:IncomeTaxesPaidNet = 146900000 (FILING-CHECKED)
- operating_expenses: era 10-K 0000885550-23-000023 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 1120700000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000885550-21-000034 R3.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 549500000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
