# Identity-break triage, 2026-11-13 (proof v5 identities, f0874b67)

`identity-breaks-2026-11-13.csv` has one row per break.

## How the breaks were found
- Proof v5 is not in `analytics.cell_proof` yet. I rebuilt each identity from the served `analytics.canonical_fact` values for the top 100 plus company 1949, at every grain.
- Each break was then checked against the FSN face of the filing whose own column is that period. The checks were read-only, run on 2026-11-13.
- Balance-sheet breaks are counted BEFORE v5's MinorityInterest and temporary-equity operands. The column `v5_operand_list_covers=True` marks the 1,083 that v5's operand list already explains. The rest (384 breaks in 45 companies) match v5's estimated 349 breaks in 31 companies.

## Decisions
- `a`: a real wrong value. The served member is not the filing's printed line, mostly vintage mixes; `correct` names the cell and the value.
- `b`: a false break. Every member is a printed line, and `missing_operand_tags` names the printed line(s) the identity leaves out.
- `c`: the identity should skip. A member is not printed (gross profit or total liabilities is derived), Q4 is derived, the span is not a filed column, or no fx line is printed.
- `open`: not resolved from FSN.

## Columns
- `served`: the served values of the identity's members.
- `diff`: left side minus right side.
- `evidence`: the FSN face lines used.

Tolerance: half a unit per member, where the unit comes from each value's trailing zeros. The cash check allows 2M.
