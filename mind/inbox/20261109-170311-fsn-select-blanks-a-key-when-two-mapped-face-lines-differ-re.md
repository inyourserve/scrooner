---
id: fsn-select-blanks-a-key-when-two-mapped-face-lines-differ-re
title: FSN select blanks a key when two mapped face lines differ: revenue (33 cos) and CFO (16 cos) hit it in latest 10-Ks
kind: gotcha
tags: fsn, select, conflicting_values_in_filing, revenue, cfo
paths: pipeline/src/scrooner_pipeline/fsn_store/select.py, data-team/tags/cards/shareholder-returns.md, data-team/tags/cards/revenue.md
evidence: DATA-INFERRED
created: 2026-11-09
verified: 2026-11-09
---
select.select_concept marks a key conflicting_values_in_filing when the latest filing has two mapped prints with different values. fsn.line_map (2026-11-09, latest 10-K, 632 cos) maps both an RCFC component and the Revenues total at 33 companies (GM Automotive 167,971M vs 185,019M; Welltower; WMT; CVX; excise pairs 14693/24545/16918), and both NetCashProvidedByUsedInOperatingActivitiesContinuingOperations and the total at 16 (2488 R8 6,493M vs 7,709M). Implied rules: later Total Revenues line wins inside one IS report; continuing-ops CFO only when no total is printed. Sent to the mapping builder.
