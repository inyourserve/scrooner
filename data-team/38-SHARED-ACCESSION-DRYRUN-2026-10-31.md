# Shared-accession (co-registrant) rule: full-population READ-ONLY dry-run, 2026-10-31

Rule: `entity.shared_accession_primary_filer@1` (`normalizer/shared_accession.py`), flag OFF.
Driver: `pipeline/scripts/shared_accession_dryrun.py` (one Postgres connection, `read_only`
session, storage/SEC fetches over HTTP threads; checkpoints per phase). Nothing was written.
Raw outputs: `38-shared-accession-dryrun/REPORT.json`, `38-shared-accession-dryrun/moves.jsonl`.
Evidence level: DATA-INFERRED (SEC submissions + companyfacts feeds, SEC submission headers);
no filing was opened by hand in this run.

## Headline

| | |
|---|---|
| Population scanned (latest submissions payload per `core.company`) | 5,284 CIKs |
| Accessions listed by 2+ registrants | 3,008 (10-K 209, 10-K/A 9, 10-Q 631, 10-Q/A 7, 8-K 2,032, 8-K/A 19, 144 61, DEF 14A 23, DEFA14A 16, 424B5 1) |
| Primary decided | 476 (header+prefix+payload 370, prefix+payload 80, header+payload 20, header+prefix 6) |
| Quarantined | 2,532 (non-periodic without payload evidence 2,151; one signal only 322; no evidence 59) |
| `core.filing` rows whose `company_id` would move to the primary | 476 (all 2009-2026 accessions) |
| `core.filing_registrant` rows that would be written | 7,368 (476 primary, 845 co_registrant, 6,047 quarantined; 0 with null company_id) |
| Carrier conflicts (payload carries facts but is NOT the primary) | 4 |
| SEC header fetched / unreadable | 857 / 453 (every miss is a 404 on `-index-headers.html`, 447 of them pre-2015 accessions) |

## The nine cohort companies with no financial data

All nine are the primary of every one of their combined 10-K/10-Q filings that carries a
companyfacts payload; their own payload already holds the facts and the Normalizer drops them
today (`skipped_no_filing`) because the filing row is owned by a subsidiary.

| Ticker | id | Accessions recovered (10-K / 10-Q) | Fact entries in own payload | Distinct (fy, fp, end) periods | Period-end range | Latest qualifying shared filing (registrant link) |
|---|---|---|---|---|---|---|
| ETR | 694 | 66 (16 / 50) | 31,166 | 587 | 2004-12-31 .. 2026-03-31 | 2026-07-31 |
| ES | 1008 | 59 (15 / 44) | 22,834 | 469 | 2008-12-31 .. 2025-04-30 | 2025-05-05 (see note) |
| SO | 1081 | 68 (17 / 51) | 27,435 | 442 | 2006-12-31 .. 2026-03-31 | 2026-07-30 |
| CMS | 1525 | 34 (8 / 26) | 13,532 | 231 | 2015-12-31 .. 2026-07-13 | 2026-10-27 |
| EIX | 1576 | 56 (14 / 42) | 20,675 | 426 | 2009-12-31 .. 2026-10-22 | 2026-10-29 |
| AEE | 2144 | 54 (13 / 41) | 21,759 | 381 | 2010-12-31 .. 2026-07-30 | 2026-08-03 |
| SRE | 2503 | 49 (12 / 37) | 26,599 | 398 | 2007-09-11 .. 2026-05-04 | 2026-08-06 |
| TXNM | 3562 | 61 (15 / 46) | 26,683 | 540 | 2005-06-30 .. 2026-04-24 | 2026-07-31 |
| CTVA | 5394 | 29 (7 / 22) | 14,219 | 252 | 2016-12-31 .. 2027-12-31 (a payload entry with a future `end`; not checked) | 2026-07-31 |

These nine are the ONLY companies that gain anything: every one of the 476 moving filings
belongs to one of them. Status: eight would leave `stale` (latest registrant filing within the
18-month threshold). ES's latest shared filing with a decided primary is 2025-05-05, which is
just outside 18 months; its later combined filings are among the quarantined (header 404 and
no agreeing second signal), so ES needs a look before the status flip is claimed.

## Who would LOSE data

Only four companies hold `core.fact` rows on a filing that would change owner, and each holds
exactly one filing: the latest combined 10-Q, which SEC's companyfacts attributes to the
subsidiary CIK while the submission header and the accession prefix both name the parent.

| Current owner | Accession | Filed | core.fact rows |
|---|---|---|---|
| Southern California Gas Co (1080) | 0001032208-26-000045 | 2026-08-06 | 543 |
| Entergy Arkansas, LLC (142) | 0000065984-26-000283 | 2026-07-31 | 467 |
| Southern California Edison Co (1079) | 0000827052-26-000059 | 2026-07-30 | 388 |
| Consumers Energy Co (1165) | 0000811156-26-000032 | 2026-10-27 | 374 |

These are the four carrier conflicts. Per the module's own filing-checked note (2026-10-26),
the facts are the parent's consolidated values filed under the subsidiary's CIK, i.e. the
subsidiary shows the wrong company's numbers today. With the flag ON the subsidiary's filing
lookup no longer resolves that accession (only the primary link is added), so on
re-normalization these rows are dropped from the subsidiary, which is the right direction.
The parent does NOT gain that quarter: its own payload does not carry the accession. Closing
that gap needs an explicit decision (attribute carrier-payload facts to the primary, or leave
the latest quarter blank with a reason) and a Verifier check against the filing; neither is
in this branch. The other six current owners (Georgia Power, NSTAR, CL&P, Ameren Illinois,
PNM, EIDP) hold zero facts on the moving filings.

## Other findings

- 10 of the 3,008 shared accessions have no `core.filing` row at all (none of their
  registrants normalized them); no impact.
- `signals_do_not_agree` (322) is mostly "one signal only": pre-2009 10-K/10-Qs with no
  companyfacts coverage and a 404 header, so only the prefix votes. No data behind them.
- Changes on this branch beyond the WIP: duplicate `rule_flags` import removed from
  `identity.py`; `Decision` now carries `header_first_filer` and the registrant upsert writes
  `header_first_filer_cik` (the migration-0100 column was never populated). Unit tests 14/14.

## Not done / next

- Nothing applied; flag stays OFF; `core.filing_registrant` still has 0 rows.
- Apply path needs a founder go, then: write registrant rows, re-own the 476 filings,
  re-run `normalize facts` for the nine (their payloads are already in storage), then
  `update-status`. Verifier draw on the recovered values before anything is served.

## Addendum 02:10 IST: header fetch fixed, ES resolved

The 2025-08 onward combined filings of Eversource (and 16 of CMS's) are submitted by a
filing agent (accession prefix 0001628280), so the `-index-headers.html` under the
prefix CIK folder does not exist (404). The same file under ANY registrant's CIK folder
answers 200 (checked live: `/data/72741/000162828025037369/...`, first FILER block
0000072741 Eversource, then NSTAR Electric, CL&P, PSNH). `shared_accession_dryrun.phase_c`
now tries the prefix folder, then each registrant's folder, and retries checkpointed
misses. Rerun from checkpoints (REPORT.json / moves.jsonl updated in place):

| | before | after |
|---|---|---|
| Primaries decided | 476 | 499 (header+payload 20 -> 43) |
| `core.filing` rows moving | 476 | 499 |
| ES filings recovered / periods | 59 / 469 | 65 / 509 |
| CMS filings recovered / periods | 34 / 231 | 50 / 342 |
| ES latest qualifying shared filing | 2025-05-05 | 2026-08-03 (leaves `stale`) |
| Header misses | 453 | 430, all pre-2015 accessions (the headers file does not exist for them) |
| Carrier conflicts / owners losing facts | 4 / 4 | unchanged |

Consequence: the before-image under `39-shared-accession-apply/before-image` (plan digest
9dcfcdde5c724bae, 476 moves) no longer matches the plan; `apply` refuses it by design.
The fresh backup taken just before apply replaces it.
