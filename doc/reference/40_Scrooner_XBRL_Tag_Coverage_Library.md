# 40 — XBRL Tag Coverage Library

> **Superseded 2026-09-08** — the JSON file this doc describes (`pipeline/reference/xbrl_tag_coverage_library.json`) and its generating script (`pipeline/scripts/build_tag_coverage_library.py`) are **retired and deleted**, per direct instruction ("retire json, make everything into db as source of truth"). The JSON was manually-triggered only and had gone stale (last built 2026-09-02, missing everything since — including this same day's `other_income_expense_net` addition and the `CostsAndExpenses` rejection). Its function now lives in `analytics.concept_tag_candidate` (`pipeline/src/scrooner_pipeline/mapper/tag_candidates.py`), rebuilt every day in the same cron pass as the coverage matrix (`doc/data-moat/SYSTEMS.md`) — `scrooner-map build-tag-candidates` to rebuild on demand, `scrooner-map tag-candidate-report` to read the current concept-by-concept status. The findings and reasoning below (the keyword-matching caveats, the `total_debt` double-counting risk) are unchanged and still the operative discipline — only the storage mechanism moved.
>
> **Original status (historical, kept for context):** Reference, living (built 2026-09-02) — a real, queryable inventory of what XBRL tags companies actually use for each of Scrooner's 44 canonical concepts, generated from live data. **Owner:** Founder/Product.

## Why this exists

Prompted directly (2026-09-02) after pushing core financial metric coverage and finding a real, live risk: `total_debt` (the one canonical concept using `sum` resolution mode) had a 360-company gap where the obvious fix — adding split debt tags (`LongTermDebtCurrent`/`LongTermDebtNoncurrent`) — would have double-counted debt for ~2,168 *other* companies that already report both forms. That finding turned into a broader ask: build a real, systematic library of what tags exist per concept, not re-derive coverage gaps live, one metric at a time, forever.

## What was built

1. **`pipeline/scripts/build_tag_coverage_library.py`** — a research tool (not wired into any CLI or production job), rerunnable, surveys all 44 canonical concepts against the real active-company population: current coverage, current mapped tags, and candidate unmapped tags (ranked by real company-count) drawn from `core.fact`'s actual tag universe.
2. **`pipeline/reference/xbrl_tag_coverage_library.json`** — the structured output, one entry per concept.
3. **Two real, previously-missing database indexes found and fixed while building this** (`db/migrations/0032_fact_concept_id_index.sql`) — `core.fact` and `analytics.canonical_fact` both had no index with `concept_id`/`canonical_concept_id` as a leading column, the same indexing-gap shape already found and fixed twice before (migrations 0019, 0029) for different columns. A basic "how many companies have this concept" query took 2+ minutes without them; both now support any future concept-coverage query, not just this script's own.

## A critical finding while using it: keyword-matched candidates are frequently wrong, not just noisy

The script's `gap_safe_candidate_found` label is a **starting point for verification, not an approval**. Real examples found checking the actual output before adding anything:

| Concept | Top keyword-matched "candidate" | Why it's wrong |
|---|---|---|
| `research_and_development` | `DeferredTaxAssetsInProcessResearchAndDevelopment` | A deferred tax asset, not R&D expense — shares the word "Research," nothing else |
| `goodwill` | `IntangibleAssetsNetExcludingGoodwill` | Explicitly *excludes* goodwill — the opposite of the concept |
| `comprehensive_income` | `AccumulatedOtherComprehensiveIncomeLossNetOfTax` | An accumulated balance-sheet balance, not the period's income-statement flow |
| `effective_tax_rate_reported` | `EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate` | The fixed *statutory* rate (~21%), not the company's own effective rate |
| `inventory` | `InventoryWriteDown` | A write-down amount, not the inventory balance |

Same-statement-area, similar-keyword tags are frequently a *different concept entirely* that happens to share vocabulary. Every candidate this library surfaces still needs the same live spot-check discipline already used everywhere else in this project's concept-mapping history — 2-3 real companies, plausible values, before marking anything beyond `provisional`.

## What was actually shipped from this pass, each individually verified before adding (not batch-applied from the raw candidate list)

- **`gross_margin`** switched from requiring a direct `GrossProfit` tag (2,525/5,024 companies) to deriving it as `(Revenue − Cost of Revenue) / Revenue` (`calculate.py`'s `sum_diff_ratio` shape) — verified exact equality against Apple's own reported figures across 3 real periods first. Coverage: 2,458 → 2,922 companies.
- **Three new fallback tags**, `provisional`, priority 2 (never override the existing approved tag): `cost_of_revenue` ← `CostOfGoodsSold` (verified against Cencora/Cardinal Health, pharma distributors with genuinely huge COGS), `capex` ← `PaymentsToAcquireProductiveAssets` (verified against Amazon), `share_buybacks` ← `StockRepurchasedDuringPeriodValue` (verified against Wells Fargo; one real anomaly noted — SPDR Gold Trust, an ETF, also uses this tag for its own share-redemption mechanism, not a real corporate buyback — a known edge case, not chased further).
- **`total_debt_split` + `total_debt_resolved`** (`db/migrations/0033_total_debt_fallback.sql`, `mapper/concept_fallback.py`) — the actual fix for the 360-vs-2,168-company risk that started this whole pass. See that module's own docstring for the full design; every consumer of the old `total_debt` concept (`debt_to_equity`, `roic`, `net_cash`, `net_cash_per_share`, `net_debt_ebitda`, `ev_ebitda`, `ev_sales`, Piotroski's leverage test, the `zero_debt` flag, and the company page's own "Total Debt" balance-sheet display line) was repointed to `total_debt_resolved` in the same pass — found via `grep`, not assumed complete after the first few obvious ones.

## What's in the library but NOT yet acted on

The full `xbrl_tag_coverage_library.json` has real candidates for most of the 44 concepts (`accounts_receivable`, `accounts_payable`, `depreciation_and_amortization`, `interest_expense`, `interest_income`, `operating_expenses`, `dividends_paid`, `dividends_per_share`, and more) that were surveyed but not individually verified/added in this pass — each needs the same live spot-check before trusting it, and the false-positive rate found above (roughly half of the top candidates checked by eye were wrong) means this is real, unhurried work, not a batch job. Treat `status: "gap_safe_candidate_found"` in the JSON as "worth investigating next," not "safe to add."

## How to use this going forward

- Before assuming a metric's low coverage is "just how it is," check this library first — rerun the script if it's more than a few weeks old (`uv run python scripts/build_tag_coverage_library.py` from `pipeline/`).
- Any concept using `sum` combination_mode (today: only `total_debt`) needs the `concept_fallback.py` pattern for any widening, never a direct add to its own `concept_mapping` — that's the double-counting trap this whole doc exists to prevent recurring.
- Any concept using `first_match` (43 of 44) can be safely widened by adding a new `provisional` `concept_mapping` row at the next priority — but only after the same live-verification discipline this doc's own "critical finding" section demonstrates is necessary.
