# Sector-template layer build: report to Dhairya (2026-11-01)

**Status: BUILT on branch `work/data-engineer/sector-templates`, not applied.** Nothing has been written to any database. The seeder cannot run for real yet because its input file does not exist (see section 1).

## In one paragraph
The founder's 2026-11-01 ruling (doc 02, "sector templates and 100% coverage") says a field is a cell for a company only if that company's sector template includes it, and that coverage = valued ÷ template cells. This branch adds:
- a per-company template table (migration **0120**),
- a seeder that turns a templates file (sector defaults plus company overrides) into rows for every top-1000 company,
- a coverage snapshot that switches to valued ÷ template cells once that table holds rows.

Tests run on real Postgres 16, and every test is mutation-checked.

## 1. Decisions you need to make

1. **The templates file does not exist.** `data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md` is not on `origin/main` or on any of the 177 remote branches; I checked every branch tree.
   - Closest drafts: doc 50 (`data-team/strategy/50-SECTOR-ROWS-AND-VISIBLE-METRIC-SETS-DRAFT-2026-10-22.md`, not approved) and `template_v1_draft.csv` (only on `archive/branches/bs-tl-release1-guard-2026-11-01`).
   - I did not invent template contents. Which fields a bank shows is a Sector Analyst and Standardization Lead call.
   - **Who writes the file, and from which draft?** It must follow the format in section 3.
2. **Land the doc 53 claim for 0120 on main first.** The claim line is on this branch only. Until it reaches main, another session can take 0120.
3. **3 cohort companies have no SIC** in `doc/data-moat/team/top1000/shards.csv`: ARCC (0001287750), CBC (0002065601) and BXSL (0001736035). They can only get a template through an explicit `## Company assignment` row. ARCC and BXSL are BDCs.
4. **Cohort mix by SIC** (986 non-excluded companies), so the templates author knows the scale:
   - banks (6020–6036): 40
   - insurers (6311–6411): 54
   - REITs (6798): 54
   - other 6000s: 61
   - utilities (4900–4991): 50
   - everything else: 724
   - The "other 6000s" group (brokers, BDCs, exchanges, holding companies) is where SIC alone will not choose the right template, so expect company assignments there.

## 2. What was built (files)

| File | What it does |
|---|---|
| `pipeline/db/migrations/0120_company_data_point_template.sql` | `analytics.company_data_point_template`, keyed by (company_id, data_point, effective_from). Columns: in_template and reason, plus template, source (`sector_default` / `company_override`), template_version and seeded_at. A check constraint requires a reason when a field is excluded and for every company override. Replays cleanly twice. **NOT applied.** |
| `pipeline/src/scrooner_pipeline/mapper/sector_templates.py` | Parser, planner, DB validator and batched writer. |
| `pipeline/src/scrooner_pipeline/jobs/map.py` | New command `scrooner-map seed-sector-templates`. Dry run by default. |
| `pipeline/src/scrooner_pipeline/mapper/coverage_snapshot.py` | Template-mode coverage. |
| `pipeline/tests/unit/test_sector_templates.py` | 22 tests: 17 pure, 5 on real SQL. |
| `pipeline/tests/unit/test_coverage_snapshot.py` | Fake cursor taught the new presence query; the 15 existing tests are unchanged and pass. |
| `doc/planning/53_...` | Claims 0120; next free number is 0121. |

## 3. Templates file format (for whoever writes it)

```
template_version: tv1
effective_from: 2026-11-01

## Sector assignment
| template | sic_from | sic_to |
|---|---|---|
| bank | 6020 | 6036 |

## Company assignment
| cik | template | reason |
|---|---|---|
| 0001287750 | bdc | BDC, no SIC in the cohort file |

## Sector defaults
| template | data_point | in_template | reason |
|---|---|---|---|
| bank | net_interest_income | yes | |
| bank | inventory | no | banks present no inventory line |

## Company overrides
| cik | data_point | in_template | reason |
|---|---|---|---|
| 0000320193 | inventory | no | <evidence> |
```

**How a company gets its template:**
- A company assignment beats its SIC range.
- The template's defaults apply first, then the company's overrides replace or add fields. An override can add the company's own combined line (ruling item 3).

**The seeder stops with a list of every problem, and never applies a silent default, when it finds:**
- a cohort company that matches no template,
- overlapping SIC ranges,
- a duplicate row,
- an excluded field or an override without a reason,
- a wrong column header,
- an override for a CIK that is not in the cohort,
- with `--validate-db` or `--apply`: a data point that is not a `canonical_concept.name` or an active `metric_definition.metric_name`, or a company id missing from `core.company`.

## 4. How it behaves

**Seeder** (`scrooner-map seed-sector-templates --templates <file>`):
- Builds the plan **from files only**, using the cohort's own company_id, cik and sic, and writes a plan CSV and a summary.
- `--validate-db` adds two read-only, indexed checks.
- `--apply --confirm-version <template_version>` writes one transaction:
  - it deletes the planned companies' rows at that effective_from and inserts the new set, in chunks of 5,000;
  - a rerun gives the same result (tested: 8 deleted and 8 inserted on the second run);
  - it needs 0120 applied and the founder's typed words.
- **A company's current template** is its full row set at the latest `effective_from` on or before the as-of date. Each version is a complete set, so a field dropped in a new version disappears instead of leaving a stale row behind (tested).

**Coverage snapshot (template mode, on once the table has current rows):**
- For each data point in any template, the concept row and/or metric row count:
  - **denominator** = companies whose current template includes it;
  - **numerator** = those companies with a value. A value outside a company's template does not count (tested). A metric row whose value is null does not count.
- A data point in no template gets no row: it is not shown, so it is not a cell.
- **New score row `template_cell_coverage_score`** = Σ valued template cells ÷ Σ template cells. On this row, `companies_covered` / `total_active_companies` hold those two cell counts.
- A template data point that nothing produces counts as template cells with 0 valued, and is logged. It stays a visible gap, never a dropped one.
- **Before 0120 is applied and seeded**, the snapshot keeps today's population denominators and logs `coverage_snapshot.template_mode_off`, so the nightly `snapshot-coverage` step keeps working. This is reporting only; no value comes from anywhere else.
- **Cell grain** is company × data point, the same as the existing snapshot. Period-level cells (ruling item 4, periods before the first filing) belong to the cohort coverage table, which this change does not touch.

## 5. Evidence

- **New and changed tests:** 37 of 37 pass, including the 5 DB tests on a local Postgres 16 prepared the way CI prepares it (`bootstrap_supabase.sql`, then every migration).
- **Full pipeline suite:** 2,276 passed, 2 failed, 1 skipped. The 2 failures are in `test_fsn_store.py` and are environmental: this container has no `zstd` binary; CI's runner does. They are unrelated to this change.
- **Repo checks:** `check_migrations.py` reports contiguous 0001–0120; `check_docs.py`, compileall and the required ruff lint pass; mypy is clean on the new and changed modules.
- **Mutation check:** 13 of 13 mutations make a test fail.

  | Area | Mutation (each one was caught) |
  |---|---|
  | Snapshot | `in_template` filter dropped |
  | Snapshot | latest-version filter dropped |
  | Snapshot | `effective_from` ignored |
  | Snapshot | null metric counted as valued |
  | Snapshot | template mode never switched on |
  | Seeder | overrides not applied |
  | Seeder | company assignment ignored |
  | Seeder | no delete before insert |
  | Seeder | reasonless exclusion allowed |
  | Seeder | SIC overlap not checked |
  | Seeder | unknown data point accepted |
  | Seeder | rows read under a wrong header |
  | Migration | reason constraint dropped (run on real SQL) |

  The tests also caught 2 real parser bugs before the commit: a bad `effective_from` was reported as "missing", and a wrong header crashed the parser. Both are fixed.
- **Smoke run** on the real cohort with a throwaway two-template file: 986 companies, 1,972 rows, 41 bank and 945 corporate. Without the 3 company assignments the run fails loudly on ARCC, CBC and BXSL.
- **CI** on this branch: see the commit message and the run linked from the branch.

## 6. Next steps (in order)
1. Release manager lands the 0120 claim line on main.
2. The templates author writes `SECTOR-TEMPLATES-2026-11-01.md` in the section 3 format. Then run `--validate-db` (read-only).
3. Founder's typed words: apply 0120, then `--apply --confirm-version <v>`.
4. The next nightly `snapshot-coverage` reports valued ÷ template cells. G2/G3 read `template_cell_coverage_score`.
