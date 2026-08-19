status: Draft (2026-08-18) · Owner: Founder/Product · Review: once the open question below is answered

# Scrooner — "Decision Dataset" Study Gap Analysis

Cross-references the user-provided [`doc/requirements/perplexity-decision-dataset-study.md`](../requirements/perplexity-decision-dataset-study.md) ("Build for decisions, not data dumps" — Perplexity-generated research, added 2026-08-18) against what's actually locked, built, or already scoped elsewhere. Same method as [doc 26](../requirements/26_Scrooner_Screener_Data_Points_Gap_Analysis.md) used for `screener-criteria-study.md`: read the study, check each claim against real doc/build state, don't re-derive from memory.

**Headline finding**: the study's core thesis — a compact, decision-oriented metric set beats a wide ratio dump — is not new to Scrooner; it's the product's own north star (`CLAUDE.md`'s "~15–20 metrics... not permission to expand ad hoc," doc 10's "Summary: Where the real differentiation lives," doc 18's Tier A/B/C split). **~85% of the study's specific asks are already locked, already built, or already scoped in an existing doc** (mapped below). The genuinely new, non-redundant contributions are three: a "Decision Cards" UX grouping for the not-yet-built Screener/company-page UI, a "why this passed / nearly passed" screener-transparency panel, and one real open product-positioning question the study poses but doesn't answer.

## 1. What the study asks for vs. what's already true

| Study ask | Status |
|---|---|
| Revenue growth, gross/operating margin, FCF margin, ROIC | **Locked & built** — doc 02's 18-metric V1 list, all pure-EDGAR, computed. |
| 3/5-year revenue CAGR, YoY growth | **Built** — `mapper/ttm.py`'s growth calculation (doc 11 Stage 3e). |
| Net debt/EBITDA, interest coverage, current ratio | Interest coverage & current ratio: **locked & built** (doc 02). Net Debt/EBITDA: **already scoped**, doc 18 §2 — blocked only on D&A tag curation (3 taxonomy variants, same `first_match` pattern as every other composite concept), not new work. |
| Share-count change, buybacks, dilution from SBC | **Already scoped**, doc 18 §2 (Dilution Trend, SBC%, Buyback Yield) — doc 18 confirms `WeightedAverageNumberOfDilutedSharesOutstanding` present for **8/8** golden companies, the most complete tag checked in that pass. |
| Insider ownership, insider buying/selling | **Already built** — doc 19 Stages 2-4 (55,109 Form 4 transactions, 527 beneficial-ownership stakes, 58,095 institutional holdings). The study's ask here is *behind* what Scrooner already has. |
| Forward P/E, EV/EBITDA, EV/sales, P/FCF, FCF yield | Trailing P/E, FCF Yield: **locked & built** (doc 25's price metrics). EV/EBITDA, EV/Sales: **already scoped**, doc 18 §2 — blocked on the same price dependency as the original 6, not a new blocker. Forward P/E specifically needs analyst estimates — **already named and deferred**, doc 18 Tier C (needs a vendor, not proposed). |
| Top risks from 10-K, revenue/customer concentration, recurring-revenue share | **Already named as a real gap**, doc 21/22/23 — unstructured text parsing (DEF 14A/deep 8-K, doc 19 Stage 5) and dimensional/segment XBRL (doc 23 — "confirmed genuinely harder... correctly left undesigned"). Not solved by this study; confirms the existing assessment. |
| Debt maturities timeline | **Not scoped anywhere** — needs dimensional XBRL (debt instruments broken out by maturity), same category doc 23 already flagged as harder than a universal mapping. Real gap, low priority given doc 23's own finding. |
| 6/12-month relative return, drawdown from 52-week high, earnings-day reaction, abnormal volume | **Already named as real gaps**, doc 26 Tier 4 — needs historical price backfill beyond doc 25's ~30-day window and (for volume/reaction) intraday/volume data Alpaca's current integration doesn't pull. |
| Sector/industry percentile per datapoint | **Already named as a real gap**, doc 26 Tier 4 — needs a wider company universe than the golden-10; doc 02's own open item on Normalizer coverage width (Supabase free-tier cap) is the actual blocker, not a new one. |
| "Formula, source filing, fiscal period, update date" shown per datapoint | **Already the product's core trust moat** — every `metric_value`/`canonical_fact` row already carries `formula_version`, source filing, period, and data date (doc 04's correctness controls, doc 11's lineage requirement). The study is describing what Scrooner already built, not proposing something new. |

## 2. What's genuinely new

### 2a. "Decision Cards" — a 5-group UX framing (Business / Financial Safety / Valuation / Shareholder Alignment / Recent Change)

Doc 17's built company page groups data by *statement type* (ratios grid, P&L/Balance Sheet/Cash Flow tables, Pros/Cons checklist) — not by *decision type*. The study's 5-card grouping is a different, plausibly better, organizing principle for a screener results row or company-page summary. This doesn't require new data — every input already exists across doc 02's 18 metrics + doc 18's Tier A candidates + doc 19's ownership data — it's purely a presentation-layer regrouping.

**Where it fits**: doc 24's Phase 3 (Screener UI, `apps/app` — not yet built, "the single most consequential gap in the whole product"). Worth considering as the results-row/company-summary layout when that phase starts. Not actionable now — no UI code exists yet to apply it to.

### 2b. "Why this passed your screen" — near-miss transparency

Doc 14's Screener Engine already returns `excluded_missing_data` (which companies were excluded and which metric was null) — but nothing about companies that *matched* showing which rules they met, or companies that *narrowly missed* a threshold. The study's ask — list exact rules met, rules nearly failed, and missing/unreliable datapoints, per result — is a genuine extension of doc 14's already-built `ScreenResult` shape, not a duplicate of it.

**Where it fits**: same as 2a — doc 24 Phase 3, when the Screener UI is actually built. This is a strong fit for doc 02's already-locked "explainability" release gate ("interpreted criteria + definitions visible") — it's the same idea applied to *results*, not just the *interpreted query*. Flagging here so it isn't lost by the time Phase 3 starts; no code change needed today since `apps/app` doesn't exist yet.

### 2c. Per-datapoint display convention: current value + trend + delta-vs-last-period + percentile

Doc 17 already shows current value + source + period. "Delta vs. last quarter/year" and "sector percentile" are two additional display fields the study proposes per datapoint. Delta-vs-last-period is cheap (the data's already in `metric_value` across periods, it's a display computation, not new data). Percentile requires the wider-universe gap already named in doc 26 Tier 4 — genuinely blocked, not new.

## 3. The one real open question

The study ends by asking which investing decision the product should optimize its **first user-facing screen** for: **long-term compounders**, **undervalued cash-generative companies**, or **fast-growing companies before earnings accelerate**. This is a real product-positioning call doc 02 doesn't currently answer, and it isn't decidable from data or precedent — it's the founder's call. Added as an open item in doc 02 (below); not resolved by this doc.

## 4. Nothing built as part of this doc

Consistent with doc 21/22/23's convention: this is a scoping/gap-analysis doc, not an execution plan. No schema, code, or UI changed. The two actionable items (2a, 2b) are UX design inputs for doc 24 Phase 3 when that phase actually starts, not standalone tasks — building either in isolation, with no Screener UI to attach them to, would be premature.
