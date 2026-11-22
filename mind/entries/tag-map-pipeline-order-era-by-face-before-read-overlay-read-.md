---
id: tag-map-pipeline-order-era-by-face-before-read-overlay-read-
title: Tag map pipeline order: era_by_face before read_overlay; read/ruling rows are never face-gated
kind: gotcha
evidence: CODE-CHECKED
status: active
created: 2026-11-12
verified: 2026-11-12
---
Running pipeline/scripts/tag_library/era_by_face.py on the FINAL ranks seed face-gates rows decided from full 10-K reads and rulings (note values, prior-year columns not printed on the period's own face) and reopened 21 FY0/FY-1 cells (Engineering DB run 2026-11-12). era_face.face_checked now skips groups holding read_verified/ruling/read_status/debt_lane rows (main 95575804). Order: library -> era_by_face -> read_overlay -> merge_debt -> apply_fy_rulings -> fy_status_rows -> value_source -> cross_stmt -> coverage checks.
