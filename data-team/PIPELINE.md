# Scrooner data pipeline: target specification

Founder-approved target, 2026-11-28; approver review applied the same day (data-team/strategy/approvals/PIPELINE-review-approver-2026-11-28.md) (six stages; see the "Target architecture" section in [`SYSTEMS.md`](SYSTEMS.md)). This file is the engineering contract: what each stage takes, produces and guarantees, and how the pipeline scales from 100 to 5,000 companies without adding people. SYSTEMS.md stays the inventory of modules. If code and this file disagree, raise it in the owning stage; don't build around it.

**Status labels:** **LIVE** means it runs on main today. **PARTIAL** means part of it exists (the gap is named). **TARGET** means not built yet. Any new table named here needs a migration claim in doc 53 and the founder's typed words before it is applied.

---

## 1. Design principles (non-negotiable)

1. **One path.** Every company goes through the same six stages. There are no per-company scripts, per-family writers or side doors. A special case is a rule row, not code.
2. **The unit of work is (company, filing).** Every stage is keyed by `cik` + `accession_number`, plus a version (rule-store version, proof version). Work is partitioned by company, so it parallelizes linearly.
3. **Idempotent and replayable.** Running a stage twice with the same inputs and versions gives the same output and writes nothing new. Any output can be rebuilt from the raw store plus the versions. Collector data is immutable.
4. **Event-driven, not schedule-driven.** A stage runs because its input changed (a new filing, a new rule-store version, a rank change), never because someone dispatched it. Schedules exist only as a catch-up sweep.
5. **Exceptions only.** Machines handle the normal case. People and agents work a queue of exceptions, and each closed exception becomes a rule, so it never recurs for any company.
6. **Truth from the filing.** A value is shown only if it is PROVEN against the filing, or HIDDEN with an evidenced reason. AI never produces a value.
7. **Versioned everything.** Rules, formulas, proof logic and templates carry versions. Every served cell records the versions that produced it, so a change re-runs exactly the cells it affects.
8. **Measured, not claimed.** Each stage publishes its metrics daily. Correctness is a measured error rate with a confidence bound, never "100%".

---

## 2. The pipeline

```
 trigger: new filing | rule-store version | rank change | template change
     |
 [1 INGEST] -> [2 KNOW] -> [3 RESOLVE] -> [4 PROVE] -> [5 CERTIFY] -> [6 SERVE]
     |            ^             |             |             |
     |            +---- exceptions queue <----+-------------+
     |                 (each closed exception becomes a rule row)
 orchestrator: one per-company run, sharded, budgeted, resumable
```

### Stage contracts

| Stage | Input | Output (system of record) | Idempotency key | Guarantee | Status |
|---|---|---|---|---|---|
| 1 Ingest | sec.gov (submissions, companyfacts, filing XBRL) | `raw.*` (immutable), `fsn.*` (filing structure: report, line, calc_arc, value), `core.fact` (SEC API standard-tag values), `core.company` | `cik`, `accession_number`, content hash | lossless; a filing is either fully stored or absent; never normalized | LIVE for raw/core; PARTIAL for fsn (new filings only by manual `pipeline-fsn-load-filings` while `FSN_NIGHTLY_STAGE` is off) |
| 2 Know | verifier misses, drill misses, filing reads, tag-expert review | **one rule store** (`data-team/tags/library/library.csv` + `tags/rules/`), versioned; cards generated from it | rule id + store version | one source for predictor, resolver and readers; every rule has a test | PARTIAL (predictor, resolver and filing reads keep separate stores; merge M2) |
| 3 Resolve | fsn structure + `core.fact` + rule store | `analytics.canonical_fact` (only writer: resolver via the structural loader) | `cik`, accession, cell key, rule-store version | deterministic; same inputs and version give the same cells; one writer | PARTIAL (older docmap/tagmap/era layers still write) |
| 4 Prove | canonical_fact + filing + templates | `analytics.cell_proof`, then one state per cell: PROVEN, HIDDEN with reason, or OPEN (`cell_display_state`) | cell key + proof version | proof checks the resolver's decision and never re-decides; identities hold per company-year; **owns the badge and parts contract**: a `derived:` cell carries parts from one filing, an as-printed cell never has a formula locator (rule 2b78da15), and identity inputs obey the one-vintage rule (X87; the LLY revenue reprint) | PARTIAL (`cell_display_state` migrations 0130/0133 in `pending/`) |
| 5 Certify | cell states + census checks + a stratified sample checked against the filing | `analytics.display_cell_certificate` + registry status | ticker + `coverage_sha256` + judge version (a re-draw happens only on a new coverage sha) | **all census checks pass** (badges, per-share, debt, derived, hides: every real FAIL so far came from these) **and** the sampled error is at most 1.5% upper bound at 95% (199-cell draw); approver is not the preparer; a certified company that changes is **held**: its certificate is marked stale (the company stays shown, labelled not currently certified), and no changed cell is ever shown as certified until a new certificate on the new coverage sha is recorded by the approver (founder delegated the call, 2026-11-28: "rest choose yourself") | LIVE (0131/0132/0134); auto re-check TARGET |
| 6 Serve | PROVEN cells only + metric registry | metric values, screener snapshot, AI query vocabulary, pages | metric id + formula version + input cell versions | no metric reads an unproven cell; every exclusion has a reason; AI emits only schema-valid queries | PARTIAL (calculators read canonical_fact, not proof; merge M3) |

### Data contract between stages
- Every row a stage writes carries `cik`, `accession_number` (or period key), `produced_by` (stage and module), and the version(s) used. A downstream stage never reads a row without these.
- Stages communicate only through their system-of-record tables and the event log (section 3). No stage reads another stage's working files.
- Schema changes go only through a committed migration (doc 53 claim, contiguous number, the founder's typed words to apply).

---

## 3. Orchestration (TARGET; merges `top100_flow.sh` and the nightly refresh)

- **Event log** (TARGET table, migration to be claimed): one row per trigger (`new_filing`, `rule_version`, `rank_change`, `template_change`) with `cik`, cause and the versions involved. Producers: the collector (new accession), the rule-store release, the rank job, the template seed.
- **Planner:** turns events into per-company work items, `(cik, from_stage, versions)`, deduplicated. A rule-version event targets only the companies whose cells the rule touches (from the rule store's usage index), not everyone.
- **Workers:** company-disjoint shards within the connection budget in doc 02 (founder decision 2026-11-13; cite it, don't restate it here). Each worker takes one company at a time and runs stages 1-4 and 6 in order. For stage 5 it only runs the judge read-only and files a certify request. **Only the approver records the verdict, the registry row and the certificate**, so the preparer never certifies its own output. The DB certificate load stays a production write that needs the founder's typed words. Each stage commits per company in one transaction and records a checkpoint, so a crash resumes at the last finished stage.
- **Backpressure:** a worker checks client backends before each write against the pause threshold in doc 02, sets its own `statement_timeout` and wall-clock cap, and yields while an FSN production write or the nightly refresh holds the lock (`heavy_job_guard.sh`).
- **Failure handling:** retry transient errors (SEC 5xx, pooler drop) with backoff, at most 3 times; then put the item in a dead letter with the error class. A dead-lettered company never blocks the others. Dead letters are a queue with an owner, reported nightly.
- **Catch-up sweep:** once a day, plan every company whose served versions lag the current versions. This replaces hand dispatches.

---

## 4. The exceptions queue (the human/agent interface)

One queue (TARGET table; today OPEN cells, DISAGREE proofs, verifier FAILs and refused resolver refreshes live in separate files).

| Exception | Source | Owner | Closes when |
|---|---|---|---|
| OPEN cell (no proof, no evidenced hide) | stage 4 | resolver lane | a rule row resolves it, or an evidenced hide is recorded |
| DISAGREE (resolver vs proof) | stage 4 | proof lane, then resolver | root-cause family fixed by a rule, with a test |
| Census FAIL (badge, per-share, debt, derived, hide) | stage 5 | resolver or proof lane, by family | the check passes on a new coverage sha |
| Sample FAIL | stage 5 | verifier, then tag expert | pattern row plus rule; the company is re-drawn |
| NEEDS_READ / REVIEW (a drawn cell the machine check can't settle) | stage 5 | approver | the read is recorded; a read class that recurs becomes a `draw_check` rule (BMY's undimensioned AccountsReceivableNetCurrent note fact needed 9+ reads) |
| Drill miss | stage 2 | tag expert | rule proposal accepted or rejected with a reason |
| Dead-lettered company | orchestrator | data engineer | rerun passes |

Every item records its root-cause family. Work is prioritized by **cells affected across all companies**, not by ticker. Closing an item without a rule or a test is not a close.

---

## 5. Scaling plan

**SEC budget:** 2 requests/second total across all agents and runners (founder 2026-11-17), about 172,800 requests a day. An FSN filing build takes about 15 requests (SYSTEMS.md, `FSN_NIGHTLY_STAGE` note).

| Load | Filings | SEC requests | Time at 2 req/s |
|---|---|---|---|
| Steady state, 1,000 companies (~4 filings a year each) | ~4,000 a year; peak season ~150 a day | ~2,250 a day at peak | under 20 minutes a day |
| Backfill, 1,000 companies, 10-Ks and 10-Qs since 2015 (~44 each) | ~44,000 | ~660,000 | ~3.8 days, one time |
| Steady state, 5,000 companies | ~20,000 a year; peak ~750 a day | ~11,250 a day at peak | ~1.6 hours a day |

The SEC budget isn't the constraint. **The constraints are the exceptions rate and the DB.** So:
- **Auto-map graduation:** a class of line maps new companies with no reading once its blind accuracy is at least 99% on at least 200 rows (block 7). The share of cells in graduated classes is the scale lever, reported daily.
- **DB:** writes are batched per company (never per row); per-company transactions; slow views (for example `company_certification_derived`, over 5 minutes for one company) get materialized or indexed before the cohort grows.
- **Cohort ladder** (founder 2026-11-13): top 100 at an exceptions queue close to zero, then an end-to-end test, then 500, 1,000, 2,000 and 5,000. A cohort enters only when the previous one's exception rate per company is at or below the target, so the queue doesn't grow faster than it closes.

---

## 6. SLOs and metrics (published daily, per cohort)

| Metric | Target | Stage |
|---|---|---|
| Filing acceptance to certified company | 24 h | all |
| Exceptions queue size; inflow vs outflow per day | outflow ≥ inflow; top 100 close to 0 | 4-5 |
| Shown cells that are PROVEN or HIDDEN with a reason | 100% | 4 |
| Sampled error upper bound (95%), per company | ≤ 1.5% | 5 |
| Pooled sampled error upper bound (95%), all certified companies | ≤ 0.10% | 5 |
| Census checks failing on certified companies | 0 | 5 |
| Cells in auto-map-graduated classes | rising to ≥ 95% | 2 |
| Dead-lettered companies older than 24 h | 0 | orchestrator |
| Metrics reading unproven inputs | 0 | 6 |
| Hand dispatches per day | 0 | orchestrator |

---

## 7. Migration path from today (merge order)

| Step | What | Gate |
|---|---|---|
| M1 | FSN path in the nightly run (`FSN_NIGHTLY_STAGE` load, then write); retire the old reprocess for the 1,000 | 155 top-100 DISAGREE cleared + the founder's typed words |
| M2 | one rule store for predictor, resolver and filing reads; drill and verifier misses become proposals automatically | tests mutation-checked |
| M3 | blocks 13-15 merged into one cell state + sampled certificate; calculators read PROVEN cells only | migrations 0130/0133 applied (founder) |
| M3 progress (2026-11-28) | calculators behind rule `serve.shown_cell_path@1` (default off, `common/rule_flags.py`). SWITCHED: `mapper/calculate.py`, `mapper/ttm.py` (via `mapper/shown_source.py`). REMAINING: `expanded_metrics.py:459`, `price_metrics.py:123/146/244`. **HARD GATE for turning the flag on: the shown view has FY and instant grain only, so quarter metrics (quarterly and TTM rows) would disappear. The flag must NOT go on until quarter grain is in the shown view or a per-grain fallback rule is decided.** Also needs 0130/0133/0135 applied (founder) | one file per commit |
| M4 | event log + planner + resumable workers replace `top100_flow.sh` dispatch and the nightly reprocess | migration claim + the founder's typed words |
| M5 | one exceptions queue table; all lanes work from it | migration claim |
| M6 | cohort ladder: 101-1,000 enter through the same path | top-100 queue close to 0 |

### M2 design: one rule store (2026-11-28; step 1 landed, rest TARGET)

**Inventory (counts at origin/main).** Predictor `tags/rules/*.csv`: 815 rows in 9 files (494 tag, 110 combined_concept, 53 data_point, 40 validation, 26 override, 92 other); read by `exam/tools/predict.load_kb`, `mapper/tag_library_rebuild.py`; written by the tag expert via `rules/inbox/` + backtest. `rules/inbox/`: `drill-auto.csv` 423 open proposals (written by `daily_drill`), `STATUS.csv` 446 rows (440 ids not in the store: drill ids), one accepted proposal file. Resolver `tags/line_map/rules/`: `roles.csv` 45 data points (144 alternative elements), `polarity.csv` 26, `filing_read_cells.csv` 1,801 (VALUE 1,555, HIDE 246), `text_disclosures` 127, plus eight keyed side files (filer_xbrl_errors, fsn_dropped_facts, absence_blocked, interest_dividend_lines, lease_location_text, net_interest_line_not_of_income, non_economic_share_classes, map_conflicts_reviewed); read by `resolve_*.py`, `standard_inputs`, `common/{polarity,filer_xbrl_errors,fsn_dropped_facts}.py`, `mapper/structural_loader.role_stmts`; written by the resolver lane and `filing_reads.py`. `library.csv` is built (Storage, not git) from these and read through `mapper/library_csv.py`.

**Overlaps.** Key (stmt, element): 123 resolver role elements meet a predictor tag rule; 0 HARD contradictions (predictor maps to another concept), 27 SOFT (predictor says component/combined/excluded for an element the resolver takes directly, e.g. BS ReceivablesNetCurrent, IS NoninterestExpense; reviewed baseline `library/rule-store-known-conflicts.csv`). Key (cik, data_point): 5 predictor overrides meet filing-read VALUE rows; 3 name another element (DHR cash, MCD weighted shares). 4 elements sit under two data points in roles.csv. `filing_read_cells.element` is truncated for long names ("WeightedAverageNumberOf...SharesOutstanding"): not joinable to a rule key. Same rule in two places: `is.operating_expenses.procedure` (active plus accepted inbox copy). Polarity (sign) exists only in the resolver; the predictor has none.

**Target schema (one CSV family, `tags/rules/store/*.csv`, generated views for the old files):** `rule_id, class, element, action, scope, version, evidence, test_id, status` (+ `when`/`then` JSON for predictor-only parameters). class = predictor kind or resolver class (role_alt, polarity, filer_error, dropped_fact, text_disclosure, filing_read); scope = all | ticker | accession | `stmt:data_point`; status = proposed | active | retired; `test_id` is required for active rows (the CI test that fails without it). A drill or verifier miss opens a `proposed` row (drill-auto already does).

**Loader.** `tags/rules/rule_store.py` (stdlib, read-only): `load_predictor/load_resolver/load_inbox` into one `Rule` record, views `tag_decisions`, `overrides`, `role_rows`, `polarity`, `conflicts`. Step 1 changes no reader.

**Plan.** (1) Landed: loader, parity tests (views equal `predict.load_kb` K['lib'] and K['ov'], `resolve_all.ROLES`/`POLARITY`), contradiction check against the reviewed baseline (new conflict fails CI, closed one must leave the list). (2) Next: predict.load_kb reads through the loader (VERSION hash must stay identical; `parity_v6_v7`-style row diff = 0). (3) Resolver release .94: `resolve_*.py` and `common/polarity.py` read through the loader; resolve each SOFT baseline row (decide the right store), then delete the baseline. (4) Move the side files into `store/` with `test_id`; old paths become generated views. (5) `filing_reads.py` writes RULE rows as `proposed` rows; drill/verifier intake feed the same file.

**Rule for every session:** name the stage and step (M1-M6) your work moves. Don't build anything outside it. Report movement in the section 6 metrics, not in activity.
