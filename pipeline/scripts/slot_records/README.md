# Slot-record engine (company-wise mapper), scripts

One copy of every shared rule lives in `common.py`; every family script and the Verifiers' own readers should import it rather than re-implement it.

## `common.py` (shared, stdlib + psycopg)
| function | what it is the single source for |
|---|---|
| `load_cal(cal_dir, adsh)` | a filing's calculation arcs with the fallback chain `_cal.xml` -> calc linkbase embedded in the `.xsd` -> `MetaLinks.json`; returns `(taxonomy_era, arcs)`; arcs = `{(role, parent): [(child, weight, child_is_custom)]}` |
| `statement_children(arcs, role_rx)` | parent -> children restricted to the STATEMENT role (`BS_ROLE_RX`, `CF_ROLE_RX`), never a note/detail/parenthetical/consolidating role |
| `fetch_instants(cur, cik, tags)` | same-accession instant facts: every term of a cell from ONE filing (the original whose period_of_report is the instant, else the accession with most of the needed tags); periodic forms only |
| `fetch_durations(cur, cik, tags)` | same for duration facts; never a derived fact (`core.fact.is_derived = false`) |
| `rounding_unit(values)` | the filer's rounding unit (largest power of ten dividing every value, capped): the tolerance of every identity and tie |
| `SecClient` | sec.gov only, `SEC_USER_AGENT` from the environment (pipeline/.env), <= 4 requests/second, disk floor 4 GB, request counter for the push message |
| `face_rows_for(path, accessions)` | ordered balance-sheet face rows per filing from the FSDS `pre` extract (plain or .gz) |

## Families
| family | detect | assemble | replay | gate |
|---|---|---|---|---|
| balance-sheet totals | `bs_totals_detect.py` | `bs_assemble.py` | `bs_replay.py` | printed `Liabilities` total first; else face-sum of calc roots (reading A) or taxonomy-total-covered roots (reading B), published only when L&E = L + mezzanine + equity incl. NCI ties on the same accession |
| total debt | `era_detect.py` | `assemble30.py` (+ `face_admission.py`) | `replay30.py` | statement-role calc members + guarded face admission; note differences are flags; no-current-side rule |
| D&A / capex | `era_detect_family.py` | `assemble_family.py` | `replay_family.py` | member-level G1 printed root line / G2 composition tie; section arithmetic informational |

Runner: `run_bs.sh <name> <cik,...|@file> [anchors.json]` = detect -> assemble -> replay, summary only (per-cell dump in the report file).
Fetchers (both on `SecClient`): `fetch_boundary_cal.py` (one cal per boundary filing), `instance_reader.py` (custom-tag and dimensioned mezzanine values from the filing instance; downloads deleted).
Checks: `check_face_admission.py` + `results/expected_face_admission.json` (12 Verifier fixtures), `check_anchors.py`, `check_expected_classes.py`.
Export: `export_slot_rows.py <bs|debt> <records.jsonl> <rows.jsonl>` writes rows in the `analytics.company_slot_record` shape (migration 0110; status=proposed, approver null; nothing inserted).
Structural guard: `taxonomy_attrs.py` over `results/us_gaap_2025_elements.csv` (FASB balance/period/abstract attributes; lexical guards remain for retired and custom elements).

## Regression numbers (must not move without a Verifier reason)
19-company BS set: 851 identity ties, 0 withheld, 16 of 16 anchors. Batch 1: 453 ties. Batch 2: 378 ties. Debt fixtures: 15 of 15. D&A V2: 2,053 publishable; capex V2: 2,532.

## Rules of use
SEC requests: sec.gov only, the pipeline's `SEC_USER_AGENT`, <= 4/s, one process, delete downloads, stop at the project cap and ask. Database: one read-only connection per job, `statement_timeout` set, no writes to shared tables. A verdict never depends on production's value. Nothing is proposed without a Verifier filing check.
