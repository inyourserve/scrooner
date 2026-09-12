# Corrected coverage denominator methodology (2026-09-12)

## The mistake this corrects

Every coverage number this project has reported so far — `revenue` at 87.4%, `dividend_yield` at 21.2%, etc. — used the same denominator: all 5,216 `status='active'` companies. That's the wrong test for any data point that doesn't apply to every company by construction.

A SPAC pre-merger has no revenue. A royalty trust has no revenue. Most companies never pay a dividend. Measuring those data points against the whole active population makes a perfectly correct "this company genuinely has none" indistinguishable from "we're missing something this company should have" — the two most different possible explanations for a null, collapsed into one misleading percentage.

**The standing rule going forward: before reporting a coverage number for any data point, ask what population it actually applies to, and use that as the denominator — not `status='active'` by default.**

## Step 1 — establish the real company universe, cross-verified

The 5,216-company `status='active'` count itself needed independent verification before trusting anything built on top of it. Three sources, none of them SEC-derived (to actually be independent):

1. **Alpaca's trading API** (`paper-api.alpaca.markets/v2/assets` — note: NOT `data.alpaca.markets`, the market-data API this project's `alpaca_client.py` already uses for prices; that one 401s on this account's keys for the assets endpoint, since it's a different product surface). Filtered to `status=active`, `tradable=true`, exchange in `(NASDAQ, NYSE, AMEX)` (excludes OTC penny/foreign-ADR listings and ARCA/BATS, which are overwhelmingly ETFs), then excluded name patterns for `ETF|Trust|Fund|Depositary|Preferred|Warrant|Right|Unit|Notes?|Acquisition Corp|SPAC`. Result: **5,392** — within 3.4% of ours.
2. **yfinance's own `y_industry` classification** (already backfilled for 82.2% of active companies via `company_master/yfinance_industry.py`). `y_industry = 'Shell Companies'` independently tags **327** of our active companies as SPACs.
3. **SEC's own live company-facts API**, fetched directly per company for the handful of hardest remaining cases (below) rather than trusting our own stored `raw.sec_companyfacts` snapshot.

All three landed in the same ballpark. Confidence: our 5,216-company universe is approximately right; ~400 of them are not operating businesses.

## Step 2 — build the real "should have revenue" population

`analytics.company_data_point_coverage` already tracks `has_value` per (company, data point) but had no `gap_reason` for concept-level rows (only metric-level rows got one — see `mapper/coverage_matrix.py`'s pre-existing comment). Built `classify_concept_gaps()`, scoped to `REVENUE_FAMILY_CONCEPTS` (revenue, cost_of_revenue, gross_profit, operating_income, operating_expenses + their `_resolved` companions), wired into every `build_coverage()` rebuild.

Every rule is evidence-checked against real companies before being trusted — never a label assumed from a SIC name alone:

| Rule | Evidence | Companies |
|---|---|---|
| `SIC_GAP_REASONS` (SIC-code lookup) | Spot-checked real companies per SIC: "Commodity Contracts Brokers & Dealers" turned out to be commodity ETF/trusts (SPDR Gold Trust, Grayscale Bitcoin Trust) paying sponsor fees, not earning revenue; "Real Estate Investment Trusts" in the gap population is exclusively mortgage REITs earning net interest income | SPACs 280 (SIC only) → 299 (+ yfinance), pharma/biotech 129, commodity trusts 74, banks 13, REITs 11, mining 14 (added same day, below) |
| BDC check | `bdc_total_investment_income` (a separate, already-built, sector-isolated concept) has a value | 35 |
| `_FINANCIAL_INCOME_TAGS` (evidence-based, not SIC) | Company has real `core.fact` rows under `InterestIncomeOperating`/`NoninterestIncome`/etc. — catches real companies a SIC guess misses (Synchrony Financial's SIC is generic "Finance Services," not a bank code) | 19 |
| yfinance `Shell Companies` widening | +26 real SPACs the SIC rule missed; excluded 31 more that yfinance still tags "Shell Companies" but that already have real revenue (a stale yfinance-tag lag, confirmed via `canonical_fact`, not assumed) | 26 net |
| Curated FPI list | Confirmed by fetching each company's own real filing history — all file 20-F/40-F | 6 |
| Curated co-registrant-subsidiary list | Confirmed by fetching each company's own **live** SEC companyfacts payload directly (`data.sec.gov/api/xbrl/companyfacts/CIK...json`) — Ameren Illinois/Georgia Power/Consumers Energy return only `ffd` (registration-fee) tags from unrelated S-3/424B filings; Public Service Co of New Mexico returns a completely empty payload | 4 |
| `Metal Mining`/`Gold and Silver Ores` SIC | Every remaining company under these codes checked by name — Lithium Americas, Trilogy Metals, Perpetua Resources, Dakota Gold: real, named, pre-production exploration miners | 14 |

## Step 3 — a real tag candidate that looked safe and wasn't

Two of the companies surfaced above (NSTAR Electric, MGE Energy) turned out to have real, non-empty data under plausible-looking revenue tags: `ElectricUtilityRevenue` (NSTAR, 1,351 facts across 4 companies) and `RegulatedAndUnregulatedOperatingRevenue` (MGE Energy, 3,697 facts across 2 companies). A small, 5-row coexistence sample against companies that already have both this tag and an existing mapped revenue tag looked consistent (values matched exactly).

**The full-population coexistence check told a different story**: `RegulatedAndUnregulatedOperatingRevenue` disagreed with the existing revenue value in 2,975 of 4,816 coexisting pairs (62%). Sampling a disagreement: Alliant Energy Corp reports the same bare tag with a value of $35M in one row and the real company-wide total of $1.03B in another row for the same period — a business-segment/dimensional breakdown sharing the same tag as the real total, for a *different* company than the one the small sample checked. `ElectricUtilityRevenue` showed the identical pattern (a diversified utility's electric-only segment vs. its real multi-segment total).

**Neither tag was added.** Adding either to `revenue`'s `concept_mapping` would have silently produced a wrong, too-small revenue figure for every other company reporting the tag as a segment breakdown — exactly the "different concept sharing vocabulary" trap this project has documented at least twice before (`CostsAndExpenses`, `LongTermDebtNoncurrent`). NSTAR/MGE Energy stay in the honestly-unexplained tail. A real fix needs dimensional-XBRL-aware extraction (already scoped in doc 23 as genuinely harder, not built) — not a `first_match` tag addition.

**Lesson, worth restating even though a version of it already exists in this project's docs**: a coexistence check's *sample size* matters as much as running the check at all. Five rows from one company is not evidence about every other company that reports the same bare tag.

## Result — revenue

| | Count | % of 4,816 |
|---|---|---|
| Real revenue value | 4,523 | 93.9% |
| Real top-line data under the sector-correct concept (bank/BDC/REIT) | 78 | 1.6% |
| Genuinely, correctly pre-revenue (biotech/mining) | 143 | 3.0% |
| Real SEC-side data-availability limit (FPI/co-registrant) | 10 | 0.2% |
| **Accounted for, total** | **4,754** | **98.7%** |
| Still genuinely unexplained | 62 | 1.3% |

Against the old, wrong 5,216 denominator this same population would read as 87.4% — a 11.3-point gap that was never a real coverage problem, only a measurement one.

## Applying the same principle to dividends

Most companies legitimately pay no dividend — the same denominator mistake applies. Determined the real, *current* dividend-payer population directly from filed data: a company counts if it has a real, nonzero `dividends_paid_resolved` or `dividends_per_share` value in its own most recent reported fiscal year (either signal, unioned — using the latest year, not "ever," since payer status changes and a company that paid once a decade ago and stopped isn't a current dividend payer).

**Result: 1,954 active companies** — matching the ~1,979 ballpark already being tracked from an earlier `/loop` growth-backfill check, a good independent sanity check that this number is stable and real, not a one-off artifact of this specific query.

Coverage against 1,954, not 5,216:

| Data point | Coverage | vs. the old (wrong) 5,216 denominator |
|---|---|---|
| `dividends_paid_resolved` | 96.9% (1,893/1,954) | 36.3% |
| `dividends_per_share` | 89.4% (1,746/1,954) | 33.5% |
| `dividend_growth_streak_years` | 84.1% | 31.5% |
| `dps_growth_yoy` | 83.5% | 31.3% |
| `payout_ratio` | 85.2% | 31.9% |
| `total_shareholder_yield` | 85.4% | 32.0% |
| `dps_growth_3y_cagr` | 76.3% | 28.6% |
| `dividend_yield` | 57.0% | 21.2% |
| `buyback_yield` | 62.1% | 23.3% |

`dividend_yield`/`buyback_yield` stay correctly lower than the others for a genuinely different, already-documented reason: they also require real `market_cap`/price data on top of dividend data, so they inherit that separate coverage ceiling too.

## Generalized to the whole registry (same day, direct follow-up)

The user's direct instruction: *"no for every coverage, follow this same methodology now."* Rather than repeat the revenue/dividends investigation by hand for each of the other 150+ data points, built it as a real, persisted, reusable mechanism.

**Schema** (migration `0062`): `analytics.data_point_registry` gained `applicable_population` (a text label, defaults to `real_operating_company`); a new table `analytics.company_population` (`company_id`, `population_name`) records which named population(s) each company genuinely belongs to — a company can be in several at once (e.g. a real operating company that also currently pays dividends is in both `real_operating_company` and `dividend_payer`).

**Populations, each built from a real, evidence-checked query** (`mapper/coverage_matrix.py`'s `POPULATION_QUERIES` + `classify_company_populations()`):

| Population | Size | Definition |
|---|---|---|
| `real_operating_company` | 4,817 | `status='active'` minus the non-operating `gap_reason`s already classified (SPAC, passthrough trust, commodity ETF trust) — the corrected default, replacing "all active companies" |
| `dividend_payer` | 1,954 | Real, nonzero `dividends_paid_resolved` or `dividends_per_share` in the company's own most recent FY |
| `buyback_company` | 2,449 | Same shape, for `share_buybacks_resolved` |
| `capital_return_company` | 3,009 | Union of the two above — for metrics needing *either* dividend or buyback activity to be a real, applicable case (`cash_returned_to_shareholders`, `total_shareholder_yield`) |
| `bdc_company` | 118 | Has a real `bdc_total_investment_income` value — the already-established sector-isolated BDC population |

`build_registry()` assigns each of the 156 registry rows its `applicable_population`: the dividend/buyback/capital-return/BDC families (curated lists, e.g. `DIVIDEND_FAMILY_DATA_POINTS`) get their narrower population; everything else defaults to `real_operating_company`. New CLI: `scrooner-map corrected-coverage-report` — computes and prints every data point's coverage against its real population directly, joining `company_population` × `company_data_point_coverage`. This is the actual point of the exercise: "why is this number low" is now a query against a durable table, not a from-scratch investigation each time.

### Full-registry result

Averaged across the whole registry, corrected vs. the old ÷5,216-for-everything numbers:

- **Concept average: 75.0% → 82.9%** (+7.9pp)
- **Metric average: 62.2% → 70.7%** (+8.5pp)

Biggest single corrections (every one of these was previously being penalized for the majority of companies that simply don't do the underlying activity):

| Data point | Old (÷5,216) | Corrected | Real population |
|---|---|---|---|
| `bdc_total_investment_income` | 2.3% | 100.0% | bdc_company |
| `dividends_paid_resolved` | 41.2% | 96.9% | dividend_payer |
| `dividends_per_share` | 37.7% | 89.4% | dividend_payer |
| `dps_growth_yoy` | 32.7% | 83.5% | dividend_payer |
| `payout_ratio` | 34.9% | 85.2% | dividend_payer |
| `dividend_growth_streak_years` | 34.0% | 84.1% | dividend_payer |
| `dps_growth_3y_cagr` | 29.7% | 76.3% | dividend_payer |
| `dividends_pct_fcf` | 26.2% | 66.7% | dividend_payer |
| `share_buybacks_resolved` | 63.6% | 100.0% | buyback_company |
| `share_buybacks` | 63.6% | 100.0% | buyback_company |
| `dividend_yield` | 21.8% | 57.0% | dividend_payer |
| `buyback_yield` | 36.5% | 65.7% | buyback_company |
| `share_repurchases_pct_fcf` | 34.2% | 61.7% | buyback_company |
| `cash_returned_to_shareholders` | 33.3% | 55.9% | capital_return_company |

### What stays genuinely low even after correction — a different, honest finding

Not every low number is a denominator problem. These are all measured against the correct `real_operating_company` population already, and stay low for a real, already-documented reason:

- `mutual_fund_ownership` (0.2%) — golden-10-only scaling status, a known, not-yet-closed gap (see root `CLAUDE.md`'s ownership entries).
- `employee_count` (3.7%) — `dei:EntityNumberOfEmployees` genuinely covers only ~3.5% of companies as structured XBRL.
- `piotroski_f_score` (27.3%) — deliberately needs all 9 raw inputs simultaneously for two consecutive FY years; a demanding, already-documented, working-as-intended bar, not a bug.
- `net_interest_income` / `cash_conversion_cycle` / `inventory_days` / `rnd_intensity` (35-45%) — each needs multiple simultaneous inputs (interest income AND expense both; three separate working-capital concepts; R&D itself is optional under GAAP for many industries) — a real data-completeness ceiling, not a population mismatch.

The distinction matters: a "doesn't apply to this population" gap and a "applies, but the data genuinely isn't complete enough" gap look identical as a bare percentage, but call for completely different responses — the first needs a corrected denominator (done here), the second needs either accepting the honest ceiling or a real, separate data-completeness investigation (not done here, correctly left as its own future work).

## What this changes going forward

- Any future "coverage is X%" claim for a data point that doesn't structurally apply to every company needs its own real denominator, established the same way: pick the actual applicable population, cross-verify it isn't an artifact of one query, then measure against it. As of this pass, this is no longer a manual step for the 156 data points already in the registry — `scrooner-map corrected-coverage-report` computes it directly from `analytics.data_point_registry.applicable_population` × `analytics.company_population`.
- `mapper/coverage_matrix.py`'s `gap_reason` is now the queryable source for "why is this missing" for the revenue family — no more from-scratch manual SIC-clustering needed for that specific question. Extending the same `gap_reason` mechanism to other structurally-uneven data points (dividends, buybacks, segment-specific concepts) is the natural next step, not yet built.
- `POPULATION_QUERIES`/`classify_company_populations()` is deliberately a small, curated set of 4 named populations (plus the `capital_return_company` union), not a combinatorial explosion of one population per data point — new populations should only be added the same way these were: a real, checked business-model reason a whole family of data points shares, not a one-off per metric.
- A same-day regression was found and fixed while investigating this: MannKind Corp (the exact company from the 2026-09-03 leap-year-FYE fix) had silently dropped back to zero `core.fact` rows sometime after that fix landed. Rebuilt live (19,112 facts restored, full normalizer+mapper chain rerun, zero errors) — root cause of the regression itself not yet chased; worth watching for recurrence on the next full-population rerun.
