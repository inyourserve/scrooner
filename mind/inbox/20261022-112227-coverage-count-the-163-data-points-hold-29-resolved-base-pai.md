---
id: coverage-count-the-163-data-points-hold-29-resolved-base-pai
title: Coverage count: the 163 data points hold 29 _resolved/base pairs; F-1 removes 30 rows, not 31
kind: gotcha
tags: coverage, denominator, resolved, F-1
paths: data-team/strategy/data/cohort_cells.csv, pipeline/src/scrooner_pipeline/statements/classify.py, data-team/strategy/FREEZE-REGISTER-2026-10-22.md
evidence: DATA-INFERRED
source: data-team/strategy/FREEZE-REGISTER-2026-10-22.md section 0.1-0.3
created: 2026-10-22
verified: 2026-10-22
---
29 data points end in _resolved: 28 have a same-name base twin (employee_count is one of them) and revenue_sanity_resolved pairs with revenue. Docs 46/47/49 say '29 twins + total_debt_split + base employee_count', which counts employee_count twice. Correct removal: 29 base rows + total_debt_split = 30 data points = 29,580 cells of the 986 cohort; D0e = 986 x 133 = 131,138. Statements display the _resolved side (classify.py L150-220), so it is the cell of record. Removal lowers fill (76.73% -> 74.98% on the 2026-10-20 export) because the removed base rows are mostly valued.
