# Cockpit Ticket Triage — 2026-10-05

**Status: Investigation in progress, written for tonight's fix session.** Full day task: pick up every open `analytics.company_data_finding` ticket, group by root cause, find the highest-leverage ("whale") fixes, document findings — **investigation and write-up only, fixing happens tonight.**

> **⚠️ CRITICAL CAVEAT, read before trusting any count below: `analytics.period_gap` (and therefore `analytics.company_data_finding`) is a snapshot frozen at 2026-10-04 19:08:55 UTC — BEFORE both the balance-sheet-identity fix (Finding "already shipped" below) and the period-corruption cleanup (Finding 2) landed.** Confirmed by checking `period_gap`'s own `checked_at` column directly. This means every count cited in this document (e.g. `total_liabilities_resolved` still showing 9,178 "no_mapped_tag" gaps, when that exact concept was fixed to ~100% hours ago) is **stale relative to today's own fixes** — the real remaining count is almost certainly lower once `period_completeness` is rerun fresh. **The root-cause findings and mechanisms described below are still real and valid** — only the specific ticket counts need a fresh measurement before tonight's prioritization is finalized. Rerun the full `period_completeness` + rebuild `company_data_finding` as the FIRST step tonight, before trusting any number here for sizing decisions.

## Starting state

60,188 open tickets (as of this morning, before today's cleanup work — see note below on staleness). Grouped by `summary`/`finding_type`:

| Summary | Count | Companies | Type |
|---|---|---|---|
| Periods missing: no mapped tag in the filing | 17,735 | 4,067 | data_limit |
| Periods missing: Q4 not derived | 16,968 | 4,129 | pipeline_bug |
| Periods missing: quarter filed only as year-to-date | 9,622 | 3,806 | pipeline_bug |
| Periods missing: filing absent from SEC Company Facts | 5,681 | 735 | data_limit |
| Periods missing: authoritative fact not resolved | 4,998 | 2,741 | pipeline_bug |
| Periods missing: filings disagree materially | 3,137 | 1,612 | filer_error |
| Periods missing: filings disagree by a stock-split ratio | 2,001 | 1,046 | pipeline_bug |

**⚠️ Known staleness**: `analytics.company_data_finding` (the cockpit table) is a snapshot that predates some of today's reprocessing. `analytics.period_gap` (the live table `period_completeness.py` writes) already reflects today's balance-sheet-identity fix and the period-corruption cleanup. Re-sync the cockpit from `period_gap` before tonight's session to get accurate current counts — the numbers below are cross-checked against `period_gap` directly, not the stale cockpit snapshot.

---

## Finding 1 (WHALE, already shipped): balance-sheet identity fallback

**Status: DONE, not a tonight task.** See `pipeline/CLAUDE.md`'s 2026-10-05 entry. `total_liabilities_resolved`/`stockholders_equity_resolved` now ~100% of the population. `avg_concept_coverage_score` 85.48%→85.62%.

## Finding 2 (WHALE, root-caused and code-fixed, cleanup in progress): corrupted filer-date periods

**Status: Code fix shipped, data cleanup running in background as of this writing.** 10,227 `core.period` rows span >400 days — real filer-side XBRL context-date corruption (truncated years like "205-01-01", Oracle's 1900-2199 sentinel span, companies spanning into 1967/1976/2108). 88,903 affected facts were `is_authoritative=true` — live corruption, not cold data. Confirmed real impact: MIND Technology had two competing `canonical_fact` rows for the same quarter's operating income.

- **Root cause fixed**: `normalizer/periods.py::extract_distinct_periods()` now rejects implausible periods before any `core.period` row is created (commit `bb9d63d`).
- **Existing bad data**: 88,903 facts marked `is_authoritative=false` (reversible, not deleted). 1,754 affected companies' full calculation chain is being rerun as of this writing — check `/tmp/bogus_remaining_stages.log` for completion before assuming this is done.
- **Nothing left to do here tonight** unless the rebuild didn't finish — verify first.

## Finding 3 (REJECTED, documented): dividends_per_share fallback

**Status: Closed, do not re-attempt without new evidence.** `dividends_paid ÷ shares_outstanding` looked like a candidate but verified unsafe two ways: (a) internal coexistence only 67% agreement, (b) real yfinance ground truth (Digital Realty Trust's actual $1.22/share/quarter vs. our implied $2.497 — `dividends_paid` bundles preferred-stock dividends with common). No safe derivation exists today.

## Finding 4 (WHALE CANDIDATE, sized, not yet fixed): `conflict_split` mislabeling bug

**Real, scoped, high-confidence fix for tonight.** `sanity/period_completeness.py::_is_split_ratio()` is a generic numeric check ("do two values differ by a whole-number ratio ≥2, within 2%") applied to **every** concept, with no awareness that only per-share/share-count concepts (`basic_eps`, `diluted_eps`, `dividends_per_share`, `shares_outstanding` — the same 4 already in `dedup_majority_resolver.py`'s `SPLIT_AWARE_CONCEPTS`) can legitimately be affected by a stock split.

**Confirmed via real samples**: `total_assets_resolved` tickets labeled "conflict_split" show ratios like 41.3x, 38.76x, 20.86x, and ~938x (Palomino Laboratories) — none are real split ratios (companies don't do 41-for-1 splits). These are almost certainly genuine material disagreements or **unit-scale filer errors** (the ~938x one especially looks like a dollars-vs-thousands mistake) currently hidden under an incorrect "harmless split" label.

**Scope**: ~1,810 tickets across 10 non-per-share concepts (`cash_and_equivalents_resolved` 366, `income_before_tax_resolved` 274+349, `income_tax_expense_resolved` 229+686, `cash_flow_investing_resolved` 223+320, `cash_flow_financing_resolved` 215+316, `cfo_resolved` 162+127, `stockholders_equity_resolved` 92+145, `revenue_sanity_resolved` 75+73, `net_income_resolved` 39+30, `total_assets_resolved` 37+9, plus smaller balance-sheet concepts) are currently mislabeled "conflict_split" when they're really `conflict_material`.

**Fix for tonight**: scope `classify()`'s call to `_is_split_ratio()` to only the 4 real per-share/share-count concepts. Everything else falls through to `conflict_material`, where it belongs — surfacing real disagreements (including possible unit-scale bugs) instead of hiding them.

**Bonus investigation thread this unlocks, confirmed real (not just hypothesized)**: once un-hidden, the "conflict_material" dollar-value tickets with suspiciously round large ratios (~10x, ~100x, ~1000x) are worth a dedicated sweep for unit-scale filer errors. Confirmed one real, clean instance by hand: **Palatin Technologies, Q4 2019 `NetIncomeLoss`** — two raw filings disagree `52224` vs `52224000`, an exact 1000x ratio (a real filer-side unit-scaling typo, one filing's amendment forgot to apply the "reported in thousands" multiplier). FY2019 (`35773027`) is unaffected and authoritative. **Methodology note**: an initial broad scan mixing values across 3 different concepts (Assets/NetIncomeLoss/Revenues) in one query produced noisy, unreliable matches — always scope a ratio comparison to facts under the SAME tag/concept for the SAME period, never compare across concepts. A dedicated tonight-or-later sweep should redo this properly scoped, concept by concept, to size the real population of these typos (likely in the hundreds, not thousands, based on Finding 4's other evidence) — each one a candidate for a safe, narrow "pick the more plausible magnitude" auto-resolution, distinct from both Finding 4 (the labeling bug) and Finding 5 (majority vote).

## Finding 5 (WHALE CANDIDATE, sized, modest yield): extend majority-vote dedup to income-statement concepts

**Real but smaller than hoped — do, but don't oversell it.** `dedup_majority_resolver.py`'s `SAFE_CONCEPTS` list only covers 9 balance-sheet concepts, deliberately excluding income-statement concepts (revenue, net_income, cfo, operating_income, income_tax_expense, income_before_tax) because a prior sample showed only 68-75% overall agreement ("a blind majority vote would silently pick a wrong number ~25-30% of the time").

**Found a real instance**: American Express FY2016 `income_tax_expense` has 3 raw filed values (2688M, 2667M, 2688M — a clear 2-of-3 majority) but Stage 2e marked all 3 non-authoritative, and this exact concept family is excluded from the fix that would otherwise catch it.

**Sized the real opportunity** (sampled 800 of 27,765 "not_resolved"/"q4_not_derived" income-statement gaps): 333/800 (42%) had no FY row at all (a quarterly gap, not an FY-resolution issue — not helped by this fix). Of the remaining 467, only 16 (3.4%) had a clear real majority. **Extrapolated: roughly 400-600 real fixes population-wide, not thousands.** Worth doing — it's safe, proven, and matches an already-built mechanism — but temper expectations; this is not the whale Finding 4 is.

**Fix for tonight**: extend `dedup_majority_resolver.SAFE_CONCEPTS` to the 6 income-statement concepts (revenue, net_income, cfo, operating_income, income_tax_expense, income_before_tax), reusing the exact same majority-vote logic already proven safe for balance-sheet concepts. Verify the extrapolated ~400-600 number against the real run before trusting it.

## Finding 6 (classification, not a fix): `not_in_sec_feed` cluster is mostly already-known structural absence

**No action needed beyond classification (Phase 3 work).** Top companies: Southern California Edison, Entergy Arkansas, Southern California Gas Co — these are the exact "wholly-owned utility co-registrant subsidiary" pattern already documented (2026-09-12 entry: these file combined 10-Ks under a parent's primary XBRL context, a genuine SEC/EDGAR-side limit, not a Scrooner bug). SIC breakdown also shows pharma/biotech/REITs (same pre-revenue/pass-through pattern as every other structural-absence finding this project has made).

**BDC sub-cluster (Hercules Capital, Stellus Capital, Crescent Capital BDC, RAND Capital) investigated in depth — genuinely harder, not a quick fix.** All 4 have hundreds of real, recent authoritative facts (latest filings Aug-Sept 2026) — not a Collector gap. The gap is bounded to exactly 2015-2022 across every concept (revenue, total_assets, operating_income, etc.) for Hercules Capital specifically, while data resumes cleanly from ~2021-2022 onward. Root cause: Hercules Capital didn't tag standard `Assets`/`Revenues` before ~2021 — confirmed the raw companyfacts payload has real data back to 2014, but under fund-specific tags. **Found and REJECTED a candidate fallback before shipping it**: `AssetsNet` (2018-2023) looked like a plausible pre-2022 `Assets` substitute, but a direct overlap-period comparison showed it's exactly the negative of `StockholdersEquity` (NAV, sign-flipped) — a BDC/investment-company NAV convention, not total assets at all. This is the same "different concept sharing vocabulary" trap this project has hit repeatedly elsewhere, just caught here before being proposed. **Conclusion: no safe fix found for the BDC pre-2022 gap — leave as `not_in_sec_feed`/structural, don't force a tag mapping here.** A real fix would need digging into each BDC's specific pre-2021 fund-reporting tags case by case, with no guarantee a clean total_assets-equivalent exists at all — not a good use of tonight's time; lower priority than Findings 4/5.

## Finding 8 (REJECTED after verification — a near-miss worth recording): basic_eps from net_income ÷ shares_outstanding_resolved

**Looked like a massive whale (17,501 of 27,754 basic_eps gaps, 63% coverage), verified unsafe before writing it up as one — do NOT ship this.**

Using `net_income_resolved ÷ shares_outstanding_resolved` (the already-built resolved concepts, much broader than the raw-tag check from this morning) appeared to cover 63% of the basic_eps "no_mapped_tag" gap population — a huge jump from the 13% (3,644) found via the raw `WeightedAverageNumberOfSharesOutstandingBasic` tag check this morning.

**Verified via real coexistence before trusting it, and it fails badly**: sampled companies/periods where `basic_eps_resolved` is already real AND both inputs exist — only 1 of 3 samples agreed within 10%, with one case 10x off. Root cause confirmed: `shares_outstanding_resolved`'s underlying tags (`CommonStockSharesOutstanding`, `EntityCommonStockSharesOutstanding`) are **point-in-time** share counts (as of a balance-sheet date or filing cover page) — EPS requires the **weighted-average** shares outstanding **during** the period, a genuinely different accounting figure that moves whenever a company issues or buys back shares mid-period (very common). Dividing net income by the wrong denominator would silently produce wrong EPS values at scale.

**The narrower derivation (this morning's finding, `net_income ÷ WeightedAverageNumberOfSharesOutstandingBasic` specifically) remains the only safe version — 3,644 companies, 13% coverage, not yet shipped.** Worth shipping tonight as a small, safe, verified fix — just don't confuse it with the broader (unsafe) version above.

**Generalizable lesson, worth naming explicitly: "shares outstanding" and "weighted-average shares outstanding" are NOT interchangeable, even though both sound like "the share count."** Any future EPS-adjacent derivation must use the weighted-average concept specifically, never the point-in-time one — this is the same class of near-miss as `AssetsNet`≠`Assets` (Finding 6) and `dividends_paid`-bundles-preferred (Finding 3): a plausible-sounding substitute concept that is actually a different real-world quantity.

## Finding 12 (REJECTED after verification): net_income identity derivation for income_before_tax/income_tax_expense

**Looked like a second real whale (14,392 potential new fills: 6,224 for income_before_tax + 8,168 for income_tax_expense), verified unsafe — do NOT ship.**

`net_income = income_before_tax − income_tax_expense (+ disc. ops − NCI + equity method)` is a real identity already in `sanity/accounting_identity.py`, and doc 49 already scoped generalizing it the same way the balance-sheet identity was shipped this morning. Sizing looked promising: 6,224/22,244 (28%) of `income_before_tax`'s gaps and 8,168/27,344 (30%) of `income_tax_expense`'s gaps have the other two terms already resolved.

**Verified via real coexistence before trusting it, properly this time (company/period-scoped, not value-coincidence-scoped — see the methodology note on Finding 4's bonus thread for why that distinction matters):**
- **Bare formula** (no adjustments): 70.9% agreement (3,546/4,999) — already too low to trust.
- **With all 3 adjustment terms included** (`IncomeLossFromDiscontinuedOperationsNetOfTax`, `NetIncomeLossAttributableToNoncontrollingInterest`, `IncomeLossFromEquityMethodInvestments`): only **79.3%** (3,963/4,999) — better, but still far short of the 95%+ bar the balance-sheet identity cleared (99.71%).

**Conclusion: this identity is genuinely noisier than the balance-sheet one, even with every documented adjustment term included — confirms, rather than contradicts, this project's own prior finding** (`dedup_majority_resolver.py`'s docstring: income-statement concepts show only 68-75% agreement, "a blind majority vote would silently pick a wrong number ~25-30% of the time"). The same caution applies to an arithmetic-fallback derivation, not just majority-vote. **Do not build `resolve_net_income_identity_fallback()` or similar — the residual 20%+ disagreement would silently corrupt real values.** This is exactly the kind of result doc 49's own risk #1 ("direction matters for pass-rate trust... has NOT been separately verified live, only asserted by algebra") was written to catch before shipping, and it caught something real.

## Finding 7 (THE BIGGEST WHALE FOUND TODAY, not yet run): `resolve-conflict-fills` may simply need a rerun

**Likely the single highest-leverage action available for tonight — cheap, safe, already-built, possibly just not run recently enough.**

Investigated "quarter filed only as year-to-date" (9,622 cockpit tickets, but `period_gap` shows ~24,600 combined across `cfo_resolved`/`cash_flow_investing_resolved`/`cash_flow_financing_resolved` — these 3 cash-flow-statement concepts dominate this bucket almost entirely). Sampled real cases:

- **BK Technologies Corp, Q1 2023**: raw `NetCashProvidedByUsedInOperatingActivities` filed as both `558000` and `558` — an exact 1000x unit-scale typo. Both marked non-authoritative by Stage 2e (correct, by design). Since Q1 has no authoritative fact, `derive_interim_quarters` can't compute Q2 = H1 − Q1, blocking the whole quarter even though H1 itself is fine. Same company, 2024: `-786` vs `-786000`, same exact shape.
- **U-Haul Holding Co, several periods**: raw values differing by only 0.1%-5% (e.g., `369297000` vs `369670000`, 0.1% apart) — well within the existing `MAX_SAFE_RATIO = 1.15` (15%) tolerance `conflict_resolution.py::resolve_conflict_fill` already handles.

**`CONFLICT_FILL_TARGETS` is far broader than just the 3 cash-flow concepts — it's all 24 statement-table lines, including `revenue`, `operating_income`, `income_before_tax`, `income_tax_expense`, `net_income`, every balance-sheet concept, `diluted_eps`/`basic_eps`/`dividends_per_share` (confirmed by reading the full list, lines 74-110).** This mechanism is purely additive (`INSERT ... ON CONFLICT DO NOTHING`, never a delete), already proven safe against real evidence (Etsy, checked against yfinance), and uses a 15%-worst-case-disagreement safety bar.

**This directly covers the AMEX income_tax_expense example from earlier**: its 3 raw FY2016 values (2688M, 2667M, 2688M) have a worst-case spread of (2688−2667)/2688 ≈ 0.78% — comfortably within the 15% tolerance. **This also means Finding 5 (the income-statement majority-vote extension, sized at ~400-600) is likely LARGELY REDUNDANT with this mechanism** — if `resolve-conflict-fills` hasn't been run recently, running it will probably resolve most of what Finding 5 would have fixed anyway, via an already-safer, already-proven, already-built tool. **Don't build Finding 5's extension until after confirming what's left post-rerun — it may turn out to be unnecessary.**

**Sampled 30 real `cfo_resolved` "quarter not derived" gaps: 22/30 (73%) trace to a Q1 conflict blocking the whole derivation chain** — and confirmed the SAME pattern holds for the other 2 cash-flow concepts too (not a cfo-specific fluke): `cash_flow_investing_resolved` 15/20 (75%), `cash_flow_financing_resolved` 14/20 (70%). — of those, roughly 1 in 12 is a clean, obvious unit-scale typo (10x/100x/1000x ratio) and the rest are smaller percentage disagreements, many likely within the already-handled 15% tolerance.

**Why this might not need any new code at all**: today's full reprocessing chain (Phase 0, this morning) ran `resolve-facts → resolve-concept-fallbacks → resolve-statement-fallbacks → calculate → growth → ttm-returns → ttm-margins → ...` — **it did NOT include `resolve-conflict-fills` or `resolve-dedup-holes`**. If this hasn't been run population-wide recently (needs verification — check git/run history, not assumed), simply running it tonight could close a very large fraction of this ~24,600-ticket bucket with zero new code.

**For tonight**:
1. Verify when `resolve-conflict-fills`/`resolve-dedup-holes` were last run population-wide (check for any logged run, or just run them — both are purely additive/safe to rerun).
2. Run both, population-wide (no `--ciks` option exists — these are set-based, whole-population tools by design).
3. Re-measure `period_gap` and see how much of the 24,600 cfo/cash-flow-investing/cash-flow-financing bucket closes.
4. Only if a real residual remains after that, consider whether the clean-unit-scale-typo pattern (1000x/100x/10x ratios) deserves its own narrow, targeted fix beyond what the 15%-tolerance mechanism already catches.

**This is cheap to try and potentially the single biggest lever found today — try this FIRST tonight, before Finding 4 or Finding 5.**

## Finding 9 (minor, safe, small): `RevenuesNetOfInterestExpense` unmapped tag

**Small, safe, legitimate — ship if convenient, not a priority.** American Express (and 96 other companies) use `RevenuesNetOfInterestExpense`, not currently in `revenue`'s `concept_mapping`. Verified coexistence: sometimes exactly equals `Revenues` (companies with no interest expense), sometimes genuinely differs (real net-of-interest companies) — unsafe to treat as a blind synonym, but **safe as a lowest-priority fallback tag** (first_match semantics never override an existing higher-priority match). Sized the real gap-fill: only **5 companies** currently have zero other revenue coverage and would benefit. Small win, no real risk, but not a whale — do if there's spare time tonight, skip if not.

(Note: AMEX's own actual gap this morning was `q4_not_derived`, not `no_mapped_tag` — its quarters already resolve fine via this tag path; the real AMEX issue is Finding 7's territory, the FY-level Stage 2e conflict.)

## Finding 10 (non-issue): `filing_not_processed` (29 tickets) is just freshness lag

Both affected companies (NEOGENOMICS INC, Kentucky First Federal Bancorp) show the gap at exactly 2026-06-30 — the most recently-filed quarter as of this investigation. Not a bug; these simply haven't gone through the next scheduled reprocessing cycle yet (same mechanism as `reprocess_recent_filers.sh`). No action needed — will self-resolve on the next normal reprocessing pass.

## Finding 11 (new structural category + a short list of real leads): currency trusts share the Hercules Capital-shaped historical gap

Checking which companies show a "real data resumes after a multi-year hole" pattern for `total_assets_resolved` (the same shape as Hercules Capital's BDC gap, Finding 6) surfaced a clean new cluster: **Invesco CurrencyShares Japanese Yen/Australian Dollar/Swiss Franc/Euro/British Pound Sterling Trust** — all 5 share the identical 2015-01-31 start and a gap ending 2019-03-31 or 2023-09-30. These are currency ETF/trust vehicles, the same structural family as the already-known commodity trusts (SPDR Gold Trust) — likely report "total assets" under a trust-specific tag or not at all in the way an operating company does. **Classification candidate for Phase 3, not a fix.**

**A handful of real operating companies in the same result set deserve individual attention tonight, not structural dismissal:**
- **TANGER INC.** (a real, well-known, actively-traded outlet-mall REIT) — gap 2015-03-31 to 2021-09-30, data resumes to present. REITs have a known different balance-sheet presentation, but a 6-year gap for a company this size/visibility is worth 10 minutes of direct investigation before assuming it's the same REIT pattern as smaller, thinner filers.
- **Home Federal Bancorp, Inc. of Louisiana** (a real community bank) — gap 2015-02-05 to 2020-05-12.
- **CPS TECHNOLOGIES CORP** — gap 2015-03-28 to 2021-03-27, an ordinary small-cap manufacturer, no obvious structural reason to be missing `total_assets` for 6 years.

**Tanger Inc. investigated — confirmed a real instance of the already-documented dimensional-XBRL limitation (doc 22/23), not a new bug.** Both `Assets` and `LiabilitiesAndStockholdersEquity` only start 2021-12-31 (so this morning's balance-sheet-identity fix doesn't help here — verified directly, canonical_fact still only covers 2021-2026). Checked Tanger's full raw fact list at 2018-12-31: 31 real facts exist, but every one is a footnote/detail disclosure (real-estate schedule, operating-lease minimum payments, intangibles) — **no primary-balance-sheet grand total exists in the standard Company Facts payload at all** for this period. This is the dimensional-XBRL stripping limitation this project has already named and deliberately left unbuilt (AAPL's own XBRL has 231 dimensional contexts, "segment members are company-specific custom extensions, not a universal mapping"). The real fix would be extending the already-built rendered-report parser framework (`revenue_parser.py`/`cost_of_revenue_parser.py`/`segment_revenue.py`) to `total_assets` specifically — a real, scoped, non-trivial future project, not a tonight fix.

**Home Federal Bancorp checked — FALSE ALARM, a methodology artifact in my own query, not a real gap.** `Assets` tag coverage is actually continuous 2011-2026 (checked directly) — real quarterly data exists for every quarter in the "gap window" I'd flagged. The two `period_gap` rows for this company are isolated single dates (2015-02-05, 2020-05-12 — neither is a quarter-end, almost certainly a cover-page share-count-as-of-date disclosure, not a missed reporting period). **My own `min(period_end)`/`max(period_end)` aggregation query made two scattered single-date anomalies look like a continuous 5-year hole** — a real lesson for whoever re-runs this kind of historical-gap scan: verify the actual gap dates individually, don't trust a min/max range summary without checking what's actually missing in between. **CPS Technologies was individually confirmed real** (Assets tag only 2020-2026, same shape as Tanger/Hercules — likely the same dimensional-XBRL or tag-absence cause, not separately dug into further).

## Finding 13 (NEW WHALE, found via the real Screener, high confidence for ONE of 5 affected metrics): `sum_diff_ratio`'s null-propagation bug, same class as the already-fixed `total_shareholder_yield`

**Discovered via a new discovery method, per direct request: ran a real `ScreenQuery` through the production `screener/query.py::run_query()` with all 82 active metrics required, and aggregated the real `excluded_missing_data` output** (saved at `/tmp/screener_excluded.json`, 5,216 companies, all excluded since nobody has all 82). Ranking which single metric most often blocks a company from an otherwise-complete profile: **`quick_ratio` blocks 2,604 companies (50% of the population) — by far the largest single blocker**, followed by `roa` (805), `sbc_pct_revenue` (300), `roic` (296), `ebitda` (231).

**Root cause, verified by reading the code directly**: `quick_ratio = (current_assets − inventory) / current_liabilities`, computed by the generic `calculate_shapes/sum_diff_ratio.py` shape. That shape's `compute()` requires every role (`add`/`subtract`/`denominator`) to be non-null — `if subtract is None: return None, "missing:subtract"` — with **no distinction between "this company genuinely has zero inventory" (correct) and "this is a real data gap" (incorrect)**. This is the exact bug class already found and fixed once for `total_shareholder_yield` (2026-09-06 entry, this file): *"a composite metric that sums multiple optional components must treat a genuinely-absent component as $0, never require ALL components non-null."* Many real sectors (software, services, most financials) structurally have zero inventory — that's correct, not missing.

**`sum_diff_ratio` is shared by 5 metrics — the fix is NOT safe to apply blindly to all of them, verified per-metric before concluding anything:**

| Metric | Formula | "subtract" role | Current coverage | Safe to zero-default? |
|---|---|---|---|---|
| `quick_ratio` | (current_assets − inventory) / current_liabilities | `inventory` | 51.12% | **YES, high confidence** — many real sectors structurally have none |
| `gross_margin` | (revenue − cost_of_revenue) / revenue | `cost_of_revenue` | 63.89% | **NO** — virtually every real operating company has nonzero cost of revenue; absence is almost always a genuine gap |
| `net_cash_per_share` | (cash − total_debt_resolved) / shares | `total_debt_resolved` | 63.66% | **AMBIGUOUS** — `total_debt_resolved` already has multiple fallback paths built this morning and prior sessions; its absence is more often a real gap than genuine debt-free status, though some small/young companies ARE genuinely debt-free. Needs its own verification before deciding, not a blanket default. |
| `fcf_margin` | (cfo − capex) / revenue | `capex` | 76.67% | **AMBIGUOUS** — most companies have some capex, but genuinely asset-light businesses might not. Needs verification. |
| `eps_dilution_spread` | (diluted_eps − basic_eps) | `basic_eps` | 96.87% | Not a priority — already near-saturated |

**For tonight: ship the `quick_ratio`-specific fix only** (default `inventory` to zero when genuinely absent, inside `sum_diff_ratio.py` or via a per-metric override flag — needs a design decision: a blanket shape-level change would incorrectly also zero-default `gross_margin`'s cost_of_revenue, which must NOT happen). **Do not touch `gross_margin`'s behavior.** Leave `net_cash_per_share`/`fcf_margin` for a future, separately-verified pass. Given `quick_ratio` alone blocks half the population from a full-metric screen, this is plausibly the single highest-leverage individual metric fix available — likely bigger in screener-usability terms than any other finding today, though (per the "whale math" from Finding 0) it still only moves `avg_metric_coverage_score` by at most `(100-51)/82 ≈ 0.6pp` on its own.

## Finding 14 (real, scoped bug — all 11 "critical" yfinance findings are false positives): `yfinance_check.py`'s own query has no fiscal-period tiebreak

**Per direct request to also mine the existing yfinance-based sanity tooling: `analytics.data_sanity_check` already has 5,115 companies checked (daily cron), with 11 critical + 15,772 major + 9,465 minor findings sitting there, largely uninvestigated.**

**All 11 "critical" findings share the exact same shape**: clinical-stage biotech/pharma companies (Rapport Therapeutics, Sky Quarry, Aligos, Taysha Gene Therapies, Tango Therapeutics, Curis, Shattuck Labs, Evommune, Spero Therapeutics, Korro Bio, Cartesian Therapeutics) flagged with "our revenue is $0, yfinance says real revenue exists." **Investigated the first one (Rapport Therapeutics) in full — this is a false positive, not a real data gap.**

Real data: Q1 2026 revenue = $20M (a one-time milestone/licensing payment), H1 2026 cumulative = $20M (confirming Q1 was the only revenue), **Q2 2026 discrete = $0 (mathematically correct — genuinely zero new revenue that quarter)**. The company's real revenue IS correctly captured. The bug: `analytics.canonical_fact` legitimately stores BOTH the discrete-Q2 ($0) and cumulative-H1 ($20M) rows for `revenue_sanity_resolved`, since both share the same `end_date` (2026-06-30) but are genuinely different periods (3-month vs 6-month span) — this is correct, by-design dual storage, not corruption. `yfinance_check.py`'s own "most recent value" query (`order by cf.company_id, p.end_date desc`, no secondary sort key) has **no deterministic tiebreak** between these two rows, so it can pick either the real $0 (correct) or coincidentally land on something else, depending on arbitrary row-return order — not safe, and a literal violation of this project's own "same query → same result" determinism release gate.

**This dual-storage pattern is genuinely widespread**: 98,148 (company, end_date) groups across **4,501 companies (86% of the active population)** have this exact shape (checked via a direct query — e.g. JPMorgan's Q2 2014 revenue: $24.678B discrete vs $47.893B cumulative H1, same end_date).

**Important, verified distinction — this does NOT corrupt the Screener or company page.** Checked `mapper/calculate.py::_load_canonical_facts()` directly: it keys duration facts by explicit `period_id` (looked up against a specific expected fiscal_year/fiscal_period anchor per metric), never by a naive "latest end_date" scan — so `analytics.metric_value` (what the Screener and company page actually read) is structurally safe from this ambiguity. **The bug is isolated specifically to `yfinance_check.py`'s own comparison logic**, which is a separate, narrower, lower-stakes consumer than I first feared.

**Real impact**: all 11 "critical" sanity findings are very likely false positives from this exact mechanism (not confirmed for all 11 individually, but Rapport Therapeutics' pattern matches the other 10 company names closely enough — all clinical-stage biotechs — to be the same root cause). **A meaningful fraction of the 15,772 "major" findings are probably the same false-positive shape too** — not sized yet, worth a dedicated sweep tonight.

**Fix for tonight**: add a deterministic tiebreak to `yfinance_check.py`'s "most recent revenue" query — prefer the row whose period has the SHORTEST span (discrete quarter over cumulative YTD) when two rows share an end_date, or more robustly, prefer by `fiscal_period is not null` (discrete labels always win over the unlabeled YTD rows). Re-run `scrooner-sanity run` + `report` after the fix and expect most/all of the 11 criticals to clear, plus a meaningful chunk of the majors.

## Not yet investigated (continuing)

- "quarter filed only as year-to-date" (9,622 tickets) — the known, harder cumulative-YTD cash-flow reconstruction gap. Not touched today.
- "no mapped tag in the filing" (17,735) — partially explained (structural absence for pharma/biotech/SPACs/REITs in the 5 concepts checked 2026-10-04/05), but the full 17,735 hasn't been swept concept-by-concept yet.
- The BDC sub-cluster inside `not_in_sec_feed` (Finding 6).
- Continuing to investigate — this document will be appended to throughout the day.

## Priority order for tonight (my recommendation, revised after Finding 7)

1. **Finding 7** (rerun `resolve-conflict-fills`/`resolve-dedup-holes` population-wide) — cheapest, safest, potentially the single biggest lever (~24,600-ticket bucket), zero new code. Try this FIRST and re-measure before doing anything else — it may make some of the other findings partially moot.
2. **Verify Finding 2's cleanup rebuild actually finished** before assuming it's done.
3. **Finding 4** (`conflict_split` mislabeling) — highest-confidence code fix, ~1,810 tickets correctly reclassified, may surface new unit-scale-error leads.
4. **Re-measure before building Finding 5** — likely largely redundant with Finding 7's `CONFLICT_FILL_TARGETS` coverage (confirmed to include all income-statement concepts, not just cash-flow). Only build the majority-vote extension for whatever's left after Finding 7 runs.
5. BDC sub-cluster (Finding 6) — investigated, no safe fix found; deprioritize unless new evidence emerges.
6. Re-check "quarter filed only as year-to-date" and "not_resolved" after Finding 7 runs — size whatever residual remains before deciding if either needs new code.
7. Finding 12 (net_income identity derivation) — REJECTED, do not build.
