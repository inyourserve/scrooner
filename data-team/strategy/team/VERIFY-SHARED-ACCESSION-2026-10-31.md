# Verify: shared-accession primary filer (work/data-engineer/shared-accession a8cd1f9), 2026-10-31

Seed 20261031. Files: data-team/38-SHARED-ACCESSION-DRYRUN-2026-10-31.md, 38-shared-accession-dryrun/moves.jsonl (476 moves). Claimed: 476 filings move to the nine parents; 4 subsidiaries lose one combined 10-Q each. Evidence class: FILING-CHECKED (cover page R page and balance-sheet R pages of each filing; parent payload from SEC companyfacts). Verifier 2 (scrooner-bc).

## Result
**Ready for apply review: YES.**
- Moves: 19 of 20 drawn filings confirmed. The parent's own companyfacts `us-gaap:Assets` for that accession equals the parent's consolidated block (first block) on the filing's balance sheet, and the parent is a registrant on the cover. The 20th (TXNM 0001108426-26-000048, Q2 2026 10-Q, basis header+prefix) has no parent payload facts for the accession. The parent is first registrant on the cover, but the move brings no data. Not wrong, just empty.
- Losing subsidiaries: 4 of 4 store the parent's consolidated numbers today, so dropping them removes wrong values.
- None of the 4 subsidiaries is in cohort v1.1 (company ids 142, 1079, 1080, 1165 absent from cohort_v1_1_proposal_2026-10-24.csv); all 9 parents are.

## Method
For each drawn move: parent CIK -> SEC companyfacts -> the `Assets` fact whose `accn` is the moved accession (latest instant). Filing: FilingSummary -> cover R page (registrant CIKs) and every balance-sheet R page; total assets at that instant, by block. A move is confirmed when the parent value equals the parent's consolidated block. Losers: stored `core.fact` Assets on the losing filing vs the same pages.

## Sample
`random.seed(20261031); random.sample(moves sorted by accession, 20)`: SO 2, ES 4, TXNM 4, SRE 2, ETR 3, EIX 2, CMS 1, AEE 1, CTVA 1. Eras 2012 to 2026, 10-K and 10-Q.

## Cell table (moves)
| Accession | Parent | Instant | Parent payload Assets | Parent block on face | Subsidiary block(s) | Verdict |
|---|---|---|---|---|---|---|
| 0000092122-12-000113 | SO | 2012-06-30 | 60,897M | 60,897M | 18,554M; 28,078M; ... | right |
| 0000072741-25-000007 | ES | 2024-12-31 | 59,594,529K | 59,594,529K | CL&P 16,839,845K; NSTAR 18,075,248K; PSNH 6,641,941K | right |
| 0001108426-12-000091 | TXNM | 2012-09-30 | 5,260,207K | 5,260,207K | 4,073,331K; 1,060,062K | right |
| 0001032208-24-000007 | SRE | 2023-12-31 | 87,181M | 87,181M | SDG&E 29,185M; SCG 24,266M | right |
| 0000092122-21-000064 | SO | 2021-06-30 | 125,907M | 125,907M | 31,691M; 47,625M; ... | right |
| 0000065984-19-000257 | ETR | 2019-06-30 | 50,565,745K | 50,565,745K | 10,858,573K; 20,895,071K; ... | right |
| 0000827052-17-000033 | EIX | 2016-12-31 | 51,319M | 51,319M | SCE 50,891M | right |
| 0000065984-15-000145 | ETR | 2015-03-31 | 46,377,533K | 46,377,533K | (not parsed) | right |
| 0000072741-20-000024 | ES | 2020-09-30 | 43,507,345K | 43,507,345K | 13,083,956K; 12,386,055K; 4,499,305K | right |
| 0000086521-14-000054 | SRE | 2014-09-30 | 38,982M | 38,982M | 15,975M; 9,954M | right |
| 0000811156-26-000004 | CMS | 2025-12-31 | 39,941M | 39,941M | Consumers 37,091M | right |
| 0000072741-22-000026 | ES | 2022-06-30 | 49,916,240K | 49,916,240K | CL&P 14,306,289K; NSTAR 14,093,503K; PSNH 4,880,871K | right |
| 0001002910-18-000119 | AEE | 2018-03-31 | 26,079M | 26,079M | 14,040M; 10,471M | right |
| 0000072741-14-000040 | ES | 2014-06-30 | 27,790,445K | 27,790,445K | 8,948,758K; ... | right |
| 0000065984-24-000012 | ETR | 2023-12-31 | 59,703,396K | 59,703,396K | 2,097,975K; 29,109,470K; ... | right |
| 0001755672-24-000013 | CTVA | 2024-03-31 | 43,625M | 43,625M (Corteva block) | EIDP 44,371M | right (cover CIKs not parsed; payload is Corteva's own) |
| 0001108426-14-000120 | TXNM | 2014-06-30 | 5,604,192K | 5,604,192K (hand-read; cover lists PNM Resources first) | - | right |
| 0000827052-24-000055 | EIX | 2024-06-30 | 84,818M | 84,818M | SCE 84,299M | right |
| 0001108426-12-000014 | TXNM | 2011-12-31 | 5,204,613K | 5,204,613K | 4,095,287K; 1,037,445K | right |
| 0001108426-26-000048 | TXNM | 2026-06-30 | none in payload | 12,507,922K | PNM 7,877,922K | no facts move (empty) |

## Losing subsidiaries (stored facts today)
| Subsidiary | Accession | Stored Assets | Parent block | Subsidiary's own block | Verdict |
|---|---|---|---|---|---|
| SoCalGas (1080) | 0001032208-26-000045 | 115,281M (2026-06-30) | Sempra 115,281M | 27,927M | parent's number: wrong today |
| Entergy Arkansas (142) | 0000065984-26-000283 | 79,002,618K | Entergy Corp (first block) 79,002,618K | next block 17,638,405K | parent's number: wrong today |
| SCE (1079) | 0000827052-26-000059 | 96,171M | Edison International 96,171M | 96,018M | parent's number: wrong today |
| Consumers Energy (1165) | 0000811156-26-000032 | 41,683M (2026-09-30); also 39,941M at 2025-12-31 = CMS 10-K | CMS 41,683M | 39,204M | parent's number: wrong today |
These four filings feed 154 / 164 / 172 / 110 canonical_fact rows under the subsidiaries today.

## Withheld cells (avoidable holds)
Not applicable (ownership move only). Note: after the flag, the four parents' latest quarter stays blank, because their own payload does not carry the accession (the report's open decision).

## False holds
None.

## Findings for the builder
1. Confirmed: in combined filings, the parent's companyfacts payload is the parent's own consolidated figures. The move is right.
2. TXNM 0001108426-26-000048 moves with no parent payload facts. Like the 4 carrier conflicts, its facts sit elsewhere or are not in companyfacts yet. Include it in the "latest quarter blank with a reason" decision, not in the recovered count.
3. Reader gotcha: in Sempra, Eversource, CMS and Edison combined filings, a SUBSIDIARY-titled balance-sheet R page also prints the parent's total in its first column (e.g. "CONDENSED BALANCE SHEETS - SoCalGas" carries 115,281M and 27,927M). Never take the first column of a subsidiary page as the subsidiary's value.
4. Entergy's combined balance sheet is one R page with seven registrant blocks labelled only by XBRL standard labels ("Assets, Total"). Block order (Entergy Corp first) is the only signal on the page.

## Requests and disk
SEC requests: 105 (9 companyfacts JSON, 96 filing pages). Nothing saved to disk except this file. One DB read (single connection, 60s timeout).

## Untested scope
456 of 476 moves not drawn; only total assets compared (no income-statement check); the 2,532 quarantined accessions and ES's stale-status note were not checked; CTVA's future-dated payload entry not checked.
