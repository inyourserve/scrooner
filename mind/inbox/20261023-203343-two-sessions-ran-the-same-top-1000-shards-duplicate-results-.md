---
id: two-sessions-ran-the-same-top-1000-shards-duplicate-results-
title: Two sessions ran the same top-1000 shards: duplicate results need a winner table before use
kind: lesson
tags: top1000, shards, process
evidence: DATA-INFERRED
source: data-team/strategy/team/DUPLICATE-SHARD-RECONCILIATION-2026-10-23.md
created: 2026-10-23
verified: 2026-10-23
---
38 shards (S020-S057) exist in two independently produced versions: upstream on origin/main and results/session-7b-versions/. By a mechanical count (distinct accessions + FILING-CHECKED labels) upstream wins 38 of 38, but that measures effort not correctness. Before quoting either as evidence a Verifier should sample disagreements. Check git log origin/main for existing results/S###.md before launching a shard run.
