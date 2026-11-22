---
id: cell-proof-rows-can-predate-a-write-check-proved-at-against-
title: cell_proof rows can predate a write: check proved_at against the write time before reading DISAGREE as post-write proof
kind: gotcha
tags: cell_proof, release, post-write, verification
paths: data-team/strategy/THE-PLAN.md
source: commit 6f27779b5 (ruling addendum, file not on main)
evidence: DATA-INFERRED
status: active
created: 2026-11-10
verified: 2026-11-10
---
analytics.cell_proof keeps rows from earlier proof runs. After the 2026-11-09 top-100 FSN write (run 42649721096, MDT 3639 the only company written, 779 protected cells at 16:18 UTC), MDT showed 995 PROVEN / 105 DISAGREE, but every DISAGREE had proved_at 2026-11-02, so no post-write proof had run (condition C4 unmet). Before reporting post-write proof, filter on proved_at > the write's rule_run started_at, and join to analytics.slot_protected_cell (rule_id like 'fsn.%') to restrict to served FSN cells.
