# GILD display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/GILD-coverage-2026-11-22.csv` (sha256 `fc4df887df611ea3e34b351e818f28233a2a9dc1557425aa754eb238b684eb2a`). Cells by display class: HIDDEN_YEAR=7, SHOWN_VALUE=499. Seed `GILD-fc4df887df61`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 6 strata of 488 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 197 auto-matched, 0 auto-mismatched, 2 need a read; 0 read, 2 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (25 undrawn) | 25 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 7 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for GILD alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 488)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 49/121, balance_sheet|derived 5/11, cash_flow|as_printed 54/132, cash_flow|derived 5/11, income_statement|as_printed 77/191, income_statement|derived 9/22

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** interest_income FY2024 (family): no fact of the checker's interest_income family at 2024-12-31 in 0000882095-26-000006 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** interest_income FY2025 (family): no fact of the checker's interest_income family at 2025-12-31 in 0000882095-26-000006 (custom, dimensioned or note-only line): read the filing -- pending read

## Hidden rows evidenced


## Hidden years evidenced (allowlist)

- interest_income FY2015: search-evidenced verified absence: 3 periodic filing(s) present 2015-12-31, none prints a interest_income line
- interest_income FY2016: search-evidenced verified absence: 3 periodic filing(s) present 2016-12-31, none prints a interest_income line
- interest_income FY2017: search-evidenced verified absence: 3 periodic filing(s) present 2017-12-31, none prints a interest_income line
- interest_income FY2018: search-evidenced verified absence: 3 periodic filing(s) present 2018-12-31, none prints a interest_income line
- interest_income FY2019: search-evidenced verified absence: 3 periodic filing(s) present 2019-12-31, none prints a interest_income line
- interest_income FY2020: search-evidenced verified absence: 3 periodic filing(s) present 2020-12-31, none prints a interest_income line
- interest_income FY2021: search-evidenced verified absence: 3 periodic filing(s) present 2021-12-31, none prints a interest_income line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
