# MCK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000927653-26-000069 (CIK 0000927653, filed 2026-05-08): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001628280-15-004098 (CIK 0000927653, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000927653-18-000010 (CIK 0000927653, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000927653-19-000009 (CIK 0000927653, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- companyfacts CIK0000927653.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 403430000000 | 403430000000 | 359051000000 | 359051000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R3.htm | Cost of sales | -388880000000 | 388880000000 | -345728000000 | 345728000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 14550000000 | 14550000000 | 13323000000 | 13323000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | -8338000000 | 8338000000 | -8901000000 | 8901000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, distribution, general, and administrative expenses | -8096000000 | 8096000000 | -8507000000 | 8507000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1144 tags across all 114 R pages, face and notes) of 0000927653-26-000069; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 6212000000 | 6212000000 | 4422000000 | 4422000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -247000000 | 247000000 | -265000000 | 265000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| income_before_tax | mapped | us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Income before income taxes | 6201000000 | 6201000000 | 4359000000 | 4359000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | -1102000000 | 1102000000 | -878000000 | 878000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to McKesson Corporation | 4762000000 | 4762000000 | 3295000000 | 3295000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 38.55 | 38.55 | 25.86 | 25.86 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 38.38 | 38.38 | 25.72 | 25.72 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 123600000 | 123600000 | 127400000 | 127400000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 124100000 | 124100000 | 128100000 | 128100000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R3.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 3975000000 | 3975000000 | 5691000000 | 5691000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:ReceivablesNetCurrent | R5.htm | Receivables, net | 27985000000 | 27985000000 | 25643000000 | 25643000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Inventories, net | 24207000000 | 24207000000 | 23001000000 | 23001000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 57210000000 | 57210000000 | 55398000000 | 55398000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment, net | 2668000000 | 2668000000 | 2502000000 | 2502000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 11316000000 | 11316000000 | 10022000000 | 10022000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 82323000000 | 82323000000 | 75140000000 | 75140000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Drafts and accounts payable | 59973000000 | 59973000000 | 55330000000 | 55330000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 67017000000 | 67017000000 | 61604000000 | 61604000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R93.htm | Variable Interest Entities (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R93.htm 'Variable Interest Entities (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total McKesson Corporation stockholders’ deficit | -2172000000 | -2172000000 | -2074000000 | -2074000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R5.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 6155000000 | 6155000000 | 6085000000 | 6085000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -3432000000 | -3432000000 | -733000000 | -733000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -4631000000 | -4631000000 | -3965000000 | -3965000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Payments for property, plant, and equipment | -436000000 | 436000000 | -537000000 | 537000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R9.htm | Depreciation | 256000000 | 256000000 | 242000000 | 242000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R61.htm | Share-Based Compensation - Schedule of Components of Share-Based Compensation Expense and Related Tax Benefits (Details) |  | 247000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R61.htm 'Share-Based Compensation - Schedule of Components of Share-Based Compensation Ex' (MetaLinks.json presentation); value from companyfacts same accession |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividends paid | -381000000 | 381000000 | -345000000 | 345000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Share repurchases | -4750000000 | 4750000000 | -3146000000 | 3146000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Interest, net | 212000000 | 212000000 | 273000000 | 273000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R9.htm | Income taxes, net of refunds | 1211000000 | 1211000000 | 1124000000 | 1124000000 | Y | FILING-CHECKED | accn 0000927653-26-000069 R9.htm period ..2026-03-31 |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R5.htm | Current portion of long-term debt + Long-term debt | 6526000000 | 6526000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | CONSOLIDATED STATEMENTS OF STOCKHOLDERS’ DEFICIT |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R7.htm 'CONSOLIDATED STATEMENTS OF STOCKHOLDERS’ DEFICIT' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- gross_profit: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- income_tax_expense: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- net_income: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- basic_eps: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- diluted_eps: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- weighted_basic_shares: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001628280-15-004098 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- accounts_receivable: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- inventory: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- accounts_payable: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- current_liabilities: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- total_liabilities: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001628280-15-004098 R4.htm read; no row matched (auto)
- cfo: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- cash_flow_investing: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- cash_flow_financing: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- capex: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-15-004098 R8.htm read; no row matched (auto)
- revenue: era 10-K 0000927653-18-000010 R2.htm prints 'Revenues' on us-gaap:SalesRevenueNet = 208357000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0000927653-18-000010 R8.htm prints 'Interest' on us-gaap:InterestPaid = 298000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000927653-19-000009 R2.htm prints 'Cost of Sales' on us-gaap:CostOfRevenue = -202565000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: no R&D line on R3; MetaLinks: tags absent
- total_liabilities: not_presented  (R5.htm): 2026-11-12 R5.htm: R5 prints no total liabilities line; the machine NOTE hit (R93) is the VIE note's liabilities, not total liabilities: not_presented (the Liabilities tag appears only in the VIE note)
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AdjustmentForAmortization (R9.htm): 2026-11-12 R9.htm: R9 prints 'Depreciation' 256 and 'Amortization' 473 as two lines with no total: D&A = 729 (duration sum); the machine row carried depreciation only
- sbc: mapped us-gaap:AllocatedShareBasedCompensationExpense (R61.htm): 2026-11-12 R61.htm: R9 CF prints no share-based compensation line; R61 note prints share-based compensation expense 247 = XBRL: mapped, stmt NOTE
- total_debt: component sum us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R5.htm): 2026-11-12 R5.htm: R5 prints current portion 1,267 + long-term debt 5,259 = 6,526 = XBRL; no short-term borrowing line
- sga_expense: mapped us-gaap:SellingGeneralAndAdministrativeExpense (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'Selling, distribution, general, and administrative' is the sga_expense line, printed -8096000000 = filing XBRL 8096000000; agrees
- income_tax_expense: mapped us-gaap:IncomeTaxExpenseBenefit (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'Income tax expense' is the income_tax_expense line, printed -1102000000 = filing XBRL 1102000000; agrees
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R9.htm): 2026-11-12 R9.htm: 10% mapped sample: CF R9.htm 'Income taxes, net of refunds' is the cash_paid_for_income_taxes line, printed 1211000000 = filing XBRL 1211000000; agrees

## Loader-reject fixes 2026-11-13 (docmap-load dry run on 669f8477)
- research_and_development: unverified -> re-checked on the R page
- total_liabilities: period/accession added
- sbc: period/accession added
- total_debt: unverified -> re-checked on the R page
- shares_outstanding: period/accession added
