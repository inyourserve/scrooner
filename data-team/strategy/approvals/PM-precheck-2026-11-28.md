# PM certification precheck, 2026-11-28 (preparer: Scrooner data verifier): FAIL (census gate), draw clean

NOT a registry verdict and NOT a certificate. No certification request from top100-flow exists for this coverage; the coverage
file is this company's rows of the hourly export artifact top100-coverage-46167654745 (as_of 2026-11-28T16:55Z), so a
flow request will carry a different sha256 and a new seeded draw. Approver countersign is needed only for a FAIL record if wanted.

- Rank check: rank 38, company 5761, CIK 1413329 (not in the brief's list; also 1 OPEN); in ranks 1-100 of doc/data-moat/team/top1000/shards.csv and not excluded.
- Hourly summary: 1 OPEN shown cell.
- Coverage: `data-team/strategy/certification/PM-coverage-2026-11-28.csv`, sha256 `d1139a42ea3acf75ada7a0fc1be845704d29176b6a5c8ada304c777ade5253f1`.
- Run: pipeline/scripts/certify_display.py at origin/main f0f7ffbd9, --live (read-only, one connection), --no-registry, --reads approvals/reads/PM-d1139a42ea3a.csv where present.
- Blocker: OPEN other_income_expense_net FY2016 (HELD conflicting_values_in_filing, cites own FY2016 10-K 0001413329-17-000014) plus census badge FAIL other_income_expense_net FY2015 (as_printed badge on a derived formula). Cause: the hold mixes the pre-recast own filing with the ASU 2017-07 recast; the latest 10-K presenting 2016 is FY2018 10-K 0001413329-19-000007 (one vintage, X87), which prints 'Pension and other employee benefit costs | 41 | 78 | 88'. Fix: resolve FY2016 from the FY2018 10-K as -88,000,000 (ruling 16, open-shown-fixes/PM-2026-11-24.csv); set FY2015 badge to derived:income_before_tax-operating_income+interest_expense (value 0 from FY2017 10-K R4).
- Draw: 199 stratified shown cells, 0 wrong, Clopper-Pearson 95% upper bound 1.49% (target 1.5%). Every NEEDS_READ cell was read in the filing (FILING-CHECKED); reads file above.
- Next: land the fix above, then one top100-flow run for this company (queue empty), then display-certify on the new request.
- Untested: the 5% AUTO_MATCH audit sample (--audit-out) was not run; it belongs to the request-sha draw.

## Generated output: PM display certification (Ritwik (cloud), approver, 2026-11-28): FAIL

Coverage `data-team/strategy/certification/PM-coverage-2026-11-28.csv` (sha256 `d1139a42ea3acf75ada7a0fc1be845704d29176b6a5c8ada304c777ade5253f1`). Cells by display class: HIDDEN_ROW=11, HIDDEN_YEAR=1, OPEN=1, SHOWN_VALUE=493. Seed `PM-d1139a42ea3a`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 2 failing |
| 199 random shown cells (stratified, 6 strata of 482 shown) | 197 match, 0 wrong, 2 locator only |
| Automated draw checker (draw_check@3, the filing's own facts) | 197 auto-matched, 0 auto-mismatched, 2 need a read; 2 read, 0 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (14 undrawn) | 14 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 2 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for PM alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 482)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 50/121, balance_sheet|derived 5/11, cash_flow|as_printed 54/132, cash_flow|combined 5/10, income_statement|as_printed 79/194, income_statement|derived 6/14

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** operating_expenses FY2022 (family): no fact of the checker's operating_expenses family at 2022-12-31 in 0001413329-25-000013 (custom, dimensioned or note-only line): read the filing -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2024 10-K 0001413329-25-000013 R3 Consolidated Statements of Earnings, 2022 column: "Gross profit 20,360"; "Marketing, administration and research costs 8,114"; "Impairment of goodwill 0"; "Operating income 12,246". Component sum 8,114 + 0 = 8,114 = GP - OI (docmap component sum). Served 8,114,000,000.)
- **NEEDS_READ** share_buybacks FY2018 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 54 of 0001413329-19-000007 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2018 10-K 0001413329-19-000007 pm123118form10kwrapinclfsm.htm Item 7: "During 2018, 2017 and 2016, we did not repurchase any shares under a share repurchase program, and we do not presently intend to repurchase shares of our common stock in 2019." Served 0.)

## Findings

- **FAIL** gate other_income_expense_net 2016: OPEN cell
- **FAIL** badge other_income_expense_net 2015: badge 'as_printed' on a computation: the locator is a formula (R4.htm (derived: us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments - us-gaap:OperatingIncomeLoss + us-gaap:InterestIncomeExpenseNet) of 0001413329-18-000007, read FY2015 10-K); a value the filing does not print carries its derived: badge
- **LOCATOR** share_buybacks FY2018: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 54 of 0001413329-19-000007), no tag: approver reads the quote
- **LOCATOR** other_income_expense_net FY2015: served 0, filing None. text-stated value located by its quote (R4.htm (derived: us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments - us-gaap:OperatingIncomeLoss + us-gaap:InterestIncomeExpenseNet) of 0001413329-18-000007, read FY2015 10-K of 0001413329-18-000007), no tag: approver reads the quote

## Hidden rows evidenced

- sga_expense: no presented, undimensioned, annual ['GeneralAndAdministrativeExpense', 'SellingGeneralAndAdministrativeExpense'] fact at a display-year end in any periodic filing

## Hidden years evidenced (allowlist)

- share_buybacks FY2025: allowlisted: 1 periodic filing(s) present 2025-12-31, none prints a share_buybacks line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
