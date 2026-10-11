# Scrooner Coverage & Ticket Backlog Replan (2026-10-11)

**Why this doc exists.** Doc 50 (the 2015 coverage completion plan) and doc 51 (the cockpit ticket triage) have both run their course for tonight — most of what each originally scoped is done, and what's left in each turned out to need real redesign, not a quick extension. This doc consolidates both threads into one prioritized plan for what's actually next, grounded in live numbers checked immediately before writing it (2026-10-11), not recalled from memory.

## Where things actually stand right now

- **Tickets** (`analytics.company_data_finding`): 54,607 open / 16,599 fixed / 2 wont_fix. Open by type: `pipeline_bug` 30,480, `data_limit` 20,016, `filer_error` 4,111.
- **Coverage** (`analytics.coverage_snapshot`, `item_type='score'`): `avg_concept_coverage_score` 85.60%, `avg_metric_coverage_score` 74.61%, `avg_core_v1_metric_coverage_score` 78.32%.
- **Doc 50's 6 phases**: 0/1/4/5 complete and verified. 2 (tag-agent sweep) is exhausted for the concepts worth checking — every remaining `no_mapped_tag` cluster checked came back with no safe tag-mapping fix. 3 (the "genuinely doesn't apply" classifier) was investigated properly tonight and found to need a fundamentally different, period-conditional design — not started, correctly not rushed.
- **Doc 51's "fix first" list** (Findings 4/13/16/22/23): all shipped, rolled out to the full population, verified with 0 errors.
- **The `_sec_feed_accessions()` classifier bug** (empty-probe-treated-as-confirmed-absence): fixed and shipped. Reclassified ~1,570 tickets from `data_limit` to the honestly-labeled `pipeline_bug`.
- **The fresh yfinance sanity/plausibility/identity re-run**: explicitly decided as the final step, **still not done** — got displaced by the Phase 4/3 coverage-denominator investigation. This is the single most overdue item from tonight's own plan.
- **The "Parser 4" idea** (SEC's bulk Company Facts lagging 2+ months behind a confirmed-filed 10-Q for large companies — Visa, Sonoco, OneMain, UDR all confirmed real examples): found, sized (~2,391 of 5,620 "filing absent" tickets are this shape), **never decided** — raised once, never revisited.

## The plan, in priority order

**1. Run the fresh yfinance sanity/plausibility/identity re-run.** This was decided before any of tonight's coverage work started and is the one thing that's been waiting the longest. Zero new investigation needed — just execute: `scrooner-sanity run` (rotates the active population, yfinance-rate-limited, takes hours for a meaningful slice), `scrooner-sanity plausibility`, `scrooner-sanity identities`, `scrooner-sanity timeseries` (all three of these are zero-external-call, whole-population, fast). This closes the loop doc 51 opened and gives a real fresh "is our displayed data actually wrong" signal for the first time since all of tonight's fixes landed.

**2. Decide on Parser 4 (the SEC bulk-data-lag gap).** This needs a founder decision, not more investigation — the evidence is already solid (3 confirmed real companies, ~2,391 tickets sized). The real question is scope and priority: build a generalized "read the filing's own rendered R\*.htm statement, bypass SEC's aggregation lag" capability for the core balance-sheet/income-statement concepts (the same proven pattern as `revenue_parser.py`/`cost_of_revenue_parser.py`), or leave this bucket as an accepted, named limitation. Either answer is fine — what's not fine is leaving it undecided indefinitely.

**3. Design Phase 3's real shape: a period-conditional classifier.** Tonight's investigation disproved the original company-level premise cleanly (near-0% of gap companies ever fully lack these concepts) and found the real pattern instead: pre- vs. post-SPAC-merger lifecycle stage, confirmed on 3 real companies (MultiSensor AI Holdings, VSee Health, Alpha Star Acquisition). Before building anything: verify this generalizes past 3 companies (sample more of the `cash_flow_investing`/`financing` gap population specifically for the SPAC-merger-timing pattern), then design a classification key that can express "before this company's own transition date," not just a SIC code. This is real, scoped work — not a quick fix.

**4. Re-measure after step 1 lands.** Once the fresh sanity pass completes, re-run `period_completeness` + `snapshot-coverage` one more time to get the true, final before/after numbers for everything shipped tonight — the numbers in this doc's "where things stand" section above are from *before* the fresh yfinance data, so they don't yet reflect any plausibility/identity findings from the re-run.

## What's deliberately NOT on this list

- Further Phase 2 tag-agent sweeping — confirmed exhausted for now; revisit only if Phase 3's redesign surfaces a new concept worth checking.
- Rebuilding the classifier for `income_tax_expense`/`basic_eps`/`diluted_eps`/`income_before_tax`/`cfo` the same way as `cash_flow_investing`/`financing` — these 5 need their own lifecycle-pattern check before assuming the SPAC-merger story generalizes to them too; don't assume, verify each the same way revenue/inventory/AR/AP/cash-flow were each individually verified tonight.
