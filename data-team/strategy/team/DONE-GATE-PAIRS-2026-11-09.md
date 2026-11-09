# Done gate per (company, data point): build of Ritwik's ruling (2026-11-09)

For Dhairya and Ritwik. Branch `work/fsn/done-gate-pairs`, from main 787cc667 (includes PR #8).

The ruling is `RULING-DONE-GATE-C4-2026-11-09.md` on branch `review/ruling-done-gate-c4-2026-11-09`. Its "Code change needed" items 1–5 are built here. Item 6 (design §5, doc 02) waits for the founder's words.

**This changes a recorded founder decision.** Doc 02, 2026-11-01, item 5 says a company is written whole. This code must not be used for a select_write until the founder confirms per-pair writing in typed words.

## Update: the founder's no-fallback decision (2026-11-09)

Dhairya relayed the founder's typed words from his session, about 22:30 IST: "No fallback. Everything is the hybrid (fcn + sec)". The build now follows them:

- **Every pair is written.** For each company that passes criteria 1, 2 and 5, every data point of the list that is in its template is written whole. Values, reasoned blanks and gap keys all go in. No old-mapper row of those pairs survives, because the loader replaces a written pair whole. C1 atomicity per (company, concept) stays.
- **A reasonless gap key is written as a reasoned blank, never skipped.** The `pilot.gap_blank` cell has state `defect` and rule `fsn.hybrid_gap_blank@1`. It takes one of two reasons:
  - `filing_not_in_store`: no stored filing's period is that period end, counting FSN's month-end rounding. Class `ingestion`, owner `data_engineer_l2`.
  - `hybrid_gap_unresolved`: the filing is stored, but the hybrid could not fill the key. The pilot cause goes in `input_refs.pilot_cause`, and the class and owner follow that cause:

    | Pilot cause | Class | Owner |
    |---|---|---|
    | `no_mapped_line`, `no_mapped_line_cond`, `no_concept_rule` | `vocabulary` | `tag_mapper` |
    | `quarter_not_printed_or_derivable` | `period` | `period_engineer` |
    | `sector_row_definition_pending` | `definition_pending` | `accountant` |
    | `no_face_print_for_period` | `unclassified` | `triage` |

  Both reasons pass `cell_loader.parse_row` and the frozen contract. `reason_code` is free text there (migration 0100 only requires it to be non-empty), so no contract entry is needed. The display texts are in `select.REASON_TEXT`.
- **C2 is a report, not a hold.** `out/valued_to_blank.json` holds three things:
  - the valued→blank transitions per data point by reason class;
  - the pairs whose new cells hold no value where the before-image had values;
  - the gap keys written as blanks, per data point.

  The `done-gate` command still refuses to run without the before-image, so the report is never skipped.
- **Unchanged:**
  - criteria 1, 2 and 5 per company: a structural failure writes nothing for that company, and it is listed;
  - C4: the cell_proof scope is `written_companies.txt`;
  - C5: `company_value_owner` is untouched;
  - C6: DPS is out;
  - C8: debt and total liabilities are out, and the gate refuses them.
- **Not written, and listed:**
  - a data point outside the company's template (`out_of_template`);
  - a pair with no expected key (`no_expected_keys`).

  **Open:** if the old mapper holds values for such a pair, they survive, because nothing is written that would replace them. Removing them needs a pair delete, or `not_in_template` blanks at the before-image keys. Tell me which, and I'll build it.
- The month-end match (branch `work/fsn/month-end-match`) is included here, so mid-month 52/53-week ends count as stored.

The original build of the ruling follows. The C1 rule (b)/(c) gating and the C2 hold it describes are replaced by the update above.

## What changed

1. **`pilot.done_gate`** returns `{company_id: {"company": [failed 1/2/5], "data_points": {dp: [reasons]}, "out_of_template": [dp]}}`. A pair is written only if all four hold:
   - (a) the company passes criteria 1, 2 and 5. A company failure is copied onto every one of its pairs as `company:<criterion>`.
   - (b) the pair has 0 reasonless gap keys: `4_reasonless_keys:N`.
   - (c) at least one expected key of the pair has a cell, valued or reasoned: `c_no_expected_key_with_a_cell:<keys>`. This catches `shares_outstanding_resolved`, which emits nothing.
   - C2: the pair is not held: `C2_held:<why>`.

   Two helpers: `done_pairs(gate)` returns the pairs to write. `fully_done(gate)` returns the companies whose every listed pair passes.
2. **`scrooner-fsn done-gate`** writes these files:
   - `done_pairs.tsv` (company_id, data_point);
   - `done_companies.txt` (the fully done companies);
   - `written_companies.txt` (every company with a written pair: the cell_proof scope, C4);
   - `not_done.json`, per pair;
   - `hold_guard.json`.

   It echoes "N pairs of M; K companies fully done", then the pairs passing per data point and the number of held pairs. It refuses `dividends_per_share_resolved` (C6), `total_debt_resolved` and `total_liabilities_resolved` (C8). It also refuses to run without the before-image, so C2 cannot be skipped.
3. **`pipeline-fsn-write.yml`**:
   - The filter is now `pipeline/scripts/fsn_write_filter.py`, moved out of the inline heredoc so it can be tested. It keeps a row only if its (company_id, data_point_name) is a done pair and the data point is in the dispatched list. The rule that operating income is never note-sourced stays.
   - It uploads `done_pairs.tsv`, `written_companies.txt` and `hold_guard.json`.
   - The before-image already covers every reported company of the shard, a superset of every company with a written pair.
   - `pilot-prod` now also exports `canonical_concept` (id, name) and the shard companies' `core.period` rows into the before-image. These are read-only, and the guard needs them to read the old rows.
4. **C2 hold guard (`pilot.hold_guard`)** reads the before-image and the new cells.
   - A pair is held when its new cells hold 0 values while the before-image held valued rows for it.
   - For every old valued key from 2014-01-01 on, it matches the new cell by grain and an end within 10 days. A blank cell counts under its reason_code. A key with no new cell counts under `no_new_cell`, because the pair's rows are replaced and that value would be lost.
   - The table per data point goes to `hold_guard.json` (`valued_to_blank_by_data_point`), for the review before dispatch.
5. **C6:** `dividends_per_share_resolved` is out of the workflow's default `data_points`. **C8:** debt and total liabilities were never in the default, and the gate now refuses them.

C5 (`company_value_owner`) is untouched.

## Two choices to confirm (Ritwik)

- **Criterion 5 is scoped to the switched data points.** The report now also counts derived-without-same-basis cells per data point. The gate counts only the data points being written, the same way criterion 4 was already scoped. Without this, PR #6's derived total-liabilities cells, which are held out by C8, would fail criterion 5 for every company that has one. The company-level total is still in the report.
- **A data point outside a company's template is not a failure.** This covers a COND point the company does not print, or a company OUT. Such a point has no expected keys, so it is never written. It is listed under `out_of_template` and does not stop the company from being "fully done". If you want it to count against the company, it is a one-line change.

## Tests

The full suite was run the way CI runs it (Postgres 16, every migration): 2,388 passed, 1 skipped.

- `test_fsn_done_gate_pairs.py`:
  - a pair passes or fails on its own;
  - an empty pair is rejected, with keys and with none;
  - a company failing criterion 2 writes nothing;
  - an out-of-template point is not written and does not fail the company;
  - a held pair is not written;
  - the hold guard holds a pair that loses every value and reports transitions (pre-floor keys ignored, `no_new_cell` counted);
  - the `done-gate` command writes the pairs, the proof scope and the hold table;
  - the command refuses C6/C8 points and a missing before-image;
  - the write filter keeps only done pairs, run as the workflow runs it;
  - the workflow filters by done pairs and keeps the held-out points out of its default.
- `test_fsn_pilot.py`: the old done-gate test is updated so criteria 1/2/5 fail every pair of the company, and criterion 5 is scoped to the switched data points.

Mutation-checked:
- the gate per company (criterion 4 summed over the company): fails "a pair passes or fails on its own";
- rule (c) removed: fails "an empty pair is rejected";
- C2 ignored: fails the held-pair test and the command test;
- the filter per company: fails "the write filter keeps only done pairs".

## Not done

- The C7 cohort dry run (main + PR #4 + PR #6 with this gate) is not started, because it is a heavy job.
- No production read or write was made for this build.
