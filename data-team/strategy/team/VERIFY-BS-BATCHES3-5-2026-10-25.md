# Verify: BS batches 3-5 (origin/work/scrooner-25/slot-records 1751333), 2026-10-25

Verifier 2. All 620 manifest instants (30 companies; 511 reading-B "taxonomy total covers", 109 reading-A "cal roots") plus the 33 batch-2 TMUS/ALB manifest instants, each checked on the balance-sheet R page of its own accession (653 filings, one fetch process at 4 req/s). Face liabilities derived independently: printed "Total liabilities", else L&E total - total equity incl. NCI - printed mezzanine lines. FILING-CHECKED.

## Result: GATE PASSES. 620 of 620 shown values equal my face-derived liabilities. No case where the identity ties but the face disagrees: the tying reading never picked a coincidental wrong sum in this sample.
- 591 matched automatically; 29 needed a manual read because my reader missed a line, and all 29 match on the face:
  - INTC 2023-2026 (10 cells): non-controlling interest printed after "Total stockholders' equity" (e.g. 2023-04-01: 27,393 + 48,836 + 3,831 + 4,840 = 84,900, NCI 2,344; 0000050863-23-000028). In 0000050863-26-000079 the filer's total-equity row (124,989) carries the label "Accumulated other comprehensive income (loss)" - a rendering/label error on the face, harmless to the slot.
  - CAKE 2020-06-30, 2021-03-30: Series A convertible preferred (204,079K; 213,485K) in mezzanine (0001104659-20-089689 R2).
  - CSL 2025-2026 (6 cells): "Contract liabilities" 326.0M etc. is a liability line between long-term debt and deferred taxes (0000790051-25-000097).
  - DDS 2021-07-31: "Subordinated debentures" 200,000K (0000028917-21-000196).
  - CDW 2015-12-31 (5,659.4 = 1,887.3 + 3,772.1), SYK 2017-12-31 (22,197 - 9,980), TW 2019-12-31 (printed 502,589K): multi-column layouts.
- Batch-2 TMUS (6) and ALB (1) manifest instants: still withheld (no value shown); the face values are derivable (e.g. TMUS 2018-03-31 12,357 + 36,771 = 49,128M), as reported in VERIFY-BS-BATCH2.

## Note
Reading B (taxonomy totals) relies on the identity tie to be safe. In this sample every tie was also a face match, but the identity alone cannot detect two errors that cancel; keep the face-line coverage check alongside it for new layouts (multi-registrant filings, partnerships with both PartnersCapital and NCI lines).
