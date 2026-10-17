# Scrooner infrastructure map — read this first, then your role file

Written 2026-10-17 from the live repository and database. The pack's other files were written without inspecting Scrooner ("No live Scrooner database or repository was inspected", 03). This file fills that gap. **Numbers below were measured on 2026-10-17: remeasure before quoting them** (pack rule: stale counts are claims, not facts).

Precedence if files disagree: root `CLAUDE.md` and `pipeline/CLAUDE.md` > `doc/data-moat/*` > this map > the generic role files. The role files say "discover the repository"; this is the discovered result.

## 1. What the company is, in one paragraph
Scrooner is a US-stock fundamental screener. Its moat is SEC EDGAR data parsed once, normalized, mapped to canonical concepts, with every number traceable to a filing. The data team's job is to make that dataset complete and correct. SEC EDGAR is the only source of stored values; yfinance, SEC Frames and anything else exist only to detect disagreements (`doc/data-moat/README.md`).

## 2. The pipeline, end to end
```
SEC EDGAR (companyfacts, submissions, filings)
  -> Collector   pipeline/src/scrooner_pipeline/collector/      raw.*     lossless, immutable
  -> Normalizer  .../normalizer/                                core.*    company, filing, period, concept, unit, fact
  -> Mapper      .../mapper/                                    analytics.*  canonical concepts, canonical_fact, metrics
  -> Screener / AI query / Backend API / Next.js app (consumers; do not touch)
```
- Collector never transforms. Normalizer never maps concepts. Mapper never fetches. Do not move logic across these boundaries ("Component boundaries", `pipeline/CLAUDE.md`).
- Hard rules in code: `core.fact.is_authoritative = false` is always filtered out (a null is valid; never fall back to a non-authoritative row). Money is `Decimal` end to end. Batch jobs batch their writes.
- **"Non-authoritative" usually means "conflicted", not "bad" (added 2026-10-17 after a false alarm in a Period Engineer run).** Normalizer Stage 2e (`normalizer/dedupe.py`) marks ALL copies of a period non-authoritative when 2+ filings disagree. `mapper/conflict_resolution.py` (migration 0059) then fills `analytics.canonical_fact` for that period only if the worst-case disagreement is <=15%, tie-broken by highest fact_id. So a `canonical_fact` row whose `source_fact_ids` point at `is_authoritative=false` facts is expected for conflict-filled cells; it is not a hard-rule violation. Derivation (`normalizer/derived.py`) takes authoritative inputs only, so it cannot see conflict-filled FY values or conflict-marked 9M values: that is why most `q4_not_derived` cells are input-conflict problems, not arithmetic problems. Whether derivation may use conflict-filled values is an OPEN founder/accounting decision (doc 56 W1 default: resolve upstream first). Raise suspected rule violations to the owner as a question with the fact ids; do not report them as findings.
- History gate: never treat data before 2015-01-01 as current for display (`doc/foundational/38_Scrooner_History_Depth_Gate.md`). Check it before widening any fetch.

## 3. The database (one shared Supabase Postgres, ~46 GB)
| Schema | Holds | Key tables (verified present) |
|---|---|---|
| `raw` | SEC payload metadata (80 MB) | `sec_companyfacts`, `sec_submissions`, `sec_filing_documents`, `collector_runs/errors`, 13F and N-PORT bulk fetch logs |
| `core` (34 GB) | Normalized identity and facts | `company` (cik, sic_code, sector, status, primary_ticker), `filing` (form, filing_date, period_of_report), `period` (start_date, end_date, fiscal_year, fiscal_period), `fact` (company_id, concept_id, period_id, filing_id, value, is_authoritative, is_derived, supersedes_fact_id) |
| `analytics` (12 GB) | Canonical layer, metrics, and every data-quality table | see below |
| `app` | Users, saved screens, entitlements | not data-team territory |

Key `analytics` tables by job:
- **Catalog and mapping:** `canonical_concept` (78 rows; `combination_mode` first_match or sum), `concept_mapping` (tag -> concept, priority, confidence), `canonical_fact` (resolved value per company, concept, period; `source_fact_ids`), `metric_definition`, `metric_definition_input`, `metric_value` (`is_null_reason` explains every null).
- **Tag evidence:** `sec_tag_library` (all ~12.4K tags, `mapping_status`, `active_company_count`), `company_sec_tag`, `company_concept_lineage` (the tag behind each value, or what the company files instead), `concept_tag_candidate`, `concept_gap_lead`.
- **Decision record (Data Truth Layer):** `tag_concept_verdict` (approved / needs_review / rejected / different_concept / partial_component), `company_data_finding` (pipeline_bug / filer_error / legitimate_absence / data_limit, open / fixed / wont_fix), `company_tag_preference`.
- **Coverage and measurement:** `data_point_registry`, `company_data_point_coverage`, `company_population` (named denominators), `coverage_snapshot`, `coverage_group_snapshot`, `company_filing_line_evidence`.
- **Period completeness:** `period_gap` (one row per missing cell with `gap_cause`), `period_completeness`.
- **Checkers' output:** `data_sanity_check`, `data_sanity_investigation`, `yfinance_statement_line`, `statement_comparison_finding`, `frames_consistency_check`, `timeseries_outlier_check`, `metric_plausibility_check`, `identity_check_*`, `data_freshness_check`; view `data_incident` unifies them.

Database rules that bite:
- The pooler allows about 15 connections **shared by every service and every Claude session**. Check `select count(*) from pg_stat_activity` before opening more. `ListAgents` before any heavy job.
- Default `statement_timeout` is about 2 minutes. Any full-population scan or delete must `set statement_timeout` itself and be chunked. A reconnect resets it.
- Schema changes only through a committed migration in `pipeline/db/migrations/` (contiguous numbers, each file ends with `;`, checked by `scripts/check_migrations.py`). Claim the next number in `doc/planning/53_Multi_Session_Collaboration_Plan_2026-10-13.md` before writing the file. Next free number at last read: 0096.
- The database can enter a project-wide read-only state independent of your session; check `show default_transaction_read_only` before blaming code.

## 4. Commands (CLIs, run from `pipeline/` with `uv run`)
| Command | Purpose |
|---|---|
| `scrooner-map` | Mapper: `build-tag-library`, `gap-report`, `gap-tags <concept>`, `record-verdict`, `record-finding`, `build-coverage-matrix`, `snapshot-coverage`, `probe-filing-lines`, `resolve-concept-fallbacks`, `corrected-coverage-report` |
| `scrooner-sanity` | `run`, `report`, `investigate`, `timeseries`; `python -m scrooner_pipeline.sanity.period_completeness` |
| `scrooner-frames-check` | `run --year --quarter`, `report` |
| `scrooner-incidents` | `dashboard`, `impact <concept>`, `verify <company_id>` |
| `scrooner-yfinance-financials` | `fetch-statements`, `compare`, `investigate`, `report` |
| `scrooner-bootstrap`, `-incremental`, `-normalize`, `-reconcile` | Collection, normalization, reconciliation |
| `scrooner-screen`, `-ask`, `-ownership`, `-segments`, `-company-master` | Consumers and adjacent modules |
Tests: `cd pipeline && uv run pytest tests/unit -q`. Quality gate: `scripts/quality.sh`. CI: `.github/workflows/ci.yml`.

## 5. Scheduled jobs (`.github/workflows/`)
| Workflow | When (cron, UTC) | What |
|---|---|---|
| `pipeline-refresh.yml` | daily 12:23 | In order: index latest SEC filing day (`scrooner-incremental`); reprocess Normalizer + Mapper for recent filers; multi-listing and primary-ticker update; Alpaca prices; freshness health check; `probe-filing-lines`; `build-coverage-matrix`; `build-tag-candidates`; `snapshot-coverage`; then valuations and screener snapshot. Job cap 180 min; per-stage cap 1800 s in `scripts/lib/sharded.sh`. If the snapshot step never runs, an earlier step failed or timed out |
| `pipeline-sanity.yml` | daily 15:17 | yfinance cross-check, time-series, plausibility, period completeness (240 min cap) |
| `pipeline-frames-check.yml` | Mondays 17:05 | SEC Frames self-consistency |
| `live-sec-verification.yml` | Mondays 11:17 | Live SEC checks |
| `pipeline-recompute.yml`, `pipeline-tag-library.yml` | manual | Full-population recompute, tag library rebuild |
| `workflow-health-check.yml` | Mondays 06:30 | Watches the others |
Gotchas: a job that "fails" in 2 seconds with zero steps never started (read annotations, not logs). Logs of a cancelled run are deleted, so keep per-stage timing lines. Cancelling a run is blocked by the permission classifier; surface it to the founder.

## 6. Review and work-queue tooling
- **Cockpit** (`apps/admin`, Django, staff-only, **currently untracked in git**): `operations` app has `Investigation`, `WorkItem`, `WorkAttempt`, `WorkEvidence`, `CommandRequest`, `AuditEvent`; `work_queue.py`, `worker_api.py`, `ticket_analytics.py`, `workflows.py`. It reads warehouse data through a read-only `WAREHOUSE_DATABASE_URL` alias. Never point it at the Supabase service role. This is the natural home for the pack's task / decision / review records (07). Inspect it before building anything new.
- **Read-only agent already defined:** `.github/agents/sec-xbrl-tag-expert.agent.md` with spec `doc/tag-agent/sec_xbrl_tag_expert_for_us_stock_screener.md`. It recommends mappings and never writes. The Tag Mapper role should reuse its JSON output contract.
- **Decision record:** use `tag_concept_verdict` and `company_data_finding` (via `record-verdict`, `record-finding`) before creating any new table (07 says extend, do not duplicate).

## 7. Rules of the road (from root `CLAUDE.md`, not in the generic role files)
1. Several Claude sessions share one working tree and one database. Read `doc/planning/53_...` for lanes and file ownership. Never `git add -A`; add named files; commit and push in the same turn; do not commit or revert files you do not own.
2. Shared modules `mapper/coverage_matrix.py`, `coverage_snapshot.py`, `company_coverage_dashboard.py` belong to lane B this week. Tell the owner before editing.
3. A new concept mapping needs a **full-population coexistence check** (a 5-row sample is not evidence). Combined lines ("payable and accrued") are never mapped as the plain line. A bare tag can be a segment figure for one company and the total for another.
4. Before reporting coverage, check `max(snapshot_date)` in `coverage_snapshot` and that `company_data_point_coverage.gap_reason` is populated. On 2026-10-17 the snapshot was stale (2026-10-13) and `gap_reason` was empty.
5. "Nothing relevant filed" in the lineage means none of OUR mapped or candidate tags were filed. It is not evidence the filing lacks the line.
6. SEC access: declared User-Agent (`SEC_USER_AGENT`), about 10 requests per second aggregate, through `common/sec_client.py`. One SEC fetch process at a time. Never print secrets or connection strings.
7. Frontend, billing and screener code are out of scope. This team changes data, not product UI.

## 8. Measured state, 2026-10-17 (remeasure before use)
- Universe: 5,209 companies in the matrix; `real_operating_company` = 4,815 (includes 13 FPI-only filers and 83 with no 10-K).
- Concept coverage 86.32% average, metric 74.61% (snapshot 2026-10-13; stale).
- Only 61 empty concept cells have a mapped tag filed but no value: the pipeline does not drop mapped data. The gap is vocabulary (about 90 of 12,372 tags approved or provisional; 64% of facts sit under unmapped tags) and template (1,339 companies with revenue have no cost of revenue or gross profit).
- `period_gap`: about 254k missing cells; about 57.6k are Q4 or quarter not derived. A raw-fact sample of 1,200 Q4 gaps (2026-10-17): only about 3% have clean authoritative inputs; about 67% have conflicting duplicate values for the same period; about 30% have no 9-month YTD fact. An earlier 60% estimate was wrong (it counted display values picked from conflicts).
- Truth layer: 102 tag verdicts recorded, about 51k open findings.
- SEC Financial Statement Data Sets 2023q1 to 2026q3 are published (60-128 MB each); only 2025q4 has been downloaded (scratchpad, measurement only). 9.2% of face lines use custom tags.
- The plan these numbers feed: `doc/planning/56_Data_Moat_and_Full_Coverage_Plan_2026-10-17.md`.

## 9. Your ground, by role
Every role: read this map, `doc/data-moat/README.md`, `SYSTEMS.md`, `decisions.md`, then your role file. State role, objective, scope, authorized actions and limits before starting (01).

### Data Chief (10)
- **Owns:** batch selection, daily founder report, the release-policy proposal.
- **Reads:** doc 56, `PROGRESS.md`, `SCORECARD.md`, `DATA_COVERAGE.md`, `coverage_snapshot`, doc 53 (lanes).
- **First task:** reproduce a fresh baseline with query text and watermark; choose one root cause (suggested: Q4 derivation, doc 56 W1); draft the release policy using the pack's worksheet (04) and the four founder decisions at the end of doc 56.
- **Hands to:** Triage, Period Engineer, Data Engineer. Does not approve accounting.

### Standardization Lead (11)
- **Owns:** concept definitions, equivalence classes (exact / combined / component / calculated / not_equivalent), combined-line policy.
- **Reads/writes:** `canonical_concept`, `concept_mapping` (proposals only), `tag_concept_verdict` (via `record-verdict`), `pipeline/src/.../mapper/concepts.py`, `expanded_concepts.py`.
- **First task:** write the combined-line policy and the definition set for the 24 most common face lines with no concept today (retained earnings, common and preferred stock value, shares issued and authorized, par value, APIC, weighted-average shares basic and diluted, operating lease asset and liabilities, interest paid, income taxes paid, other non-current assets and liabilities, cash-flow prepaid change). Keep share counts, weighted averages and cash vs expense distinct.
- **Hands to:** Verifier. Cannot approve its own rule.

### Sector Analyst (12)
- **Owns:** template applicability and sector metrics. Evidence: 1,339 companies with revenue but no cost of revenue or gross profit (Financials 560, Healthcare 247, Real Estate 159).
- **Reads:** `core.company.sic_code`, `sector`, `company_filing_line_evidence`, `company_population`, `doc/execution-plans/33_...`, `doc/scoping/32b_...` (FDIC source for banks).
- **First task:** bank template pilot: select a cohort from `core.company` by SIC, inspect original statements, list the lines they file (G&A, labor, loan-loss provision, deposits, loans), produce the template and the metric matrix. Keep insurers and mortgage REITs separate.
- **Hands to:** Standardization Lead (definitions), Verifier.

### Tag Mapper (13)
- **Owns:** high-reach unmapped tag investigations.
- **Reads/runs:** `sec_tag_library` (order by `active_company_count`), `scrooner-map gap-tags <concept>`, `company_concept_lineage`, `concept_tag_candidate`; reuse the JSON contract in the tag-expert agent spec.
- **First task:** the same 24 lines as the Standardization Lead, drawing the evidence: distinct issuers, same-context coexistence against the target, counterexamples, dimensions. Output one decision per rule family; no `concept_mapping` edits.
- **Hands to:** Standardization Lead, then Verifier.

### Period Engineer (14)
- **Owns:** quarter derivation (Q2, Q3, Q4 from YTD and annual), TTM inputs.
- **Reads/writes:** `core.period` (note YTD periods can have null `fiscal_period`), `canonical_fact`, `period_gap`, `normalizer/derived.py`, `sanity/period_completeness.py`, `core.fact.is_derived`, `source_fact_ids`.
- **First task:** full-population census of `period_gap` where `gap_cause` is `q4_not_derived` or `quarter_not_derived`: classify by raw-fact input state (clean / conflicting / no YTD source / chain available). Company 8 FY2023 is the warning case: its 9M and Q1 values have 2-3 conflicting copies differing 5-10x and only FY is authoritative, so Q4 is NOT safely derivable. Resolve basis conflicts first, then derive; restrict to the additive allowlist; produce a dry-run table. Scrooner-2b currently owns Q4/YTD ticket analysis in doc 53: contact that session first.
- **Hands to:** Verifier. No EPS or share subtraction.

### Data Engineer (15)
- **Owns:** nightly reliability, ingestion, size, replay.
- **Reads/runs:** the workflows in section 5, `scripts/lib/sharded.sh`, `scripts/reprocess_recent_filers.sh`, `pipeline/db/migrations/`, `scripts/check_migrations.py`.
- **First tasks:** (1) find why the coverage snapshot stopped on 2026-10-13 and why `gap_reason` is empty in `company_data_point_coverage`; (2) run the Financial Statement Data Sets size pilot: load one quarter (2025q4 already downloaded in the scratchpad), measure rows, bytes and index growth, and report before any wider load (doc 56 W2); (3) check `yfinance_statement_line`: 4,967 rows in 899 MB looks like bloat. Heavy jobs: `ListAgents` first.
- **Hands to:** Verifier, Triage.

### Data Verifier (16)
- **Owns:** independent challenge. Form your own interpretation from the original filing (SEC filing HTML or `R*.htm`, not our tables) before reading the proposer's rationale.
- **Reads/runs:** `scrooner-incidents verify <company_id>`, `scrooner-frames-check`, golden-company set (`doc/execution-plans/08_...`, 10 companies), `edgartools` (doc 12) as an independent parser.
- **First task:** build the fixed regression set (golden-10 plus a few banks and REITs) with source locators; review the Period Engineer's dry-run Q4 candidates against filings. Report that a shared parser may hide shared errors.
- **Hands to:** Chief with per-decision verdicts.

### Data Triage (17)
- **Owns:** queue hygiene and the coverage ledger.
- **Reads/runs:** `company_data_finding`, `data_gap_by_concept/_by_metric/_by_company` views, `period_gap`, `coverage_snapshot`, `scrooner-map gap-report`, `scrooner-incidents dashboard`.
- **First task:** reconcile the three counts (findings, unique issues, affected cells), group the ~51k open findings by root cause (many sit under a few mappings), and publish the denominator ledger. Note `no_line_item_filed` over-claims about 1 gap in 5, and `data_limit` tickets are often mislabeled (verify against raw tags).
- **Hands to:** every specialist.

## 10. Hand-off lanes and who to ask
| Question | Ask / read |
|---|---|
| Coverage dashboard, launch readiness | Lane A (scrooner-98), `mapper/coverage_groups.py` |
| Applicability, filing-line evidence, nightly/CI | Lane B (scrooner-f9), `parsers/filing_line_evidence.py` |
| Sanity checks, ticket fixes, denominators | Lane C (scrooner-64) |
| Q4 / YTD tickets, cash-flow tag mapping | Lane F (scrooner-2b) |
| Anything touching `apps/app` | Not this team |
Status of lanes changes; re-read doc 53 and `ListAgents` before relying on this table.

## 11. What these role files are not
They are Claude Code role instructions, not installed skills or running services. Nothing here registered `/scrooner-*` commands; doing so means copying each file to `.claude/skills/<name>/SKILL.md` (00-START-HERE explains how). That edits the repository's tooling and was not done. They do not replace an accountant: new accounting definitions stay proposals until the founder's adopted release policy says otherwise.
