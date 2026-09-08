# Doc 45 — yfinance Expansion & Data Sanity Plan

**Draft (2026-09-08).** Prompted directly: "what more we can do with yfinance API... plan for data sanity." Every API surface named below was checked live against a real AAPL payload before being included — none of this is from yfinance's docs or memory. See the raw evidence in this session's tool history; the shapes quoted here are real, not illustrative.

**Governing rule, unchanged from the rest of this plan (doc 44's Tag Investigator entry, locked by explicit user direction 2026-09-08): yfinance is an observer, never an authority.** Every item below is a DETECT/MATCH mechanism. Nothing here proposes writing a yfinance number into `core`/`analytics` as a stored value — a finding either (a) confirms our own SEC-derived data is right, (b) surfaces a lead the Tag Investigator traces back to a real `core.fact` row before anything changes, or (c) is a pure freshness/staleness signal with no "value" to store at all.

## What's already built (not repeated here — see doc 44)

- `sanity/yfinance_check.py` — 22 `.info()`-based ratio checks, latest period only.
- `yfinance_financials/` — quarterly income statement / balance sheet / cash flow, every available quarter, full population fetch in progress as of this doc.
- `sanity/tag_investigator.py` — the fix mechanism (per-company SEC tag preference, `company_tag_preference`).

## New surface, verified live, ranked by value / cost / risk

| # | API | What it gives (verified real shape) | What it checks against | Cost/company | Priority |
|---|---|---|---|---|---|
| 1 | `Ticker.splits` | Exact stock-split dates + ratios, full history (AAPL: 1987 2:1, 2000 2:1, 2005 2:1, 2014 7:1, 2020 4:1 — all real, all correct) | Whether our own `shares_outstanding`/`diluted_eps`/per-share series has an un-adjusted split discontinuity — a real, **already-named gap** (doc 21 §2: "stock-split... tags still raw/unmapped") | 1 call, tiny payload | **P0** |
| 2 | `Ticker.dividends` | Exact per-payment date + per-share amount, full history | Per-payment granularity for `dividends_paid`/`dps_growth_yoy`/`dividend_growth_streak_years` — tighter than the existing `dividend_yield` ratio check | 1 call, small payload | **P0** |
| 3 | `Ticker.calendar` | Next earnings date, next ex-dividend date, analyst EPS/revenue range for the upcoming quarter (real AAPL value: Earnings Date 2026-10-30) | **A genuinely new SANITY DIMENSION**: freshness, not correctness. Everything built so far checks "is the value right"; nothing checks "is our data current." A company whose latest stored period is 2+ real reporting cycles behind this date is stale, independent of whether any stored value is itself correct | 1 call (often free — same payload as `.info()`'s `earningsTimestamp` fields, already fetched) | **P0** |
| 4 | Annual statements (`income_stmt`/`balance_sheet`/`cashflow`, no `quarterly_` prefix) | Same shape as the already-built quarterly comparison, FY periods instead | Closes the **already-named gap** in `yfinance_financials/`'s own "what's NOT done" section — FY-period values, which for some concepts (banks' `Total Revenue` aggregate, e.g.) may be the only genuinely comparable granularity | Same 3 calls/company as the quarterly system (reuses the exact same fetch/compare code, one new `frequency='annual'` branch) | **P1** |
| 5 | `Ticker.get_shares_full(start=, end=)` | A genuine dated **time series** of shares outstanding (real AAPL values: 14,776,353,000 on 2026-01-10 down to 14,594,180,000 on 2026-08-05) | Directly targets the **already-documented** Block/Reddit-style gap (`company_master/shares_outstanding_fallback.py`'s own text-extraction fallback) — an independent check on whether that fallback's extracted value is even the right order of magnitude, and a candidate lead for companies missing point-in-time shares entirely | 1 call, small payload | **P1** |
| 6 | `Ticker.insider_transactions` | Individual transactions: shares, value, insider name, position, transaction type, date (real AAPL row: 1,439 shares, $456,177, dated 2026-09-01) | Cross-check against our own **real, SEC Form-4-derived** `core.insider_transaction` (doc 19) — a third-party validation of a system that has never been externally checked before. Compare transaction COUNT and net buy/sell direction over the same window, not exact share-for-share matching (yfinance's own transaction list is known to be incomplete/delayed relative to a direct EDGAR parse) | 1 call | **P2** |
| 7 | `Ticker.institutional_holders` / `major_holders` | Named top holders, separate `Shares`/`Value`/`pctHeld`/`pctChange` columns (verified real AAPL row: BlackRock Inc., 1,162,996,939 shares, $372,124,131,991, 7.97% held) + aggregate `institutionsPercentHeld`/`insidersPercentHeld`/`institutionsCount` | Cross-check against our own **real, SEC Form-13F-derived** `core.institutional_ownership` Top 10 table (doc 19) — name-match the top few holders, sanity-check aggregate % against our own computed `institutional_ownership_pct` at a MORE granular (holder-level) resolution than the existing single-number check | 1 call | **P2** |
| 8 | `Ticker.get_earnings_dates()` | Per-quarter actual reported EPS vs. analyst estimate, with real report dates | A cleaner, per-quarter-labeled source for `diluted_eps` verification than deriving from `.info()`'s single trailing figure — could replace/strengthen the existing `diluted_eps` line in `yfinance_financials` | 1 call | **P2** |

**Explicitly ruled out, not silently skipped:** `Ticker.recommendations`/`analyst_price_targets` (analyst forecasts — doc 02 excludes this from the product entirely, nothing of ours to check it against), `Ticker.sustainability` (ESG — same reasoning), `Ticker.option_chain()` (derivatives — out of scope), `Ticker.news` (no numeric data to compare). Building a sanity check against data Scrooner doesn't claim to have would be checking nothing — see doc 02's decision register before revisiting any of these.

## Recommended build order

**Phase 1 (P0, build first — cheap, high-value, closes named gaps):**
1. `Ticker.calendar`-based freshness check — new severity class entirely (`stale`, not `major`/`minor`), since this isn't a value mismatch. Simplest to build (no period-matching, no sign conventions, no normalization) — good first addition to prove the pattern before the harder ones.
2. `Ticker.splits` discontinuity check — for each real split date, verify our own `shares_outstanding`/`diluted_eps` series shows the expected ratio change across that date, not a silent gap or an unadjusted jump.
3. `Ticker.dividends` per-payment check — extend the existing `dividends_paid` comparison (currently a single TTM-ish figure) to per-payment-date granularity.

**Phase 2 (P1, real cost — reuses existing code shape):**
4. Extend `yfinance_financials/fetch.py`/`compare.py` with a `frequency='annual'` branch (mechanically identical to the quarterly path already built and proven).
5. `get_shares_full()` cross-check, specifically targeted at the known Block/Reddit-shaped gap population (companies with `core.shares_outstanding_fallback` rows or zero point-in-time shares at all) rather than the full population — a bounded, evidence-scoped rollout matching this project's own "measure before building broadly" discipline.

**Phase 3 (P2, genuinely new comparison surfaces, higher build cost):**
6. Insider transactions cross-check against `core.insider_transaction`.
7. Institutional holders cross-check against `core.institutional_ownership`.
8. Earnings-date-based EPS history, replacing/strengthening the existing `diluted_eps` check.

## Real risks to design around (learned this session, not new)

- **Sign/unit conventions must be verified live per field, never assumed** — `dividends`/`splits` look unambiguous (a split ratio and a per-share dollar amount are hard to misinterpret) but should still get one real spot-check against a known value before trusting at scale, the same discipline that caught `dividendYield`/`debtToEquity`'s scale mismatch.
- **Period alignment**: `get_shares_full()`/`insider_transactions`/`institutional_holders` are NOT quarter-aligned at all — they're point-in-time or transaction-dated. The comparison logic for these needs its own matching rule (nearest-date-within-tolerance, not the quarterly `_closest_period` reused as-is).
- **Cost multiplies fast.** Phases 2-3 each add 1 more yfinance request per company on top of the 4 calls/company already in flight (`.info()` + 3 statements). A full-population Phase-3 rollout would be 6 calls/company, double today's already-multi-hour cost — size real findings on a bounded batch (golden-10 or a few hundred) before committing to full population, the same gate that justified building `yfinance_financials/` in the first place.
- **`insider_transactions`/`institutional_holders` are NOT a source of truth even for comparison purposes the way `.info()`'s ratios are** — Yahoo's own holder data is known (from public reporting on yfinance's own limitations) to lag and sometimes miss filings entirely. A mismatch here is weaker evidence of a real Scrooner bug than a mismatch in `.info()`'s ratios or the statement-line comparison; treat findings from Phase 3 as leads to investigate, not confirmed bugs, more readily than Phase 1/2 findings.

## Verification plan (before any phase ships)

Same discipline as everything else this session: for each new check, spot-verify against 2-3 real, named companies (at least one with a genuinely known history — e.g. AAPL's real 2020 4:1 split, a company with a well-documented recent dividend cut) before trusting the comparison logic at scale. Golden-10 first, exactly as `yfinance_financials/` was built and proven, before any full-population run.
