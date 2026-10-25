# Verify: BS totals V3 (origin/work/scrooner-25/slot-records 133cda9), 2026-10-25

Verifier 2. Method as V2: read-only copy of the branch's `bs_replay.py` with a per-instant dump (reproduced 728 ties, 0 gaps, 123 needs_instance_reader, 1 not computable, 4 member-blank-confirmed; 14/16 anchors; one connection, 20s), then the balance-sheet R page of each cell's own accession (59 filings), face liabilities derived independently (printed "Total liabilities", else L&E total - total equity - printed mezzanine), mismatches read by hand. Seed random.Random(20261031). FILING-CHECKED unless marked.

## Result: GATE PASSES on this sample: 55 shown cells checked, 0 wrong; 0 false holds found. AWK shows no value.

| Set | Cells | Shown | Right | Notes |
|---|---|---|---|---|
| MCK formerly needs_instance_reader (2017-06-30..2020-03-31) | 12 | 12 | 12 | e.g. 2018-03-31 48,865 = 60,381 - 10,057 - redeemable NCI 1,459 (0000927653-18-000010 R4); the equity row "Other" is out of the liabilities sum now |
| ET 2016-03-31 (formerly custom member) | 1 | 1 | 1 | 49,678 = 72,765 - 23,039 - preferred units of subsidiary 33 - redeemable NCI 15 (0001276187-16-000165 R2) |
| Member blank in column, identity-confirmed | 4 | 4 | 4 | DVN 2018-06-30 16,311; 2018-09-30 11,274 (0001564590-18-027813 R4); 2018-12-31 10,380; ET 2018-03-31 53,407 |
| Borrowed calc graph records | 5 instants | 1 | 1 | BRKR 2024-12-31 3,991.5 = printed total; DVN 2024-06-30..2025-03-31 are needs_instance_reader (no value; the face gives 12,433 / 15,785 / 15,785 / 16,155, the replay's partial misses a custom lease line) |
| GE former gaps | 12 | 12 | 12 | all equal GE's printed consolidated Total liabilities (8 parsed automatically; 2019-06-30 255,980, 2019-09-30 233,856, 2020-06-30 221,233, 2020-09-30 219,522 read by hand on the same R pages as in V2); 0 identity gaps now |
| Random ties (15 companies, max 2 each, earlier sample cells excluded) | 25 | 25 | 25 | AJG x2, BRKR x2, BX x2, DIS x2, DVN, EMR, ET x2, FE x2, GE x2, KKR x2, MCK, NI, OXY x2, T, WMT x2 |
| AWK | 46 | 0 | n/a | all needs_instance_reader; no partial value leaks (the anchor path returns None) |

## Holds (all correct today)
123 needs_instance_reader: AWK 46 (custom Total long-term debt subtotal), TRGP 46 (custom noncurrent risk-management liability), DVN 30 (custom noncurrent lease line, incl. the 4 borrowed-graph instants), BRKR 2019-12-31 (custom deferred revenue noncurrent). Each needs a custom fact that companyfacts does not carry; the value is withheld, not guessed. BRO 2019-01-01 not computable (ASC 842 adoption column, not a balance-sheet date): correct.

## Residual risks (not defects in shown values)
- The member-blank rule relies on the identity tie; it accepted 4 cells, all right here. Keep it limited to standard members on face_sum records.
- Two equity readings are accepted by the identity (incl.-NCI total, or parent + NCI); a wrong face-sum could tie against a stray equity fact by coincidence. None seen in 55 cells.
- Untested: values once the instance reader fills AWK/TRGP/DVN/BRKR (re-verify those cells then); second reader.
