---
id: held-differs-from-resolver-cells-live-in-analytics-cell-blan
title: Held differs_from_resolver cells live in analytics.cell_blank_reason (reason_code), not in canonical_fact
kind: howto
tags: resolver, held, census
paths: pipeline/src/scrooner_pipeline/mapper/structural_direct.py
evidence: CODE-CHECKED
status: active
created: 2026-11-22
verified: 2026-11-22
---
structural_direct.enforce_resolver writes each held cell as a defect blank (defect_class guard_hidden, reason_code differs_from_resolver) into analytics.cell_blank_reason. Count them per company with: select company_id, data_point_name, count(*) from analytics.cell_blank_reason where reason_code='differs_from_resolver' group by 1,2. core.company has primary_ticker, not ticker. As of 2026-11-22 there are only 19 (LIN 18, C 1), because the rebuild since enforcement covered just 32 companies.
