---
id: mapper-dedup-majority-resolver-py-ca9f8d
title: `mapper/dedup_majority_resolver.py`
kind: gotcha
tags: pipeline
paths: pipeline/CLAUDE.md
evidence: DOC-CITED
source: pipeline/CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
(`resolve-dedup-holes`): where Stage 2e correctly-by-design left a concept with zero authoritative facts over a trivial cross-filing disagreement, a majority vote across raw facts (with a stock-split-aware reconciliation path) fills the `_resolved` concept — never overrides a value `resolve()` already found.
