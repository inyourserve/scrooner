---
id: scripts-find-period-gap-candidate-tags-py-33cd6c
title: `scripts/find_period_gap_candidate_tags.py`
kind: gotcha
tags: pipeline
paths: pipeline/CLAUDE.md
evidence: DOC-CITED
source: pipeline/CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
/ **`scripts/find_concept_gap_clusters.py`** — the two reusable tools for finding a real tag-mapping fix: the first asks "what unmapped tag is present at a concept's specific missing periods," the second asks "what do companies missing a concept *entirely* share." Both only ever produce a *lead* — every candidate still needs a live coexistence check against real companies before shipping.
