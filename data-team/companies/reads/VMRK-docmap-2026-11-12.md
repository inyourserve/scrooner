# VMRK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-051433 (CIK 0000906107, filed 2026-02-13): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0000906107-16-000029 (CIK 0000906107, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R5.htm, CI R7.htm, CF R9.htm
- companyfacts CIK0000906107.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, RegulatedAndUnregulatedOperatingRevenue, RegulatedOperatingRevenue in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| cost_of_revenue | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total expenses | 2224207000 | 2224207000 | 2108409000 | 2108409000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 65280000 | 65280000 | 61653000 | 61653000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseDebt | R4.htm | Expense incurred, net | -306798000 | 306798000 | -285735000 | 285735000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R4.htm | Income before income and other taxes, income (loss) from investments in unconsolidated entities and net gain (loss) on s | 1172529000 | 1172529000 | 1081205000 | 1081205000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income and other tax (expense) benefit | -1585000 | 1585000 | -1256000 | 1256000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income attributable to controlling interests | 1120089000 | 1120089000 | 1035831000 | 1035831000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income available to Common Shares | 2.95 | 2.95 | 2.73 | 2.73 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income available to Common Shares | 2.94 | 2.94 | 2.72 | 2.72 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average Common Shares outstanding | 379610000 | 379610000 | 378795000 | 378795000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average Common Shares outstanding | 390411000 | 390411000 | 390740000 | 390740000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 55904000 | 55904000 | 62302000 | 62302000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R2.htm period ..2025-12-31 |
| accounts_receivable | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsReceivableNetCurrent, ReceivablesNetCurrent in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| inventory | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| ppe_net | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| goodwill | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Goodwill in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 20746023000 | 20746023000 | 20834176000 | 20834176000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | eqr:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrentOtherThanInterestAndDividendPayable | R2.htm | Accounts payable and accrued expenses | 109165000 |  | 99347000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-051433 R2.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1716 tags across all 141 R pages, face and notes) of 0001193125-26-051433; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 9336889000 | 9336889000 | 9249829000 | 9249829000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total shareholders’ equity | 11041499000 | 11041499000 | 11044560000 | 11044560000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 1648763000 | 1648763000 | 1573607000 | 1573607000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash provided by (used for) investing activities | -321362000 | -321362000 | -1176484000 | -1176484000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used for) financing activities | -1328713000 | -1328713000 | -376952000 | -376952000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| capex | mapped | eqr:PaymentsForCapitalExpendituresToRealEstate | R6.htm | Capital expenditures to real estate | -342040000 |  | -301434000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R6.htm | Depreciation | 1010400000 | 1010400000 | 952191000 | 952191000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Compensation paid with Company Common Shares | 32210000 | 32210000 | 31287000 | 31287000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Common Shares | -1046247000 | 1046247000 | -1019050000 | 1019050000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Common Shares repurchased and retired | -280720000 | 280720000 | -38474000 | 38474000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Cash paid for interest, net of amounts capitalized | 274153000 | 274153000 | 241034000 | 241034000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R6.htm | Net cash paid (received) for income and other taxes | 1121000 | 1121000 | 1339000 | 1339000 | Y | FILING-CHECKED | accn 0001193125-26-051433 R6.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R98.htm | Debt - Summary of Aggregate Payments of Principal on All Debt (Details) |  | 8241242000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R98.htm 'Debt - Summary of Aggregate Payments of Principal on All Debt (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common Stock, Shares, Outstanding | 377806173 | 377806173 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- operating_expenses: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Total expenses' on us-gaap:CostsAndExpenses = 1736145000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000906107-16-000029 R5.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 65082000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Expense incurred, net' on us-gaap:InterestExpenseDebt = -444069000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Income (loss) before income and other taxes, income (loss) from investments in u' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 558380000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Income and other tax (expense) benefit' on us-gaap:IncomeTaxExpenseBenefit = -917000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Net income attributable to controlling interests' on us-gaap:NetIncomeLoss = 870120000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Net income available to Common Shares' on us-gaap:EarningsPerShareBasic = 2.37 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Net income available to Common Shares' on us-gaap:EarningsPerShareDiluted = 2.36 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Weighted average Common Shares outstanding' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 363498000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000906107-16-000029 R5.htm prints 'Weighted average Common Shares outstanding' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 380620000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000906107-16-000029 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 42276000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000906107-16-000029 R2.htm prints 'Total assets' on us-gaap:Assets = 23157328000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000906107-16-000029 R2.htm prints 'Accounts payable and accrued expenses' on eqr:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrentOtherThanInterestAndDividendPayable = 187124000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000906107-16-000029 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 11894190000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000906107-16-000029 R2.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 10470368000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1356499000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Net cash (used for) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -678471000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Net cash (used for) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -675832000 (FILING-CHECKED)
- capex: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Capital expenditures to real estate' on us-gaap:PaymentsForCapitalImprovements = -182113000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000906107-16-000029 R9.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Compensation paid with Company Common Shares' on us-gaap:ShareBasedCompensation = 34607000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000906107-16-000029 R9.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Common Shares repurchased and retired' on us-gaap:PaymentsForRepurchaseOfCommonStock = 0 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Cash paid for interest, net of amounts capitalized' on us-gaap:InterestPaidNet = 436748000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000906107-16-000029 R9.htm prints 'Net cash paid for income and other taxes' on us-gaap:IncomeTaxesPaidNet = 1264000 (FILING-CHECKED)

## Mismatches (printed vs API)
- accounts_payable: API missing (eqr:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrentOtherThanInterestAndDividendPayable)
- capex: API missing (eqr:PaymentsForCapitalExpendituresToRealEstate)
