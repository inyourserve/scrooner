---
id: era-detect-label-rx-matches-securities-loaned-asset-line-and
title: era_detect LABEL_RX matches 'securities loaned' (asset line) and holds whole debt records (MSFT, GOOG)
kind: gotcha
tags: debt, era_detect, coverage
paths: pipeline/scripts/slot_records/era_detect.py
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
'loan' in LABEL_RX hits 'Short-term investments, securities loaned' (MSFT SecuritiesLoaned, GOOG custom SecuritiesOwnedAndLoaned): uncovered candidate -> coverage_clean=false -> 18 Verifier-passed report_v4 cells held as not_computable_uncovered_candidates in the assemble_fsn cohort path. Fails safe. BS-PORT-2026-11-01.md 5.1.
