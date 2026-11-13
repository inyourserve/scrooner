# Era predictions (top 110, FY2015 to FY-2)

These are predictor runs over the earlier 10-Ks of the top-110 cohort companies (ranks 1-110 in data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv). They are candidates for Engineering's tag-switch gaps. A row is served only if proof marks it PROVEN.

- **Files:** `<TICKER>-<accession>-prediction.csv`, one per 10-K. 938 filings, 105 companies; 5 of the 110 have no 10-K in the window.
- **Columns:**
  - The same columns as the FY0 predictions.
  - `fy0_value` is that filing's own fiscal-year value.
  - `period` is the filing's balance-sheet date.
  - `rules_commit` is the commit of data-team/tags/rules and exam/tools/predict.py used for the run.
- **Window:** every 10-K with period on or after 2015-01-01, except each company's latest two (FY0 and FY-1).
- **Inputs:** all from FSN in the database, read-only. No SEC requests were made for this run.
  - Face lines: `tools/render_sql.py tools/LINES.sql --eras <CIKS>` (or `--accession <ACC,...>`).
  - Note facts: NOTES.sql, the same way.
  - Location slices: LOCATION.sql, the same way.
- **Engine:** `tools/predict.py LINES.jsonl TICKER RANK ../../rules NOTES.jsonl --accession <ACC>`. The `--accession` filter keeps only that filing's lines and note facts. FY0 output is unchanged with or without it.
- **Limits:**
  - The two instance-fed inputs (finance-lease balance-sheet location `fl_loc`, and per-series interest `debt_series`) exist for FY0 only. They need SEC instance reads.
  - In these files the note-only finance-lease addition to total_debt and the per-series interest sum therefore do not fire. Face finance-lease lines are still added.
  - The prior-era label (`prior`) is the tag of the same printed label in the 10-K about four years before each filing.
