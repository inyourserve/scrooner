---
id: cell-display-state-0130-is-live-although-its-file-is-in-pend
title: cell_display_state 0130 is live although its file is in pending/; change the hide_class CHECK only by a new migration
kind: gotcha
evidence: CODE-CHECKED
status: active
created: 2026-11-22
verified: 2026-11-22
---
analytics.cell_display_state exists on dev Supabase with a 4-class hide_class CHECK (pg_constraint cell_display_state_hide_class_check, checked 2026-11-22). Its file stays in pipeline/db/pending/ only for contiguity (doc 53 row 0130). Never edit 0130; a new class needs a new migration (0133 added only_after_tax_disclosed, 783fa4a4). tests/unit/test_cell_display_state.py reads the effective CHECK.
