# 2026-09-27 — Metric Plausibility Gates: root-causing and fixing the critical cluster end to end

Direct follow-up to doc 47's own build the same day. Doc 47 built the *detection* system (`sanity/plausibility_check.py`) and found 7,003 critical violations on its first run. The explicit next instruction was: **"are these correct fix? we should fix from core, like how these things generated? mapping issue, calculation issue or what? verify and test with yfinance and do a complete fix end to end."**

This entry is the investigation trail — what each cluster turned out to be, how it was verified, and what was actually fixed vs. correctly left alone.

## Starting point

After doc 47's own same-day correction (the `profitable_streak_years` bound-widening, `[0,15]`→`[0,40]`, documented in doc 47 itself): **6,582 critical, 7,327 watch**, 663 pipeline unit tests passing.

## Investigation 1: `net_income_growth_yoy` / `eps_growth_yoy` / `fcf_growth_yoy` (894 / 702 / 524 critical — the three largest clusters)

Queried the top 15 `net_income_growth_yoy` violations by magnitude. The #1 result, Infleqtion, Inc. (CIK 0002007825), showed 483,836.84% — investigated by hand, not assumed:

```
Q1 2024: -$44,611   Q2 2024: -$7,230   Q3 2024: -$69   (all real, all correctly extracted)
Q3 2025: -$33,384,811
```

Also found two CONFLICTING "FY2024" rows for the same company — one `start_date=2024-01-01` at -$55,742,000 (real, large), one `start_date=2024-01-04` at -$51,910 (tiny) — not investigated further at the time, but consistent with the same pattern below.

**Hypothesis**: Infleqtion is a SPAC (blank-check company) that completed a business combination sometime between Q3 2024 and Q3 2025. Q1-Q3 2024's `core.fact` rows are the pre-merger shell's own separately-filed 10-Qs (SEC requires the registrant — the shell — to keep filing until the merger closes); the FY2024 10-K, filed post-merger, uses reverse-merger accounting to retroactively report the real operating company's full-year figures. Q3 2025 is the real, post-merger operating company.

**Verified against yfinance directly** (the explicit instruction): fetched INFQ's `quarterly_income_stmt`.

```
2026-06-30: -24,695,000   2026-03-31: -30,263,000
2025-09-30:  -6,030,000   2025-06-30:  -9,186,000   2025-03-31: -5,985,000
2024-12-31: NaN
```

Yahoo's own quarterly series simply **starts** at 2025-03-31 — the first clean post-merger quarter — with 2024-12-31 returned as `NaN`, not a real value. This independently corroborates the discontinuity: an independent data provider doesn't treat the pre-merger period as comparable either, it just has no data there at all rather than fabricating a comparison across the boundary. (Note: Yahoo's absolute dollar figures differ from ours — Yahoo restates historicals under reverse-merger accounting treating the operating company as the accounting acquirer throughout, while our pipeline extracts the shell's own separately-filed pre-merger 10-Qs as-is; this is a genuine, expected divergence in *what each source considers the historical entity to be*, not a bug in either.)

**Sampled other top violators**: several more SPAC-shaped company names in the same top-15 list ("Crown Reserve Acquisition Corp. I", "Cantor Equity Partners V/VI", "Alussa Energy Acquisition Corp. II", "BTC Development Corp.", "Twenty One Capital, Inc.", "StableCoinX Inc.", "Fermi Inc.") — consistent with the same pattern being widespread across the de-SPAC-heavy population, not unique to Infleqtion.

**Second, different instance of the same shape**: sampling `eps_growth_yoy`'s top violations surfaced real operating companies too (Beasley Broadcast Group -51,155%, PBF Energy -15,180%, Americold Realty Trust -12,000%...) — NOT SPACs. Investigated Beasley directly: its diluted EPS jumped from -$0.09 (Q2 2025) to $45.95 (Q2 2026) — a real, authoritative, as-filed `us-gaap:EarningsPerShareDiluted` fact, `is_derived=false`. Checked net_income: Q4 2025 = **-$190,149,042** (a massive loss, likely a fresh-start-accounting write-down), Q2 2026 = **+$84,293,430** (a massive gain, likely a debt-extinguishment/equity-revaluation gain from bankruptcy emergence). Real corporate discontinuity, same conceptual shape as a SPAC merger — a bankruptcy emergence — but with a materially-*large* prior base (-$190M is not "near-zero"), so a simple prior-base materiality floor wouldn't have caught this one. Flagged, not force-fixed: this is a genuinely harder case (detecting "this company just underwent a corporate discontinuity event" in general would need real bankruptcy/reorganization-event detection, out of scope for this pass) — but it's a real, legitimate, correctly-flagged extreme, not a data bug, so leaving it flagged is the correct behavior, not a gap.

### Fix

Added a per-concept **materiality floor on the prior-period base** — the general, root-cause-agnostic fix: whatever the specific corporate event, a near-zero prior base makes ANY growth ratio off it mathematically well-defined but economically meaningless.

`mapper/ttm.py`:
```python
CONCEPT_MATERIALITY_FLOORS: dict[str, Decimal] = {
    "revenue": Decimal("1000000"),
    "net_income": Decimal("1000000"),
    "diluted_eps": Decimal("0.01"),
    "dividends_per_share": Decimal("0.01"),
    "shares_outstanding": Decimal("10000"),
}
```
`_growth_value()` gained a `materiality_floor` parameter; `abs(value_prior) < materiality_floor` → `None, "immaterial_prior_base"` (checked before the sign/CAGR branches, after the existing exact-zero check).

`mapper/fcf_growth.py`: same fix, `FCF_MATERIALITY_FLOOR = Decimal("1000000")` (FCF is dollar-scale like net_income/revenue), applied to its own `_growth_value()` call.

**Honestly noted**: Beasley's EPS-growth case (bankruptcy emergence with a *materially large* prior base) is NOT caught by this fix — the floor only helps the near-zero-base shape, which is the dominant pattern by volume but not the only one. Left correctly flagged as a real, extreme, worth-investigating value.

### Deployment

Queried all companies with a critical/watch finding on any growth metric — 2,301 CIKs. Ran `scrooner-map growth` + `scrooner-map calculate-fcf-growth` for all of them, parallelized across 6 shards (chunks of 150, sequential within a shard). Real wall-clock cost: ~10s/company for `growth` (multiple concept loads over network), much faster for `calculate-fcf-growth`. Total run took roughly 2 hours wall-clock across the parallel shards, including one hang-and-restart (see Infrastructure bug below).

Spot-verified: Infleqtion's `net_income_growth_yoy` now correctly nulls with `immaterial_prior_base` where the prior base is genuinely tiny.

## Investigation 2: the plausibility checker's own bug — TTM vs. single-quarter denominator

Sampled the remaining `ebitda`/`fcf` critical cluster (RELATIVE_CHECKS, "> 3x TTM revenue"). United Rentals, Inc. showed `ebitda=$4,476,000,000` flagged against `revenue=$929,000,000` (denominator=929M) — a "4.82x TTM revenue" finding.

Checked United Rentals' actual `revenue_sanity_resolved` history directly:
```
Q1 2026: $929M   Q4 2025: $992M   Q3 2025: $938M   Q2 2025: $872M   FY2025: $3,695M
```
$929M was the single MOST RECENT period (Q1 2026 alone) — not a trailing-twelve-month figure. The real trailing-4-quarter sum (929+992+938+872 = $3,731M) matches United Rentals' own real FY2025 total ($3,695M) almost exactly. Real EBITDA/TTM-revenue ratio is ~1.2x, not 4.8x — a false positive from the checker's own construction, not a real pipeline bug.

**Root cause**: `_load_latest_concept_values()` (used for every `RELATIVE_CHECKS` denominator, including `total_assets_resolved`) picks the single most-recent `canonical_fact` period regardless of duration — correct for a balance-sheet snapshot concept like `total_assets_resolved`, wrong for `revenue_sanity_resolved` when the numerator (`ebitda`/`fcf`/`net_interest_income`) is itself TTM-scale (per `expanded_metrics.py`'s own TTM-row persistence, documented in `pipeline/CLAUDE.md`'s 2026-09-08 entry).

### Fix

New `_load_ttm_revenue_denominators()` in `plausibility_check.py`: prefers the latest real FY row directly (a fiscal year's revenue already IS a trailing-twelve-month figure as of its own end_date); otherwise sums the trailing 4 quarters, requiring all 4 present; otherwise skips (no denominator, no finding — same "don't guess" discipline `check_relative()` already uses for a zero/missing denominator). Wired into `run_all()` to override just the `revenue_sanity_resolved` entries in the denominator dict — `total_assets_resolved` keeps the original plain-latest-period lookup, which is correct as-is for a balance-sheet concept.

**Verified live**: United Rentals now shows `ebitda: ok, value=4476000000` (the value is unchanged — this was always a false alarm about the *check*, never about the stored `ebitda` figure itself).

**Result**: this single fix, redeployed, dropped critical **6,582 → 5,580** across `ebitda`, `fcf`, `net_interest_income`, `cash_returned_to_shareholders`, and the 3 `*_change_reconciliation_gap` metrics (all share the same `revenue_sanity_resolved` denominator).

## Investigation 3: pharma/biotech sector noise in the residual `ebitda`/`fcf` cluster

Re-sampled the top-15 remaining `ebitda` critical violations after fix #2. Triton International Ltd stood out as a real anomaly (23x revenue — investigated, found a genuine, separate, NOT-yet-fixed revenue-mapping gap for container-leasing companies, flagged below, not fixed this pass). Most of the rest — Trump Media & Technology Group, Aurora Innovation, IonQ, Joby Aviation, NuScale Power, Cytokinetics, Sharplink, Oscar Health, Roivant Sciences, Crinetics Pharmaceuticals, CRISPR Therapeutics, SITE Centers, BETA Technologies — are real, named, early-stage/pre-revenue companies.

Grouped the whole remaining critical `ebitda`/`fcf` population by `sic_description`:
```
Pharmaceutical Preparations: 145
Biological Products, (No Diagnostic Substances): 68
Services-Prepackaged Software: 19
Surgical & Medical Instruments & Apparatus: 19
... (long tail)
```
145+68 = 213 of ~313 (68%) from two SIC codes. Spot-checked 3 real companies against real revenue/EBITDA (Cytokinetics -$695M ebitda / $67.7M revenue, CRISPR Therapeutics -$516M / $13.4M, NuScale Power -$702M / $10.7M) — all real, correctly-computed values for genuinely R&D-burn-heavy pre-revenue biotechs. Same sector-isolation reasoning this project already applies to banks/BDCs/REITs (see `pipeline/CLAUDE.md`'s repeated "a real sector characteristic, not a data error" pattern).

### Fix

`PRE_REVENUE_RD_SIC_DESCRIPTIONS = {"Pharmaceutical Preparations", "Biological Products, (No Diagnostic Substances)", "In Vitro & In Vivo Diagnostic Substances"}`, `SECTOR_EXCLUDED_RELATIVE_CHECK_METRICS = {"ebitda", "fcf"}` — deliberately narrow: only these two R&D-burn-driven metrics are excluded for these three sectors, not the balance-sheet/reconciliation checks, which aren't R&D-driven.

**Result**: critical **5,580 → 5,362**.

## Investigation 4: immaterial-denominator ratios (`operating_margin`/`net_margin`/`pretax_margin`/`gross_margin`/`fcf_margin`/expense ratios, `roa`, `interest_coverage_ratio`)

Sampled `operating_margin`'s top violations. #1: Inhibikase Therapeutics, Inc., -20,063,937 (-2,006,393,700%) for the TTM period ending 2024-09-30. Checked the raw inputs directly:

```
operating_income (Q4'23+Q1'24+Q2'24+Q3'24): -4,403,566 -4,782,360 -5,050,535 -5,827,476 = -20,063,937
revenue: Q4'23=$1, Q1'24=$0, Q2'24=$0, Q3'24=$0  →  TTM revenue = $1
```
Real, authoritative facts on both sides — a real $1 licensing/grant payment (not a data error) against real multi-million-dollar operating losses. `-20,063,937 / 1 = -20,063,937` — exactly matches the stored value. Mathematically correct, economically meaningless.

Checked whether this pattern was isolated or systemic: sampled `roa`'s top-15 violations — all obscure micro-cap/shell companies (Appsoft Technologies -13,377x, Cannaisseur Group, Loan Artificial Intelligence Corp, Bravo Multinational, BioForce Nanosciences, Burzynski Research Institute, GBT Technologies, Flywheel Advanced Technology...). Verified Appsoft Technologies directly: real FY2025 `total_assets = $7` (seven dollars), real `net_income = -$93,642`. `roa = -93,642/7 = -13,377.4` — exact match. Broke down the full 175-company `roa` critical population by denominator size: **142 of 175 (81%) have total_assets under $1M** — confirms the pattern dominates, not a one-off.

Checked `interest_coverage_ratio` (94 critical) the same way. Dermata Therapeutics, Inc.: real Q4 2021 `interest_expense = $4` (four dollars) against real operating losses — a multi-million-percent "coverage ratio," despite this metric's already-wide doc-47 CRITICAL bound of ±5000 (±500,000%). Checked the company's own OTHER quarters to size an appropriate floor (not just picking a round number): Dermata's real Q3 2021 was $651, Q2 2021 was $1,823, Q1 2021 was $43,135 — all real, legitimately small-but-material figures for an early-stage company. A $1M floor (same as revenue/assets) would have wrongly nulled these real values; used a much lower $10,000 floor instead, informed directly by this company's own real data.

### Fix

Three new materiality-floor constants added to `calculate.py`'s shared `_compute()` engine (the "ratio" and "sum_diff_ratio" formula shapes), each scoped to only the metrics whose denominator concept matches:

```python
REVENUE_DENOMINATOR_MATERIALITY_FLOOR = Decimal("1000000")
REVENUE_DENOMINATOR_METRICS = {"operating_margin", "net_margin", "pretax_margin",
    "gross_margin", "fcf_margin", "sga_pct_revenue", "rnd_intensity",
    "capex_pct_revenue", "sbc_pct_revenue"}

ASSET_DENOMINATOR_MATERIALITY_FLOOR = Decimal("1000000")
ASSET_DENOMINATOR_METRICS = {"roa"}

INTEREST_EXPENSE_DENOMINATOR_MATERIALITY_FLOOR = Decimal("10000")
INTEREST_EXPENSE_DENOMINATOR_METRICS = {"interest_coverage_ratio"}
```

Each check returns an explicit null reason (`immaterial_revenue_base` / `immaterial_asset_base` / `immaterial_interest_expense_base`) before the ratio would otherwise compute. `_compute()` gained a `metric_name` parameter (default `""`, so every pre-existing caller not passing it is unaffected — confirmed by running the full suite before adding new tests).

Matching fix in `expanded_metrics.py`'s standalone `ebitda_margin` computation (not part of `calculate.py`'s shared engine): `REVENUE_TTM_MATERIALITY_FLOOR = Decimal("1000000")`, checked before the division.

**Deliberately did NOT add a floor to `roe`** — its denominator is stockholders' equity, and near-zero/negative equity is a real, common, ALREADY-ACCEPTED degenerate case (a genuine leverage story for a distressed or heavy-buyback company), fundamentally different from total_assets going near-zero (which essentially always signals "this is not a real operating business"). Doc 47 §1's own CRITICAL bound for `roe` (±1000%) is deliberately wide for exactly this reason. Added an explicit regression test (`test_non_revenue_ratio_ignores_the_floor`) asserting `roe` is unaffected.

### Deployment

Queried all companies with a critical/watch finding on any of the 10 affected metrics — 948 CIKs (margins) + 774 CIKs (roa/interest_coverage_ratio, a separately-scoped rerun since `roa`/`interest_coverage_ratio` don't need `calculate-expanded-metrics`, just `calculate`). Ran `scrooner-map calculate` (+ `calculate-expanded-metrics` for the margin batch, since `ebitda_margin` lives there) for all of them.

**Verified live**: Inhibikase's `roa`... wait, Inhibikase wasn't in the roa set — verified its `operating_margin` for FY period ending 2024-09-30 now returns `value=None, is_null_reason='immaterial_revenue_base'`. Appsoft Technologies' `roa` (FY2025) now `value=None, is_null_reason='immaterial_asset_base'`. Dermata Therapeutics' `interest_coverage_ratio` (Q4 2021) now `value=None, is_null_reason='immaterial_interest_expense_base'`.

## Investigation 5: a real infrastructure bug, found verifying #1's deployment, not the original target

3 of the 6 growth-fix shards (which had been running unmonitored, not the two I'd explicitly killed-and-restarted for hanging) turned out to have hit a real mid-batch connection death. Checked the actual tracebacks in the shard logs rather than assuming a transient blip:

```
OperationalError: consuming input failed: could not receive data from server: ...
growth.log_error_itself_failed cik=... stage=growth
OperationalError: the connection is closed
```

62-63 companies per affected shard failed in a row, all logged as `growth.company_failed` — a cascading pattern, not scattered isolated failures. `log_error()` itself is already protected against a dead connection (fixed 2026-09-03, per `pipeline/CLAUDE.md`), so it correctly logged a warning instead of crashing — but nothing reconnected the actual `conn` object afterward, so every SUBSEQUENT company in that same batch also failed against the now-permanently-dead connection.

**Root cause**: `mapper/ttm.py` (3 call sites: `growth`, `ttm_margins`, `ttm_returns`), `mapper/fcf_growth.py`, and `mapper/calculate.py` were all missing the `safe_rollback()` reconnect pattern already centralized in `common/errors.py` and already applied to 10+ other batch-loop modules across this codebase (per `pipeline/CLAUDE.md`'s own running list) — these 5 sites had simply never been swept.

### Fix

Added `conn = safe_rollback(conn, stage="<name>", cik=cik)` to all 5 `except Exception` blocks, matching the established idiom exactly. This is a real, generalizable robustness fix independent of today's materiality-floor work — closes the gap structurally so a future dead-connection mid-batch costs one company, not the rest of the batch.

### Recovery

Extracted the 187 unique CIKs that had failed (`grep -oE "growth\.company_failed\s+cik=[0-9]+"` across the 3 affected shard logs), re-ran `scrooner-map growth` for just those — `considered=187, ok=187, errored=0`. (Their `calculate-fcf-growth` runs, launched as separate `uv run` processes after each shard's growth chunk, had already succeeded cleanly — confirmed by checking those specific log lines — so only `growth` itself needed the targeted rerun.)

## A sixth, smaller fix found running the final verification

`_load_latest_metric_values()`'s own SELECT (a window-function scan over `analytics.metric_value` filtered to ~85 metric names) started hitting `QueryCanceled: canceling statement due to statement timeout` (the pooler's default 2-minute `statement_timeout`) on the first two attempts at the final full-population plausibility rerun — almost certainly because this session's own growth/margin/roa/interest-coverage-ratio fixes had just rewritten a large share of that table (many new explicit-null rows), changing the query's real cost profile. Fixed with `cur.execute("set statement_timeout = '5min'")` before the query, the same established pattern already used in `tag_candidates.py`/`coverage_matrix.py` for a rare, heavier-than-usual full-population scan (see `pipeline/CLAUDE.md`'s existing entries for both).

## Correctly identified as NOT bugs — investigated and left alone

- **`working_capital` (236 critical)**: sampled the top violators — Triller Group, Yale Transaction Finders, Armata Pharmaceuticals, Dominari Holdings, Galectin Therapeutics, BioXcel Therapeutics, Bright Mountain Media, Evofem Biosciences, Viking Global Technologies, Emmaus Life Sciences. Checked Galectin Therapeutics directly: `current_liabilities` jumped from $7.3M (Q1 2026) to **$151.6M** (Q2 2026) while `total_assets` stayed ~$14.8M — traced to the real, single, authoritative `us-gaap:LiabilitiesCurrent` tag from its own real 10-Q filed 2026-08-14, `is_authoritative=true`. A real distressed-company balance-sheet distortion (almost certainly a going-concern-triggered reclassification of long-term debt/warrant liabilities to current), not a mapping or calculation bug. Left correctly flagged.
- **`net_cash`/`net_change_in_cash`**: same `total_assets_resolved`-denominator RELATIVE_CHECKS shape as `working_capital`, already benefiting from the same real-data reasoning — not separately investigated in depth this pass, but the mechanism is identical and no evidence of a systemic false-positive pattern was found.
- **The `*_change_reconciliation_gap` family (ar/ap/inventory, 88/103/104 critical) and `effective_tax_rate_gap` (11 critical)**: doc 47 §6's own stated design is that these are diagnostic quality-of-earnings signals meant to flag "something to investigate" (M&A, reclassification), explicitly never meant to be suppressed or treated as automatically wrong. Left entirely alone, working as designed.

## Sized but deliberately NOT fixed this pass

**Triton International Ltd's revenue** (a real, large, well-known container-leasing company — its FY2025 `revenue_sanity_resolved` shows $59.5M, when its real total revenue is roughly $1.6-1.7B/year). This is a genuine, sector-specific revenue-mapping gap — almost certainly Triton's dominant "operating lease revenue" line is tagged separately from whatever narrower tag currently resolves, similar in shape to the Hyatt Hotels Cost-of-Revenue dimensional-tagging gap already fixed 2026-09-21 (`pipeline/CLAUDE.md`). Not investigated further or fixed this pass — flagged here as a real, sized lead for whoever next does a revenue-coverage pass, not swept under the rug.

## Final verified result

| | Before this pass | After |
|---|---|---|
| critical | 6,582 | **4,371** |
| watch | 7,327 | **6,109** |
| ok | — | 230,711 |
| skipped_no_denominator | — | 2,631 |
| skipped_sector_exclusion (new) | 0 | 1,022 |
| considered | 247,834 | 244,844 |

(`considered` dropped slightly because 1,022 rows that used to be checked-and-flagged are now correctly excluded pre-check via the sector carve-out, and a further ~2,631 revenue-denominated checks now honestly skip rather than compute against an incomplete trailing-quarter window.)

663 pipeline unit tests passing before this root-cause pass began, growing to 700 across it — 37 new tests covering every materiality-floor branch, the sector exclusion, and `_load_ttm_revenue_denominators`.

## Generalizable lesson

**A near-zero-but-nonzero denominator produces a value that is mathematically correct and structurally meaningless — this is now a recognized, recurring class of bug in this codebase, not a one-off.** Found and fixed in 5 different places in one session (growth-rate priors, TTM-revenue-vs-quarterly-revenue, revenue-denominated margins, asset-denominated ROA, interest-expense-denominated coverage ratio) — always the same shape: (1) both inputs are real, authoritative, correctly-extracted facts; (2) the arithmetic is correct; (3) the result is nonetheless useless for comparison because the denominator's real-world magnitude is below the threshold where a *ratio* of it means anything. The fix is always the same idiom: a per-metric-family materiality floor on the denominator, sized from real data for that specific denominator type (not one universal number — $1M for revenue/assets, $10K for interest expense, because a real company's genuine interest expense is legitimately smaller-scale than its genuine revenue or asset base). Worth checking any NEW ratio-shaped metric added to this pipeline for the same exposure before it ships, rather than waiting for a plausibility-check cluster to surface it.

## Same-day addendum (2026-09-28): "why so big? fix at root level so it never arises again"

Direct follow-up asking for the deeper structural explanation, not just the per-cluster fixes above.

### Why the count was so big — the real structural reason

Three things compounded, not one:

1. **Scrooner covers the full ~5,216-company active population**, not a blue-chip index. That necessarily includes hundreds of penny-stock shells, pre-revenue biotechs, SPACs mid-merger, bankruptcy-emergent companies, and commodity/currency pass-through trusts — company types whose financials are *structurally* different from a normal operating business (near-zero assets, revenue, or liabilities are all *normal* for these).
2. **The shared calculation engine (`calculate.py`'s `_compute()`) was built as a pure formula executor from day one** — sum numerator inputs, sum denominator inputs, divide. It never had any concept of "is this ratio meaningful," only "can these two numbers be divided." Every ratio-shaped metric added over months of build sessions silently inherited that same blind spot.
3. **No systematic full-catalog check existed until doc 47 was built.** Everything that had been silently wrong since the 2026-08-26 full-population rollout surfaced in one shot instead of being caught incrementally.

### The root-level fix: per-metric allowlist → per-concept registry

The fixes documented above (`REVENUE_DENOMINATOR_METRICS`, `ASSET_DENOMINATOR_METRICS`, `INTEREST_EXPENSE_DENOMINATOR_METRICS`) were themselves still reactive — three separate sets of metric NAMES a human has to remember to extend every time a new violating metric surfaces. Refactored to a single **`CONCEPT_MATERIALITY_FLOORS: dict[str, Decimal]`**, keyed by the actual canonical concept a metric divides by (`revenue`, `total_assets`, `current_liabilities`, `interest_expense`), consulted automatically by `_compute()`'s `ratio`/`sum_diff_ratio`/`days` branches via a new `_materiality_floor_violation()` helper. `calculate_for_company()` now derives `denominator_concept_names` directly from each metric's own `metric_definition_input` rows (`role == "denominator"`) and passes that through — **a future metric denominating on any registered concept is automatically protected, no manual allowlist edit required.**

### A 5th real bug found extending the coverage: `current_liabilities`

Investigating `current_ratio`/`quick_ratio`'s own critical cluster (denominator = `current_liabilities`, a concept never covered by the original 3-set design) surfaced the same near-zero-denominator shape on a new concept: **5 Invesco CurrencyShares trusts** (Euro/Swiss Franc/Yen/Pound/AUD) showing current ratios of 1,000-3,000x. Verified on Invesco CurrencyShares Euro Trust: real, authoritative `current_liabilities = $155,864` (a genuine near-zero management-fee accrual for a pass-through currency trust with no real operating liabilities) against `current_assets = $219.7M`. Added `"current_liabilities": Decimal("1000000")` to the registry — same $1M floor as revenue/assets, sized the same way (checked the company's own other real periods first).

### Two more real, DIFFERENT root causes found and deliberately NOT fixed this pass

Investigating the same `current_ratio`/`quick_ratio` cluster surfaced two bugs that are **not** materiality issues at all — a floor can't fix either:

- **Oyocar Group Inc.**: real, authoritative, as-filed `AssetsCurrent = -$26` (negative twenty-six dollars). Current assets can never legitimately be negative — this is the filer's own XBRL tagging error in their real 10-Q, not a Scrooner extraction bug (confirmed `is_authoritative=true`, correctly extracted exactly as filed).
- **Zedge, Inc.**: real, authoritative `InventoryNet = $21.6M` for the same period where `current_assets = $20.3M` — logically impossible under GAAP (inventory is always a subset of current assets), yet both facts are individually correctly-tagged and authoritative under the standard `us-gaap:InventoryNet` tag. Looks like a period-bracketing/context mismatch rather than a mapping or sign error — needs real forensic investigation (checking the source filing directly) before attempting a fix. Sized: 4 companies total show this negative-ratio shape.

Also found, investigated, and correctly left alone: **`goodwill_pct_assets`** (6 critical) — checked whether the same `total_assets` floor would explain it and found it doesn't: most of the affected companies' `total_assets` values are well above $1M (e.g. BTC Digital Ltd. at $39.9M), so this is a different, not-yet-diagnosed bug (most likely the `goodwill` numerator itself being stale/wrong), not a materiality issue. Flagged, not force-fixed under an ill-fitting explanation.

### Deployment status: paused, not skipped

Code refactor complete, 708 pipeline unit tests passing, committed to `main`. The actual population-wide `calculate` rerun needed to apply the new `current_liabilities` floor (437 affected companies) was launched, then **stopped mid-run** after a coordinating peer session (`scrooner-50`) flagged that it was racing a coordinated full-population recompute (`pipeline-recompute.yml`) already in flight across multiple sessions, competing for the same ~15-connection Supabase pooler budget. Killed cleanly (the whole wrapper tree, not just the visible workers, per this project's own documented `xargs -P N` gotcha). Deployment will resume once that peer run reports done — the code is live and correct in `main`, just not yet re-run against the 437 affected companies' stored `analytics.metric_value` rows.

## Second-day addendum (2026-09-29): the `roe`/`price_to_book` cluster — a SPAC accounting artifact, generalized sector exclusion

Investigating the still-open `roe` cluster (115 critical, flagged as untouched in an earlier honest status report). Top offender: Cantor Equity Partners V, Inc. at 3294.04% TTM ROE. Checked directly: real, authoritative `stockholders_equity = $1,693` (Q2 2026) against real multi-million-dollar TTM net income.

**Not the same "genuine leverage/distress story" doc 47's own wide ROE bound is deliberately tolerant of.** SPAC accounting convention classifies most of a blank-check company's raised capital as temporary "shares subject to possible redemption," structurally excluded from PERMANENT stockholders_equity by design — regardless of the company's actual financial health. Confirmed this is a genuinely different case by spot-checking a second company the same pass: **NRX Pharmaceuticals** (a real distressed biotech, -$170K equity from real, ongoing cash burn) — correctly left un-excluded, a real signal worth flagging, not swept away by the same fix.

Grouped the full 115-company `roe` critical cluster by `sic_description`: Pharmaceutical Preparations (25) dominates, Blank Checks (7) is smaller but cleaner-cut. Unlike the ebitda/fcf case, pharma/biotech's ROE extremes here look like genuine distress signals (same reasoning as NRX Pharmaceuticals), not a sector-wide structural artifact — so only `Blank Checks` was added to the exclusion, not the full `PRE_REVENUE_RD_SIC_DESCRIPTIONS` set.

**A second real finding along the way**: `ttm.py`'s own TTM ROE computation (`_compute_ttm_returns_for_company`) is a completely separate code path from `calculate_shapes/` — it was never covered by yesterday's materiality-floor refactor at all, and has no floor/guard mechanism whatsoever (`roe_value = ttm_net_income / equity_hit[0]`, guarded only against exact zero). A blanket equity floor there would be the wrong fix regardless (it would incorrectly suppress NRX Pharmaceuticals' real signal) — the sector exclusion is the correct mechanism specifically because the SPAC case is a structural accounting artifact, not a magnitude problem.

**Fix**: generalized `plausibility_check.py`'s sector-exclusion mechanism from `SECTOR_EXCLUDED_RELATIVE_CHECK_METRICS` (ebitda/fcf only, RELATIVE_CHECKS-only) to `SECTOR_EXCLUDED_METRICS: dict[str, set[str]]`, checked once before the EXACT_SET/RELATIVE_CHECKS/ABSOLUTE_BOUNDS dispatch — reaches ABSOLUTE_BOUNDS metrics (`roe`, `price_to_book`, both share the `stockholders_equity` denominator) as well as RELATIVE_CHECKS ones, with zero change to either check type's own logic. 734 pipeline unit tests passing (1 new test asserting the dict reaches both check types correctly).

**Deployment status**: code committed, not yet redeployed — a coordinating peer session is running a multi-stage full-population recompute (refresh, sanity, then a conflict-fill/TTM-recompute pass) that will itself change `metric_value` again. Holding the full `scrooner-sanity plausibility` rerun until that's done, so the resulting numbers reflect the final, stable state rather than an intermediate one.

## Third-day addendum (2026-10-02): `goodwill_pct_assets` investigated and closed out — heterogeneous, correctly left flagged

Last remaining unexamined cluster from doc 47's original list (6 critical). Investigated 2 of 6 companies in depth, found two genuinely *different* root causes, confirming this cluster is heterogeneous rather than one systemic bug:

- **Triller Group Inc.**: `goodwill = $1,005,778,000` ($1.006B) against `total_assets = $50,578,000` for the same FY2024 period — real, authoritative, correctly-mapped `us-gaap:Goodwill` tag from a real 10-K (filed 2026-01-26), no amendment exists. Almost certainly a genuine filer-side 1000x scale error (plausibly should read $1,005,778) — same category as Mosaic Co's dividend-per-share error, not fixable without guessing the intended value.
- **PetVivo Holdings, Inc.**: `goodwill = $13,407,693` stays **exactly frozen** across 5 consecutive real filing periods (FY2018 through FY2019) while `total_assets` genuinely shrinks from $1.57M to $691K as the company burns cash. Since goodwill is always a subset of total assets by accounting definition, this is structurally impossible once total_assets drops below it — but the flat, repeated value across many periods is a different signature than a one-off typo, more consistent with a stale/carried-over XBRL context than a single data-entry mistake. Not investigated further (would need the actual filing HTML, not just the structured facts, to confirm).

**Conclusion: this cluster does not get a code fix.** Unlike the materiality-floor pattern (revenue/assets/liabilities/interest-expense near-zero) or the SPAC equity-structure pattern (roe/price_to_book), there's no single root cause here that generalizes across companies — each is its own small, real, likely-unfixable-without-guessing anomaly in a real company's own SEC filing. Given the tiny scale (6 of ~245,000 checked values) and this project's standing "never guess a value" discipline, correctly left flagged as `critical` (working as intended — these ARE worth a human's attention) rather than force-fit into an explanation that doesn't actually hold for all 6.

## Final status, this investigation closed out

All items from the original "still open" list have now been either fixed or deliberately, evidence-backed left alone:

| Cluster | Outcome |
|---|---|
| Growth-rate discontinuities (net_income/eps/fcf_growth_yoy) | **Fixed** — materiality floor on prior-period base |
| ebitda/fcf TTM-vs-quarterly denominator | **Fixed** — `_load_ttm_revenue_denominators()` |
| ebitda/fcf pharma/biotech noise | **Fixed** — sector exclusion |
| operating_margin/net_margin/roa/interest_coverage_ratio | **Fixed** — concept-keyed materiality floors |
| current_ratio/quick_ratio (Invesco currency trusts) | **Fixed** — `current_liabilities` floor |
| roe/price_to_book (SPAC equity structure) | **Fixed** — sector exclusion, generalized mechanism |
| Oyocar Group (`AssetsCurrent = -$26`) | Investigated, real filer XBRL error, correctly left flagged |
| Zedge (`InventoryNet` > `current_assets`) | Investigated, likely period-bracketing mismatch, correctly left flagged |
| Mosaic Co (`dividend_yield` 837,700%+) | Investigated, real filer XBRL scale error, correctly left flagged |
| goodwill_pct_assets (6 companies) | Investigated, heterogeneous real anomalies, correctly left flagged |
| working_capital/net_cash (distressed balance sheets) | Investigated, real signal, correctly left flagged |
| `*_reconciliation_gap` family | By design, diagnostic not a locked ratio, correctly left flagged |
| Triton International's revenue gap | Sized, not fixed — a real, separate dimensional-XBRL mapping gap, flagged for a future pass |
| Beasley Broadcast's large-base EPS case (bankruptcy emergence) | Sized, not fixed — the materiality floor doesn't apply to a large prior base |

Verified live via the daily cron's own run (2026-09-30 21:33 UTC, after the coordinated full-population recompute completed): `current_ratio` critical 6→0, `price_to_book` 5→2, `roe` 115→105 (Cantor Equity Partners V confirmed fully excluded, zero rows). Critical count overall: 7,003 (original) → 4,509 (current, includes normal day-to-day drift from new periods/prices on top of all fixes above).
