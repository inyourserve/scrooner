# Sector-template layer build: report to Dhairya (2026-11-01)

**Status: the layer is on main (`7e44f83`). The seeder input from the APPROVED templates is on `work/data-engineer/sector-templates-seed` for Ritwik's check (section 8). 0120 is not applied.** Nothing has been written to any database.

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
**Run 41312244846, on `b1ed2f9`, rebased on main `e4f776d`: green.**
- **Python tests and correctness lint:** pass. Pipeline 2,281 passed, 0 failed, including all 23 new template tests and the 6 on real Postgres 16. Backend 92 passed.
- **Migrations, documentation, and secrets:** pass. The 0120 clean replay passes in CI.
- **Next.js frontend:** pass.
- **Advisory job (non-blocking):** it flagged one unformatted file, my new CLI command in `jobs/map.py`. The follow-up commit formats it, and `ruff format --check` is now clean across `pipeline/src` and `apps/backend`. The advisory npm audit failure (1 critical) is on main as well and has nothing to do with this branch.

## 8. Seeder input from the approved templates (2026-11-01, branch `work/data-engineer/sector-templates-seed`)

**What Ritwik checks before 0120 is applied.** Source: `SECTOR-TEMPLATES-2026-11-01.md` §1–3 with the §8 corrections (approval `485e38d`), plus the founder's BDC ruling of 2026-11-01. The ruling was relayed to this session by the HD pilot session; this session did not hear it directly, and doc 02 should record it.

### Files
| File | What it is |
|---|---|
| `data-team/strategy/SECTOR-TEMPLATES-SEED-2026-11-01.md` | **The seeder input**: the four tables, 9 templates × 163 data points, plus 12 company assignments and 17 company overrides. Generated; do not hand-edit. |
| `data-team/strategy/data/cohort_v1_1_sic_2026-11-01.csv` | Cohort v1.1 (1,000 companies, same order) with SEC SIC from `group_assignment_v2.csv`. It agrees with `shards.csv` on all 991 shared SICs; ARCC, BXSL and CBC have none. |
| `data-team/strategy/tools/build_sector_template_seed.py` | **The generator: the file to review.** Every rule cites its § of the approval. |
| `pipeline/tests/unit/test_sector_template_seed.py` | Checks that the committed seed equals the generator output, the seeder dry run on the cohort, the §8 points, and a real-SQL load of all 163,000 rows under 0120. |

**Command** (dry run; `--apply --confirm-version tv1-2026.11.01-approved` only after the founder's words and 0120):

```bash
uv run --project pipeline scrooner-map seed-sector-templates --templates data-team/strategy/SECTOR-TEMPLATES-SEED-2026-11-01.md --cohort data-team/strategy/data/cohort_v1_1_sic_2026-11-01.csv
```

**Dry-run result:** 1,000 companies, 163,000 rows: **156,070 template cells** and **6,930 excluded**, with 17 overrides.

**§8.6 sum check (it reproduces §1 exactly, with the three companies moved):**

| Template | Companies |
|---|---|
| general | 769 (712 + 60 pharma − ARCC, BXSL, CBC) |
| bank | 42 (41 + CBC) |
| bdc | 2 |
| lender | 7 |
| broker_am | 37 |
| insurer | 39 |
| reit_equity | 51 |
| reit_mortgage | 2 |
| utility | 51 |

### How §8 was applied
1. **Taxonomy (§8.1):**
   - SIC ranges: utility 4911/4922–4924/4931/4932/4941; bank 6021/6022/6035/6036; lender 6141/6162/6199; broker_am 6200/6211/6282; insurer 6311/6321/6331/6351/6361/6399; reit_equity 6798.
   - Every other SIC is general.
   - Company assignments: the 7 crypto names (6199) → general; NLY and AGNC → reit_mortgage; ARCC and BXSL → bdc; CBC → bank.
2. **Category A OUTs (§8.1):** the 9 probed lines per §3's matrix, mapped onto catalog names. For example, "COR / GP / margin trend / Piotroski" covers cost_of_revenue(_resolved), gross_profit(_resolved), gross_margin, margin_expanding_3yr and piotroski_f_score. Where a sector loses only GP (broker_am, reit_equity, utility), COR stays IN.
3. **Category C, OUT by definition (§8.2):**
   - Banks, lenders and insurers: EBITDA family, capex/FCF family, ROIC and interest coverage.
   - Banks only: D/E and operating income/margin.
   - Plus the matrix's other "by definition" cells: equity REIT capex/FCF, and mortgage REIT operating income, EBITDA, ROIC and capex/FCF.
   - Lender and mortgage REIT carry the inherited bank-like marks as defaults only (§8.7).
4. **Dependent metrics:** a metric that *requires* an OUT input is OUT too, using `metric_dependency_graph.csv` (§6 category A says "+ dependent metrics"). Optional inputs (`alt`, `alt_derive`, `ttm_optional`, and quick ratio's inventory) do not propagate. What it added:
   - `dividends_pct_fcf` and `share_repurchases_pct_fcf` wherever FCF is OUT;
   - **`payables_days` for insurer, mortgage REIT and bdc** (it needs cost_of_revenue);
   - **`interest_coverage_ratio` for mortgage REIT** (it needs operating income).
5. **Category B stays IN (§8.3):** current assets/liabilities, current and quick ratio, and working capital are IN for every template except bdc.
6. **BDC (§8.4 plus the founder ruling):**
   - OUT by definition: COR/GP, inventory, R&D, the current ratio family, the EBITDA family and the capex/FCF family.
   - `revenue` and `bdc_total_investment_income` are IN and marked **RULED**: revenue = total investment income as printed.
   - `net_income` is IN and marked **RULED**: the BDC earnings line = NII as printed.
   - Total debt and D/E are IN. Nothing in bdc says pending.
7. **REP cells stay IN with a reason, so they remain visible defects until defined:** bank and lender revenue (B7, accountant), and mortgage REIT revenue (interest income) and D/E (recourse leverage).
8. **Company overrides (§3):** 19 line instances, written as 17 rows because JPM's two AR lines and BNY's two AR lines each become one row:
   - JPM, BAC, BNY, BOKF: AR;
   - MTB: COR;
   - BPOP, C, STT: opex;
   - RYN, LINE, SUI, WY: inventory; WY also gross_profit;
   - BRK-A: inventory and COR;
   - SNEX: inventory;
   - HOOD: R&D.
   All are `in_template = yes` with a reason.

### Points for Ritwik's check (preparer's choices, not stated in the approval)
1. **`bdc_total_investment_income` is OUT for the 8 non-BDC templates**, with the reason "BDC-only sector row". Left IN, it would be 998 guaranteed blank defects; the concept also fires falsely at 15 insurers (§1).
2. **Evidence accessions are missing from the 17 overrides.** §8.2 wants the accession as the reason. This container has no database, so each reason names the probe (`company_filing_line_evidence`) and says the FSN company step attaches the accession. **Decide whether that is enough to apply, or whether accessions are needed first.**
3. **The §6 category C row also lists SG&A and net cash for banks, insurers and lenders; §8.2's text does not.** I followed §8.2, so those stay IN. Bank SG&A ("OUT candidate, 0% valued") stays IN as a candidate.
4. **Overrides restore only the named line.** For example, WY's gross_profit is IN but its gross_margin stays OUT, and JPM's AR is IN but debtor_days stays OUT.
5. **Not seedable yet:** the new sector rows (bank NII, deposits, loans, efficiency ratio; insurer premiums earned, loss ratio; REIT rental revenue, NOI; BDC NAV per share and NII per share). They are not in the 163-item catalog, so `--validate-db` would reject them. They join a later `template_version` once the concepts exist.
6. **Seven catalog items are IN everywhere by default,** which matches the proposal's 163 × 1,000 denominator:
   - two revenue-resolver inputs (`collaborative_arrangement_revenue`, `net_lease_revenue`);
   - `net_interest_income`, whose registry definition collides with bank NII (§7.6);
   - the three ownership items;
   - the reconciliation-gap diagnostics.
   They will read as blank defects for most companies. **Say if any is not a displayed field.**

### Fixes to the template layer found while doing this (included on this branch)
1. **Ownership data points:** `insider_ownership`, `institutional_ownership` and `mutual_fund_ownership` are registry items of type `ownership`, neither a concept nor a metric.
   - `--validate-db` now accepts any `analytics.data_point_registry` name. Before this fix it would have rejected all three.
   - Template-mode coverage now counts their values from `company_data_point_coverage`. Before, they counted as never valued.
2. **The catalog is the 163 coverage-cell names.** The dependency graph also has `price`, an input node rather than a cell; a test caught it.

### Evidence
- **Template and coverage tests:** 48 of 48 pass, 8 of them on real Postgres 16 (CI-style replay of every migration). One of them loads all 163,000 seed rows under 0120's reason constraint.
- **Full pipeline suite:** 2,294 passed. 2 failed, the known `zstd`-binary environment failures in `test_fsn_store.py`, which pass in CI.
- **Mutation check:** 12 of 12 caught. Each one was applied and the files regenerated:

  | Area | Mutation |
  |---|---|
  | Assignment | CBC not assigned to bank |
  | Assignment | BDC companies not assigned |
  | Assignment | crypto names left in lender |
  | Template | category B made OUT for banks |
  | Template | category C dropped for banks |
  | Template | BDC current ratio family kept IN |
  | Template | BDC ruling reverted to pending |
  | Template | one override dropped |
  | Dependents | no dependent propagation |
  | Dependents | optional inventory edge ignored |
  | Coverage | snapshot ignores ownership values |
  | Seeder | validator ignores the registry |

- **Lint:** ruff format clean, required lint clean, mypy clean on the changed modules, docs links pass.
- **CI run 41317933298 on `311fa5e9`: green.** Pipeline 2,296 passed, 0 failed (the seed and template DB tests ran, none skipped); backend 92; migrations, docs and frontend pass. The only failure is the advisory npm audit, which is non-blocking and also fails on main.

## 9. Verifier FIX 2026-11-09 applied (branch `work/certification-lead/template-seed-fixes`)
Source: `VERIFY-TEMPLATES-AND-LADDER-2026-11-09.md` (branch `verify/templates-and-ladder-2026-11-09` @ 01d203d), FIX rows 1–5 and 8, as Dhairya asked.

**Applied:**
- **Rows 1–3:** company assignments. EQH and ACT → insurer; INVH and TRNO → reit_equity. Each reason cites the Verifier's accession.
- **Rows 4–5:** the MTB `cost_of_revenue` and BNY `accounts_receivable` overrides are removed, so the bank defaults (OUT) stand. That leaves 15 override rows.
- **Row 8:** `seed-sector-templates` now defaults to `SECTOR-TEMPLATES-SEED-2026-11-01.md` and `cohort_v1_1_sic_2026-11-01.csv`.
- **New counts:** general 765, bank 42, lender 7, broker_am 37, insurer 41, reit_equity 53, reit_mortgage 2, utility 51, bdc 2.

**Not applied, decisions needed:**
- **Row 6:** GS, MS and SCHW (and LPLA's OI) behave bank-like. Either put them in a bank-like template, or add per-company OUT overrides for OI, COR and current totals.
- **Row 7:** "IN COND" is applied as IN for the whole sector. The company overlay the approved §4 asks for needs per-company face evidence from the FSN store.
- **Noted:** capex OUT-by-definition hides printed lines, and current totals for banks and insurers stay IN as approved. Both are accountant or approver calls.

## 10. Insurer capex and D&A ruling (2026-11-11, asked by Dhairya after cloud Ritwik's 83bc4988: CB prints neither)
**Evidence:** `data-team/strategy/data/insurer_cf_da_capex_lines_2026-11-11.csv`. For each of the 41 insurer-template companies I read the cash-flow statement (R page) of its latest 10-K on sec.gov, using the declared `SEC_USER_AGENT`, at no more than 3 requests per second. The file lists every depreciation, amortization and capex-like line label it prints.

**Capex: no change.** It is already OUT for every insurer (category C, approved §8.2), so CB shows no capex blank. Noted: 18 of the 41 insurers do print a capex line, for example PGR, ALL, HIG, L, CNA, MKL, FNF and BRK-A. The approved ruling hides those lines, as the Verifier noted on 2026-11-09.

**D&A: stays IN the insurer template.**
- **31 of 41 print a depreciation-type line**, for example TRV "Depreciation and amortization", PGR "Depreciation", AIG "Depreciation and other amortization", and EQH "Amortization and depreciation".
- ALL, CINF, WRB and RNR print it combined with other items. Under ruling item 3 those show under their own label.
- An OUT for the whole sector would hide a line most insurers print.

**D&A: OUT for 10 companies** (company override, `in_template = no`, with the accession and page in the reason):

| Company | What its cash-flow statement prints instead |
|---|---|
| CB | only investment accretion and purchased-intangible amortization |
| AFL | only deferred acquisition cost amortization |
| ACGL | only intangible amortization |
| EG | only bond-premium amortization |
| GL | only deferred acquisition cost amortization |
| ORI | no depreciation or amortization line |
| JXN | only investment amortization |
| VOYA | no depreciation or amortization line |
| LNC | no depreciation or amortization line |
| ACT | only investment, deferred-cost and intangible amortization |

With this, CB shows no D&A blank.

**Open for the Standardization Lead:** amortization of purchased intangibles alone (CB, ACGL) is treated as "no D&A line". Whether intangible amortization by itself counts as D&A is a definition call.

**Branch and verification:**
- On `work/certification-lead/template-seed-fixes`; 3/3 mutations caught.
- Needs the Verifier's re-check, together with rows 1–5 and 8 (section 9), before it is applied.
- **Process note:** two early probe requests (one CB 10-K search and one submissions JSON) went out with a hand-typed User-Agent before I switched to the declared one. Every evidence read used `SEC_USER_AGENT`.
