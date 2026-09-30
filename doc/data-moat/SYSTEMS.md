# Data Moat — Systems

**Canonical from 2026-09-08 forward** for anything in the correctness/verification layer specifically — narrower than [doc 44](../reference/44_Scrooner_Systems_Index.md), which indexes every standing system built on top of the frozen pipeline (including pure coverage-building tools like the Text Extraction Framework or Segment Revenue Parser, which aren't verification systems). Everything below either **checks** whether our data is right/current, or **fixes** it by tracing back to a real SEC filing — never a third-party value.

**When you build a new one: add a row here in the same pass, not as a follow-up.** Same discipline as `doc/status/DATA_COVERAGE.md`'s own update rule.

| System | Checks | Fixes via | Code | Tables | CLI |
|---|---|---|---|---|---|
| **Concept Fallback** (doc 40, extended 09-07/08) | N/A — a safe-widening layer, not a checker | A `*_resolved` concept (zero `concept_mapping` rows, `resolve()` never touches it) merges a primary tag with a pair-coalesce, an arithmetic derivation, or a per-company tag preference | `mapper/concept_fallback.py` | writes into `analytics.canonical_fact` under the `*_resolved` concept's own id | `scrooner-map resolve-concept-fallbacks`, `resolve-statement-fallbacks` |
| **Data Sanity Layer** (09-08) | 22 `.info()`-based ratios + a revenue-zero special case, latest period only, against yfinance | Hands `major`/`critical` findings to the Tag Investigator | `sanity/yfinance_check.py` | `analytics.data_sanity_check` | `scrooner-sanity run`, `report` |
| **Tag Investigator** (09-08) | N/A — the fix engine, triggered by findings from any checker above | Traces every raw `core.fact` row under a company's already-mapped tags (including non-authoritative ones), scores against the external value, stores a **per-company tag preference** (not a value) when one reconciles | `sanity/tag_investigator.py` | `analytics.data_sanity_investigation`, `analytics.company_tag_preference` | `scrooner-sanity investigate` |
| **Data Freshness Check** (09-08) | Is our latest stored period actually current, independent of whether its VALUE is right — reuses the same `.info()` payload the ratio check already fetches, zero extra cost | N/A — a stale finding means "run the incremental pipeline," not a tag problem | `sanity/freshness_check.py` | `analytics.data_freshness_check` | wired into `scrooner-sanity run` |
| **yfinance Full Financial Statements** (09-08) | Every available quarter's individual income statement / balance sheet / cash flow line items, not just latest-period ratios | Hands `major` findings to the Tag Investigator | `yfinance_financials/` | `analytics.yfinance_statement_line`, `analytics.yfinance_line_item_mapping`, `analytics.statement_comparison_finding` | `scrooner-yfinance-financials fetch-statements / compare / investigate / report` |
| **SEC Frames Self-Consistency Checker** (09-08) | Our stored value vs. SEC's own bulk-served copy of the SAME filing — the strongest possible signal, since both sides are supposed to read the identical fact | N/A yet — a mismatch here is highest-confidence evidence of an extraction bug, worth tracing by hand before automating a fix path | `frames/` | `analytics.frames_consistency_check` | `scrooner-frames-check run --year --quarter`, `report` |
| **Time-Series Self-Consistency Checker** (09-08) | Zero external calls — a company's own value vs. its own value for the same `fiscal_period` one fiscal year earlier; catches an internally-wrong-but-plausible-looking value nothing else here can (yfinance only sees the latest period, Frames only proves "we copied the chosen tag correctly") | N/A yet — an outlier/sign_violation is a lead, same as Frames | `sanity/timeseries_check.py` | `analytics.timeseries_outlier_check` | `scrooner-sanity timeseries` |
| **Unified Data Incident Dashboard + Impact Analysis + Verifier** (09-08) | Normalizes all 5 tables above into one severity vocabulary; answers "which metrics/saved-screens does concept X's data feed" via the real `metric_definition_input`/`saved_screen.query` edges; re-runs the two rerun-safe checks for one company and diffs before/after | N/A — this layer reads/re-runs, it doesn't itself write a fix | `incidents/dashboard.py`, `incidents/impact.py`, `incidents/verifier.py` | `analytics.data_incident` (a VIEW, not a table — no sync lag) | `scrooner-incidents dashboard / impact <concept> / verify <company_id>` |
| **Coverage Matrix + Snapshot** (doc 41, 09-06) | Does company X have data point Y at all, and why not; the trend line (`avg_metric_coverage_score` etc.) | N/A — measurement, not correction | `mapper/coverage_matrix.py`, `mapper/coverage_snapshot.py` | `analytics.data_point_registry`, `analytics.company_data_point_coverage`, `analytics.coverage_snapshot` | `scrooner-map build-coverage-matrix`, `snapshot-coverage` |
| **Data Truth Layer** (09-29, migration 0080) | The DB records every conclusion: `tag_concept_verdict` (each tag x concept: approved / needs_review / rejected / different_concept / partial_component, with reason; concept_mapping mirrored automatically, investigation verdicts never overwritten), `company_data_finding` (pipeline_bug / filer_error / legitimate_absence / data_limit, open/fixed/wont_fix). Gaps ranked by concept (unexplained missing market cap), metric and company via views `data_gap_by_concept` / `_by_metric` / `_by_company`; `concept_gap_lead` holds lift-ranked tag leads that skip ruled-out tags | Plan fixes from `gap-report`; after each investigation, `record-verdict` / `record-finding`. Always fresh: daily reprocess refreshes touched companies, `pipeline-recompute` phase 5 rebuilds everything | `mapper/tag_library.py` | the four tables + three views above | `scrooner-map gap-report`, `gap-tags <concept>`, `record-verdict`, `record-finding`, `build-tag-library` |
| **SEC Tag Library** (09-27, migration 0077) | Every tag x every company (`company_sec_tag`, ~2M rows); tag -> companies/mapped concepts/metrics (`sec_tag_library`, all ~12.4K tags); company x concept -> the exact source tag behind our value, or what the company files instead when missing (`company_concept_lineage`); metric -> company -> tag via view `metric_company_tag_lineage` | N/A -- a lead list: `gap-tags <concept>` ranks every tag filed by companies MISSING a concept. Leads still need a coexistence check before `concept_mapping` | `mapper/tag_library.py` | `analytics.company_sec_tag`, `analytics.sec_tag_library`, `analytics.company_concept_lineage` | `scrooner-map build-tag-library` (manual workflow; rerun after any mapping/resolver change), `gap-tags <concept>` |
| **Component Total Debt** (09-27) | N/A -- a resolver | Replaces the sum-mode `total_debt` + split-pair fallback: `total_debt_resolved` built per balance-sheet date from ranked, non-overlapping components (all-in total, LTD incl. current + short-term, noncurrent + DebtCurrent, ...). vs yfinance ex-lease debt, 16,064 company-dates: within 5% 42.5% -> 50.0%, wrong 12.4% -> 7.5% | `mapper/concept_fallback.py` (`compute_total_debt`) | writes `analytics.canonical_fact` (`total_debt_resolved`) | `scrooner-map resolve-concept-fallbacks` |
| **Tag Candidate Library** (doc 40, retired-to-DB 09-08) | Candidate UNMAPPED XBRL tags per canonical concept, ranked by real company count — every candidate is a lead to investigate, never an approval (keyword matches are frequently a different concept, see doc 40) | N/A — a candidate found here becomes a real fix only after live coexistence-checking, same discipline as every concept_mapping addition this project has made | `mapper/tag_candidates.py` | `analytics.concept_tag_candidate` | `scrooner-map build-tag-candidates`, `tag-candidate-report` |

## How a finding becomes a fix (the actual loop)

```
A checker runs (Sanity / yfinance Financials / Frames)
        │
        ▼
Finding written (ok / minor / major / critical / mismatch / stale)
        │
        ▼
Tag Investigator traces the company's own core.fact rows under
already-mapped tags (never proposes a NEW global tag -- that needs
a human-reviewed concept_mapping change, same as doc 40's discipline)
        │
   ┌────┴─────┐
   │          │
reconciles   doesn't
   │          │
   ▼          ▼
company_tag_  recorded as
preference    needs_review /
stored        no_match_found
   │          (a real lead,
   ▼           not silently
Merged into    dropped)
a *_resolved
concept
```

## Verified numbers as of 2026-09-08 (real, not projected)

- Data Sanity Layer: full population run, 22 metrics, real bugs found and fixed (ebitda TTM, roa annualization, both now 100%/verified rolled out).
- yfinance Financials: golden-10 verified clean after fixing the `operating_expenses`/`CostsAndExpenses` global tag bug (682 companies).
- SEC Frames: **99.69% exact agreement** (28,099/28,187 company-concept pairs) between our extraction and SEC's own re-served data, across 7 of the highest-value concepts for CY2026Q1.
- Time-Series Self-Consistency: full population, 7 concepts, 4,196,782 (company, period) pairs checked — 16,722 outliers, 1,493 sign violations (revenue going negative — the strongest, least ambiguous signal this checker produces, not yet triaged past the aggregate count).
- Unified dashboard's first real run surfaced a genuinely new, un-triaged finding of its own: commodity ETF/trust structures (United States Oil Fund, Natural Gas Fund, etc.) dominate the "top offending companies" list purely because they have no revenue/opex/balance-sheet structure a fundamentals checker expects — the same "wrong entity type in the active population" shape as the BDC/bank carve-outs already documented elsewhere, not yet acted on (see doc-moat learnings).

## The Verifier — closing the loop

`incidents verify <company_id>` snapshots `analytics.data_incident` for one company, re-runs the two checks that are cheap and safe to rerun on demand (Tag Investigator resolution, Time-Series self-consistency), snapshots again, and reports resolved/regressed/still-open. Both underlying functions (`investigate_open_findings`, `timeseries_check.run_concept`) gained an optional `company_id` scope specifically for this — the first live run without it took 90+ seconds and had to be killed because it was reprocessing the whole population's ~20,000 open findings just to verify one company; scoped, the same check runs in under 2 minutes end-to-end for one company (dominated by 7 sequential SQL passes, not per-row work). Deliberately does NOT auto-trigger a fresh yfinance/Frames fetch — those only update on their own scheduled run; verifying a fix that depends on one of those means waiting for that run, then diffing again.

## Period Completeness — which quarters are missing, and why (2026-09-30)

`sanity/period_completeness.py`, migration 0083, runs daily in `pipeline-sanity.yml` (`uv run python -m scrooner_pipeline.sanity.period_completeness [--ciks ...]`, ~8 min for all active companies).

- **Expected periods come from the company's own filings** (`core.filing.period_of_report`): each 10-Q → a quarter, each 10-K → a full year plus a Q4 (derived is fine), balance-sheet concepts → the period-end snapshot. Since 2019, for six concepts: display revenue, net income, diluted EPS, CFO, total assets, equity. Only (company, concept) pairs with at least one value are checked; a concept absent entirely is the tag library's question.
- **Every missing cell gets one cause:** `not_in_sec_feed` (confirmed per filing against SEC's own `companyconcept` accessions, after a 7-day grace), `filing_not_processed`, `conflict_rounding` (≤0.1% apart), `conflict_split` (whole-number ratio, e.g. Apple 2020 4:1), `conflict_material`, `not_resolved`, `q4_not_derived`, `quarter_not_derived` (only year-to-date filed), `no_mapped_tag`. A Q4 whose full year is missing inherits the full year's cause.
- **Stored:** `analytics.period_gap` (one row per missing cell, with filing and filed values), `analytics.period_completeness` (expected/present/missing per company-concept), `analytics.period_gap_summary` (causes ranked by recent periods and market cap), and one `analytics.company_data_finding` per company/concept/cause (`evidence->>'source' = 'period_completeness'`). A cause that stops occurring is marked `fixed` with `resolved_at` — the history of what was wrong and when it cleared is the point.

First run (2026-09-30): 91.1% of expected cells present; 74,888 missing cells, 21,864 findings. Last 15 months by cause: no mapped tag 3,688 · absent from SEC's feed 1,319 (159 companies, e.g. PayPal's 2026-07-28 10-Q) · Q4 not derived 515 · material conflict 505 · quarter only YTD 495 · rounding conflict 466 (Airbnb, JPM FY net income) · split 117 · never processed 15.

## Extending this

- **New checker against an existing source** (more yfinance fields, more Frames concepts/periods): add to the relevant module's existing config list (`METRIC_MAPPINGS`, `CONCEPTS_TO_CHECK`, `LINE_ITEM_MAP`) — verify the real field/shape live first, same discipline as every entry already there.
- **New source entirely**: see [doc 45](../planning/45_Scrooner_yfinance_Expansion_Data_Sanity_Plan.md) for the next-ranked candidates (stock splits, dividends, `edgartools` as a second independent SEC parser) before building from scratch.
- **A finding that looks like a serious new bug**: trace it to the real underlying rows before reporting it as one. The Frames checker's own first real finding (2026-09-08) looked like a serious `is_authoritative` integrity violation and turned out to be a bug in the checker itself — see `learnings/` for the full story before assuming the pipeline is wrong just because a new checker says so.
