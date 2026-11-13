# Red cells of the top 100: cause and fix (Tag Expert, first responder)

`top100-redcells-<date>.csv` has one row per BLANK or DISAGREE cell of data-team/strategy/top100-coverage.csv, with cause, fix and evidence (accession, R page or NOTE, tag, value). It is built by exam/tools/redcells.py.

- **How a cell is explained:** each cell is matched to the predictor's run on that exact filing (FY0 lines, or exam/eras/ for FY2015 to FY-2, period within 10 days).
  - **DISAGREE:** grouped by the proof reason. restated_copies_disagree is audit R13 in data-team/tags/proof-ruling-audit-2026-11-13.csv.
  - **BLANK with a docmap decision not loaded:** loader gap. Load the docmap status as the reason.
  - **BLANK with a value in the filing:** map or era gap. The fix is the company_tag_map row the predictor names (status, tags, stmt, era).
  - **BLANK where the filing has no line:** the reason is not_presented, OUT, combined or component_in_note.
  - **BLANK with no filing-matched prediction:** FY-1, a window before 2015, or a 10-K missing from FSN. Take the value from the next 10-K's comparative column.
