---
id: release-package-scripts-compute-and-assert-everything-first-
title: Release-package scripts: compute and assert everything first, write files last; match dropped cells by rounded month-end
kind: gotcha
tags: release-package, before-image, fsn, periods
paths: 
evidence: CODE-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/scripts/slot_records/capex_release_remove.py
---
2026-11-03: capex_release_remove.py rewrote the release cells file BEFORE asserting before-image/cells parity; the assertion then failed (11 of 96 dropped cells unmatched), leaving a half-updated package folder that had to be restored from git. Rule: build every output in memory, assert counts (cells = before-image = rollback updates) and subset/identical-values, then write. Cause of the mismatch: dropped cells were matched to production rows by calendar month, but FSN columns are month-end ROUNDED, so a 52/53-week year end such as 2016-01-02 belongs to the 2015-12-31 column. Always match with the same month_end() rounding the cells were built with. Also: in a shell chain, a ';' after a failing step still runs the following steps; use && throughout for package edits.
