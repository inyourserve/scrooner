---
id: bulk-fsn-cell-writes-must-add-slot-protection-rows-in-the-sa
title: Bulk FSN cell writes must add slot-protection rows in the same transaction, or the nightly mapper silently reverts them
kind: gotcha
tags: fsn, write, nightly, slot_protected_cell, guard, canonical_fact
paths: pipeline
evidence: CODE-CHECKED
status: superseded
created: 2026-11-05
verified: 2026-11-05
---
Ritwik's review of the FSN write-safety branch (c67a6d2, 2026-11-04): the cohort loader wrote canonical_fact but added no slot_protected_cell rows or company_value_owner row, so the nightly refresh's old-mapper stages could overwrite every new FSN cell and quietly undo the write. Rule: any bulk write that replaces served values writes the per-cell protection (and owner) rows in the same transaction, removes them on restore, and has a DB test showing a nightly-style write is skipped. Related guards: the 0113 trigger and 0119 company_value_owner.

[2026-11-22 curator] SUPERSEDED (merged) into cell-writes-to-canonical-fact-must-pass-protect-or-the-night: same rule, text merged
