---
id: cell-writes-to-canonical-fact-must-pass-protect-or-the-night
title: Cell writes to canonical_fact must pass --protect or the nightly refresh overwrites them
kind: gotcha
tags: canonical_fact, cell_loader, slot_protected_cell, nightly
paths: pipeline/src/scrooner_pipeline/normalizer/cell_loader.py, .github/workflows/pipeline-fsn-write.yml
evidence: CODE-CHECKED
status: active
created: 2026-11-06
verified: 2026-11-22
---
scrooner-cells load sets scrooner.slot_writer=on, which only lets it past the 0113 guard; it does not stop later writers. Without --protect (bc6ab31) the nightly mapper/conflict fill/derivation can overwrite or re-insert old values over loaded cells. --protect records each written key in analytics.slot_protected_cell (value, or null for a reasoned blank per 0115), per cell, family-scoped; do not use company_value_owner (freezes the whole company). Rollback: scrooner-cells restore from the pilot-prod before-image, which includes slot_protected_cell. Tests: test_protected_write_survives_a_non_slot_writer_update_which_is_logged (mutation run 41709219798 fails it).

[2026-11-22] Merged 2026-11-22 from two earlier entries (2026-11-05): any bulk write that replaces served values must write the per-cell slot_protected_cell rows in the same transaction (removed again on restore) with a DB test showing a nightly-style write is skipped; slot_protected_cell.value is nullable since 0115 so reasoned blanks can be protected; the 0113 guard only lets a writer past, it does not protect (CFO/buyback applies 2026-10-31; Ritwik review of c67a6d2 2026-11-04).
