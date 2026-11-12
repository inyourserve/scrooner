# OSK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing, tags from the R-page element references = MetaLinks equivalent; API = SEC companyfacts, undimensioned, same accession, same period). Extension (custom) tags are not in companyfacts: those rows are checked against the R page only.

## Filings opened
- Latest 10-K 0001193125-26-054061 (CIK 0000775158, Oshkosh Corporation, filed 2026-02-17, FY ended 2025-12-31); filing index and statement-page list from FSN report index (our DB). R pages fetched from sec.gov: R2.htm IS '2IS'; R3.htm CI '3CI'; R4.htm BS '4BS'; R5.htm PAR '5BSp'; R6.htm EQ '6EQ'; R7.htm PAR '7EQp'; R8.htm CF '8CF'; cover R1.htm.
- companyfacts CIK0000775158.json (data.sec.gov, one call; our raw companyfacts copy sits in Supabase Storage, which this session cannot read).

FY0 = 2025-12-31; FY1 = prior year. Values in full USD (printed value x the R-page scale); EPS per share; shares in shares.

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | IS R2.htm | Net sales | 10422300000 | 10422300000 | 10730200000 | 10730200000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | IS R2.htm | Cost of sales | 8603300000 | 8603300000 | 8760800000 | 8760800000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| gross_profit | mapped | GrossProfit | IS R2.htm | Gross income | 1819000000 | 1819000000 | 1969400000 | 1969400000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| operating_expenses | mapped | OperatingExpenses | IS R2.htm | Total operating expenses | 879500000 | 879500000 | 958700000 | 958700000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| sga_expense | mapped | SellingGeneralAndAdministrativeExpense | IS R2.htm | Selling, general and administrative | 818700000 | 818700000 | 852400000 | 852400000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| research_and_development | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no research and development line on the face |
| operating_income | mapped | OperatingIncomeLoss | IS R2.htm | Operating income | 939500000 | 939500000 | 1010700000 | 1010700000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| interest_expense | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no interest expense line on the face |
| interest_income | mapped | InvestmentIncomeInterest | IS R2.htm | Interest income | 8700000 | 8700000 | 7600000 | 7600000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | IS R2.htm | Miscellaneous, net | 11400000 | 11400000 | 4200000 | 4200000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | IS R2.htm | Income before income taxes and losses of unconsolidated affi | 842000000 | 842000000 | 903000000 | 903000000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R2.htm | Provision for income taxes | 191500000 | 191500000 | 210000000 | 210000000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| net_income | combined | ProfitLoss | IS R2.htm | Net income | 647000000 | 647000000 | 681400000 | 681400000 | Y | FILING-CHECKED | 'Net income': includes noncontrolling interests | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| basic_eps | mapped | IncomeLossFromContinuingOperationsPerBasicShare | IS R2.htm | Basic | 10.08 | 10.08 | 10.41 | 10.41 | Y | FILING-CHECKED | 'Basic': continuing operations only | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| diluted_eps | mapped | IncomeLossFromContinuingOperationsPerDilutedShare | IS R2.htm | Diluted | 10.02 | 10.02 | 10.35 | 10.35 | Y | FILING-CHECKED | 'Diluted': continuing operations only | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| weighted_basic_shares | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no weighted basic shares line on the face |
| weighted_diluted_shares | not_presented |  | IS/CI R2.htm,R3.htm  |  |  |  |  |  |  | FILING-CHECKED | no weighted diluted shares line on the face |
| dividends_per_share | mapped | CommonStockDividendsPerShareDeclared | PAR R7.htm | Cash dividends declared per share on common stock (in dollar | 2.04 | 2.04 | 1.84 | 1.84 | Y | FILING-CHECKED | printed on R7.htm (7EQp) | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| comprehensive_income | combined | ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest | CI R3.htm | Comprehensive income | 756600000 | 756600000 | 650200000 | 650200000 | Y | FILING-CHECKED | 'Comprehensive income': includes noncontrolling interests | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R4.htm | Cash and cash equivalents | 479800000 | 479800000 | 204900000 | 204900000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| accounts_receivable | combined | ReceivablesNetCurrent | BS R4.htm | Receivables, net | 1456100000 | 1456100000 | 1254700000 | 1254700000 | Y | FILING-CHECKED | wider tag us-gaap:ReceivablesNetCurrent beside other receivables lines on R4.htm (Unbilled receivables, net; Income taxes receivable): combined | accn 0001193125-26-054061 period ..2025-12-31 |
| inventory | mapped | InventoryNet | BS R4.htm | Inventories | 2375000000 | 2375000000 | 2265700000 | 2265700000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| current_assets | mapped | AssetsCurrent | BS R4.htm | Total current assets | 5168500000 | 5168500000 | 4527500000 | 4527500000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | BS R4.htm | Property, plant and equipment, net | 1271200000 | 1271200000 | 1216500000 | 1216500000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| goodwill | mapped | Goodwill | BS R4.htm | Goodwill | 1448100000 | 1448100000 | 1410100000 | 1410100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| total_assets | mapped | Assets | BS R4.htm | Total assets | 10072400000 | 10072400000 | 9423100000 | 9423100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| accounts_payable | mapped | AccountsPayableCurrent | BS R4.htm | Accounts payable | 1074200000 | 1074200000 | 1143400000 | 1143400000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | BS R4.htm | Total current liabilities | 2664400000 | 2664400000 | 2987300000 | 2987300000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| total_liabilities | not_presented |  | BS R4.htm  |  |  |  |  |  |  | FILING-CHECKED | no total liabilities line on the face |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent | BS+NOTE | Revolving credit facilities and current maturities of long-term debt + Long-term debt, less current maturities + Finance lease liabilities, current + non-current (note) | 1172200000 | 1172200000 | 1020700000 | 1020700000 | Y | FILING-CHECKED | KEY FIX 2026-11-12 (founder item 5: total_debt includes finance lease liabilities, never operating leases): no face debt line carries leases; lease note R114.htm prints finance lease liabilities current 19600000 + non-current 51700000 (= companyfacts), sitting in 'Other current liabilities' / 'Other non-current liabilities' (extensible-list cells on R114.htm): added / BS debt lines: 'Revolving credit facilities and current maturities of long-term debt' + 'Long-term debt, less current maturities'; operating leases excluded / accn 0001193125-26-054061 period ..2025-12-31 |
| stockholders_equity | mapped | StockholdersEquity | BS R4.htm | Total shareholders’ equity | 4530500000 | 4530500000 | 4152100000 | 4152100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period ..2025-12-31 |
| shares_outstanding | not_presented |  | BS/PAR  |  |  |  |  |  |  | FILING-CHECKED | no balance-sheet-date outstanding count (CommonStockSharesOutstanding) printed (BS prints issued 75,101,465, treasury 12,511,995); cover count 62,548,631 as of 2026-02-10 not used (ruling 2026-11-12) |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R8.htm | Net cash provided by operating activities | 783400000 | 783400000 | 550100000 | 550100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R8.htm | Net cash used in investing activities | -204900000 | -204900000 | -388800000 | -388800000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R8.htm | Net cash provided by (used in) financing activities | -315900000 | -315900000 | -75100000 | -75100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| capex | mapped | PaymentsToAcquirePropertyPlantAndEquipment | CF R8.htm | Additions to property, plant and equipment | -165400000 | 165400000 | -281000000 | 281000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | CF R8.htm | Depreciation and amortization | 224100000 | 224100000 | 200100000 | 200100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| amortization_of_intangibles | not_presented |  | CF/IS R2.htm,R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no amortization of intangibles line on the face |
| sbc | mapped | ShareBasedCompensation | CF R8.htm | Stock-based incentive compensation | 38000000 | 38000000 | 38100000 | 38100000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| dividends_paid | combined | PaymentsOfDividends | CF R8.htm | Dividends paid | -130400000 | 130400000 | -120000000 | 120000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Dividends paid': all dividends (may include preferred/NCI) | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | CF R8.htm | Repurchases of Common Stock | -278000000 | 278000000 | -116000000 | 116000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cf_ar_change | combined | IncreaseDecreaseInReceivables | CF R8.htm | Receivables, net | -188800000 | 188800000 | 65900000 | -65900000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | 'Receivables, net': receivables incl. non-trade | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | CF R8.htm | Inventories | -77700000 | 77700000 | -112400000 | 112400000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | CF R8.htm | Accounts payable | -28200000 | -28200000 | -77300000 | -77300000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | CF R8.htm | Cash paid for interest | 98500000 | 98500000 | 112400000 | 112400000 | Y | FILING-CHECKED | accn 0001193125-26-054061 period 2025-01-01..2025-12-31 |
| cash_paid_for_income_taxes | not_presented |  | CF R8.htm  |  |  |  |  |  |  | FILING-CHECKED | no cash paid for income taxes line on the face |

## Era checks (tag changes in the last ~5 years)
No tag change in the last 5 FY for any single-tag data point (companyfacts scan); no era 10-K needed.

## Disagreements with cloud Ritwik (exceptions file)
No cloud exceptions file covers ranks 801-900 on origin/main (checked 2026-11-12); nothing to compare.

## Mismatches (printed vs API)
none beyond sign differences

## FSN line check (printed page -> FSN tag)
39 of 39 mapped (R page, tag) pairs are on the same report in fsn.line for this accession.
