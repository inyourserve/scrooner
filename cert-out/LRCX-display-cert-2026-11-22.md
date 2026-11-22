# LRCX display certification (Ritwik (cloud), approver, 2026-11-22): PASS

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/LRCX-coverage-2026-11-22.csv` (sha256 `c623fcf8ff3126426e306942c4c3cb7c1fbe73b47a45a27dafe206ca65a3c613`). Cells by display class: HIDDEN_YEAR=2, SHOWN_VALUE=550. Seed `LRCX-c623fcf8ff31`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 4 strata of 538 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 199 auto-matched, 0 auto-mismatched, 0 need a read; 0 read, 0 pending |
| total_debt census (12 years) | 12 match, 0 wrong, 0 for review |
| Derived cells census (7 undrawn) | 7 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 2 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for LRCX alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 538)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 53/144, cash_flow|as_printed 58/156, income_statement|as_printed 83/226, income_statement|derived 5/12

## Hidden rows evidenced


## Hidden years evidenced (allowlist)

- amortization_of_intangibles FY2025: search-evidenced verified absence: 2 periodic filing(s) present 2025-06-29, none prints a amortization_of_intangibles line
- amortization_of_intangibles FY2026: search-evidenced verified absence: 1 periodic filing(s) present 2026-06-28, none prints a amortization_of_intangibles line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
