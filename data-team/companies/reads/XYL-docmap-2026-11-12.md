# XYL document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001524472-26-000012 (CIK 0001524472, filed 2026-02-25): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R7.htm
- 10-K 0001524472-16-000027 (CIK 0001524472, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001524472-18-000006 (CIK 0001524472, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001524472-20-000006 (CIK 0001524472, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- companyfacts CIK0001524472.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 9035000000 | 9035000000 | 8562000000 | 8562000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of revenue | 5560000000 | 5560000000 | 5350000000 | 5350000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 3475000000 | 3475000000 | 3212000000 | 3212000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+xyl:RestructuringAndAssetImpairmentLosses | R3.htm | Selling, general and administrative expenses + Research and development expenses + Restructuring and asset impairment ch | 2252000000 |  | 2203000000 |  | API missing | FILING-CHECKED | every face line between gross profit and operating income; ties to GP - OI / accn 0001524472-26-000012 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 1923000000 | 1923000000 | 1911000000 | 1911000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research and development expenses | 226000000 | 226000000 | 230000000 | 230000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 1223000000 | 1223000000 | 1009000000 | 1009000000 | Y | FILING-CHECKED | accn 0001524472-26-000012 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -29000000 | 29000000 | -44000000 | 44000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R3.htm | Income before taxes | 1181000000 | 1181000000 | 1087000000 | 1087000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | -231000000 | 231000000 | -197000000 | 197000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Xylem | 957000000 | 957000000 | 890000000 | 890000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 3.93 | 3.93 | 3.67 | 3.67 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 3.92 | 3.92 | 3.65 | 3.65 | Y | FILING-CHECKED | accn 0001524472-26-000012 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 243366000 | 243366000 | 242583000 | 242583000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 243994000 | 243994000 | 243521000 | 243521000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 1479000000 | 1479000000 | 1121000000 | 1121000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables, less allowances for discounts, returns and credit losses of $68 and $59 in 2025 and 2024, respectively | 1759000000 | 1759000000 | 1668000000 | 1668000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories | 983000000 | 983000000 | 996000000 | 996000000 | Y | FILING-CHECKED | accn 0001524472-26-000012 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 4641000000 | 4641000000 | 4098000000 | 4098000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 1159000000 | 1159000000 | 1152000000 | 1152000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 8332000000 | 8332000000 | 7980000000 | 7980000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 17634000000 | 17634000000 | 16493000000 | 16493000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 1013000000 | 1013000000 | 1006000000 | 1006000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 2856000000 | 2856000000 | 2336000000 | 2336000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 5885000000 | 5885000000 | 5611000000 | 5611000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders’ equity | 11480000000 | 11480000000 | 10642000000 | 10642000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net Cash — Operating activities | 1241000000 | 1241000000 | 1263000000 | 1263000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net Cash — Investing activities | -471000000 | -471000000 | -482000000 | -482000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net Cash — Financing activities | -501000000 | -501000000 | -615000000 | -615000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Capital expenditures | -331000000 | 331000000 | -321000000 | 321000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation+us-gaap:AdjustmentForAmortization | R7.htm | Depreciation | 575000000 |  | 562000000 |  |  | FILING-CHECKED | CF R7 Depreciation 267 + Amortization 308 / check: hand R7.htm corrected: CF prints Depreciation 267 and Amortization 308 as separate lines; component sum must include both = 575M (FY1 258 + 304 = 562). |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Share-based compensation | 53000000 | 53000000 | 56000000 | 56000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid | -391000000 | 391000000 | -350000000 | 350000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | -15000000 | 15000000 | -20000000 | 20000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest | 61000000 | 61000000 | 67000000 | 67000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Income taxes (net of refunds received) | 267000000 | 267000000 | 219000000 | 219000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001524472-26-000012 R7.htm period ..2025-12-31 |
| total_debt | component_in_note | xyl:ShortTermDebtAndLongTermDebtCurrentMaturities+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent | R5.htm | Long-term debt, net | 2067000000 |  | 2119000000 |  |  | FILING-CHECKED | BS R5 short-term/current debt 534 (extension tag) + long-term debt 1,408 + finance lease liabilities current 34 and noncurrent 91 from leases note R84 (classified in accrued liabilities) / check: hand R5.htm corrected: Missing the face line 'Short-term borrowings and current maturities of long-term debt' 534 (xyl extension); finance lease liabilities 34 + 91 sit in accrued liabilities (R84) -> 534 + 1,408 + 34 + 91 = 2,067 (FY1 38 + 1,978 + 27 + 76 = 2,119). |
| shares_outstanding | not_presented |  |  | Capital Stock (Changes in Common Stock Outstanding) (Details) |  |  |  |  |  | FILING-CHECKED | no CommonStockSharesOutstanding on face or BS parenthetical (R6: issued 259.9M, treasury 16.3M); note R127 shows ending balance 243,584K / check: hand R6.htm corrected: BS parenthetical prints only issued 259.9M and treasury 16.3M; outstanding 243,584K appears only in the capital stock note R127, which rule 8 does not accept -> not_presented. |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 3653000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Cost of revenue' on us-gaap:CostOfRevenue = 2249000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 1404000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Selling, general and administrative expenses + Research and development expenses' on us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:RestructuringSettlementAndI = 955000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 854000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Research and development expenses' on us-gaap:ResearchAndDevelopmentExpense = 95000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 449000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Interest expense' on us-gaap:InterestExpense = 55000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Income before taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 403000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 63000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 340000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.88 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.87 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 180893000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001524472-16-000027 R2.htm prints 'Weighted average common shares outstanding — Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 181737000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 680000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Receivables, less allowances for discounts, returns and doubtful accounts of $33' on us-gaap:AccountsReceivableNetCurrent = 749000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 433000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2005000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 439000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 1584000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Total assets' on us-gaap:Assets = 4657000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 338000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 823000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 2573000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001524472-16-000027 R4.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 2084000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Net Cash — Operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 464000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Net Cash — Investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -132000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Net Cash — Financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -262000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -117000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001524472-16-000027 R6.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 15000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividendsCommonStock = -102000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -179000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Interest' on us-gaap:InterestPaid = 52000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001524472-16-000027 R6.htm prints 'Income taxes (net of refunds received)' on us-gaap:IncomeTaxesPaidNet = 75000000 (FILING-CHECKED)
- revenue: era 10-K 0001524472-18-000006 R2.htm prints 'Revenue' on us-gaap:SalesRevenueNet = 4707000000 (FILING-CHECKED)
- revenue: era 10-K 0001524472-20-000006 R2.htm prints 'Revenue' on us-gaap:Revenues = 5249000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (us-gaap:SellingGeneralAndAdministrativeExpense+us-gaap:ResearchAndDevelopmentExpense+xyl:RestructuringAndAssetImpairmentLosses)

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 7 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 3.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
