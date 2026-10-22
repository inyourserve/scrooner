# Scoreboard (WO-7, Data Triage)

Immutable weekly files. The coverage tables are rebuilt in place, so these committed extracts ARE the history.
All figures are functions of a cell extract (`cells/<date>.cells.csv.gz`); nothing here writes to a database.

| path | what |
|---|---|
| `<date>.csv` | long format: H header, K KPI, R reconciliation, M movement rows. Never edited; a correction is `<date>.rN.csv` |
| `cells/` | the extracts. `2026-10-20.cells.csv.gz` = doc 44 export (sha256 of the decompressed bytes `39df9373...`), the control |
| `defects/` | proxy defect register (`source = proxy`, DATA-INFERRED, never counted as covered) |
| `reason_class_map.csv` | frozen reason-to-class map v1 (134 patterns); changes only as `reason_class_map_v2.csv` |
| `maps/` | D0 data point list (163) and the D0e removal list (30), both hash-checked |
| `sql/` | the live queries (written, NOT run by the author); `scripts/extract_live.py` runs them under the gates |
| `lists/`, `frames/` | the 116 valued-with-reason cells; seeded sampling frames; S4's first-draw exclusions |
| `TARGETS.csv`, `CHAIN.md`, `MANIFEST.sha256` | versioned targets (skeleton), D0 -> D0e -> D1 chain (generated), append-only hashes |

```
python3 scripts/rt1_reconcile.py                       # exact equality with doc 44; exit 1 on any difference
python3 scripts/build_scoreboard.py --check-only       # RT-1 + build in memory
python3 scripts/build_scoreboard.py --cells <extract> --as-of YYYY-MM-DD [--prev-cells P --prev-defects D --ref-end R]
python3 scripts/sampling_frame.py cells|groups --seed S ...
python3 -m unittest discover -s data-team/strategy/scoreboard/tests
/Users/vikash/scrooner/pipeline/.venv/bin/python scripts/extract_live.py --authorised-by "<who/when>" --out-dir DIR   # E0/E1, only when scrooner-4d releases the slot
```
stdlib only (Python 3.12+ ok). `extract_live.py` needs psycopg (the pipeline venv). Evidence labels: MEASURED, PROXY, REPORTED, NOT_COMPUTABLE, NOT_RUN.
