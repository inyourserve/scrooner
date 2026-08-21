# Scrooner `doc/` — Index

34+ documents have accumulated here since 2026-08-14. This index exists so "which doc do I actually need" doesn't require reading the root `CLAUDE.md`'s full narrative every time.

**Reorganized 2026-08-18**: docs now physically live in the topic subfolders below (`foundational/`, `requirements/`, `execution-plans/`, `scoping/`, `planning/`, `reference/`, `status/`), matching the groupings this index already used. This reverses the 2026-08-14 "files are not being renamed or moved" note — that decision held while the doc set was small; at 39 files it's superseded. Filenames and numbering are unchanged (a doc's number is still its write-order identity, independent of which folder holds it), so `doc 19` still means the same document, just at `doc/execution-plans/19_...md` instead of `doc/19_...md`. Every cross-reference across the repo (root `CLAUDE.md`, `pipeline/CLAUDE.md`, code comments, `.claude/skills/`, and every doc-to-doc link) was updated in the same pass — verified with a repo-wide link check, not asserted.

**For "what's actually done," always check [`PROGRESS.md`](status/PROGRESS.md) first** — not this index, not memory.
**For "what data points/features exist vs. don't," check [`DATA_COVERAGE.md`](status/DATA_COVERAGE.md)** — the living tracker requested 2026-08-18.

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
| Ownership & Insider Activity | [`19`](execution-plans/19_Scrooner_Ownership_and_Insider_Activity_Plan.md) | (evidence inline + `learnings/ownership-and-8k-discovery.md`, `learnings/form-13f-cusip-crosswalk.md`) |
| Alpaca Market Price + price metrics | [`25`](execution-plans/25_Scrooner_Alpaca_Market_Price_Integration_Plan.md) | (evidence inline, §7-11) |

## Scoping / evaluation docs (proposals — check status line for what's actually built)

- [`21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md`](scoping/21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md) — Form N-PORT, corporate actions
- [`22_Scrooner_EDGAR_Full_Surface_Evaluation.md`](scoping/22_Scrooner_EDGAR_Full_Surface_Evaluation.md) — full EDGAR API/report surface vs. requirements
- [`23_Scrooner_EDGAR_Signal_Enhancements_Execution_Plan.md`](scoping/23_Scrooner_EDGAR_Signal_Enhancements_Execution_Plan.md) — scopes doc 22's ranked items (mostly now built, see doc 24 Phase 1)
- [`27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md`](scoping/27_Scrooner_Decision_Dataset_Study_Gap_Analysis.md) — cross-references `perplexity-decision-dataset-study.md` against build state; UX ideas for doc 24 Phase 3
- [`28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md`](scoping/28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md) — cross-references a live Trendlyne stock page against build state; ranks new candidates (R&D Expense, Interest Income, ownership-by-category, ownership trend, Beta, Congressional trading disclosures)

## Planning / backlog (sequencing across everything above)

- [`20_Scrooner_Remaining_Work_End_to_End_Plan.md`](planning/20_Scrooner_Remaining_Work_End_to_End_Plan.md) — superseded by doc 24 for sequencing; §3's open-decisions table still accurate
- [`24_Scrooner_Final_Build_Backlog.md`](planning/24_Scrooner_Final_Build_Backlog.md) — **current**, supersedes doc 20

## Reference (non-canonical, kept for detail doc 01-26 don't repeat)

- [`DOCUMENTATION.md`](reference/DOCUMENTATION.md) — URL structure, repo layout, implementation detail. Where it conflicts with 01-26 on a *decision*, 01-26 wins (see root `CLAUDE.md`'s "known conflicts" note).
- [`claude-code-guide.md`](reference/claude-code-guide.md) — how to build a skill/subagent/slash-command, for whoever needs one next

## Subdirectories

- [`learnings/`](learnings/) — 31 entries covering product, design, architecture, and engineering: what broke or was clarified, how it was actually found, and the generalizable lesson. Not a decision doc — read to avoid rediscovering a solved problem.
- [`adr/`](adr/) — Architecture Decision Records for consequential, hard-to-reverse technical calls. Currently just the template; none written yet (no call has needed one).
- [`html/`](html/) — reference source material (e.g. `screener.html`, the real Screener.in page doc 17's analysis was grounded in; `trendlyne-apple.html`, doc 28's grounding), not documentation itself.
- [`consultant/`](consultant/) — independent recommendations and opportunity assessments; these advise but do not override canonical decisions or status.
- [`design/`](design/) — product proposition, UX architecture, design system, accessibility, state, and UI implementation guidance.

## Folder layout (2026-08-18)

```
doc/
├── README.md                 this index — stays at the root
├── foundational/             01,02,03,04,05,06,07,12 — rarely change
├── requirements/              10,18,26 + screener-criteria-study.md
├── execution-plans/           08,08b,09,09b,11,11b,13,13b,14,14b,15,15b,16,16b,17,19,25
├── scoping/                    21,22,23 — proposals, not builds
├── planning/                   20,24 — sequencing/backlog
├── reference/                  DOCUMENTATION.md, claude-code-guide.md
├── status/                     PROGRESS.md, DATA_COVERAGE.md, SCORECARD.md — living trackers
├── learnings/                  unchanged — day-by-day journal
├── adr/                        unchanged — Architecture Decision Records
├── html/                       unchanged — reference source material
├── consultant/                 advisory product and data-strategy recommendations
└── design/                     product design framework and UI guidance
```

---

## Numbering convention (for the next doc)

Docs are numbered in the order they were written, not by topic — there's no gap-filling. The next new doc is `27_Scrooner_<Name>.md`, placed directly in whichever topic folder above fits it (an execution plan goes in `execution-plans/`, a scoping proposal in `scoping/`, etc.) — the number is a write-order identity, the folder is just where it physically lives. A `b`-suffixed doc (`NNb_`) is always a Definition-of-Done evidence report paired with plan `NN`, filed alongside it in the same folder. Living/reference docs (`PROGRESS.md`, `SCORECARD.md`, `DATA_COVERAGE.md`, `DOCUMENTATION.md`, `claude-code-guide.md`) stay unnumbered and live in `status/` or `reference/` per the table above.
