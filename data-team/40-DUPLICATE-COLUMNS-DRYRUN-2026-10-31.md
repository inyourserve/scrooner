# Duplicate statement columns: rule period.duplicate_column_merge@1, cohort dry run 2026-10-31

Flag OFF, plan only, nothing written. Code: `pipeline/src/scrooner_pipeline/normalizer/duplicate_columns.py`
(branch work/engineering/duplicate-column-merge). Full plan: `40-duplicate-columns/dryrun-report.jsonl.gz`
(one line per cell action); Verifier draw: `40-duplicate-columns/verifier-draw.jsonl` (10 merges, 10 hides,
seed 20261031, mapped statement concepts only).

| | |
|---|---|
| Cohort companies planned | 986 (868 with at least one duplicate column) |
| Clusters (one accounting column, 2+ period rows with facts) | 4,898; duplicate rows 5,179 |
| Cell actions | 14,671: re-point 6,700, merge 6,437, hide 1,534 |
| ...on mapped statement concepts | 6,230: re-point 3,250, merge 2,476, hide 504 |
| Facts touched if applied | 17,359 re-pointed, 3,508 demoted; 0 deleted |
| Companies with most actions | WAT 700, DE 539, JCI 537, ATI 499, ONTO 492, CIEN 460, EXEL 459, RBC 435 |

Shapes seen in the draw: 52-53-week filers whose quarter is spelled on the calendar date and on the
fiscal date (RBC, TER, WAT, GRMN: equal values -> merge); a stray context with one or two facts
(EPRT, VTRS: differing or zero values -> hide); genuine alternative periods under one label (ATI
2022 Q2 Apr 1..Jun 30 vs Apr 4..Jul 3, CHRD 2020 fresh-start 11-18 vs 11-19: differing -> hide, an
entity/calendar rule may later pick one). MSFT Q1 FY2017 (recast) hides with a reason; RBC Q2 FY26
merges to one column. Acceptance: Verifier draw before any flag flip.
