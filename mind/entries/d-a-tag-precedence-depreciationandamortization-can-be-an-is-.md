---
id: d-a-tag-precedence-depreciationandamortization-can-be-an-is-
title: D&A tag precedence: DepreciationAndAmortization can be an IS sub-line (Kura 448K vs CF 14,046K)
kind: lesson
tags: d_and_a, tag-precedence, mapper
paths: pipeline/src/scrooner_pipeline/mapper/expanded_concepts.py
evidence: FILING-CHECKED
status: active
source: R7 verifier 2026-10-21
created: 2026-10-21
verified: 2026-10-21
---
Mapper ranks DepreciationAndAmortization p1 over DepreciationDepletionAndAmortization p2. Kura 0001193125-25-269773 R4/R6 and Starbucks 0000829224-25-000114 R3/R5 tag an IS sub-line with DA while the CF total is DDA. FSDS 2025q4: 137 of 394 filing-periods with both tags differ. Anchor D&A to the CF total.
