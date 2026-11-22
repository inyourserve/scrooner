---
id: a-data-point-write-must-cover-every-key-the-before-image-had
title: A data-point write must cover every key the before-image had valued: MDT's FSN write silently dropped 48 DPS values
kind: gotcha
tags: fsn, write, done-gate, before-image, reasonless, C1
paths: pipeline
evidence: DATA-INFERRED
status: superseded
created: 2026-11-10
verified: 2026-11-10
---
Run 42649721096 (2026-11-09) wrote MDT dividends_per_share: the before-image held 70 valued rows, the write left 22 and gave the other 48 (after 2018-07-27) neither a value nor a blank reason. The per-company done gate passed MDT because its expected-key calendar did not include those keys. Rule: expected keys for a written (company, data point) = the calendar UNION every key the before-image had valued; the C2 table needs a 'valued -> no row' column that must be 0 before any dispatch. Found by Ritwik (scrooner-3d) comparing the before-image artifact with live rows after a Verifier pass on the 22 served cells.

[2026-11-22 curator] SUPERSEDED (merged) into a-pair-write-deletes-every-row-of-the-data-point-gate-on-bef: same incident and rule, text merged
