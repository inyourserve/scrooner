# FCX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000831259-26-000012 (CIK 0000831259, filed 2026-02-13): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0000831259-16-000062 (CIK 0000831259, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm
- 10-K 0000831259-18-000008 (CIK 0000831259, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, CF R4.htm, BS R5.htm, BSP R6.htm
- 10-K 0000831259-25-000006 (CIK 0000831259, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- companyfacts CIK0000831259.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Revenues | 25915000000 | 25915000000 | 25455000000 | 25455000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Total cost of sales | 18618000000 | 18618000000 | 17795000000 | 17795000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1241 tags across all 99 R pages, face and notes) of 0000831259-26-000012; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total costs and expenses | 19397000000 | 19397000000 | 18591000000 | 18591000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 545000000 | 545000000 | 513000000 | 513000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1241 tags across all 99 R pages, face and notes) of 0000831259-26-000012; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 6518000000 | 6518000000 | 6864000000 | 6864000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNet | R3.htm | Interest expense, net | -369000000 | -369000000 | -319000000 | -319000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income before income taxes and equity in affiliated companies’ net earnings | 6372000000 | 6372000000 | 6907000000 | 6907000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for (benefit from) income taxes | -2221000000 | 2221000000 | -2523000000 | 2523000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R3.htm | Net income attributable to common stockholders | 2204000000 | 2204000000 | 1889000000 | 1889000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerBasicShare | R3.htm | Basic | 1.53 | 1.53 | 1.31 | 1.31 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare | R3.htm | Diluted | 1.52 | 1.52 | 1.3 | 1.3 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic | 1437000000 | 1437000000 | 1438000000 | 1438000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted | 1443000000 | 1443000000 | 1445000000 | 1445000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R6.htm | Cash and cash equivalents | 3824000000 | 3824000000 | 3923000000 | 3923000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R6.htm | Trade accounts receivable | 977000000 | 977000000 | 578000000 | 578000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| inventory | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1241 tags across all 99 R pages, face and notes) of 0000831259-26-000012; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R6.htm | Total current assets | 13790000000 | 13790000000 | 13296000000 | 13296000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R6.htm | Property, plant, equipment and mine development costs, net | 40736000000 | 40736000000 | 38514000000 | 38514000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| goodwill | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1241 tags across all 99 R pages, face and notes) of 0000831259-26-000012; no face row matched |
| total_assets | mapped | us-gaap:Assets | R6.htm | Total assets | 58167000000 | 58167000000 | 54848000000 | 54848000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R6.htm | Accounts payable and accrued liabilities | 4565000000 | 4565000000 | 4057000000 | 4057000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R6.htm | Total current liabilities | 6019000000 | 6019000000 | 5496000000 | 5496000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R6.htm | Total liabilities | 27401000000 | 27401000000 | 26070000000 | 26070000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R6.htm | Total stockholders’ equity | 18899000000 | 18899000000 | 17581000000 | 17581000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R6.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R5.htm | Net cash provided by (used in) operating activities | 5610000000 | 5610000000 | 7160000000 | 7160000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash provided by (used in) investing activities | -4472000000 | -4472000000 | -5028000000 | -5028000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash used in financing activities | -1876000000 | -1876000000 | -3284000000 | -3284000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R5.htm | Capital expenditures | -4494000000 | 4494000000 | -4808000000 | 4808000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R5.htm | Depreciation, depletion and amortization | 2244000000 | 2244000000 | 2241000000 | 2241000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Stock-based compensation | 121000000 | 121000000 | 109000000 | 109000000 | Y | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R5.htm | Common stock | -865000000 | 865000000 | -865000000 | 865000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R5.htm | Treasury stock purchases | -107000000 | 107000000 | -59000000 | 59000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000831259-26-000012 R5.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R50.htm | ACCOUNTS PAYABLE AND ACCRUED LIABILITIES (Details) |  | 256000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R50.htm 'ACCOUNTS PAYABLE AND ACCRUED LIABILITIES (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R68.htm | INCOME TAXES (Income Taxes Paid) (Details) |  | 2898000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R68.htm 'INCOME TAXES (Income Taxes Paid) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R6.htm | Current portion of debt + Long-term debt, less current portion | 9379000000 | 9379000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | not_presented |  | R6.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CommonStockSharesOutstanding in MetaLinks.json (1241 tags across all 99 R pages, face and notes) of 0000831259-26-000012; no face row matched |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Revenues' on us-gaap:SalesRevenueNet = 15877000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Total cost of sales' on us-gaap:CostOfGoodsSold = 28524000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 29259000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 569000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Operating (loss) income' on us-gaap:OperatingIncomeLoss = -13382000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Interest expense, net' on fcx:InterestExpenseIncludingAccretion = -645000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000831259-16-000062 R2.htm prints '(Loss) income before income taxes and equity in affiliated companies' net (losse' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -14021000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Benefit from (provision for) income taxes' on us-gaap:IncomeTaxExpenseBenefit = 1935000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Net (loss) income attributable to common stockholders' on us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic = -12236000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = -11.31 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = -11.31 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 1082000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000831259-16-000062 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 1082000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 224000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Trade accounts receivable' on us-gaap:AccountsReceivableNetCurrent = 689000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 7462000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Property, plant, equipment and mining development costs, net' on us-gaap:PropertyPlantAndEquipmentNet = 27509000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Total assets' on us-gaap:Assets = 46577000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 3355000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 4307000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Total liabilities' on us-gaap:Liabilities = 33769000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000831259-16-000062 R5.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 7828000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000831259-16-000062 R4.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 3220000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000831259-16-000062 R4.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -6246000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000831259-16-000062 R4.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 2786000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000831259-16-000062 R4.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0000831259-16-000062 R4.htm prints 'Depreciation, depletion and amortization' on us-gaap:CostOfGoodsSoldDepreciationDepletionAndAmortization = 3497000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000831259-16-000062 R4.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 85000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000831259-16-000062 R4.htm prints 'Common stock' on us-gaap:PaymentsOfDividendsCommonStock = -605000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0000831259-16-000062 R4.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0000831259-16-000062 R4.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0000831259-16-000062 R4.htm read; no row matched (auto)
- diluted_eps: era 10-K 0000831259-18-000008 R2.htm prints 'Earnings per share, basic and diluted (in dollars per share)' on us-gaap:EarningsPerShareBasicAndDiluted = 1.25 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0000831259-25-000006 R5.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ExplorationExpense+us-gaap:EnvironmentalRemediationExpense+us-gaap:GainLossOnDispositionOfAssets1 (R3.htm): 2026-11-12 R3.htm: corrected: lines after 'Total cost of sales': 545 + 192 + 58 - 16 = 779 = 25,915 - 18,618 - 6,518 (FY2024 796 ties)
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- goodwill: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R50.htm): 2026-11-12 R50.htm: agree: value in the note is the full data point; agree
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R68.htm): 2026-11-12 R68.htm: agree: value in the note is the full data point; agree
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R6.htm): 2026-11-12 R6.htm: agree: R6 466 + 8,913
- shares_outstanding: not_presented  (R6.htm): 2026-11-12 R6.htm: agree: whole-filing check agrees; nothing printed; only issued and treasury shares printed
- revenue: mapped us-gaap:Revenues (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Revenues' is the revenue line, printed 25915000000 = filing XBRL 25915000000; agrees
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Diluted' is the weighted_diluted_shares line, printed 1443000000 = filing XBRL 1443000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Total current assets' is the current_assets line, printed 13790000000 = filing XBRL 13790000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: BS R6.htm 'Property, plant, equipment and mine development co' is the ppe_net line, printed 40736000000 = filing XBRL 40736000000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: CF R5.htm 'Stock-based compensation' is the sbc line, printed 121000000 = filing XBRL 121000000; agrees
- share_buybacks: mapped us-gaap:PaymentsForRepurchaseOfCommonStock (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: CF R5.htm 'Treasury stock purchases' is the share_buybacks line, printed -107000000 = filing XBRL 107000000; agrees
- interest_expense: combined us-gaap:InterestIncomeExpenseNet (R3.htm): net line; map via override only if the note shows net of capitalized interest alone
- interest_expense: override test failed: the filing shows no gross interest minus capitalized interest tie (R14 DEBT note has no interest breakdown; R48 'Capitalized interest' 342 is a PP&E balance, not the year's capitalized amount); stays combined (Dhairya condition 2026-11-12)
