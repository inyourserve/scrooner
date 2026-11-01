# Sector-template layer build: report to Dhairya (2026-11-01)

**Status: BUILT on branch `work/data-engineer/sector-templates`, rebased on main `e4f776d`, not applied.** Nothing has been written to any database.

## In one paragraph
The founder's 2026-11-01 ruling (doc 02, "sector templates and 100% coverage") says a field is a cell for a company only if that company's sector template includes it, and that coverage = valued ÷ template cells. This branch adds:
- a per-company template table (migration **0120**),
- a seeder that turns a templates table file (sector defaults plus company overrides) into rows for every cohort company,
- a coverage snapshot that switches to valued ÷ template cells once that table holds rows.

Tests run on real Postgres 16; 15 of 15 mutations are caught. The seeder cannot run for real yet: the Sector Analyst's templates file landed on main mid-build (`83081b5`), but it is an unsigned narrative proposal, not tables the seeder can read (section 1a).

## 1. Decisions you need to make

**a. The templates file is a proposal, not a seed.**
- When I started, `data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md` did not exist on any branch. The Sector Analyst landed it on main during the build.
- It says "**Proposal only** … every rule below needs an accountant/Standardization Lead sign-off before use", so I did not seed from it, and I did not translate it into seed tables myself.

Once signed off, it maps onto the seeder's format (section 3) like this:

| Proposal concept | Seeder format | Gap |
|---|---|---|
| Sector by SIC (§1 table) | `## Sector assignment` SIC ranges | Its SIC lists are sparse codes (6021, 6022, 4911, 4922-4924 …); write them as one-code ranges. |
| Named exceptions (crypto miners out of 6199, NLY/AGNC as mortgage REIT, hybrids BRK-A/CVS/F/DE …) | `## Company assignment` (cik, template, reason) | None. |
| IN / **OUT** per sector (§2, only the 9 evidenced lines of §3) | `## Sector defaults` with in_template yes/no and a reason | None. Its §7.1 says to publish only the evidenced OUTs. |
| **COND** (in only for companies that print the line) | `## Company overrides` | It needs a per-company evidence step from the FSN store (its §4 step 2). The seeder takes the result as override rows but does not compute it. **Next build item:** a generator that writes those override rows from `fsn.line_map`. |
| **REP** sector rows (bank NII, premiums earned, rental revenue …) | `## Sector defaults` rows | Those concepts do not exist yet, so `--validate-db` will reject them, which is correct. They are `definition_pending` until the accountant rules (B7, R7, R8). |
| "OUT by definition" (EBITDA, FCF and others for banks and insurers) | in_template = no plus a reason | Its §7.4 asks whether these count as OUT or as "not applicable" shown separately. Today the reason text carries it; a reason class column is a small follow-up if the founder wants them reported separately. |
| Effective-dated per filing period (§4) | `effective_from` per company version | The seeder writes one effective_from per file; per-company dates need one file per date or a later extension. |
| Its §7.3: an OUT line whose value we hold stays displayed | The snapshot does not count values outside the template | Display is the page's job. Coverage is not inflated by those cells. |

**Who converts the proposal into the section 3 tables, and when is it signed off?**

**b. Which cohort?**
- The proposal measured on `data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv`: 1,000 companies.
- The FSN tooling uses `doc/data-moat/team/top1000/shards.csv`: 986 non-excluded companies.
- They share 980; 20 are only in v1.1 and 6 only in shards.
- The seeder takes either (`--cohort`). The v1.1 file has no SIC column, so in that case the seeder reads `core.company.sic_code` (one read-only query, and it checks each CIK against the database).
- **Pick one.**

**c. Land the doc 53 claim for 0120 on main first.** The claim line is on this branch only.

**d. 3 companies in `shards.csv` have no SIC:** ARCC (0001287750), CBC (0002065601) and BXSL (0001736035). They need `## Company assignment` rows.
- The proposal says ARCC-type BDCs are outside the top 1,000, but ARCC and BXSL are in `shards.csv`. This is the cohort question (1b) again.

## 2. What was built (files)

| File | What it does |
|---|---|
| `pipeline/db/migrations/0120_company_data_point_template.sql` | `analytics.company_data_point_template`, keyed by (company_id, data_point, effective_from). Columns: in_template and reason, plus template, source (`sector_default` / `company_override`), template_version and seeded_at. A check constraint requires a reason when a field is excluded and for every company override. Replays cleanly twice. **NOT applied.** |
| `pipeline/src/scrooner_pipeline/mapper/sector_templates.py` | Parser, planner, DB validator and batched writer. |
| `pipeline/src/scrooner_pipeline/jobs/map.py` | New command `scrooner-map seed-sector-templates`. Dry run by default. |
| `pipeline/src/scrooner_pipeline/mapper/coverage_snapshot.py` | Template-mode coverage. |
| `pipeline/tests/unit/test_sector_templates.py` | 23 tests: 17 pure, 6 on real SQL. |
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

- **New and changed tests:** 38 of 38 pass, including the 6 DB tests on a local Postgres 16 prepared the way CI prepares it (`bootstrap_supabase.sql`, then every migration).
- **Full pipeline suite:** 2,276 passed, 2 failed, 1 skipped. The 2 failures are in `test_fsn_store.py` and are environmental: this container has no `zstd` binary; CI's runner does. They are unrelated to this change.
- **Repo checks:** `check_migrations.py` reports contiguous 0001–0120; `check_docs.py`, compileall and the required ruff lint pass; mypy is clean on the new and changed modules.
- **Mutation check:** 15 of 15 mutations make a test fail.

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
  | Seeder | cohort CIK not checked against `core.company` |
  | Seeder | SIC not read from `core.company` |
  | Migration | reason constraint dropped (run on real SQL) |

  The tests also caught 2 real parser bugs before the commit: a bad `effective_from` was reported as "missing", and a wrong header crashed the parser. Both are fixed.
- **Smoke run** on the real cohort with a throwaway two-template file: 986 companies, 1,972 rows, 41 bank and 945 corporate. Without the 3 company assignments the run fails loudly on ARCC, CBC and BXSL.
- **CI** on the pre-rebase commit `dc11264` (run 41311707944): 2,277 passed. The only failure was `test_fsn_store.py::test_load_company_is_atomic_idempotent_and_keeps_every_print`, which was failing on main at the time and was fixed on main by `460e729`; this branch is now rebased past that fix. The advisory job's npm audit fails on main too and is non-blocking. Results for the rebased commit are in section 7.

## 6. Next steps (in order)
1. Release manager lands the 0120 claim line on main.
2. Pick the cohort (1b). Accountant and Standardization Lead sign off the proposal's evidenced OUTs. Someone converts them into the section 3 tables, with the FSN-derived COND overrides generated rather than hand-typed. Then run `--validate-db` (read-only).
3. Founder's typed words: apply 0120, then `--apply --confirm-version <v>`.
4. The next nightly `snapshot-coverage` reports valued ÷ template cells. G2/G3 read `template_cell_coverage_score`.

## 7. CI on the rebased branch
The run for the head commit of `work/data-engineer/sector-templates` is listed under that branch in Actions (CI workflow); its result is in the latest commit message thread below.
