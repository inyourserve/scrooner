# GLPI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001575965-26-000032 (CIK 0001575965, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0001575965-16-000091 (CIK 0001575965, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001575965-21-000008 (CIK 0001575965, era filing): COVER R1.htm, BS R4.htm, BSP R5.htm, IS R6.htm, CF R9.htm
- 10-K 0001575965-25-000008 (CIK 0001575965, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- companyfacts CIK0001575965.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R92.htm | Revenue Recognition (Narrative) (Details) |  | 1594752000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R92.htm 'Revenue Recognition (Narrative) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 393299000 | 393299000 | 400861000 | 400861000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 63488000 | 63488000 | 59571000 | 59571000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 1201453000 | 1201453000 | 1130685000 | 1130685000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -373881000 | 373881000 | -366897000 | 366897000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 852585000 | 852585000 | 809777000 | 809777000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 2229000 | 2229000 | 2129000 | 2129000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 825111000 | 825111000 | 784620000 | 784620000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic earnings per common share (in dollars per share) | 2.95 | 2.95 | 2.87 | 2.87 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted earnings per common share (in dollars per share) | 2.95 | 2.95 | 2.87 | 2.87 | Y | FILING-CHECKED | accn 0001575965-26-000032 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R101.htm | Earnings Per Share Earnings Per Share (Weighted Average Common Shares Outstanding) (Details) |  | 279605000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R101.htm 'Earnings Per Share Earnings Per Share (Weighted Average Common Shares Outstandin' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R101.htm | Earnings Per Share Earnings Per Share (Weighted Average Common Shares Outstanding) (Details) |  | 280043000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R101.htm 'Earnings Per Share Earnings Per Share (Weighted Average Common Shares Outstandin' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | R3.htm | Cash and cash equivalents | 224314000 | 224314000 | 462632000 | 462632000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R3.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| ppe_net | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| goodwill | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 12909609000 | 12909609000 | 13075949000 | 13075949000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 6641000 | 6641000 | 5802000 | 5802000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001575965-26-000032 R3.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 7901349000 | 7901349000 | 8430425000 | 8430425000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total equity attributable to Gaming and Leisure Properties | 4626452000 | 4626452000 | 4268562000 | 4268562000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 1129417000 | 1129417000 | 1072770000 | 1072770000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -308756000 | -308756000 | -1605944000 | -1605944000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | -1058979000 | -1058979000 | 311823000 | 311823000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation, Depletion and Amortization | 282944000 | 282944000 | 273422000 | 273422000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 21181000 | 21181000 | 24262000 | 24262000 | Y | FILING-CHECKED | accn 0001575965-26-000032 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends paid | -871872000 | 871872000 | -830716000 | 830716000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001575965-26-000032 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1045 tags across all 110 R pages, face and notes) of 0001575965-26-000032; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R107.htm | Supplemental Disclosures of Cash Flow Information and Noncash Activities (Supplemental Cash Flow Information) (Details) |  | 357025000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R107.htm 'Supplemental Disclosures of Cash Flow Information and Noncash Activities (Supple' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R107.htm | Supplemental Disclosures of Cash Flow Information and Noncash Activities (Supplemental Cash Flow Information) (Details) |  | 2228000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R107.htm 'Supplemental Disclosures of Cash Flow Information and Noncash Activities (Supple' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebt | R3.htm | Long-term debt, net of unamortized debt issuance costs, bond premiums and original issuance discounts | 7203731000 | 7203731000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding | 283037310 | 283037310 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Net revenues' on us-gaap:Revenues = 575053000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 317638000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001575965-16-000091 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 85669000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 257415000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -124183000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 135564000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 7442000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 128122000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Basic earnings per common share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.12 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001575965-16-000091 R4.htm prints 'Diluted earnings per common share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.08 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001575965-16-000091 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001575965-16-000091 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001575965-16-000091 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 41875000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001575965-16-000091 R2.htm prints 'Total assets' on us-gaap:Assets = 2448155000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001575965-16-000091 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrentAndNoncurrent = 406000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001575965-16-000091 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2701669000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001575965-16-000091 R2.htm prints 'Total shareholders’ deficit' on us-gaap:StockholdersEquity = -253514000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001575965-16-000091 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 319688000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001575965-16-000091 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -14142000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001575965-16-000091 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -299644000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001575965-16-000091 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001575965-16-000091 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 16811000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001575965-16-000091 R7.htm prints 'Dividends paid (including the Purging Distribution in 2014)' on us-gaap:PaymentsOfDividends = -251732000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001575965-16-000091 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001575965-16-000091 R7.htm read; no row matched (auto)
- operating_expenses: era 10-K 0001575965-21-000008 R6.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 343891000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001575965-21-000008 R9.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -230522000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001575965-21-000008 R9.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -230522000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001575965-21-000008 R9.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -230522000 (FILING-CHECKED)
- interest_expense: era 10-K 0001575965-25-000008 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -366897000 (FILING-CHECKED)
- dividends_paid: era 10-K 0001575965-25-000008 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -830716000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (2). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| revenue | NOTE | agree | page value 1594752000 vs API 1594752000 |
| cost_of_revenue | not_presented | agree | none of the candidate elements in MetaLinks.json |
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 393299000 vs printed 393299000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| basic_eps | mapped-sample | agree | page value 2.95 vs printed 2.95 |
| diluted_eps | mapped-sample | agree | page value 2.95 vs printed 2.95 |
| weighted_basic_shares | NOTE | agree | page value 279605000 vs API 279605000 |
| weighted_diluted_shares | NOTE | agree | page value 280043000 vs API 280043000 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| goodwill | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| capex | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 357025000 vs API 357025000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 2228000 vs API 2228000 |
| total_debt | component sum | agree | page value 7203731000 vs printed 7203731000 |
