# 26 — Scrooner: Screener Data-Points Gap Analysis

Cross-references `doc/screener-criteria-study.md` (what makes a screener good) against what Scrooner's pipeline **actually has right now**, checked live, not assumed. Scoped deliberately to **data points only** — the study's §3 (query mechanics: AND/OR, saved screens, NL entry) and §4 (preset screens) are real, but they're doc 24 Phase 3's territory (Screener UI + AI Query), already sequenced; this doc doesn't re-litigate them. §8's monetization tiering is noted where relevant but isn't a data question either.

> **Status:** Draft (2026-08-18) — a gap analysis and proposal, not a build plan. Nothing here is locked. Per doc 02's own guardrail, adding any of these to the locked metric list is a decision, not something this doc does unilaterally.

---

## 1. Already real, already built — just needs exposing as a *filter*

Everything below is a real, computed, verified value already sitting in `analytics.metric_value` or `core.*` tables from this project's own build — not proposed, already shipped. The gap is purely "make it filterable in the Screener," which is doc 24 Phase 3's job, not new data work.

| Study's filter | Scrooner status |
|---|---|
| P/E, Market Cap, Price/Sales, Price/Book, FCF Yield, Dividend Yield | ✅ Computed (doc 25), real values verified for 8/10 golden companies |
| Gross/Operating/Net Margin, ROE, ROIC | ✅ Locked metrics, computed since Mapper Stage 3d |
| Revenue growth, EPS growth (YoY + 3Y CAGR) | ✅ Locked metrics (Mapper Stage 3e) — study wants more horizons, see §3 |
| Debt/Equity, Current Ratio, Interest Coverage | ✅ Locked metrics |
| FCF, FCF Margin | ✅ Locked metrics |
| Market cap band, sector/industry (SIC), exchange | ✅ Company Master 4a already has SIC code, exchange, market cap once price lands |
| Insider buying/selling (§2.6) — the study calls this "rare on free screeners, real differentiator" | ✅ Already have it and better than most: 55,109 real Form 4 transactions, **plus the `is_10b5_1_plan` field** (doc 24 Phase 1) distinguishing discretionary from pre-scheduled sales — something the study doesn't even ask for and most competitors don't have |
| Institutional ownership % (§2.6) | ✅ 58,095 real Form 13F holdings (doc 19 Stage 4) — aggregate % of shares outstanding is one query away, not a new fetch |
| Major shareholders / beneficial ownership | ✅ 527 real Schedule 13D/13G stakes (doc 19 Stage 3) |

**Recommendation**: when doc 24 Phase 3 (Screener UI) is built, make sure insider/institutional signals are in the *initial* filter set, not an afterthought — per the study's own §2.6 framing, this is a genuine differentiator most free screeners don't have, and Scrooner already has better data here (the 10b5-1 flag) than the study's own wishlist asks for.

---

## 2. Zero-new-fetch, real data already in hand — needs a derived-metric build, not new collection

These need new Mapper-side computation (matching the exact pattern doc 18's Tier A metrics and doc 25's price metrics already used), but **no new SEC fetch, no new vendor** — every raw ingredient is already in `core.fact`/`analytics.canonical_fact`.

| Study's filter | What's needed | Evidence checked live |
|---|---|---|
| **Business-quality boolean flags** (§2.9: "FCF > Net Income", "no debt", "profitable every year for N years", "margins expanding 3yr running", "insider buying cluster") | Pure computation over already-locked metrics/facts — no new concept mapping at all | The study itself calls these "cheap to compute... disproportionately valuable" — matches doc 17's existing Pros/Cons checklist pattern (`prosCons.ts`) almost exactly; this is the same deterministic-boolean-flag idea, just screenable instead of display-only |
| **Share count trend / dilution flag** (§2.5) | `shares_outstanding` already has real quarterly history | Confirmed live: AAPL's real trend, 14.94B → 14.59B shares over ~1 year, a genuine buyback signal already sitting in the database, unused |
| **Payout ratio** (§2.5) | `dividends_paid` ÷ `net_income`, both already mapped concepts | No new data |
| **Total shareholder yield** (§2.5) | Dividend yield + buyback yield − dilution — all three components' raw facts (`dividends_paid`, `share_buybacks`, `shares_outstanding` trend) already exist | Needs price (have it) + a new composite formula |
| **Piotroski F-Score (0–9)** (§2.2/2.4) | All 9 components trace to concepts already mapped: net income, ROA (needs `total_assets`, already mapped), CFO, CFO-vs-NI, current ratio trend, gross margin trend, shares-outstanding trend, revenue (asset turnover) | Confirmed live: `net_income`, `total_assets`, `cfo`, `shares_outstanding`, `revenue` all already resolved canonical concepts — a real, computable composite score, zero new fetches |
| **Dividend growth streak (years)** (§2.5) | Multi-year `dividends_per_share` trend — already a mapped, quarterly-resolving concept (used for TTM Dividend Yield) | Just needs a "consecutive years of increase" derived computation |
| **Growth consistency score** (§2.3: "% of last N years with positive growth") | Same YoY growth data already computed for revenue/EPS, just needs a rolling-window aggregation | No new data |

**This is the single highest-value, lowest-risk category** — matches this project's own "boring" philosophy exactly: deterministic, EDGAR-only, no vendor dependency, no new legal/cost exposure. Recommend this as the next data-layer build after doc 24 Phase 3 ships (or even alongside it, since it's independent pipeline work).

---

## 3. Needs new concept-mapping/curation, still EDGAR-only, no vendor

| Study's filter | What's needed |
|---|---|
| **EV/EBITDA, EV/Sales** (§2.1) | Needs an `ebitda` canonical concept (Operating Income + D&A). Confirmed live: D&A tags already exist raw in `core.fact` (`DepreciationAndAmortization`, `DepreciationDepletionAndAmortization`, etc.) — same curation pattern as `statements/classify.py`'s existing additive concepts, not a new fetch. Ties directly to doc 18 Tier A's already-named "EV/EBITDA, EV/Sales" candidates. |
| **Net Debt/EBITDA** (§2.4) | Same EBITDA concept, combined with cash & total debt (already mapped) |
| **PEG ratio** (§2.1) | P/E (have it) ÷ EPS growth rate (have it) — pure formula, no new concept |
| **Quick Ratio** (§2.4) | Already named in doc 18 Tier A — current assets minus inventory, over current liabilities; needs an `inventory` concept curated |
| **Altman Z-Score** (§2.4) | A known, fixed formula over working capital, retained earnings, EBIT, market cap, total liabilities, revenue — all already available or one EBITDA-style curation pass away |
| **Sector/industry "friendly buckets"** (§2.8) | SIC codes already captured (Company Master 4a) but are coarse/dated, exactly as the study notes — needs a curated SIC→sector mapping table, a bounded, one-time reference-data task, not a data-collection one |

None of this needs a new SEC fetch or a vendor — it's the same "curate a composite concept, verify against the golden-10" work this project has already done repeatedly (Mapper's original 17 concepts, doc 17's statement concepts, doc 25's price metrics).

---

## 4. Real gaps — needs new data collection or a vendor decision

| Study's filter | Why it's a real gap | Path forward |
|---|---|---|
| **52-week high/low, price change momentum, beta, average volume/liquidity** (§2.7) | Confirmed: `core.market_price_alpaca` only holds the **latest** price snapshot (doc 25 §2's own deliberate scope — "a snapshot, not a multi-quarter trend"). None of these are computable without a real historical price series. | A genuinely new, bigger Alpaca integration (historical bars, not just latest) — a real follow-on to doc 25, not built |
| **Valuation vs. own 5-10yr history (percentile)** (§2.1) | Same root cause — needs historical price × historical fundamentals over many years | Blocked on the same historical-price gap above |
| **Valuation vs. sector/peer median** (§2.1) | Needs a real peer universe to compute a median against — golden-10 is too small and cross-industry for this to be meaningful (e.g., AAPL's only "peer" in the current universe might be a bank) | Blocked on doc 02's still-open "how wide should the universe go" decision, not just a data-point question |
| **Institutional ownership trend (QoQ)** (§2.6) | We have Form 13F for one filing window only (doc 19 Stage 4's own deliberate scope, same reasoning as price snapshots) | Needs multiple 13F bulk windows ingested over time — a real, bounded follow-on (re-run Stage 4 quarterly, keep history instead of overwriting) |
| **Short interest % of float** (§2.6) | Genuinely not in EDGAR at all — needs FINRA data, a real external source | A real vendor decision, same category as doc 02's still-open items |
| **Index membership (S&P 500/400/600, Russell)** (§2.8) | Not in EDGAR | Needs a vendor or a maintained reference list |
| **Forward growth estimates** (§2.3) | Not in EDGAR (analyst estimates) | Vendor decision, already flagged doc 18 Tier C |
| **Currency handling** (§5.5) | Not currently a real issue for the golden-10 (all USD reporters, even TSM/ENB report in USD per their SEC filings) but would matter at a wider universe | Not urgent; revisit if/when scope widens |

---

## 5. Recommended sequencing

1. **§2's zero-new-fetch derived metrics** (business-quality flags, Piotroski F-Score, dilution trend, payout ratio, shareholder yield, dividend streak) — highest value-to-effort ratio, matches this project's existing patterns exactly, no new decisions needed.
2. **§3's EBITDA-based ratios and Quick Ratio** — ties directly into doc 18's already-named Tier A metrics; building §2 and this together is natural, since both reuse the same curation muscle doc 17/25 already proved.
3. **§1's exposure work** happens naturally as part of doc 24 Phase 3 (Screener UI) — no separate data work required, just don't let the filter list ship thinner than what's already computed.
4. **§4's real gaps** each need their own decision or bigger build (historical price backfill, wider universe, a vendor) — correctly left as open items, not silently assumed, matching doc 02's own discipline.

## 6. What this doc does not do

No metric here is added to doc 02's locked list. No new vendor is chosen. This is the same "real evidence, ranked, nothing built yet" shape as docs 18/21/22/23 before them — say which section to build and it becomes the next doc 27/28-style execution plan.
