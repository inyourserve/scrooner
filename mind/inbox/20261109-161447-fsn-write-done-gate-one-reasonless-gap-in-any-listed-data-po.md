---
id: fsn-write-done-gate-one-reasonless-gap-in-any-listed-data-po
title: FSN write done gate: one reasonless gap in ANY listed data point blocks ALL families for that company
kind: gotcha
tags: fsn-store, done-gate, release
paths: pipeline/src/scrooner_pipeline/fsn_store/pilot.py, .github/workflows/pipeline-fsn-write.yml
evidence: DATA-INFERRED
created: 2026-11-09
verified: 2026-11-09
---
pilot.done_gate criterion 4 counts gaps over every data point in the write's data_points; a failing company gets no family written. Cohort dry run 41708119011 gaps.csv: default 15 IS/CF/per-share points pass 13 of 960 companies (buybacks block 876, dividends 817); +capex+D&A -> 5; +debt -> 0. Adding a correct family can shrink the write. Measure from gaps.csv before changing data_points. Also: D&A 'combined' line_map rows carry no concept id, so they become no_mapped_line gaps, not reasons.
