# AAON document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0000824142-26-000005 (CIK 0000824142, filed 2026-03-02): COVER R1.htm, BS R3.htm, IS R4.htm, CF R6.htm, BSP R7.htm
- 10-K 0001026608-13-000024 (CIK 0000824142, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0000824142-23-000019 (CIK 0000824142, era filing): COVER R1.htm, BS R3.htm, IS R4.htm, CF R6.htm, BSP R7.htm
- companyfacts CIK0000824142.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R4.htm | Net sales | 1442076000 | 1442076000 | 1200635000 | 1200635000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of sales | 1056352000 | 1056352000 | 803526000 | 803526000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Gross profit | 385724000 | 385724000 | 397109000 | 397109000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative expenses | 239480000 | 239480000 | 188014000 | 188014000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the research_and_development tag/label rules; not hand-verified |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | Income from operations | 146248000 | 146248000 | 209118000 | 209118000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNet | R4.htm | Interest expense | -17726000 | -17726000 | -2905000 | -2905000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income before taxes | 128752000 | 128752000 | 206591000 | 206591000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax provision | 21159000 | 21159000 | 38032000 | 38032000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income | 107593000 | 107593000 | 168559000 | 168559000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (usd per share) | 1.32 | 1.32 | 2.07 | 2.07 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (usd per share) | 1.29 | 1.29 | 2.02 | 2.02 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 81529140 | 81529140 | 81473131 | 81473131 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 83105538 | 83105538 | 83629502 | 83629502 | Y | FILING-CHECKED | accn 0000824142-26-000005 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 13000 | 13000 | 14000 | 14000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 314387000 | 314387000 | 147434000 | 147434000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, net | 261151000 | 261151000 | 187420000 | 187420000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 869180000 | 869180000 | 488212000 | 488212000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 631262000 | 631262000 | 510356000 | 510356000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the goodwill tag/label rules; not hand-verified |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1686510000 | 1686510000 | 1175234000 | 1175234000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 110437000 | 110437000 | 44645000 | 44645000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 330855000 | 330855000 | 174905000 | 174905000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R3.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Total stockholders' equity | 894985000 | 894985000 | 824582000 | 824582000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000824142-26-000005 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 534000 | 534000 | 192532000 | 192532000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash used in investing activities | -192417000 | -192417000 | -213075000 | -213075000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used in) financing activities | 186608000 | 186608000 | 18034000 | 18034000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireMachineryAndEquipment | R6.htm | Capital expenditures | -190563000 | 190563000 | -195660000 | 195660000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 79191000 | 79191000 | 62735000 | 62735000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Share-based compensation | 17994000 | 17994000 | 16729000 | 16729000 | Y | FILING-CHECKED | accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R6.htm | Cash dividends paid to stockholders | -32603000 | 32603000 | -26084000 | 26084000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfEquity | R6.htm | Repurchase of stock - open market | -29995000 | 29995000 | -100034000 | 100034000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000824142-26-000005 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the cash_paid_for_interest tag/label rules; not hand-verified |
| cash_paid_for_income_taxes | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R6.htm read; no face row matched the cash_paid_for_income_taxes tag/label rules; not hand-verified |
| total_debt | component sum | us-gaap:DebtCurrent | R3.htm | Debt, short-term | 0 | 0 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 81691075 | 81691075 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era checks (tag changes in the last ~5 years)
- interest_expense: era 10-K 0001026608-13-000024 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -44 (FILING-CHECKED)
- capex: era 10-K 0000824142-23-000019 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -54024000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
