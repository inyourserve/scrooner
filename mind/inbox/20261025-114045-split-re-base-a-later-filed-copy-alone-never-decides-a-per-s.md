---
id: split-re-base-a-later-filed-copy-alone-never-decides-a-per-s
title: Split re-base: a later filed copy alone never decides a per-share cell; the period's original filing must agree
kind: lesson
tags: split, per-share, dps, restatement
paths: pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py
evidence: FILING-CHECKED
source: Verifier VERIFY-SPLIT-REBASE-1000-2026-10-24.md; branch work/period-engineer/split-rebase
created: 2026-10-25
verified: 2026-10-25
---
Verifier-1000: 13 of 14 other_changed cells were wrong because the pass took the latest copy (TRMB/DCI later 10-Ks shift comparatives by a year; XYL/TSCO/GLPI put the current dividend rate on a prior period; OHI -0.66, BWA 0, WTRG quarterly rate on FY, OGE annual on a quarter). Rules: require the original periodic copy to agree; never drop the original as a label shift (equal dividend rates in neighbouring quarters are normal) except a DPS rate on a longer context (LEA 9M 0.20); same-filing DPS checks; repeated same-ratio splits months apart are real unless the filings reverse (CPRT, AAON, HEI vs KR). Ship in phases: exclude other_changed from writes first.
