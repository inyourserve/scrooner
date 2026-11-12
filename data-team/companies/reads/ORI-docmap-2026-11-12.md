# ORI document-first map 2026-11-12 (rank 718, read-only)

Evidence: FILING-CHECKED unless a row says otherwise. Printed values come from the R pages of the 10-K on sec.gov; tags from each R-page row's element reference; API = SEC companyfacts (undimensioned, same accession, same period); FSN = our fsn.line rows for the same filing and report.

Company: OLD REPUBLIC INTERNATIONAL CORPORATION (CIK 0000074260); sector shape read from the face: insurer.

## Filings opened
- Latest 10-K 0000074260-26-000008 (index from FSN store (fsn.filing, fsn.report)): R3.htm Consolidated Balance Sheets [BS], R4.htm Consolidated Balance Sheets (Parenthetical) [BSP], R5.htm Consolidated Statements of Income [IS], R6.htm Consolidated Statements of Comprehensive Income [CI], R8.htm Consolidated Statements of Cash Flows [CF].
- Era 10-K 0000074260-16-000082 (FY2015): R2.htm Consolidated Balance Sheets, R4.htm Consolidated Statements of Income, R6.htm Consolidated Statements of Cash Flows, R7.htm Consolidated Statements of Comprehensive Income Statement.
- Era 10-K 0000074260-25-000042 (FY2024): R3.htm Consolidated Balance Sheets, R5.htm Consolidated Statements of Income, R6.htm Consolidated Statements of Comprehensive Income, R8.htm Consolidated Statements of Cash Flows.
- Era 10-K 0000074260-22-000012 (FY2021): R5.htm Consolidated Statements of Income, R6.htm Consolidated Statements of Comprehensive Income, R8.htm Consolidated Statements of Cash Flows.
- companyfacts: one call to data.sec.gov.
- sec.gov requests for this company: 0.

FY0 = the latest fiscal-year column, FY1 = the prior year. Values in full units (printed value × the R-page scale); EPS per share; shares in shares.

## Data points (the CSV holds exactly these rows)
| data point | status | tag(s) | R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match |
|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | R5.htm | Total revenues | 9136300000 | 9136300000 | 8231500000 | 8231500000 | Y |
| cost_of_revenue | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| gross_profit | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| operating_expenses | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| sga_expense | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| research_and_development | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| operating_income | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| interest_expense | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| interest_income | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| other_income_expense_net | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before income taxes | 1184000000 | 1184000000 | 1069700000 | 1069700000 | Y |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R5.htm | Total income taxes | 242100000 | 242100000 | 216900000 | 216900000 | Y |
| net_income | mapped | NetIncomeLoss | R5.htm | Net income to shareholders | 935400000 | 935400000 | 852700000 | 852700000 | Y |
| basic_eps | mapped | EarningsPerShareBasic | R5.htm | Net income per share: basic (in dollars per share) | 3.82 | 3.82 | 3.3 | 3.3 | Y |
| diluted_eps | mapped | EarningsPerShareDiluted | R5.htm | Net income per share: diluted (in dollars per share) | 3.72 | 3.72 | 3.24 | 3.24 | Y |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average number of shares outstanding, basic | 245121426 | 245121426 | 258032085 | 258032085 | Y |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted Average Number of Shares Outstanding, Diluted | 251313860 | 251313860 | 262880631 | 262880631 | Y |
| dividends_per_share | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R6.htm | Comprehensive Income to Shareholders | 1201000000 | 1201000000 | 882600000 | 882600000 | Y |
| cash_and_equivalents | mapped | Cash | R3.htm | Cash | 263200000 | 263200000 | 201900000 | 201900000 | Y |
| accounts_receivable | not_presented |  |  |  |  |  |  |  | wider receivables tag PremiumsAndOtherReceivablesNet is one of 2 recei |
| inventory | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| current_assets | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| ppe_net | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| goodwill | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| total_assets | mapped | Assets | R3.htm | Total assets | 29862700000 | 29862700000 | 27843100000 | 27843100000 | Y |
| accounts_payable | combined | AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Commissions, expenses, fees, and taxes | 601800000 | 601800000 | 547500000 | 547500000 | Y |
| current_liabilities | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| total_liabilities | mapped | Liabilities | R3.htm | Total liabilities | 23934200000 | 23934200000 | 22224100000 | 22224100000 | Y |
| total_debt | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| stockholders_equity | mapped | StockholdersEquity | R3.htm | Total shareholders' equity | 5914000000 | 5914000000 | 5618900000 | 5618900000 | Y |
| shares_outstanding | not_presented |  |  |  |  |  |  |  | no CommonStockSharesOutstanding at the balance-sheet date on the BS or |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R8.htm | Total | 1164300000 | 1164300000 | 1233400000 | 1233400000 | Y |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R8.htm | Total | -177200000 | -177200000 | -3900000 | -3900000 | Y |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R8.htm | Total | -925700000 | -925700000 | -1226900000 | -1226900000 | Y |
| capex | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| depreciation_and_amortization | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| amortization_of_intangibles | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| sbc | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | R8.htm | Dividends on common shares | -782600000 | 782600000 | -271900000 | 271900000 | Y (sign differs: printed in parentheses/negated label) |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | R8.htm | Treasury stock acquired | -123800000 | 123800000 | -942200000 | 942200000 | Y (sign differs: printed in parentheses/negated label) |
| cf_ar_change | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_inventory_change | OUT |  |  |  |  |  |  |  | insurer: unclassified balance sheet / no such line (sector template) |
| cf_ap_change | combined | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | R8.htm | Other - net | 29100000 | 29100000 | -45400000 | -45400000 | Y |
| cash_paid_for_interest | mapped | InterestPaidNet | R8.htm | Cash paid during the period for: Interest | 69300000 | 69300000 | 77300000 | 77300000 | Y |
| cash_paid_for_income_taxes | mapped | ori:IncomeTaxesPaidFederalForeignNet | R8.htm | Income Taxes Paid, Federal & Foreign, Net | 198700000 |  | 196300000 |  | custom tag: no companyfacts fact |
| net_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| total_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_expense | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| provision_for_credit_losses | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| deposits | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| loans_net | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |

Sector lines also on the face (not in the graded vocabulary): premiums_earned = PremiumsEarnedNet 'Net premiums earned' 7788700000; net_investment_income = NetInvestmentIncome 'Net investment income' 708700000; policy_benefits = PolicyholderBenefitsAndClaimsIncurredNet 'Loss and loss adjustment expenses' 3361100000; net_income_incl_nci = ProfitLoss 'Net Income (Loss), Including Portion Attributable ' 941900000; total_equity_incl_nci = StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest 'Equity, Including Portion Attributable to Noncontr' 5928400000.

## Eras FY2015 to FY2025 (every data point; companyfacts tag per original 10-K, and the era 10-Ks opened: FY2015 always, plus the last 10-K of each earlier era)
| data point | latest status | eras (companyfacts) | era 10-K reads (FILING-CHECKED) | coverage |
|---|---|---|---|---|
| revenue | mapped | FY2015-FY2025: Revenues | FY2015 10-K 0000074260-16-000082 R4.htm 'Total revenues' Revenues (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Total revenues' Revenues (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Total revenues' Revenues (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| income_before_tax | mapped | FY2015-FY2025: IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | FY2015 10-K 0000074260-16-000082 R4.htm 'Income (loss) before income taxes (credi' IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Income before income taxes' IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Income (loss) before income taxes (credi' IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| income_tax_expense | mapped | FY2015-FY2025: IncomeTaxExpenseBenefit | FY2015 10-K 0000074260-16-000082 R4.htm 'Total' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Total' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Total' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| net_income | mapped | FY2015-FY2025: NetIncomeLoss | FY2015 10-K 0000074260-16-000082 R4.htm 'Net Income (Loss)' NetIncomeLoss (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Net Income' NetIncomeLoss (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Net Income (Loss)' NetIncomeLoss (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| basic_eps | mapped | FY2015-FY2025: EarningsPerShareBasic | FY2015 10-K 0000074260-16-000082 R4.htm 'Net income (loss) per share: basic (in d' EarningsPerShareBasic (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Net income per share: basic (in dollars ' EarningsPerShareBasic (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Net income (loss) per share: basic (in d' EarningsPerShareBasic (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| diluted_eps | mapped | FY2015-FY2025: EarningsPerShareDiluted | FY2015 10-K 0000074260-16-000082 R4.htm 'Net income (loss) per share: diluted (in' EarningsPerShareDiluted (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Net income per share: diluted (in dollar' EarningsPerShareDiluted (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Net income (loss) per share: diluted (in' EarningsPerShareDiluted (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| weighted_basic_shares | mapped | FY2015-FY2025: WeightedAverageNumberOfSharesOutstandingBasic | FY2015 10-K 0000074260-16-000082 R4.htm 'weighted average number of shares outsta' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Weighted average number of shares outsta' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Weighted average number of shares outsta' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| weighted_diluted_shares | mapped | FY2015-FY2025: WeightedAverageNumberOfDilutedSharesOutstanding | FY2015 10-K 0000074260-16-000082 R4.htm 'Weighted Average Number of Shares Outsta' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R5.htm 'Weighted Average Number of Shares Outsta' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R5.htm 'Weighted Average Number of Shares Outsta' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| comprehensive_income | mapped | FY2015-FY2025: ComprehensiveIncomeNetOfTax | FY2015 10-K 0000074260-16-000082 R7.htm 'Comprehensive Income (Loss)' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R6.htm 'Comprehensive Income' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R6.htm 'Comprehensive Income (Loss)' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| cash_and_equivalents | mapped | FY2015-FY2025: Cash | FY2015 10-K 0000074260-16-000082 R2.htm 'Cash' Cash (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R3.htm 'Cash' Cash (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012: no face line | coverage FY2015-FY2025 complete |
| total_assets | mapped | FY2015-FY2025: Assets | FY2015 10-K 0000074260-16-000082 R2.htm 'Total Assets' Assets (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R3.htm 'Total assets' Assets (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012: no face line | coverage FY2015-FY2025 complete |
| accounts_payable | combined | FY2015-FY2025: no standard tag | FY2015 10-K 0000074260-16-000082 R2.htm 'Commissions, expenses, fees, and taxes' AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent (combined) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R3.htm 'Commissions, expenses, fees, and taxes' AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent (combined) FILING-CHECKED; FY2021 10-K 0000074260-22-000012: no face line | coverage FY2015-FY2025 gaps FY2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| total_liabilities | mapped | FY2015-FY2025: Liabilities | FY2015 10-K 0000074260-16-000082 R2.htm 'Total Liabilities' Liabilities (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R3.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012: no face line | coverage FY2015-FY2025 complete |
| stockholders_equity | mapped | FY2015-FY2025: StockholdersEquity | FY2015 10-K 0000074260-16-000082 R2.htm 'Total Common Shareholders' Equity' StockholdersEquity (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R3.htm 'Total common shareholders' equity' StockholdersEquity (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012: no face line | coverage FY2015-FY2025 complete |
| cfo | mapped | FY2015-FY2025: NetCashProvidedByUsedInOperatingActivities | FY2015 10-K 0000074260-16-000082 R6.htm 'Total' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Total' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Total' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| cash_flow_investing | mapped | FY2015-FY2025: NetCashProvidedByUsedInInvestingActivities | FY2015 10-K 0000074260-16-000082 R6.htm 'Total' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Total' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Total' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| cash_flow_financing | mapped | FY2015-FY2025: NetCashProvidedByUsedInFinancingActivities | FY2015 10-K 0000074260-16-000082 R6.htm 'Total' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Total' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Total' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| dividends_paid | mapped | FY2015-FY2025: PaymentsOfDividendsCommonStock | FY2015 10-K 0000074260-16-000082 R6.htm 'Dividends on common shares' PaymentsOfDividendsCommonStock (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Dividends on common shares (including sp' PaymentsOfDividendsCommonStock (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Dividends on common shares (including sp' PaymentsOfDividendsCommonStock (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| share_buybacks | mapped | FY2015-FY2021: no standard tag; FY2022-FY2025: PaymentsForRepurchaseOfCommonStock | FY2015 10-K 0000074260-16-000082: no face line; FY2024 10-K 0000074260-25-000042 R8.htm 'Treasury stock acquired' PaymentsForRepurchaseOfCommonStock (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012: no face line | coverage FY2015-FY2025 gaps FY2015,2016,2017,2018,2019,2020,2021 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cf_ap_change | combined | FY2015-FY2025: no standard tag | FY2015 10-K 0000074260-16-000082 R6.htm 'Accounts payable, accrued expenses and o' IncreaseDecreaseInAccountsPayableAndAccruedLiabilities (combined) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Other - net' IncreaseDecreaseInAccountsPayableAndAccruedLiabilities (combined) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Accounts payable, accrued expenses and o' IncreaseDecreaseInAccountsPayableAndAccruedLiabilities (combined) FILING-CHECKED | coverage FY2015-FY2025 gaps FY2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025 (no standard-tag 10-K fact; see FILING-CHECKED era reads) |
| cash_paid_for_interest | mapped | FY2015-FY2025: InterestPaidNet | FY2015 10-K 0000074260-16-000082 R6.htm 'Cash paid (received) during the period f' InterestPaidNet (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Cash paid (received) during the period f' InterestPaidNet (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Cash paid (received) during the period f' InterestPaidNet (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |
| cash_paid_for_income_taxes | mapped | FY2015-FY2025: IncomeTaxesPaidNet | FY2015 10-K 0000074260-16-000082 R6.htm 'Cash paid (received) during the period f' IncomeTaxesPaidNet (mapped) FILING-CHECKED; FY2024 10-K 0000074260-25-000042 R8.htm 'Cash paid (received) during the period f' IncomeTaxesPaidNet (mapped) FILING-CHECKED; FY2021 10-K 0000074260-22-000012 R8.htm 'Cash paid (received) during the period f' IncomeTaxesPaidNet (mapped) FILING-CHECKED | coverage FY2015-FY2025 complete |

## Quirks and mismatches (the filing decides)
- [combined_line] cf_ap_change: us-gaap:IncreaseDecreaseInAccountsPayableAndAccruedLiabilities 'Other - net' — combined line; never the pure concept (0000074260-26-000008 R8.htm 2025-12-31)
- [combined_line] accounts_payable: us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent 'Commissions, expenses, fees, and taxes' — combined line; never the pure concept (0000074260-26-000008 R3.htm 2025-12-31)
- [custom_tag_line] cash_paid_for_income_taxes: ori:IncomeTaxesPaidFederalForeignNet 'Income Taxes Paid, Federal & Foreign, Net' — data-point line carries a company extension tag (not in companyfacts) (0000074260-26-000008 R8.htm 2025-12-31)

## Every face line (printed page → tag → FSN → companyfacts)
| R | stmt | # | label | tag | member | FY0 printed | FY0 API | match | in FSN |
|---|---|---|---|---|---|---|---|---|---|
| R3.htm | BS | 1 | Fixed income securities (at fair value) (amortized cost: $12 | us-gaap:AvailableForSaleSecuritiesDebtSecurities |  | 12709800000 | 12709800000 | Y | Y |
| R3.htm | BS | 2 | Equity securities (at fair value) (cost: $1,377.7 and $1,410 | us-gaap:EquitySecuritiesFvNiCurrentAndNoncurrent |  | 2487700000 | 2487700000 | Y | Y |
| R3.htm | BS | 3 | Short-term investments (at fair value which approximates cos | us-gaap:OtherShortTermInvestments |  | 1613600000 | 1613600000 | Y | Y |
| R3.htm | BS | 4 | Other investments | us-gaap:OtherInvestments |  | 27700000 | 27700000 | Y | Y |
| R3.htm | BS | 5 | Total investments | us-gaap:Investments |  | 16839000000 | 16839000000 | Y | Y |
| R3.htm | BS | 6 | Cash | us-gaap:Cash |  | 263200000 | 263200000 | Y | Y |
| R3.htm | BS | 7 | Accrued investment income | us-gaap:AccruedInvestmentIncomeReceivable |  | 141100000 | 141100000 | Y | Y |
| R3.htm | BS | 8 | Accounts and notes receivable | us-gaap:PremiumsAndOtherReceivablesNet |  | 2782200000 | 2782200000 | Y | Y |
| R3.htm | BS | 9 | Reinsurance balances and funds held | us-gaap:FundsHeldUnderReinsuranceAgreementsAsset |  | 404500000 | 404500000 | Y | Y |
| R3.htm | BS | 10 | Reinsurance recoverable: Paid losses | us-gaap:ReinsuranceRecoverablesOnPaidLosses |  | 209900000 | 209900000 | Y | Y |
| R3.htm | BS | 11 | Reinsurance recoverable for loss and loss adjustment expense | ori:ReinsuranceRecoverableForLossAndLossAdjustmentExpenseReserves |  | 6399100000 |  | custom | Y |
| R3.htm | BS | 12 | Unearned premium and policy reserves | ori:UnearnedPremiumAndPolicyReserves |  | 1131100000 |  | custom | Y |
| R3.htm | BS | 13 | Deferred policy acquisition costs | us-gaap:DeferredPolicyAcquisitionCosts |  | 636200000 | 636200000 | Y | Y |
| R3.htm | BS | 14 | Other assets | us-gaap:OtherAssets |  | 1055900000 | 1055900000 | Y | Y |
| R3.htm | BS | 15 | Total assets | us-gaap:Assets |  | 29862700000 | 29862700000 | Y | Y |
| R3.htm | BS | 16 | Loss and loss adjustment expense reserves | us-gaap:LiabilityForClaimsAndClaimsAdjustmentExpense |  | 14775700000 | 14775700000 | Y | Y |
| R3.htm | BS | 17 | Unearned premiums | us-gaap:UnearnedPremiums |  | 3982500000 | 3982500000 | Y | Y |
| R3.htm | BS | 18 | Other policyholders' benefits and funds held | ori:OtherPolicholdersBenefitsAndFunds |  | 177800000 |  | custom | Y |
| R3.htm | BS | 19 | Total policy liabilities | ori:TotalPolicyLiabilitiesAndAccruals |  | 18936100000 |  | custom | Y |
| R3.htm | BS | 20 | Commissions, expenses, fees, and taxes | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent |  | 601800000 | 601800000 | Y | Y |
| R3.htm | BS | 21 | Reinsurance balances and funds held | ori:ReinsuranceBalancesAndFundsHeld |  | 1428000000 |  | custom | Y |
| R3.htm | BS | 22 | Deferred Tax Liabilities, Net | us-gaap:DeferredIncomeTaxLiabilitiesNet |  | 219300000 | 219300000 | Y | Y |
| R3.htm | BS | 23 | Debt | us-gaap:DebtAndCapitalLeaseObligations |  | 1589900000 | 1589900000 | Y | Y |
| R3.htm | BS | 24 | Other liabilities | us-gaap:OtherLiabilities |  | 1158700000 | 1158700000 | Y | Y |
| R3.htm | BS | 25 | Total liabilities | us-gaap:Liabilities |  | 23934200000 | 23934200000 | Y | Y |
| R3.htm | BS | 26 | Preferred Stock | us-gaap:PreferredStockValueOutstanding |  | 0 | 0 | Y | Y |
| R3.htm | BS | 27 | Common stock | us-gaap:CommonStockValue |  | 246300000 | 246300000 | Y | Y |
| R3.htm | BS | 28 | Additional paid-in capital | us-gaap:AdditionalPaidInCapitalCommonStock |  | 23300000 | 23300000 | Y | Y |
| R3.htm | BS | 29 | Retained earnings | us-gaap:RetainedEarningsAccumulatedDeficit |  | 5515200000 | 5515200000 | Y | Y |
| R3.htm | BS | 30 | Accumulated other comprehensive income (loss) | us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax |  | 163100000 | 163100000 | Y | Y |
| R3.htm | BS | 31 | Unallocated 401(k) plan shares (at cost) | ori:UnallocatedEssopShares |  | -34.1 |  | custom | Y |
| R3.htm | BS | 32 | Treasury Stock, Value | us-gaap:TreasuryStockValue |  | 0 | 0 | Y | Y |
| R3.htm | BS | 33 | Total shareholders' equity | us-gaap:StockholdersEquity |  | 5914000000 | 5914000000 | Y | Y |
| R3.htm | BS | 34 | Equity, Attributable to Noncontrolling Interest | us-gaap:MinorityInterest |  | 14400000 | 14400000 | Y | Y |
| R3.htm | BS | 35 | Equity, Including Portion Attributable to Noncontrolling Int | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest |  | 5928400000 | 5928400000 | Y | Y |
| R3.htm | BS | 36 | Total liabilities and equity | us-gaap:LiabilitiesAndStockholdersEquity |  | 29862700000 | 29862700000 | Y | Y |
| R4.htm | BSP | 1 | Debt Securities, Available-for-sale, Amortized Cost | us-gaap:AvailableForSaleDebtSecuritiesAmortizedCostBasis |  | 12478800000 | 12478800000 | Y | N |
| R4.htm | BSP | 2 | Preferred Stock, Par or Stated Value Per Share | us-gaap:PreferredStockParOrStatedValuePerShare |  | 0.01 | 0.01 | Y | N |
| R4.htm | BSP | 3 | Preferred Stock, Shares Authorized | us-gaap:PreferredStockSharesAuthorized |  | 75000000 | 75000000 | Y | N |
| R4.htm | BSP | 4 | Preferred Stock, Shares Outstanding | us-gaap:PreferredStockSharesOutstanding |  | 0 | 0 | Y | N |
| R4.htm | BSP | 5 | Common Stock, Par or Stated Value Per Share | us-gaap:CommonStockParOrStatedValuePerShare |  | 1 | 1 | Y | N |
| R4.htm | BSP | 6 | Common Stock, Shares, Issued | us-gaap:CommonStockSharesIssued |  | 246355085 | 246355085 | Y | N |
| R4.htm | BSP | 7 | Common Stock, Shares Authorized | us-gaap:CommonStockSharesAuthorized |  | 500000000 | 500000000 | Y | N |
| R4.htm | BSP | 8 | Debt Securities, Available-for-sale, Amortized Cost | us-gaap:AvailableForSaleDebtSecuritiesAmortizedCostBasis | us-gaap_FixedIncomeSecuritiesMember | 12478800000 |  | dimensional | N |
| R4.htm | BSP | 9 | Equity Securities, Amortized Cost Basis | us-gaap:EquitySecuritiesFvNiCost | us-gaap_EquitySecuritiesMember | 1377700000 |  | dimensional | N |
| R4.htm | BSP | 10 | Common Stock, Par or Stated Value Per Share | us-gaap:CommonStockParOrStatedValuePerShare | us-gaap_CommonClassBMember | 1 |  | dimensional | N |
| R4.htm | BSP | 11 | Common Stock, Shares, Issued | us-gaap:CommonStockSharesIssued | us-gaap_CommonClassBMember | 0 |  | dimensional | N |
| R4.htm | BSP | 12 | Common Stock, Shares Authorized | us-gaap:CommonStockSharesAuthorized | us-gaap_CommonClassBMember | 100000000 |  | dimensional | N |
| R5.htm | IS | 1 | Net premiums earned | us-gaap:PremiumsEarnedNet |  | 7788700000 | 7788700000 | Y | Y |
| R5.htm | IS | 2 | Title, escrow, and other fees | ori:TitleEscrowAndOtherFees |  | 264100000 |  | custom | Y |
| R5.htm | IS | 3 | Total premiums and fees | ori:TotalPremiumsAndFees |  | 8052900000 |  | custom | Y |
| R5.htm | IS | 4 | Net investment income | us-gaap:NetInvestmentIncome |  | 708700000 | 708700000 | Y | Y |
| R5.htm | IS | 5 | Other income | us-gaap:OtherIncome |  | 194900000 | 194900000 | Y | Y |
| R5.htm | IS | 6 | Total operating revenues | ori:TotalOperatingRevenues |  | 8956600000 |  | custom | Y |
| R5.htm | IS | 7 | Consolidated net realized investment gains (losses) | us-gaap:RealizedInvestmentGainsLosses |  | 202000000 | 202000000 | Y | Y |
| R5.htm | IS | 8 | Unrealized from changes in fair value of equity securities | us-gaap:EquitySecuritiesFvNiUnrealizedGainLoss |  | -22300000 | -22300000 | Y | Y |
| R5.htm | IS | 9 | Total net investment gains (losses) | us-gaap:GainLossOnInvestments |  | 179700000 | 179700000 | Y | Y |
| R5.htm | IS | 10 | Total revenues | us-gaap:Revenues |  | 9136300000 | 9136300000 | Y | Y |
| R5.htm | IS | 11 | Loss and loss adjustment expenses | us-gaap:PolicyholderBenefitsAndClaimsIncurredNet |  | 3361100000 | 3361100000 | Y | Y |
| R5.htm | IS | 12 | Dividends to policyholders | us-gaap:PolicyholderDividends |  | 16200000 | 16200000 | Y | Y |
| R5.htm | IS | 13 | Underwriting, acquisition, and other expenses | ori:UnderwritingAcquisitionAndOtherExpenses |  | 4504500000 |  | custom | Y |
| R5.htm | IS | 14 | Interest and other charges | ori:InterestAndOtherCharges |  | 70300000 |  | custom | Y |
| R5.htm | IS | 15 | Total expenses | us-gaap:BenefitsLossesAndExpenses |  | 7952300000 | 7952300000 | Y | Y |
| R5.htm | IS | 16 | Income before income taxes | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments |  | 1184000000 | 1184000000 | Y | Y |
| R5.htm | IS | 17 | Current | us-gaap:CurrentIncomeTaxExpenseBenefit |  | 225200000 | 225200000 | Y | Y |
| R5.htm | IS | 18 | Deferred | us-gaap:DeferredIncomeTaxExpenseBenefit |  | 16800000 | 16800000 | Y | Y |
| R5.htm | IS | 19 | Total income taxes | us-gaap:IncomeTaxExpenseBenefit |  | 242100000 | 242100000 | Y | Y |
| R5.htm | IS | 20 | Net Income (Loss), Including Portion Attributable to Noncont | us-gaap:ProfitLoss |  | 941900000 | 941900000 | Y | Y |
| R5.htm | IS | 21 | Comprehensive Income (Loss), Net of Tax, Attributable to Non | us-gaap:ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest |  | 6500000 | 6500000 | Y | Y |
| R5.htm | IS | 22 | Net income to shareholders | us-gaap:NetIncomeLoss |  | 935400000 | 935400000 | Y | Y |
| R5.htm | IS | 23 | Net income per share: basic (in dollars per share) | us-gaap:EarningsPerShareBasic |  | 3.82 | 3.82 | Y | Y |
| R5.htm | IS | 24 | Net income per share: diluted (in dollars per share) | us-gaap:EarningsPerShareDiluted |  | 3.72 | 3.72 | Y | Y |
| R5.htm | IS | 25 | Weighted average number of shares outstanding, basic | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic |  | 245121426 | 245121426 | Y | Y |
| R5.htm | IS | 26 | Weighted Average Number of Shares Outstanding, Diluted | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding |  | 251313860 | 251313860 | Y | Y |
| R6.htm | CI | 1 | Net Income (Loss), Including Portion Attributable to Noncont | us-gaap:ProfitLoss |  | 941900000 | 941900000 | Y | Y |
| R6.htm | CI | 2 | Unrealized gains (losses) on securities before reclassificat | us-gaap:OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodBeforeTax |  | 306300000 | 306300000 | Y | Y |
| R6.htm | CI | 3 | Amounts reclassified as realized investment (gains) losses i | us-gaap:OtherComprehensiveIncomeLossReclassificationAdjustmentFromAOCIForSaleOfSecuritiesBeforeTax |  | 10600000 | -10600000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R6.htm | CI | 4 | Pretax unrealized gains (losses) on securities not included  | us-gaap:OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentBeforeTax |  | 317000000 | 317000000 | Y | Y |
| R6.htm | CI | 5 | Deferred income taxes | us-gaap:OtherComprehensiveIncomeLossAvailableForSaleSecuritiesTax |  | 66700000 | 66700000 | Y | Y |
| R6.htm | CI | 6 | Net unrealized gains (losses) on securities not included in  | us-gaap:OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodNetOfTax |  | 250300000 | 250300000 | Y | Y |
| R6.htm | CI | 7 | Foreign currency translation adjustment and other | ori:ForeignCurrencyTranslationAdjustmentAndOther |  | 15300000 |  | custom | Y |
| R6.htm | CI | 8 | Total other comprehensive income | us-gaap:OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent |  | 265600000 | 265600000 | Y | Y |
| R6.htm | CI | 9 | Comprehensive Income (Loss), Net of Tax, Including Portion A | us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest |  | 1207600000 | 1207600000 | Y | Y |
| R6.htm | CI | 10 | Comprehensive Income (Loss), Net of Tax, Attributable to Non | us-gaap:ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest |  | 6500000 | 6500000 | Y | Y |
| R6.htm | CI | 11 | Comprehensive Income to Shareholders | us-gaap:ComprehensiveIncomeNetOfTax |  | 1201000000 | 1201000000 | Y | Y |
| R8.htm | CF | 1 | Net Income (Loss), Including Portion Attributable to Noncont | us-gaap:ProfitLoss |  | 941900000 | 941900000 | Y | Y |
| R8.htm | CF | 2 | Deferred policy acquisition costs | us-gaap:IncreaseDecreaseInDeferredPolicyAcquisitionCosts |  | -104900000 | 104900000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 3 | Accounts and notes receivable | us-gaap:IncreaseDecreaseInPremiumsReceivable |  | -278600000 | 278600000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 4 | Loss and loss adjustment expense reserves | us-gaap:IncreaseDecreaseInLiabilityForClaimsAndClaimsAdjustmentExpenseReserve |  | 438100000 | 438100000 | Y | Y |
| R8.htm | CF | 5 | Unearned premiums and other policyholders' liabilities | us-gaap:IncreaseDecreaseInOtherPolicyholderFunds |  | 260600000 | 260600000 | Y | Y |
| R8.htm | CF | 6 | Federal income taxes | ori:IncreaseDecreaseInIncomeTaxesNet |  | 45100000 |  | custom | Y |
| R8.htm | CF | 7 | Reinsurance balances and funds held | us-gaap:IncreaseDecreaseInFundsHeldUnderReinsuranceAgreements |  | 12600000 | -12600000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 8 | Realized Investment Gains (Losses) | us-gaap:RealizedInvestmentGainsLosses |  | -202000000 | 202000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 9 | Unrealized from changes in fair value of equity securities | ori:Unrealizedfromchangesinfairvalueofequitysecurities |  | 22300000 |  | custom | Y |
| R8.htm | CF | 10 | Other - net | us-gaap:IncreaseDecreaseInAccountsPayableAndAccruedLiabilities |  | 29100000 | 29100000 | Y | Y |
| R8.htm | CF | 11 | Total | us-gaap:NetCashProvidedByUsedInOperatingActivities |  | 1164300000 | 1164300000 | Y | Y |
| R8.htm | CF | 12 | Maturities and calls on fixed income securities | us-gaap:ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities |  | 1561700000 | 1561700000 | Y | Y |
| R8.htm | CF | 13 | Fixed income securities | us-gaap:ProceedsFromSaleOfAvailableForSaleSecuritiesDebt |  | 863100000 | 863100000 | Y | Y |
| R8.htm | CF | 14 | Equity securities | us-gaap:ProceedsFromSaleOfEquitySecuritiesFvNi |  | 510200000 | 510200000 | Y | Y |
| R8.htm | CF | 15 | Other investments | us-gaap:ProceedsFromSaleAndMaturityOfOtherInvestments |  | 3900000 | 3900000 | Y | Y |
| R8.htm | CF | 16 | Fixed income securities | us-gaap:PaymentsToAcquireAvailableForSaleSecuritiesDebt |  | -2612200000 | 2612200000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 17 | Equity securities | us-gaap:PaymentsToAcquireEquitySecuritiesFvNi |  | -182700000 | 182700000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 18 | Other investments | us-gaap:PaymentsToAcquireOtherInvestments |  | -119800000 | 119800000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 19 | Proceeds from Divestiture of Interest in Consolidated Subsid | us-gaap:ProceedsFromDivestitureOfInterestInConsolidatedSubsidiaries |  | 0 | 0 | Y | Y |
| R8.htm | CF | 20 | Net increase in short-term investments | us-gaap:PaymentsForProceedsFromShortTermInvestments |  | -203700000 | 203700000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 21 | Payments for (Proceeds from) Other Investing Activities | us-gaap:PaymentsForProceedsFromOtherInvestingActivities |  | 2300000 | -2300000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 22 | Total | us-gaap:NetCashProvidedByUsedInInvestingActivities |  | -177200000 | -177200000 | Y | Y |
| R8.htm | CF | 23 | Proceeds from Issuance of Long-term Debt | us-gaap:ProceedsFromIssuanceOfSeniorLongTermDebt |  | 0 | 0 | Y | Y |
| R8.htm | CF | 24 | Issuance of common shares | us-gaap:ProceedsFromIssuanceOfCommonStock |  | 3800000 | 3800000 | Y | Y |
| R8.htm | CF | 25 | Redemption of debentures and notes | us-gaap:RepaymentsOfOtherDebt |  | 0 | 0 | Y | Y |
| R8.htm | CF | 26 | Dividends on common shares | us-gaap:PaymentsOfDividendsCommonStock |  | -782600000 | 782600000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 27 | Treasury stock acquired | us-gaap:PaymentsForRepurchaseOfCommonStock |  | -123800000 | 123800000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 28 | Other - net | us-gaap:ProceedsFromPaymentsForOtherFinancingActivities |  | -23100000 | -23100000 | Y | Y |
| R8.htm | CF | 29 | Total | us-gaap:NetCashProvidedByUsedInFinancingActivities |  | -925700000 | -925700000 | Y | Y |
| R8.htm | CF | 30 | Increase in cash | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect |  | 61300000 | 61300000 | Y | Y |
| R8.htm | CF | 31 | Net Cash Provided by (Used in) Discontinued Operations | us-gaap:NetCashProvidedByUsedInDiscontinuedOperations |  | 0 | 0 | Y | Y |
| R8.htm | CF | 32 | Cash, cash equivalents, restricted cash and restricted cash  | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |  | 201900000 |  |  | Y |
| R8.htm | CF | 33 | Cash, Cash Equivalents, Restricted Cash and Restricted Cash  | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |  | 263200000 |  |  | Y |
| R8.htm | CF | 34 | Cash paid during the period for: Interest | us-gaap:InterestPaidNet |  | 69300000 | 69300000 | Y | Y |
| R8.htm | CF | 35 | Income Taxes Paid, Federal & Foreign, Net | ori:IncomeTaxesPaidFederalForeignNet |  | 198700000 |  | custom | Y |

Totals: 108 IS/BS/CF/CI face lines with an FY0 value; 91 equal companyfacts, 0 differ, 17 without a companyfacts fact (15 custom-tag, 0 dimensional).

## Hand check vs the shared reader (data-team/companies/reads/tools/docmap.py @558f2f15, origin/work/reads/901-1000)
22 data points agree; 16 differ. The value kept is the one printed on the R page.

| data point | shared reader | this read (kept) | why |
|---|---|---|---|
| cost_of_revenue | not_presented   | OUT   | sector template (approved 2026-11-01) for a not-presented line |
| gross_profit | not_presented   | OUT   | sector template (approved 2026-11-01) for a not-presented line |
| operating_expenses | mapped BenefitsLossesAndExpenses 7952300000 | not_presented   | ruling 2026-11-12 (operating expenses never include cost of revenue) |
| sga_expense | mapped GeneralAndAdministrativeExpense  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| research_and_development | not_presented   | OUT   | sector template (approved 2026-11-01) for a not-presented line |
| interest_expense | mapped InterestExpense  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| accounts_receivable | mapped PremiumsAndOtherReceivablesNet 2782200000 | not_presented   | face lines re-read for this row: see the face-line table above |
| inventory | not_presented   | OUT   | sector template (approved 2026-11-01) for a not-presented line |
| current_assets | not_presented   | OUT   | sector template (approved 2026-11-01) for a not-presented line |
| goodwill | mapped Goodwill  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| accounts_payable | mapped AccountsPayableCurrent  | combined AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent 601800000 | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| current_liabilities | not_presented   | OUT   | sector template (approved 2026-11-01) for a not-presented line |
| capex | mapped PaymentsToAcquirePropertyPlantAndEquipment  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| depreciation_and_amortization | component_in_note Depreciation  | not_presented   | face lines re-read for this row: see the face-line table above |
| sbc | mapped AllocatedShareBasedCompensationExpense  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
| shares_outstanding | mapped CommonStockSharesOutstanding  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
