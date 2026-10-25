---
id: replay-inputs-must-come-from-one-accession-and-identity-tole
title: Replay inputs must come from ONE accession, and identity tolerances must be the filer's rounding unit, never a percentage
kind: rule
tags: replay, restatement, tolerance, bs-totals, same-accession
paths: pipeline/scripts/slot_records/bs_replay.py @ 68ed251; data-team/strategy/team/VERIFY-BS-TOTALS-V0-2026-10-24.md
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Verifier BS-v0 class 5 (2026-10-24): picking each tag's 'best' copy independently (distinct on tag+date, authoritative first) silently MIXES filings - DVN 2018-03-31 got its ARO member from the Q1-2019 10-Q while everything else came from the original, and the 14M error TIED inside a 0.05% percentage tolerance; BRKR tied on a restated FY2016 copy while the FY2015 10-K prints a different total. Standing rules: (1) every term of a computed cell comes from ONE accession - the filing whose period_of_report IS the instant, else the accession covering the most member tags; (2) a cross-check tolerance is the FILER'S ROUNDING UNIT (largest power of ten dividing the member values, capped at 1e6), never a percentage - 0.05% of a 30B balance sheet is 15M of invisible error. Related same-day rules: calc-graph ROOTS for subtotal dedup (label-run heuristics swallowed T's standalone 134.6B LTD line); no cal -> hold, never raw-sum; truncate the face zone at the filer's closing total (re-rendered rows after it double count).
