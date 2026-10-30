# Verify: nightly per-company resolve-statement-fallbacks + resolve-conflict-fills (work/engineering/nightly-resolve-stages d2f6c1a), 2026-10-31

Seed 20261031. Files: nightly-resolve-dryrun-cells.csv from scrooner-8a (473 rows: 466 added, 7 value_changed; regenerated from a rolled-back dry run against live DB). Claimed counts: added=466, value_changed=7. Evidence class: FILING-CHECKED (each cell read from the claimed accession's own BS/IS/CF R page). Verifier 2 (scrooner-bc).

## Result
**Ready to merge: NO as packaged, YES once one cell is held.** 25 of 26 graded cells right, 1 wrong (RNG capex x2 reported separately, ungraded).
- 20 of 20 drawn added rows right.
- PM: 4 of 5 changed values right (they now match PM's recast comparatives in the 2026 Q3 10-Q). **PM Q4 2025 operating_expenses_resolved 3,412M is wrong** on any single basis: it is inherited from a mixed-basis derived Q4 gross profit (below), not introduced by this branch's logic. Production's current 3,415M is also wrong.
- The stage change itself (per-company scoping, ON CONFLICT DO NOTHING inserts) produced no defect in the sample.

## Method
Instant cells: printed balance-sheet line at the instant. Duration cells: income or cash-flow line at the column matched by end date and duration (months). Derived cells (operating expenses = revenue - cost of revenue - operating income): recomputed from the same page and cross-checked against the printed expense lines. Derived quarters: 9M from the claimed 10-Q minus 6M from the prior 10-Q, or FY minus 9M. Production values and builder code were not used as evidence.

## Sample
All 7 value_changed rows; 20 added rows by `random.seed(20261031); random.sample(sorted added rows by (company_id, concept, period_id), 20)`.

## Cell table
| Company | Concept | Period | Accession (page) | Face | New | Verdict |
|---|---|---|---|---|---|---|
| JBL 1825 | current_liabilities | 2026-08-31 | 0001628280-26-067038 BS | 21,673M | 21,673M | right |
| JBHT 1343 | basic_eps | Q3 2026 | 0001437749-26-033365 IS | 1.84 | 1.84 | right |
| RNG 5574 | current_assets | 2026-09-30 | 0001384905-26-000061 BS | 723,049K | 723,049K | right |
| LVS 4813 | income_tax_expense | Q3 2026 | 0001300514-26-000103 IS | (102)M deduction | 102M | right (sign is presentation) |
| KMI 2340 | net_income | Q3 2026 | 0001506307-26-000132 IS | 764M attributable | 764M | right |
| OMC 347 | income_before_tax | Q2 2026 | 0000029989-26-000019 IS | 829.2M | 829.2M | right |
| ALV 2518 | diluted_eps | 9M 2026 | 0001193125-26-429588 IS | 5.36 | 5.36 | right |
| OMC 347 | diluted_eps | 9M 2026 | 0000029989-26-000026 IS | 5.77 | 5.77 | right |
| TXN 1104 | total_assets | 2026-09-30 | 0000097476-26-000169 BS | 36,839M | 36,839M | right |
| JBHT 1343 | cash_flow_financing | 9M 2026 | 0001437749-26-033365 CF | (830,829)K | -830,829K | right |
| STLD 2396 | income_tax_expense | Q3 2026 | 0001104659-26-118461 IS | 222,896K | 222,896K | right |
| WDC 1145 | current_liabilities | 2026-10-02 | 0001628280-26-066933 BS | 4,092M | 4,092M | right |
| AYI 3955 | net_income | FY to 2026-08-31 | 0001144215-26-000052 IS | 531.3M | 531.3M | right |
| HAL 620 | total_liabilities | 2026-09-30 | 0000045012-26-000074 BS | 14,912M | 14,912M | right |
| OMC 347 | operating_expenses | 6M 2026 | 0000029989-26-000019 IS | 12,805.4 - 10,470.0 - 1,568.7 = 766.7M (= SG&A 433.5 + D&A 333.2) | 766.7M | right |
| RNG 5574 | dividends_paid | 9M 2026 | 0001384905-26-000061 CF | (23,284)K | 23,284K | right |
| TDY 3385 | income_before_tax | Q3 2026 | 0001094285-26-000059 IS | 346.8M | 346.8M | right |
| BAH 5880 | current_liabilities | 2026-09-30 | 0001628280-26-066973 BS | 2,010M | 2,010M | right |
| RNG 5574 | cash_flow_investing | 9M 2026 | 0001384905-26-000061 CF | (80,696)K | -80,696K | right |
| TDY 3385 | operating_expenses | 9M 2026 | 0001094285-26-000059 IS | 4,907.5 - 2,756.2 - 974.6 = 1,176.7M (= SG&A + R&D + amortization) | 1,176.7M | right |
| PM 5761 | cost_of_revenue | Q3 2025 | 0001628280-26-066976 IS (recast comparative) | 3,484M | 3,484M (was 3,487) | right |
| PM 5761 | cost_of_revenue | 9M 2025 | same | 9,789M | 9,789M (was 9,806) | right |
| PM 5761 | gross_profit | Q3 2025 | same | 7,361M | 7,361M (was 7,358) | right |
| PM 5761 | operating_expenses | Q3 2025 | same | 7,361 - 4,263 = 3,098M | 3,098M (was 3,095) | right |
| PM 5761 | operating_expenses | Q4 2025 | 10-K 0001628280-26-005939 IS + 10-Q above | see Findings | 3,412M (was 3,415) | **wrong** |

## Withheld cells (avoidable holds)
None in scope (this change only adds or replaces).

## False holds
None.

## RNG capex (reported, not graded: software perimeter is an open founder question)
What the filing prints (10-Q 0001384905-26-000061 CF, $ thousands, 9M 2026): "Purchases of property and equipment" (24,127) and "Capitalized internal-use software" (48,640), two separate investing lines; no printed capex total. Q2 10-Q 0001384905-26-000046 CF (6M): (17,135) and (32,507). So Q3 2026 = 6,992 PP&E + 16,133 software. New values: 9M 72,767 = 24,127 + 48,640; Q3 23,125 = 6,992 + 16,133. Both are exact sums of printed lines. Old values (24,127 and 6,992) are the PP&E line alone. Which is "capex" is the founder's call.

## Findings for the builder
1. **PM Q4 2025 mixed basis (upstream, derive-q4).** The FY 2025 10-K (filed 2026-02-06) is on the pre-recast basis: revenue 40,648, cost of sales 13,366, GP 27,282, OI 14,892. The 2026 Q3 10-Q recast the 2025 comparatives (cost of sales "(Note 1)": 9M 9,806 -> 9,789; GP 9M 20,480 -> 20,497). Derived Q4 GP 6,785 = 27,282 - 20,497 (recast 9M), but derived Q4 cost of revenue 3,560 = 13,366 - 9,806 (original 9M). Q4 revenue 10,362 is not equal to 3,560 + 6,785 = 10,345. On the 10-K's own basis, Q4 GP = 6,802 and Q4 operating expenses = 6,802 - 3,373 = 3,429M. Action: derive-q4 must take FY and 9M from the same basis (the 9M as originally filed when the FY predates the recast), or hold the quarter when the 9M was recast after the FY. Until then, hold PM Q4 2025 operating_expenses_resolved (and check its gross_profit / cost_of_revenue rows). Re-verify after the fix: Q4 GP + Q4 COGS = Q4 revenue.
2. The 4 PM Q3/9M 2025 changes adopt the recast comparatives. That is right per the latest filing, but those quarters now sit on a different basis from FY 2025 until PM files its FY 2026 10-K. Any derived Q4 2025 or TTM that spans both is mixed. Worth a rule: when a later filing recasts a comparative, re-derive or hold every dependent Q4/TTM cell.
3. PM Q3 2025 cost_of_revenue_resolved is derived (revenue from the 2025 10-Q minus GP from the 2026 10-Q) although the 2026 10-Q prints cost of sales 3,484 directly. Same number here (revenue unchanged), but prefer the printed line from the same filing.

## Requests and disk
SEC requests: 79 (64 sample pages, 12 re-reads, 3 RNG Q2). Nothing saved to disk except this file. One DB read for 7 source fact ids (single connection, 60s timeout).

## Untested scope
446 of 466 added rows not drawn. The 10 rows whose only change was source_fact_ids were not checked. Run-time behaviour of the nightly script (timeouts, per-company scoping under load) was not exercised.
