Under test: origin/review/template-company-outs-2026-11-03 ce38be9, data-team/47-fsn-store/template_company_outs_approval_2026-11-03.csv (Ritwik's verdicts; the brief called it template_company_outs.csv).
Seed 20261101 (md5('20261101:'+cik+':'+data_point)). Drawn: 10 REJECT_NOTE_SOURCED_VALUE + 5 APPROVE_OUT_FROM. SEC requests: 100 (sec.gov only, <= 3.4/s). Verifier session scrooner-c3, read-only.

# Verify: template company OUTs, approver verdicts (2026-11-03)

## Result

| verdict class | drawn | right | wrong |
|---|---|---|---|
| REJECT_NOTE_SOURCED_VALUE (the value is printed in a note, so not an OUT) | 10 | **9** | **1** (ELV operating income) |
| APPROVE_OUT_FROM (IN through the date, OUT after) | 5 | **0** | **5** (DAL, TOL, IP, SLB, WPC) |

**Root cause: tag presence is not concept presence.** The approval used non-dimensional annual facts in core.fact. It found the tag, not the line. In 6 of 15 rows the tagged fact is something else:
- **Segment totals:** ELV, IP, SLB. Their `OperatingIncomeLoss` is "Reportable segments' operating gain", "Total industry segment operating profit" or "Pretax segment operating income". Each reconciles to pretax income; none is a consolidated operating income line.
- **A net figure under a gross tag:** DAL's `InterestExpense` is "Interest expense (income), net", the same figure as the face's net line.
- **A misused tag:** WPC's `OperatingIncomeLoss` is income before income taxes.
- **A partial concept:** TOL's `InterestExpenseDebt` is "Directly expensed interest" (0 in FY2021-22). The interest TOL capitalises is not in it.

For the 5 OUT_FROM rows the cutoff date matches where the tag stops, but the IN-period values it would serve are not interest expense or operating income. **All 5 should be APPROVE_OUT for every period.** ELV should be APPROVE_OUT too, or a separate segment concept.

## Method

For each row:
1. I opened the latest 10-K for a REJECT row, or the 10-K for the OUT year and the next one for an OUT_FROM row.
2. In the XBRL instance I listed non-dimensional annual facts of the approver's tags (IE: InterestExpense, InterestExpenseNonoperating, InterestExpenseDebt, InterestAndDebtExpense, InterestExpenseOperating; OI: OperatingIncomeLoss).
3. I found which statement or note presents them, from the presentation linkbase (or the embedded linkbase for SLB) and FilingSummary roles.
4. I read the line label and value on that R page.

## REJECT_NOTE_SOURCED_VALUE (10)

| company, data point | 10-K | where printed (R page, label, tag) | FY values | verdict |
|---|---|---|---|---|
| PEN IE | 0001321732-26-000007 | R93 "Interest and other income, net (Details)": "Interest expense", InterestExpenseNonoperating | 2025 1,311; 2024 1,418; 2023 1,739 ($K) | RIGHT (note) |
| INTC IE | 0000050863-26-000011 | R68 "Interest and Other, Net (Details)": "Interest expense", InterestExpenseNonoperating | 2025 1,091; 2024 1,034; 2023 878 ($M) | RIGHT (note) |
| CRWV IE | 0001769628-26-000104 | R75 "Debt - Interest Expense (Details)": "Total", InterestExpenseDebt | 2025 1,148; 2024 349; 2023 27 ($M) | RIGHT (note) |
| PYPL IE | 0001633917-26-000024 | R76 "Other Income (Expense), Net (Details)": "Interest expense", InterestExpenseNonoperating | 441; 382; 347 ($M) | RIGHT (note) |
| CRCL IE | 0001876042-26-000062 | R86 "Other (Expense) Income, Net": "Interest expense and amortization of discount", InterestExpenseNonoperating | 1,226; 1,906; 1,912 ($K) | RIGHT (note; includes discount amortization) |
| BIIB IE | 0000875045-26-000013 | R139 "Other Income (Expense), Net (Details)": "Interest expense", InterestExpense | 267.5; 250.3; 246.9 ($M) | RIGHT (note) |
| DRI IE | 0000940944-26-000025 | R77 "Schedule of Components of Interest": "Interest expense", InterestExpenseNonoperating | FY2026 126.5; FY2025 115.9; FY2024 93.5 ($M) | RIGHT (note) |
| W IE | 0001616707-26-000027 | R58 "Debt ... Interest Expense (Details)": "Total Interest Expense", InterestExpense (first row is the non-dimensional total) | 165; 83; 63 ($M) | RIGHT (note) |
| AVAV IE | 0001104659-26-078906 | R61 "Significant Accounting Policies - Interest Expense, net (Details)": "Interest expense", InterestExpenseDebt | **FY2026 only: 24.197M**; no comparatives tagged | RIGHT for FY2026. Earlier years are not shown in this filing, so the effective date needs a per-year check |
| **ELV OI** | 0001156039-26-000013 | R114/R116 Segment Information: "Reportable segments' operating gain", OperatingIncomeLoss | 7,199; 7,862; 8,499 ($M). Reconciles to income before tax of 6,710 / 7,904 / 7,715 (R116) | **WRONG.** A segment-measure total, not consolidated operating income. Keep the OUT |

## APPROVE_OUT_FROM (5)

| company, data point, OUT after | 10-K for the OUT year (where, label) | next 10-K | verdict |
|---|---|---|---|
| DAL IE, 2017-12-31 | 0000027904-18-000006 R83 segment note: "Interest expense (income), net", InterestExpense 396 / 388 / 481. The face (R4) prints the same 396 as "Interest expense, net" (InterestIncomeExpenseNet) | 0000027904-19-000003: no non-dimensional fact | **WRONG.** The IN values are net interest, exactly what the template's `only_net_interest_printed` says. OUT for all periods |
| TOL IE, 2022-10-31 | 0000794170-22-000049 R105 "Other Income - Net": "Directly expensed interest", InterestExpenseDebt FY2022 0, FY2021 0, FY2020 2.44M | 0000794170-23-000066: none | **WRONG as interest expense.** This is only the directly expensed part (TOL capitalises interest into inventory). Serving 0 for FY2021-22 would mislead. OUT for all periods, or a definition ruling |
| IP OI, 2015-12-31 | 0000051434-16-000042: only role R136 "Financial Information By Industry Segment (Operating Profit By Industry Segment)"; non-dimensional 2,361 / 2,058 / 2,233 | 0000051434-17-000007: the same role, dimensional facts only | **WRONG.** A segment operating-profit total. OUT for all periods |
| SLB OI, 2023-12-31 | 0000950170-24-006884 R85 "Segment Reporting Information by Segment": "Pretax segment operating income", OperatingIncomeLoss 6,523 / 5,011 / 3,365, beside "Pretax Income" 5,282 / 4,271 / 2,374 | 0000950170-25-007638: none | **WRONG.** A segment measure. OUT for all periods |
| WPC OI, 2015-12-31 | 0001025378-16-000062 R106 "Income Taxes (Details 2)": "Income from continuing operations before income taxes, net of amounts attributable to noncontrolling interests", tagged OperatingIncomeLoss 209,879 / 223,938 / 85,889 ($K) | 0001025378-17-000016: none | **WRONG.** A misused tag (pretax income). OUT for all periods |

## Findings for the approver and engineering

1. **Before a REJECT or OUT_FROM verdict stands, read each fact's label and page,** not just the tag. Reject the evidence when the page is a segment note whose total reconciles to pretax income, when the label says "net", or when the page is a tax-rate reconciliation.
2. **Re-check all 25 OUT_FROM rows on that basis.** This sample suggests most are segment totals or misused tags. Of the 15 OI REJECT rows, ELV shows the same segment-total pattern; check those too.
3. **The IE REJECT rows look sound.** The note tables print a gross "Interest expense" line. AVAV needs its effective start year checked, because only FY2026 is tagged.

## Requests and disk

100 sec.gov requests: index.json, instance, presentation linkbase and FilingSummary per 10-K, plus the R pages. Downloads were deleted at the end. No database writes; one read on core.filing for 10-K accessions.
