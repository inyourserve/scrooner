---
id: derived-ytd-subtraction-quarters-same-vintage-by-copies-miss
title: Derived YTD-subtraction quarters: same-vintage-by-copies misses cross-filing and recast-perimeter pairs
kind: gotcha
tags: q4, derivation, vintage, is_core
paths: 
evidence: DATA-INFERRED
created: 2026-11-01
verified: 2026-11-01

unmerged_paths: pipeline/scripts/slot_records/is_emit.py
status: superseded
---
The unrestated_single_value rule only checks that copies of the SAME key agree, so Q = YTD_n - YTD_(n-1) can still pair a later 10-K's comparative full year with the original 10-Q's 9M (inputs filed 2+ years apart), or a 10-K recast for discontinued operations with an unrecast 9M (Teleflex 1100 Q4 2025 revenue -401.9M). is_core 77f5846a had 7 negative derived revenue quarters and 105 cross-vintage pairs. Guard (is_emit b9f3c4f): defect mixed_vintage when accession years differ by 2+ or revenue/COR YTD decreases; the perimeter hold applies to all data points of that quarter. Cheap check on any derived-cell file: count negative derived revenue and input_accessions years apart.

[2026-11-01 curator] SUPERSEDED by data-team/strategy/FSN-STORE-DESIGN-2026-11-01.md: the per-lane unrestated_single_value rule and is_emit mixed_vintage guard are retired (design section 8); quarter derivation is now SAME_BASIS(A,B,L) with a witness (design section 5). The Teleflex case is kept as the design's worked example.
