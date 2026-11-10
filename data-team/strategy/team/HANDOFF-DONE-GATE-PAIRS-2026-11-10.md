# Handoff: per-pair done gate (`work/fsn/done-gate-pairs`) to Engineering on the Mac (2026-11-10)

From the balance-sheet lane, for Engineering on the Mac and Dhairya. From now on the branch is Engineering's; this lane pushes nothing more to it.

The full build note is `data-team/strategy/team/DONE-GATE-PAIRS-2026-11-09.md`, which is on the branch and on main. This file records the state at handoff.

## Commits from this lane

All on `work/fsn/done-gate-pairs`, built on main `787cc667`:

| Commit | What | CI |
|---|---|---|
| `14d3b237` | Ritwik's ruling, code items 1–5: per-pair gate, C2 hold guard, `done_pairs.tsv`, `written_companies.txt`, the write filter `pipeline/scripts/fsn_write_filter.py`, C6/C8 refusal | 42656645563 green |
| `50b26d8d` | Month-end match, cherry-picked from `work/fsn/month-end-match` `7b796a1b`: an FSN `ddate` rounded to the month end matches a mid-month 52/53-week end, in `pilot._match` and in `cell_loader.bind_periods` | (with the next commit) |
| `9e80070e` | The founder's no-fallback decision: every in-template pair of a company passing criteria 1/2/5 is written whole; each gap key becomes a reasoned blank (`pilot.gap_blank`); C2 becomes a report (`out/valued_to_blank.json`) | 42660017406 green |
| `cdb8825c` | Addendum N1 and N2: hybrid blanks are defects with class and owner set by cause; `pilot.blank_disagreements` and `scrooner-fsn proof-blank`; the shard artifact carries `out/write/` | 42662298742 green |

The branch head is now `6db6f74d`, Engineering's merge of main. It contains `cdb8825c`.

Full suite at `cdb8825c`, run the way CI runs it (Postgres 16): 2,396 passed, 1 skipped (live SEC). Every new test was mutation-checked; the list is in the build note.

## Against Ritwik's conditions

| Condition | State |
|---|---|
| C1 atomicity per (company, concept) | Built. A written pair carries every expected key: values, reasoned blanks and gap blanks. The filter keeps exactly the done pairs. |
| C2 | A report, per the founder's decision: `valued_to_blank.json` lists the valued→blank transitions by reason class, the pairs losing every value, and the gap blanks per data point. `done-gate` refuses to run without the before-image. |
| C3 | Withdrawn by the addendum. |
| C4 | `written_companies.txt` is the cell_proof scope. The restore stays an emergency rollback (N2). |
| C5 | `company_value_owner` untouched. |
| C6, C8 | Dividends per share, total debt and total liabilities are out of the workflow default. `done-gate` refuses them (`HELD_OUT`). |
| C7 | Not run. It is the next step, on main + PR #4 + PR #6 + this branch. |
| N1 | Built and tested: state `defect`; `filing_not_in_store` → `ingestion` / `data_engineer_l1`; `hybrid_gap_unresolved` → class by pilot cause (vocabulary / tag_mapper, period / period_engineer, otherwise unclassified / triage); the cause in `reason_text`; the accession in `input_refs` when one exists. A defect without a class or owner is refused. |
| N2 | Command built and tested (`scrooner-fsn proof-blank`, read-only). It rewrites every row of each affected pair, because the loader replaces a pair whole. **Not wired into the workflow yet:** needs a `proof_blank` stage that downloads `out/write/` from the select_write run, runs the command, then loads the output, which needs the founder's words. |
| N3 | Ritwik's default holds: debt, total liabilities and DPS stay unlisted. If the founder chooses `hybrid_rule_held` blanks instead, that is a small change. |
| N4 | The thresholds can be read from `valued_to_blank.json`. Ritwik applies the flag at C7. |
| N5 | Before-images are taken and uploaded for every company in the shard, a superset of the written companies. |

## Open items for the new owner

1. **Out-of-template and no-expected-key pairs keep their old rows.** These are pairs the gate does not write. If the old mapper holds values for them, the values survive, which goes against "no fallback". This needs the founder's choice between a pair delete and `not_in_template` blanks at the before-image keys.
2. **N2 workflow stage** (above).
3. **Main's `51533c20` wires `no_public_filing_for_period` into `gap_blank`.** Check that merge against N1's reason classes and tests (`test_fsn_done_gate_pairs.py`).
4. **The criterion 5 scope changed.** It now counts only the derived cells of the data points being written. Ritwik should confirm this. Without it, PR #6's derived total-liabilities cells, which C8 holds out, would fail every company that has one.
5. **Q4-for-every-data-point gaps** (AT&T, PG&E) come from `latest_copy_fails_identity` on an unrelated subtotal (`FSN-MISSING-QUARTERS-2026-11-09.md`). They are written as `latest_copy_fails_identity` blanks, not gap blanks. Scoping that blank to the failing calc needs a ruling.

Nothing in this handoff wrote to production or applied a migration.
