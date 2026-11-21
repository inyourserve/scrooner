# JNJ display certification (Ritwik (cloud), approver, 2026-11-21): PASS

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/JNJ-coverage-2026-11-16.csv` (sha256 `674389ae0acd749aea09ffaa48e37fe3ab1ca07f7044f9cf7385f42a497229bb`). Cells by display class: HIDDEN_ROW=44, SHOWN_VALUE=462. Seed `JNJ-674389ae0acd`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 32 random shown cells | 32 match, 0 wrong, 0 locator only |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 4 evidenced |

**Bound:** 0 error(s) in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for JNJ alone (per-company screen; the 0.10% target is pooled across certified companies in registry.csv).

## Hidden rows evidenced

- cf_ap_change: no presented, undimensioned, annual ['IncreaseDecreaseInAccountsPayable', 'IncreaseDecreaseInAccountsPayableTrade'] fact at a display-year end in any periodic filing
- operating_expenses: no presented, undimensioned, annual ['CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses'] fact at a display-year end in any periodic filing
- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing
- shares_outstanding: no presented, undimensioned, annual ['CommonStockSharesOutstanding'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
