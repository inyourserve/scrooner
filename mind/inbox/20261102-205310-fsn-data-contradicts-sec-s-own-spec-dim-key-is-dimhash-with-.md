---
id: fsn-data-contradicts-sec-s-own-spec-dim-key-is-dimhash-with-
title: FSN data contradicts SEC's own spec: dim key is dimhash with 0x00000000 = none, iprx starts at 0, datp = ddate minus actual date in DAYS, dcml -32768 = nil value, coreg only when LegalEntity is the sole axis
kind: gotcha
tags: fsn, spec, num, dim, coreg, datp
paths: data-team/fsn/FSN-GUIDE.md
evidence: DATA-INFERRED
source: FSN 2025q3 + 75 other sets, 101 CIKs; spec https://www.sec.gov/files/aqfsn_1.pdf
created: 2026-11-02
verified: 2026-11-02
---
Measured 2026-11-02 on real rows. (1) dim.tsv key column is 'dimhash' (num/txt call it dimh); no-dimension key is 0x00000000, not '0'. (2) iprx is 0-based; iprx 0 is the highest-precision copy (CAT TreasuryStockSharesAcquired 4,578,023 dcml INF vs 4,600,000 dcml -5); 195 of 7,533 multi-iprx dimn=0 groups differ in value. (3) datp is in days and = ddate - actual: AMD 2024-12-28 -> 20241231 datp +3; HD 2025-08-03 -> 20250731 datp -3 (spec says fraction, opposite sign). sub.period is rounded the same way; PepsiCo Q2 ending 2025-06-14 -> ddate and period 20250531 (previous month). (4) dcml 32767 = INF exact; dcml -32768 rows have an EMPTY value (nil), 381/381 in 2025q3. (5) coreg is set only for dimn=1 LegalEntity facts (NEE FPL Assets); LegalEntity plus another axis has coreg empty, so dimn=0 is the filter that matters. (6) pre.stmt can be 'SI' (ABT equity) or 'UN' for a real equity statement (PLD capital, MPC); FSN pre also carries note rows with stmt empty. (7) cal 'negative' is +1/-1, never boolean. Full list: data-team/fsn/FSN-GUIDE.md section 10.
