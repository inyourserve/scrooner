# RRX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000082811-26-000054 (CIK 0000082811, filed 2026-02-20): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000082811-16-000124 (CIK 0000082811, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000082811-15-000014 (CIK 0000082811, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0000082811-19-000018 (CIK 0000082811, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0000082811.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R3.htm | Net Sales | 5934500000 | 5934500000 | 6033800000 | 6033800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of Sales | 3716700000 | 3716700000 | 3842800000 | 3842800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross Profit | 2217800000 | 2217800000 | 2191000000 | 2191000000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total Operating Expenses | 1537000000 | 1537000000 | 1561000000 | 1561000000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (1089 tags across all 112 R pages, face and notes) of 0000082811-26-000054; no face row matched |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R46.htm | Accounting Policies - Schedule of Research and Development Costs are Expense (Details) |  | 198700000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R46.htm 'Accounting Policies - Schedule of Research and Development Costs are Expense (De' (MetaLinks.json presentation); value from companyfacts same accession |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Income from Operations | 680800000 | 680800000 | 630000000 | 630000000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest Expense | 349200000 | 349200000 | 399700000 | 399700000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income (Loss) before Taxes | 352500000 | 352500000 | 248000000 | 248000000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for Income Taxes | 71700000 | 71700000 | 49600000 | 49600000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net Income (Loss) Attributable to Regal Rexnord Corporation | 279500000 | 279500000 | 196200000 | 196200000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 4.22 | 4.22 | 2.96 | 2.96 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Assuming Dilution (in dollars per share) | 4.2 | 4.2 | 2.94 | 2.94 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 66300000 | 66300000 | 6.64e+07 | 66400000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Assuming Dilution (in shares) | 6.66e+07 | 66600000 | 66700000 | 66700000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and Cash Equivalents | 5.217e+08 | 521700000 | 393500000 | 393500000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Trade Receivables, Less Allowances of $10.5 Million in 2025 and $29.9 Million in 2024 | 5.242e+08 | 524200000 | 842800000 | 842800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 1321700000 | 1321700000 | 1227500000 | 1227500000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total Current Assets | 2712300000 | 2712300000 | 2751300000 | 2751300000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R5.htm | Net Property, Plant and Equipment | 911800000 | 911800000 | 921000000 | 921000000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 6611300000 | 6611300000 | 6458900000 | 6458900000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total Assets | 13921000000 | 13921000000 | 14033700000 | 14033700000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts Payable | 607300000 | 607300000 | 542800000 | 542800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total Current Liabilities | 1264300000 | 1264300000 | 1215700000 | 1215700000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1089 tags across all 112 R pages, face and notes) of 0000082811-26-000054; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Regal Rexnord Corporation Shareholders' Equity | 6844100000 | 6844100000 | 6259800000 | 6259800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net Cash Provided by Operating Activities | 990800000 | 990800000 | 609400000 | 609400000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net Cash (Used in) Provided by Investing Activities | -71000000 | -71000000 | 275400000 | 275400000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net Cash (Used in) Provided by Financing Activities | -814100000 | -814100000 | -1095800000 | -1095800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Additions to Property, Plant and Equipment | -97700000 | 97700000 | -109500000 | 109500000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 154500000 | 154500000 | 165300000 | 165300000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Share-Based Compensation Expense | 37300000 | 37300000 | 34800000 | 34800000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends Paid to Shareholders | -93000000 | 93000000 | -93000000 | 93000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Repurchase of Common Stock | 0 | 0 | -50000000 | 50000000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest | 312100000 | 312100000 | 380300000 | 380300000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income Taxes | 188700000 | 188700000 | 177100000 | 177100000 | Y | FILING-CHECKED | accn 0000082811-26-000054 R9.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current Maturities of Long-Term Debt + Long-Term Debt | 4.789e+09 | 4788700000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 6.64e+07 | 66400000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Net Sales' on us-gaap:SalesRevenueGoodsNet = 3509700000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Cost of Sales' on us-gaap:CostOfGoodsSold = 2576500000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Gross Profit' on us-gaap:GrossProfit = 933200000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000082811-16-000124 R2.htm read; no row matched (auto)
- research_and_development: FY2015 10-K 0000082811-16-000124 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Income from Operations' on us-gaap:OperatingIncomeLoss = 252800000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Interest Expense' on us-gaap:InterestExpense = 60200000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Income before Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 196900000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Provision for Income Taxes' on us-gaap:IncomeTaxExpenseBenefit = 48400000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Net Income Attributable to Regal Beloit Corporation' on us-gaap:NetIncomeLoss = 143300000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Basic (in dollars per shares)' on us-gaap:EarningsPerShareBasic = 3.21 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Assuming Dilution (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.18 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 44700000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000082811-16-000124 R2.htm prints 'Assuming Dilution (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 45100000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Cash and Cash Equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 252900000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Trade Receivables, less Allowances of $11.3 million in 2015 and $11.6 million in' on us-gaap:AccountsReceivableNetCurrent = 462000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Inventories' on us-gaap:InventoryNet = 775000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Total Current Assets' on us-gaap:AssetsCurrent = 1635200000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Net Property, Plant and Equipment' on us-gaap:PropertyPlantAndEquipmentNet = 678500000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Goodwill' on us-gaap:Goodwill = 1465600000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Total Assets' on us-gaap:Assets = 4591700000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Accounts Payable' on us-gaap:AccountsPayableCurrent = 336200000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Total Current Liabilities' on us-gaap:LiabilitiesCurrent = 612800000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000082811-16-000124 R5.htm prints 'Total Regal Beloit Corporation Shareholders' Equity' on us-gaap:StockholdersEquity = 1937300000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Net Cash Provided by Operating Activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = -381100000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Net Cash Used in Investing Activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1487600000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Net Cash Provided By (Used In) Financing Activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1.037e+09 (FILING-CHECKED)
- capex: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Additions to Property, Plant and Equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -92200000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000082811-16-000124 R9.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Share-based Compensation Expense' on us-gaap:ShareBasedCompensation = 13900000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Dividends Paid to Shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -40200000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Repurchase of Common Stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -12000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Interest' on us-gaap:InterestPaid = 54600000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000082811-16-000124 R9.htm prints 'Income Taxes' on us-gaap:IncomeTaxesPaidNet = 70100000 (FILING-CHECKED)
- revenue: era 10-K 0000082811-15-000014 R2.htm read; no row matched (auto)
- revenue: era 10-K 0000082811-19-000018 R2.htm prints 'Net Sales' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 3645600000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | mapped-sample | agree | page value 5934500000 vs printed 5934500000 |
| gross_profit | mapped-sample | agree | page value 2217800000 vs printed 2217800000 |
| operating_expenses | mapped-sample | agree | page value 1537000000 vs printed 1537000000 |
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | NOTE | agree | page value 198700000 vs API 198700000 |
| total_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| depreciation_and_amortization | component sum | agree | page value 154500000 vs printed 154500000 |
| share_buybacks | mapped-sample | agree | page value 0 vs printed 0 |
| total_debt | component sum | agree | page value 4788700000 = printed 4.789e+09 at 4 significant digits; fy0_printed restored to the page value |
