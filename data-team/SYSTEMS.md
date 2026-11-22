# Scrooner systems: the one inventory

Founder order 2026-11-22: one resource file of every system, so nobody builds a new one; extend the owning system unless new is truly required; mature each base system like an expert. Written 2026-11-22 from `origin/main` f5f600cb (paths checked, numbers cited). Supersedes, as the systems inventory, the older partial lists `doc/data-moat/SYSTEMS.md` (2026-10-02), `doc/reference/44_Scrooner_Systems_Index.md` (2026-09-08) and the pipeline map in `data-team/20-SCROONER-INFRA-MAP.md` (2026-10-17); those stay as history.

**Chain:** SEC filing → (1) SEC access/collector raw → (3) normalizer core.fact (standard-tag values) + (4) FSN store/standard extract → (5,6) tag knowledge + tag library → (7) predictor → (8) line_map resolver ← (9) filing reads → (10) structural loader → analytics.canonical_fact → (11) proof → (12) templates + (13) coverage/display state → (14,15) verifier + display certificate → (16) metric registry/calculators → (17) screener + (18) AI query → (19) apps/app pages. Cross-cutting: (20) flow + CI, (21) nightly refresh, (22) migrations, (23) mind, (24) agent roles. (25) lists legacy systems.

Paths: bare module paths are under `pipeline/src/scrooner_pipeline/`; `line_map/`, `exam/`, `rules/`, `library/` are under `data-team/tags/`. Format: **Entry** scripts/modules · **Owns** data files/tables · **Runs** workflows · **Tests** · **Doc**. Maturity 1 (sketch) to 5 (world class, measured, self-correcting).

## 1. SEC access: collector + rate limiter
Fetch, retry, checkpoint, hash and store SEC data losslessly; one 2 req/s machine budget.
- **Entry** `pipeline/src/scrooner_pipeline/collector/` (companyfacts, submissions, filings, storage), `common/sec_client.py`, `common/sec_rate.py` (the one budget), `common/rate_limiter.py` (flock base), `data-team/tags/line_map/tools/sec_pace.py` (stdlib tools' door to sec_rate) · **Owns** `raw.*`, Supabase Storage · **Runs** onboard-company-*.yml, pipeline-refresh.yml (`scrooner-incremental`) · **Tests** `pipeline/tests/unit/test_sec_rate_ceiling*`, `test_storage_dedupe_and_retire.py`, `line_map/tools/test_sec_pace.py` · **Doc** `doc/foundational/07_SEC_EDGAR_Rules_and_Data_Guide.md`
- **Maturity 4.** Every in-package caller and the line_map tools share one flock limiter at 2.0/s, mutation-tested (commit 8891c531).
- **Gaps:** (1) `pipeline/scripts/per_share/eps_face_read.py` (own `sleep(0.3)`) and `pipeline/scripts/slot_records/common.py` ("<= 4 req/s") still bypass sec_rate. (2) The lock is per machine: GitHub runners split the budget by hand (onboard matrix 1/s per runner), nothing enforces it across runners. (3) The ad-hoc scratchpad `secfetch` helper is outside the repo and temporary: replace its uses with `sec_rate.wait()` or `SECClient`.
- **Do not build** another limiter, sleep loop or fetch helper. Merge candidates: the two scripts above; `data-team/strategy/tools/groups_v2/sec.py`.

## 2. Company master and onboarding
Company identity, CIK/predecessor windows, tickers, prices, sector, text.
- **Entry** `company_master/`, `onboarding/` (ciks, predecessors, history_apply, no_filing), `corporate_actions/` (splits), `jobs/company_master.py` · **Owns** `core.company`, `core.company_history_source` (0121), market price tables · **Runs** onboard-company-identity.yml, onboard-company-filings.yml, pipeline-refresh.yml · **Tests** `pipeline/tests/unit/test_company_*`, `test_*history*` · **Doc** `pipeline/CLAUDE.md`
- **Maturity 3.** Onboarding is a two-step workflow; the no-filing rule is data-driven (`onboarding/no_filing.py`, was a CIK list until 2026-11-16).
- **Gaps:** (1) predecessor/new-CIK cases still break history (XOM's new CIK had no 10-K in FSN, `line_map/README.md`). (2) Sector assignment comes from SIC ranges plus yfinance industry, not from the filing. (3) No scale check for 5,000 companies (ladder in `data-team/strategy/SCALE-5K-30DAY-PLAN-2026-11-17.md`).
- **Do not build** another universe or CIK list; use `onboarding/ciks.py` and `collector/universe.py`.

## 3. Normalizer: core.fact (value source for standard tags)
companyfacts → `core.fact` with lineage; per founder 2026-11-11/12, the SEC company API is the value source for us-gaap tags.
- **Entry** `normalizer/` (facts, periods, units, dedupe, restatements, shared_accession), `jobs/normalize.py` · **Owns** `core.fact`, `core.filing`, `core.period`, `core.concept` · **Runs** pipeline-refresh.yml (`reprocess_recent_filers.sh`), onboard-company-filings.yml · **Tests** `pipeline/tests/unit/test_*normaliz*`, `test_*shared_accession*` · **Doc** `doc/execution-plans/09_Scrooner_Normalizer_Execution_Plan.md`
- **Maturity 3.** Lossless lineage to raw; `is_authoritative` hard filter.
- **Gaps:** (1) nightly reprocess still runs the old normalize+map chain for new filers, not the resolver path. (2) companyfacts carries only us-gaap/dei: custom tags need FSN values (founder 2026-11-12), two value paths to reconcile. (3) Authority rules live here and again in resolver/proof (see 11).
- **Do not build** a second fact table; `normalizer/cell_loader.py` is a writer (see 25), not a normalizer.

## 4. FSN store + standard extract
SEC Financial Statement and Notes data per filing (lines, calc arcs, values) as the structure source; the standard extract feeds the resolver.
- **Entry** `fsn_store/` (load, increment, xbrl_fsn, extract_sec, dim_note), `jobs/fsn.py` (`scrooner-fsn`), `pipeline/scripts/fsn_nightly_incremental.sh`; extract: `data-team/tags/line_map/tools/standard_run.py`, `extract*.sql`, `scripts/ci/run_extract_sql.py` · **Owns** schema `fsn` (0118), 7 extract JSON files · **Runs** pipeline-fsn-load-filings.yml, pipeline-fsn-extract-predecessors.yml, pipeline-standard-extract.yml, pipeline-fsn-cohort/pilot.yml · **Tests** 27 `test_*fsn*` files, `test_run_extract_sql.py`, `test_extract_shards.py` · **Doc** `data-team/strategy/FSN-STORE-DESIGN-2026-11-01.md`, `data-team/47-fsn-store/FORMATS-v1.md`
- **Maturity 4.** 1,000 companies loaded; EDGAR-built rows equal SEC FSN on 20/20 filings, 22,774/22,774 numbers (NOW.md 2026-11-12).
- **Gaps:** (1) the FSN nightly incremental step in pipeline-refresh.yml is flag-gated off by default, so new filings do not reach the extract automatically. (2) The extract reads 10-K/20-F/40-F only (`RULEBOOK.md` §2): no 10-Q quarters in the resolver. (3) Missing filings are tracked by hand (`data-team/strategy/fsn-missing-filings-2026-11-16.csv`).
- **Do not build** another SEC XBRL parser or per-filing fetcher; `fsn_store/xbrl_fsn.py` is it.

## 5. Tag knowledge: cards, quirks, ledger
What a tag means, who uses it, known misuses; FILING-CHECKED evidence classes.
- **Entry/Owns** `data-team/tags/cards/` (24 cards + 9 `generated/`), `INDEX.md`, `company-quirks.md`, `playbooks/`, `taxonomy/` (FASB elements, calc, deprecations, DQC), `validations/`, `decisions/`, `feedback-inbox.md`, `data-team/22-FILING-LESSONS-LEDGER.md` · **Runs** none · **Tests** none · **Doc** `data-team/tags/00-README.md`, `LEARNING-SYSTEM.md`, `STRUCTURAL-MAPPING.md`, role `data-team/19-TAG-EXPERT.md`
- **Maturity 3.** Cards carry accession and R-page evidence; taxonomy and DQC rules are data.
- **Gaps:** (1) cards unchanged since 2026-11-13 while the resolver moved .73→.87: rulings land in code, mind and commit bodies, not cards. (2) Knowledge is split across cards, INDEX, quirks, ledger, decisions/, feedback-inbox and mind with no single key per element. (3) Not generated from the tag library, so they drift.
- **Do not build** new card families or decision folders; merge candidate: generate cards from `tags/library/library.csv` + RULEBOOK rows.

## 6. Tag library
One row per element: meaning, data points served, rule, proof and certification counts, problems.
- **Entry** `data-team/tags/library/build_library.py`, `learn_from_filings.py`, `browser.html` · **Owns** `library.csv/json`, `learned_elements.csv`, `learned_labels.csv` (read back by the resolver), `company-overrides.csv`, `standard-tag-library.csv`, `proof_by_tag.*` · **Runs** tag-library-learn.yml · **Tests** `test_build_library.py`, `test_learn_from_filings.py` · **Doc** `data-team/tags/library/README.md`
- **Maturity 3.** Generated, never hand-edited, ~1 s, no DB; 27,999 rows, coverage 64.6% (`coverage.json`).
- **Gaps:** (1) built for resolver .85 (2026-11-20) while main is .87: not rebuilt on every resolver version as its README requires. (2) Only 581 of 27,999 rows have usage and 115 are full. (3) Three libraries: this one, `mapper/tag_library.py` (analytics.sec_tag_library, 0077, weekly pipeline-tag-library.yml) and `mapper/tag_library_rebuild.py` (company×tag×metric, 0128, pipeline-tag-library-rebuild.yml).
- **Do not build** a fourth. Merge candidate: make the two DB builds load `library.csv` instead of re-deriving.

## 7. Predictor, rules-as-data, blind exam, daily drill
Deterministic predictor maps a new filing's lines from rules; graduates per class at 99% blind accuracy (founder 2026-11-13).
- **Entry** `data-team/tags/exam/tools/predict.py`, `grade.py`, `backtest.py`, `scripts/ci/daily_drill.py`; `data-team/tags/tools/scoreboard.py`; `mapper/era_predictor.py` · **Owns** `data-team/tags/rules/*.csv` (761 rules at v7) + `rules/inbox/`, `exam/*-prediction.csv` (~900), `exam/eras/`, `exam/results/` · **Runs** pipeline-daily-drill.yml (07:41 UTC, commits to branch `drills`) · **Tests** `exam/tools/test_backtest.py`, `pipeline/tests/test_daily_drill.py`, `parity_v6_v7.py` · **Doc** `data-team/tags/exam/README.md`, `rules/README.md`
- **Maturity 3.** Versioned dev scores 82.4%→91.0% (v1→v6); blind 89.1% on hand-verified rows (NOW.md).
- **Gaps:** (1) far from the 99% / 200-company graduation bar; no class has graduated. (2) Rules and predict.py unchanged since 2026-11-13; drill misses land on branch `drills`, not as rule proposals. (3) Two rule systems: predictor rules in `tags/rules/*.csv`, resolver rules in code + `line_map/rules/`.
- **Do not build** a third predictor or rule format. Merge candidate: one rule store read by both predictor and resolver.

## 8. line_map structural resolver
For each 10-K, finds each data point's node by the filer's own face statement and calc tree; the source of truth per the one-path decision (doc 02, 2026-11-16).
- **Entry** `data-team/tags/line_map/tools/resolve_all.py` (+ resolve, resolve_is/bs/cf, standard_inputs, total_debt, filing_reads, gate*, split_resolver) · **Owns** `line_map/resolver/<TICKER>.csv` (110 companies), `line_map/rules/*.csv` (roles, polarity, absence_blocked, filer_xbrl_errors, ...), `line_map/CHANGELOG.md` · **Runs** tag-library-learn.yml, pipeline-daily-drill.yml, top100-auto-trigger.yml · **Tests** 29 `line_map/tools/test_*.py` (238 tests at .87) · **Doc** `line_map/README.md`, `data-team/tags/RULEBOOK.md`, `line_map/RESOLVER-OUTPUT-FORMAT.md`
- **Maturity 4.** Version .87; oracle 13 BAD of all dated read files (commit e8a7fe24); every rule indexed with code, test and source.
- **Gaps:** (1) RULEBOOK §7 lists ~50 rules with no test (C06-C31, F01-F03, X02-X33, I03-I25). (2) Most rules are Python branches, not data: a new filer quirk needs a code release. (3) Scope is the top-110 10-Ks only; no quarterly and no path to 1,000 measured.
- **Do not build** a second resolver or per-family resolver; extend `resolve_*.py` with a RULEBOOK row and a test.

## 9. Filing reads and the open-shown-fixes loop (X109)
Agents read the filing for every open shown cell and record VALUE / HIDE / RULE outcomes the resolver applies.
- **Entry** `line_map/tools/filing_reads.py`, `scripts/ci/top100_open_shown.py`; docmaps via `mapper/docmap_loader.py` · **Owns** `data-team/strategy/open-shown/<TICKER>.csv`, `open-shown-fixes/<TICKER>-<date>.csv` (130 files), `data-team/companies/reads/` (docmaps, `fixes/`), `line_map/rules/filing_read_cells.csv`, `filing_read_skips.csv`, `line_map/_filing-reads-skipped-*.csv` · **Runs** top100-flow.yml (open-shown export) · **Tests** `line_map/tools/test_filing_reads.py` · **Doc** RULEBOOK X109
- **Maturity 3.** 1,339 read cells applied at .87; latest-dated read wins.
- **Gaps:** (1) 745 reads skipped at .87: 361 HIDE rows lacked a hide class at the start of the free-text quote (format changed, old files never migrated) and 311 RULE rows never became rules. (2) Outcome, class and evidence live in a free-text `quote`; no schema check at commit. (3) 1,684 shown cells still OPEN in the top 100 (coverage summary 2026-11-21).
- **Do not build** another read format or fix folder; add a schema + validator to `filing_reads.py` and convert RULE rows into resolver rules.

## 10. Structural loader: writes into canonical_fact
Loads resolver decisions, docmaps and the tag map into `analytics.canonical_fact`, with guards.
- **Entry** `mapper/structural_loader.py`, `structural_direct.py` (enforce_resolver), `docmap_loader.py`, `company_tag_map.py` (`tagmap-plan`), `era_guard.py`, `derived_cells.py`, `certified_guard.py`; CLI `scrooner-map structural-load|docmap-load|tagmap-plan|era-guard|certified-guard|restore-before-image` · **Owns** `analytics.canonical_fact` rows for the top 100, `analytics.company_tag_map` (0122/0125), `company_combined_line`, before-images · **Runs** top100-flow.yml · **Tests** `test_structural_direct.py`, `test_resolver_enforce.py`, `test_*docmap*`, `test_*tag_map*` · **Doc** `data-team/strategy/ONE-PATH-DESIGN-2026-11-16.md`
- **Maturity 3.** Served value must equal the resolver value or is HELD (83 held, 256 later restatements kept; commit 51972357).
- **Gaps:** (1) four writer paths (structural, docmap, tag map, era predictor) layer onto one table; the resolver is not yet the only path (ONE-PATH step 3). (2) Sign/orientation fixed in two places on one day (cdd847d5, 96dcf648 vs proof e64bb98f). (3) 339 served cells differed from the resolver in the census.
- **Do not build** another loader; `normalizer/cell_loader.py` + `scrooner-cells` is the older one (see 25).

## 11. Proof (cell_proof)
Proves each served cell against the filing structure: PROVEN, DISAGREE, NOT_PRESENTED, UNCHECKED.
- **Entry** `proof/` (prove.py 1,595 lines, rules.py rule-scoped versions, shown.py, fsn.py, identities, perimeter, dims), `jobs/proof.py` (`scrooner-proof run --write`) · **Owns** `analytics.cell_proof` (0114) · **Runs** top100-flow.yml, pipeline-cells-proof.yml · **Tests** 24 `test_*proof*` files · **Doc** ONE-PATH-DESIGN, doc 02 "One path"
- **Maturity 4.** Rule-scoped re-proof (ONE-PATH step 1 shipped); top 100: 41,548 PROVEN, 139 DISAGREE, 414 UNCHECKED (summary 2026-11-21).
- **Gaps:** (1) `common/cell_rules.py` (ONE-PATH step 2) does not exist: period, sign, authority, page and part rules are copied in resolver, loader and prove.py. (2) Proof still re-decides in places instead of checking the resolver decision. (3) 553 DISAGREE+UNCHECKED cells with no owner queue.
- **Do not build** another checker of served values; build `common/cell_rules.py` and delete copies.

## 12. Sector templates and applicability
Which data points a company shows (no blank cells outside its template).
- **Entry** `mapper/sector_templates.py` (`seed-sector-templates`), `metrics/applicability.py`, `common/sector_applicability.py` (banks) · **Owns** `data-team/strategy/SECTOR-TEMPLATES-2026-11-01.md` (the templates file), `analytics.company_data_point_template` (0120), `data-team/47-fsn-store/template_company_outs_*` · **Tests** 4 `test_*sector*` · **Doc** templates file, doc 02 (2026-11-01 ruling)
- **Maturity 3.** Every top-100 company has a template row set; outs approved with evidence.
- **Gaps:** (1) templates are parsed from markdown tables, not a typed data file. (2) Applicability lives in three modules. (3) Insurer rules are thin (`tags/rules/insurer.csv`, 1 rule); REIT/utility/energy groups unmeasured.
- **Do not build** another applicability table; merge the three modules behind `sector_templates.py`.

## 13. Coverage and display state
Classifies every (company, data point, FY) cell and decides what the stock page shows or hides.
- **Entry** `mapper/top100_coverage.py` (2,460 lines), `pipeline/scripts/top100_coverage.py --write-display-state`, `mapper/cell_display_state.py`, `scripts/ci/top100_coverage_merge.py` · **Owns** `data-team/strategy/top100-coverage*.csv`, `analytics.cell_display_state` (0130) · **Runs** top100-flow.yml, top100-coverage-hourly.yml · **Tests** 13 `pipeline/tests/test_top100_*` · **Doc** `data-team/strategy/top100-coverage-README.md`
- **Maturity 3.** One class per cell; top 100: 43,973 shown, 42,289 shown values, 283 hidden rows, 523 hidden years (2026-11-21).
- **Gaps:** (1) 0130 is applied live but its file sits in `pipeline/db/pending/`; 0133 (hide class `only_after_tax_disclosed`) is not applied, so that class fails the live CHECK. (2) The app never reads `cell_display_state` (no reference under `apps/`). (3) Hard-wired to ranks 1-100/110.
- **Do not build** another coverage table or scoreboard; legacy coverage_matrix/coverage_snapshot (25) are not the measure.

## 14. Display certificate and certification registry
Approver certifies a company when every shown cell is a proven value or evidenced hide.
- **Entry** `certification/display_cert.py`, `display_cert_load.py`, `pipeline/scripts/certify_display.py`, schema `certification/schemas/display_certificate.v1.schema.json` · **Owns** `data-team/strategy/approvals/` (`registry.csv`, `certificates/*.json`, `requests/`, `*-certificate-*.md`), `certification/` coverage CSVs, `analytics.display_cell_certificate` (0132, pending) · **Runs** display-certify.yml, display-certify-auto.yml · **Tests** `test_display_cert*`, `test_*certif*` · **Doc** `data-team/strategy/approvals/CERTIFICATION-METHOD-2026-11-16.md`, `CERT-REGISTRY-rulings-2026-11-21.md`
- **Maturity 2.** 2 of 100 certified (GILD, JNJ); BA, MO, STX failed (`registry.csv`).
- **Gaps:** (1) 0131/0132/0134 not applied: certificates live only as files. (2) `registry.csv` has duplicate GILD/JNJ/STX rows and MSFT's certificate is an old-method .md only. (3) 32-cell draws give a 95% upper error of 8.9%, far above the 1.5% bar used for the predictor.
- **Do not build** another certification table; `certification/runner.py` + `company_certification` (0097) are legacy (25).

## 15. Verifier (Ritwik cloud lane + filing skill)
Independent filing checks of builder output before anything certifies.
- **Entry** `.claude/skills/scrooner-verify-against-filing/`, `verification/filing_kit.py`, agent `scrooner-data-verifier` · **Owns** `data-team/strategy/certification/*-verifier-sample-*`, `allowlist-check-*.csv`, `analytics.verifier_check` (0124) · **Runs** display-certify.yml (approver), live-sec-verification.yml (weekly) · **Tests** `pipeline/tests/verification/` · **Doc** `data-team/16-DATA-VERIFIER.md`, `data-team/strategy/VERIFIER-BRIEF-TEMPLATE.md`
- **Maturity 3.** Catches real errors: allowlist checks failed 9/20 (no_debt_interest) and 5 wrong hides (nothing_to_amortize), 2026-11-17.
- **Gaps:** (1) the lane is a manual session; no scheduled sampled re-check of certified companies. (2) Verdicts are spread over md/csv files plus 0124, not one table the certificate reads. (3) Sample size too small to bound error at 1.5%.
- **Do not build** another verifier kit; `incidents/verifier.py` is the legacy checker loop (25), not this.

## 16. Metric registry and calculators
Registry-as-data for every metric; calculators compute from canonical_fact.
- **Entry** `metrics/registry.py`, `registry/*.csv` (13 families, 84 metrics), `generate.py`, `engine.py`, `lock.py` + `formula_lock.json`, `provenance.py`; calculators `mapper/calculate.py`, `ttm.py`, `expanded_metrics.py`, `price_metrics.py`, `main_calculator.py` · **Owns** metric tables, `analytics.metric_lineage` view (0126) · **Runs** pipeline-refresh.yml (`refresh_valuations.sh`), pipeline-recompute.yml · **Tests** `test_metric_registry_agreement.py`, `test_metric_engine.py`, 7 `test_*metric*` · **Doc** `metrics/registry.py` docstring (no README yet)
- **Maturity 3.** Hand copies are generated from the registry and an agreement test pins them.
- **Gaps:** (1) 21 metrics `described` and 2 `planned`, not engine-wired. (2) Calculators read every canonical_fact row; only `provenance.py` reads cell_proof, so DISAGREE/hidden inputs can feed a metric. (3) No golden expected value per metric per company.
- **Do not build** a new formula table; add a registry row. Merge candidate: `main_calculator.py` registry vs `metrics/registry.py`.

## 17. Screener
Structured query → deterministic result over a precomputed snapshot.
- **Entry** `screener/` (query, evaluate, snapshot, schema), `jobs/screen.py`, `apps/backend/routers/screen.py` · **Owns** `analytics.company_screening_snapshot` (0061/0068), screen result tables (0060, 0074) · **Runs** pipeline-refresh.yml, pipeline-recompute.yml · **Tests** 10 `test_*screen*` · **Doc** `doc/execution-plans/14_Scrooner_Screener_Engine_Execution_Plan.md`, `doc/faster-loading/`
- **Maturity 3.** Versioned snapshot and result ids; deterministic evaluation.
- **Gaps:** (1) snapshot is built from all metrics, not only proven/shown cells. (2) No measured screen-result accuracy. (3) Last screener code change 2026-10-21.
- **Do not build** another query executor or cache.

## 18. AI query layer
Plain English → schema-validated structured query only (never a stock list or number).
- **Entry** `ai_query/` (rules.py rule-based interpreter, templates, aliases, normalizer, `llm_interpreter.py`), `jobs/ask.py`, `apps/app/app/api/ask` · **Tests** 10 `test_*ai_query*` · **Doc** `doc/execution-plans/15_Scrooner_AI_Query_Engine_Execution_Plan.md`
- **Maturity 3.** Rule-based interpreter with screen/edit templates.
- **Gaps:** (1) `llm_interpreter.py` is imported nowhere: no fallback for unmatched phrasing. (2) No evaluation set with a measured hit rate. (3) Vocabulary is not generated from the metric registry.
- **Do not build** a second interpreter; implement the existing `interpreter.py` contract.

## 19. Company pages and display API
Stock page, screener UI, account pages.
- **Entry** `apps/backend/company_page.py`, `routers/`, `metric_catalog.py` (generated from 16); `apps/app/app/stocks/[ticker]/page.tsx`, `apps/app/lib/company/` · **Tests** `apps/backend/tests/` (18), `apps/app` vitest · **Doc** `apps/app/AGENTS.md`, `doc/design/`
- **Maturity 2.** Pages serve from `analytics.canonical_fact` directly (`company_page.py`).
- **Gaps:** (1) hidden rows/years and `cell_display_state` are not honoured. (2) badges (`combined:<label>`, DERIVED) and R-page links not shown. (3) No end-to-end check that a page cell equals the certified cell.
- **Do not build** a new API service; extend `company_page.py`.

## 20. Top-100 flow and CI
Per-company chain: no-filing check → docmap-load → structural-load → tagmap-plan → proof → era-guard → coverage → certified guard.
- **Entry** `scripts/top100_flow.sh`, `scripts/ci/top100_*.py`, `changed_areas.py`, `.github/scripts/check_workflow_health.py` · **Runs** top100-flow.yml, top100-auto-trigger.yml, ci.yml, workflow-health-check.yml (29 workflows) · **Tests** `test_top100_changed.py`, CI against Postgres 16 · **Doc** `data-team/strategy/GITHUB-INFRA-AUDIT-2026-11-16.md`
- **Maturity 4.** Resolver change triggers the flow for changed companies; certified companies are restored on regression.
- **Gaps:** (1) one commit per company per run on main ("Coverage row for company N", ~100 per run). (2) Fixed to the top 110 ids. (3) Many dispatch-only workflows (fsn-pilot/cohort/write, bs/cf port gates) with no owner or retirement date.
- **Do not build** another orchestrator script; add a step to `top100_flow.sh`.

## 21. Nightly refresh
Daily SEC index, prices, freshness gate, screener snapshot.
- **Entry** pipeline-refresh.yml (12:23 UTC), `reprocess_recent_filers.sh`, `refresh_valuations.sh`, `scrooner-operations --fail-on-alert`; pipeline-sanity.yml · **Doc** workflow comments
- **Maturity 2.** Runs daily with a write-in-progress guard, but on the old path.
- **Gaps:** (1) reprocesses new filers through old normalize+map, not FSN→resolver→flow. (2) FSN incremental flag off. (3) rebuilds legacy coverage matrix and tag candidates daily that gate nothing.
- **Do not build** a second nightly; move steps of this one onto the new path.

## 22. Migrations ledger
- **Entry** `pipeline/db/migrations/`, `pipeline/db/pending/`, `SKIPPED.txt`, `scripts/check_migrations.py`, `scripts/migration_ledger.py`, `scripts/ci/replay_pending_migrations.py`; claims in `doc/planning/53_Multi_Session_Collaboration_Plan_2026-10-13.md` · **Runs** ci.yml, migrations-pending-replay.yml
- **Maturity 4.** Contiguity enforced in CI; pending files replayed in CI.
- **Gaps:** (1) `ops.migration_ledger` (0131) not applied: what is live is known only from doc 53 prose. (2) 0130 applied but still in pending/. (3) Six pending files (0129-0134) wait on approvals.

## 23. Mind (shared memory)
- **Entry** `mind/mind.py` (search/get/add/promote/lint/stats) · **Owns** `mind/entries/` (258), `mind/inbox/` (39 on main) · **Runs** mind.yml · **Tests** `mind/test_mind.py` · **Doc** `mind/README.md`
- **Maturity 3.** Gated promotion, lint for dead paths, gap logging.
- **Gaps:** (1) last curation 2026-11-09; local checkout holds many uncommitted inbox files. (2) Founder/Dhairya rulings are captured as mind entries, which are hints, not the decision register. (3) No link from an entry to the rule id it produced.

## 24. Agent roles, skills, routing
- **Entry/Owns** `.claude/agents/` (12), `.claude/skills/` (5), role docs `data-team/09-` to `19-`, `AGENTS.md`, `CLAUDE.md`, `scripts/agent_context.py` · **Maturity 3.**
- **Gaps:** (1) the shared checkout has all 12 agent files modified and uncommitted. (2) Live lanes (Dhairya, Ritwik) are sessions, not defined roles. (3) `18-REPORTED-NUMBERS-CHECKER.md` has no agent.
- **Do not build** new roles for one task; brief an existing agent.

## 25. Legacy and superseded (learning only; never gate, never extend)
- Old canonical mapping: `mapper/concepts.py`, `resolve.py`, `concept_fallback.py`, `parsers/`, analytics.concept_mapping + company_tag_preference (0051/0072): replaced for the 1,000 by sections 8-10 (founder 2026-11-04/11).
- Patch packages and slot records: `data-team/41-`/`42-release-applies-*`, `pipeline/scripts/slot_records/`, `*_release.py` modules, `pipeline/scripts/split_release_*`: superseded 2026-11-04.
- Family cell-file write path: `normalizer/cell_loader.py`, `scrooner-cells`, `data-team/46-canonical-fact-v2/`, pipeline-fsn-write.yml, cells-load*.yml: not used by `top100_flow.sh`.
- Old checkers: `sanity/`, `yfinance_financials/`, `frames/`, `incidents/`, `mapper/coverage_matrix.py`, `coverage_snapshot.py`, `tag_candidates.py`, `data-team/strategy/scoreboard/`, `certification/runner.py` (invariants I1-I11, pipeline-certify.yml), `company_certification` (0097).
- Old inventories: `doc/data-moat/SYSTEMS.md`, `doc/reference/44_Scrooner_Systems_Index.md`.
- Other product data (current, outside the cell chain): `ownership/`, `segments/`, `corporate_actions/`.

## Before you build
1. Search this file (`rg -n "<term>" data-team/SYSTEMS.md`) and the owning system's doc.
2. Extend the owning system: a rule row, a test, a registry row, a flow step. Never a parallel copy.
3. A new system, module family, registry, table or file family needs a one-line reason added here first (and a migration claim in doc 53 if it is a table). Update the owning block when a gap closes.

## Interconnection map
Founder 2026-11-22: "everything should be interconnected so well." Written 2026-11-22 from the workflow `on:` blocks on main. Trigger: **E** event (push/workflow_run), **S** schedule, **M** manual (a person or session dispatches, relays a sha or commits a file). **GAP** = a manual link, with the system that should own its automation. Switches: `AUTO_LOOP` (on since 2026-11-16) gates top100-auto-trigger and display-certify-auto; `AUTO_FLOW_ON_RESOLVER` (unset = off; founder turns it on) gates top100-auto-trigger on its own.

| # | System | Reads | Writes | Trigger | Triggers next | Manual link (GAP → owner) |
|---|---|---|---|---|---|---|
| 1 | SEC access | sec.gov | `raw.*`, Storage | S pipeline-refresh 12:23Z; M onboard-* | 3 normalizer (same run) | onboarding dispatch → 2 |
| 2 | Company master | raw submissions, prices | `core.company`, history source | M onboard-company-identity/filings | 1, 3 | GAP: a new top-N company is dispatched by hand → 2 (rank change event) |
| 3 | Normalizer | `raw.*` | `core.fact`, filing, period | S nightly reprocess | old map chain (legacy) | GAP: new filers do not go on to 4→8 → 21 |
| 4 | FSN + standard extract | `fsn.*` | 7 extract JSON (artifact) | M pipeline-fsn-load-filings, pipeline-standard-extract | E tag-library-learn | GAP: new filing → FSN load → extract is dispatched by hand (nightly flag off) → 21 |
| 5 | Tag knowledge | library, verifier notes | cards, ledger, quirks | M sessions | none | GAP: cards not generated from 6 → 6 |
| 6 | Tag library | resolver/*.csv, rules, proof_by_tag, certification CSVs, pattern hits | library.*, pattern_hits.csv, `pattern-intake.csv` | E tag-library-auto-rebuild (resolver/** push); E verifier-fail-intake (registry.csv push); E tag-library-learn | commits generated files on main | learned labels: data branch → main by tag expert (review gate, keep); DB copy (0128) M → 6 |
| 7 | Predictor + drill | exam, rules | branch `drills` | S daily drill 07:41Z | none | GAP: drill misses do not open `rules/inbox/` proposals → 7 |
| 8 | Resolver | extract JSON, rules, filing reads | resolver/<TICKER>.csv | M a session runs `resolve_all.py` and commits | E top100-auto-trigger → top100-flow; E tag-library-auto-rebuild; E pipeline-tag-library-rebuild (DB dry run) | GAP: extract → resolve → commit is by hand (learn's resolver output goes to a data branch) → 8 |
| 9 | Filing reads | open-shown/<T>.csv, filings | open-shown-fixes, reads/ | M read sessions | 8 (next resolver release reads them) | GAP: open-shown file → read assignment by hand → 9 |
| 10 | Structural loader | resolver, docmaps | `canonical_fact`, tag map | E/M top100-flow | 11 (same chain) | none (in chain) |
| 11 | Proof | canonical_fact, FSN | `cell_proof` | E/M top100-flow | 13 (same chain) | DISAGREE cells have no queue → 11 |
| 12 | Sector templates | templates md | template table | M `seed-sector-templates` | 13 | GAP: template edit → reseed by hand → 12 |
| 13 | Coverage/display state | canonical_fact, proof, templates | coverage CSVs, `cell_display_state`, open-shown | E top100-flow publish; S hourly 17 * * * *; E after flow | 9 (open-shown files); 14 (gate) | none |
| 14 | Certify request + certificate | coverage CSV | requests/<T>-request (coverage path, resolver file + `resolver_version`), certify-out branch | E top100-flow publish on gate PASS (gate = 0 OPEN, incl. the verifier self-check once it lands in the flow); E display-certify-auto | display-certify (judge) → branch certify-out/run-<id> | GAP: approver commits verdict, certificate and registry row by hand (approver ≠ preparer; keep the person, automate the copy) → 14 |
| 15 | Verifier | certify-out draws, filings | registry.csv rows, draw md | M Ritwik lane; S live-sec-verification Mon | E verifier-fail-intake → 6 | GAP: no scheduled re-check of certified companies → 15 |
| 16 | Metric registry | canonical_fact | metric tables | S nightly `refresh_valuations`; M recompute | 17 | GAP: a certified company does not trigger recompute → 16 |
| 17 | Screener | metrics | screening snapshot | S nightly | 19 | follows 16 |
| 18 | AI query | registry aliases | none | request | 17 | vocabulary not generated from 16 → 18 |
| 19 | Company pages | backend API | none | request | none | page does not read `cell_display_state` → 19 |
| 20 | Flow + CI | git, DB | as 10-14 | E push (ci, auto-trigger); M top100-flow | 13, 14, hourly export | GAP: top100-flow beyond resolver changes (new company, rule-only change in `line_map/rules/*`) is dispatched by hand → 20 |
| 21 | Nightly refresh | SEC, DB | as 1, 3, 16, 17 | S 12:23Z | old path | GAP: does not run 4 → 8 → flow → 13 → 14 → 21 |
| 22 | Migrations | migration files | live DB | M founder's typed go | none | by design (founder gate) |
| 23 | Mind | inbox | entries | M curator | none | GAP: curation by hand (last 2026-11-09) → 23 |
| 24 | Agent roles | role docs | none | M sessions | none | GAP: Dhairya relays shas and briefs by hand → 24 |

New 2026-11-22 (reasons, per "Before you build"): `tag-library-auto-rebuild.yml` (owner 6: pattern detectors when present, then `build_library.py` with `PYTHONHASHSEED=0`, library tests, commit only if `library.csv` or `pattern_hits.csv` changed; it regenerates a pure function of main, unlike tag-library-learn which learns new labels and stays on a data branch), `verifier-fail-intake.yml` + `data-team/tags/library/pattern_intake.py` + `pattern-intake.csv` (owner 6, worked by the tag expert: one append-only row per registry FAIL verdict, keyed ticker|date|coverage_sha256; status/pattern_id/resolution are the tag expert's), `AUTO_FLOW_ON_RESOLVER` (an own switch for the 8 → 20 link inside top100-auto-trigger, no second dispatcher). Tests: `test_pattern_intake.py`, `pipeline/tests/test_top100_gate_request.py`, `test_top100_changed.py::test_per_company_resolver_files_scope_the_flow`.

## World-class scorecard
Founder 2026-11-22: "all the systems in SYSTEMS.md should be world class." Score today is the Maturity in each block above; update the row when a block's score or gap changes.

**The 5/5 bar (every system):**
1. One owner and one source: no parallel copy of its data, rules or code (the "Do not build" line is empty of merge candidates).
2. Rules and knowledge are tested data or code, not prose.
3. Every rule has a CI test that fails without it (mutation-checked).
4. A live metric with a target, published daily.
5. Failures become rules or patterns automatically (a miss opens a rule proposal, not a note).
6. Runs on data change, not by hand.

Waves: **1** in flight 2026-11-22 (verifier/tag-expert pattern loop + flow self-check, filing reads, proof stale fix, screener exclusion reasons, metric registry definitions, display path steps 1-4) · **2** systems at score 2 (display certificate, company pages / display path steps 5-6 needing migrations 0133+0135 with founder approval, nightly refresh) · **3** the remaining 3s and the "Do not build" merges · **4** all at 5, then scale to 1,000.

| # | System | Today | 5/5 test (measurable) | Metric, target | Next step | Wave |
|---|---|---|---|---|---|---|
| 1 | SEC access | 4 | 0 SEC fetch paths outside `sec_rate` (grep test in CI); cross-runner total enforced, not hand-split | max observed req/s across all runners, <=2.0 | route `eps_face_read.py` and `slot_records/common.py` through `sec_rate`; drop `secfetch` | 3 |
| 2 | Company master | 3 | every top-1,000 predecessor/new-CIK window has a 10-K in FSN (XOM case); sector from filing, tested | companies with a history break, 0 | predecessor check in onboarding fails on a window with no FSN 10-K | 3 |
| 3 | Normalizer | 3 | nightly new filers go FSN→resolver, not old normalize+map; authority rule in one module | old-path reprocess runs, 0 | authority rules into `common/cell_rules.py` (shared with 11) | 3 |
| 4 | FSN store | 4 | new filing in FSN extract within 24 h, flag on; 10-Q in extract; missing filings a query, not a CSV | filings filed but not extracted, 0 after 24 h | turn on FSN nightly incremental in pipeline-refresh.yml | 3 |
| 5 | Tag knowledge | 3 | cards generated from `library.csv` + RULEBOOK, one key per element; every verifier miss lands as a card/pattern row | cards older than the resolver version, 0 | verifier/tag-expert pattern loop: miss → pattern row → card | 1 |
| 6 | Tag library | 3 | rebuilt on every resolver version; the two DB builds load `library.csv` | library resolver version = main (.85 vs .87 today); rows with usage 581/27,999 → all served | rebuild in tag-library-learn.yml on resolver change; merge `tag_library*.py` | 3 |
| 7 | Predictor | 3 | one rule store shared with the resolver; drill misses auto-open rule proposals | blind accuracy per class, >=99% on 200 companies (89.1% today) | drill misses from branch `drills` → `rules/inbox/` proposals | 3 |
| 8 | Resolver | 4 | every RULEBOOK rule has a test (~50 untested in §7); quirks as data rows | untested rules 0; oracle BAD 0 (13 today) | tests for C06-C31, F01-F03, X02-X33, I03-I25 | 3 |
| 9 | Filing reads | 3 | read rows schema-validated at commit; RULE rows become resolver rules | skipped reads 0 (745 at .87); open shown top 100, 0 (1,684) | schema + validator in `filing_reads.py`; migrate the 361 HIDE rows | 1 |
| 10 | Structural loader | 3 | resolver is the only writer (ONE-PATH step 3); sign fixed in one place | served != resolver, 0 (339 in census); held cells 0 (83) | retire docmap/tagmap/era writer layers behind the resolver | 3 |
| 11 | Proof | 4 | proof checks the resolver decision, never re-decides; no stale proof rows; `common/cell_rules.py` exists | DISAGREE+UNCHECKED top 100, 0 (553); stale proofs 0 | proof stale fix; then `common/cell_rules.py` | 1 |
| 12 | Sector templates | 3 | templates a typed data file; one applicability module; every group measured | groups with measured template coverage, all (insurer 1 rule; REIT/utility/energy unmeasured) | templates markdown → CSV with a loader test | 3 |
| 13 | Coverage/display state | 3 | every shown cell one class; app reads `cell_display_state`; any rank set, not 1-100 | shown cells not value-or-evidenced-hide, 0 (1,684 OPEN) | display path steps 1-4; move 0130 out of pending/ | 1 |
| 14 | Display certificate | 2 | certificates in the DB (0131/0132/0134); one registry row per company; draw size gives <=1.5% upper error at 95% | certified of top 100, 100 (2 today); 95% upper error <=1.5% (8.9% at 32 cells) | dedupe `registry.csv`; raise draw size; certificate reads verifier table | 2 |
| 15 | Verifier | 3 | 0 certified-company regressions; error bound <=1% at 95% via sample size; re-check all certified weekly, scheduled | certified regressions 0; sampled error <=1% at 95% | verdicts into `analytics.verifier_check` only; weekly scheduled re-check | 1 |
| 16 | Metric registry | 3 | all 84 metrics engine-wired; inputs only proven/shown cells; golden value per metric per company | described/planned metrics 0 (21+2); golden mismatches 0 | write definitions for the 21 `described`; calculators read cell_proof | 1 |
| 17 | Screener | 3 | snapshot built from proven/shown cells only; every excluded company has a reason | screen-result accuracy measured on a golden set, 100%; unexplained exclusions 0 | exclusion reasons on snapshot rows | 1 |
| 18 | AI query | 3 | eval set with measured hit rate; vocabulary generated from registry; fallback wired | eval-set hit rate, target >=95% (none today) | build the eval set from registry aliases | 3 |
| 19 | Company pages | 2 | page cell = certified cell, end-to-end CI test; hides, badges and R-page links shown | page cells != certified cell, 0 | display path steps 5-6 (migrations 0133+0135, founder approval) | 2 |
| 20 | Flow + CI | 4 | flow self-checks each step; one commit per run, not per company; every workflow has an owner/retire date | flow steps without a post-check 0; unowned dispatch-only workflows 0 | flow self-check; batch coverage commits | 1 |
| 21 | Nightly refresh | 2 | new filings flow FSN→resolver→flow→proof→coverage nightly with no hand step; legacy rebuilds removed | filings served within 24 h of acceptance, 100% | move reprocess onto the new path; drop coverage-matrix/tag-candidate steps | 2 |
| 22 | Migrations | 4 | live state is a query (`ops.migration_ledger`, 0131), CI diffs it with main | live-vs-main drift 0; applied files in pending/ 0 (0130) | apply 0131 with founder approval | 3 |
| 23 | Mind | 3 | every entry links the rule id it produced; inbox curated daily | inbox age max <=2 days (last curation 2026-11-09) | rule-id field + lint in `mind.py` | 3 |
| 24 | Agent roles | 3 | every live lane a committed role file; agent files clean on main | uncommitted agent files 0 (12 today); roles without agent 0 | commit the 12 files; role for `18-REPORTED-NUMBERS-CHECKER` | 3 |
| 25 | Legacy | n/a | nothing in the chain imports or gates on a legacy module (CI import test) | legacy imports from live paths, 0 | retire after each wave-3 merge lands | 3 |
