---
id: 0119-company-value-owner-is-per-company-and-nothing-writes-i
title: 0119 company_value_owner is per company and nothing writes it; FSN cell protection is per cell via slot_protected_cell
kind: gotcha
tags: fsn, write, ownership, 0119, 0113
paths: pipeline/db/migrations/0119_company_value_owner.sql, pipeline/src/scrooner_pipeline/normalizer/cell_loader.py
evidence: CODE-CHECKED
created: 2026-11-09
verified: 2026-11-09
---
At origin/main 2026-11-09, analytics.company_value_owner (0119) is keyed by company_id only, and no code in pipeline/src inserts into it (0 rows since the apply). The FSN write protects its cells through analytics.slot_protected_cell (0113), per (company, concept) in cell_loader.py ~l.506-512, and it deletes old rows per (company, concept) (~l.954). If the write runs per (company, data point), one owner row would freeze that company's unwritten data points against the nightly. Keep the table empty, or migrate to per-concept ownership first (approver ruling RULING-DONE-GATE-C4, 2026-11-09).
