# AUR document-first map 2026-11-12 (rank 706, read-only)

Evidence: FILING-CHECKED unless a row says otherwise. Printed values come from the R pages of the 10-K on sec.gov; tags from each R-page row's element reference; API = SEC companyfacts (undimensioned, same accession, same period); FSN = our fsn.line rows for the same filing and report.

Company: Aurora Innovation, Inc. (CIK 0001828108); sector shape read from the face: general.

## Filings opened
- Latest 10-K 0001828108-26-000016 (index from FSN store (fsn.filing, fsn.report)): R3.htm Consolidated Balance Sheets [BS], R4.htm Consolidated Balance Sheets (Parenthetical) [BSP], R5.htm Consolidated Statements of Operations [IS], R6.htm Consolidated Statements of Comprehensive Loss [CI], R8.htm Consolidated Statements of Cash Flows [CF].
- Era 10-K 0001628280-22-005886 (FY2021): R5.htm Consolidated Statements of Operations, R6.htm Consolidated Statements of Comprehensive Loss, R8.htm Consolidated Statements of Redeemable Convertible Preferred Stock and Stockholders Deficit (Parenthetical), R9.htm Statement of Cash Flows (Statement).
- Era 10-K 0001828108-25-000028 (FY2024): R3.htm Consolidated Balance Sheets, R5.htm Consolidated Statements of Operations, R6.htm Consolidated Statements of Comprehensive Loss, R8.htm Consolidated Statements of Cash Flows.
- Era 10-K 0001828108-23-000020 (FY2022): R3.htm Consolidated Balance Sheets, R5.htm Consolidated Statements of Operations, R6.htm Consolidated Statements of Comprehensive Loss, R8.htm Consolidated Statements of Redeemable Convertible Preferred Stock and Stockholders Equity (Parenthetical), R9.htm Consolidated Statements of Cash Flows.
- companyfacts: one call to data.sec.gov.
- sec.gov requests for this company: 0.

FY0 = the latest fiscal-year column, FY1 = the prior year. Values in full units (printed value × the R-page scale); EPS per share; shares in shares.

## Data points (the CSV holds exactly these rows)
| data point | status | tag(s) | R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match |
|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 3000000 | 3000000 | 0 | 0 | Y |
| cost_of_revenue | mapped | CostOfRevenue | R5.htm | Cost of revenue | 17000000 | 17000000 | 0 | 0 | Y |
| gross_profit | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| operating_expenses | component sum | ResearchAndDevelopmentExpense;SellingGeneralAndAdministrativeExpense | R5.htm | Research and development + Selling, general and administrative | 887000000 | 887000000 | 786000000 | 786000000 | Y |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 142000000 | 142000000 | 110000000 | 110000000 | Y |
| research_and_development | mapped | ResearchAndDevelopmentExpense | R5.htm | Research and development | 745000000 | 745000000 | 676000000 | 676000000 | Y |
| operating_income | mapped | OperatingIncomeLoss | R5.htm | Loss from operations | -901000000 | -901000000 | -786000000 | -786000000 | Y |
| interest_expense | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| interest_income | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | R5.htm | Other income, net | 56000000 | 56000000 | 62000000 | 62000000 | Y |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Loss before income taxes | -816000000 | -816000000 | -748000000 | -748000000 | Y |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 0 | 0 | 0 | 0 | Y |
| net_income | mapped | NetIncomeLoss | R5.htm | Net loss | -816000000 | -816000000 | -748000000 | -748000000 | Y |
| basic_eps | mapped | EarningsPerShareBasic | R5.htm | Basic net loss per share (in usd per share) | -0.44 | -0.44 | -0.46 | -0.46 | Y |
| diluted_eps | mapped | EarningsPerShareDiluted | R5.htm | Diluted net loss per share (in usd per share) | -0.44 | -0.44 | -0.46 | -0.46 | Y |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic weighted-average shares outstanding (in shares) | 1839000000 | 1839000000 | 1618000000 | 1618000000 | Y |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted weighted-average shares outstanding (in shares) | 1839000000 | 1839000000 | 1618000000 | 1618000000 | Y |
| dividends_per_share | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R6.htm | Comprehensive loss | -815000000 | -815000000 | -748000000 | -748000000 | Y |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 221000000 | 221000000 | 211000000 | 211000000 | Y |
| accounts_receivable | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| inventory | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| current_assets | mapped | AssetsCurrent | R3.htm | Total current assets | 1317000000 | 1317000000 | 1254000000 | 1254000000 | Y |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 103000000 | 103000000 | 104000000 | 104000000 | Y |
| goodwill | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| total_assets | mapped | Assets | R3.htm | Total assets | 2343000000 | 2343000000 | 2138000000 | 2138000000 | Y |
| accounts_payable | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| current_liabilities | mapped | LiabilitiesCurrent | R3.htm | Total current liabilities | 111000000 | 111000000 | 105000000 | 105000000 | Y |
| total_liabilities | mapped | Liabilities | R3.htm | Total liabilities | 203000000 | 203000000 | 263000000 | 263000000 | Y |
| total_debt | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| stockholders_equity | mapped | StockholdersEquity | R3.htm | Total stockholders’ equity | 2140000000 | 2140000000 | 1875000000 | 1875000000 | Y |
| shares_outstanding | mapped | CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 1943000000 | 1943000000 | 1733000000 |  | Y |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash used in operating activities | -581000000 | -581000000 | -611000000 | -611000000 | Y |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash (used in) provided by investing activities | -245000000 | -245000000 | -172000000 | -172000000 | Y |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by financing activities | 834000000 | 834000000 | 492000000 | 492000000 | Y |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -31000000 | 31000000 | -34000000 | 34000000 | Y (sign differs: printed in parentheses/negated label) |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 30000000 | 30000000 | 21000000 | 21000000 | Y |
| amortization_of_intangibles | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| sbc | mapped | ShareBasedCompensation | R8.htm | Stock-based compensation | 188000000 | 188000000 | 144000000 | 144000000 | Y |
| dividends_paid | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| share_buybacks | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_ar_change | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_inventory_change | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cf_ap_change | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cash_paid_for_interest | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| cash_paid_for_income_taxes | not_presented |  |  |  |  |  |  |  | no face line carries this data point in the latest 10-K statements (fa |
| net_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| total_interest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_income | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| noninterest_expense | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| provision_for_credit_losses | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| deposits | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |
| loans_net | OUT |  |  |  |  |  |  |  | not a bank (no deposits/bank income lines on the face) |

Sector lines also on the face (not in the graded vocabulary): intangibles_net = IntangibleAssetsNetExcludingGoodwill 'Acquisition related intangible assets, net' 617000000.

## Eras FY2015 to FY2025 (every data point; companyfacts tag per original 10-K, and the era 10-Ks opened: FY2015 always, plus the last 10-K of each earlier era)
- First 10-K in companyfacts is FY2021: no FY2015 10-K exists for this registrant.
| data point | latest status | eras (companyfacts) | era 10-K reads (FILING-CHECKED) | coverage |
|---|---|---|---|---|
| revenue | mapped | FY2021-FY2022: RevenueFromContractWithCustomerExcludingAssessedTax; FY2023-FY2024: no standard tag; FY2025-FY2025: RevenueFromContractWithCustomerExcludingAssessedTax | FY2021 10-K 0001628280-22-005886 R5.htm 'Collaboration revenue' RevenueFromContractWithCustomerExcludingAssessedTax (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028: no face line; FY2022 10-K 0001828108-23-000020 R5.htm 'Collaboration revenue' RevenueFromContractWithCustomerExcludingAssessedTax (mapped) FILING-CHECKED | coverage FY2021-FY2025 gaps FY2023,2024 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2021) |
| cost_of_revenue | mapped | FY2021-FY2024: no standard tag; FY2025-FY2025: CostOfRevenue | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028: no face line; FY2022 10-K 0001828108-23-000020: no face line | coverage FY2021-FY2025 gaps FY2021,2022,2023,2024 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2021) |
| operating_expenses | component sum | FY2021-FY2025: ResearchAndDevelopmentExpense+SellingGeneralAndAdministrativeExpense | FY2021 10-K 0001628280-22-005886 R5.htm 'Total operating expenses' OperatingExpenses (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Total operating expenses' OperatingExpenses (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Total operating expenses' OperatingExpenses (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| sga_expense | mapped | FY2021-FY2025: SellingGeneralAndAdministrativeExpense | FY2021 10-K 0001628280-22-005886 R5.htm 'Selling, general and administrative' SellingGeneralAndAdministrativeExpense (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Selling, general and administrative' SellingGeneralAndAdministrativeExpense (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Selling, general and administrative' SellingGeneralAndAdministrativeExpense (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| research_and_development | mapped | FY2021-FY2025: ResearchAndDevelopmentExpense | FY2021 10-K 0001628280-22-005886 R5.htm 'Research and development' ResearchAndDevelopmentExpense (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Research and development' ResearchAndDevelopmentExpense (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Research and development' ResearchAndDevelopmentExpense (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| operating_income | mapped | FY2021-FY2025: OperatingIncomeLoss | FY2021 10-K 0001628280-22-005886 R5.htm 'Loss from operations' OperatingIncomeLoss (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Loss from operations' OperatingIncomeLoss (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Loss from operations' OperatingIncomeLoss (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| other_income_expense_net | mapped | FY2021-FY2021: no standard tag; FY2022-FY2025: OtherNonoperatingIncomeExpense | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R5.htm 'Other income, net' OtherNonoperatingIncomeExpense (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Other income (expense), net' OtherNonoperatingIncomeExpense (mapped) FILING-CHECKED | coverage FY2021-FY2025 gaps FY2021 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2021) |
| income_before_tax | mapped | FY2021-FY2025: IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | FY2021 10-K 0001628280-22-005886 R5.htm 'Total loss from operations before income' IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Loss before income taxes' IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Loss before income taxes' IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| income_tax_expense | mapped | FY2021-FY2025: IncomeTaxExpenseBenefit | FY2021 10-K 0001628280-22-005886 R5.htm 'Income tax expense (benefit)' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Income tax expense' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Income tax benefit' IncomeTaxExpenseBenefit (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| net_income | mapped | FY2021-FY2025: NetIncomeLoss | FY2021 10-K 0001628280-22-005886 R5.htm 'Net loss' NetIncomeLoss (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Net loss' NetIncomeLoss (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Net loss' NetIncomeLoss (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| basic_eps | mapped | FY2021-FY2025: EarningsPerShareBasic | FY2021 10-K 0001628280-22-005886 R5.htm 'Basic net loss per share (in usd per sha' EarningsPerShareBasic (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Basic net loss per share (in usd per sha' EarningsPerShareBasic (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Basic net loss per share (in usd per sha' EarningsPerShareBasic (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| diluted_eps | mapped | FY2021-FY2025: EarningsPerShareDiluted | FY2021 10-K 0001628280-22-005886 R5.htm 'Diluted net loss per share (in usd per s' EarningsPerShareDiluted (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Diluted net loss per share (in usd per s' EarningsPerShareDiluted (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Diluted net loss per share (in usd per s' EarningsPerShareDiluted (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| weighted_basic_shares | mapped | FY2021-FY2025: WeightedAverageNumberOfSharesOutstandingBasic | FY2021 10-K 0001628280-22-005886 R5.htm 'Basic weighted-average shares outstandin' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Basic weighted-average shares outstandin' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Basic weighted-average shares outstandin' WeightedAverageNumberOfSharesOutstandingBasic (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| weighted_diluted_shares | mapped | FY2021-FY2025: WeightedAverageNumberOfDilutedSharesOutstanding | FY2021 10-K 0001628280-22-005886 R5.htm 'Diluted weighted-average shares outstand' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R5.htm 'Diluted weighted-average shares outstand' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R5.htm 'Diluted weighted-average shares outstand' WeightedAverageNumberOfDilutedSharesOutstanding (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| comprehensive_income | mapped | FY2021-FY2025: ComprehensiveIncomeNetOfTax | FY2021 10-K 0001628280-22-005886 R6.htm 'Comprehensive loss' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R6.htm 'Comprehensive loss' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R6.htm 'Comprehensive loss' ComprehensiveIncomeNetOfTax (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| cash_and_equivalents | mapped | FY2021-FY2025: CashAndCashEquivalentsAtCarryingValue | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Cash and cash equivalents' CashAndCashEquivalentsAtCarryingValue (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Cash and cash equivalents' CashAndCashEquivalentsAtCarryingValue (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| current_assets | mapped | FY2021-FY2025: AssetsCurrent | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Total current assets' AssetsCurrent (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Total current assets' AssetsCurrent (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| ppe_net | mapped | FY2021-FY2025: PropertyPlantAndEquipmentNet | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Property and equipment, net' PropertyPlantAndEquipmentNet (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Property and equipment, net' PropertyPlantAndEquipmentNet (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| total_assets | mapped | FY2021-FY2025: Assets | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Total assets' Assets (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Total assets' Assets (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| current_liabilities | mapped | FY2021-FY2025: LiabilitiesCurrent | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Total current liabilities' LiabilitiesCurrent (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Total current liabilities' LiabilitiesCurrent (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| total_liabilities | mapped | FY2021-FY2025: Liabilities | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Total liabilities' Liabilities (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| stockholders_equity | mapped | FY2021-FY2025: StockholdersEquity | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028 R3.htm 'Total stockholders’ equity' StockholdersEquity (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R3.htm 'Total stockholders’ equity' StockholdersEquity (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| shares_outstanding | mapped | FY2021-FY2021: no standard tag; FY2022-FY2025: CommonStockSharesOutstanding | FY2021 10-K 0001628280-22-005886: no face line; FY2024 10-K 0001828108-25-000028: no face line; FY2022 10-K 0001828108-23-000020: no face line | coverage FY2021-FY2025 gaps FY2021 (no standard-tag 10-K fact; see FILING-CHECKED era reads) (first 10-K FY2021) |
| cfo | mapped | FY2021-FY2025: NetCashProvidedByUsedInOperatingActivities | FY2021 10-K 0001628280-22-005886 R9.htm 'Net cash used in operating activities' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R8.htm 'Net cash used in operating activities' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R9.htm 'Net cash used in operating activities' NetCashProvidedByUsedInOperatingActivities (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| cash_flow_investing | mapped | FY2021-FY2025: NetCashProvidedByUsedInInvestingActivities | FY2021 10-K 0001628280-22-005886 R9.htm 'Net cash provided by investing activitie' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R8.htm 'Net cash (used in) provided by investing' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R9.htm 'Net cash (used in) provided by investing' NetCashProvidedByUsedInInvestingActivities (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| cash_flow_financing | mapped | FY2021-FY2025: NetCashProvidedByUsedInFinancingActivities | FY2021 10-K 0001628280-22-005886 R9.htm 'Net cash provided by financing activitie' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R8.htm 'Net cash provided by financing activitie' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R9.htm 'Net cash provided by financing activitie' NetCashProvidedByUsedInFinancingActivities (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| capex | mapped | FY2021-FY2025: PaymentsToAcquirePropertyPlantAndEquipment | FY2021 10-K 0001628280-22-005886 R9.htm 'Purchases of property and equipment' PaymentsToAcquirePropertyPlantAndEquipment (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R8.htm 'Purchases of property and equipment' PaymentsToAcquirePropertyPlantAndEquipment (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R9.htm 'Purchases of property and equipment' PaymentsToAcquirePropertyPlantAndEquipment (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| depreciation_and_amortization | mapped | FY2021-FY2025: DepreciationDepletionAndAmortization | FY2021 10-K 0001628280-22-005886 R9.htm 'Depreciation and amortization' DepreciationDepletionAndAmortization (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R8.htm 'Depreciation and amortization' DepreciationDepletionAndAmortization (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R9.htm 'Depreciation and amortization' DepreciationDepletionAndAmortization (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |
| sbc | mapped | FY2021-FY2025: ShareBasedCompensation | FY2021 10-K 0001628280-22-005886 R9.htm 'Stock based compensation' ShareBasedCompensation (mapped) FILING-CHECKED; FY2024 10-K 0001828108-25-000028 R8.htm 'Stock-based compensation' ShareBasedCompensation (mapped) FILING-CHECKED; FY2022 10-K 0001828108-23-000020 R9.htm 'Stock-based compensation' ShareBasedCompensation (mapped) FILING-CHECKED | coverage FY2021-FY2025 complete (first 10-K FY2021) |

## Quirks and mismatches (the filing decides)
- none

## Every face line (printed page → tag → FSN → companyfacts)
| R | stmt | # | label | tag | member | FY0 printed | FY0 API | match | in FSN |
|---|---|---|---|---|---|---|---|---|---|
| R3.htm | BS | 1 | Cash and cash equivalents | us-gaap:CashAndCashEquivalentsAtCarryingValue |  | 221000000 | 221000000 | Y | Y |
| R3.htm | BS | 2 | Short-term investments | us-gaap:DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent |  | 1055000000 | 1055000000 | Y | Y |
| R3.htm | BS | 3 | Other current assets | us-gaap:OtherAssetsCurrent |  | 41000000 | 41000000 | Y | Y |
| R3.htm | BS | 4 | Total current assets | us-gaap:AssetsCurrent |  | 1317000000 | 1317000000 | Y | Y |
| R3.htm | BS | 5 | Property and equipment, net | us-gaap:PropertyPlantAndEquipmentNet |  | 103000000 | 103000000 | Y | Y |
| R3.htm | BS | 6 | Operating lease right-of-use assets | us-gaap:OperatingLeaseRightOfUseAsset |  | 85000000 | 85000000 | Y | Y |
| R3.htm | BS | 7 | Acquisition related intangible assets, net | us-gaap:IntangibleAssetsNetExcludingGoodwill |  | 617000000 | 617000000 | Y | Y |
| R3.htm | BS | 8 | Long-term investments | us-gaap:DebtSecuritiesAvailableForSaleExcludingAccruedInterestNoncurrent |  | 183000000 | 183000000 | Y | Y |
| R3.htm | BS | 9 | Other assets | us-gaap:OtherAssetsNoncurrent |  | 38000000 | 38000000 | Y | Y |
| R3.htm | BS | 10 | Total assets | us-gaap:Assets |  | 2343000000 | 2343000000 | Y | Y |
| R3.htm | BS | 11 | Operating lease liabilities, current | us-gaap:OperatingLeaseLiabilityCurrent |  | 11000000 | 11000000 | Y | Y |
| R3.htm | BS | 12 | Other current liabilities | us-gaap:AccruedLiabilitiesCurrent |  | 100000000 | 100000000 | Y | Y |
| R3.htm | BS | 13 | Total current liabilities | us-gaap:LiabilitiesCurrent |  | 111000000 | 111000000 | Y | Y |
| R3.htm | BS | 14 | Operating lease liabilities, long-term | us-gaap:OperatingLeaseLiabilityNoncurrent |  | 73000000 | 73000000 | Y | Y |
| R3.htm | BS | 15 | Derivative liabilities, long-term | us-gaap:DerivativeLiabilitiesNoncurrent |  | 15000000 | 15000000 | Y | Y |
| R3.htm | BS | 16 | Other liabilities | us-gaap:OtherLiabilitiesNoncurrent |  | 4000000 | 4000000 | Y | Y |
| R3.htm | BS | 17 | Total liabilities | us-gaap:Liabilities |  | 203000000 | 203000000 | Y | Y |
| R3.htm | BS | 18 | Commitments and contingencies | us-gaap:CommitmentsAndContingencies |  |  |  |  | Y |
| R3.htm | BS | 19 | Common stock - $0.00001 par value, 51,000 shares authorized, | us-gaap:CommonStockValue |  | 0 | 0 | Y | Y |
| R3.htm | BS | 20 | Additional paid-in capital | us-gaap:AdditionalPaidInCapital |  | 7312000000 | 7312000000 | Y | Y |
| R3.htm | BS | 21 | Accumulated other comprehensive income | us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax |  | 2000000 | 2000000 | Y | Y |
| R3.htm | BS | 22 | Accumulated deficit | us-gaap:RetainedEarningsAccumulatedDeficit |  | -5174000000 | -5174000000 | Y | Y |
| R3.htm | BS | 23 | Total stockholders’ equity | us-gaap:StockholdersEquity |  | 2140000000 | 2140000000 | Y | Y |
| R3.htm | BS | 24 | Total liabilities and stockholders’ equity | us-gaap:LiabilitiesAndStockholdersEquity |  | 2343000000 | 2343000000 | Y | Y |
| R4.htm | BSP | 1 | Common stock, par value (in usd per share) | us-gaap:CommonStockParOrStatedValuePerShare |  | 0 | 0 | Y | N |
| R4.htm | BSP | 2 | Common stock, shares authorized (in shares) | us-gaap:CommonStockSharesAuthorized |  | 51000000000 | 51000000000 | Y | N |
| R4.htm | BSP | 3 | Common stock, shares issued (in shares) | us-gaap:CommonStockSharesIssued |  | 1943000000 | 1943000000 | Y | N |
| R4.htm | BSP | 4 | Common stock, shares outstanding (in shares) | us-gaap:CommonStockSharesOutstanding |  | 1943000000 | 1943000000 | Y | N |
| R5.htm | IS | 1 | Revenue | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |  | 3000000 | 3000000 | Y | Y |
| R5.htm | IS | 2 | Cost of revenue | us-gaap:CostOfRevenue |  | 17000000 | 17000000 | Y | Y |
| R5.htm | IS | 3 | Research and development | us-gaap:ResearchAndDevelopmentExpense |  | 745000000 | 745000000 | Y | Y |
| R5.htm | IS | 4 | Selling, general and administrative | us-gaap:SellingGeneralAndAdministrativeExpense |  | 142000000 | 142000000 | Y | Y |
| R5.htm | IS | 5 | Loss from operations | us-gaap:OperatingIncomeLoss |  | -901000000 | -901000000 | Y | Y |
| R5.htm | IS | 6 | Change in fair value of derivative liabilities | us-gaap:DerivativeGainLossOnDerivativeNet |  | 29000000 | 29000000 | Y | Y |
| R5.htm | IS | 7 | Other income, net | us-gaap:OtherNonoperatingIncomeExpense |  | 56000000 | 56000000 | Y | Y |
| R5.htm | IS | 8 | Loss before income taxes | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |  | -816000000 | -816000000 | Y | Y |
| R5.htm | IS | 9 | Income tax expense | us-gaap:IncomeTaxExpenseBenefit |  | 0 | 0 | Y | Y |
| R5.htm | IS | 10 | Net loss | us-gaap:NetIncomeLoss |  | -816000000 | -816000000 | Y | Y |
| R5.htm | IS | 11 | Basic net loss per share (in usd per share) | us-gaap:EarningsPerShareBasic |  | -0.44 | -0.44 | Y | Y |
| R5.htm | IS | 12 | Diluted net loss per share (in usd per share) | us-gaap:EarningsPerShareDiluted |  | -0.44 | -0.44 | Y | Y |
| R5.htm | IS | 13 | Basic weighted-average shares outstanding (in shares) | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic |  | 1839000000 | 1839000000 | Y | Y |
| R5.htm | IS | 14 | Diluted weighted-average shares outstanding (in shares) | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding |  | 1839000000 | 1839000000 | Y | Y |
| R6.htm | CI | 1 | Net loss | us-gaap:NetIncomeLoss |  | -816000000 | -816000000 | Y | Y |
| R6.htm | CI | 2 | Unrealized income on investments | us-gaap:OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax |  | 1000000 | 1000000 | Y | Y |
| R6.htm | CI | 3 | Other comprehensive income | us-gaap:OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent |  | 1000000 | 1000000 | Y | Y |
| R6.htm | CI | 4 | Comprehensive loss | us-gaap:ComprehensiveIncomeNetOfTax |  | -815000000 | -815000000 | Y | Y |
| R8.htm | CF | 1 | Net loss | us-gaap:NetIncomeLoss |  | -816000000 | -816000000 | Y | Y |
| R8.htm | CF | 2 | Depreciation and amortization | us-gaap:DepreciationDepletionAndAmortization |  | 30000000 | 30000000 | Y | Y |
| R8.htm | CF | 3 | Reduction in the carrying amount of right-of-use assets | us-gaap:OperatingLeaseRightOfUseAssetAmortizationExpense |  | 28000000 | 28000000 | Y | Y |
| R8.htm | CF | 4 | Stock-based compensation | us-gaap:ShareBasedCompensation |  | 188000000 | 188000000 | Y | Y |
| R8.htm | CF | 5 | Change in fair value of derivative liabilities | us-gaap:DerivativeGainLossOnDerivativeNet |  | -29000000 | 29000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 6 | Accretion of discount on investments | us-gaap:AccretionAmortizationOfDiscountsAndPremiumsInvestments |  | -11000000 | 11000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 7 | Other operating activities | us-gaap:OtherOperatingActivitiesCashFlowStatement |  | 0 | 0 | Y | Y |
| R8.htm | CF | 8 | Other current and non-current assets | aur:IncreaseDecreaseInOtherCurrentAndNonCurrentAssets |  | -9000000 |  | custom | Y |
| R8.htm | CF | 9 | Operating lease liabilities | us-gaap:IncreaseDecreaseInOperatingLeaseLiability |  | -29000000 | -29000000 | Y | Y |
| R8.htm | CF | 10 | Other current and non-current liabilities | aur:IncreaseDecreaseInOtherCurrentAndNonCurrentLiabilities |  | 67000000 |  | custom | Y |
| R8.htm | CF | 11 | Net cash used in operating activities | us-gaap:NetCashProvidedByUsedInOperatingActivities |  | -581000000 | -581000000 | Y | Y |
| R8.htm | CF | 12 | Purchases of property and equipment | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment |  | -31000000 | 31000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 13 | Purchases of investments | us-gaap:PaymentsToAcquireInvestments |  | -1452000000 | 1452000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 14 | Maturities and sales of investments | us-gaap:ProceedsFromSaleMaturityAndCollectionsOfInvestments |  | 1238000000 | 1238000000 | Y | Y |
| R8.htm | CF | 15 | Net cash (used in) provided by investing activities | us-gaap:NetCashProvidedByUsedInInvestingActivities |  | -245000000 | -245000000 | Y | Y |
| R8.htm | CF | 16 | Proceeds from issuance of common stock | us-gaap:ProceedsFromIssuanceOfCommonStock |  | 916000000 | 916000000 | Y | Y |
| R8.htm | CF | 17 | Payments for taxes on net settlement of equity incentive awa | us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation |  | -79000000 | 79000000 | Y (sign differs: printed in parentheses/negated label) | Y |
| R8.htm | CF | 18 | Other financing activities | us-gaap:ProceedsFromPaymentsForOtherFinancingActivities |  | -3000000 | -3000000 | Y | Y |
| R8.htm | CF | 19 | Net cash provided by financing activities | us-gaap:NetCashProvidedByUsedInFinancingActivities |  | 834000000 | 834000000 | Y | Y |
| R8.htm | CF | 20 | Net increase (decrease) in cash, cash equivalents, and restr | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect |  | 8000000 | 8000000 | Y | Y |
| R8.htm | CF | 21 | Cash, cash equivalents, and restricted cash at beginning of  | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |  | 227000000 |  |  | Y |
| R8.htm | CF | 22 | Cash, cash equivalents, and restricted cash at end of the pe | us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |  | 235000000 |  |  | Y |

Totals: 63 IS/BS/CF/CI face lines with an FY0 value; 59 equal companyfacts, 0 differ, 4 without a companyfacts fact (2 custom-tag, 0 dimensional).

## Hand check vs the shared reader (data-team/companies/reads/tools/docmap.py @558f2f15, origin/work/reads/901-1000)
36 data points agree; 2 differ. The value kept is the one printed on the R page.

| data point | shared reader | this read (kept) | why |
|---|---|---|---|
| operating_expenses | not_presented   | component sum ResearchAndDevelopmentExpense;SellingGeneralAndAdministrativeExpense 887000000 | ruling 2026-11-12 (operating expenses never include cost of revenue) |
| cash_paid_for_income_taxes | mapped IncomeTaxesPaid  | not_presented   | shared reader marks it from companyfacts with no printed value on the face; this read keeps the face (the filing decides) |
