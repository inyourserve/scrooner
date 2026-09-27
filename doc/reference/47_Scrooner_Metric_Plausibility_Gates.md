# Doc 47 — Metric Plausibility Gates

**Draft (2026-09-27), grounded in live data, not guessed numbers.** Direct request: "PE can't be higher and lower than this? dividend yield etc — do this for almost all the metrics." This doc answers that for all 82 rows in `analytics.metric_definition`.

**What this is:** a reference table of plausible-value bounds per metric — a **CRITICAL** range outside which a value is almost certainly a formula/data bug, not a real number, and a narrower **WATCH** range outside which a value is unusual enough to deserve a human look but is not automatically wrong. This doc does **not** change any code by itself — see "Status" at the bottom.

**What this is not:** a second source of truth. Every bound here is a plausibility check on our own already-computed `analytics.metric_value`, the same "observer, not authority" role yfinance plays in `sanity/yfinance_check.py` (`pipeline/CLAUDE.md`). A value outside CRITICAL means "go look at the filing," never "silently clamp or discard."

## Methodology

1. **Every bound below is checked against the real, current distribution** of that metric across the full active population (`select percentile_cont(...) ... from analytics.metric_value`, run 2026-09-27) — not derived from theory alone. The exact query and raw percentiles are preserved in `doc/learnings/2026-09-27-metric-plausibility-gates.md`.
2. **This immediately surfaced real, currently-live degenerate values** — e.g. `roe` max **56,600,000%**, `price_to_book` max **$1.29 billion**, `current_ratio` max **5,820,424**, `dividend_yield` max **837,700%**. These are not hypothetical edge cases this doc is guarding against in the abstract; they are rows in the database today. All are the same, already-documented failure mode: a ratio's denominator lands near zero (near-zero equity, near-zero revenue, a data-entry/scale error in one input), producing an arithmetically-correct but economically-meaningless number. `sanity/yfinance_check.py` already has one instance of this guard (`DEGENERACY_GUARD_BOUND = Decimal(3)`, i.e. 300%, applied to `net_margin`/`gross_margin`/`operating_margin`/`ebitda_margin`/`roa`/`roe`/`peg_ratio`/`revenue_growth_yoy`) and `apps/app/lib/company/db.ts`'s peer-comparison query independently bounds `roe`/`roic` to ±200% for the same reason — this doc generalizes both precedents to every metric, and widens where the existing bound turns out tighter than real, legitimate data (see ROE/ROIC below).
3. **CRITICAL bounds are set wide of the real p01/p99** — loose enough that a genuine distressed or hyper-growth company never trips them, tight enough that the observed degenerate maximums above always do. **WATCH bounds sit closer to the real p01/p99** — a company beyond WATCH is statistically unusual and worth a look, not necessarily wrong.
4. **A bound of `None` means "no safe universal number exists for this metric"** — these are flagged explicitly with the better, relative check to use instead (Section 6). Forcing a fake absolute number here would repeat the exact mistake this project's own history warns against (`pipeline/CLAUDE.md`'s "a keyword-matched candidate tag is frequently a different concept" lesson, applied to bounds instead of tags).
5. Every ratio below is expressed as a **plain decimal fraction** (0.15 = 15%), matching `analytics.metric_value.value`'s own stored convention — never the "whole-percentage" scale yfinance uses for some fields (`dividendYield`, `debtToEquity`), which `sanity/yfinance_check.py` already has to normalize around.

---

## 1. Margins and returns (fraction of revenue/equity/assets)

| Metric | Formula | CRITICAL (reject) | WATCH (review) | Note |
|---|---|---|---|---|
| `gross_margin` | Gross Profit / Revenue | `[-10, 2]` | `[-2, 1.05]` | Ceiling >100% only via "other income" reclass; real p99 = 99.9%. |
| `operating_margin` | Operating Income / Revenue | `[-20, 5]` | `[-5, 1]` | Real p05 = -1,366%; distressed micro-caps legitimately go very negative on tiny revenue. |
| `net_margin` | Net Income / Revenue | `[-30, 10]` | `[-10, 2]` | Same shape, one-time gains can push net margin briefly >100% of revenue for a tiny-revenue company. |
| `pretax_margin` | Income Before Tax / Revenue | `[-30, 10]` | `[-10, 2]` | Mirrors net_margin. |
| `ebitda_margin` | EBITDA (TTM) / Revenue | `[-30, 10]` | `[-5, 2]` | |
| `fcf_margin` | (CFO − CapEx) / Revenue | `[-30, 10]` | `[-5, 2]` | |
| `roe` | Net Income / Equity | `[-10, 10]` | `[-2, 2]` | **Widens** the existing ±200% peer-comparison bound (`db.ts`) to ±1000% for CRITICAL only — a real near-zero-equity company (post-heavy-buyback, e.g. real AAPL-shaped cases) can legitimately clear 200% without being a bug; keep ±200% as WATCH, not CRITICAL. Real max 56,600,000% is unambiguously degenerate either way. |
| `roa` | Net Income / Total Assets | `[-5, 5]` | `[-1, 1]` | Real p99 = 43%; ROA rarely exceeds 100% for a real operating company. |
| `roic` | NOPAT / Invested Capital | `[-10, 10]` | `[-2, 2]` | Same widening rationale as ROE — Invested Capital (Debt + Equity − Cash) can be near-zero for a real, cash-rich, low-debt company. |
| `interest_coverage_ratio` | Operating Income / Interest Expense | `[-5000, 5000]` | `[-500, 500]` | Denominator (Interest Expense) is often tiny for a low-debt company — real p99 = 885x; bound is wide by design. |

## 2. Liquidity and leverage

| Metric | Formula | CRITICAL | WATCH | Note |
|---|---|---|---|---|
| `current_ratio` | Current Assets / Current Liabilities | `[0, 1000]` | `[0.1, 50]` | **Hard floor at 0** — both inputs are non-negative by accounting definition; any negative value (real min: **-1.27**, seen live) is a sign/tag bug, always CRITICAL, no exception. |
| `quick_ratio` | (Current Assets − Inventory) / Current Liabilities | `[0, 1000]` | `[0.1, 20]` | Same floor-at-0 rule; real min **-530** is impossible and always a bug. |
| `debt_to_equity` | Total Debt / Equity | `[-2000, 2000]` | `[-50, 50]` | Legitimately negative when Equity is negative (common for heavy-buyback or distressed companies) — do not treat negative as automatically wrong, only extreme magnitude. |
| `debt_to_ebitda` / `net_debt_ebitda` | (Net) Debt / EBITDA (TTM) | `[-2000, 2000]` | `[-50, 50]` | Sign flips when EBITDA is negative — legitimate, not a bug by itself. |
| `working_capital`, `net_cash`, `net_change_in_cash` | see §6 | — | — | Dollar-scale; use the relative check in §6, not an absolute bound. |

## 3. Valuation multiples (require price)

| Metric | Formula | CRITICAL | WATCH | Note |
|---|---|---|---|---|
| `trailing_pe` | Price / Diluted EPS (TTM) | `[-2000, 2000]` | `[-200, 200]` | Legitimately negative (net loss) or very high (near-breakeven EPS) — sign alone is never the trigger. Real max 14,121 and min -6,995 are both bugs (near-zero EPS denominator). |
| `price_to_book` | Market Cap / Equity | `[-10000, 10000]` | `[-500, 500]` | Real max **1.29 billion** confirms Equity landed near zero for at least one company — a live, current bug worth chasing separately from this doc. |
| `price_to_sales` | Market Cap / Revenue (TTM) | `[0, 10000]` | `[0, 200]` | Should floor at 0 (Market Cap and Revenue are both normally ≥ 0); real min **-237** implies a negative-revenue period, itself worth checking rather than assumed impossible. |
| `ev_ebitda` | (Mkt Cap + Debt − Cash) / EBITDA | `[-10000, 10000]` | `[-500, 500]` | |
| `ev_sales` | (Mkt Cap + Debt − Cash) / Revenue | `[-500, 10000]` | `[0, 300]` | |
| `peg_ratio` | Trailing P/E / EPS Growth % | `[-500, 500]` | `[-50, 50]` | Already has a documented, deliberate wide-tolerance treatment vs. yfinance (real methodology divergence, not a bug) — see `sanity/yfinance_check.py`'s own module docstring. |

## 4. Yield / capital-return ratios (require price, except `institutional_ownership_pct`)

| Metric | Formula | CRITICAL | WATCH | Note |
|---|---|---|---|---|
| `dividend_yield` | DPS (TTM) / Price | `[0, 1]` (100%) | `[0, 0.20]` (20%) | **Hard floor 0** — dividends can't be negative by construction (confirmed: real min is exactly 0). Real max **837,700%** is unambiguously a scale/unit bug (almost certainly a stock-split-unadjusted DPS divided by a post-split price, or a per-share vs. aggregate mixup) — chase this directly, don't just gate it. |
| `fcf_yield`, `buyback_yield` | (FCF or Buybacks, TTM) / Market Cap | `[-10, 10]` | `[-1, 1]` | Can be negative (negative FCF, or `buyback_yield`'s own real min -0.29 for a company issuing, not buying, stock). |
| `total_shareholder_yield` | Div Yield + Buyback Yield − Dilution | `[-20, 20]` | `[-2, 2]` | Already a known, not-yet-fixed live anomaly for one company (Akari Therapeutics, `pipeline/CLAUDE.md` 2026-09-10) — this gate would have caught it before it ever reached the screener. |
| `institutional_ownership_pct` | Σ 13F holdings / Shares Outstanding | `[0, 1]` | `[0, 0.98]` | **Hard bound [0,1]** — this is a real percentage of a finite share count; anything ≥100% is definitely a bug (double-counted filer, stale share count, or an amendment not deduped). Never sum with mutual-fund % per `doc/scoping/insider_info.md`'s own locked rule — that's a separate, product-level guard this doc doesn't relitigate. |

## 5. Expense ratios, dilution, and per-share figures

| Metric | Formula | CRITICAL | WATCH | Note |
|---|---|---|---|---|
| `sga_pct_revenue`, `rnd_intensity`, `capex_pct_revenue`, `sbc_pct_revenue` | Expense / Revenue | `[-1, 1000]` (100,000%) | `[0, 5]` (500%) | **Deliberately loose ceiling** — a real pre-revenue biotech can spend 1000x+ its tiny revenue on R&D (real p99 for `rnd_intensity` is already 22,112%) and that is a true, correct number, not a bug. Floor near 0 (expenses shouldn't be negative) is the real signal; observed max values in the hundreds of thousands of percent (e.g. `sga_pct_revenue` 140,058,700%) are still bugs, just further out than the ratio metrics above. **This category needs the revenue-floor check in §6, not a tighter ceiling** — the real fix for a false-negative here is requiring Revenue > some minimum (e.g. $100K) before trusting the ratio at all, not lowering this bound and risking false-flagging real hyper-growth biotechs. |
| `goodwill_pct_assets` | Goodwill / Total Assets | `[0, 1]` | `[0, 0.85]` | **Hard bound [0,1]** — goodwill is a balance-sheet line item and cannot legitimately exceed Total Assets in a properly consolidated statement. Real max 51,099 (5.1 million %) is definitely a unit-scale mismatch between the two inputs. |
| `eps_dilution_spread` | (Basic − Diluted EPS) / Basic EPS | `[-2, 1]` | `[-0.1, 0.5]` | Normally in `[0, 0.3]`; small negative values can occur from restatement timing mismatches, large negative/positive values are a real bug. |
| `share_dilution_trend`, `diluted_shares_growth_yoy` | ΔShares / Shares(t-1) | `[-1, 20]` | `[-0.5, 3]` | **Hard floor -1 (-100%)** — a company cannot retire more than 100% of its own shares; this is a mathematical certainty, not a judgment call. |
| `book_value_per_share`, `fcf_per_share`, `net_cash_per_share` | (Equity, FCF, or Net Cash) / Shares Outstanding | `[-100000, 100000]` | `[-1000, 1000]` | Per-share dollar figures scale with a company's own share price convention (Berkshire-shaped high-price stocks vs. a $1 penny stock) — bound is wide for that reason. Real max **$8.76 billion/share** (`book_value_per_share`) is a share-count/scale bug, not a real company. |

## 6. Metrics with no safe universal bound — use a relative check instead

These are aggregate dollar amounts (not ratios) that legitimately range from a few thousand dollars (a micro-cap) to hundreds of billions (Apple/Microsoft) — no fixed number is "too big" in isolation. The right check compares the value **against the same company's own Revenue or Market Cap**, not a universal constant.

| Metric | Suggested relative check | Real evidence |
|---|---|---|
| `market_cap` | flag if > $6T (no real US company has ever exceeded this as of 2026) or **exactly 0** for an active company with real trading history | Real max **$5.47T** is plausible (largest real companies); real min **$0** is suspicious and worth a direct look — a genuine operating company's market cap should never be exactly zero. |
| `ebitda`, `fcf` | flag if `abs(value) > 3 × Revenue (TTM)` | EBITDA/FCF exceeding 3x revenue implies a margin structure with no real precedent; real p99 for both is well under 1x revenue for most companies. |
| `working_capital`, `net_cash`, `net_change_in_cash` | flag if `abs(value) > 2 × Total Assets` | These are balance-sheet-scale figures; a magnitude larger than the balance sheet itself is definitionally a bug. |
| `net_interest_income`, `cash_returned_to_shareholders` | flag if `abs(value) > Revenue (TTM)` | A company rarely returns more cash to shareholders in a year than it earns in revenue (real exceptions are one-time special dividends after an asset sale, hence "flag," not "reject"). |
| `ar_change_reconciliation_gap`, `ap_change_reconciliation_gap`, `inventory_change_reconciliation_gap`, `effective_tax_rate_gap` | flag if `abs(gap) > 10% of Revenue` (the change metrics) or `abs(gap) > 0.5` (the tax-rate gap, itself already a fraction) | These are diagnostic quality-of-earnings signals, not locked ratios, per their own `formula_description` — a large gap flags something to investigate (M&A, reclassification), not necessarily an error. Do not treat a large gap as automatically wrong. |

## 7. Growth rates and CAGRs (all `*_growth_yoy`, `*_growth_3y_cagr`, `*_growth_5y_cagr`, `*_growth_10y_cagr`)

One shared rule for the whole family (`revenue_growth_*`, `eps_growth_*`, `net_income_growth_*`, `fcf_growth_*`, `dps_growth_*`, `diluted_shares_growth_*`):

| Bound type | Range | Note |
|---|---|---|
| CRITICAL | `[-1, 1000]` (-100% to 100,000%) | **Hard floor -100%** — a company recovering from a real near-zero base (a common, real pattern for a turnaround or a recent IPO) can post a legitimate 1,000%+ YoY or CAGR number; real p99 values confirm this (`revenue_growth_3y_cagr` p99 = 317%, and real named companies post 1,000%+ off a tiny base). A value can never be below **-100%** though — you cannot lose more than 100% of a positive quantity, so any value under -1 is a certain sign/formula bug, not a real result. |
| WATCH | `[-0.9, 20]` (-90% to 2,000%) | Beyond 2,000% growth is rare enough to warrant a look, even though not impossible. |

`share_dilution_trend`/`diluted_shares_growth_yoy` already have their own row in §5 (same -100% floor logic, tighter ceiling since share issuance is more bounded in practice than earnings/revenue swings).

## 8. Streaks, flags, and scores (bounded by construction, not by data)

| Metric | Valid values | Note |
|---|---|---|
| `piotroski_f_score` | integer, exactly `{0, 1, ..., 9}` | Defined by the standard 9-test methodology — any other value is a code bug, not a data question. Real data already confirms this holds (`min=0, max=9`). |
| `fcf_gt_net_income`, `zero_debt`, `margin_expanding_3yr` | `{0, 1, null}` only | `null` is a valid, meaningful "insufficient data" state per each module's own docstring — never coerce to 0. |
| `profitable_streak_years`, `dividend_growth_streak_years` | integer, `[0, 40]` CRITICAL if higher, `[0, 22]` WATCH | **Corrected 2026-09-27** — the original `[0, 15]` bound here was wrong, based on conflating doc 38's 2015-01-01 floor (which is specific to OWNERSHIP data's refiling cadence) with fundamentals data depth, which is NOT bounded there. Found live on the very first real run: all 348 "critical" violations were major, decades-stable blue-chips (Procter & Gamble, Apple, IBM, Kimberly-Clark, Hershey, Abbott, Colgate-Palmolive) — confirmed Apple's own real `net_income` data spans FY2007-FY2025 (19 real years, unbroken profitability the whole time, matching its well-known real history), and 1,611 companies population-wide have real FY data before 2010, some back to 1992. Real observed max across the population is exactly 20. Widened to double that (40) for CRITICAL, matching the doc's own "wide enough that a real value never trips it" discipline applied correctly this time. |

## 9. Metrics this doc deliberately leaves ungated

`ar_change_reconciliation_gap` and its 3 siblings, plus `effective_tax_rate_gap`, are covered by the relative check in §6, not a fixed bound — repeated here only to be explicit that "no row in §1-§5" does not mean "forgotten," it means "the right check is in §6."

---

## Status and next step

**Built and live, 2026-09-27, same day as this doc.** `sanity/plausibility_check.py` (same shape as `sanity/yfinance_check.py`/`sanity/timeseries_check.py`) implements every bound in §1-§8 as executable Python (`ABSOLUTE_BOUNDS`, `EXACT_SET_METRICS`, `RELATIVE_CHECKS`), runs against the full active population daily (`.github/workflows/pipeline-sanity.yml`, `scrooner-sanity plausibility`), and writes into `analytics.metric_plausibility_check`, wired into the existing `analytics.data_incident` unified view (migration `0072`) alongside the other 5 checkers rather than as a sixth disconnected surface. The code, not this doc, is now the source of truth for the exact numbers — keep this doc in sync if a bound changes, don't let it drift silently.

**First live run, 2026-09-27: 247,834 values checked — 231,929 ok, 7,585 watch, 7,003 critical.** Confirmed it catches exactly what this doc's own research found by hand: `roe` (115 critical), `price_to_book` (4 critical), `dividend_yield` (5 critical), `current_ratio`/`quick_ratio`'s impossible negative values (6/3 critical). Worst offenders by volume: `net_income_growth_yoy` (894), `eps_growth_yoy` (702), `ebitda` (575), `fcf_growth_yoy` (524), `fcf` (465) — the growth-rate and §6 relative-check families dominate, as expected from a near-zero-base denominator.

**Same day, same-session correction: `profitable_streak_years`'s 348 "critical" findings were a bug in this doc's own bound, not the pipeline.** Investigated as the top lead from the first run (see §8's table entry for the full evidence) — every one of the 348 was a real, correct value for a real, decades-stable blue-chip (Apple, Procter & Gamble, IBM...), not a streak-counter bug. Fixed by widening the bound from `[0, 15]` to `[0, 40]` and rerunning: **critical dropped 7,003 → 6,582**, all 6,327 streak-metric rows now correctly `ok`. Left in this doc as a direct, undisguised example of the exact failure mode this whole project's own history warns about repeatedly (`pipeline/CLAUDE.md`) — a plausible-sounding assumption, unverified against the real data, produces a confident-looking false positive. The fix was to do exactly what doc 47's own methodology already demanded: check the real distribution before trusting a bound, which this specific row skipped the first time.

**Same day, same session, direct follow-up ("verify and test with yfinance and do a complete fix end to end"): root-caused and fixed 5 distinct bug classes behind the remaining critical cluster, not just documented them. Final verified count: critical 6,582 → 4,371, watch 7,327 → 6,109.**

1. **De-SPAC / bankruptcy-emergence growth-rate discontinuity** (the largest single cluster: `net_income_growth_yoy` 894, `eps_growth_yoy` 702, `fcf_growth_yoy` 524). Traced to Infleqtion, Inc. (CIK 0002007825): its Q3 2024 `core.fact` rows are the pre-merger blank-check shell's own real, correctly-extracted -$69 quarterly net loss (a separately-filed pre-merger 10-Q), while post-merger periods are the real operating company (-$33.4M Q3 2025) — producing a mathematically-correct but meaningless 483,836.84% "growth" figure. Verified against yfinance before concluding: Yahoo's own quarterly series for INFQ starts only at 2025-03-31 (2024-12-31 returned `NaN`), independently corroborating that the pre-merger shell figures aren't treated as a comparable prior year by an independent provider either. Same root pattern also found in Beasley Broadcast Group (bankruptcy emergence, not a SPAC — a real one-time debt-extinguishment gain + share-count collapse). Fixed with a per-concept materiality floor on the prior-period base (`mapper/ttm.py`'s `CONCEPT_MATERIALITY_FLOORS`, `mapper/fcf_growth.py`'s `FCF_MATERIALITY_FLOOR`) — a near-zero (<$1M) prior value now nulls the growth metric with an explicit `immaterial_prior_base` reason instead of computing a technically-correct but meaningless ratio. Deployed population-wide to the ~2,300 companies flagged critical/watch on any growth metric.

2. **The plausibility checker's own bug: TTM-vs-single-quarter denominator mismatch** (`ebitda` 575→313, `fcf` 465→250 critical, plus the 3 reconciliation-gap metrics and `net_interest_income`/`cash_returned_to_shareholders`, all sharing the same `revenue_sanity_resolved` denominator lookup). `RELATIVE_CHECKS`' own descriptions all say "vs. TTM revenue," but the original `_load_latest_concept_values` picked whichever single `canonical_fact` period was most recent — routinely one quarter, not a trailing-twelve-month figure — while the numerators (`ebitda`/`fcf`) are genuinely TTM-scale. Confirmed on United Rentals: latest revenue picked was $929M (Q1 2026 alone), vs. the real trailing-4-quarter figure of ~$3.73B (929+992+938+872, matching its own real FY2025 total of $3.695B almost exactly) — a false "4.8x revenue" EBITDA finding that's actually ~1.2x. Fixed with a new `_load_ttm_revenue_denominators()` (prefers a real FY row directly, else sums a complete trailing 4 quarters, else skips rather than guesses) — this single fix alone dropped critical 6,582→5,580.

3. **Pharma/biotech sector noise**, found investigating the residual `ebitda`/`fcf` cluster after fix #2: 68% of it (145 Pharmaceutical Preparations + 68 Biological Products companies, spot-checked — Cytokinetics -$695M ebitda on $67.7M revenue, CRISPR Therapeutics -$516M on $13.4M, NuScale Power -$702M on $10.7M) is real, structurally-expected pre-revenue R&D burn, not a bug — the same "real sector characteristic" treatment this project already gives banks/BDCs/REITs. Added a targeted sector carve-out (`PRE_REVENUE_RD_SIC_DESCRIPTIONS`, `ebitda`/`fcf` only — not applied to the balance-sheet/reconciliation checks, which aren't R&D-driven). Critical dropped 5,580→5,362.

4. **Immaterial-denominator ratios**, the same root pattern as #1 applied to `calculate.py`'s shared ratio engine instead of the growth engine. Traced to Inhibikase Therapeutics: a real, authoritative $1 TTM revenue fact (Q4 2023, a genuine tiny licensing payment) against real ~$20M operating losses produced a -2,006,393,700% `operating_margin`. Same pattern found and fixed for `roa` (Appsoft Technologies: real $7 total assets → -1,337,700% ROA) and `interest_coverage_ratio` (Dermata Therapeutics: real $4 quarterly interest expense → millions-of-percent coverage, despite this metric's already-wide ±5000 bound). Fixed with 3 new materiality-floor constants in `calculate.py` (`REVENUE_DENOMINATOR_METRICS`/`ASSET_DENOMINATOR_METRICS`/`INTEREST_EXPENSE_DENOMINATOR_METRICS`, each with its own floor — $1M for revenue/assets, a lower $10K for interest expense since real small companies can have genuinely small-but-material interest expense) plus the matching fix in `expanded_metrics.py`'s standalone `ebitda_margin` computation. **Deliberately did NOT add a floor to `roe`** — near-zero/negative equity is a different, already-accepted degenerate case (a real leverage story for distressed/buyback-heavy companies), not a shell-company signal, and doc 47 §1's own wide ROE bound already accounts for it. Deployed to the ~950 (margins) + ~774 (roa/interest_coverage_ratio) affected companies, each spot-verified live in the database.

5. **A real infrastructure bug found verifying fix #1's deployment, not the original target**: `mapper/ttm.py`/`mapper/fcf_growth.py`/`mapper/calculate.py`'s per-company error handlers were missing the `safe_rollback()` reconnect pattern already established elsewhere in this codebase (`common/errors.py`) — a single dead Supabase pooler connection mid-batch cascaded into 187 companies across 3 of 6 parallel shards failing instead of just the one that hit the drop (confirmed via the actual traceback: `OperationalError: consuming input failed`, then every subsequent company in that same CLI invocation also failing on the now-dead connection). Fixed at all 5 call sites; the 187 stranded companies were identified from the error logs and re-run cleanly (`errored=0`) once fixed. This gap is now closed structurally, not just for this run.

**Correctly identified as NOT bugs, left as-is**: `working_capital`/`net_cash` (real distressed-company balance-sheet distortions — e.g. Galectin Therapeutics' real, authoritative $151.6M current liabilities against $14.8M total assets, traced to a real `LiabilitiesCurrent` XBRL tag, not a mapping error) and the `*_reconciliation_gap` family (doc 47 §6's own stated design: a diagnostic "worth investigating" signal, never meant to be suppressed).

Also hit and fixed along the way: `_load_latest_metric_values`'s own SELECT started hitting the pooler's 2-minute `statement_timeout` once `analytics.metric_value` grew from this session's own rewrite activity — fixed with `set statement_timeout = '5min'` on that connection, the same established pattern already used in `tag_candidates.py`/`coverage_matrix.py` for a rare, heavier-than-usual full-population scan.

700 pipeline unit tests passing throughout this root-cause pass (663 at the start of it, +37 new tests: materiality-floor coverage for `ttm.py`/`fcf_growth.py`/`calculate.py`/`expanded_metrics.py`, plus `_load_ttm_revenue_denominators`). See `doc/learnings/2026-09-27-plausibility-gates-root-cause-fixes.md` for the full investigation trail.
