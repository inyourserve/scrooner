# COF document-first map, 2026-11-12 (read-only, built bottom-up from the 10-K)

Latest 10-K: accession 0000927628-26-000024, period end 2025-12-31. Evidence: R pages of FilingSummary (face statements + notes opened: R1.htm, R3.htm, R4.htm, R5.htm, R6.htm, R7.htm, R8.htm, R9.htm, R61.htm, R63.htm, R67.htm, R86.htm, R87.htm, R90.htm, R92.htm, R93.htm, R96.htm, R97.htm, R98.htm, R107.htm, R108.htm, R112.htm, R113.htm, R116.htm, R129.htm, R130.htm, R134.htm, R135.htm, R136.htm, R137.htm), values compared with data.sec.gov companyfacts (undimensioned, same accession). Values below are scaled to full units (USD, shares, USD/share). match = printed vs API; Y(abs) = same magnitude, sign differs (expense/outflow printed negative, tag positive).  Custom (company-prefix) tags are not in companyfacts: match NA.

Bank template. Face statements: R3 income, R4 comprehensive income, R5 balance sheet (unclassified), R6 parenthetical, R8 equity, R9 cash flows. FY0 = FY2025. NOTE: FY2025 includes the Discover acquisition (balance sheet roughly +180B).

| data_point | status | tags | page | label | fy0 printed | fy0 api | fy1 printed | fy1 api | match | note |
|---|---|---|---|---|---|---|---|---|---|---|
| revenue | component sum | InterestIncomeExpenseNet;NoninterestIncome | R3.htm | Net interest income + Total non-interest income | 53434000000 | 53434000000 | 39112000000 | 39112000000 | Y/Y | bank revenue = 'Net interest income' 42,878 + 'Total non-interest income' 10,556 (duration sum of two printed face totals; no 'total net revenue' line printed; agrees with Ritwik row) / fy0=2025-12-31 fy1=2024-12-31 |
| cost_of_revenue | OUT |  |  |  |  |  |  |  |  | bank template OUT: no cost-of-revenue line (IS: interest income, interest expense, provision, non-interest income and expense) |
| gross_profit | OUT |  |  |  |  |  |  |  |  | bank template OUT: no gross profit line |
| operating_expenses | mapped | NoninterestExpense | R3.htm | Total non-interest expense | 30498000000 | 30498000000 | 21486000000 | 21486000000 | Y/Y | bank opex = face 'Total non-interest expense' 30,498 / fy0=2025-12-31 fy1=2024-12-31 |
| sga_expense | OUT |  |  |  |  |  |  |  |  | bank template OUT candidate: no SG&A line ('Salaries and associate benefits', 'Marketing', 'Occupancy and equipment' etc. are separate) |
| research_and_development | OUT |  |  |  |  |  |  |  |  | bank template OUT |
| operating_income | OUT |  |  |  |  |  |  |  |  | bank template OUT by definition: no operating income subtotal (goes to Income from continuing operations before income taxes) |
| interest_expense | mapped | InterestExpenseOperating | R3.htm | Total interest expense | 15818000000 | 15818000000 | 14826000000 | 14826000000 | Y/Y | 'Total interest expense' 15,818 (face total; sub-lines by funding type) / fy0=2025-12-31 fy1=2024-12-31 |
| interest_income | mapped | InterestAndDividendIncomeOperating | R3.htm | Total interest income | 58696000000 | 58696000000 | 46034000000 | 46034000000 | Y/Y | 'Total interest income' 58,696 / fy0=2025-12-31 fy1=2024-12-31 |
| other_income_expense_net | OUT |  |  |  |  |  |  |  |  | bank: no non-operating other income line; non-interest income / expense are the face totals |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income from continuing operations before income taxes | 2281000000 | 2281000000 | 5910000000 | 5910000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R3.htm | Income tax provision | 193000000 | 193000000 | 1163000000 | 1163000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| net_income | mapped | NetIncomeLoss | R3.htm | Net income | 2453000000 | 2453000000 | 4750000000 | 4750000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | R3.htm | Net income (loss) per basic common share (in dollars per sha | 4.03 | 4.03 | 11.61 | 11.61 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | R3.htm | Net income (loss) per diluted common share (in dollars per s | 4.03 | 4.03 | 11.59 | 11.59 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R112.htm | Total weighted-average basic common shares outstanding (in s | 540700000 | 540700000 | 382700000 | 382700000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R112.htm | Total weighted-average diluted common shares outstanding (in | 541300000 | 541300000 | 383600000 | 383600000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_per_share | not_presented |  |  |  |  |  |  |  |  | equity statement parenthetical R8 prints only quarterly 'Dividend per share on common stock declared' (0.80 Q4-2025, 0.60 for each of Q1-Q3 2025); no annual figure is printed or tagged for the year (companyfacts holds quarterly fa |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R4.htm | Comprehensive income | 6271000000 | 6271000000 | 3732000000 | 3732000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_and_equivalents | mapped | CashCashEquivalentsAndFederalFundsSold | R5.htm | Total cash and cash equivalents | 57434000000 | 57434000000 | 43230000000 | 43230000000 | Y/Y | DISAGREE WITH RITWIK (CashAndDueFromBanks 3,031): BS face prints 'Total cash and cash equivalents' 57,434 = cash and due from banks 3,031 + interest-bearing deposits and other short-term investments 54,403; cash card: never CashAn |
| accounts_receivable | OUT |  |  |  |  |  |  |  |  | bank template OUT: 'Interest receivable' (InterestReceivable 3,492) is not trade AR; loans are not receivables |
| inventory | OUT |  |  |  |  |  |  |  |  | bank template OUT |
| current_assets | OUT |  |  |  |  |  |  |  |  | unclassified BS: no current totals (R5 read) |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | R5.htm | Premises and equipment, net | 5602000000 | 5602000000 | 4511000000 | 4511000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| goodwill | mapped | Goodwill | R5.htm | Goodwill | 28509000000 | 28509000000 | 15059000000 | 15059000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| total_assets | mapped | Assets | R5.htm | Total assets | 669009000000 | 669009000000 | 490144000000 | 490144000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| accounts_payable | OUT |  |  |  |  |  |  |  |  | bank template OUT: no accounts payable line ('Interest payable' 844, 'Other liabilities' 27,778) |
| current_liabilities | OUT |  |  |  |  |  |  |  |  | unclassified BS: no current totals (R5 read) |
| total_liabilities | mapped | Liabilities | R5.htm | Total liabilities | 555393000000 | 555393000000 | 429360000000 | 429360000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| total_debt | component sum | SecuredDebt;UnsecuredDebt;OtherBorrowings | R5.htm | Securitized debt obligations + Senior and subordinated notes | 50413000000 | 50413000000 | 44989000000 | 44989000000 | Y/Y | HELD, bank debt perimeter pending: candidate = 'Securitized debt obligations' 12,853 + 'Senior and subordinated notes' 36,001 + 'Other borrowings' 1,559; the BS also prints custom subtotal 'Total other debt' 38,147 (cof:DebtExclud |
| stockholders_equity | mapped | StockholdersEquity | R5.htm | Total stockholders’ equity | 113616000000 | 113616000000 | 60784000000 | 60784000000 | Y/Y | 'Total stockholders' equity' 113,616 / fy0=2025-12-31 fy1=2024-12-31 |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | R1.htm | Entity Common Stock, Shares Outstanding (cover, as of cover  | 621,931,593 | 621931593 |  |  | Y/NA | cover dei; BS parenthetical R6 has CommonStockSharesOutstanding / cover date not period end; dei facts in companyfacts lack the class dimension |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash from operating activities | 27718000000 | 27718000000 | 18159000000 | 18159000000 | Y/Y | CF face total / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -444000000 | -444000000 | -26410000000 | -26410000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash from (used in) financing activities | -8852000000 | -8852000000 | 8167000000 | 8167000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| capex | OUT | PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Changes in premises and equipment | -1578000000 | 1578000000 | -1204000000 | 1204000000 | Y(abs)/Y(abs) | bank template OUT by definition (approved category C); CF prints only a net line 'Changes in premises and equipment' (1,578), tagged PaymentsToAcquirePropertyPlantAndEquipment / fy0=2025-12-31 fy1=2024-12-31 |
| depreciation_and_amortization | mapped | DepreciationAndAmortization | R9.htm | Depreciation and amortization, net | 5260000000 | 5260000000 | 3237000000 | 3237000000 | Y/Y | CF 'Depreciation and amortization, net' 5,260 (net caption: includes premium/discount and intangible amortization; combined perimeter) / fy0=2025-12-31 fy1=2024-12-31 |
| amortization_of_intangibles | mapped | cof:AmortizationAndImpairmentOfIntangibles | R3.htm | Amortization of intangibles | 1326000000 |  | 77000000 |  | NA/NA | IS 'Amortization of intangibles' 1,326 on a custom tag named 'Amortization and impairment of intangibles' (impairment may be inside); companyfacts has no value; the note R90 prints AmortizationOfIntangibleAssets / API MISSING: Amo |
| sbc | mapped | ShareBasedCompensation | R9.htm | Stock-based compensation expense | 776000000 | 776000000 | 569000000 | 569000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_paid | mapped | PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -1516000000 | 1516000000 | -932000000 | 932000000 | Y(abs)/Y(abs) | common dividends 1,516; preferred dividends 252 separate / fy0=2025-12-31 fy1=2024-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | R9.htm | Purchases of treasury stock | -4099000000 | 4099000000 | -734000000 | 734000000 | Y(abs)/Y(abs) | 'Purchases of treasury stock' 4,099 / fy0=2025-12-31 fy1=2024-12-31 |
| cf_ar_change | OUT |  |  |  |  |  |  |  |  | bank template OUT |
| cf_inventory_change | OUT |  |  |  |  |  |  |  |  | bank template OUT |
| cf_ap_change | OUT |  |  |  |  |  |  |  |  | bank template OUT |
| cash_paid_for_interest | mapped | InterestPaidNet | R9.htm | Interest paid | 14886000000 | 14886000000 | 13201000000 | 13201000000 | Y/Y | auto: first candidate tag on face / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | R9.htm | Income taxes paid | 806000000 | 806000000 | 1105000000 | 1105000000 | Y/Y | CF supplemental (face, below federal/state split) / fy0=2025-12-31 fy1=2024-12-31 |

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
1 DISAGREEMENT: cash_and_equivalents. Ritwik maps CashAndDueFromBanks 3,031 ('bank: cash and due from banks', 2013-2025). The FY2025 BS prints 'Total cash and cash equivalents' 57,434 (CashCashEquivalentsAndFederalFundsSold) = cash and due from banks + interest-bearing deposits and other short-term investments; the cash card says never take CashAndDueFromBanks as bank cash, and the bank rule points to the printed combined figure (CF ending 62,093 incl. 4,659 restricted cash, or the BS total 57,434): the filing does not support 3,031. Agreements: revenue = NII + non-interest income (component sum, no total net revenue line); interest_expense = 'Total interest expense' (total wins); insurer/bank OUT for cost_of_revenue, gross_profit, operating_income, current assets/liabilities confirmed on R3/R5 (those were template_out_pending_read).

## Era checks (older 10-K opened: tag on the same printed line?)
Older 10-K opened: 0000927628-22-000106 (period 2021-12-31); face pages ['R3.htm', 'R4.htm', 'R5.htm', 'R6.htm', 'R7.htm', 'R8.htm', 'R9.htm']. Result: 30 mapped rows checked.
- interest_expense: TAG CHANGED vs 0000927628-22-000106 (2021-12-31): old tag us-gaap:InterestExpense on 'Total interest expense' (new 'Total interest expense' us-gaap:InterestExpenseOperating)
- amortization_of_intangibles: tag cof:AmortizationAndImpairmentOfIntangibles ABSENT from the old filing 0000927628-22-000106 (2021-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read)
- cash_paid_for_income_taxes: TAG CHANGED vs 0000927628-22-000106 (2021-12-31): old tag us-gaap:IncomeTaxesPaid on 'Income tax paid' (new 'Income taxes paid' us-gaap:IncomeTaxesPaidNet)
- (27 rows: same tag and same label on the older 10-K, no change)

## Mismatches / unresolved
- none

## Method and untested scope
- FILING-CHECKED = value read from the 10-K R page (MetaLinks used to locate tags/pages) and compared with companyfacts for the same accession; not_presented/OUT rows are FILING-CHECKED for the statements opened (all face statements plus the note pages that carry the candidate tags per MetaLinks); a note not opened could still hold an unprinted detail.
- Era check: one older 10-K per company (statement pages only, via MetaLinks); same-tag / label comparison on the same statement type. Note-page values of the older filing were not opened.
- Not covered: 10-Q-era tag history, quarterly values, segment-level data points, FSN store comparison (document-first read only).