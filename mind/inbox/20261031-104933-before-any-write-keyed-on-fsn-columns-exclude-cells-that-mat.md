---
id: before-any-write-keyed-on-fsn-columns-exclude-cells-that-mat
title: Before any write keyed on FSN columns, exclude cells that match two production periods (predecessor entity, 52/53-week)
kind: gotcha
tags: fsn, release-package, before-image, periods
paths: pipeline/scripts/slot_records/capex_release_package.py
evidence: DATA-INFERRED
created: 2026-10-31
verified: 2026-10-31
---
FSN num ddate is month-end rounded and carries no start date, so (cik, rounded end, quarters) can match two core.period rows: merger predecessors (ONTO/Rudolph, JCI/Tyco, KDP/DPS) and 52/53-week duplicates (RBC, Z). In capex release 1 (2026-11-01), 8 of 2,123 cells matched two production rows, and in several one row already equalled the face value, so the 'difference' was against the wrong row. Rule: count production matches per cell; exclude any cell with more than one from the release (reason ambiguous_period_match), from its before-image and from its CIK list. Related: FSN pre can give a generic line another row's label (AMD FY2024 AdjustmentForAmortization carried the ROU line's label), so a label shared by two different tags is no evidence.
