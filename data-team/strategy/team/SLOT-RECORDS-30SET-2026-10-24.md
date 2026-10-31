# Slot records, 30-company debt set: eras, replay vs lane 3 (scrooner-25, 2026-10-24)

> **REJECTED by the Verifier (same day, VERIFY-SLOT-RECORDS-30SET-2026-10-24.md) — read this before the numbers below.** 22 replay slot values wrong; 12 of the 126 "agreeing" cells wrong in BOTH slot and production (KO 4, ORCL 8 — both miss the same face line, so agreement proved nothing); "149 holds resolved" overstated by ≥17. Root causes (fixed in the same-day follow-up, see SLOT-RECORDS-30SET-V2): D1 the regex gate missed whole face lines (KO `NotesAndLoansPayable[Current]`, ORCL `LongTermNotesAndLoans`, AMD `LinesOfCredit`) — replaced by a face-coverage check (every debt-reading face line is a member or carries a recorded exclusion, else the record fails); D2 the non-authoritative fallback took an 8-K recast copy (GE 2021-12-31) — facts now restricted to periodic filings; D3 AMAT's custom AP+accrued+debt line entered as borrowing — combined AP lines are excluded with reason; the replay's silent zero for missing members is now a hard stop; the borrowings-only variant is dropped from verdicts (CVX 2022/LRCX artifacts). What the Verifier CONFIRMED: the CVX cluster (6/6) and the 8 fragment holds are right in the slot and wrong in production; slot right in 45 of 58 filing-read cells. Lesson (same as the 2026-10-17 vocabulary audit, now at line level): **a regex gate agrees with itself — only a coverage check against the filing's own face can say "nothing missed."**

Branch `work/scrooner-25/slot-records`. Read-only throughout: JSONL proposals, no migration, no DB writes; DB reads on one connection (replay ran before the 6-connection allowance arrived). SEC usage this stage ≈ 420 requests (47 FSDS quarterly zips streamed + 182 era-boundary cal fetches ×2 + 4 MetaLinks + 4 earlier), ≤4 req/s, one process, `SEC_USER_AGENT`; every download deleted; free disk never below 8 GB. Method: FSDS face fingerprints detect eras across all filings (cheap); the filer's calc linkbase is fetched only at era boundaries (the founder's gate, inverted for backfill).

## Scale results

**33 companies, 1,478 filings → 169 era records** (FSDS detected 182 face eras; adjacent eras with identical calc fingerprints re-collapsed). Median ~4 records/company for 12 years. One-era companies: INTC, JNJ, MRK, PG, PM, SPCX. Noisy: AMD 15, CAT 13, UNH 12 (frequent face reshuffles — real, each one a boundary filing on record). Every record carries members, classes with evidence, taxonomy era, fingerprint, and its evidence accession.

## Replay vs lane 3's before-images (323 cells evaluated, 2015+ window; 146 more pre-2015 cells out of window by I11)

| Verdict | Cells | Meaning |
|---|---|---|
| agrees_lease_inclusive | 115 | slot = production value (lease-inclusive perimeter) |
| agrees_borrowings_only | 11 | slot = production value (borrowings perimeter, LRCX) |
| **DISAGREES_with_lane3** | **194** | see decomposition below |
| lane3 blank, slot has value | 1 | |
| not computable / no covering record | 11 | SPCX (shell), GE edge, 4 COST cells |
| **Lane-3 holds resolved by a slot value** | **149** | of lane 3's value-to-blank holds, the slot composition produces a computable, evidence-backed value |

**Decomposition of the 194 disagreements** (by relative delta to the nearer slot variant):

| Class | Cells | Of which holds | Reading |
|---|---|---|---|
| < 0.5% | 54 | 0 | precision class: prod appears to carry rounded later-filed comparatives (the known latest-filing-wins defect) or ±issuance-cost deltas — likely slot wins, needs filing sample |
| 0.5–5% | 82 | 13 | composition deltas (e.g. WMT ~1.8%: lease-content treatment) — per-class rules, Verifier sample |
| > 5%, prod LOWER | 48 | 27 | **the target class: prod shows a fragment of the face debt** (MRK 2015: prod 2.3B vs face 26.4B; UNH 2015-12: 6.6B vs 31.9B; COST 2015: 1.3B vs 6.1B; PG 2015: 11.6B vs 30.3B; AMAT 2016: 0.4B vs 3.3B) |
| > 5%, prod HIGHER | 10 | 4 | slot may miss a member or prod includes op leases — listed for Verifier |

**CVX cluster (13 cells, all non-hold):** prod uses `LongTermDebt` (e.g. 22,700M at 2015-03-31), the slot's face tag is `LongTermDebtNoncurrent` (29,960M) — both facts exist, authoritative, same instant, 7.3B apart. Which is CVX's printed balance-sheet line is a filing question; flagged as the single highest-value Verifier read in this set.

**Named regression anchors:** ABBV 39/40 cells agree exactly (incl. 2022-03-31 = 73,474M class); PM 18/18 agree; KO's container line resolves (NotesAndLoansPayableCurrent era records; 2018–2019 cells agree to the dollar); LRCX shows the only borrowings-only-perimeter era (11 cells); AMAT 2010 and CVX 2014-09-30 are pre-2015, out of window by I11.

## Honest limits

- Verdicts are DATA-INFERRED (stored-facts arithmetic vs lane 3's stored before-images); only the Verifier's filing sample makes any class CONFIRMED. 7 of 323 cells needed non-authoritative fallback values (the is_authoritative gap already in triage).
- Era members come from each era's FIRST filing's cal; mid-era drift inside an FSDS-identical face is not re-checked (the Verifier's earlier 6-mid-era sample found none).
- Operating leases are excluded from both variants by the standardization card; if lane 3's lease_inclusive included them anywhere, part of the 0.5–5% class is definitional, not defect.

## Files

`pipeline/scripts/slot_records/`: `fsds_debt_pre.py` (lean FSDS BS extractor), `era_detect.py`, `assemble30.py`, `replay30.py`, `results/thirty_debt_records.jsonl` (169 records), `results/replay30_report.json` (all 323 verdicts, per-cell), `results/lease_facts_33.csv` (evidence input).

## Proposed next

1. Verifier sample: the CVX tag-pair, 6–8 of the prod-much-lower holds, 4–6 of the <0.5% precision cells.
2. On pass: migration (`company_slot_record`, next free number in doc 53), certification I12, resolve.py wiring — debt family first, then D&A and capex via the same FSDS-era + boundary-cal machinery (it is family-generic except the tag regexes).
