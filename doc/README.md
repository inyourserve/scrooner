# Scrooner `doc/` — Index

155 files have accumulated here since 2026-08-14 (recount: 2026-09-06 doc audit — the folder/subfolder counts below were stale before this pass). This index exists so "which doc do I actually need" doesn't require reading the root `CLAUDE.md`'s full narrative every time.

**Reorganized 2026-08-18**: docs now physically live in the topic subfolders below (`foundational/`, `requirements/`, `execution-plans/`, `scoping/`, `planning/`, `reference/`, `status/`), matching the groupings this index already used. This reverses the 2026-08-14 "files are not being renamed or moved" note — that decision held while the doc set was small; at 39 files it's superseded. Filenames and numbering are unchanged (a doc's number is still its write-order identity, independent of which folder holds it), so `doc 19` still means the same document, just at `doc/execution-plans/19_...md` instead of `doc/19_...md`. Every cross-reference across the repo (root `CLAUDE.md`, `pipeline/CLAUDE.md`, code comments, `.claude/skills/`, and every doc-to-doc link) was updated in the same pass — verified with a repo-wide link check, not asserted.

**For "what's actually done," always check [`PROGRESS.md`](status/PROGRESS.md) first** — not this index, not memory.
**For "what data points/features exist vs. don't," check [`DATA_COVERAGE.md`](status/DATA_COVERAGE.md)** — the living tracker requested 2026-08-18.
**For anything about data correctness/verification specifically — the actual moat (doc 01) — start at [`data-moat/README.md`](data-moat/README.md)**, a dedicated entry point added 2026-09-08 so that work doesn't require reading the whole product-wide doc tree first.

---

## Start here

| Doc | Purpose |
|---|---|
| [`01_What_Is_Scrooner_and_Why.md`](foundational/01_What_Is_Scrooner_and_Why.md) | Product thesis, target user, moat |
| [`02_Scrooner_Decision_Register.md`](foundational/02_Scrooner_Decision_Register.md) | **Check before assuming any decision** — locked, rejected, and open items |
| [`03_Scrooner_MVP_Scope.md`](foundational/03_Scrooner_MVP_Scope.md) | In/out of scope, release gates |
| [`PROGRESS.md`](status/PROGRESS.md) | Live status across all 14 project parts — **the "what's done" source of truth** |
| [`DATA_COVERAGE.md`](status/DATA_COVERAGE.md) | Live status across every individual data point/feature — **the "which metric exists" source of truth** |
| [`SCORECARD.md`](status/SCORECARD.md) | Quantitative build-quality score |
| [`24_Scrooner_Final_Build_Backlog.md`](planning/24_Scrooner_Final_Build_Backlog.md) | **The plan being executed right now** — ordered phases, supersedes doc 20 |
| [`consultant/`](consultant/) | Independent product and data-strategy recommendations; advisory, not canonical |
| [`design/`](design/) | Product design framework, UX system, and UI implementation guidance |

## Foundational / methodology (rarely change)

- [`04_Scrooner_System_Design_and_Tech_Stack.md`](foundational/04_Scrooner_System_Design_and_Tech_Stack.md) — architecture, schemas, tech stack
- [`05_Scrooner_Product_and_Engineering_Methodology.md`](foundational/05_Scrooner_Product_and_Engineering_Methodology.md) — KISS BORING, build method
- [`06_Scrooner_Project_Breakdown_and_Execution_Plan.md`](foundational/06_Scrooner_Project_Breakdown_and_Execution_Plan.md) — the 14 parts, module breakdown
- [`07_SEC_EDGAR_Rules_and_Data_Guide.md`](foundational/07_SEC_EDGAR_Rules_and_Data_Guide.md) — every EDGAR API/bulk URL, access rules, form types
- [`12_Scrooner_Edgar_Python_Plugin_Usage.md`](foundational/12_Scrooner_Edgar_Python_Plugin_Usage.md) — `edgartools` verification-layer usage
- [`38_Scrooner_History_Depth_Gate.md`](foundational/38_Scrooner_History_Depth_Gate.md) — **mandatory gate, check before writing any new fetch or widening an existing one's date range.** A 5-case decision tree keyed on the source's real refiling cadence (mandatory-every-period / per-transaction / only-if-changed / already-self-comparing), not one blanket rule; hard ceiling of 2015-01-01 either way. Written after `beneficial_ownership.py` was found with no history bound at all, needing a 90% (193,751-row) DB cleanup once fixed

## Requirements / domain reference

- [`10_scrooner_required_data_points.md`](requirements/10_scrooner_required_data_points.md) — **the master P0/P1/P2 data-point inventory** (~120 items, screener.in-equivalent for US investors). `DATA_COVERAGE.md` tracks status against this doc's exact rows.
- [`18_Scrooner_Expanded_Metric_Scope_for_Premium.md`](requirements/18_Scrooner_Expanded_Metric_Scope_for_Premium.md) — Tier A/B/C candidate metrics beyond the locked 18
- [`screener-criteria-study.md`](requirements/screener-criteria-study.md) — what makes a *screener* (not just a company page) good; user-provided
- [`26_Scrooner_Screener_Data_Points_Gap_Analysis.md`](requirements/26_Scrooner_Screener_Data_Points_Gap_Analysis.md) — the above study cross-referenced against what's built
- [`perplexity-decision-dataset-study.md`](requirements/perplexity-decision-dataset-study.md) — "build for decisions, not data dumps": a compact decision-oriented metric set + UX proposal; user-provided
- [`27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md`](scoping/27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md) — the above study cross-referenced against what's built (~85% already covered; 2 new UX ideas for Phase 3, 1 open product question)
- [`../html/trendlyne-apple.html`](html/trendlyne-apple.html) — a live Trendlyne stock page, user-provided reference for competitive data-point comparison
- [`28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md`](scoping/28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md) — the above cross-referenced against what's built; 2 cheap zero-new-fetch concepts (R&D Expense, Interest Income), 2 real-but-harder items (ownership-by-category breakdown, historical ownership trend), 2 items needing an explicit scope call (Beta, Congressional trading disclosures)

## Execution plans + their evidence reports (built, in order)

Each pair: the plan, then the Definition-of-Done evidence proving it was actually verified, not just written.

| Part | Plan | Evidence |
|---|---|---|
| Collector | [`08`](execution-plans/08_Scrooner_Collector_Execution_Plan.md) | [`08b`](execution-plans/08b_Collector_Definition_of_Done_Evidence.md) |
| Normalizer | [`09`](execution-plans/09_Scrooner_Normalizer_Execution_Plan.md) | [`09b`](execution-plans/09b_Normalizer_Definition_of_Done_Evidence.md) |
| Mapper & Metrics | [`11`](execution-plans/11_Scrooner_Mapper_Metrics_Execution_Plan.md) | [`11b`](execution-plans/11b_Mapper_Definition_of_Done_Evidence.md) |
| Company Master 4a | [`13`](execution-plans/13_Scrooner_Company_Master_Execution_Plan.md) | [`13b`](execution-plans/13b_Company_Master_4a_Definition_of_Done_Evidence.md) |
| Screener Engine | [`14`](execution-plans/14_Scrooner_Screener_Engine_Execution_Plan.md) | [`14b`](execution-plans/14b_Screener_Engine_Definition_of_Done_Evidence.md) |
| AI Query Engine | [`15`](execution-plans/15_Scrooner_AI_Query_Engine_Execution_Plan.md) | [`15b`](execution-plans/15b_AI_Query_Engine_Definition_of_Done_Evidence.md) |
| Backend API | [`16`](execution-plans/16_Scrooner_Backend_API_Execution_Plan.md) | [`16b`](execution-plans/16b_Backend_API_Definition_of_Done_Evidence.md) |
| Company Page | [`17`](execution-plans/17_Scrooner_Company_Page_Reference_and_MVP_Plan.md) | (evidence inline in doc 17 + `learnings/company-page-mvp.md`) |
| Ownership & Insider Activity | [`19`](execution-plans/19_Scrooner_Ownership_and_Insider_Activity_Plan.md) | (evidence inline + `learnings/ownership-and-8k-discovery.md`, `learnings/form-13f-cusip-crosswalk.md`; full-population insider scale-out + institutional/mutual-fund 2-window builds evidenced in `learnings/2026-08-29-ownership-scale-out-and-zero-fetch-metrics.md`) |
| Alpaca Market Price + price metrics | [`25`](execution-plans/25_Scrooner_Alpaca_Market_Price_Integration_Plan.md) | (evidence inline, §7-11) |

## Scoping / evaluation docs (proposals — check status line for what's actually built)

- [`21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md`](scoping/21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md) — Form N-PORT, corporate actions
- [`22_Scrooner_EDGAR_Full_Surface_Evaluation.md`](scoping/22_Scrooner_EDGAR_Full_Surface_Evaluation.md) — full EDGAR API/report surface vs. requirements
- [`23_Scrooner_EDGAR_Signal_Enhancements_Execution_Plan.md`](scoping/23_Scrooner_EDGAR_Signal_Enhancements_Execution_Plan.md) — scopes doc 22's ranked items (mostly now built, see doc 24 Phase 1)
- [`27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md`](scoping/27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md) — cross-references `perplexity-decision-dataset-study.md` against build state; UX ideas for doc 24 Phase 3
- [`28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md`](scoping/28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md) — cross-references a live Trendlyne stock page against build state; ranks new candidates (R&D Expense, Interest Income, ownership-by-category, ownership trend, Beta, Congressional trading disclosures)
- [`29_Scrooner_Personalized_Key_Metrics_Plan.md`](scoping/29_Scrooner_Personalized_Key_Metrics_Plan.md) — a concrete plan for letting a logged-in user customize the company page's Key Metrics bar; gated on Part 9 (User System) existing first
- [`insider_info.md`](scoping/insider_info.md) — user-supplied product spec, **Locked (2026-08-25)**, for the Ownership page section's full MVP scope (Insider/Institutional 13F/Mutual Fund N-PORT subsections + Overview + disclosure requirement); kept under its original filename rather than renumbered since other docs already cite it by name. Underlying data for all three subsections is built (2026-08-29); the unified frontend page section is not
- [`37_Scrooner_Segment_Revenue_Scoping.md`](scoping/37_Scrooner_Segment_Revenue_Scoping.md) — revenue-by-business-segment for the top 100 companies by revenue (Market Cap unusable for universe selection — still 0 population-wide; a real `dei:EntityPublicFloat` data-quality bug found live rules that out too). Grounded in a real inspection of Apple's actual 10-K filing structure: the R.htm auto-rendered disclosure tables (not raw XBRL dimensional parsing) are the practical path. Scope only, nothing built
- [`39_Scrooner_Employee_Headcount_Full_Coverage_Plan.md`](scoping/39_Scrooner_Employee_Headcount_Full_Coverage_Plan.md) — closing the gap from the XBRL-only `dei:EntityNumberOfEmployees` tag covering only ~3.5% of active companies (even Apple/Microsoft/Costco don't tag it). Grounded in real 10-K text pulled live for all three — confirms the data exists as prose in each company's "Human Capital" section, plus a real hazard found in the same pass (a naive parse matches garbage from hidden inline-XBRL metadata unless properly stripped first). Proposes a two-tier regex-now/LLM-later extractor (mirrors doc 15's AI Query Engine precedent) and a new `core.employee_headcount_disclosure` table, kept separate from `core.fact` rather than blended with authoritative XBRL data. Scope only, nothing built

## Planning / backlog (sequencing across everything above)

- [`20_Scrooner_Remaining_Work_End_to_End_Plan.md`](planning/20_Scrooner_Remaining_Work_End_to_End_Plan.md) — superseded by doc 24 for sequencing; §3's open-decisions table still accurate
- [`24_Scrooner_Final_Build_Backlog.md`](planning/24_Scrooner_Final_Build_Backlog.md) — **current**, supersedes doc 20
- [`41_Scrooner_Coverage_Improvement_Plan.md`](planning/41_Scrooner_Coverage_Improvement_Plan.md) — **living, started 2026-09-02**. The tactical score-and-tag-list doc: defines `avg_metric_coverage_score`/`avg_concept_coverage_score` (`analytics.coverage_snapshot`, `scrooner-map snapshot-coverage`), the day-by-day trend (79.41%→56.85% as of 2026-09-03, corrected for bugs found along the way), and a ranked, tag-by-tag candidate-verification table (what's shipped, what's correctly rejected with evidence).
- [`42_Scrooner_Multi_Parser_Coverage_Architecture_Plan.md`](planning/42_Scrooner_Multi_Parser_Coverage_Architecture_Plan.md) — **living, started 2026-09-03**. The strategic study doc: root-causes every "should be near-100%" mandatory GAAP concept by sampling its real missing companies (finding `current_assets`/`operating_income`'s real ~80-85% ceiling is structural — banks/insurers/REITs use an unclassified statement format, not a tag-mapping gap), designs a 4-parser architecture (XBRL tags, cover-page text, rendered-report tables, sector-specific concept profiles) instead of relying on one extraction method, and formalizes the measure→sample→root-cause→verify→ship loop this week's real work already validated three times.
- [`43_Single_Nextjs_Shared_Domain_and_Shadcn_Migration_Plan.md`](planning/43_Single_Nextjs_Shared_Domain_and_Shadcn_Migration_Plan.md) — **executed 2026-09-05**. Next.js is the only frontend framework on `scrooner.com`; authenticated workflows live under `/app`, legacy paths redirect, and shadcn New York supplies the base component language.
- [`45_Scrooner_yfinance_Expansion_Data_Sanity_Plan.md`](planning/45_Scrooner_yfinance_Expansion_Data_Sanity_Plan.md) — **draft (2026-09-08)**, not built. Every new yfinance API surface (splits, dividends, calendar/freshness, annual statements, shares-outstanding time series, insider transactions, institutional holders) checked live against a real AAPL payload before being ranked. P0: a stock-split discontinuity check (closes a named doc-21 gap), a per-payment dividend check, and a genuinely new sanity DIMENSION — data freshness/staleness, not just value correctness. Same "yfinance detects/matches, SEC data is the only fill source" rule as doc 44's Tag Investigator.

## Reference (non-canonical, kept for detail doc 01-26 don't repeat)

- [`36_Scrooner_SEC_Filing_Types_Reference.md`](reference/36_Scrooner_SEC_Filing_Types_Reference.md) — one section per SEC filing type (10-K through S-1): what it legally covers, exactly what Scrooner's real code extracts from it, why it matters. Found N-PORT built but still described as "not built" in docs 21/22/root CLAUDE.md.
- [`40_Scrooner_XBRL_Tag_Coverage_Library.md`](reference/40_Scrooner_XBRL_Tag_Coverage_Library.md) — a real, live-generated inventory of what XBRL tags companies actually use per canonical concept (`pipeline/scripts/build_tag_coverage_library.py` → `pipeline/reference/xbrl_tag_coverage_library.json`), built after a real `total_debt` double-counting risk was found and fixed via a new `concept_fallback.py` fallback-resolver pattern. Key finding: keyword-matched candidate tags are frequently semantically wrong (R&D candidate was a deferred-tax-asset tag, goodwill candidate explicitly excludes goodwill) — every candidate still needs live spot-check verification before use, most of the 44 concepts' candidates remain unverified.
- [`44_Scrooner_Systems_Index.md`](reference/44_Scrooner_Systems_Index.md) — one row per standing system built on top of the frozen Collector/Normalizer/Mapper (Multi-Parser Registry, Tag Coverage Library, Concept Fallback/`*_resolved` concepts, Coverage Matrix/Snapshot, Data Sanity Layer + Tag Investigator, yfinance backfill, etc.): purpose, code location, tables, CLI commands, current scale. Added because the count of these got too easy to lose track of — add a row here the same pass any new one ships.
- [`DOCUMENTATION.md`](reference/DOCUMENTATION.md) — URL structure, repo layout, implementation detail. Where it conflicts with 01-26 on a *decision*, 01-26 wins (see root `CLAUDE.md`'s "known conflicts" note).
- [`claude-code-guide.md`](reference/claude-code-guide.md) — how to build a skill/subagent/slash-command, for whoever needs one next

## Subdirectories

- [`audit/`](audit/) — dated, point-in-time inspections of an existing built feature (data-point/investor-value quality, frontend component-system quality), not a build plan or a status tracker. Filename is `YYYY-MM-DD_topic.md`, not numbered.
- [`learnings/`](learnings/) — 64+ entries (63 as of the 2026-09-06 recount, plus `2026-09-10-screener-performance.md`) covering product, design, architecture, and engineering: what broke or was clarified, how it was actually found, and the generalizable lesson. Not a decision doc — read to avoid rediscovering a solved problem.
- [`Frontend/`](Frontend/) — competitor/reference material (raw HTML captures of real competitor pages — StockAnalysis, Yahoo Finance, Nasdaq, Value Research, Trendlyne — plus a few specs, e.g. the financials-display spec). Distinct from `design/`: this folder is unauthored raw reference material and working specs, not Scrooner's own numbered design decisions/evidence. Not previously indexed here — added 2026-09-06.
- [`adr/`](adr/) — Architecture Decision Records for consequential, hard-to-reverse technical calls. First real one written 2026-09-10: [`0001-screener-redis-cache-and-boolean-logic.md`](adr/0001-screener-redis-cache-and-boolean-logic.md), reversing doc 02's "No Redis or Celery" lock (Redis/caching only) and the Screener's AND-only boundary, by explicit founder direction.
- [`html/`](html/) — reference source material (e.g. `screener.html`, the real Screener.in page doc 17's analysis was grounded in; `trendlyne-apple.html`, doc 28's grounding), not documentation itself.
- [`consultant/`](consultant/) — independent recommendations and opportunity assessments; these advise but do not override canonical decisions or status.
- [`design/`](design/) — product proposition, UX architecture, design system, accessibility, state, and UI implementation guidance.

## Folder layout (2026-08-18)

```
doc/
├── README.md                 this index — stays at the root
├── foundational/             01,02,03,04,05,06,07,12,38 — rarely change
├── requirements/              10,18,26 + screener-criteria-study.md
├── execution-plans/           08,08b,09,09b,11,11b,13,13b,14,14b,15,15b,16,16b,17,19,25
├── scoping/                    21,22,23,27,28,29,37 + insider_info.md — proposals, not builds
├── planning/                   20,24 — sequencing/backlog
├── reference/                  36, DOCUMENTATION.md, claude-code-guide.md
├── status/                     PROGRESS.md, DATA_COVERAGE.md, SCORECARD.md — living trackers
├── audit/                      dated point-in-time feature inspections (YYYY-MM-DD_topic.md)
├── learnings/                  unchanged — day-by-day journal
├── adr/                        unchanged — Architecture Decision Records
├── html/                       unchanged — reference source material
├── consultant/                 advisory product and data-strategy recommendations
└── design/                     product design framework and UI guidance
```

---

## Numbering convention (for the next doc)

Docs are numbered in the order they were written, not by topic — there's no gap-filling. The next new doc is `44_Scrooner_<Name>.md` (highest so far: doc 43) — check this file's own tables above for the current highest number before assuming one, since this line itself has gone stale before. Place it directly in whichever topic folder above fits it (an execution plan goes in `execution-plans/`, a scoping proposal in `scoping/`, etc.) — the number is a write-order identity, the folder is just where it physically lives. A `b`-suffixed doc (`NNb_`) is always a Definition-of-Done evidence report paired with plan `NN`, filed alongside it in the same folder. Living/reference docs (`PROGRESS.md`, `SCORECARD.md`, `DATA_COVERAGE.md`, `DOCUMENTATION.md`, `claude-code-guide.md`) stay unnumbered and live in `status/` or `reference/` per the table above.
