# FFIV document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001048695-25-000157 (CIK 0001048695, filed 2025-11-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001048695-15-000020 (CIK 0001048695, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001048695-18-000031 (CIK 0001048695, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001048695-20-000041 (CIK 0001048695, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001048695.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net revenues | 3088072000 | 3088072000 | 2816120000 | 2816120000 | Y | FILING-CHECKED | accn 0001048695-25-000157 R5.htm period ..2025-09-30 / check: hand R5.htm agree |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of net revenues | 573978000 | 573978000 | 557647000 | 557647000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 2514094000 | 2514094000 | 2258473000 | 2258473000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total | 1748145000 | 1748145000 | 1599882000 | 1599882000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 322340000 | 322340000 | 268828000 | 268828000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 539815000 | 539815000 | 490120000 | 490120000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 765949000 | 765949000 | 658591000 | 658591000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (785 tags across all 94 R pages, face and notes) of 0001048695-25-000157; no face row matched / check: hand R5.htm agree |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 808336000 | 808336000 | 695465000 | 695465000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 115956000 | 115956000 | 128687000 | 128687000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 692380000 | 692380000 | 566778000 | 566778000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net income per share - basic (USD per share) | 11.96 | 11.96 | 9.65 | 9.65 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net income per share - diluted (USD per share) | 11.8 | 11.8 | 9.55 | 9.55 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted average shares - basic (shares) | 57904000 | 57904000 | 58720000 | 58720000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted average shares - diluted (shares) | 58684000 | 58684000 | 59359000 | 59359000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R5.htm period ..2025-09-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1344273000 | 1344273000 | 1074602000 | 1074602000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances of $2,877 and $4,585 | 414433000 | 414433000 | 389024000 | 389024000 | Y | FILING-CHECKED | accn 0001048695-25-000157 R3.htm period ..2025-09-30 / check: hand R3.htm agree |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 77229000 | 77229000 | 76378000 | 76378000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2518701000 | 2518701000 | 2109471000 | 2109471000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 156947000 | 156947000 | 150943000 | 150943000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 2443882000 | 2443882000 | 2312362000 | 2312362000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 6319492000 | 6319492000 | 5613004000 | 5613004000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 83972000 | 83972000 | 67894000 | 67894000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1612581000 | 1612581000 | 1489653000 | 1489653000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R3.htm period ..2025-09-30 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (785 tags across all 94 R pages, face and notes) of 0001048695-25-000157; no face row matched / check: hand R3.htm agree |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Total shareholders’ equity | 3591999000 | 3591999000 | 3129378000 | 3129378000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001048695-25-000157 R3.htm period ..2025-09-30 / check: hand R3.htm agree |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 949666000 | 949666000 | 792419000 | 792419000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -219491000 | -219491000 | -59214000 | -59214000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -464815000 | -464815000 | -457002000 | -457002000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Purchases of property and equipment | -43260000 | 43260000 | -30412000 | 30412000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R9.htm | Depreciation and amortization | 92399000 | 92399000 | 106991000 | 106991000 | Y | FILING-CHECKED | accn 0001048695-25-000157 R9.htm period ..2025-09-30 / check: hand R9.htm agree |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 231491000 | 231491000 | 219108000 | 219108000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| dividends_paid | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (785 tags across all 94 R pages, face and notes) of 0001048695-25-000157; no face row matched / check: hand R9.htm agree |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Payments for repurchase of common stock, including excise taxes | -502085000 | 502085000 | -500558000 | 500558000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest on long-term debt | 0 | 0 | 0 | 0 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Cash paid for taxes, net of refunds | 205717000 | 205717000 | 181635000 | 181635000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001048695-25-000157 R9.htm period ..2025-09-30 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (785 tags across all 94 R pages, face and notes) of 0001048695-25-000157; no face row matched / check: hand R3.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding | 57684000 | 57684000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-09-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Total' on us-gaap:SalesRevenueNet = 1919823000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Total' on us-gaap:CostOfGoodsAndServicesSold = 332261000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Gross profit' on us-gaap:GrossProfit = 1587562000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Total' on us-gaap:OperatingExpenses = 1034663000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001048695-15-000020 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 135540000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Research and development' on us-gaap:ResearchAndDevelopmentExpense = 296583000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 552899000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 561344000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 196330000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 365014000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Net income per share - basic (USD per share)' on us-gaap:EarningsPerShareBasic = 5.07 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Net income per share - diluted (USD per share)' on us-gaap:EarningsPerShareDiluted = 5.03 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Weighted average shares - basic (shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 71944000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001048695-15-000020 R4.htm prints 'Weighted average shares - diluted (shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 72547000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 390460000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Accounts receivable, net of allowances of $1,979 and $4,958' on us-gaap:AccountsReceivableNetCurrent = 279434000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Inventories' on us-gaap:InventoryNet = 33717000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1188140000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 95909000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 555965000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Total assets' on us-gaap:Assets = 2312290000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 50814000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 755123000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001048695-15-000020 R2.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1316728000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 684541000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Net cash (used in) provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -10699000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -556902000 (FILING-CHECKED)
- capex: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Purchases of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -60307000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 52583000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 145553000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -606858000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001048695-15-000020 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001048695-15-000020 R8.htm prints 'Cash paid for taxes' on us-gaap:IncomeTaxesPaidNet = 189235000 (FILING-CHECKED)
- revenue: era 10-K 0001048695-18-000031 R4.htm prints 'Total' on us-gaap:SalesRevenueNet = 2161407000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001048695-20-000041 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 396397000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 8 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 0.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
