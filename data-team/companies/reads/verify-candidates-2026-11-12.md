# Verifier: note-sourced and template-OUT candidates, ranks 1-50 (re-draw 2026-11-12)

Source: origin/work/tag-library/verifier-fixes-2026-11-12 @ addef9fe, data-team/47-fsn-store/company_tag_map/note_sourced_candidates_ranks_1_50.csv (83 rows) and template_out_candidates_ranks_1_50.csv (145 rows).
Draw: simple random sample without replacement. Python `random.Random(20261112)`. Seed **20261112**. `rng.sample(range(83), 40)` then `rng.sample(range(145), 50)` (row index = 0-based data-row order in each CSV). Script: scratchpad/v12/draw.py, result scratchpad/v12/draw.json.
Evidence: FILING-CHECKED. Each verdict opened the filing on sec.gov (MetaLinks.json for the tag-to-R-page map, then R<n>.htm, or the primary document text). Requests went to sec.gov and data.sec.gov only, at most 1 per 1.05 s, with the UA from pipeline/.env. data.sec.gov companyconcept (undimensioned facts) was used only to find which filings and periods carry a tag. Those period lists are DATA-INFERRED, and each FAIL below also cites an opened filing.
Scope of absence checks (template-OUT): the latest 10-K's full MetaLinks tag list plus its face R pages. Older 10-Ks were added where an era change was plausible (GE FY2018, LLY FY2019, CVX FY2020, V FY2015/FY2018, MA FY2019). Not every filing since 2015 was opened.
Verdicts: FAIL-clear = the filing contradicts the row and a wrong value or a wrong blank would be shown. FAIL-def = the filing prints a combined line or components the row ignores, and the right handling needs a definition call. FAIL-class (note-sourced only) = the value is right but the face carries it, so it is not note-only.

## Note-sourced (40 drawn)

| company | data point | class | accession / R page | verdict | reason |
|---|---|---|---|---|---|
| AAPL | amortization_of_intangibles | general | 0000320193-26-000026 R50, R8 | PASS | Not on the face (the CF prints D&A only). Note: "Amortization expense related to intangible assets" $4.9B / 3.7 / 3.6 (rounded to $0.1B). |
| AAPL | interest_income | general | 0000320193-23-000106 R53, R3 | PASS | The face prints only "Other income/(expense), net". Note: "Interest and dividend income" 3,750 / 2,825 / 2,843, consolidated (a combined line shown as the company line). |
| MSFT | interest_expense | general | 0001193125-26-323660 R48, R90, R2 | PASS (caveat) | Note R48: "Interest expense" (3,051). The tag set also holds FinanceLeaseInterestExpense (R90, "Interest on lease liabilities" 2,547, a component). Companyconcept shows no period that has only the component, so no component value would be served. |
| GOOG | interest_expense | general | 0001652044-26-000018 R74 | PASS | Note: "Interest expense" (736) / (268) / (308). The face prints only OI&E net. No component-only period. |
| GOOG | interest_income | general | 0001652044-26-000018 R74 | PASS | Note: "Interest income" 4,337 / 4,482 / 3,865. |
| KO | cf_ar_change | general | 0001628280-26-010047 R126, R7 | PASS | The CF face prints only "Net change in operating assets and liabilities". Note R126: "(Increase) decrease in trade accounts receivable" 334 / (295) / (2). |
| GE | interest_expense | industrial | 0000040545-21-000064 R95, R2; 0000040545-26-000008 R3 | FAIL-clear | The face prints "Interest and other financial charges" (custom tag ge_InterestAndOtherFinancialCharges) in every year, e.g. 843 in FY2025. The only note fact (2 periods) is from the ASC 815 hedge table R95, "Interest expense" 9M 2021 = 2,866 against the face's 1,450. The note figure includes 1,416 of debt extinguishment costs: different basis, and the face carries the line. |
| GE | interest_income | industrial | 0000040545-26-000008 R128 + footnote (a) | FAIL-clear (COMPONENT) | InvestmentIncomeInterest 144 / 132 / 127 is "interest income associated with customer advances", which footnote (a) says is included in "Other net interest and investment income" 946 / 813 / 637. A component is served as the total. |
| INTC | interest_income | tech | 0000050863-26-000011 R68, R3 | PASS | Note: "Interest income" 1,007 / 1,245 / 1,335. The face prints "Interest and other, net". |
| LLY | interest_expense | pharma | 0000059478-25-000067 R105; 0000059478-26-000013 R75 | PASS | Note: "Interest expense" 780.6 (FY2024), and in FY2025 "Interest expense on borrowings" 895. Not on the face. |
| LLY | interest_income | pharma | 0000059478-25-000067 R105 | PASS | Note: "Interest income" 175.2 / 173.6 / 62.8. |
| WFC | sbc | bank | 0000072971-26-000133 R112, R7 | FAIL-class | The equity statement (a face statement) prints "Stock-based compensation" 1,476 / 1,281 / 1,122 in the APIC column, equal to note R112 "Total stock compensation expense". Under the CAT equity-statement ruling the face carries it, so it is not note-only. The value is the same. (This reverses yesterday's PASS, which checked only the CF.) |
| PG | research_and_development | consumer | 0000080424-26-000103 R43; doc text | PASS | Policy note: R&D costs "$2.1 billion in 2026, $2.0 billion ..." (inside SG&A, consolidated, rounded to $0.1B). |
| CVX | research_and_development | energy | 0000093410-26-000078 R126 | PASS | "Research and development expenses" 427 / 353 / 320. Not on the face. |
| RTX | amortization_of_intangibles | industrial | 0000101829-26-000006 R59, R7 | PASS | Note: $2.1B / 2.2 / 2.1 (rounded). The CF prints D&A only. |
| JNJ | amortization_of_intangibles | pharma | 0000200406-26-000016 R65, R10 | PASS | Note: $4.6B / 4.5 / 4.5 (rounded). The CF prints combined D&A only. |
| MRK | interest_expense | pharma | 0000310158-26-000063 R105, R3 | PASS | Other (income) expense note: "Interest expense". The face prints only "Other (income) expense, net". |
| MRK | interest_income | pharma | 0000310158-26-000063 R105 | PASS | Same note: "Interest income". |
| LRCX | interest_income | tech | 0000707549-26-000037 R56, R3 | PASS | OI&E note: "Interest income". The face prints only "Other income (expense), net". |
| MU | amortization_of_intangibles | tech | 0000723125-25-000028 R75, R8 | PASS | Intangibles note: 71 / 82 / 86. The CF prints combined "Depreciation expense and amortization of intangible assets". |
| CSCO | depreciation_and_amortization | tech | 0000858877-26-000132 R53, R8 | FAIL-clear (COMPONENT) | Unchanged from 2026-11-11. DepreciationDepletionAndAmortization is the policy-note "Depreciation and amortization expenses" for property and equipment, $0.7B (PP&E only, rounded). The CF face prints combined "Depreciation, amortization, and other" 2,540 / 2,811 / 2,507 (csco_DepreciationAmortizationAndOther), which is the company line. |
| GS | goodwill | broker_am | 0000886982-26-000091 R135, R5 | PASS | Inside "Other assets" on the BS. Note: Goodwill 5,949 / 5,853. |
| GS | ppe_net | broker_am | 0000886982-26-000091 R135 | PASS | Note: "Property, leasehold improvements and equipment" 7,474 / 8,024. |
| MS | amortization_of_intangibles | broker_am | 0000895421-26-000086 R105 | PASS | Note: "Amortization expense". Not on the face. |
| AMZN | amortization_of_intangibles | tech | 0001018724-26-000004 R64, R3 | PASS | Note: "Amortization expense for acquired intangibles". The CF prints combined D&A. |
| DELL | interest_expense | tech | 0001571996-26-000046 R65 + text line 726; 0001571996-26-000008 R132 | FAIL-clear (COMPONENT) | Annual and most quarterly periods use the note's "Interest expense" (InterestExpenseNonoperating, 1,560 in FY2026). For the Q2 FY27 periods (2026-05-02..07-31 and 6M) the only fact is InterestExpenseDebt, "Total interest expense related to the Company's outstanding debt ... $0.4 billion": a debt-only component, rounded to $0.1B. |
| SHOP | amortization_of_intangibles | tech | 0001594805-26-000007 R85, R7 | PASS | Note: "Amortization expense" 13 / 14 / 38 (undimensioned total). Not on the face. |
| SHOP | sbc | tech | 0001594805-26-000007 R7, R6, R102 | FAIL-class | The CF face prints "Stock-based compensation" 449 / 430 / 615 under StockOptionPlanExpense, which is not in the sbc tag set. The equity statement also prints it. The note value (449) is equal. |
| ANET | amortization_of_intangibles | tech | 0001596532-25-000216 R41; 0001596532-26-000013 R41 | FAIL-clear (FILER MISTAG) | In the Q2 and Q3 2025 10-Qs ANET tags ACCUMULATED amortization (a balance) with AmortizationOfIntangibleAssets as durations: "Accumulated Amortization" (170.5) for 6M 2025 and (159.9) for "12 months" 2024. The FY2025 10-K gives FY2024 amortization expense as 26.8. Serving the tag gives wrong values (186.2 for 9M 2025). |
| GEV | sbc | industrial | 0001996810-26-000015 R8, R115 | FAIL-class | The equity statement prints "Share-based compensation expense" 257 / 155, equal to note R115. The face carries it. |
| LIN | amortization_of_intangibles | industrial | 0001628280-26-011430 R75, R3 | PASS | Note: 517 / 554 / 550. The face prints combined D&A 3,763. |
| TSLA | amortization_of_intangibles | auto | 0001564590-21-004599 R67 + text | PASS | "Amortization expense ... $51 million, $44 million and $66 million". The CF prints combined DA&I. |
| PLTR | amortization_of_intangibles | tech | 0001321655-25-000022 R76 + text | PASS | "Amortization expense of intangible assets was $7.8 million and $9.6 million". |
| META | interest_expense | tech | 0001628280-26-003942 R80, R68; 0001628280-26-050705 R47 + MD&A line 894 | FAIL-clear (COMPONENT) | The annual total "Interest expense" (1,165, R80) is fine. Quarterly periods carry only components: InterestExpenseDebt "recognized on debt" (Q2 2026: 754, against the MD&A total of 783; FY2025: 1,090 against 1,165) and, for 2019-2022 quarters, FinanceLeaseInterestExpense only (DATA-INFERRED period list). |
| META | interest_income | tech | 0001628280-26-003942 R80 | PASS | "Interest income" 2,123 / 2,517 / 1,639. The face prints "Interest and other income, net". |
| AVGO | interest_income | tech | 0001730168-25-000121 R63, R5 | PASS | Note: "Interest income" 347 / 461 / 535. The face prints "Other income, net". |
| XOM | research_and_development | energy | 0000034088-26-000045 R94 | PASS | "Research and development expense" $1.2B / 1.0 / 0.9 (CIK 34088). Note: FY2025 restates prior years at $0.1B rounding (earlier 10-Ks gave 987 / 879). |
| V | amortization_of_intangibles | payments | 0001403161-26-000134 R72, R5 | PASS | Note: 105 / 78 / 79. The face prints combined D&A. |
| PM | interest_income | consumer | 0001628280-26-005939 R105, R3 | PASS | "Interest expense, net" note: "Interest income" (621) / (620) / (465). The face prints only net interest. |
| PM | sbc | consumer | 0001413329-22-000114 R49; 0001628280-26-005939 R76 | FAIL-clear (COMPONENT) | The undimensioned AllocatedShareBasedCompensationExpense facts (2022-2023 10-Qs) are "Compensation Expense Related to PSU Awards" (Q3 2022 13, 9M 44). RSU expense is a separate table, and PM prints no SBC total. A component is served as the total. |

Note-sourced: 40 drawn, 30 PASS, 10 FAIL (7 clear value errors: GE x2, CSCO, DELL, ANET, META, PM; 3 FAIL-class with the right value: WFC, SHOP, GEV). 5 of the 7 value errors are components served as totals (GE ii, CSCO, DELL, META, PM sbc).

## Template-OUT (50 drawn)

| company | data point | class | accession / R page | verdict | reason |
|---|---|---|---|---|---|
| JPM | accounts_receivable | bank | 0001628280-26-008131 R5, R9 | FAIL-def | The BS face prints combined "Accrued interest and accounts receivable" 111,599 (jpm_), and the CF prints its change. A combined line exists; the bank AR perimeter needs a ruling. |
| MSFT | interest_income | tech | 0001193125-26-323660 R48 | FAIL-clear | Unchanged from 2026-11-11. The note prints "Interest and dividends income" 3,301 / 2,647 / 3,157 (InvestmentIncomeNet, not in the 6-tag set). |
| CAT | gross_profit | industrial | 0000018230-26-000008 R3 | PASS | The face prints sales and COGS but no GP line. The quarterly "gross margin" note is narrower (ruling: not presented). |
| GE | gross_profit | industrial | 0000040545-26-000008 R3; 0000040545-19-000014 R2 | PASS | No GP line in FY2025 or FY2018. |
| GE | operating_income | industrial | same | PASS | No OI line in either era (segment profit only). |
| LLY | operating_expenses | pharma | 0000059478-26-000013 R3; 0000059478-20-000057 R2 | PASS | The only total is "Costs, expenses, and other", which includes cost of sales and other-net. |
| LLY | operating_income | pharma | same | PASS | No OI line in either era. |
| BAC | accounts_receivable | bank | 0000070858-26-000157 R5 | FAIL-def | The BS face prints "Customer and other receivables" 98,186 (OtherReceivables), a combined line. |
| BAC | current_assets | bank | 0000070858-26-000157 R5 + tag list | PASS | Unclassified BS. No AssetsCurrent. |
| BAC | sga_expense | bank | 0000070858-26-000157 R3 | PASS | Noninterest expense lines only. |
| CVX | cf_ap_change | energy | 0000093410-26-000078 R66 | FAIL-clear | The note prints "Increase (decrease) in accounts payable and accrued liabilities" (IncreaseDecreaseInAccountsPayableAndAccruedLiabilities), a combined line. |
| CVX | cf_ar_change | energy | 0000093410-26-000078 R66 | FAIL-clear | The note prints "Decrease (increase) in accounts and notes receivable" (IncreaseDecreaseInAccountsAndNotesReceivable), a combined line. The same tag is mapped "combined" for XOM. |
| CVX | interest_income | energy | 0000093410-26-000078 R89 + text lines 2518/2552/2580; 0000093410-20-000010 text line 2297 | FAIL-def | The segment-earnings reconciliation prints "Interest income" 52 / 181 / 137 (FY2020/19/18), and FY2025 prints "interest income of $257 in All Other". Segments exclude investment interest income, so this is the company's investment interest income. It is tagged under a segment dimension. |
| CVX | sbc | energy | 0000093410-26-000078 R110 + text line 3035 | FAIL-def (reason) | Unchanged from 2026-11-11. SBC is printed in two components, stock options 73 and SARs/RS/PSU/RSU 399, with no total. The reason "no fact" is false: the note prints both components but no total. (The R112 AllocatedShareBasedCompensationExpense 323 is ESIP savings-plan expense, not SBC.) |
| WMT | operating_expenses | consumer | 0000104169-26-000055 R3 | PASS (def note) | No "total operating expenses" line. The sole opex line is "Operating, selling, general and administrative expenses" 147,943, served as SG&A. |
| HD | cf_inventory_change | consumer | 0001628280-26-019436 MetaLinks R8* | FAIL-clear | Unchanged from 2026-11-11. The CF face prints "Changes in merchandise inventories" (IncreaseDecreaseInRetailRelatedInventories). |
| MU | interest_income | tech | 0000723125-26-000023 R3* (MetaLinks) | FAIL-clear | The IS face prints "Interest income" (InvestmentIncomeNet, label "Interest income"). |
| UNH | cf_inventory_change | health | 0000731766-26-000062 tag list | PASS | No inventory-change line on the CF. Inventory moves are not split out. |
| UNH | other_income_expense_net | health | 0000731766-26-000062 R5 | PASS | Below OI only interest expense and a loss on sale of subsidiaries. |
| GS | accounts_payable | broker_am | 0000886982-26-000091 R5 | FAIL-def | The BS face prints combined "Customer and other payables" 231,865 (gs_). |
| GS | cf_ap_change | broker_am | 0000886982-26-000091 R8 | FAIL-def | The CF prints "Customer and other receivables and payables, net" (43,206). It is one netted line spanning AR and AP changes. |
| GS | cf_ar_change | broker_am | same | FAIL-def | Same line. |
| GS | other_income_expense_net | broker_am | 0000886982-26-000091 R3 | PASS | No non-operating section. |
| GS | sga_expense | broker_am | 0000886982-26-000091 R3 | PASS | No SG&A line. |
| MS | capex | broker_am | 0000895421-26-000086 R8 | FAIL-clear | Unchanged from 2026-11-11. The CF face prints "Other assets—Premises, equipment and software" (2,898) / (3,462) / (3,412) (PaymentsForProceedsFromProductiveAssets). |
| MS | cost_of_revenue | broker_am | 0000895421-26-000086 R3 | PASS | No COR line. |
| MS | other_income_expense_net | broker_am | same | PASS | "Other" is a revenue line. No non-operating section. |
| COST | operating_expenses | consumer | 0000909832-26-000093 R3 | PASS (def note) | "OPERATING EXPENSES" heading with merchandise costs and SG&A. No total line. |
| COST | research_and_development | consumer | 0000909832-26-000093 text line 1138 | PASS | Only an R&D tax-credit line in the rate reconciliation. No R&D expense. |
| AMZN | gross_profit | tech | 0001018724-26-000004 R4 | PASS | No GP line. |
| CRWD | cf_inventory_change | tech | 0001535527-26-000010 tag list | PASS | No inventory tags. |
| CRWD | dividends_paid | tech | same, text line 757 | PASS | "never declared or paid any cash dividends". |
| ABBV | gross_profit | pharma | 0001551152-26-000008 R3 | PASS | No GP line. |
| NFLX | operating_expenses | media | 0001065280-26-000034 R3 | PASS | No total opex line. |
| SHOP | dividends_paid | tech | 0001594805-26-000007 text line 609 | PASS | "never declared or paid any dividends". |
| ANET | dividends_paid | tech | 0001596532-26-000013 text line 726 | PASS | Same. |
| MA | research_and_development | payments | 0001141391-26-000013, 0001141391-20-000032 | PASS | No R&D tag or text in FY2025 or FY2019. |
| GEV | ppe_net | industrial | 0001996810-26-000015 R4, R67 | FAIL-clear | The BS face prints "Property, plant, and equipment – net (Note 6)" 6,006 / 5,150 (custom tag; includes operating-lease ROU), and the note prints net carrying value by class. It is printed. |
| LIN | operating_expenses | industrial | 0001628280-26-011430 R3 | PASS | No total opex line. |
| TSLA | dividends_paid | auto | 0001628280-26-003952 text line 521 | PASS | Never paid. |
| PLTR | cf_inventory_change | tech | 0001321655-26-000011 tag list | PASS | No inventory tags. |
| PLTR | inventory | tech | same | PASS | Same. |
| META | gross_profit | tech | 0001628280-26-003942 R5 | PASS | No GP line. |
| XOM | amortization_of_intangibles | energy | 0000034088-26-000045 tag list + text | PASS | Tag absent and no text. D&D only. |
| XOM | cost_of_revenue | energy | 0000034088-26-000045 R3 | PASS | Purchases and production lines. No COR total. |
| XOM | gross_profit | energy | same | PASS | No GP line. |
| V | cost_of_revenue | payments | 0001403161-26-000134 R5 | PASS | Opex lines only. |
| V | inventory | payments | 0001403161-26-000134; -19-000050; -16-000058 | PASS | No inventory. |
| V | research_and_development | payments | same three 10-Ks | PASS | Only R&D tax-credit text. |
| PM | other_income_expense_net | consumer | 0001628280-26-005939 R3 | PASS | Below OI: net interest, pension, equity investments. No other-income line. |

Template-OUT: 50 drawn, 36 PASS, 14 FAIL (7 clear: MSFT ii, CVX cf_ap, CVX cf_ar, HD, MU, MS capex, GEV ppe; 7 def: JPM AR, BAC AR, GS AP, GS cf_ap, GS cf_ar, CVX ii, CVX sbc).

## Rates (Clopper-Pearson, exact binomial)

| class | n | FAIL | rate | 95% upper (two-sided interval) | 95% upper (one-sided) |
|---|---|---|---|---|---|
| note-sourced, all FAIL | 40 | 10 | 25.0% | 41.2% | 38.7% |
| note-sourced, value errors only | 40 | 7 | 17.5% | 32.8% | 30.4% |
| template-OUT, all FAIL | 50 | 14 | 28.0% | 42.5% | 40.3% |
| template-OUT, clear only | 50 | 7 | 14.0% | 26.7% | 24.7% |

## Re-check of the 42 FAIL rows from 2026-11-11

21 rows are no longer in either list. The tag map (ranks_1_50.csv @ addef9fe) decides each of them; DATA-INFERRED from the map, with the cited lines matching the 2026-11-11 filing evidence. 21 rows are still listed and were re-checked against the filing. 9 are fixed, 12 are not.

| company | data point | 11-11 class | now | accession / R page | status |
|---|---|---|---|---|---|
| JPM | interest_income | NS | removed: reason bank_interest_income_component | map | fixed (map) |
| JPM | cash_and_equivalents | NS | removed: CashAndDueFromBanks concept (bank_cash ruling) | map | fixed (map) |
| GS | interest_income | NS | removed: bank_interest_income_component | map | fixed (map) |
| AMD | other_income_expense_net | NS | removed: OtherNonoperatingIncomeExpense concept | map | fixed (map) |
| CAT | gross_profit | NS | OUT (in today's draw) | 0000018230-26-000008 R3 | FIXED |
| GE | gross_profit | NS | OUT (in today's draw) | 0000040545-26-000008 R3 | FIXED |
| JNJ | operating_income | NS | OUT | 0000200406-26-000016 R5 (GP printed, no OI) | FIXED |
| AMGN | gross_profit | NS | OUT | 0000318154-26-000010 R3 (no GP) | FIXED |
| COST | gross_profit | NS | OUT | 0000909832-26-000093 R3 (no GP) | FIXED |
| ORCL | gross_profit | NS | OUT | 0001193125-26-277521 R4 (no GP) | FIXED |
| CAT | stockholders_equity | NS | removed: parent_equity_not_printed | map | fixed (map) |
| PG | stockholders_equity | NS | removed: parent_equity_not_printed | map | fixed (map) |
| CSCO | depreciation_and_amortization | NS | still NS (in today's draw) | 0000858877-26-000132 R53, R8 | NOT FIXED: PP&E-only $0.7B component; the CF combined line 2,540 is unmapped |
| SHOP | accounts_receivable | NS | still NS (ReceivablesNetCurrent) | 0001594805-26-000007 R3 | NOT FIXED: the BS face prints "Trade and other receivables, net" 500 (AccountsAndOtherReceivablesNetCurrent) |
| BAC | interest_income | OUT | removed: bank_interest_income_component | map | fixed (map) |
| WFC | interest_income | OUT | removed: same | map | fixed (map) |
| GS | operating_expenses | OUT | still OUT | 0000886982-26-000091 R3 | NOT FIXED: the face prints "Total operating expenses" 37,544 (NoninterestExpense) |
| MS | interest_income | OUT | removed: bank_interest_income_component | map | fixed (map) |
| MS | share_buybacks | OUT | still OUT | 0000895421-26-000086 R8 | NOT FIXED: the CF prints "Repurchases of common stock and employee tax withholdings" (5,835), combined |
| MS | capex | OUT | still OUT (in today's draw) | 0000895421-26-000086 R8 | NOT FIXED |
| AAPL | interest_income | OUT | NS (in today's draw) | 0000320193-23-000106 R53 | FIXED |
| MSFT | interest_income | OUT | still OUT (in today's draw) | 0001193125-26-323660 R48 | NOT FIXED: InvestmentIncomeNet is not in the tag set |
| MSFT | depreciation_and_amortization | OUT | removed: combined DepreciationAmortizationAndOther | map | fixed (map) |
| GOOG | interest_income | OUT | NS (in today's draw) | 0001652044-26-000018 R74 | FIXED |
| GOOG | depreciation_and_amortization | OUT | removed: combined lines to 2023-09, then d_and_a_not_presented (ruling) | map | fixed (map) |
| ORCL | operating_expenses | OUT | removed: total_costs_incl_cost_of_revenue | map | fixed (map) |
| TXN | other_income_expense_net | OUT | removed: OtherNonoperatingIncomeExpense concept | map | fixed (map) |
| TSLA | other_income_expense_net | OUT | removed: same | map | fixed (map) |
| CAT | interest_income | OUT | still OUT | 0000018230-26-000008 R71 | NOT FIXED: "Investment and interest income" 416 (InvestmentIncomeNet) |
| CAT | other_income_expense_net | OUT | removed: OtherNonoperatingIncomeExpense concept | map | fixed (map) |
| KO | other_income_expense_net | OUT | removed: same | map | fixed (map) |
| KO | cf_ap_change | OUT | still OUT | 0001628280-26-010047 R126 | NOT FIXED: note combined "Increase (decrease) in accounts payable and accrued expenses" (6,612) |
| WMT | interest_expense | OUT | removed: InterestExpenseDebt + finance-lease components (ruling) | map | fixed (map) |
| HD | cf_inventory_change | OUT | still OUT (in today's draw) | 0001628280-26-019436 R8 | NOT FIXED: the map excludes IncreaseDecreaseInRetailRelatedInventories |
| LLY | cf_ar_change | OUT | still OUT | 0000059478-26-000013 R9; -20-000057 R8 | NOT FIXED: the CF face prints "Receivables—(increase) decrease"; the map excludes IncreaseDecreaseInAccountsAndOtherReceivables as "detail_of_printed_total" |
| AMGN | operating_expenses | OUT | removed: total_costs_incl_cost_of_revenue | map | fixed (map) |
| CVX | interest_expense | OUT | removed: InterestExpenseDebt concept | map | fixed (map) |
| CVX | sbc | OUT | still OUT (in today's draw) | 0000093410-26-000078 R110 | NOT FIXED: the reason "no fact" is false; two components are printed |
| XOM | inventory | OUT | removed: XOM components (CIK 34088 history) | map | fixed (map) |
| XOM | cf_ar_change | OUT | removed: combined IncreaseDecreaseInAccountsAndNotesReceivable | map | fixed (map) |
| XOM | sbc | OUT | still OUT | 0000034088-26-000045 R110 | NOT FIXED: "Compensation cost charged against income" $1.0B / 0.8 / 0.6, tagged only under PlanNameAxis/AwardTypeAxis (2003 Incentive Program, XOM's only SBC plan) |
| XOM | research_and_development | OUT | NS (in today's draw) | 0000034088-26-000045 R94 | FIXED |

Total: 30 of 42 fixed (21 by map, DATA-INFERRED; 9 FILING-CHECKED). 12 not fixed.

## Root causes still open
1. Tag sets are still narrow for combined or variant lines: InvestmentIncomeNet (MSFT, CAT, MU), IncreaseDecreaseInAccountsAndOtherReceivables (LLY; the map wrongly excludes the face line as "detail_of_printed_total", and WMT has the same exclusion), IncreaseDecreaseInRetailRelatedInventories (HD, also excluded in the WMT map), PaymentsForProceedsFromProductiveAssets as a sole capex line (MS), custom combined buyback and capex lines (MS), custom face lines (GEV PP&E, GE interest).
2. Combined note lines (KO, CVX working-capital notes) are not considered. The combined rule is applied only to face rows.
3. Component tags in the note-sourced tag sets: FinanceLeaseInterestExpense and InterestExpenseDebt inside interest_expense (META, DELL), InvestmentIncomeInterest used as total interest income when the company labels it a sub-item (GE), PSU-only SBC (PM), PP&E-only D&A (CSCO). The note class needs a per-period check that the fact is the total, not just tag membership.
4. Dimensioned-only totals read as absence: XOM SBC (plan axis), CVX interest income (segment axis).
5. The face check ignores the equity statement and non-set tags: WFC, GEV, SHOP SBC are printed on a face statement.
6. Filer mistag: ANET AmortizationOfIntangibleAssets carrying accumulated amortization in the 2025 10-Qs.
7. Bank and broker combined receivable/payable lines (JPM, BAC, GS) need a perimeter ruling.
