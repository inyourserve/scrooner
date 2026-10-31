# Split release 2: restated-copy candidates (FROZEN, not built)

`release2_restated_copy_candidates.json`: 238 cells at 14 companies that split
release 1 (re-cut 2, sha256 10cfa5fc) REMOVES as a basis problem, where a later
10-K/10-Q copy of the same period differs from production by a clean split
ratio. Release 2 would show that restated copy instead of removing the cell.

| removed as | cells | companies |
|---|---|---|
| basis_conflict | 138 | CELH, ISRG, PRAX, QXO |
| basis_review | 83 | AHR, FRHC, NAVN, PINS, PNFP, PRAX, UHAL, Z |
| basis_review_company_invariant | 11 | HWM |
| held_basis_stale | 6 | CP (FY2019 basic EPS 3.52, DPS 0.628 in the FY2021 10-K) |

The other 1,302 removed basis cells have no restated copy.

Candidates, not proof. Before any cell is shown, read the restated copy's own
column on the filing face (the AHR trap: the same filings carry a right x4
DPS and a wrong x4 EPS). Each entry has the restated value, accession and
filing date. Sized 2026-11-04 (scrooner-28) from one read-only query.
