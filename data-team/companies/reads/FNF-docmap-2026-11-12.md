# FNF document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001331875-26-000026 (CIK 0001331875, filed 2026-02-26): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001331875-16-000111 (CIK 0001331875, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001331875-25-000013 (CIK 0001331875, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- 10-K 0001331875-20-000008 (CIK 0001331875, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001331875.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 14445000000 | 14445000000 | 13681000000 | 13681000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| operating_expenses | mapped | us-gaap:BenefitsLossesAndExpenses | R5.htm | Total expenses | 13048000000 | 13048000000 | 11939000000 | 11939000000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Interest expense | 242000000 | 242000000 | 209000000 | 209000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Earnings before income taxes and equity in earnings of unconsolidated affiliates | 1397000000 | 1397000000 | 1742000000 | 1742000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 753000000 | 753000000 | 367000000 | 367000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net earnings attributable to Fidelity National Financial, Inc. common shareholders | 602000000 | 602000000 | 1270000000 | 1270000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net earnings per share attributable to FNF common shareholders, basic (in dollars per share) | 2.22 | 2.22 | 4.69 | 4.69 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net earnings per share attributable to FNF common shareholders, diluted (in dollars per share) | 2.21 | 2.21 | 4.65 | 4.65 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average shares outstanding FNF common stock, basic basis (in shares) | 271000000 | 271000000 | 271000000 | 271000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average shares outstanding FNF common stock, diluted basis (in shares) | 272000000 | 272000000 | 273000000 | 273000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents, as of December 31, 2025 and 2024 includes $261 and $69, respectively, of pledged cash related | 2636000000 | 2636000000 | 3479000000 | 3479000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsAndNotesReceivableNet | R3.htm | Trade and notes receivables, net of allowance of $31 and $32 as of December 31, 2025 and 2024, respectively | 473000000 | 473000000 | 471000000 | 471000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 189000000 | 189000000 | 173000000 | 173000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5272000000 | 5272000000 | 5271000000 | 5271000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 109014000000 | 109014000000 | 95263000000 | 95263000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued liabilities | 3828000000 | 3828000000 | 3249000000 | 3249000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1609 tags across all 172 R pages, face and notes) of 0001331875-26-000026; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 100042000000 | 100042000000 | 86731000000 | 86731000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Fidelity National Financial, Inc. shareholders’ equity | 7424000000 | 7424000000 | 7754000000 | 7754000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by (used in) operating activities | 5828000000 | 5828000000 | 6815000000 | 6815000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -8934000000 | -8934000000 | -7862000000 | -7862000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by financing activities | 2263000000 | 2263000000 | 1759000000 | 1759000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| capex | mapped | fnf:PaymentsToAcquirePropertyPlantandEquipmentandSoftware | R9.htm | Additions to property and equipment and capitalized software | -147000000 |  | -146000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 844000000 | 844000000 | 739000000 | 739000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation cost | 88000000 | 88000000 | 82000000 | 82000000 | Y | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -546000000 | 546000000 | -532000000 | 532000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Purchases of treasury stock | -251000000 | 251000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001331875-26-000026 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R111.htm | Supplemental Cash Flow Information (Details) |  | 229000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R111.htm | Supplemental Cash Flow Information (Details) |  | 250000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R111.htm 'Supplemental Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Notes payable | 4400000000 | 4400000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 271000000 | 271000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Total revenues' on us-gaap:Revenues = 9132000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Total expenses' on us-gaap:BenefitsLossesAndExpenses = 8265000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = 131000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Earnings from continuing operations before income taxes and equity in (loss ) ea' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 867000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Income tax expense on continuing operations' on us-gaap:IncomeTaxExpenseBenefit = 290000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Net earnings attributable to Fidelity National Financial, Inc. common shareholde' on us-gaap:NetIncomeLoss = 527000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Basic earnings per share (in usd per share)' on us-gaap:EarningsPerShareBasic =  (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Diluted earnings per share (in usd per share)' on us-gaap:EarningsPerShareDiluted =  (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Weighted average number of shares outstanding, basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic =  (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001331875-16-000111 R4.htm prints 'Weighted average number of shares outstanding, diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding =  (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Cash and cash equivalents, at December 31, 2015 and 2014, includes pledged cash ' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 780000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Trade and notes receivables, net of allowance of $32 at December 31, 2015 and 20' on us-gaap:AccountsAndNotesReceivableNet = 496000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 510000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 4760000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Total assets' on us-gaap:Assets = 13931000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Accounts payable and other accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 1283000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 6999000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001331875-16-000111 R2.htm prints 'Total Fidelity National Financial, Inc. shareholders’ equity' on us-gaap:StockholdersEquity = 5754000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 917000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -571000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -238000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Additions to property and equipment and capitalized software' on fnf:PaymentsToAcquirePropertyPlantandEquipmentandSoftware = -241000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 410000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Stock-based compensation cost' on us-gaap:ShareBasedCompensation = 56000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -220000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001331875-16-000111 R7.htm prints 'Purchases of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -498000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001331875-16-000111 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001331875-16-000111 R7.htm read; no row matched (auto)
- interest_expense: era 10-K 0001331875-25-000013 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = 209000000 (FILING-CHECKED)
- sbc: era 10-K 0001331875-20-000008 R8.htm prints 'Stock-based compensation cost' on us-gaap:ShareBasedCompensation = 38000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- capex: API missing (fnf:PaymentsToAcquirePropertyPlantandEquipmentandSoftware)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | mapped-sample | agree | page value 753000000 vs printed 753000000 |
| weighted_basic_shares | mapped-sample | agree | page value 271000000 vs printed 271000000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| total_liabilities | mapped-sample | agree | page value 100042000000 vs printed 100042000000 |
| cash_paid_for_interest | NOTE | agree | page value 229000000 vs API 229000000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 250000000 vs API 250000000 |
| total_debt | component sum | agree | page value 4400000000 vs printed 4400000000 |
