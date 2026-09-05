# Financials Display Spec — Data-Point Gap Analysis and Batch A-D Build (2026-09-05)

**Scope note:** this work is explicitly limited to pipeline data points (canonical concepts,
metric definitions, computed values) per direct instruction — frontend/UI rendering of the
spec is being handled separately (Codex), not by this pass.

## Source

[`doc/Frontend/financials/scrooner-financials-display-spec-final.md`](../Frontend/financials/scrooner-financials-display-spec-final.md)
("Final v2") — defines the Financials section of the company page: Quarterly Financial
Results / Income Statement / Balance Sheet / Cash Flow Statement, an Investor View vs.
Detailed View split, per-metric provenance, locked EBITDA (`Operating Income + D&A`) and FCF
(`CFO − Capex`) formulas — both already matching this project's existing computation — and
auto-generated "signal chips" (revenue growth trend, margin trend, net cash/debt trend,
dilution trend).

## Gap analysis

Inventory taken before building: 47 `canonical_concept` rows, 11 `statement_line` rows, 64
`metric_definition` rows (pre-session). Cross-referenced against every metric/ratio the spec's
§4-§9 name. Most of the spec's needs were already covered by existing locked metrics
(margins, ROE/ROIC, the 4 growth families, leverage ratios, Piotroski). The real gap was 18
specific metrics never built, all computable with **zero new SEC fetches** — every required
input concept (`stockholders_equity`, `current_assets`/`current_liabilities`, `cash_and_
equivalents`, `net_income`, `cfo`, `capex`, `dividends_paid`, `share_buybacks`, `shares_
outstanding`, `ebitda`, `fcf`) already resolves in `analytics.canonical_fact`/`metric_value`.

## Phase 1 (this pass) — 18 new metrics, built and verified

Split across 4 existing computation modules, each metric routed to whichever module's shape
already fits (no new module needed):

**`calculate.py`'s generic engine** (data-only additions, `metric_definition_input` rows +
`FORMULA_SHAPES` entries): `book_value_per_share` (ratio), `working_capital` (sum_diff),
`net_change_in_cash` (additive), `ocf_to_net_income` (ratio), `cash_returned_to_shareholders`
(additive).

**`ttm.py`'s `GROWTH_METRICS`** (2-line dict additions, reuses `_growth_value` unchanged):
`net_income_growth_yoy/3y/5y/10y_cagr`, `diluted_shares_growth_yoy/3y/5y_cagr` — the last
three use `shares_outstanding` as a proxy for diluted weighted-average shares, since this
project has no separate concept for the latter yet (same precedent `share_dilution_trend`
already established).

**`fcf_growth.py`**: added `fcf_growth_yoy` alongside the existing 3y/5y CAGR entries (1-line
`LAG_YEARS` addition).

**`expanded_metrics.py`**: `ebitda_margin`, `debt_to_ebitda`, `fcf_per_share`, `share_
repurchases_pct_fcf`, `dividends_pct_fcf` — all price-independent composites mixing
`metric_value` (ebitda, fcf) with `canonical_fact` (total_debt_resolved, shares_outstanding,
share_buybacks, dividends_paid), the same reasoning already established for `net_debt_ebitda`.
Added a new `_fcf_ttm()` helper (mirrors the existing `_ebitda_ttm()`), and confirmed live
that `dividends_paid`/`share_buybacks` are both stored as positive magnitudes (no sign-flip
needed).

Every new metric name was added to its module's deferral/registry set (`DEFERRED_TO_STAGE_3E`,
`DEFERRED_TO_EXPANDED_METRICS`, `main_calculator.py`'s `METRIC_CALCULATOR_REGISTRY`) in the
same edit as its `metric_definition` seed row — the exact discipline this project's own
`net_debt_ebitda`/`share_dilution_trend` incidents established, applied proactively this time
rather than re-discovered by a crash.

**Testing**: 5 new `FORMULA_CASES` entries (hand-computed numeric cases), all 18 names added
to `EXPECTED_EXPANDED_DEFINITIONS`, `test_expanded_metrics.py` extended with `_fcf_ttm`
monkeypatches and 5 new value/null-reason assertions. Full suite: 383/383 passing.

**Verification**: full compute chain (`calculate`, `growth`, `calculate-fcf-growth`,
`calculate-expanded-metrics`) run for AAPL and JPM (a bank, deliberately picked as the
project's standard edge case). All values plausible and internally consistent — AAPL's
`diluted_shares_growth_yoy` -1.66% and `share_repurchases_pct_fcf` 60% both correctly reflect
its well-known aggressive buyback program; JPM's `working_capital`/`ebitda_margin`/`fcf_per_
share` correctly null (banks report no classified current/non-current balance sheet and no
EBITDA-shaped income statement — the same reason Piotroski F-Score already nulls for JPM/ARCC),
while its non-bank-specific new metrics (`book_value_per_share` $140.92, `cash_returned_to_
shareholders` $11.1B, `net_income_growth_yoy` 41.2%) are all real and plausible.

**One real non-bug found and resolved during verification**: `book_value_per_share` initially
appeared to null for AAPL's *most recent* quarter (`incomplete:numerator`), which looked like a
regression. Root-caused: AAPL has **two distinct `core.period` rows for the same nominal fiscal
quarter** — one at the true balance-sheet date (e.g. 2026-06-27) where both `stockholders_
equity` and `shares_outstanding` resolve, and a second, later one at the 10-Q's own cover-page
filing date (e.g. 2026-07-17), created because `dei:EntityCommonStockSharesOutstanding`'s
instant context uses the filing date, not the quarter-end — confirmed this pattern repeats for
every historical quarter, not just the latest (a pre-existing Normalizer period-classification
characteristic, unrelated to this session's changes). `calculate.py`'s existing "iterate every
anchor period, null on any incomplete role" logic did exactly the right thing: it correctly
computed the real value for the balance-sheet-dated period and correctly nulled the cover-page-
only period (since `stockholders_equity` genuinely has no fact there). Both rows are real and
traceable — my own verification query simply sorted `period_end desc` and surfaced the null row
first, creating a false impression of a regression. No code change was needed; documented here
so a future check of this metric isn't re-investigated as a new bug.

## Rollout

AAPL + JPM pilot verified 2026-09-05. Full-population backfill launched the same day via
`scripts/backfill_financials_spec_metrics.sh` (200-CIK chunks, sequential, reusing the exact
pattern `scripts/backfill_zero_fetch_metrics.sh` established 2026-08-29 for the same
"new generic-engine metrics never scaled" situation) across all ~5,216 active companies, all 4
touched stages (`calculate`, `growth`, `calculate-fcf-growth`, `calculate-expanded-metrics`).

**Real environment gotcha hit launching this**: the harness's background-execution mode does
not reliably inherit this shell's full `PATH` when invoking a `#!/bin/zsh`-shebang script file
directly (`./script.sh` failed both via manual `nohup ... &` and via the harness's own
`run_in_background`, both with `command not found: rm` at the script's own `rm -rf` line,
despite `rm`/`PATH` resolving fine for a plain inline command in the same background mode).
Fixed by exporting `PATH` explicitly at the top of the command and inlining the script body
directly as the Bash tool's `command` argument rather than invoking it as a separate executable
file. Worth remembering for any future backgrounded shell-script launch in this harness.

## Phase 2 (sized, not built) — new canonical concepts needing tag-coverage investigation

Concepts the spec implies but this project doesn't have yet, each needing the same
"investigate real XBRL tags before mapping" discipline as every prior concept addition
(`doc/reference/40_Scrooner_XBRL_Tag_Coverage_Library.md`'s methodology):

- Balance sheet: `short_term_investments`, `intangible_assets`, `deferred_revenue`,
  `retained_earnings`, `treasury_stock`, `accumulated_other_comprehensive_income`,
  `common_stock_apic`, `deferred_tax_assets`/`deferred_tax_liabilities`, `operating_lease_
  liabilities`, `non_controlling_interest` (balance sheet).
- Income statement: `ebit` (distinct from `ebitda`), `restructuring_charges`,
  `acquisition_related_charges`, `discontinued_operations`, `other_income_expense`,
  `non_controlling_interest` (income statement), and `basic`/`diluted` weighted-average-shares
  as their own concepts (currently proxied by `shares_outstanding` — see Batch A-D's growth
  metrics above).
- Cash flow: `acquisitions`, `debt_issued`, `debt_repaid`, `common_stock_issued`, `effect_of_
  fx`, `purchases_of_investments`/`sales_of_investments`, `deferred_income_taxes`, `change_in_
  deferred_revenue`.

## Phase 3 (not sized) — sector-specific templates

Banks/insurance/REITs each need their own statement template (spec §11) — a substantial
separate effort, comparable in scope to doc 42's "Parser 4," not attempted this pass.

## Also flagged, not yet built

"Average margin over 3/5 years" (`avg_gross_margin_3y/5y`, `avg_operating_margin_3y/5y`,
`avg_net_margin_3y/5y`) — surfaced during this gap analysis, needs genuinely new logic (no
existing shape computes "average of a metric's own past N values"), deferred.
