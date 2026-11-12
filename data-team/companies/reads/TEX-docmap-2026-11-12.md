# TEX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000097216-26-000035 (CIK 0000097216, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- 10-K 0000097216-16-000245 (CIK 0000097216, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- companyfacts CIK0000097216.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Net sales | 5421000000 | 5421000000 | 5127000000 | 5127000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of goods sold | -4370000000 | 4370000000 | -4059000000 | 4059000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 1051000000 | 1051000000 | 1068000000 | 1068000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | -576000000 | 576000000 | -542000000 | 542000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | -576000000 | 576000000 | -542000000 | 542000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating profit | 475000000 | 475000000 | 526000000 | 526000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | -177000000 | 177000000 | -89000000 | 89000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (loss) from continuing operations before income taxes | 292000000 | 292000000 | 408000000 | 408000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | (Provision for) benefit from income taxes | -71000000 | 71000000 | -73000000 | 73000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:ProfitLoss | R3.htm | Net income (loss) | 221000000 | 221000000 | 335000000 | 335000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Net income (loss) (in dollars per share) | 3.36 | 3.36 | 5 | 5 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Net income (loss) attributable to Terex Corporation (in dollars per share) | 3.33 | 3.33 | 4.96 | 4.96 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 65800000 | 65800000 | 67000000 | 67000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 66300000 | 66300000 | 67600000 | 67600000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 772000000 | 772000000 | 388000000 | 388000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R6.htm | Receivables (net of allowance of $9 million at December 31, 2025 and 2024) | 712000000 | 712000000 | 643000000 | 643000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R6.htm | Inventories | 1109000000 | 1109000000 | 1147000000 | 1147000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 2725000000 | 2725000000 | 2320000000 | 2320000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant and equipment – net | 760000000 | 760000000 | 714000000 | 714000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R6.htm | Goodwill | 1091000000 | 1091000000 | 1093000000 | 1093000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 6139000000 | 6139000000 | 5730000000 | 5730000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R6.htm | Trade accounts payable | 683000000 | 683000000 | 580000000 | 580000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 1187000000 | 1187000000 | 1073000000 | 1073000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 4044000000 | 4044000000 | 3898000000 | 3898000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R6.htm | Total stockholders’ equity | 2095000000 | 2095000000 | 1832000000 | 1832000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000097216-26-000035 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 440000000 | 440000000 | 326000000 | 326000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash provided by (used in) investing activities | 32000000 | 32000000 | -2127000000 | -2127000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by (used in) financing activities | -123000000 | -123000000 | 1837000000 | 1837000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| capex | mapped | tex:PaymentstoAcquireProductiveAssetsincludingdiscontinuedoperations | R9.htm | Capital expenditures | -118000000 |  | -137000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | tex:DepreciationDepletionandAmortizationincludingdiscontinuedoperations | R9.htm | Depreciation and amortization | 158000000 |  | 82000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 32000000 | 32000000 | 30000000 | 30000000 | Y | FILING-CHECKED | accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -45000000 | 45000000 | -46000000 | 46000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Share repurchases | -56000000 | 56000000 | -49000000 | 49000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000097216-26-000035 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R9.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R6.htm | Current portion of long-term debt + Long-term debt, less current portion | 2584000000 | 2584000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding count at the BS date on the BS face or parenthetical (auto); dei cover count not used |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Net sales' on us-gaap:Revenues = 6543100000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Cost of goods sold' on us-gaap:CostOfRevenue = -5234600000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1308500000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Selling, general and administrative expenses + Goodwill and Intangible Asset Imp' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:GoodwillAndIntangibleAssetImpairment = -9.533e+08 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = -918600000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Income (loss) from operations' on us-gaap:OperatingIncomeLoss = 355200000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = -104600000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Income (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 226600000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000097216-16-000245 R2.htm prints '(Provision for) benefit from income taxes' on us-gaap:IncomeTaxExpenseBenefit = -81000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Net income (loss) attributable to Terex Corporation' on us-gaap:NetIncomeLoss = 145900000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Net income (loss) attributable to Terex Corporation (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.36 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Net income (loss) attributable to Terex Corporation (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.33 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 107400000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000097216-16-000245 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 109600000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 466500000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Trade receivables (net of allowance of $29.6 and $30.5 at December 31, 2015 and ' on us-gaap:ReceivablesNetCurrent = 939200000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 1445700000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3144200000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Property, plant and equipment – net' on us-gaap:PropertyPlantAndEquipmentNet = 675800000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 1023200000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Total assets' on us-gaap:Assets = 5637100000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Trade accounts payable' on us-gaap:AccountsPayableCurrent = 737700000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1458600000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 3725100000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000097216-16-000245 R5.htm prints 'Total Terex Corporation stockholders’ equity' on us-gaap:StockholdersEquity = 1877400000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 212900000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -172700000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -14400000 (FILING-CHECKED)
- capex: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Capital expenditures' on tex:PaymentstoAcquireProductiveAssetsincludingdiscontinuedoperations = -103800000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Depreciation and amortization' on tex:DepreciationDepletionandAmortizationincludingdiscontinuedoperations = 1.282e+08 (FILING-CHECKED)
- sbc: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 38500000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -25800000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000097216-16-000245 R8.htm prints 'Share repurchases' on us-gaap:PaymentsForRepurchaseOfCommonStock = -50800000 (FILING-CHECKED)

## Mismatches (printed vs API)
- capex: API missing (tex:PaymentstoAcquireProductiveAssetsincludingdiscontinuedoperations)
- depreciation_and_amortization: API missing (tex:DepreciationDepletionandAmortizationincludingdiscontinuedoperations)
