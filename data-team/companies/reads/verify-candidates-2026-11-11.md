# Verifier: note-sourced and template-OUT candidates, ranks 1-50 (2026-11-11/12)

Source rows: commit 20c854b (origin/work/tag-library/ranks-1-50), data-team/47-fsn-store/company_tag_map/note_sourced_candidates_ranks_1_50.csv (104 rows in the file; 90 per coverage_full) and template_out_candidates_ranks_1_50.csv (214 rows in the file; 148 per coverage_full). Branch head has since moved to 9190dcf; these two files did not change.
Evidence: every verdict below is FILING-CHECKED. I opened the filing's R page on sec.gov (MetaLinks.json or FilingSummary.xml to find the page, then R<n>.htm; for older filings without MetaLinks I used the _pre.xml/instance). The only exception is the "no tag in filing" PASS rows: those rest on a full search of that filing's MetaLinks tag list plus the face page. Rate limit 1.1 s per request, sec.gov and data.sec.gov only, User-Agent from pipeline/.env.
How the sample was drawn: stratified and risk-weighted, not random. All 13 rows tagged "segment-total risk" were taken, plus gross profit, operating income and opex rows are oversampled. The cohort ranks 1-50 has no insurer, REIT or utility (templates are bank 3, broker_am 2, general 45), so those strata cannot be sampled. Do not read the FAIL rates as population rates.
Verdict classes: FAIL-clear = the proposal gives a wrong value or the filing contradicts it. FAIL-def = the filing prints something the proposal ignores, but the right handling is a definition call.

## Note-sourced (34 sampled)

| company | data point | class | accession / R page | verdict | reason |
|---|---|---|---|---|---|
| JPM | interest_income | bank | 0001628280-26-008131 R3, R113 | FAIL-clear | The IS face prints "Interest income" 193,341 (InterestIncomeOperating). The proposed tag InvestmentIncomeInterest is "Total investment securities" 28,032, one component in note R113. This serves a component as the total. |
| JPM | cash_and_equivalents | bank | 0001628280-26-008131 R9, R5 | FAIL-clear | Not note-only. The CF face R9 prints "Cash and due from banks and deposits with banks at the end of the period" 343,338 (CashCashEquivalentsRestricted...), and the BS prints its two parts. The face carries it. |
| JPM | amortization_of_intangibles | bank | 0001628280-26-008131 R176 | PASS | Not on the face. The note narrative gives "Amortization expense for other intangible assets" 292 (2025) and 339 (2024), consolidated. |
| WFC | sbc | bank | 0000072971-26-000133 R112, R8 | PASS | The CF face has no SBC line. Note R112 "Total stock compensation expense" 1,476 / 1,281 / 1,122. |
| GS | goodwill | broker_am | 0000886982-26-000091 R135 | PASS | Inside "Other assets" on the BS. The note gives Goodwill 5,949 / 5,853. |
| GS | ppe_net | broker_am | 0000886982-26-000091 R135 | PASS | The note gives "Property, leasehold improvements and equipment" 7,474 / 8,024. |
| GS | interest_income | broker_am | 0000886982-26-000091 R3, R182 | FAIL-clear | The face R3 prints "Interest income" 80,373 (InterestAndDividendIncomeOperating). InvestmentIncomeInterest is the "Investments" component, 7,597 in R182. Component served as total. |
| MS | amortization_of_intangibles | broker_am | 0000895421-26-000086 R105 | PASS | Note roll-forward: amortization expense 454 / 602. |
| MSFT | operating_expenses (risk) | tech | 0001193125-26-323660 R107, R2 | PASS | The face prints R&D, S&M and G&A with no total. The segment note's undimensioned total of 70,228 = 35,562+26,710+7,956, and that note's OI of 155,237 equals the face OI. The figure is consolidated because MSFT has no unallocated items. That has to be re-checked each year. |
| AMD | other_income_expense_net (risk) | tech | 0000002488-26-000191 R2 | FAIL-clear | The proposed tag NonoperatingIncomeExpense sits on the 10-Q IS face R2, "Other income (expense), net" (902) / 82 / (139) / 219. It is a face line, not a note. |
| CAT | gross_profit (risk) | industrial | 0000018230-21-000063 R126 | FAIL-def | The quarterly note's "Gross margin" 2,786 = Sales of ME&T 10,570 - COGS 7,784. It excludes Financial Products revenue (665). Total sales and revenues 11,235 - COGS would give 3,451. Narrower basis than revenue - COR, quarterly only, FY2015-2020. |
| GE | gross_profit (risk) | industrial | 0000040545-17-000010 R164, R2 | FAIL-clear (sub-entity total) | The quarterly "Gross profit from sales" is on the "GE" (industrial, excluding GE Capital) basis. Its quarterly sales sum to 110,836, which matches the GE column 75,580+35,255, not the consolidated 75,414+34,976 = 110,390. A sub-entity total served as consolidated. |
| LLY | operating_expenses (risk) | pharma | 0000059478-19-000082 R99, R2 | PASS | The quarterly note's "Operating expenses" sum to 11,938.9 = R&D 5,307.1 + MSA 6,631.8 (consolidated face lines). Caveats: LLY's own definition excludes acquired IPR&D and special charges, and only 3-month values exist (to FY2020). |
| TMO | gross_profit (risk) | industrial | 0000097745-20-000009 R96, R4 | PASS | No GP on the face. The quarterly note gives consolidated GP (3,035 for Q4 2019). Quarterly only, to FY2020. |
| RTX | gross_profit (risk) | industrial | 0000101829-21-000008 R127, R2 | PASS | No GP on the face. Quarterly note "Gross margin" 2,153 on Q4 2020 sales of 16,419, consolidated. Quarterly only. |
| JNJ | operating_income (risk) | pharma | 0000200406-15-000019 R42 | FAIL-clear (SEGMENT TOTAL) | The only fact is "Total Segment Operating Income" 5,827. JNJ then deducts 252 of "expense not allocated to segments" to reach pre-tax 5,575. JNJ prints no consolidated OI. |
| AMGN | gross_profit (risk) | pharma | 0000318154-21-000010 R119 | FAIL-def | The note says "Gross profit from product sales": product sales minus cost of sales, excluding Other revenues. Narrower than total revenue - COR, quarterly only. |
| COST | gross_profit (risk) | consumer | 0000909832-19-000019 _pre.xml role SummaryOfSignificantAccountingPolicies + instance | FAIL-def | One annual fact, 16,465 in FY2019, from the ASC 606 transition table. It is net sales minus merchandise costs and excludes membership fees. One period only, and on a different basis. |
| ABBV | gross_profit (risk) | pharma | 0001551152-26-000008 R104, R3 | PASS | No GP on the face. The fourth-quarter note gives consolidated Q4 gross margin 12,066. Only the Q4 3-month value exists. |
| NFLX | gross_profit (risk) | tech | 0001065280-21-000040 R65, R2 | PASS | No GP on the face. Quarterly note GP is consolidated (Q4 2020 2,479,282K). Quarterly only, to FY2020. |
| ORCL | gross_profit (risk) | tech | 0001193125-18-201034 R81, R82 | FAIL-clear (SEGMENT TOTAL) | GrossProfit is "Total margin for operating segments" 24,287. The footnote says it covers "only the direct controllable costs" and excludes product development and G&A. It is also tagged without a dimension, so a plain tag pick takes it. |
| CAT | stockholders_equity | industrial | 0000018230-26-000008 R5, R113 | FAIL-clear | Not note-sourced. The BS face prints "Total shareholders' equity" 21,318 (incl. NCI, NCI 0). The "note" (AOCI roll-forward R113) repeats the same incl.-NCI total. Parent equity is not tagged anywhere in the filing. |
| PG | stockholders_equity | consumer | 0000080424-26-000103 R6, R91 | FAIL-clear | Same pattern. The face prints TOTAL SHAREHOLDERS' EQUITY 54,311, which includes NCI 230. The note R91 repeats 54,311. Used as parent equity it is wrong by 230. |
| PG | research_and_development | consumer | 0000080424-26-000103 R43 | PASS | Accounting-policy note: R&D costs $2.1B / 2.1 / 2.0 (reported in billions, 1 decimal). |
| CVX | research_and_development | energy | 0000093410-26-000078 R126 | PASS | "Other financial information" note: R&D 427 / 353 / 320. |
| CVX | share_buybacks | energy | 0000093410-26-000078 R7, R66 | PASS | The face prints only the net "Net sales (purchases) of treasury shares" (11,855). Note R66 gives gross "Shares purchased under share repurchase and deferred compensation plans" 12,079. Caveat: the perimeter includes deferred-comp purchases. |
| KO | cf_ar_change | consumer | 0001628280-26-010047 R126, R7 | PASS | The CF face prints only "Net change in operating assets and liabilities". Note R126 gives the trade AR change, 334. |
| AMAT | accounts_payable | tech | 0001628280-25-056742 R5, R59 | PASS | The face prints only "Accounts payable and accrued expenses". Note R59 gives AP 1,978 / 1,570. |
| UNH | inventory | health | 0000731766-26-000062 R46 | PASS | Policy narrative: Inventory, net 3,300 / 3,800 (rounded to 100M). |
| CSCO | depreciation_and_amortization | tech | 0000858877-26-000132 R53, R8; 10-K text | FAIL-clear | The note's $700M is "Depreciation and amortization expenses for property and equipment" (rounded, PP&E only). The CF face prints "Depreciation, amortization, and other" 2,540. Component served as total. |
| MRK | interest_income | pharma | 0000310158-26-000063 R105 | PASS | Other (income) expense note: interest income 343 / 415 / 365 (shown as negative inside an expense table). |
| GOOG | interest_expense | tech | 0001652044-26-000018 R74 | PASS | Other income note: interest expense 736 / 268 / 308. |
| SHOP | accounts_receivable | tech | 0001594805-26-000007 R3, R70 | FAIL-clear | The BS face prints "Trade and other receivables, net" 500 (AccountsAndOtherReceivablesNetCurrent, which is not in the concept's tag set). The note repeats 500. It is on the face, and as a combined trade-and-other line. |
| META | interest_expense | tech | 0001628280-26-003942 R80 | PASS | Note: interest expense 1,165 / 715 / 446. |

Note-sourced: 34 sampled, 20 PASS, 14 FAIL (11 clear, 3 definition). Segment or sub-entity total served as consolidated: ORCL GP, JNJ OI, GE GP.

## Template-OUT (63 sampled)

| company | data point | class | accession / R page | verdict | reason |
|---|---|---|---|---|---|
| JPM | current_assets | bank | 0001628280-26-008131 R5 | PASS | Unclassified BS. No AssetsCurrent in the filing. |
| JPM | other_income_expense_net | bank | 0001628280-26-008131 R3 | PASS | No non-operating section. "Other income" is a noninterest revenue line (NoninterestIncomeOther). |
| BAC | interest_income | bank | 0000070858-26-000157 R3 | FAIL-clear | The face prints "Interest income" 138,566 (InterestAndDividendIncomeOperating). The bank template has interest income IN. It went OUT only because the tag set is InvestmentIncomeInterest alone. |
| BAC | sga_expense | bank | 0000070858-26-000157 R3 | PASS | Noninterest expense lines only, no SG&A. |
| WFC | interest_income | bank | 0000072971-26-000133 R3 | FAIL-clear | The face prints "Total interest income" 87,314. |
| WFC | current_liabilities | bank | 0000072971-26-000133 R5 | PASS | Unclassified BS. |
| GS | operating_expenses | broker_am | 0000886982-26-000091 R3 | FAIL-clear | The face prints "Total operating expenses" 37,544 (NoninterestExpense). Broker template: opex IN COND. |
| GS | operating_income | broker_am | 0000886982-26-000091 R3 | PASS | Only pre-tax earnings. No OI. |
| GS | cost_of_revenue | broker_am | 0000886982-26-000091 R3 | PASS | No COR line. |
| MS | interest_income | broker_am | 0000895421-26-000086 R3 | FAIL-clear | The face prints "Interest income" 59,063. |
| MS | share_buybacks | broker_am | 0000895421-26-000086 R8, R150 | FAIL-clear | The CF face prints "Repurchases of common stock and employee tax withholdings" (5,835) (custom tag, combined). Equity note R150 gives program repurchases of 4,585. |
| MS | capex | broker_am | 0000895421-26-000086 R8 | FAIL-clear | The CF face prints "Other assets—Premises, equipment and software" (2,898) (PaymentsForProceedsFromProductiveAssets, net). |
| AAPL | interest_income | tech | 0000320193-23-000106 R53; 0000320193-26-000026 R3 | FAIL-clear (period) | "Interest and dividend income" (InvestmentIncomeInterestAndDividend) is printed in the note FY2015 to FY2023 (3,750 in FY2023). Absent only from FY2024 on. |
| MSFT | interest_income | tech | 0001193125-26-323660 R48 | FAIL-clear | The note prints "Interest and dividends income" 3,301 (InvestmentIncomeNet). That is a combined line, not absent. |
| MSFT | depreciation_and_amortization | tech | 0001193125-26-323660 R6, R62 | FAIL-clear | The CF face prints "Depreciation, amortization, and other" (custom, combined), and the note R62 prints depreciation expense. Under template s5 a combined line is IN, not OUT. |
| GOOG | gross_profit | tech | 0001652044-26-000018 R5 | PASS | No GP line. |
| GOOG | operating_expenses | tech | 0001652044-26-000018 R5, R90 | PASS | Only "Total costs and expenses" (includes COR). The OperatingExpenses tag appears only in R90 as segment "Other costs and expenses". |
| GOOG | interest_income | tech | 0001652044-26-000018 R74 | FAIL-clear | The note prints "Interest income" 4,337 / 4,482 / 3,865 (InterestIncomeOther). |
| GOOG | depreciation_and_amortization | tech | 0001652044-26-000018 R10 | FAIL-def | The CF face prints "Depreciation of property and equipment" 21,136. There is no D&A total. D&A is always-IN, and OUT hides a printed component. |
| AMD | dividends_paid | tech | 0000002488-26-000018 (MetaLinks search) | PASS | No dividend tags. Non-payer. |
| META | gross_profit | tech | 0001628280-26-003942 R5 | PASS | No GP line. |
| ORCL | operating_expenses | tech | 0001193125-26-277521 R4 | FAIL-def (reason) | The face prints a line labelled "Total operating expenses" 46,751 (CostsAndExpenses, all costs). Blank is right under the tag-card rule, but the reason "not presented" is false. It should carry the total_costs_incl_cost_of_revenue point reason. |
| TXN | operating_expenses | tech | 0000097476-26-000059 R3 | PASS | R&D, SG&A and restructuring are printed. No total. |
| TXN | other_income_expense_net | tech | 0000097476-26-000059 R3 | FAIL-clear | The face prints "Other income (expense), net (OI&E)" 230 (OtherNonoperatingIncomeExpense). |
| TSLA | other_income_expense_net | tech | 0001628280-26-003952 R5 | FAIL-clear | The face prints "Other (expense) income, net" (419) (OtherNonoperatingIncomeExpense). |
| TSLA | share_buybacks | tech | 0001628280-26-003952 CF + MetaLinks | PASS | No repurchase line or tag. |
| NFLX | goodwill | tech | 0001065280-26-000034 (MetaLinks search) | PASS | No Goodwill tag in the filing. |
| CRWD | inventory | tech | 0001535527-26-000010 (MetaLinks search) | PASS | No inventory tag. |
| V | gross_profit | tech/payments | 0001403161-26-000134 R5 | PASS | Opex lines only. |
| MA | gross_profit | tech/payments | 0001141391-26-000013 R3 | PASS | Opex lines only. |
| CAT | interest_income | industrial | 0000018230-26-000008 R71 | FAIL-clear | The note prints "Investment and interest income" 416 (InvestmentIncomeNet). Combined, not absent. |
| CAT | other_income_expense_net | industrial | 0000018230-26-000008 R3, R71 | FAIL-clear | The face prints "Other income (expense)" 892 (OtherNonoperatingIncomeExpense). |
| GE | operating_income | industrial | 0000040545-26-000008 R3 | PASS | No OI line. |
| GE | operating_expenses | industrial | 0000040545-26-000008 R3 | PASS | Only "Total costs and expenses" (incl. cost of sales). |
| LIN | gross_profit | industrial | 0001628280-26-011430 R3 | PASS | No GP. Cost of sales is shown excl. D&A. |
| KO | other_income_expense_net | consumer | 0001628280-26-010047 R3 | FAIL-clear | The face prints "Other income (loss) — net" 1,073 (OtherNonoperatingIncomeExpense). |
| KO | operating_expenses | consumer | 0001628280-26-010047 R3 | PASS | SG&A and other operating charges only. |
| KO | research_and_development | consumer | 0001628280-26-010047 (MetaLinks search) | PASS | No R&D tag. |
| KO | cf_ap_change | consumer | 0001628280-26-010047 R126 | FAIL-clear | Note R126 prints "Increase (decrease) in accounts payable and accrued expenses" (IncreaseDecreaseInAccountsPayableAndAccruedLiabilities). That is a combined line, so it is not absent. |
| PG | gross_profit | consumer | 0000080424-26-000103 R3 | PASS | No GP line. |
| PG | operating_expenses | consumer | 0000080424-26-000103 R3 | PASS | SG&A only. |
| WMT | gross_profit | consumer | 0000104169-26-000055 R3 | PASS | No GP line. |
| WMT | interest_expense | consumer | 0000104169-26-000055 R3 | FAIL-def | The face prints interest expense as "Debt" 2,318 (InterestExpenseDebt) plus "Finance lease" 481. There is no total line. Interest expense is template IN, and OUT hides printed lines. |
| HD | cf_inventory_change | consumer | 0001628280-26-019436 R8 | FAIL-clear | The CF face prints "Changes in merchandise inventories" (1,498) (IncreaseDecreaseInRetailRelatedInventories). |
| AMZN | gross_profit | consumer | 0001018724-26-000004 R4 | PASS | No GP line. |
| PM | operating_expenses | consumer | 0001628280-26-005939 R3 | PASS (caveat) | No total opex line. "Marketing, administration and research costs" 12,349 is a combined SG&A+R&D line. |
| LLY | gross_profit | pharma | 0000059478-26-000013 R3 | PASS | No GP line. |
| LLY | operating_income | pharma | 0000059478-26-000013 R3 | PASS | No OI line. |
| LLY | cf_ar_change | pharma | 0000059478-26-000013 CF face | FAIL-clear | The CF face prints "Receivables—(increase) decrease" (7,000) (IncreaseDecreaseInAccountsAndOtherReceivables). |
| MRK | gross_profit | pharma | 0000310158-26-000063 R3 | PASS | No GP line. |
| MRK | operating_income | pharma | 0000310158-26-000063 R3 | PASS | No OI line. |
| AMGN | operating_expenses | pharma | 0000318154-26-000010 R3 | FAIL-def (reason) | The face prints "Total operating expenses" 27,671 (CostsAndExpenses, includes cost of sales). Blank is right, but the reason "not presented" is false. Same fix as ORCL. |
| UNH | gross_profit | health | 0000731766-26-000062 R5 | PASS | No GP line. |
| CVX | gross_profit | energy | 0000093410-26-000078 R3 | PASS | No GP line. |
| CVX | operating_income | energy | 0000093410-26-000078 R3 | PASS | No OI line. |
| CVX | interest_expense | energy | 0000093410-26-000078 R3 | FAIL-clear | The face prints "Interest and debt expense" 1,217 (InterestExpenseDebt, not in the tag set). |
| CVX | sbc | energy | 0000093410-26-000078 R110 | FAIL-clear | The note prints stock option compensation expense 73 and SAR/RS/PSU/RSU compensation expense 399 (2025). |
| XOM | gross_profit | energy | 0000034088-26-000045 R3 | PASS | No GP line. |
| XOM | operating_income | energy | 0000034088-26-000045 R3 | PASS | No OI line. |
| XOM | inventory | energy | 0000034088-26-000045 R5 | FAIL-clear | The BS prints Inventories: crude oil, products and merchandise 22,979 plus materials and supplies 3,323. |
| XOM | cf_ar_change | energy | 0000034088-26-000045 R7 | FAIL-clear | The CF face prints "Notes and accounts receivable reduction/(increase)" (3,042). |
| XOM | sbc | energy | 0000034088-26-000045 R110 | FAIL-clear | "Compensation cost charged against income" $1.0B (2025). |
| XOM | research_and_development | energy | 0000034088-26-000045 R94 | FAIL-clear | "Research and development expense" $1.2B (2025). |

Template-OUT: 63 sampled, 35 PASS, 28 FAIL (24 clear, 4 definition or reason).

## Root causes seen (each covers many unsampled rows)
1. The concept tag sets are too narrow, so "no companyfacts fact" is false evidence. interest_income = InvestmentIncomeInterest only, which misses bank totals (InterestAndDividendIncomeOperating/InterestIncomeOperating), InterestIncomeOther, InvestmentIncomeNet and InvestmentIncomeInterestAndDividend. other_income_expense_net misses OtherNonoperatingIncomeExpense (the tag card maps it). interest_expense misses InterestExpenseDebt as a face line. cf_ar_change misses IncreaseDecreaseInAccountsAndOtherReceivables/AccountsAndNotesReceivable. cf_inventory_change misses IncreaseDecreaseInRetailRelatedInventories.
2. XOM is mapped to CIK 0002115436 (ExxonMobil Holdings Corp, 10-Qs only from 2026). All history is under CIK 0000034088, so all 13 XOM OUT rows rest on an empty companyfacts set.
3. Combined lines (MSFT D&A, MSFT/CAT interest income, KO/HD AP changes, SHOP AR, MS buybacks) are proposed OUT. Template s5 says combined lines are IN under the company label.
4. The note-sourced class has no "face check": the value is often on a face statement under another tag (JPM cash, AMD, SHOP, CAT/PG equity). It also has no "component check": a note tag can be a component of the face total (JPM/GS interest income, CSCO D&A). And it has no "segment/sub-entity check" (ORCL, JNJ, GE).
