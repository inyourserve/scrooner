# Scrooner 2015 Coverage Completion Plan

**Status: Active plan, written 2026-10-04, Phase 0 complete 2026-10-05.** Prompted directly by: *"plan all financial columns should be filled since January 2015. If company listed later on: so from listing date to till date, this will be the biggest winner."*

## The core problem with the goal as stated

"Fill every financial column since 2015" isn't currently *measurable* — the one tool built to measure exactly this (`sanity/period_completeness.py`) only checked back to **2019-01-01**, not 2015, and only checked **6 of ~78 concepts / 82 metrics**. Phase 0 has to fix the ruler before anything else, or progress is unverifiable.

**Baseline measured before any fix (2026-10-04, from `analytics.coverage_snapshot`):**
- Core V1 metrics (20 locked): **77.78%** covered
- All 82 metrics: **72.37%** covered
- All 78 concepts: **85.45%** covered
- Weakest metrics: `piotroski_f_score` (27%), `cash_conversion_cycle` (35%), `peg_ratio` (37%) — mostly composite metrics needing several inputs at once
- Weakest concepts: `collaborative_arrangement_revenue` (0.5%, niche — probably not real), `employee_count` (3.7%, known structural, text-extraction only), `dividends_per_share_resolved` (41%, looks like a real gap worth investigating)
- Universe split: 2,843 companies have real filings back to 2015+; 2,373 listed after 2015 (the "from listing date" rule applies to these)

## The plan — 6 phases, in order

**Phase 0 — Fix the ruler.** Widen `HISTORY_START` to 2015-01-01 and `CHECK_CONCEPTS` from 6 to every concept with a genuine quarterly/annual cadence (excludes text-extraction-only fields like `employee_count`, which can't be period-complete the same way). Turns "fill since 2015" from an aspiration into a tracked number — the same 3-state model `company_coverage_dashboard.py` already uses, applied with the right floor and the right scope.

> **Status: COMPLETE (2026-10-05).** Widened `HISTORY_START` 2019→2015, `CHECK_CONCEPTS` 6→16. Along the way, found and fixed a real structural bug in `normalizer/derived.py` (Q1-period-labeling failure for companies with an atypical first-quarter length, e.g. Albertsons' 111-day Q1) that was silently breaking Q2/Q3/Q4 derivation — plus a missing `safe_rollback()` reconnect bug that caused 82% failures on the first full-population attempt. Reprocessed the entire `calculate`-family chain population-wide (5,216 companies, 0 errors). Result: 3,858 open cockpit findings confirmed fixed, "Q4 not derived" dropped 20,129→16,968 open, coverage score up modestly (`avg_metric_coverage_score` 72.37%→72.99%). Full writeup: `pipeline/CLAUDE.md`'s 2026-10-04/05 entry.

**Phase 1 — Finish what's running.** `resolve-facts` (in progress at the time this plan was written) propagates the derive-interim/derive-q4 fix. Once done: rerun the fixed, widened `period_completeness` to get the real new baseline. This alone should move the needle a lot, since the fix touched the *mechanism* every later quarter depends on.

> **Status: Effectively absorbed into Phase 0's full reprocessing run** — `resolve-facts` and every downstream stage ran population-wide as part of Phase 0's completion, and the widened `period_completeness` re-measure happened at the end of that same pass.

**Phase 2 — Systematic tag-agent sweep.** Run `scripts/find_period_gap_candidate_tags.py` against every remaining open cluster in `analytics.company_data_finding`, concept by concept, cross-referenced against the SEC XBRL Tag Expert's own canonical dictionary as a checklist. Each candidate still gets coexistence-tested and human-reviewed before being added — same discipline as every prior tag addition this project has made, no shortcuts.

> **Status: Not started.**

**Phase 3 — Close the "genuinely doesn't apply" gap.** `coverage_matrix.py`'s `classify_concept_gaps()` only recognizes structural absences (bank/REIT/BDC/SPAC) for the revenue family today. Widening it to the rest of the concepts means the 2015-to-date target is honest — not chasing 100% on cells that can't exist (e.g., a bank reporting `cost_of_revenue`), and the dashboard correctly tells weak-but-real gaps apart from non-applicable ones.

> **Status: Not started.**

**Phase 4 — Attack the named weak list directly.** `dividends_per_share_resolved` (41%) and the reconciliation-gap metrics are the most promising real targets from the baseline list above — worth a dedicated investigation pass each, same shape as the `net_income`/`diluted_eps` fixes already made.

> **Status: Not started.** Candidate next step: the "authoritative fact not resolved" cluster that grew 1,096→4,998 open during Phase 0's widened re-measure (a side effect of measuring more, not a new bug) is a strong candidate to fold into this phase's scope.

**Phase 5 — Full-population reprocess + re-measure loop.** After each batch of fixes: rerun the affected Normalizer/Mapper stages population-wide (sharded, as proven in Phase 0), then re-run `period_completeness` against the 2015 floor, and track the real number over time via the coverage snapshot + the company-wise cockpit dashboard.

> **Status: The mechanism (sharded full reprocessing + re-measure) is proven and reusable, built during Phase 0.** Not yet run as a repeating loop — each future phase should close with its own instance of this step.

## Next step

Phase 0 is done and verified. Phase 1 is effectively subsumed. The next real work is **Phase 2 (tag-agent sweep)** or **Phase 4 (attack the named weak list / the newly-surfaced "authoritative fact not resolved" cluster)** — pick one based on which the founder wants prioritized; both are legitimate next moves and neither blocks the other.
