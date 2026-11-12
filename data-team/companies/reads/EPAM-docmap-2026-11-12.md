# EPAM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001352010-26-000015 (CIK 0001352010, filed 2026-02-26): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001352010-26-000015 (CIK 0001352010, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001352010.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues | 5457056000 | 5457056000 | 4727940000 | 4727940000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenues (exclusive of depreciation and amortization) | 3883535000 | 3883535000 | 3277497000 | 3277497000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | 928707000 | 928707000 | 816300000 | 816300000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 520003000 | 520003000 | 544584000 | 544584000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R5.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 505624000 | 505624000 | 584412000 | 584412000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 127946000 | 127946000 | 129879000 | 129879000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 377678000 | 377678000 | 454533000 | 454533000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 6.76 | 6.76 | 7.93 | 7.93 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 6.72 | 6.72 | 7.84 | 7.84 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 55893000 | 55893000 | 57288000 | 57288000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 56233000 | 56233000 | 57983000 | 57983000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1296077000 | 1296077000 | 1286267000 | 1286267000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | epam:TradeReceivablesAndContractAssetsAfterAllowanceForCreditLossCurrent | R3.htm | Trade receivables and contract assets, net of allowance of $6,350 and $5,612, respectively | 1108201000 |  | 1002175000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the inventory tag/label rules; not hand-verified |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2533888000 | 2533888000 | 2426248000 | 2426248000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 202387000 | 202387000 | 207667000 | 207667000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1210564000 | 1210564000 | 1181575000 | 1181575000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4902136000 | 4902136000 | 4750473000 | 4750473000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 55329000 | 55329000 | 44702000 | 44702000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 976942000 | 976942000 | 821039000 | 821039000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 1224328000 | 1224328000 | 1119322000 | 1119322000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total EPAM Systems, Inc. stockholders’ equity | 3677226000 | 3677226000 | 3629211000 | 3629211000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 654934000 | 654934000 | 559168000 | 559168000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -49047000 | -49047000 | -884980000 | -884980000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -651200000 | -651200000 | -390407000 | -390407000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -42243000 | 42243000 | -32146000 | 32146000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:OtherDepreciationAndAmortization | R8.htm | Depreciation and amortization expense | 124811000 | 124811000 | 89559000 | 89559000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation expense | 176764000 | 176764000 | 167297000 | 167297000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -662159000 | 662159000 | -398028000 | 398028000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 1397000 | 1397000 | 3738000 | 3738000 | Y | FILING-CHECKED | accn 0001352010-26-000015 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Long-term debt | 25034000 | 25034000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 54274000 | 54274000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- depreciation_and_amortization: era 10-K 0001352010-26-000015 R8.htm prints 'Depreciation and amortization expense' on us-gaap:OtherDepreciationAndAmortization = 124811000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_receivable: API missing (epam:TradeReceivablesAndContractAssetsAfterAllowanceForCreditLossCurrent)
