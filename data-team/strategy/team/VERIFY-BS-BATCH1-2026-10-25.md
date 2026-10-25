# Verify: BS rollout batch 1 (origin/work/scrooner-25/slot-records c6dd9ff), 2026-10-25

Verifier 2. Each cell checked against the balance-sheet R page of its own accession (80 filings), face liabilities derived independently (printed "Total liabilities", else L&E total - total equity incl. NCI - printed mezzanine). FILING-CHECKED. Seed random.Random(20261105) for the 3-per-company picks.

## Result: GATE PASSES: 80 of 80 shown values checked are right.
| Company | Cells checked | Right | Layout |
|---|---|---|---|
| DUK (0001326160) | all 39 tie cells (incl. the 26 member-blank columns; the 6 not-computable cells show no value) | 39 | utility face-sum on a borrowed cal; e.g. 2016-03-31 10,891 + 38,232 + 32,645 = 81,768 (0001326160-16-000296 R4: L&E 121,709 - equity incl. NCI 39,941). The combined filing stacks the subsidiary registrants below; the consolidated block was used |
| JPM (0000019617) | 10 manifest instants (first, last, every boundary) | 10 | bank, printed total (e.g. 2015-03-31 2,341,284M, 0000019617-15-000318) |
| BAC (0000070858) | 2 manifest instants | 2 | bank, printed total |
| TRV (0000086312) | 9 manifest instants | 9 | insurer, printed total |
| PLD (0001045609) | 5 manifest instants | 5 | REIT (no current/noncurrent split); printed total |
| GE, EMR, WMT, T, VLO | 3 each (first, last, one random boundary) | 15 | as verified in V2/V3 |
51 cells matched via L&E - equity - mezzanine, 29 via the printed total. The 2 DUK cells my automated reader first flagged (2016-03-31, 2016-06-30) were my reader taking parent equity instead of the "including NCI" line; read by hand they match.

## Untested
DUK's 6 not-computable instants (are any of them false holds?); BAC has only 2 manifest instants, so its other 44 cells rely on the same printed-total rule; second reader.
