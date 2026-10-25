---
id: reason-store-design-company-level-cells-key-on-the-latest-pe
title: Reason-store design: company-level cells key on the latest periodic filing period, never date.today()
kind: decision
tags: cell-key, reason-store
paths: doc/data-moat/team/PLAN.md
evidence: CODE-CHECKED
created: 2026-10-23
verified: 2026-10-23
---
Ruled 2026-10-22: a company-level cell (e.g. D-4 employee_count) uses grain I with period_start = period_end = period_of_report of the latest periodic filing; no periodic filing means no cell. date.today() orphans rows each run; a sentinel date breaks 'history never forces a re-key'. Reasons use rule-specific reason_code; state/class names are rejected. Migration numbers: 0107 TTM cleanup (lane 2), 0108/0109 ADS tables (lane 3), next free 0110.
