# CLX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000021076-25-000039 (CIK 0000021076, filed 2025-08-08): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001206774-15-002800 (CIK 0000021076, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000021076-18-000011 (CIK 0000021076, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001628280-17-008700 (CIK 0000021076, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000021076.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Net sales | 7104000000 | 7104000000 | 7093000000 | 7093000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of products sold | 3891000000 | 3891000000 | 4045000000 | 4045000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 3213000000 | 3213000000 | 3048000000 | 3048000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (1060 tags across all 124 R pages, face and notes) of 0000021076-25-000039; no face row matched |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling and administrative expenses | 1124000000 | 1124000000 | 1167000000 | 1167000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development costs | 121000000 | 121000000 | 126000000 | 126000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| operating_income | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1060 tags across all 124 R pages, face and notes) of 0000021076-25-000039; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R3.htm | Interest expense | 88000000 | 88000000 | 90000000 | 90000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before income taxes | 1078000000 | 1078000000 | 398000000 | 398000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 254000000 | 254000000 | 106000000 | 106000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings attributable to Clorox | 810000000 | 810000000 | 280000000 | 280000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic net earnings per share (in dollars per share) | 6.56 | 6.56 | 2.26 | 2.26 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted net earnings per share (in dollars per share) | 6.52 | 6.52 | 2.25 | 2.25 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 123525000 | 123525000 | 124174000 | 124174000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 124287000 | 124287000 | 124804000 | 124804000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R3.htm period ..2025-06-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 167000000 | 167000000 | 202000000 | 202000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net | 821000000 | 821000000 | 695000000 | 695000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories, net | 523000000 | 523000000 | 637000000 | 637000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1608000000 | 1608000000 | 1622000000 | 1622000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 1267000000 | 1267000000 | 1315000000 | 1315000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 1229000000 | 1229000000 | 1228000000 | 1228000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 5561000000 | 5561000000 | 5751000000 | 5751000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R5.htm | Accounts payable and accrued liabilities | 1828000000 | 1828000000 | 1486000000 | 1486000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 1919000000 | 1919000000 | 1574000000 | 1574000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 5079000000 | 5079000000 | 5259000000 | 5259000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total Clorox stockholders’ equity | 321000000 | 321000000 | 328000000 | 328000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R5.htm period ..2025-06-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operations | 981000000 | 981000000 | 695000000 | 695000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used for investing activities | -94000000 | -94000000 | -175000000 | -175000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used for financing activities | -924000000 | -924000000 | -655000000 | -655000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Capital expenditures | -220000000 | 220000000 | -212000000 | 212000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 219000000 | 219000000 | 235000000 | 235000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 81000000 | 81000000 | 74000000 | 74000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Cash dividends paid to Clorox stockholders | -602000000 | 602000000 | -595000000 | 595000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Treasury stock purchased | -332000000 | 332000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest paid | 97000000 | 97000000 | 102000000 | 102000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes paid, net of refunds | 264000000 | 264000000 | 347000000 | 347000000 | Y | FILING-CHECKED | accn 0000021076-25-000039 R9.htm period ..2025-06-30 |
| total_debt | component sum | us-gaap:CommercialPaper+us-gaap:LongTermDebtNoncurrent | R5.htm | Notes and loans payable + Long-term debt | 2488000000 | 2488000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 122694263 | 122694263 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-06-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 5655000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 3190000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 2465000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Selling and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 798000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Research and development costs' on us-gaap:ResearchAndDevelopmentExpense = 136000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 100000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Earnings from continuing operations before income taxes' on clx:EarningsFromContinuingOperationsBeforeIncomeTaxes = 921000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Income taxes on continuing operations' on us-gaap:IncomeTaxExpenseBenefit = 315000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 580000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Basic net earnings per share' on us-gaap:EarningsPerShareBasic = 4.45 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Diluted net earnings per share' on us-gaap:EarningsPerShareDiluted = 4.37 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 130310000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001206774-15-002800 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 132776000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 382000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Receivables, net' on us-gaap:ReceivablesNetCurrent = 519000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Inventories, net' on us-gaap:InventoryNet = 385000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1429000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 918000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1067000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Total assets' on us-gaap:Assets = 4164000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 431000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1405000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 4046000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001206774-15-002800 R4.htm prints 'Stockholders' equity' on us-gaap:StockholdersEquity = 118000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Net cash provided by operations' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 874000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -106000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Net cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -696000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -125000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 169000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 32000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Cash dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -385000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Treasury stock purchased' on us-gaap:PaymentsForRepurchaseOfCommonStock = -434000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 104000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001206774-15-002800 R7.htm prints 'Income taxes paid, net of refunds' on us-gaap:IncomeTaxesPaidNet = 236000000 (FILING-CHECKED)
- revenue: era 10-K 0000021076-18-000011 R2.htm prints 'Net sales' on us-gaap:Revenues = 6124000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001628280-17-008700 R2.htm prints 'Cost of products sold' on us-gaap:CostOfGoodsSold = 3302000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| operating_expenses | not_presented | agree | none of the candidate elements in MetaLinks.json |
| research_and_development | mapped-sample | agree | page value 121000000 vs printed 121000000 |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| interest_expense | mapped-sample | agree | page value 88000000 vs printed 88000000 |
| diluted_eps | mapped-sample | agree | page value 6.52 vs printed 6.52 |
| weighted_diluted_shares | mapped-sample | agree | page value 124287000 vs printed 124287000 |
| total_debt | component sum | agree | page value 2524000000 vs printed 2524000000 |
