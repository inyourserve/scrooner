# Scrooner `doc/` — Index

34 documents have accumulated here since 2026-08-14. This index exists so "which doc do I actually need" doesn't require reading the root `CLAUDE.md`'s full narrative every time. Files are **not** being renamed or moved — every existing cross-reference (`doc/19_...md` etc.) stays valid. This is purely a navigation aid, grouped by purpose instead of by number.

**For "what's actually done," always check [`PROGRESS.md`](PROGRESS.md) first** — not this index, not memory.
**For "what data points/features exist vs. don't," check [`DATA_COVERAGE.md`](DATA_COVERAGE.md)** — the living tracker requested 2026-08-18.

---

## Start here

| Doc | Purpose |
|---|---|
| [`01_What_Is_Scrooner_and_Why.md`](01_What_Is_Scrooner_and_Why.md) | Product thesis, target user, moat |
| [`02_Scrooner_Decision_Register.md`](02_Scrooner_Decision_Register.md) | **Check before assuming any decision** — locked, rejected, and open items |
| [`03_Scrooner_MVP_Scope.md`](03_Scrooner_MVP_Scope.md) | In/out of scope, release gates |
| [`PROGRESS.md`](PROGRESS.md) | Live status across all 14 project parts — **the "what's done" source of truth** |
| [`DATA_COVERAGE.md`](DATA_COVERAGE.md) | Live status across every individual data point/feature — **the "which metric exists" source of truth** |
| [`SCORECARD.md`](SCORECARD.md) | Quantitative build-quality score |
| [`24_Scrooner_Final_Build_Backlog.md`](24_Scrooner_Final_Build_Backlog.md) | **The plan being executed right now** — ordered phases, supersedes doc 20 |

## Foundational / methodology (rarely change)

- [`04_Scrooner_System_Design_and_Tech_Stack.md`](04_Scrooner_System_Design_and_Tech_Stack.md) — architecture, schemas, tech stack
- [`05_Scrooner_Product_and_Engineering_Methodology.md`](05_Scrooner_Product_and_Engineering_Methodology.md) — KISS BORING, build method
- [`06_Scrooner_Project_Breakdown_and_Execution_Plan.md`](06_Scrooner_Project_Breakdown_and_Execution_Plan.md) — the 14 parts, module breakdown
- [`07_SEC_EDGAR_Rules_and_Data_Guide.md`](07_SEC_EDGAR_Rules_and_Data_Guide.md) — every EDGAR API/bulk URL, access rules, form types
- [`12_Scrooner_Edgar_Python_Plugin_Usage.md`](12_Scrooner_Edgar_Python_Plugin_Usage.md) — `edgartools` verification-layer usage

## Requirements / domain reference

- [`10_scrooner_required_data_points.md`](10_scrooner_required_data_points.md) — **the master P0/P1/P2 data-point inventory** (~120 items, screener.in-equivalent for US investors). `DATA_COVERAGE.md` tracks status against this doc's exact rows.
- [`18_Scrooner_Expanded_Metric_Scope_for_Premium.md`](18_Scrooner_Expanded_Metric_Scope_for_Premium.md) — Tier A/B/C candidate metrics beyond the locked 18
- [`screener-criteria-study.md`](screener-criteria-study.md) — what makes a *screener* (not just a company page) good; user-provided
- [`26_Scrooner_Screener_Data_Points_Gap_Analysis.md`](26_Scrooner_Screener_Data_Points_Gap_Analysis.md) — the above study cross-referenced against what's built

## Execution plans + their evidence reports (built, in order)

Each pair: the plan, then the Definition-of-Done evidence proving it was actually verified, not just written.

| Part | Plan | Evidence |
|---|---|---|
| Collector | [`08`](08_Scrooner_Collector_Execution_Plan.md) | [`08b`](08b_Collector_Definition_of_Done_Evidence.md) |
| Normalizer | [`09`](09_Scrooner_Normalizer_Execution_Plan.md) | [`09b`](09b_Normalizer_Definition_of_Done_Evidence.md) |
| Mapper & Metrics | [`11`](11_Scrooner_Mapper_Metrics_Execution_Plan.md) | [`11b`](11b_Mapper_Definition_of_Done_Evidence.md) |
| Company Master 4a | [`13`](13_Scrooner_Company_Master_Execution_Plan.md) | [`13b`](13b_Company_Master_4a_Definition_of_Done_Evidence.md) |
| Screener Engine | [`14`](14_Scrooner_Screener_Engine_Execution_Plan.md) | [`14b`](14b_Screener_Engine_Definition_of_Done_Evidence.md) |
| AI Query Engine | [`15`](15_Scrooner_AI_Query_Engine_Execution_Plan.md) | [`15b`](15b_AI_Query_Engine_Definition_of_Done_Evidence.md) |
| Backend API | [`16`](16_Scrooner_Backend_API_Execution_Plan.md) | [`16b`](16b_Backend_API_Definition_of_Done_Evidence.md) |
| Company Page | [`17`](17_Scrooner_Company_Page_Reference_and_MVP_Plan.md) | (evidence inline in doc 17 + `learnings/company-page-mvp.md`) |
| Ownership & Insider Activity | [`19`](19_Scrooner_Ownership_and_Insider_Activity_Plan.md) | (evidence inline + `learnings/ownership-and-8k-discovery.md`, `learnings/form-13f-cusip-crosswalk.md`) |
| Alpaca Market Price + price metrics | [`25`](25_Scrooner_Alpaca_Market_Price_Integration_Plan.md) | (evidence inline, §7-11) |

## Scoping / evaluation docs (proposals — check status line for what's actually built)

- [`21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md`](21_Scrooner_MF_Holdings_and_Corporate_Actions_Scope.md) — Form N-PORT, corporate actions
- [`22_Scrooner_EDGAR_Full_Surface_Evaluation.md`](22_Scrooner_EDGAR_Full_Surface_Evaluation.md) — full EDGAR API/report surface vs. requirements
- [`23_Scrooner_EDGAR_Signal_Enhancements_Execution_Plan.md`](23_Scrooner_EDGAR_Signal_Enhancements_Execution_Plan.md) — scopes doc 22's ranked items (mostly now built, see doc 24 Phase 1)

## Planning / backlog (sequencing across everything above)

- [`20_Scrooner_Remaining_Work_End_to_End_Plan.md`](20_Scrooner_Remaining_Work_End_to_End_Plan.md) — superseded by doc 24 for sequencing; §3's open-decisions table still accurate
- [`24_Scrooner_Final_Build_Backlog.md`](24_Scrooner_Final_Build_Backlog.md) — **current**, supersedes doc 20

## Reference (non-canonical, kept for detail doc 01-26 don't repeat)

- [`DOCUMENTATION.md`](DOCUMENTATION.md) — URL structure, repo layout, implementation detail. Where it conflicts with 01-26 on a *decision*, 01-26 wins (see root `CLAUDE.md`'s "known conflicts" note).
- [`claude-code-guide.md`](claude-code-guide.md) — how to build a skill/subagent/slash-command, for whoever needs one next

## Subdirectories

- [`learnings/`](learnings/) — 29 entries, day-by-day engineering journal: what broke, how it was actually found, the generalizable lesson. Not a decision doc — read to avoid rediscovering a solved problem.
- [`adr/`](adr/) — Architecture Decision Records for consequential, hard-to-reverse technical calls. Currently just the template; none written yet (no call has needed one).
- [`html/`](html/) — reference source material (e.g. `screener.html`, the real Screener.in page doc 17's analysis was grounded in), not documentation itself.

---

## Numbering convention (for the next doc)

Docs are numbered in the order they were written, not by topic — there's no gap-filling. The next new doc is `27_Scrooner_<Name>.md`. A `b`-suffixed doc (`NNb_`) is always a Definition-of-Done evidence report paired with plan `NN`. Unnumbered docs (`PROGRESS.md`, `SCORECARD.md`, `DATA_COVERAGE.md`, `DOCUMENTATION.md`) are living/reference docs, not point-in-time plans.
