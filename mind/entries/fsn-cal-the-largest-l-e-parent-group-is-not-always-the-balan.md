---
id: fsn-cal-the-largest-l-e-parent-group-is-not-always-the-balan
title: FSN cal: the largest L&E-parent group is not always the balance sheet; pick the group whose arcs sit on the BS face
kind: gotcha
tags: fsn, cal, balance-sheet, bs_assemble
paths: pipeline/scripts/slot_records/common.py
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
OXY 0000797468-16-000023: grp2 (larger, carries cash-flow arcs) beats the real face group grp6 under common.fsn_cal_arcs' largest-group rule, so bs_assemble kept 8 members instead of 3 roots. fsn_cal_arcs(face_tags=...) (opt-in, BS port 2026-11-01) picks the group with most arcs whose parent and child are both BS face tags. Debt (assemble_fsn) still uses the default. Evidence: data-team/strategy/team/BS-PORT-2026-11-01.md 5.3.
