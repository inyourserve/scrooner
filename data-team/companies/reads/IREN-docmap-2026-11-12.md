# IREN document-first map 2026-11-12 (rank 715, read-only)

Evidence: FILING-CHECKED unless a row says otherwise. Printed values come from the R pages of the 10-K on sec.gov; tags from each R-page row's element reference; API = SEC companyfacts (undimensioned, same accession, same period); FSN = our fsn.line rows for the same filing and report.

Company: IREN Limited (CIK 0001878848); sector shape read from the face: general.

## Filings opened
- Latest 10-K 0001878848-26-000052 (index from FSN store (fsn.filing, fsn.report)): R3.htm Consolidated Balance Sheets [BS], R4.htm Consolidated Balance Sheets (Parenthetical) [BSP], R5.htm Consolidated Statements of Operations and Comprehensive Income (Loss) [IS], R7.htm Consolidated Statements of Cash Flows [CF].
- Era 10-K 0001878848-25-000063 (FY2025): R3.htm Consolidated Balance Sheets, R5.htm Consolidated Statements of Operations and Comprehensive Income (Loss), R7.htm Consolidated Statements of Cash Flows.
- companyfacts: one call to data.sec.gov.
- sec.gov requests for this company: 0.

FY0 = the latest fiscal-year column, FY1 = the prior year. Values in full units (printed value × the R-page scale); EPS per share; shares in shares.

## Data points (the CSV holds exactly these rows)
| data point | status | tag(s) | R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match |
|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 707007000 | 707007000 | 501023000 | 501023000 | Y |
| cost_of_revenue | mapped | CostOfRevenue | R5.htm | Total segment and consolidated cost of revenue | -219706000 | 219706000 | -158992000 | 158992000 | Y (sign differs: printed in parentheses/negated label) |
| gross_profit | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| operating_expenses | not_presented |  |  |  |  |  |  |  | face lines between GP and OI sum to -3068029000, GP - OI = 1534015000: |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative expenses | -449115000 | 449115000 | -136458000 | 136458000 | Y (sign differs: printed in parentheses/negated label) |
| research_and_development | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| operating_income | mapped | OperatingIncomeLoss | R5.htm | Operating (loss) income | -1046714000 | -1046714000 | 17327000 | 17327000 | Y |
| interest_expense | mapped | InterestExpenseNonoperating | R5.htm | Finance expense | -59251000 | 59251000 | -11045000 | 11045000 | Y (sign differs: printed in parentheses/negated label) |
| interest_income | mapped | InvestmentIncomeInterest | R5.htm | Interest income | 80631000 | 80631000 | 7504000 | 7504000 | Y |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | R5.htm | Other non-operating income | 72000 | 72000 | 817000 | 817000 | Y |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before taxes | -708683000 | -708683000 | 93501000 | 93501000 | Y |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R5.htm | Income tax (expense) benefit | 6062000 | -6062000 | -6560000 | 6560000 | Y (sign differs: printed in parentheses/negated label) |
| net_income | mapped | NetIncomeLoss | R5.htm | Net income (loss) | -702621000 | -702621000 | 86941000 | 86941000 | Y |
| basic_eps | mapped | EarningsPerShareBasic | R5.htm | Basic net income (loss) per share of Ordinary shares ( in USD per shar | -2.22 | -2.22 | 0.41 | 0.41 | Y |
| diluted_eps | mapped | EarningsPerShareDiluted | R5.htm | Diluted net income (loss) per share of Ordinary shares (in USD per sha | -2.22 | -2.22 | 0.39 | 0.39 | Y |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted-average shares used in computing net income (loss) per  | 316123145 | 316123145 | 214586767 | 214586767 | Y |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted-average shares used in computing net income (loss) pe | 316123145 | 316123145 | 223245651 | 223245651 | Y |
| dividends_per_share | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| comprehensive_income | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 5895591000 | 5895591000 | 564526000 | 564526000 | Y |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 21062000 | 21062000 | 1564000 | 1564000 | Y |
| inventory | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| current_assets | mapped | AssetsCurrent | R3.htm | Total current assets | 7886176000 | 7886176000 | 641173000 | 641173000 | Y |
| ppe_net | mapped | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property, plant and equipment, net | 6753183000 | 6753183000 | 1930567000 | 1930567000 | Y |
| goodwill | mapped | Goodwill | R3.htm | Goodwill | 36577000 | 36577000 | 0 | 0 | Y |
| total_assets | mapped | Assets | R3.htm | Total assets | 15790039000 | 15790039000 | 2940323000 | 2940323000 | Y |
| accounts_payable | combined | AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 1825392000 | 1825392000 | 144115000 | 144115000 | Y |
| current_liabilities | mapped | LiabilitiesCurrent | R3.htm | Total current liabilities | 2221100000 | 2221100000 | 149347000 | 149347000 | Y |
| total_liabilities | mapped | Liabilities | R3.htm | Total liabilities | 11604426000 | 11604426000 | 1122835000 | 1122835000 | Y |
| total_debt | component sum | FinanceLeaseLiabilityCurrent;LongTermDebtCurrent;FinanceLeaseLiabilityNoncurrent;LongTermDebtNoncurrent | R3.htm | Finance lease liability, current portion + Debt, current portion + Fin | 7836740000 | 7836740000 | 962765000 | 962765000 | Y |
| stockholders_equity | mapped | StockholdersEquity | R3.htm | Total stockholders' equity | 4185613000 | 4185613000 | 1817488000 | 1817488000 | Y |
| shares_outstanding | component sum | CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) + Common stock, shares ou | 380193610 |  | 258103211 |  | dimensional: class members (companyfacts holds no member facts) |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash from (used in) operating activities | 2100418000 | 2100418000 | 245886000 | 245886000 | Y |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash from (used in) investing activities | -4722984000 | -4722984000 | -1380487000 | -1380487000 | Y |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash from (used in) financing activities | 9680050000 | 9680050000 | 1294735000 | 1294735000 | Y |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Payments for property, plant and equipment, net of computer hardware | -2998006000 | 2998006000 | -573456000 | 573456000 | Y (sign differs: printed in parentheses/negated label) |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 417729000 | 417729000 | 181136000 | 181136000 | Y |
| amortization_of_intangibles | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| sbc | mapped | ShareBasedCompensation | R7.htm | Stock-based compensation expense | 205023000 | 205023000 | 42642000 | 42642000 | Y |
| dividends_paid | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| share_buybacks | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsAndOtherReceivables | R7.htm | Accounts receivable and other receivables | -29434000 | 29434000 | -9656000 | 9656000 | Y (sign differs: printed in parentheses/negated label) |
| cf_inventory_change | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | R7.htm | Accounts payable and accrued expenses | 38017000 | 38017000 | 16689000 | 16689000 | Y |
| cash_paid_for_interest | mapped | InterestPaidNet | R7.htm | Cash paid for interest | -42639000 | 42639000 | -7634000 | 7634000 | Y (sign differs: printed in parentheses/negated label) |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | R7.htm | Cash paid for income taxes | -2696000 | 2696000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) |
| net_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| total_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_expense | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| provision_for_credit_losses | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| deposits | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| loans_net | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |

Sector lines also on the face (not in the graded vocabulary): intangibles_net = IntangibleAssetsNetExcludingGoodwill 'Intangible assets, net' 317432000.

## Eras FY2015 to FY2026 (every data point; companyfacts tag per original 10-K, and the era 10-Ks opened: FY2015 always, plus the last 10-K of each earlier era)
- First 10-K in companyfacts is FY2025: no FY2015 10-K exists for this registrant.
| data point | latest status | eras (companyfacts) | era 10-K reads (FILING-CHECKED) | coverage |
|---|---|---|---|---|
| revenue | mapped | FY2025-FY2026: Revenues | FY2025 10-K 0001878848-25-000063 R5.htm 'Total revenue' RevenueFromContractWithCustomerExcludingAssessedTax (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cost_of_revenue | mapped | FY2025-FY2026: CostOfRevenue | FY2025 10-K 0001878848-25-000063 R5.htm 'Total cost of revenue' CostOfRevenue (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| sga_expense | mapped | FY2025-FY2026: SellingGeneralAndAdministrativeExpense | FY2025 10-K 0001878848-25-000063 R5.htm 'Selling, general and administrative expe' SellingGeneralAndAdministrativeExpense (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| operating_income | mapped | FY2025-FY2026: OperatingIncomeLoss | FY2025 10-K 0001878848-25-000063 R5.htm 'Operating (loss) income' OperatingIncomeLoss (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| interest_expense | mapped | FY2025-FY2026: InterestExpenseNonoperating | FY2025 10-K 0001878848-25-000063 R5.htm 'Finance expense' InterestExpenseNonoperating (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| interest_income | mapped | FY2025-FY2026: InvestmentIncomeInterest | FY2025 10-K 0001878848-25-000063 R5.htm 'Interest income' InvestmentIncomeInterest (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| other_income_expense_net | mapped | FY2025-FY2026: OtherNonoperatingIncomeExpense | FY2025 10-K 0001878848-25-000063 R5.htm 'Other non-operating income' OtherNonoperatingIncomeExpense (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| income_before_tax | mapped | FY2025-FY2026: IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | FY2025 10-K 0001878848-25-000063 R5.htm 'Income (loss) before taxes' IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| income_tax_expense | mapped | FY2025-FY2026: IncomeTaxExpenseBenefit | FY2025 10-K 0001878848-25-000063 R5.htm 'Income tax (provision) benefit' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| net_income | mapped | FY2025-FY2026: NetIncomeLoss | FY2025 10-K 0001878848-25-000063 R5.htm 'Net income (loss)' NetIncomeLoss (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| basic_eps | mapped | FY2025-FY2026: EarningsPerShareBasic | FY2025 10-K 0001878848-25-000063 R5.htm 'Basic net income (loss) per share of Ord' EarningsPerShareBasic (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| diluted_eps | mapped | FY2025-FY2026: EarningsPerShareDiluted | FY2025 10-K 0001878848-25-000063 R5.htm 'Diluted net income (loss) per share of O' EarningsPerShareDiluted (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| weighted_basic_shares | mapped | FY2025-FY2026: WeightedAverageNumberOfSharesOutstandingBasic | FY2025 10-K 0001878848-25-000063 R5.htm 'Basic weighted-average shares used in co' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| weighted_diluted_shares | mapped | FY2025-FY2026: WeightedAverageNumberOfDilutedSharesOutstanding | FY2025 10-K 0001878848-25-000063 R5.htm 'Diluted weighted-average shares used in ' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cash_and_equivalents | mapped | FY2025-FY2026: CashAndCashEquivalentsAtCarryingValue | FY2025 10-K 0001878848-25-000063 R3.htm 'Cash and cash equivalents' CashAndCashEquivalentsAtCarryingValue (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| accounts_receivable | mapped | FY2025-FY2026: AccountsReceivableNetCurrent | FY2025 10-K 0001878848-25-000063 R3.htm 'Accounts receivable, net' AccountsReceivableNetCurrent (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| current_assets | mapped | FY2025-FY2026: AssetsCurrent | FY2025 10-K 0001878848-25-000063 R3.htm 'Total current assets' AssetsCurrent (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| ppe_net | mapped | FY2025-FY2025: PropertyPlantAndEquipmentNet; FY2026-FY2026: PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | FY2025 10-K 0001878848-25-000063 R3.htm 'Property, plant and equipment, net' PropertyPlantAndEquipmentNet (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| goodwill | mapped | FY2025-FY2025: no standard tag; FY2026-FY2026: Goodwill | FY2025 10-K 0001878848-25-000063: no face line | coverage FY2025-FY2026 gaps FY2025 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2025) |
| total_assets | mapped | FY2025-FY2026: Assets | FY2025 10-K 0001878848-25-000063 R3.htm 'Total assets' Assets (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| accounts_payable | combined | FY2025-FY2026: AccountsPayableCurrent | FY2025 10-K 0001878848-25-000063 R3.htm 'Accounts payable and accrued expenses' AccountsPayableAndAccruedLiabilitiesCurrent (combined) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| current_liabilities | mapped | FY2025-FY2026: LiabilitiesCurrent | FY2025 10-K 0001878848-25-000063 R3.htm 'Total current liabilities' LiabilitiesCurrent (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| total_liabilities | mapped | FY2025-FY2026: Liabilities | FY2025 10-K 0001878848-25-000063 R3.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| total_debt | component sum | FY2025-FY2025: ConvertibleNotesPayableCurrent+ConvertibleLongTermNotesPayable; FY2026-FY2026: FinanceLeaseLiabilityCurrent+LongTermDebtCurrent+FinanceLeaseLiabilityNoncurrent+LongTermDebtNoncurrent+LongTermDebt+FinanceLeaseLiability | FY2025 10-K 0001878848-25-000063 R3.htm 'Convertible notes payable' ConvertibleLongTermNotesPayable (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| stockholders_equity | mapped | FY2025-FY2026: StockholdersEquity | FY2025 10-K 0001878848-25-000063 R3.htm 'Total stockholders' equity' StockholdersEquity (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| shares_outstanding | component sum | FY2025-FY2026: no standard tag | FY2025 10-K 0001878848-25-000063: no face line | coverage FY2025-FY2026 gaps FY2025,2026 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2025) |
| cfo | mapped | FY2025-FY2026: NetCashProvidedByUsedInOperatingActivities | FY2025 10-K 0001878848-25-000063 R7.htm 'Net cash used in operating activities' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cash_flow_investing | mapped | FY2025-FY2026: NetCashProvidedByUsedInInvestingActivities | FY2025 10-K 0001878848-25-000063 R7.htm 'Net cash from (used in) investing activi' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cash_flow_financing | mapped | FY2025-FY2026: NetCashProvidedByUsedInFinancingActivities | FY2025 10-K 0001878848-25-000063 R7.htm 'Net cash from (used in) financing activi' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| capex | mapped | FY2025-FY2026: PaymentsToAcquirePropertyPlantAndEquipment | FY2025 10-K 0001878848-25-000063 R7.htm 'Payments for property, plant and equipme' PaymentsToAcquirePropertyPlantAndEquipment (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| depreciation_and_amortization | mapped | FY2025-FY2026: DepreciationDepletionAndAmortization | FY2025 10-K 0001878848-25-000063 R7.htm 'Depreciation and amortization' DepreciationDepletionAndAmortization (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| sbc | mapped | FY2025-FY2026: ShareBasedCompensation | FY2025 10-K 0001878848-25-000063 R7.htm 'Stock-based compensation expense' ShareBasedCompensation (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cf_ar_change | mapped | FY2025-FY2026: IncreaseDecreaseInAccountsAndOtherReceivables | FY2025 10-K 0001878848-25-000063 R7.htm 'Accounts receivable and other receivable' IncreaseDecreaseInAccountsAndOtherReceivables (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cf_ap_change | combined | FY2025-FY2026: no standard tag | FY2025 10-K 0001878848-25-000063 R7.htm 'Accounts payable and accrued expenses' IncreaseDecreaseInAccountsPayableAndAccruedLiabilities (combined) FILING-CHECKED | coverage FY2025-FY2026 gaps FY2025,2026 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2025) |
| cash_paid_for_interest | mapped | FY2025-FY2026: InterestPaidNet | FY2025 10-K 0001878848-25-000063 R7.htm 'Cash paid for interest' InterestPaidNet (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |
| cash_paid_for_income_taxes | mapped | FY2025-FY2026: IncomeTaxesPaidNet | FY2025 10-K 0001878848-25-000063 R7.htm 'Cash paid for income taxes' IncomeTaxesPaidNet (mapped) FILING-CHECKED | coverage FY2025-FY2026 complete (first 10-K FY2025) |

## Quirks and mismatches (the filing decides)
- [combined_line] accounts_payable: us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent 'Accounts payable and accrued expenses' — combined line; never the pure concept (0001878848-26-000052 R3.htm 2026-06-30)
- [combined_line] cf_ap_change: us-gaap:IncreaseDecreaseInAccountsPayableAndAccruedLiabilities 'Accounts payable and accrued expenses' — combined line; never the pure concept (0001878848-26-000052 R7.htm 2026-06-30)
- [era_change] ppe_net: PropertyPlantAndEquipmentNet -> PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization 'Property, plant and equipment, net' — tag switch between the FY2025 10-K (0001878848-25-000063) and the FY2026 10-K (0001878848-26-000052) (0001878848-25-000063  FY2025 -> FY2026)
- [era_change] total_debt: ConvertibleNotesPayableCurrent+ConvertibleLongTermNotesPayable -> FinanceLeaseLiabilityCurrent+LongTermDebtCurrent+FinanceLeaseLiabilityNoncurrent+LongTermDebtNoncurrent+LongTermDebt+FinanceLeaseLiability 'Finance lease liability, current portion' — tag switch between the FY2025 10-K (0001878848-25-000063) and the FY2026 10-K (0001878848-26-000052) (0001878848-25-000063  FY2025 -> FY2026)

## Every face line (printed page → tag → FSN → companyfacts)
| R | stmt | # | label | tag | member | FY0 printed | FY0 API | match | in FSN |
|---|---|---|---|---|---|---|---|---|---|
| R3.htm | BS | 1 | Cash and cash equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue |  | 5895591000 | 5895591000 | Y | Y |
| R3.htm | BS | 2 | Restricted cash, current portion | us-gaap:RestrictedCashCurrent |  | 1670252000 | 1670252000 | Y | Y |
| R3.htm | BS | 3 | Accounts receivable, net | us-gaap:AccountsReceivableNetCurrent |  | 21062000 | 21062000 | Y | Y |
| R3.htm | BS | 4 | Deposits and prepaid expenses | us-gaap:PrepaidExpenseAndOtherAssetsCurrent |  | 189140000 | 189140000 | Y | Y |
| R3.htm | BS | 5 | Derivative assets | us-gaap:DerivativeAssetsCurrent |  | 0 | 0 | Y | Y |
| R3.htm | BS | 6 | Assets held for sale | us-gaap:AssetsHeldForSaleNotPartOfDisposalGroupCurrent |  | 72540000 | 72540000 | Y | Y |
| R3.htm | BS | 7 | Income taxes receivable | us-gaap:IncomeTaxesReceivable |  | 1122000 | 1122000 | Y | Y |
| R3.htm | BS | 8 | Other assets | us-gaap:OtherAssetsCurrent |  | 36469000 | 36469000 | Y | Y |
| R3.htm | BS | 9 | Total current assets | us-gaap:AssetsCurrent |  | 7886176000 | 7886176000 | Y | Y |
| R3.htm | BS | 10 | Property, plant and equipment, net | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization |  | 6753183000 | 6753183000 | Y | Y |
| R3.htm | BS | 11 | Intangible assets, net | us-gaap:IntangibleAssetsNetExcludingGoodwill |  | 317432000 | 317432000 | Y | Y |
| R3.htm | BS | 12 | Goodwill | us-gaap:Goodwill |  | 36577000 | 36577000 | Y | Y |
| R3.htm | BS | 13 | Operating lease right-of-use asset, net | us-gaap:OperatingLeaseRightOfUseAsset |  | 2720000 | 2720000 | Y | Y |
| R3.htm | BS | 14 | Restricted cash, less current portion | us-gaap:RestrictedCashNoncurrent |  | 53684000 | 53684000 | Y | Y |
| R3.htm | BS | 15 | Deposits and prepaid expenses | us-gaap:PrepaidExpenseAndOtherAssetsNoncurrent |  | 265956000 | 265956000 | Y | Y |
| R3.htm | BS | 16 | Financial assets | us-gaap:LongTermInvestments |  | 0 | 0 | Y | Y |
| R3.htm | BS | 17 | Derivative assets | us-gaap:DerivativeAssetsNoncurrent |  | 415641000 | 415641000 | Y | Y |
| R3.htm | BS | 18 | Other assets | us-gaap:OtherAssetsNoncurrent |  | 58670000 | 58670000 | Y | Y |
| R3.htm | BS | 19 | Total non-current assets | us-gaap:AssetsNoncurrent |  | 7903863000 | 7903863000 | Y | Y |
| R3.htm | BS | 20 | Total assets | us-gaap:Assets |  | 15790039000 | 15790039000 | Y | Y |
| R3.htm | BS | 21 | Accounts payable and accrued expenses | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent |  | 1825392000 | 1825392000 | Y | Y |
| R3.htm | BS | 22 | Operating lease liability, current portion | us-gaap:OperatingLeaseLiabilityCurrent |  | 555000 | 555000 | Y | Y |
| R3.htm | BS | 23 | Finance lease liability, current portion | us-gaap:FinanceLeaseLiabilityCurrent |  | 125340000 | 125340000 | Y | Y |
| R3.htm | BS | 24 | Debt, current portion | us-gaap:LongTermDebtCurrent |  | 169370000 | 169370000 | Y | Y |
| R3.htm | BS | 25 | Income taxes payable, current portion | us-gaap:AccruedIncomeTaxesCurrent |  | 0 | 0 | Y | Y |
| R3.htm | BS | 26 | Deferred revenue, current portion | us-gaap:DeferredRevenueCurrent |  | 46491000 | 46491000 | Y | Y |
| R3.htm | BS | 27 | Other liabilities, current portion | us-gaap:OtherLiabilitiesCurrent |  | 53952000 | 53952000 | Y | Y |
| R3.htm | BS | 28 | Total current liabilities | us-gaap:LiabilitiesCurrent |  | 2221100000 | 2221100000 | Y | Y |
| R3.htm | BS | 29 | Operating lease liability, less current portion | us-gaap:OperatingLeaseLiabilityNoncurrent |  | 2231000 | 2231000 | Y | Y |
| R3.htm | BS | 30 | Finance lease liability, less current portion | us-gaap:FinanceLeaseLiabilityNoncurrent |  | 118456000 | 118456000 | Y | Y |
| R3.htm | BS | 31 | Debt, less current portion | us-gaap:LongTermDebtNoncurrent |  | 7423574000 | 7423574000 | Y | Y |
| R3.htm | BS | 32 | Deferred revenue, less current portion | us-gaap:DeferredRevenueNoncurrent |  | 1796055000 | 1796055000 | Y | Y |
| R3.htm | BS | 33 | Deferred tax liabilities | us-gaap:DeferredIncomeTaxLiabilitiesNet |  | 30832000 | 30832000 | Y | Y |
| R3.htm | BS | 34 | Income taxes payable, less current portion | us-gaap:LiabilityForUncertainTaxPositionsNoncurrent |  | 4283000 | 4283000 | Y | Y |
| R3.htm | BS | 35 | Other liabilities, less current portion | us-gaap:OtherLiabilitiesNoncurrent |  | 7894000 | 7894000 | Y | Y |
| R3.htm | BS | 36 | Total non-current liabilities | us-gaap:LiabilitiesNoncurrent |  | 9383326000 | 9383326000 | Y | Y |
| R3.htm | BS | 37 | Total liabilities | us-gaap:Liabilities |  | 11604426000 | 11604426000 | Y | Y |
| R3.htm | BS | 38 | Commitments and contingencies (See Note 29) | us-gaap:CommitmentsAndContingencies |  |  |  |  | Y |
| R3.htm | BS | 39 | Additional paid-in capital | us-gaap:AdditionalPaidInCapital |  | -1647061000 | -1647061000 | Y | Y |
| R3.htm | BS | 40 | Retained earnings (accumulated deficit) | us-gaap:RetainedEarningsAccumulatedDeficit |  | -1298789000 | -1298789000 | Y | Y |
| R3.htm | BS | 41 | Accumulated other comprehensive income (loss) | us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax |  | -41424000 | -41424000 | Y | Y |
| R3.htm | BS | 42 | Total stockholders' equity | us-gaap:StockholdersEquity |  | 4185613000 | 4185613000 | Y | Y |
| R3.htm | BS | 43 | Total liabilities and stockholders' equity | us-gaap:LiabilitiesAndStockholdersEquity |  | 15790039000 | 15790039000 | Y | Y |
| R3.htm | BS | 44 | Common stock, par value (in USD per share) | us-gaap:CommonStockParOrStatedValuePerShare | us-gaap_CommonClassAMember | 0 |  | dimensional | Y |
| R3.htm | BS | 45 | Common stock per class | us-gaap:CommonStockValue | us-gaap_CommonClassAMember | 7172887000 |  | dimensional | Y |
| R3.htm | BS | 46 | Common stock, par value (in USD per share) | us-gaap:CommonStockParOrStatedValuePerShare | us-gaap_CommonClassBMember | 0 |  | dimensional | Y |
| R3.htm | BS | 47 | Common stock per class | us-gaap:CommonStockValue | us-gaap_CommonClassBMember | 0 |  | dimensional | Y |
| R4.htm | BSP | 1 | Common stock, par value (in USD per share) | us-gaap:CommonStockParOrStatedValuePerShare | us-gaap_CommonClassAMember | 0 |  | dimensional | N |
| R4.htm | BSP | 2 | Common stock, shares outstanding (in shares) | us-gaap:CommonStockSharesOutstanding | us-gaap_CommonClassAMember | 380193608 |  | dimensional | N |
| R4.htm | BSP | 3 | Common stock, shares issued (in shares) | us-gaap:CommonStockSharesIssued | us-gaap_CommonClassAMember | 380193608 |  | dimensional | N |
| R4.htm | BSP | 4 | Common stock, par value (in USD per share) | us-gaap:CommonStockParOrStatedValuePerShare | us-gaap_CommonClassBMember | 0 |  | dimensional | N |
| R4.htm | BSP | 5 | Common stock, shares outstanding (in shares) | us-gaap:CommonStockSharesOutstanding | us-gaap_CommonClassBMember | 2 |  | dimensional | N |
| R4.htm | BSP | 6 | Common stock, shares issued (in shares) | us-gaap:CommonStockSharesIssued | us-gaap_CommonClassBMember | 2 |  | dimensional | N |
| R4.htm | BSP | 7 | Common stock, shares authorized (in shares) | us-gaap:CommonStockSharesAuthorized | us-gaap_CommonClassBMember | 2 |  | dimensional | N |
| R5.htm | IS | 1 | Total revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |  | 707007000 | 707007000 | Y | Y |
| R5.htm | IS | 2 | Total segment and consolidated cost of revenue | us-gaap:CostOfRevenue |  | -219706000 | 219706000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 3 | Selling, general and administrative expenses | us-gaap:SellingGeneralAndAdministrativeExpense |  | -449115000 | 449115000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 4 | Depreciation and amortization | us-gaap:DepreciationDepletionAndAmortization |  | -417729000 | 417729000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 5 | Impairment of assets | us-gaap:ImpairmentOfLongLivedAssetsHeldForUse |  | -638805000 | 638805000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 6 | Gain (loss) on disposal of property, plant and equipment | us-gaap:GainLossOnSaleOfPropertyPlantEquipment |  | -24908000 | -24908000 | Y | Y |
| R5.htm | IS | 7 | Other operating expenses | us-gaap:OtherCostAndExpenseOperating |  | -15157000 | 15157000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 8 | Other operating income | us-gaap:OtherOperatingIncome |  | 11699000 | 11699000 | Y | Y |
| R5.htm | IS | 9 | Total operating (expenses) income | iren:OperatingIncomeExpense |  | -1534014000 |  | custom | Y |
| R5.htm | IS | 10 | Operating (loss) income | us-gaap:OperatingIncomeLoss |  | -1046714000 | -1046714000 | Y | Y |
| R5.htm | IS | 11 | Finance expense | us-gaap:InterestExpenseNonoperating |  | -59251000 | 59251000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 12 | Interest income | us-gaap:InvestmentIncomeInterest |  | 80631000 | 80631000 | Y | Y |
| R5.htm | IS | 13 | Increase (decrease) in fair value of assets held for sale | iren:GainLossFromFairValueAdjustmentsOfAssetsHeldForSale |  | -110622000 |  | custom | Y |
| R5.htm | IS | 14 | Realized gain (loss) on financial instruments | us-gaap:RealizedInvestmentGainsLosses |  | -9269000 | -9269000 | Y | Y |
| R5.htm | IS | 15 | Unrealized gain (loss) on financial instruments | us-gaap:UnrealizedGainLossOnInvestments |  | 558541000 | 558541000 | Y | Y |
| R5.htm | IS | 16 | Gain on partial extinguishment of financial liabilities | us-gaap:GainLossOnSaleOfDerivatives |  | 0 | 0 | Y | Y |
| R5.htm | IS | 17 | Debt conversion inducement expense | us-gaap:InducedConversionOfConvertibleDebtExpense |  | -111799000 | 111799000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 18 | Foreign exchange gain (loss) | us-gaap:ForeignCurrencyTransactionGainLossBeforeTax |  | -10273000 | -10273000 | Y | Y |
| R5.htm | IS | 19 | Other non-operating income | us-gaap:OtherNonoperatingIncomeExpense |  | 72000 | 72000 | Y | Y |
| R5.htm | IS | 20 | Total other (expense) income | us-gaap:NonoperatingIncomeExpense |  | 338029000 | 338029000 | Y | Y |
| R5.htm | IS | 21 | Income (loss) before taxes | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |  | -708683000 | -708683000 | Y | Y |
| R5.htm | IS | 22 | Income tax (expense) benefit | us-gaap:IncomeTaxExpenseBenefit |  | 6062000 | -6062000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R5.htm | IS | 23 | Net income (loss) | us-gaap:NetIncomeLoss |  | -702621000 | -702621000 | Y | Y |
| R5.htm | IS | 24 | Basic net income (loss) per share of Ordinary shares ( in US | us-gaap:EarningsPerShareBasic |  | -2.22 | -2.22 | Y | Y |
| R5.htm | IS | 25 | Basic weighted-average shares used in computing net income ( | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic |  | 316123145 | 316123145 | Y | Y |
| R5.htm | IS | 26 | Diluted net income (loss) per share of Ordinary shares (in U | us-gaap:EarningsPerShareDiluted |  | -2.22 | -2.22 | Y | Y |
| R5.htm | IS | 27 | Diluted weighted-average shares used in computing net income | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding |  | 316123145 | 316123145 | Y | Y |
| R5.htm | IS | 28 | Gain (loss) on cash flow hedges, net of tax | us-gaap:OtherComprehensiveIncomeLossCashFlowHedgeGainLossAfterReclassificationAndTax |  | 3141000 | 3141000 | Y | Y |
| R5.htm | IS | 29 | Change in foreign currency translation adjustments, net of t | us-gaap:OtherComprehensiveIncomeForeignCurrencyTransactionAndTranslationAdjustmentNetOfTaxPortionAttributableToParent |  | -14492000 | -14492000 | Y | Y |
| R5.htm | IS | 30 | Total other comprehensive income (loss), net of tax | us-gaap:OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent |  | -11351000 | -11351000 | Y | Y |
| R5.htm | IS | 31 | Total comprehensive income (loss) | us-gaap:ComprehensiveIncomeNetOfTax |  | -713972000 | -713972000 | Y | Y |
| R5.htm | IS | 32 | Total revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | iren_AICloudServicesMember | 128795000 |  | dimensional | Y |
| R5.htm | IS | 33 | Total segment and consolidated cost of revenue | us-gaap:CostOfRevenue | iren_AICloudServicesMember | -16932000 |  | dimensional | Y |
| R5.htm | IS | 34 | Total revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | iren_BitcoinMiningMember | 578212000 |  | dimensional | Y |
| R5.htm | IS | 35 | Total segment and consolidated cost of revenue | us-gaap:CostOfRevenue | iren_BitcoinMiningMember | -202774000 |  | dimensional | Y |
| R7.htm | CF | 1 | Net income (loss) | us-gaap:NetIncomeLoss |  | -702621000 | -702621000 | Y | Y |
| R7.htm | CF | 2 | Depreciation and amortization | us-gaap:DepreciationDepletionAndAmortization |  | 417729000 | 417729000 | Y | Y |
| R7.htm | CF | 3 | Impairment of assets | us-gaap:ImpairmentOfLongLivedAssetsHeldForUse |  | 638805000 | 638805000 | Y | Y |
| R7.htm | CF | 4 | Increase (decrease) in fair value of assets held for sale | iren:GainLossFromFairValueAdjustmentsOfAssetsHeldForSale |  | 110622000 |  | custom | Y |
| R7.htm | CF | 5 | Other non-operating income | iren:OtherNonCashNonoperatingIncome |  | 0 |  | custom | Y |
| R7.htm | CF | 6 | Realized gain (loss) on financial asset | iren:RealizedInvestmentGainsLossesNoncash |  | 8667000 |  | custom | Y |
| R7.htm | CF | 7 | Unrealized (gain) loss on financial instrument | us-gaap:UnrealizedGainLossOnInvestments |  | -558541000 | 558541000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 8 | Debt conversion inducement expense | us-gaap:InducedConversionOfConvertibleDebtExpense |  | 111799000 | 111799000 | Y | Y |
| R7.htm | CF | 9 | Other (income) expense | us-gaap:OtherNoncashIncomeExpense |  | 0 | 0 | Y | Y |
| R7.htm | CF | 10 | Other finance expense | iren:OtherNoncashFinanceExpense |  | 0 |  | custom | Y |
| R7.htm | CF | 11 | (Gain) loss on disposal of property, plant and equipment | us-gaap:GainLossOnSaleOfPropertyPlantEquipment |  | 24908000 | -24908000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 12 | Foreign exchange loss (gain) | us-gaap:ForeignCurrencyTransactionGainLossUnrealized |  | 9919000 | -9919000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 13 | Gain on partial extinguishment of financial liabilities | us-gaap:GainLossOnSaleOfDerivatives |  | 0 | 0 | Y | Y |
| R7.htm | CF | 14 | Amortization of debt issuance costs | us-gaap:AmortizationOfFinancingCosts |  | 9408000 | 9408000 | Y | Y |
| R7.htm | CF | 15 | Stock-based compensation expense | us-gaap:ShareBasedCompensation |  | 205023000 | 205023000 | Y | Y |
| R7.htm | CF | 16 | Accounts receivable and other receivables | us-gaap:IncreaseDecreaseInAccountsAndOtherReceivables |  | -29434000 | 29434000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 17 | Financial asset, current | us-gaap:IncreaseDecreaseInFinancialInstrumentsUsedInOperatingActivities |  | 0 | 0 | Y | Y |
| R7.htm | CF | 18 | Accounts payable and accrued expenses | us-gaap:IncreaseDecreaseInAccountsPayableAndAccruedLiabilities |  | 38017000 | 38017000 | Y | Y |
| R7.htm | CF | 19 | Other assets | us-gaap:IncreaseDecreaseInOtherOperatingAssets |  | 494000 | -494000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 20 | Tax related receivables | iren:IncreaseDecreaseFromTaxReceivables |  | 0 |  | custom | Y |
| R7.htm | CF | 21 | Tax related liabilities | us-gaap:IncreaseDecreaseInAccruedTaxesPayable |  | -9136000 | -9136000 | Y | Y |
| R7.htm | CF | 22 | Other liabilities | us-gaap:IncreaseDecreaseInOtherOperatingLiabilities |  | 49506000 | 49506000 | Y | Y |
| R7.htm | CF | 23 | Deferred revenue | us-gaap:IncreaseDecreaseInContractWithCustomerLiability |  | 1841662000 | 1841662000 | Y | Y |
| R7.htm | CF | 24 | Prepayments and deposits | us-gaap:IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets |  | -67727000 | 67727000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 25 | Operating lease liabilities | us-gaap:IncreaseDecreaseInOperatingLeaseLiability |  | 1319000 | 1319000 | Y | Y |
| R7.htm | CF | 26 | Net cash from (used in) operating activities | us-gaap:NetCashProvidedByUsedInOperatingActivities |  | 2100418000 | 2100418000 | Y | Y |
| R7.htm | CF | 27 | Payments for property, plant and equipment, net of computer  | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment |  | -2998006000 | 2998006000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 28 | Payments for computer hardware | iren:PaymentsRelatedToComputerHardware |  | -1335081000 |  | custom | Y |
| R7.htm | CF | 29 | Payments for intangible assets | us-gaap:PaymentsToAcquireIntangibleAssets |  | -107573000 | 107573000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 30 | Payments for other prepayments and deposits | iren:PaymentsForOtherPrepaymentsAndDepositsInvestingActivities |  | -203439000 |  | custom | Y |
| R7.htm | CF | 31 | Proceeds from disposal of property, plant and equipment | us-gaap:ProceedsFromSaleOfPropertyPlantAndEquipment |  | 23782000 | 23782000 | Y | Y |
| R7.htm | CF | 32 | Deposits paid for right-of-use assets | iren:PaymentsToAcquireRightOfUseAssets |  | -10184000 |  | custom | Y |
| R7.htm | CF | 33 | Payment for the acquisition of subsidiaries | us-gaap:PaymentsToAcquireBusinessesAndInterestInAffiliates |  | -92483000 | 92483000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 34 | Proceeds from release of deposits | us-gaap:ProceedsFromOtherDeposits |  | 0 | 0 | Y | Y |
| R7.htm | CF | 35 | Net cash from (used in) investing activities | us-gaap:NetCashProvidedByUsedInInvestingActivities |  | -4722984000 | -4722984000 | Y | Y |
| R7.htm | CF | 36 | Payment for induced conversion of convertible notes | iren:PaymentForInducedConversionOfConvertibleNotes |  | -1623484000 |  | custom | Y |
| R7.htm | CF | 37 | Proceeds from loan funded shares | us-gaap:ProceedsFromRepaymentOfLoansToPurchaseCommonStock |  | 658000 | 658000 | Y | Y |
| R7.htm | CF | 38 | Proceeds from exercise of options | us-gaap:ProceedsFromStockOptionsExercised |  | 6597000 | 6597000 | Y | Y |
| R7.htm | CF | 39 | Proceeds from convertible notes | us-gaap:ProceedsFromConvertibleDebt |  | 6299555000 | 6299555000 | Y | Y |
| R7.htm | CF | 40 | Proceeds from financing facilities | iren:ProceedsFromFinancingFacilities |  | 938000000 |  | custom | Y |
| R7.htm | CF | 41 | Repayment of debt | us-gaap:RepaymentsOfLongTermDebt |  | -9213000 | 9213000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 42 | Payment of capped call transactions | iren:RepaymentsOfCappedCallTransactions |  | -448922000 |  | custom | Y |
| R7.htm | CF | 43 | Settlement of capped call transactions | iren:ProceedsFromSettlementOfCappedCallTransactions |  | 38812000 |  | custom | Y |
| R7.htm | CF | 44 | Repayment of finance lease liabilities | us-gaap:FinanceLeasePrincipalPayments |  | -48876000 | 48876000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 45 | Payment of borrowing transaction costs | us-gaap:PaymentsOfDebtIssuanceCosts |  | -165536000 | 165536000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 46 | Net cash from (used in) financing activities | us-gaap:NetCashProvidedByUsedInFinancingActivities |  | 9680050000 | 9680050000 | Y | Y |
| R7.htm | CF | 47 | Net increase (decrease) in cash, cash equivalents and restri | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect |  | 7057484000 | 7057484000 | Y | Y |
| R7.htm | CF | 48 | Cash, cash equivalents and restricted cash — beginning of pe | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |  | 564526000 |  |  | Y |
| R7.htm | CF | 49 | Effects of exchange rate changes on cash, cash equivalents a | us-gaap:EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations |  | -2483000 | -2483000 | Y | Y |
| R7.htm | CF | 50 | Cash, cash equivalents and restricted cash — end of period | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |  | 7619527000 |  |  | Y |
| R7.htm | CF | 51 | Cash paid for interest | us-gaap:InterestPaidNet |  | -42639000 | 42639000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 52 | Cash paid for income taxes | us-gaap:IncomeTaxesPaidNet |  | -2696000 | 2696000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R7.htm | CF | 53 | Additions to right-of-use assets in exchange for lease liabi | us-gaap:RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability |  | 291592000 | 291592000 | Y | Y |
| R7.htm | CF | 54 | Stock-based compensation - third party issuance | iren:NonCashShareBasedCompensationThirdParty |  | 0 |  | custom | Y |
| R7.htm | CF | 55 | Reclassification of property and equipment to equipment held | iren:PropertyPlantAndEquipmentTransferredToHeldToSale |  | 204762000 |  | custom | Y |
| R7.htm | CF | 56 | Property and equipment obtained in exchange transactions | us-gaap:FairValueOfAssetsAcquired |  | 0 | 0 | Y | Y |
| R7.htm | CF | 57 | Issuance of Ordinary shares - restricted stock unit and opti | us-gaap:StockIssued1 | us-gaap_RestrictedStockUnitsRSUMember | 73564000 |  | dimensional | Y |
| R7.htm | CF | 58 | Payments of offering costs for committed equity facility and | us-gaap:PaymentsOfStockIssuanceCosts | iren_CommittedEquityFacilityMember | 0 |  | dimensional | Y |
| R7.htm | CF | 59 | Proceeds from committed equity facility and issuance of Ordi | us-gaap:ProceedsFromIssuanceOfCommonStock | iren_CommittedEquityFacilityMember | 0 |  | dimensional | Y |
| R7.htm | CF | 60 | Payments of offering costs for committed equity facility and | us-gaap:PaymentsOfStockIssuanceCosts | iren_AtTheMarketFacilityMember | -50380000 |  | dimensional | Y |
| R7.htm | CF | 61 | Proceeds from committed equity facility and issuance of Ordi | us-gaap:ProceedsFromIssuanceOfCommonStock | iren_AtTheMarketFacilityMember | 4742839000 |  | dimensional | Y |

Totals: 142 IS/BS/CF/CI face lines with an FY0 value; 111 equal companyfacts, 0 differ, 31 without a companyfacts fact (16 custom-tag, 13 dimensional).

## Hand check vs the shared reader (data-team/companies/reads/tools/docmap.py @558f2f15, origin/work/reads/901-1000)
35 data points agree; 3 differ. The value kept is the one printed on the R page.

| data point | shared reader | this read (kept) | why |
|---|---|---|---|
| gross_profit | mapped GrossProfit  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| accounts_payable | mapped AccountsPayableAndAccruedLiabilitiesCurrent 1825392000 | combined AccountsPayableAndAccruedLiabilitiesCurrent 1825392000 | face lines re-read for this row: see the face-line table above |
| total_debt | component sum LongTermDebtCurrent+LongTermDebtNoncurrent 7592944000 | component sum FinanceLeaseLiabilityCurrent;LongTermDebtCurrent;FinanceLeaseLiabilityNoncurrent 7836740000 | face lines re-read for this row: see the face-line table above |
