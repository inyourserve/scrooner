# Document-first reads, ranks 101-200 (Ritwik cloud), running totals

The numbers only, updated at each 10-company commit. Per-company files are `data-team/companies/reads/<TICKER>-docmap-2026-11-12.{md,csv}`.

| chunk | companies read | data points | value mismatches (printed vs companyfacts) | disagreements with my file | corrections to my exceptions file | corrections to the tag library |
|---|---|---|---|---|---|---|
| ranks 101-110 | 10 | 460 | 0 | 6 | 3 rows (SYK interest, SYK total liabilities, LOW operating income: latest-era map rows) | 0 |
| ranks 101-110, re-read with the shared tool (558f2f15) + hand checks | 10 | 380 | 0 | 6 machine errors corrected in checked rows | see the decisions file | 6 tool fixes proposed (NOTES-TAG-EXPERT-reads-101-110-2026-11-12.md) |

Hand checks on ranks 101-110:
- 67 rows hand-checked: every non-mapped row and every NOTE row.
- 30 mapped rows sampled. The disagreement rate is 1/30 = 3.3%, above 2%, so **reading has stopped** pending the Tag Expert's tool fixes.
