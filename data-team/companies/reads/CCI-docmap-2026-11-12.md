# CCI document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001051470-26-000016 (CIK 0001051470, filed 2026-02-23): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R6.htm
- 10-K 0001051470-16-000158 (CIK 0001051470, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- 10-K 0001051470-18-000082 (CIK 0001051470, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R5.htm
- 10-K 0001051470-25-000089 (CIK 0001051470, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R6.htm
- companyfacts CIK0001051470.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Net Revenues | 4264000000 | 4264000000 | 4460000000 | 4460000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Services and other | 113000000 | 113000000 | 107000000 | 107000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (972 tags across all 86 R pages, face and notes) of 0001051470-26-000016; no face row matched / check: hand R5.htm agree |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating expenses | 2189000000 | 2189000000 | 2342000000 | 2342000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001051470-26-000016 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 383000000 | 383000000 | 435000000 | 435000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (972 tags across all 86 R pages, face and notes) of 0001051470-26-000016; no face row matched / check: hand R5.htm agree |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income (loss) | 2075000000 | 2075000000 | 2118000000 | 2118000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestExpenseDebt | R5.htm | Interest expense and amortization of deferred financing costs, net | 972000000 | 972000000 | 932000000 | 932000000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest | 1119000000 | 1119000000 | 1180000000 | 1180000000 | Y | FILING-CHECKED | accn 0001051470-26-000016 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Benefit (provision) for income taxes | -16000000 | 16000000 | -18000000 | 18000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income (Loss) | 444000000 | 444000000 | -3903000000 | -3903000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.02 | 1.02 | -8.98 | -8.98 | Y | FILING-CHECKED | accn 0001051470-26-000016 R5.htm period ..2025-12-31 / check: hand R5.htm agree |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.01 | 1.01 | -8.98 | -8.98 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 435000000 | 435000000 | 434000000 | 434000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 437000000 | 437000000 | 434000000 | 434000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 99000000 | 99000000 | 100000000 | 100000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Receivables, net of allowance of $9 and $9, respectively | 172000000 | 172000000 | 129000000 | 129000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (972 tags across all 86 R pages, face and notes) of 0001051470-26-000016; no face row matched / check: hand R3.htm agree |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1144000000 | 1144000000 | 1090000000 | 1090000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 6273000000 | 6273000000 | 6577000000 | 6577000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5127000000 | 5127000000 | 5127000000 | 5127000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 31518000000 | 31518000000 | 32736000000 | 32736000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 71000000 | 71000000 | 48000000 | 48000000 | Y | FILING-CHECKED | accn 0001051470-26-000016 R3.htm period ..2025-12-31 / check: hand R3.htm agree |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4479000000 | 4479000000 | 2177000000 | 2177000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 33153000000 | 33153000000 | 32869000000 | 32869000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Total equity (deficit) | -1635000000 |  | -133000000 |  |  | FILING-CHECKED | face total equity tagged with the incl-NCI tag; company has no noncontrolling interest line, so it equals parent equity / check: hand R3.htm corrected: R3 prints 'Total equity (deficit)' (1,635) / (133) under StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest; no NCI line exists, so it is the shareholders' equity line. |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by (used for) operating activities | 3057000000 | 3057000000 | 2943000000 | 2943000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash provided by (used for) investing activities | -1158000000 | -1158000000 | -1220000000 | -1220000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used for) financing activities | -1886000000 | -1886000000 | -1708000000 | -1708000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R6.htm | Payments to Acquire Productive Assets | -182000000 | 182000000 | -176000000 | 176000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R6.htm | Depreciation, amortization and accretion | 690000000 | 690000000 | 736000000 | 736000000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock-based compensation expense, net | 73000000 | 73000000 | 84000000 | 84000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Dividends/distributions paid on common stock | -2080000000 | -2080000000 | -2729000000 | -2729000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Purchases of common stock | -23000000 | -23000000 | -33000000 | -33000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001051470-26-000016 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R82.htm | Statement of Cash Flows, Supplemental Information (Details) | 965000000 | 965000000 | 895000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R82.htm 'Statement of Cash Flows, Supplemental Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R82.htm corrected: R82 'Interest paid' (InterestPaidNet) 965 / 895; printed values were blank. |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R82.htm | Statement of Cash Flows, Supplemental Information (Details) | 15000000 | 15000000 | 10000000 |  | Y | FILING-CHECKED | not on the face statement; shown in R82.htm 'Statement of Cash Flows, Supplemental Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession / check: hand R82.htm corrected: R82 'Income taxes paid (refund)' (IncomeTaxesPaidNet) 15 / 10; printed values were blank. |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of debt and other obligations + Debt and other long-term obligations | 24337000000 | 24337000000 | 24054000000 |  | Y | FILING-CHECKED | sum of printed BS debt lines; finance leases/installment purchases already inside LongTermDebtAndCapitalLeaseObligations and current maturities 'and other obligations' / check: hand R3.htm corrected: R3 'Current maturities of debt and other obligations' 2,783 + 'Debt and other long-term obligations' 21,554 (LongTermDebtAndCapitalLeaseObligations, finance leases inside by tag) = 24,337; FY24 603 + 23,451 = 24,054 was blank. |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding | 435000000 | 435000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 3663851000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Network services and other' on us-gaap:CostOfServices = 357557000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Total operating expenses' on us-gaap:CostsAndExpenses = 2717671000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001051470-16-000158 R4.htm prints 'General and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 310921000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Operating income (loss)' on us-gaap:OperatingIncomeLoss = 946180000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Interest expense and amortization of deferred financing costs' on cci:InterestExpenseAndAmortizationOfDeferredFinancingCosts = -527128000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Income (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 473829000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Benefit (provision) for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 51457000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Net income (loss) attributable to CCIC stockholders' on us-gaap:NetIncomeLoss = 1520992000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 4.44 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 4.42 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 333002000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001051470-16-000158 R4.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 334062000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 178810000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Receivables, net of allowance of $9,574 and $10,037, respectively' on us-gaap:AccountsReceivableNetCurrent = 313296000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 981245000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 9580057000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 5513551000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Total assets' on us-gaap:Assets = 22036245000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 159629000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 855369000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001051470-16-000158 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 14947024000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Net cash provided by (used for) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1794025000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Net cash provided by (used for) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1959734000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Net cash provided by (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -935476000 (FILING-CHECKED)
- capex: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquireProductiveAssets = -908892000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Depreciation, amortization and accretion' on us-gaap:DepreciationAmortizationAndAccretionNet = 1036178000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Stock-based compensation expense' on us-gaap:ShareBasedCompensation = 60773000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Dividends/distributions paid on common stock' on us-gaap:PaymentsOfDividendsCommonStock = -1116444000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001051470-16-000158 R5.htm prints 'Purchases of capital stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -29657000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001051470-16-000158 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001051470-16-000158 R5.htm read; no row matched (auto)
- revenue: era 10-K 0001051470-18-000082 R4.htm prints 'Net revenues' on us-gaap:SalesRevenueNet = 4355605000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001051470-18-000082 R4.htm prints 'Network services and other' on us-gaap:CostOfServices = 419787000 (FILING-CHECKED)
- net_income: era 10-K 0001051470-18-000082 R4.htm prints 'Net income (loss) attributable to CCIC stockholders' on us-gaap:NetIncomeLoss = 444550000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001051470-25-000089 R5.htm prints 'Income (Loss) Attributable to Parent, before Tax, Total' on us-gaap:IncomeLossAttributableToParent = -3879000000 (FILING-CHECKED)
- net_income: era 10-K 0001051470-25-000089 R5.htm prints 'Net Income (Loss), Including Portion Attributable to Noncontrolling Interest, To' on us-gaap:ProfitLoss = -3903000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 11 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 4.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
