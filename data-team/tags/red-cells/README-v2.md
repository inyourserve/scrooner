# Top-100 red cells v2 (coverage 6e9a31be, proof v2), 2026-11-13

`top100-redcells-v2-2026-11-13.csv` has one row per red cell (DISAGREE 309, UNCHECKED 1,523, BLANK 3,192; 5,024 in all).

- **Order:** JNJ first, then the 23 companies at 95% or more (highest first), then the rest by coverage.
- **Columns:**
  - `scope`: `reader` (a fix file closes the cell) or `systemic` (Engineering);
  - `systemic_id`: S1–S17;
  - `band`: the rank band;
  - `cause`, `fix` and `evidence`, where evidence is the filing accession, R page, tag and value from the proof, from predict v7 era reads (rules 3330685c), or from the reader fix files.
- **Reader fix files:** where one already decides the cell, the evidence says so. If that decision is one the tag-expert review found wrong, the evidence says that too.
- **Rebuild:** run `data-team/tags/exam/tools/redcells_v2.py` from a scratch folder that holds `v2/cov.csv`, `v2/sum.csv`, `exam/lines_eng`, `exam/ranks.csv`, `fixes/` and a `wt/` checkout of main.

## Limits
- The live DB was not reachable for this pass: the Supabase connector was down. Evidence comes from the committed coverage CSV, the era predictions and the fix files.
- The predecessor CIKs in S17 come from SEC registrant history and need one company-master check before linking.
