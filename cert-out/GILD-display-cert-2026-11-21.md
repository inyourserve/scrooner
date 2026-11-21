# GILD display certification (Ritwik (cloud), approver, 2026-11-21): PASS

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/GILD-coverage-2026-11-16.csv` (sha256 `e4ed0b0f7eb9e927845211c4a4d13fc805723768d2472112192e4889568905f9`). Cells by display class: HIDDEN_ROW=11, SHOWN_VALUE=495. Seed `GILD-e4ed0b0f7eb9`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 32 random shown cells | 32 match, 0 wrong, 0 locator only |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 1 evidenced |

**Bound:** 0 error(s) in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for GILD alone (per-company screen; the 0.10% target is pooled across certified companies in registry.csv).

## Hidden rows evidenced

- interest_income: no presented, undimensioned, annual ['InterestAndOtherIncome', 'InterestIncomeNonoperating', 'InterestIncomeOperating', 'InterestIncomeOther', 'InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
