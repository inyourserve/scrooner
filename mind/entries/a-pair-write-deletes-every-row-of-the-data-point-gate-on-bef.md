---
id: a-pair-write-deletes-every-row-of-the-data-point-gate-on-bef
title: A pair write deletes every row of the data point: gate on before-image keys by duration class, or values vanish
kind: gotcha
tags: canonical_fact, done-gate, fsn-write, ytd
paths: pipeline/src/scrooner_pipeline/fsn_store/pilot.py, pipeline/src/scrooner_pipeline/normalizer/cell_loader.py
evidence: DATA-INFERRED
status: active
created: 2026-11-11
verified: 2026-11-22
---
FSN top-100 write 42649721096 (2026-11-09) switched MDT and left 252 previously valued keys with no row: cells load replaces a (company, data point) pair whole, but select emitted only Q/FY. 6M/9M YTD rows, multi-year buyback periods, and DPS (outside the template, so ungated) were deleted unseen. The old hold_guard called any period under 300 days a Q, so a 9M row matched the Q3 cell ending the same day. Fix on main (6db6f74): expected keys = calendar ∪ before-image valued keys, matched by real duration class (Q/H1/9M/FY/MULTI/I); a valued->no-row key holds its pair; the C2 column must be 0. Also: a fiscal-label-bound row kept (fsn_end, fsn_end) as its key, so every FSN Q reason was stored with start=end (fixed in bind_periods). Check a write by diffing the before-image against live per key, not by row counts.

[2026-11-22] Merged 2026-11-22 from the MDT entry: MDT dividends_per_share before-image held 70 valued rows, the write left 22 (48 DPS values after 2018-07-27 lost); the done gate missed it because its expected-key calendar omitted those keys. Rule: expected keys = calendar UNION every before-image valued key; C2 'valued -> no row' column must be 0 before dispatch (found by Ritwik, run 42649721096).
