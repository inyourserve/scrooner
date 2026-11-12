# IOVA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001104659-26-018899 (CIK 0001425205, filed 2026-02-24): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001144204-19-010702 (CIK 0001425205, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001425205.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Total revenue | 263502000 | 263502000 | 164070000 | 164070000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R4.htm | Cost of sales | 173184000 | 173184000 | 93248000 | 93248000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the gross_profit tag/label rules; not hand-verified |
| operating_expenses | mapped | us-gaap:CostsAndExpenses | R4.htm | Total costs and expenses | 666858000 | 666858000 | 559348000 | 559348000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | Selling, general, and administrative | 152322000 | 152322000 | 152269000 | 152269000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 300270000 | 300270000 | 276228000 | 276228000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Loss from operations | -403356000 | -403356000 | -395278000 | -395278000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the interest_expense tag/label rules; not hand-verified |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Net Loss before income taxes | -393049000 | -393049000 | -375005000 | -375005000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax (expense) benefit | 2071000 | -2071000 | 2828000 | -2828000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net Loss | -390978000 | -390978000 | -372177000 | -372177000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net Loss Per Share of Common Stock, Basic (in dollars per share) | -1.09 | -1.09 | -1.28 | -1.28 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net Loss Per Share of Common Stock, Diluted (in dollars per share) | -1.09 | -1.09 | -1.28 | -1.28 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted Average Shares of Common Stock Outstanding, Basic (in shares) | 357345 | 357345 | 289877 | 289877 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted Average Shares of Common Stock Outstanding, Diluted (in shares) | 357345 | 357345 | 289877 | 289877 | Y | FILING-CHECKED | accn 0001104659-26-018899 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 163078000 | 163078000 | 115694000 | 115694000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Trade accounts receivable | 82448000 | 82448000 | 69340000 | 69340000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventory | 51678000 | 51678000 | 51520000 | 51520000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total Current Assets | 442689000 | 442689000 | 457018000 | 457018000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 131112000 | 131112000 | 109081000 | 109081000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| goodwill | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total Assets | 913170000 | 913170000 | 910426000 | 910426000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 22159000 | 22159000 | 27509000 | 27509000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total Current Liabilities | 138358000 | 138358000 | 122341000 | 122341000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total Liabilities | 214587000 | 214587000 | 200021000 | 200021000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total Stockholders' Equity | 698583000 | 698583000 | 710405000 | 710405000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash used in operating activities | -302408000 | -302408000 | -352977000 | -352977000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided by (used in) investing activities | 47496000 | 47496000 | -96411000 | -96411000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by financing activities | 300773000 | 300773000 | 390664000 | 390664000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchase of property and equipment | -33836000 | 33836000 | -11069000 | 11069000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-018899 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization of property and equipment | 12862000 | 12862000 | 11255000 | 11255000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock-based compensation expense | 61575000 | 61575000 | 109627000 | 109627000 | Y | FILING-CHECKED | accn 0001104659-26-018899 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R7.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: no standard debt line on the BS face; not hand-verified |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common Stock, Shares, Outstanding | 411938061 | 411938061 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- revenue: era 10-K 0001144204-19-010702 R4.htm prints 'Revenues' on us-gaap:Revenues = 0 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
