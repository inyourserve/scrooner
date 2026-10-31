---
id: stored-derived-eps-quarters-stay-displayed-after-the-family-
title: Stored derived EPS quarters stay displayed after the Family B deriver gate; Family C retires them
kind: lesson
tags: eps, per-share, derived, retirement
paths: pipeline/src/scrooner_pipeline/mapper/derived_row_retirement.py
evidence: DATA-INFERRED
created: 2026-10-31
verified: 2026-10-31
---
Family B (review/family-b-split) only STOPS new per-share derivations. Cohort v1.1 live count 2026-10-31: about 5.3k basic and 5.3k diluted EPS quarter cells have an is_derived source (97% Q4), at about 920 companies; DPS has 4.3k (split/dividend lane); shares_outstanding has 0. Family C retire.derived_per_share_cells@1 (work/per-share/eps-never-derive ad9d622) replaces each from the cell's OWN concept mapping (BasicAndDiluted feeds both) or removes it with the Item 302(a) era reason; split re-based *_resolved cells go to review. Migration 0098 objects are already live, so no migration is needed.
