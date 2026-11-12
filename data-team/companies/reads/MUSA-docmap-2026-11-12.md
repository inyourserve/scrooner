# MUSA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001573516-26-000090 (CIK 0001573516, filed 2026-02-18): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001573516-16-000051 (CIK 0001573516, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- 10-K 0001573516-18-000010 (CIK 0001573516, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- 10-K 0001573516-24-000007 (CIK 0001573516, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0001573516.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax | R5.htm | Total operating revenues | 19384000000 | 19384000000 | 20244300000 | 20244300000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of goods sold | 13589800000 |  | 14556400000 |  | API missing | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (844 tags across all 103 R pages, face and notes) of 0001573516-26-000090; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 18662700000 | 18662700000 | 19496900000 | 19496900000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 231500000 | 231500000 | 235400000 | 235400000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (844 tags across all 103 R pages, face and notes) of 0001573516-26-000090; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income (loss) from operations | 718500000 | 718500000 | 742900000 | 742900000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -110900000 | 110900000 | -97100000 | 97100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 609200000 | 609200000 | 651600000 | 651600000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense (benefit) | 138600000 | 138600000 | 149100000 | 149100000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income | 470600000 | 470600000 | 502500000 | 502500000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 24.38 | 24.38 | 24.47 | 24.47 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 24.1 | 24.1 | 24.11 | 24.11 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 19303000 | 19303000 | 20533000 | 20533000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 19526000 | 19526000 | 20842000 | 20842000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 28900000 | 28900000 | 47000000 | 47000000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable—trade, less allowance for doubtful accounts of $0.3 in 2025 and 2024, respectively | 276200000 | 276200000 | 268500000 | 268500000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, at lower of cost or market | 413000000 | 413000000 | 401600000 | 401600000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 747800000 | 747800000 | 748100000 | 748100000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant and equipment, at cost less accumulated depreciation and amortization of $2,173.5 in 2025 and $1,931.4 i | 2962800000 | 2962800000 | 2813200000 | 2813200000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 328000000 | 328000000 | 328000000 | 328000000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 4725800000 | 4725800000 | 4541600000 | 4541600000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Trade accounts payable and accrued liabilities | 865200000 | 865200000 | 874400000 | 874400000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 929100000 | 929100000 | 947900000 | 947900000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 4102300000 | 4102300000 | 3701500000 | 3701500000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 623500000 | 623500000 | 840100000 | 840100000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided (required) by operating activities | 813900000 | 813900000 | 847600000 | 847600000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash provided (required) by investing activities | -436000000 | -436000000 | -445800000 | -445800000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided (required) by financing activities | -396000000 | -396000000 | -472600000 | -472600000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Property additions | -439600000 | 439600000 | -458100000 | 458100000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 276800000 | 276800000 | 248000000 | 248000000 | Y | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation | R7.htm | Amounts related to share-based compensation | -23500000 | 23500000 | -30400000 | 30400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R7.htm | Dividends paid | -41500000 | 41500000 | -36800000 | 36800000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Purchase of treasury stock | -649900000 | 649900000 | -445700000 | 445700000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001573516-26-000090 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R86.htm | Other Financial Information - Narrative (Details) |  | 105100000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R86.htm 'Other Financial Information - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R71.htm | Income Taxes - Schedule of Cash Income Tax, Net of Refunds (Details) |  | 101000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R71.htm 'Income Taxes - Schedule of Cash Income Tax, Net of Refunds (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt + Long-term debt, including capitalized lease obligations | 2182600000 | 2182600000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (844 tags across all 103 R pages, face and notes) of 0001573516-26-000090; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Total revenues' on us-gaap:Revenues = 12699411000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Merchandise cost of goods sold' on us-gaap:CostOfGoodsSold = 1946423000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Total costs and operating expenses' on us-gaap:CostsAndExpenses = 12444647000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 129277000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 254764000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -33531000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Income from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 218289000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 80698000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Net Income' on us-gaap:NetIncomeLoss = 176340000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Net income - basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 4.06 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Net income - diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 4.02 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 43434000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001573516-16-000051 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 43794000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 102335000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Accounts receivable—trade, less allowance for doubtful accounts of $1,963 in 201' on us-gaap:AccountsReceivableNetCurrent = 136253000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Inventories, at lower of cost or market' on us-gaap:InventoryNet = 155906000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 435667000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Property, plant and equipment, at cost less accumulated depreciation and amortiz' on us-gaap:PropertyPlantAndEquipmentNet = 1369318000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001573516-16-000051 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Total assets' on us-gaap:Assets = 1886241000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Trade accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 390341000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 392292000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 1093951000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001573516-16-000051 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 792290000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 215838000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Net cash provided by (required by) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -189634000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Net cash required by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -251974000 (FILING-CHECKED)
- capex: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Property additions' on us-gaap:PaymentsToAcquireProductiveAssets = -205225000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 86568000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Amounts related to share-based compensation' on us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation = -3075000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001573516-16-000051 R5.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001573516-16-000051 R5.htm prints 'Purchase of treasury stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -248695000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001573516-16-000051 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001573516-16-000051 R5.htm read; no row matched (auto)
- revenue: era 10-K 0001573516-18-000010 R4.htm prints 'Total operating revenues' on us-gaap:Revenues = 12826553000 (FILING-CHECKED)
- interest_expense: era 10-K 0001573516-24-000007 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -98500000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (4). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 18662700000 vs printed 18662700000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | mapped-sample | agree | page value 413000000 vs printed 413000000 |
| ppe_net | mapped-sample | agree | page value 2962800000 vs printed 2962800000 |
| accounts_payable | mapped-sample | agree | page value 865200000 vs printed 865200000 |
| capex | mapped-sample | agree | page value -439600000 vs printed -439600000 |
| cash_paid_for_interest | NOTE | agree | page value 105100000 vs API 105100000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 101000000 vs API 101000000 |
| total_debt | component sum | agree | page value 2182600000 vs printed 2182600000 |
| shares_outstanding | not_presented | agree | none of the candidate elements in MetaLinks.json |
