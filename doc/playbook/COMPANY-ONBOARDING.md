# Company onboarding: zero to certified

Take any US-listed company from nothing in the database to a certified page. This page lists the steps in order, the exact command for each, and the check that says the step passed. It also shows where the steps are not yet automatic. Checked against `origin/main` 5d9530b6 (2026-11-16). If this page and the code disagree, trust the code. Then fix this page.

**Target (founder):** onboarding 500 companies is one dispatch plus a Tag Expert queue. **Today:** steps 4 to 7 are one dispatch (`top100-flow.yml`). Steps 1 and 2 are dispatches (`onboard-company-identity.yml`, `onboard-company-filings.yml`, added 2026-11-16, see below). Step 3 is a local chain (another agent is building `pipeline-standard-extract.yml`). Step 8 is switched off. See "Gaps".

**Read first:** the display rule (doc 02, `Display coverage means a value in every shown cell`, 2026-11-16), [CERTIFICATION-METHOD-2026-11-16](../../data-team/strategy/approvals/CERTIFICATION-METHOD-2026-11-16.md), and [ONE-PATH-DESIGN-2026-11-16](../../data-team/strategy/ONE-PATH-DESIGN-2026-11-16.md). The one-path note covers why the layers in steps 4 to 6 each decide the same things again. That is not repeated here.

**Before any heavy run:** run `ListAgents`, check `select count(*) from pg_stat_activity`, and check `df -h`. Every write below is a production write (see "Decisions").

## The steps

Each step lists four properties. **List:** is it one command or dispatch keyed by a company list? **Idem:** is it idempotent? **Resume:** can it resume after a failure? **Width:** can it run at batch width?

### 1. Company, CIK and predecessor windows
- **Dispatch (2026-11-16):** `onboard-company-identity.yml`, inputs `tickers`, `ciks`, `history_csv`, `apply`. Dry run by default: it resolves the list, proposes predecessor windows (`proposed_history_sources.csv`, `review_queue.csv` in the artifact, never applied), prints the no-filing CIKs and dry-runs a reviewed `history_csv`. `apply=true` (main only) runs the bootstrap submissions and identity with `--ciks` always set, and applies `history_csv` (idempotent, one transaction, an unreviewed row with an empty `klass` is refused). Code: `pipeline/src/scrooner_pipeline/onboarding/`.
- **Detection limit (live, DATA-INFERRED):** it reads 8-K12B and 8-K12G3 filings and takes the other filers on that accession as predecessor candidates. The 8-K12B headers of ExxonMobil Holdings and BlackRock Inc list only the successor, so for those two it proposes nothing and queues them (`successor_notice_without_predecessor_cik`). A person or agent still names those predecessors.
- **`NOFILE`:** `top100_flow.sh` now computes it with `python -m scrooner_pipeline.onboarding.no_filing` (first 10-K period or predecessor window end on or after 2024-01-01). It returns exactly the old five CIKs for the 110 companies with a docmap. The cutoff is an assumption, not filing-checked.
- **Commands:**
  - `scrooner-bootstrap submissions --ciks C1,C2`, then `scrooner-normalize identity --ciks C1,C2`. This creates `core.company`, `core.listing` and `core.filing`.
  - Predecessor history: add rows to `core.company_history_source` (migration 0121: `predecessor` or `exclude`, a window and a reason).
  - Predecessor periods: `pipeline/scripts/history_periods.py <sources.csv> <out.csv> <cache>`. It is read-only on sec.gov and writes a CSV to review. The "0121 apply script" inserts the rows.
  - Predecessor FSN rows: `pipeline-fsn-extract-predecessors.yml` with inputs `ciks`, `sets` and `apply=true`. It writes to the bucket folder `fsn-notes/predecessors/<set>/`.
- **Pass:** the company has a `core.company` id. Every predecessor CIK has a history row. Its sets are listed under `predecessors/`.
- **List:** yes for the bootstrap and identity commands, by `--ciks`. No for history rows: a person or agent judges which CIKs are predecessors, and nothing detects them. **Idem:** yes. Identity upserts, and the bootstrap resumes the same run. **Resume:** yes for the bootstrap (`start_or_resume_run`). **Width:** list-wide, one process. **Gotcha:** `scrooner-normalize` falls back to the *golden set* when `--ciks` is empty.
- **Non-cohort companies:** the cohort bucket extracts were cut to the top-1,000 cohort CIKs. A company outside the cohort gets its FSN rows only through the predecessors extract above, used with its own CIK. `scrooner-fsn shard` reads `predecessors/` for every target CIK.

### 2. Filings into core and FSN, plus instance evidence
- **Dispatch (2026-11-16):** `onboard-company-filings.yml`, inputs `tickers`, `ciks`, `width` (1 to 8 shards), `since`, `max_minutes`, `apply`. Needs step 1 done. Apply (main only): bootstrap companyfacts and submissions (CIKs plus their predecessor source CIKs), then per shard normalize identity, periods, units, facts (`--ciks` always set), tagmap-authority, tagmap-dedupe, `fsn nightly` plus `fsn load --increment` (the commands of `pipeline-fsn-load-filings.yml`, which works for any CIK because it reads core.filing minus fsn.filing, not the cohort bucket), and add-dim-notes. Dry run (default) skips the bootstrap and the four normalize stages and dry-runs the rest. At most 2 shards run at once (2 req/s each, 4 req/s total). The R-page lookup and instance evidence are not in it.
- **Core (value source):**
  - `scrooner-bootstrap companyfacts --ciks …`. The bulk zip is cached for the day.
  - `scrooner-normalize identity|periods|units|facts --ciks …`
  - `scrooner-normalize tagmap-authority --company-ids … --apply`. This keeps one authoritative copy per disagreeing group. A dry run first prints the held cells before and after.
  - `scrooner-normalize tagmap-dedupe --company-ids … --apply`
- **FSN (structure):**
  - `scrooner-fsn shard --ciks … --out companies`, then `scrooner-fsn load --companies companies --ciks …`
  - For new filings EDGAR has but the SEC sets lack: `scrooner-fsn nightly --ciks … --since YYYY-MM-DD`, then `scrooner-fsn load --increment`.
  - `scrooner-fsn add-dim-notes --company-ids … --apply`. This is insert-only and reads both bucket folders.
- **Instance evidence:** `data-team/tags/line_map/tools/instance_evidence.py fetch` (part of step 3).
- **Note R pages:** `scripts/build_note_report_lookup.py <coverage csv> <fsn cache> --edgar` runs at 2 req/s. It appends to `data-team/47-fsn-store/note_report_lookup.csv`, which must be committed.
- **Pass:**
  - `core.fact` has rows for each filing since 2015.
  - The duplicate-group count after `tagmap-dedupe` is 0.
  - `fsn.company_load` has a row per company.
  - `fsn load --dry-run` reports nothing left to insert.
  - The coverage summary shows 0 `pageless_shown`.
- **List:** yes, each command takes `--ciks` or `--company-ids`. There is no single command for the whole step. **Idem:**
  - `fsn load`: yes, keyed on (company, input_sha256, loader_commit).
  - `add-dim-notes`: yes, insert-only on the unique key.
  - normalize: upserts.
- **Resume:**
  - `shard`: yes, `progress.json` records each period that is done.
  - `load`: yes, one transaction per company.
  - The note lookup keeps its existing rows.
- **Width:** local runs only.
  - `pipeline-fsn-write.yml stage=load_map` shards `fsn.*` loads. It refuses CIKs outside cohort v1.1.
  - `pipeline-recompute.yml` runs normalize stages, but only for companies that **already have** `core.fact` rows. It cannot onboard a new company.
  - `tagmap-authority` and `tagmap-dedupe` are in no workflow.
  - The note lookup runs after a coverage export, so it is a second loop: flow, then lookup, commit, then flow again.

### 3. Standard extract and resolver (owner: Tag Expert)
- **Commands**, from `data-team/tags/line_map/tools/`:
  1. `python3 standard_run.py sql CIKS OUTDIR --batch 4` writes the four standard queries (`extract.sql`, `extract_bs.sql`, `extract_notefacts.sql`, `extract_facelines.sql`).
  2. **Run each `.sql` against the DB and save the rows as `OUTDIR/{lines,bs,notes,face}.jsonl`.** No tool does this step.
  3. `standard_run.py assemble OUTDIR`
  4. `sql-le`, then assemble again.
  5. `instance_evidence.py fetch OUTDIR/filings.json OUTDIR/instances`
  6. `resolve_all.py VERSION OUT.csv`
- **Output:** append the rows to `data-team/tags/line_map/resolver-all110-<date>.csv`, in the format in [RESOLVER-OUTPUT-FORMAT.md](../../data-team/tags/line_map/RESOLVER-OUTPUT-FORMAT.md), and commit it to main.
- **Pass:** no `no_role` rows. Every `READER CHECK` and `location by absence: CHECK` flag is ruled. `calc_check` fails are quarantined.
- **List:** a CIK list goes in, but the chain is five manual hops. **Idem:** read-only, so the same inputs give the same CSV. **Resume:** no, rerun from the start. The instance cache is per accession. **Width:** CIK batches of 4 per query, local only.
- **Scale gap:**
  - `structural-load` in the flow and `structural_direct.py` both read only the **latest** `resolver-all110-*.csv`. Every company must live in that one file, which held 68,903 rows for 110 companies.
  - `instance_evidence.py` has its own limiter (about 3 req/s). It does not use the shared lock.

### 4. Structural load and serve
`top100-flow.yml` runs `scripts/top100_flow.sh`, which runs these in order:
1. `scrooner-map docmap-load <reads> --extend-eras --predictor-eras data-team/tags/exam/eras --no-filing-ciks <list> --apply`
2. `scrooner-map structural-load <latest resolver csv> --company-ids … --apply`
3. `scrooner-map tagmap-plan --company-ids … --apply --coverage-gate --coverage-gate-scope concept --docmap-reads <reads> --before-image-dir bi_a`. Through `mapper/structural_direct.py`, this serves resolver rows the tag-era path cannot reach.
4. The proof (step 5).
5. `scrooner-map era-guard --company-ids … --apply`
6. `tagmap-plan` again, into `bi_b`, then the proof again.

- **Inputs:**
  - The docmap `data-team/companies/reads/<TICKER>-docmap-*.csv`. This is the page template: with no docmap, the company is `TEMPLATE_UNAVAILABLE` with 0 cells.
  - Fix files `reads/fixes/<TICKER>-fixes-*.csv`.
  - The resolver CSV.
- **Outputs:** `analytics.company_tag_map` and `analytics.canonical_fact` rows, plus before-images in the run artifact.
- **Pass:** each command exits 0. Rejects and conflicts CSVs are empty or ruled.
- **List:** yes, `company_ids` or `csv_path`. **Idem:**
  - `docmap-load`: replaces the company's rows in one transaction.
  - `structural-load`: replaces the structural rows of the input pairs.
  - `tagmap-plan`: one transaction per company, with a before-image.
  - `era-guard`: not checked.
- **Resume:** per company. A failed company reruns its whole chain, and there is no checkpoint within a company. **Width:** `parallel` from 1 to 20, default 16, matrix cap 256.
- **Hard-coded:** the `NOFILE` CIK list inside `top100_flow.sh`.

### 5. Proof
- **Command** (in the flow, once per CIK in sequence): `scrooner-proof run --ciks C --report … --write`. Outside the flow, use `pipeline-cells-proof.yml`: inputs `ciks`, `shards` from 1 to 40, `resume`, and `write`.
- **Pass:** no DISAGREE. Every shown value is PROVEN at the current `DETECTOR_VERSION` (`proof/prove.py`, now `cell_proof_v21_2026-11-16`, pinned by `pipeline/tests/unit/test_detector_version_pin.py`).
- **Idem:** upsert. **Resume:** `pipeline-cells-proof.yml resume=true` skips proved companies. **Width:** 16 to 20 in the flow, 40 shards in the workflow.
- **Gap:** coverage reads only proofs at the current version. Each bump re-opens every company until it is proved again (ONE-PATH §1, step 1 fixes it).

### 6. Display
- **Command:** `pipeline/scripts/top100_coverage.py <out>`, a read-only wrapper around `mapper/top100_coverage.py`. `apply_display` sets each cell to SHOWN_VALUE, HIDDEN_ROW, HIDDEN_YEAR or OPEN.
- **Outputs:**
  - `top100-coverage.csv` and the summary
  - `top100-open-shown-cells-*`, `top100-hidden-rows-*` and `top100-hidden-years-*`
  - in the flow, `data-team/strategy/open-shown/<TICKER>.csv`, the **Tag Expert queue**
- **Pass:** `gate_ready = yes`: shown cells > 0, 0 OPEN, 0 `pageless_shown` and 0 `parts_blank_shown`. This is the mechanical gate only; `verifier_certified = yes` means the latest verdict in `data-team/strategy/approvals/registry.csv` is PASS.
- **Idem:** read-only. **Width: a hard limit today.**
  - `main()` keeps only `rank <= 100` of `doc/data-moat/team/top1000/shards.csv`. A company outside that set has no coverage row, so it can never pass the gate.
  - Each flow job rebuilds coverage for all 100 companies.
  - The flow's `only_open` filter still reads the old `pct_proven_plus_reason` column, not `display`.

### 7. Page gate, certification request and Ritwik's draw
- **Gate:** `scripts/ci/top100_gate.py --coverage-csv … --company-id … --out-dir … --resolver …`. It runs in the flow job and makes no DB call.
  - Exit codes: 0 PASS, 1 FAIL, 3 SKIP, 2 error.
  - PASS means: ≥1 SHOWN_VALUE, 0 OPEN, an accession and R page on every shown cell and every part, and no shown cell with a hidden-year reason.
- **Publish:** the `publish` job alone holds `contents: write`. On PASS it commits `data-team/strategy/certification/<T>-coverage-<date>.csv` and `data-team/strategy/approvals/requests/<T>-request-<date>.md`.
- **Draw:** Ritwik follows CERTIFICATION-METHOD: 32 shown cells against the filing, the total_debt census, every hidden row and year, and the locators. On pass he writes `approvals/<T>-certificate-<date>.md`. From then on, the flow's `certified-guard` restores any certified cell that regresses.
- **List:** yes, inside the flow. **Idem:** yes, it only adds new files. **Width:** up to 16 publish jobs, each with 10 push retries. **The draw is a manual step for each company.**

### 8. Nightly incremental for new filings
- **Workflow:** `pipeline-refresh.yml`, daily at cron 12:23, concurrency `heavy-db-jobs`. It runs:
  1. `scrooner-incremental`
  2. `pipeline/scripts/fsn_nightly_incremental.sh`, the hybrid
  3. `reprocess_recent_filers.sh`, the old normalize and map path
- **Hybrid stages**, set by `FSN_NIGHTLY_STAGE`:
  - `build`: `scrooner-fsn nightly`
  - `load`: also `fsn load --increment` and `fsn pilot`
  - `write`: also `tagmap-plan --apply` for the night's companies that have a `company_tag_map`
- **Old-path skip:** with `HYBRID_NEW_PATH=on`, the old writers skip companies on the new path. `fsn_store/new_path.py` names them: companies with an applied `company_tag_map.select@1` or `fsn.*` protected cell, or a `company_value_owner` row.
- **Today:**
  - Both repository variables are **unset**, so both default to `off`. `gh variable list` shows only `TOP100_COVERAGE_HOURLY`.
  - The night's cohort is `cohort_v1_1_proposal_2026-10-24.csv`. A newly onboarded company outside it is never picked up.
  - Even at `write`, the nightly runs **no** resolver, structural-load, proof, era-guard, coverage or certified-guard. A new 10-K is served without being proved, and the certificate is not re-checked.

## Decisions a person or agent still makes, and how each becomes a rule

| Decision today | Where | Becomes |
|---|---|---|
| Tag Expert rulings: `no_role`, `READER CHECK`, combined splits, false reasons | resolver versions, `_false-reason-rulings-*.csv` (`reason_guard.RULINGS_GLOB`), `open-shown/<T>.csv` | Every ruling ships as a resolver rule with a test. The open-shown queue is the only input. The predictor (`data-team/tags/exam/tools/predict.py`) graduates per class at ≥99% blind with a one-sided upper bound ≤1.5% (NOW.md). Graduated classes become sampled checks. |
| Hand-fix rows | `data-team/companies/reads/fixes/` (114 files), `structural-fixrows-*.csv` | They become resolver input, not serve-time overrides (ONE-PATH §3). A new fix needs a resolver rule. |
| Reader checks and docmap reads (the template itself) | `data-team/companies/reads/<T>-docmap-*` | The template is generated from the resolver decision plus the sector template (ONE-PATH step 5). Reading becomes a random sample. |
| Predecessor CIKs and no-filing CIKs | `core.company_history_source` rows, the `NOFILE` list in `top100_flow.sh` | Detect them from submissions (former names, `formerNames`, Form 8-K12B successor filings). Today this is not built. A detection that is not certain goes to the queue. |
| Founder typed go: production writes, migrations, proof-version merges, `FSN_NIGHTLY_STAGE` or `HYBRID_NEW_PATH` on | CLAUDE.md; `top100-flow.yml` header ("The founder dispatches it"); the commit a256009d "NOT FOR MERGE" pattern | Stays a gate for migrations and DDL. The flow's writes already rest on standing approvals: the founder approved the load, the guarded rewrite, `proof --write` and the era guard on 2026-11-13/14 (`top100_flow.sh` header). Proof merges need the certified guard plus a scoped re-prove diff (ONE-PATH step 1), not a hand hold. |
| Ritwik's draw, per company | CERTIFICATION-METHOD | A seeded draw generated from the request file, with the answer key built from the filing by tool. A person reviews only failures and a pooled sample across companies (0.10% pooled target). |

## Scale knobs

- **Actions width:** the `parallel` input of `top100-flow.yml`, from 1 to 20, default 16. One job uses about 1.6 pooler connections (commit b4d8e412). The matrix is capped at 256 companies, so 500 companies take two dispatches.
- **SEC rate:** at most 4 req/s in total, sec.gov only. Tools use 2 req/s on a shared `CrossProcessRateLimiter` lock file. **The lock is per machine**: each Actions runner has its own, so N runners can make N × 2 req/s.
  - `common/config.py` defaults `sec_max_requests_per_second` to **8.0**, above the 4 req/s rule.
  - `instance_evidence.py` has its own limiter (about 3 req/s) and does not use the shared lock.
  - Today, no SEC calls run inside the flow.
- **DB budget:** keep within 70 connections. `top100_flow.sh` waits while `pg_stat_activity > 80`. The nightly hybrid stops above `MAX_BACKENDS` = 60. Every job sets `statement_timeout` (flow: 15 min per statement, coverage: 10 min).
- **Disk:**
  - Mac: `FREE_FLOOR_GB` = 8 in the flow.
  - `fsn shard --floor-gb` defaults to 4. The workflows set 3.
  - Proof caches FSN quarters in `.cache/fsn`, about 1.7 GB per shard.
- **Concurrency:** `top100-flow.yml` and `pipeline-cells-proof.yml`/`-load.yml` share `manual-db-jobs`. The nightly and the other scheduled jobs use **`heavy-db-jobs`**, a different group. `heavy_job_guard.sh wait-for-write` waits only for `pipeline-fsn-write.yml`. **So nothing stops the flow running beside the nightly refresh**, except the connection wait.

## Gaps between today and "500 = one dispatch plus a queue"

1. **Steps 1 and 2 now have workflows (2026-11-16, untested live: no dispatch has been run); step 3 has none yet.**
   - CLOSED by the two dispatches: bootstrap and normalize with `--ciks`, `tagmap-authority` and `tagmap-dedupe`, the FSN load for non-cohort CIKs (via `fsn nightly` and `load --increment`, not `load_map`), add-dim-notes.
   - STILL OPEN: the dispatches have not been run live (dry run first, then a founder-approved apply). `fsn-write load_map` still refuses non-cohort CIKs. Instance evidence and the note R-page lookup are not in step 2. The resolver extract (step 3) has a manual SQL-to-jsonl hop.
   - The shared-limiter cap is a workflow setting (2 runners at 2 req/s). It is not enforced across other SEC jobs on other runners.
2. **Predecessor detection is partly built.** CLOSED: `NOFILE` is data-driven; reviewed history rows apply through `onboard-company-identity.yml` (dry run by default). STILL OPEN: the detector finds a predecessor only when the 8-K12B header lists it as a co-filer (not for ExxonMobil Holdings or BlackRock Inc); predecessor `core.period` rows (`history_periods.py`) are still a manual step; the `NOFILE` cutoff is an assumption.
3. **The template is a hand-read docmap.** With no docmap, there are no cells (`TEMPLATE_UNAVAILABLE`).
4. **The resolver is one file** (`resolver-all110-*`, latest only). Batches cannot add to it independently.
5. **Display covers ranks 1 to 100 only.** It also rebuilds all 100 companies in every job, and `only_open` uses the old measure.
6. **The note R-page lookup is a second pass** outside the flow, and it commits by hand.
7. **A proof-version bump re-opens every company** (ONE-PATH step 1).
8. **Ritwik's draw is per company and by hand.**
9. **The nightly is off**, its cohort is fixed, and it does not prove, re-gate or guard certificates.
10. **The SEC rate is per runner, not global.** The config default is 8 req/s.
11. **The flow and the nightly use different concurrency groups.**
12. **The matrix caps at 256 companies.**
