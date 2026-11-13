# Top-100 coverage report (work queue)

Files: `top100-coverage.csv` (one row per cell), `top100-coverage-summary.csv` (one row per company: cells, count per class,
`pct_proven_plus_reason`, `note`, `as_of`). Rebuild (read-only): `PYTHONPATH=pipeline/src python3 pipeline/scripts/top100_coverage.py`
from the repo root; logic in `pipeline/src/scrooner_pipeline/mapper/top100_coverage.py`, test `pipeline/tests/test_top100_coverage.py`.
As-of timestamp is in every summary row (first run 2026-11-13T04:57Z, while 18 companies were being rewritten; rerun later).

## 1. Where the values and proofs come from (live DB, read-only)
- Companies: ranks 1-100 of `doc/data-moat/team/top1000/shards.csv` (4 of them are flagged `excluded` there and have no docmap: AKTX, TBLA, SPCX, RPAY; listed `TEMPLATE_UNAVAILABLE`, zero cells).
- Cells (template): the company's latest FILING-CHECKED docmap `data-team/companies/reads/<TICKER>-docmap-*.csv`, every data point whose status is not `OUT`. `analytics.company_data_point_template` (0120) has 0 rows live and `SECTOR-TEMPLATES-2026-11-01.md` is an unsigned proposal, so neither defines cells yet.
- Fiscal years: `core.period` rows with `fiscal_period='FY'`, FY2015 to the latest FY ending on or before the as-of date (flow data points: the duration of at least 300 days; balance-sheet and share data points: the FY-end instant, `INSTANT_DPS` in the module).
- Served value: `analytics.canonical_fact` joined to `core.period` and `analytics.canonical_concept`; for a data point `x` the resolved concept `x_resolved` is tried first (revenue: `revenue_sanity_resolved`), then `x`.
- Proof: `analytics.cell_proof`, `basis='latest'`, `period_grain` FY (flows) or I (instants), latest `proved_at` per (company, concept, period).
- Reasons: `analytics.cell_blank_reason` (latest `created_at` per cell, grain FY or I) and `analytics.company_tag_map` decisions `not_presented` / `not_in_template` whose era covers the FY end.
- Not used: `analytics.company_data_point_template`, `metric_value` (the docmap data points are all concepts).

## 2. Class rules (first match wins; see `classify`)
1. proof PROVEN and the served value equals the proof's shown value: PROVEN. PROVEN with a different or missing served value: UNCHECKED `proof_is_for_another_value` / BLANK `proof_proven_but_no_served_value`.
2. proof DISAGREE: DISAGREE. proof UNCHECKED: UNCHECKED.
3. served value with no proof row: UNCHECKED `no_proof_row`.
4. no served value, proof NOT_PRESENTED, or a `cell_blank_reason` state in (not_presented, not_in_template, evidenced_zero, undefined_by_math, history_horizon), or a defect code starting `held_`/`hold_` (assumption: held counts as an evidenced reason), or a tag-map not_presented/not_in_template: REASON.
5. otherwise BLANK; `reason_code` is the stored defect code, or `docmap_<status>_not_loaded` when the docmap read decided the cell (not_presented, combined, component sum, ...) but nothing is loaded yet, else `no_value_no_reason`.

## 3. Cell counts per company
In `top100-coverage-summary.csv`.

## 4. Evidence fields per cell (CSV columns)
`accession` = `cell_proof.shown_accession`; `r_page` = `cell_proof.face_report`, else the docmap `r_page`; `tag` = `cell_proof.shown_tag`; `value_source` = `cell_proof.position_source` (slot_record / fsn_pre_calc / face_total), else `canonical_fact` when only a served value exists; `proof_verdict` and `verdict` = latest `cell_proof.verdict` (same value); `reason_code` / `reason` = proof or blank-reason code and text (or tag-map reason); `docmap_status` = the docmap decision for the data point. Evidence columns are empty where no proof row exists.
