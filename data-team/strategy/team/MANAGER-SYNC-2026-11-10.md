# Manager sync: cloud Dhairya ↔ Mac Dhairya (2026-11-10)

From the cloud manager session (session_01GLmSDyzegqZw4JqC91z7XH) to the Mac manager session (session_01GLmSE2WKhNnSe6DQe8JSgT). NOW.md stays the single source of truth; this file is the hand-off detail. The cloud session can send to the Mac session (trust granted 2026-11-09); the Mac session replies by writing here or in NOW.md.

## Correction
Run 42649721096 (top-100, code 1beb755) DID write: company_id 3639 (MDT), 779 cells protected 2026-11-09 16:17:59–16:18:07 UTC (analytics.slot_protected_cell, read 2026-11-10). The cloud manager reported "0 written"; that was from a 16:14 UTC partial snapshot. Every other company failed the per-company gate.

## Proposed split (to avoid two owners per job)
- **Mac manager owns production operations:** writes (pipeline-fsn-write.yml), cell_proof on MDT and after each write (incl. Ritwik N2), the C7 cohort dry run, the C2 table, and getting Ritwik's clearance.
- **Cloud manager owns the cloud build sessions** and lands their branches: FSN nightly incremental (session_01GLmSDzsJCP8Q8R6eXToEFg), SEC/FSN Tag Expert (…zfptGrTXZu6qg8aL3), Mapping & derivation builder (…z5HjxgJE8DX49bNSg), Release prep (…E3yJhPu25eryM5Zsen), Cash-flow lane (…z8UEMvBQnmo9n7qHU), Balance-sheet lane (…E3bN5dZdXDa76fFLp2), Certification lead (…E1SAPUBpeYGyM6GQmA), Verifier (…E2XmWDLTqKZZnJor17), Ritwik (cloud) (…z8UUfjBrVex2j8ugb).
- If you disagree, edit this section; the cloud side follows NOW.md.

## Hand-offs to the Mac side
1. **Per-pair done gate:** branch `work/fsn/done-gate-pairs` @ 9e80070e was built by the cloud balance-sheet lane to Ritwik's ruling plus the founder's no-fallback decision (reasonless gaps become reasoned blanks: `filing_not_in_store`, `hybrid_gap_unresolved` + cause; C2 is a report). Engineering takes it from here as you said; the cloud lane stops pushing to it and moves to PR #5 B1/B2.
2. **Ruling:** Ritwik (cloud) ruling + addendum on `review/ruling-done-gate-c4-2026-11-09` (a30f057, 6f27779): C3 withdrawn, C2 a report; N1 hybrid blanks written as defects; N2 cell_proof DISAGREE becomes a blank, not an old value; N3 debt, total liabilities and DPS stay off the write list.
3. **Founder words in the cloud manager session (2026-11-09):** ~22:10 IST "Yes approved" (per-(company, data point) writes on Ritwik's conditions, plus top-100 and 1,000 writes once Ritwik clears the dry run); ~22:30 IST "No fallback. Everything is the hybrid (fcn + sec)"; ~23:05 and ~23:10 IST "Approved" again to the same write sentence. Ritwik (cloud) says the founder's words must be typed in the approver's session; whoever dispatches should confirm that with the founder.
4. **2026m10 FSN set:** extraction dispatched 2026-11-09 ~17:35 UTC, `pipeline-fsn-extract-predecessors.yml` on ref `work/fsn/store-coverage`, destination=cohort, sets=2026m10, apply=true (bucket only, no DB). Release prep confirms the counts. Include it in the C7 dry run: the data chief found the missing latest 10-Q (store ends at 2026m09) is the #1 blocker (~2,570 pairs, 319 companies).
5. **PR #4 / PR #6** (cash-flow gaps; derived total liabilities): both Verifier PASS; PR #4 is getting the CSCO FX-twin fix and rebase. They should be in the C7 dry run.
6. **Open review fixes:** PR #5 B1 (the guard fails open on a GitHub API error) and B2 (missing CI test), cloud balance-sheet lane; the sector-template seed (Verifier FIX: EQH/ACT insurer, INVH/TRNO REIT, MTB/BNY overrides, default inputs) and the ladder (6 holes), certification lead.
