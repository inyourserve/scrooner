---
id: a-canonical-fact-write-that-the-nightly-must-not-revert-need
title: A canonical_fact write that the nightly must not revert needs slot_protected_cell rows in the same transaction (value may be null since 0115)
kind: gotcha
tags: canonical_fact, nightly, slot_protected_cell, release, cell_loader
paths: pipeline/src/scrooner_pipeline/normalizer/cell_loader.py, pipeline/db/migrations/0113_slot_protected_cell.sql, pipeline/db/migrations/0115_slot_protected_cell_value_nullable.sql
evidence: CODE-CHECKED
status: superseded
created: 2026-11-05
verified: 2026-11-05
---
Setting scrooner.slot_writer='on' only lets a writer PAST the 0113 guard; it does not protect what it wrote. Without analytics.slot_protected_cell rows for the written (company, concept, period) keys, the nightly mapper / conflict-fill / derivation stages can overwrite or re-insert old values the same evening (seen on the CFO/buyback applies 2026-10-31; caught again in the FSN cohort write review 2026-11-04, fixed in cell_loader --protect, bc6ab31). Protect per cell, not via analytics.company_value_owner (0119), which freezes every family of the company. slot_protected_cell.value is nullable in production since 0115 (2026-10-31): reasoned blanks can be protected with value null; no new migration is needed. Before-images must include slot_protected_cell so a restore puts earlier protection back.

[2026-11-22 curator] SUPERSEDED (merged) into cell-writes-to-canonical-fact-must-pass-protect-or-the-night: same rule, text merged
