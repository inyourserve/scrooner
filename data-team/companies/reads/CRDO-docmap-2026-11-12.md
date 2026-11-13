# CRDO document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-043303 (CIK 0001807794, filed 2026-06-15): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001628280-23-023187 (CIK 0001807794, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001807794.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 1335116000 | 1335116000 | 436775000 | 436775000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Cost of revenue | 426767000 | 426767000 | 153866000 | 153866000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross profit | 908349000 | 908349000 | 282909000 | 282909000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 463344000 | 463344000 | 245785000 | 245785000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 183963000 | 183963000 | 98918000 | 98918000 | Y | FILING-CHECKED | accn 0001628280-26-043303 R5.htm period ..2026-05-02 / check: hand R5.htm agree |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 279381000 | 279381000 | 146867000 | 146867000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income (loss) | 445005000 | 445005000 | 37124000 | 37124000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| interest_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestExpense, InterestExpenseNonoperating, InterestExpenseOperating, InterestExpenseDebt, InterestIncomeExpenseNonoperatingNet in MetaLinks.json (739 tags across all 86 R pages, face and notes) of 0001628280-26-043303; no face row matched / check: hand R5.htm agree |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income (loss) before income taxes | 475435000 | 475435000 | 54870000 | 54870000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 3156000 | 3156000 | 2687000 | 2687000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income (loss) | 472279000 | 472279000 | 52183000 | 52183000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in US dollars per share) | 2.65 | 2.65 | 0.31 | 0.31 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in US dollars per share) | 2.51 | 2.51 | 0.29 | 0.29 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 178538000 | 178538000 | 167505000 | 167505000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 188232000 | 188232000 | 181158000 | 181158000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R5.htm period ..2026-05-02 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1164952000 | 1164952000 | 236328000 | 236328000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable | 233377000 | 233377000 | 162144000 | 162144000 | Y | FILING-CHECKED | accn 0001628280-26-043303 R3.htm period ..2026-05-02 / check: hand R3.htm agree |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories | 250831000 | 250831000 | 90029000 | 90029000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2001070000 | 2001070000 | 713534000 | 713534000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 101605000 | 101605000 | 63631000 | 63631000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 92798000 | 92798000 | 0 | 0 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 2295619000 | 2295619000 | 809257000 | 809257000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 107345000 | 107345000 | 56158000 | 56158000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 197091000 | 197091000 | 107711000 | 107711000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 232007000 | 232007000 | 127675000 | 127675000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total shareholders' equity | 2063612000 | 2063612000 | 681582000 | 681582000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R3.htm period ..2026-05-02 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 464292000 | 464292000 | 65083000 | 65083000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R8.htm period ..2026-05-02 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | -253528000 | -253528000 | 111990000 | 111990000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R8.htm period ..2026-05-02 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 717629000 | 717629000 | -7728000 | -7728000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R8.htm period ..2026-05-02 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property and equipment | -57296000 | 57296000 | -36061000 | 36061000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R8.htm period ..2026-05-02 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 34637000 | 34637000 | 21938000 | 21938000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R8.htm period ..2026-05-02 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 182638000 | 182638000 | 77355000 | 77355000 | Y | FILING-CHECKED | accn 0001628280-26-043303 R8.htm period ..2026-05-02 / check: hand R8.htm agree |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (739 tags across all 86 R pages, face and notes) of 0001628280-26-043303; no face row matched / check: hand R8.htm agree |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (739 tags across all 86 R pages, face and notes) of 0001628280-26-043303; no face row matched / check: hand R8.htm agree |
| cash_paid_for_interest | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InterestPaidNet, InterestPaid in MetaLinks.json (739 tags across all 86 R pages, face and notes) of 0001628280-26-043303; no face row matched / check: hand R8.htm agree |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes paid | 2472000 | 2472000 | 1447000 | 1447000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001628280-26-043303 R8.htm period ..2026-05-02 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (739 tags across all 86 R pages, face and notes) of 0001628280-26-043303; no face row matched / check: hand R3.htm agree |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock outstanding (in shares) | 185419000 | 185419000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-05-02; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0001628280-23-023187 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 108583000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand check (Dhairya 2026-11-12)
- Rows hand-checked against their R pages: 8 of 38 (every not_presented, combined, component and NOTE row; mapped rows the machine flagged: no API value, extension tag, label match; and a seeded random 10% of the other mapped rows). All other rows: check: machine-full-filing.
- Corrected by hand: 0.
- Random mapped sample: 3 rows, 0 disagreements (0.0%).
