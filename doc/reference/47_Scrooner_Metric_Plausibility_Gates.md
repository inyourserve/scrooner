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
| `profitable_streak_years`, `dividend_growth_streak_years` | integer, `[0, 15]` CRITICAL if higher | This project's real filing history starts 2015-01-01 (`doc/foundational/38_Scrooner_History_Depth_Gate.md`'s hard ceiling) — an FY streak longer than ~11-15 years is not representable from data this pipeline actually holds, so a higher value is a real bug (most likely a missing streak-reset check), not a legitimately long streak we just haven't seen yet. |

## 9. Metrics this doc deliberately leaves ungated

`ar_change_reconciliation_gap` and its 3 siblings, plus `effective_tax_rate_gap`, are covered by the relative check in §6, not a fixed bound — repeated here only to be explicit that "no row in §1-§5" does not mean "forgotten," it means "the right check is in §6."

---

## Status and next step

This is a **reference doc only** — nothing in the pipeline reads these bounds yet. The natural next step, if wanted, is a new `sanity/plausibility_check.py` module (same shape as the existing `sanity/yfinance_check.py`/`sanity/timeseries_check.py`) that runs this table against live `analytics.metric_value` daily, writing CRITICAL violations as a new severity tier feeding the existing `analytics.data_incident` unified view (`pipeline/CLAUDE.md`, 2026-09-08) rather than a fifth, disconnected reporting surface. Not built in this pass — this doc's own job was to get the *numbers* right and evidence-backed first, matching this project's own "measure before building" discipline; wiring it into code is a separate, explicit ask.

**One live finding this doc's own research surfaced, not yet chased:** `dividend_yield`'s real max of 837,700% and `price_to_book`'s real max of $1.29 billion are current, live rows in `analytics.metric_value` today — both are the exact shape of bug this doc exists to catch, and both are sitting unfixed in production right now, independent of whether this doc's checks ever get wired into code. Worth a direct look before broader coverage work continues.
