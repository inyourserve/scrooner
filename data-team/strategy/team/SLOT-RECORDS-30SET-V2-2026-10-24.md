# Slot records 30-set V2: rebuilt after the Verifier rejection (scrooner-25, 2026-10-24)

Branch `work/scrooner-25/slot-records`. Implements all Verifier fixes (D1–D3 + replay rules) from VERIFY-SLOT-RECORDS-30SET-2026-10-24.md; supersedes the V1 numbers (see the REJECTED header on SLOT-RECORDS-30SET-2026-10-24.md). Read-only throughout; SEC this rebuild ≈ 500 requests (47 FSDS re-stream — a self-inflicted re-download, lesson logged: derived extracts now persist until a family closes — plus ~200 boundary fetches, partly reused from the parked family downloads); campaign total ≈ 1,420 of the 1,500 cap.

## What changed

1. **D1 — face coverage check replaces the regex gate.** Candidates are detected wide (tag AND printed label); every candidate must be a member or carry a recorded exclusion reason (`excluded_combined_nondebt`, `excluded_asset_side`, `excluded_equity_reserve`, `excluded_structural`); anything unclassified fails the record (`coverage_clean=false`). The previously missed lines are now members: KO `NotesAndLoansPayableCurrent`, ORCL `LongTermNotesAndLoans`, AMD's era lines.
2. **D2 — facts restricted to periodic filings** (10-K/10-Q): GE 2021-12-31 now reproduces the 10-K face 35,185M, not the 8-K recast 35,114M.
3. **D3 — combined AP lines excluded with reason** (AMAT custom line), asset-side label catches (finance receivables, leased assets) excluded with reason.
4. **Replay: missing member = hard stop; borrowings-only variant dropped from verdicts** (informational only).

## Results (173 era records, 33 companies, 1,478 filings)

- **coverage_clean: 172 of 173.** The one dirty record is deliberate: GE 2018-12-31, custom line `ge:ShortTermDebtAssumed` ("Short-term borrowings assumed by GE", Note 11) reads as debt on the face but is not a calc child of the Liabilities parents — a REAL composition question the coverage check surfaced; left for the Verifier, never silently classified.
- **Fixture suites: ALL PASS** — 8 class fixtures, 4 membership fixtures, 6 value anchors (MU 6,776M / 14,577M; ABBV 73,474M; GE 35,185M from the 10-K; ORCL 54,327M at 2016-11-30; KO membership). Two fixture periods were corrected during the run — both "failures" were transcription errors in MY fixture file, not engine errors: ORCL's cited accession 0001193125-16-797253 is the 2016-11-30 10-Q (the slot's 43,855M at 2016-05-31 is ORCL's correct FY2016 face: 3,750 + 40,105), and AMAT's combined line is on the face only 2015-07..2016-01 (eras which DO carry it as an exclusion). Flagged for the Verifier's awareness: FSDS shows era face tags for ORCL 2015 (`LongTermNotesPayable`) and AMD 2018 H1 (`DebtCurrent`) that differ from the rejection note's tag names for the same printed lines.

## Replay vs lane 3, V2 (same cells, stricter rules)

| Verdict | V1 | V2 | Why it moved |
|---|---|---|---|
| agrees_lease_inclusive | 115 | 98 | 12 fake agreements (KO/ORCL, both-wrong) now DISAGREE with the fuller slot; hard stops removed others |
| DISAGREES_with_lane3 | 194 | 217 | includes the former fake agreements — these are now candidate production defects |
| holds resolved by slot | 149* | **145** | *V1 number was overstated (Verifier: ≥17 fake); V2's 145 are computed with full coverage + hard stops |
| not_computable (missing member / uncovered) | 2 | 7 + 1 | honest hard stops instead of silent zeros |

Disagreement decomposition (V2): **63 precision <0.5%** (rounded later-filed comparatives), **72 composition 0.5–5%**, **76 prod-shows-fragment >5%** (35 of them holds — grew from 48 because the fuller member sets expose more undercounts, e.g. KO's 13 cells), **6 prod-higher**. The CVX LongTermDebt-vs-LongTermDebtNoncurrent cluster stands as before (Verifier already confirmed slot right 6/6).

## Status

Ready for the Verifier's fresh seed. D&A/capex stay paused per Dhairya; their machinery will inherit the face-coverage check before any run. All verdicts DATA-INFERRED except where the Verifier's first pass already filing-confirmed them.
