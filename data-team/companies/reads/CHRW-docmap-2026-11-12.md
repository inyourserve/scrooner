# CHRW document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001043277-26-000009 (CIK 0001043277, filed 2026-02-13): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0001043277-16-000020 (CIK 0001043277, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001043277-18-000007 (CIK 0001043277, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001043277-21-000009 (CIK 0001043277, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0001043277.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 16232763000 | 16232763000 | 17724956000 | 17724956000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Purchased services and products | 12235163000 |  | 13719935000 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (823 tags across all 89 R pages, face and notes) of 0001043277-26-000009; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 15437802000 | 15437802000 | 17055815000 | 17055815000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:OtherSellingGeneralAndAdministrativeExpense | R5.htm | Other selling, general, and administrative expenses | 564291000 | 564291000 | 639624000 | 639624000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (823 tags across all 89 R pages, face and notes) of 0001043277-26-000009; HAND REVIEW: 3 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsTaxCreditCarryforwards 'Tax credit carryforward / Deferred Tax Assets, Tax Credit Ca' R60; us-gaap:EffectiveIncomeTaxRateReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R58; us-gaap:IncomeTaxReconciliationTaxCredits 'Tax credits / Effective Income Tax Rate Reconciliation, Tax ' R58 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 794961000 | 794961000 | 669141000 | 669141000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (823 tags across all 89 R pages, face and notes) of 0001043277-26-000009; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:UnrecognizedTaxBenefitsIncomeTaxPenaltiesAndInterestExpense 'Interest and penalties recognized / Unrecognized Tax Benefit' R54 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before provision for income taxes | 722457000 | 722457000 | 579204000 | 579204000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 135376000 | 135376000 | 113514000 | 113514000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 587081000 | 587081000 | 465690000 | 465690000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in dollars per share) | 4.88 | 4.88 | 3.89 | 3.89 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in dollars per share) | 4.83 | 4.83 | 3.86 | 3.86 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted average shares outstanding (in shares) | 120242000 | 120242000 | 119805000 | 119805000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted average shares outstanding (in shares) | 121502000 | 121502000 | 120679000 | 120679000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 160871000 | 160871000 | 145762000 | 145762000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R3.htm | Receivables, net of allowance for credit loss of $14,420 and $13,285 | 2360829000 | 2360829000 | 2383709000 | 2383709000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (823 tags across all 89 R pages, face and notes) of 0001043277-26-000009; label search over every tag in the filing (custom included) found no candidate |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2798543000 | 2798543000 | 2969603000 | 2969603000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Net property and equipment | 116362000 | 116362000 | 127189000 | 127189000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1457976000 | 1457976000 | 1428965000 | 1428965000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 5058381000 | 5058381000 | 5297926000 | 5297926000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 1210295000 | 1210295000 | 1178335000 | 1178335000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1831702000 | 1831702000 | 2324898000 | 2324898000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 3212734000 | 3212734000 | 3575875000 | 3575875000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ investment | 1845647000 | 1845647000 | 1722051000 | 1722051000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 914519000 | 914519000 | 509084000 | 509084000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used for investing activities | -54670000 | -54670000 | -74288000 | -74288000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used for financing activities | -862748000 | -862748000 | -416099000 | -416099000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -19628000 | 19628000 | -22653000 | 22653000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 102818000 | 102818000 | 97160000 | 97160000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 80070000 | 80070000 | 84590000 | 84590000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Cash dividends | -301376000 | 301376000 | -294772000 | 294772000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -354652000 | 354652000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 63209000 | 63209000 | 86124000 | 86124000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001043277-26-000009 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R54.htm | Income taxes paid | 95047000 | 95047000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R54.htm 'INCOME TAXES - Narrative (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Current portion of debt + Long-term debt | 1089438000 | 1089438000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 118429000 | 118429000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Total revenues' on us-gaap:Revenues = 13476084000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Purchased products sourced for resale' on us-gaap:CostOfGoodsSold = 1365333000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 12617774000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Other selling, general, and administrative expenses' on us-gaap:OtherSellingGeneralAndAdministrativeExpense = 358760000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 858310000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 822781000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 313082000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 509699000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Basic net income per share (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.52 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Diluted net income per share (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.51 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Basic weighted average shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 144967000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001043277-16-000020 R4.htm prints 'Diluted weighted average shares outstanding (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 145349000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 168229000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Receivables, net of allowance for doubtful accounts of $43,455 and $41,051' on us-gaap:ReceivablesNetCurrent = 1505620000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1730698000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Net property and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 190874000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1108337000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Total assets' on us-gaap:Assets = 3184358000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 697585000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1448597000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2033908000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001043277-16-000020 R2.htm prints 'Total stockholders’ investment' on us-gaap:StockholdersEquity = 1150450000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 718336000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Net cash used for investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -54446000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Net cash used for financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -607741000 (FILING-CHECKED)
- capex: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -28115000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 66409000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 57661000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Cash dividends' on us-gaap:PaymentsOfDividends = -235615000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -229863000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 28537000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001043277-16-000020 R7.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 311800000 (FILING-CHECKED)
- revenue: era 10-K 0001043277-18-000007 R4.htm prints 'Total revenues' on us-gaap:Revenues = 14869380000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001043277-18-000007 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 37871000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001043277-21-000009 R4.htm prints 'Income before provision for income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 628331000 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold)

## Hand check (check: hand = the R page opened by the reader; every row also check: machine-full-filing)
- checked 3 rows: every not_presented / combined / component / NOTE row + 3 random mapped (seed 501-600:CHRW); disagree on the mapped sample: 0/3
- cfo: agree (R8 net cash provided by operating activities 914,519)
- income_before_tax: agree (R5 Income before provision for income taxes 722,457)
- weighted_basic_shares: agree (R5 basic weighted shares 120,242 thousand)
