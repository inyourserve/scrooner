# Verify: shared-accession apply plan, 23 new moves (origin/work/engineering/shared-accession-apply 9a1b4f7), 2026-11-01

Seed 20261101. File: data-team/38-shared-accession-dryrun/moves.jsonl (499 moves; 23 not in the a8cd1f9 plan: ES 6, CMS 16, QSR 1). Evidence class: FILING-CHECKED (cover R page and balance-sheet R pages; parent payload from SEC companyfacts). Verifier 2 (scrooner-bc). Extends VERIFY-SHARED-ACCESSION-2026-10-31.md.

## Result
**Ready for apply: YES.** 8 of 8 drawn new moves right.
- 7 of 7 with parent payload facts: the parent is the first registrant on the cover, and its own companyfacts `Assets` for the accession equals the parent's consolidated (first) balance-sheet block.
- QSR: a DEF 14A proxy co-filed by Restaurant Brands International Inc. (1618756) and its limited partnership (1618755). Owned today by the LP (company 3706, 0 facts). Its cover names only the Inc. The move is right and carries no data.

## Sample
`random.Random(20261101)`: 5 of the 6 Eversource moves, then 3 of the other 17.

## Cell table
| Accession | Parent | Form / instant | Parent payload Assets | Parent block on face | Verdict |
|---|---|---|---|---|---|
| 0001628280-26-051906 | ES | 10-Q 2026-06-30 | 63,415,743K | 63,415,743K (CL&P 17,379,151K; NSTAR 20,757,487K; PSNH 7,234,180K) | right |
| 0001104659-14-034149 | ES (Northeast Utilities) | 10-Q 2014-03-31 | 28,096,870K | 28,096,870K | right |
| 0001628280-26-032278 | ES | 10-Q 2026-03-31 | 64,707,601K | 64,707,601K | right |
| 0001628280-25-037369 | ES | 10-Q 2025-06-30 | 60,956,100K | 60,956,100K | right |
| 0001628280-26-008461 | ES | 10-K 2025-12-31 | 63,786,711K | 63,786,711K | right |
| 0001104659-14-073231 | CMS | 10-Q 2014-09-30 | 18,381M | 18,381M (Consumers 16,919M) | right |
| 0001104659-17-006823 | CMS | 10-K 2016-12-31 | 21,622M | 21,622M (Consumers 19,946M) | right |
| 0001193125-26-171760 | QSR | DEF 14A 2026-04-23 | none (proxy) | cover: Restaurant Brands International Inc. only | right, no data |

## Findings for the builder
1. The ES header fix works: the 2025-2026 Eversource 10-Q/10-Ks now resolve to ES. This should also clear the ES "stale" status note in the 2026-10-31 report.
2. The plan moves a non-periodic filing (DEF 14A) when header and payload agree. That is fine for ownership; it adds no financial data.

## Requests and disk
SEC requests: 39. One DB read for the QSR filing owner.

## Untested scope
15 of 23 new moves not drawn. The other 476 were covered by the 2026-10-31 verdict (20 drawn).
