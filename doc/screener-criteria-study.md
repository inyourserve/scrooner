# What a Great Investor Wants in a Stock Screener — A Complete Study

**Purpose:** `us-investor-data-points.md` defines what belongs on a *company page*. This
doc answers the narrower, harder question: of all that data, what makes a **screener**
(the filtering/discovery tool) actually good — the criteria to filter on, the UX that
makes filtering powerful, the presets serious investors reach for on day one, and the
data-integrity traps that make most free screeners untrustworthy. Written from the seat
of someone who actually screens for a living (value, quality, and GARP style), not a
feature checklist.

---

## 1. The core insight: a screener is not "the company page with sliders"

Most screener side-projects fail here. They take every metric from the company page and
turn it into a filter, which produces a wall of 80 sliders nobody uses. A screener that
investors actually adopt does three things a static company page doesn't:

1. **Lets you express an investment thesis as a query**, not a metric-by-metric hunt.
   ("Show me profitable companies growing revenue >15%/yr, trading below their 5-year
   average P/E, with no debt.") The query *is* the product — Screener.in's biggest single
   differentiator over Finviz is exactly this: a saved formula, not a form.
2. **Ranks and compares across the *whole market* on a common basis**, not one company at
   a time. This means every filterable field must be normalized/comparable — same fiscal
   period alignment, same currency, same TTM vs. FY convention — across thousands of
   tickers simultaneously. This is a harder data problem than the company page.
3. **Is reusable and shareable.** A one-off filter session is a toy. A *saved, named,
   shareable screen* that re-runs against fresh data every day is a tool people come back
   to — and, per SEO strategy, a public shareable screen page is also a growth channel.

So this study is organized around: (A) what to filter on, (B) how filtering should work,
(C) what screens to ship pre-built, (D) the data-integrity issues unique to screening,
(E) an MVP cut.

---

## 2. Filter categories (what to filter on)

Cross-referenced against `us-investor-data-points.md`. Marked **screen** (good filter
candidate — a number you'd set a threshold on), **display-only** (belongs on the company
page but rarely filtered directly), or **derived** (computed specifically for screening,
not a raw fundamental).

### 2.1 Valuation — the most-used filter category
| Filter | Type | Notes |
|---|---|---|
| P/E (trailing, forward) | screen | Include negative-earnings handling (exclude vs. flag, don't silently drop) |
| PEG ratio | screen | Growth-adjusted — high-signal for GARP investors |
| EV/EBITDA | screen | Preferred over P/E for capital-structure-neutral comparison |
| EV/Sales, Price/Sales | screen | Essential for unprofitable growth names (can't use P/E) |
| Price/Book | screen | Still core for financials/asset-heavy sectors |
| Price/FCF, FCF Yield | screen | The metric serious value/quality investors weight most |
| Valuation vs. own 5–10yr history (percentile) | derived | "Cheap relative to itself" — very high value, rarely offered by free tools |
| Valuation vs. sector/peer median | derived | "Cheap relative to peers" — complements the above |

### 2.2 Quality & Profitability
| Filter | Type | Notes |
|---|---|---|
| Gross / Operating / Net Margin | screen | Filter on level AND trend (expanding vs. compressing) |
| ROE, ROIC, ROA | screen | ROIC is the one serious quality investors screen on first |
| Margin trend flag (3yr direction) | derived | "expanding margins" as a boolean filter — big UX win |
| Piotroski F-Score (0–9) | derived | Composite quality/financial-strength score, screenable as a single number |

### 2.3 Growth
| Filter | Type | Notes |
|---|---|---|
| Revenue growth (1/3/5/10yr CAGR) | screen | Offer multiple horizons — a filter locked to one period misses consistency |
| EPS growth (1/3/5/10yr CAGR) | screen | |
| FCF growth (3/5yr CAGR) | screen | |
| Growth consistency (e.g., % of last N years with positive growth) | derived | Screens out "one great year" false positives |
| Forward growth estimate (next FY) | screen | Requires vendor data (see vendor-data-study.md) |

### 2.4 Financial Health / Safety
| Filter | Type | Notes |
|---|---|---|
| Debt/Equity, Net Debt/EBITDA | screen | Core "will this survive a downturn" filter |
| Interest Coverage | screen | |
| Current Ratio, Quick Ratio | screen | |
| Altman Z-Score | derived | Composite bankruptcy-risk score — high-value single-number filter |
| Cash & equivalents / Market Cap | derived | "Net cash" screens (popular deep-value/net-net screen type) |

### 2.5 Capital Allocation & Shareholder Returns
| Filter | Type | Notes |
|---|---|---|
| Dividend Yield | screen | |
| Dividend growth streak (years) | screen | Powers "Dividend Aristocrat"-style screens |
| Buyback yield | screen | |
| Total shareholder yield (div + buyback − dilution) | derived | Better single filter than yield alone |
| Share count trend (dilution vs. buyback, 5yr) | screen | Filter for "not diluting me" |
| Payout ratio | screen | Sustainability check on the dividend |

### 2.6 Ownership / Insider Signal
| Filter | Type | Notes |
|---|---|---|
| Insider buying (net, last 6mo) | screen | High-signal, rare on free screeners — real differentiator |
| Institutional ownership % | screen | Both "high conviction" and "under-owned/undiscovered" screens use this |
| Institutional ownership trend (QoQ) | screen | Rising institutional ownership as a momentum-adjacent filter |
| Short interest % of float | screen | Needs FINRA data per vendor-data-study.md |

### 2.7 Price / Technical (light touch — not the product's core, but expected)
| Filter | Type | Notes |
|---|---|---|
| Market cap band | screen | Universe-defining filter, nearly always used first |
| 52-week high/low proximity | screen | "Near 52wk low" is a classic value-screener filter |
| Price change (1M/3M/6M/1Y) | screen | Momentum overlay, popular even among fundamentals investors as a *timing* filter |
| Beta | screen | Risk-tolerance filter |
| Average volume / liquidity floor | screen | Practical filter — excludes untradeable micro-caps |

### 2.8 Classification / Universe
| Filter | Type | Notes |
|---|---|---|
| Sector / Industry (SIC-based, mapped to friendly buckets) | screen | Nearly always combined with other filters |
| Exchange (NYSE/NASDAQ) | screen | |
| Index membership (S&P 500 / 400 / 600, Russell) | screen | Popular universe-narrowing filter; needs an index-membership data source |
| Country of incorporation / HQ | screen | For investors who care about domicile/ADR structure |

### 2.9 Business Quality Flags (auto-generated, boolean filters)
This is where Screener.in's "pros/cons" concept becomes literally filterable rather than
just descriptive:
- "FCF > Net Income" (earnings quality flag)
- "SBC < X% of revenue" (dilution discipline)
- "No debt" / "Net cash position"
- "Profitable every year for 10 years" (survivor quality)
- "Margins expanding 3 years running"
- "Insider buying, no insider selling, last 6 months"

These composite boolean flags are cheap to compute (all derived from data already in the
pipeline) and are disproportionately valuable in the UI — they let a novice screener
build a good screen without knowing what threshold to type into 10 separate number boxes.

---

## 3. How filtering should work (the mechanics that separate a good screener from a bad one)

1. **Two modes, one engine:** a guided builder (pick metric → operator → value, chip-based,
   like Screener.in and Finviz) for most users, *and* a raw query/formula mode (type
   `ROE > 15 AND DebtToEquity < 0.5 AND PE < Sector_PE_Median`) for power users. Screener.in's
   query language is the single most-cited "why I switched to Screener.in" feature among
   its users — this is not optional if the goal is to out-power Finviz.
2. **Natural-language entry** ("profitable small caps growing revenue over 20% a year")
   that compiles down to the same structured query — per the "What we're building" doc,
   this is explicitly part of the differentiation thesis, so the underlying filter engine
   needs to be structured/composable enough that an LLM layer can reliably translate into
   it (this argues for a well-typed query DSL under the hood, not ad hoc SQL string building).
3. **AND/OR/NOT composition, not just AND-of-ranges.** Real theses need "high margin OR
   high growth" logic sometimes, not only "all conditions true."
4. **Relative/dynamic thresholds, not just absolute numbers.** "P/E below sector median,"
   "margin above 5-year own average," "growth accelerating vs. prior period" — these
   require the filter engine to reference computed baselines (sector medians, historical
   percentiles), not just a static column value. This is exactly the kind of filter EDGAR's
   raw data can't give you out of the box — it's the derived-metrics layer that becomes the
   real product moat.
5. **Sortable, customizable results table** — every filter field should also be a
   selectable/sortable output column, with the ability to save a custom column set per
   screen (Screener.in does this well; most competitors bury results behind fixed columns).
6. **Save, name, and share screens** as a public URL — this is both a UX feature and,
   per the SEO thesis in "What we're building," a distribution mechanism: public screen
   pages get indexed and pull in organic search traffic the same way company pages do.
7. **Alerts on screen membership changes** ("notify me when a stock newly enters this
   screen") — P1/P2, but a strong retention hook once someone has a saved screen they trust.
8. **Point-in-time correctness (critical, easy to get wrong):** a screen run today should
   filter on data *as it would have been known at that time* if ever used for backtesting,
   and should always use the *latest available/restated* figures for live screening. Mixing
   these up either produces look-ahead bias (in a backtest feature) or shows stale numbers
   (in live screening). See Section 5.
9. **Explain the miss, not just the hit.** When a stock is *close* to matching a screen but
   fails on one criterion, surfacing "would match except ROIC is 11%, you required 12%" is a
   small feature with an outsized trust payoff — it signals the tool understands nuance
   rather than being a blunt filter.
10. **Backtesting a screen (P2, high differentiation).** "If I had run this screen every
    quarter for the last 10 years, what would the return have been?" is a premium, high-value
    feature (this is what tools like Portfolio123 charge real money for) — flag as a
    post-MVP monetization lever, not a v1 requirement, but worth designing the data model
    to not preclude later (i.e., keep historical point-in-time snapshots from day one even
    if the backtest UI ships later).

---

## 4. Pre-built / preset screens to ship (the "screener needs a starting point" problem)

A blank screener with 50 filters is intimidating. Every well-loved screener ships famous,
named, one-click starting screens. Recommended launch set, roughly in order of investor
familiarity:

| Preset | Logic sketch | Audience |
|---|---|---|
| **Magic Formula (Greenblatt)** | Rank by high ROIC + high earnings yield (EBIT/EV), combined rank | Value/quant investors |
| **Piotroski F-Score ≥ 8** | 9-point fundamental strength score, high threshold | Deep value screeners |
| **Graham Defensive/Enterprising criteria** | P/E, P/B, current ratio, earnings stability thresholds | Classic value investors |
| **Quality Compounders** | ROIC > 15%, 10yr consistent profitability, low debt, margin expansion | Buffett/Munger-style investors |
| **Dividend Growth / "Aristocrats-lite"** | 10+ yr consecutive dividend growth, payout ratio < 60% | Income investors |
| **Net-Net / Deep Value** | Price below net current asset value | Classic Graham deep value |
| **GARP (Growth at a Reasonable Price)** | PEG < 1, revenue growth > 15%, positive FCF | Growth-value blend |
| **High FCF Yield, Low Debt** | FCF yield > X%, Debt/Equity < X | Screener's own quality-cash thesis (ties directly to Section 4 of the data-points doc) |
| **52-Week Low, Still Profitable** | Near 52wk low, positive earnings, positive FCF | Contrarian/turnaround hunters |
| **Insider Buying Cluster** | 3+ insiders buying, no sales, last 3 months | Signal-following investors |
| **Small-Cap Momentum + Quality** | Market cap band, positive price momentum, ROE > 15% | GARP/momentum blend |

Each preset should be **editable, not fixed** — clicking a preset should load it into the
query builder so a user can start from Magic Formula and then tighten one threshold,
rather than treating presets as opaque black boxes.

---

## 5. Data-integrity issues that are unique to screening (and that most free tools get wrong)

These don't show up on a single company page (where a human can sanity-check one number)
but silently corrupt results across thousands of tickers in a screener — this is where a
screener's credibility is actually won or lost:

1. **Survivorship bias in the universe.** If delisted/bankrupt/acquired companies quietly
   drop out of the trackable universe, historical screens and backtests look artificially
   good. The universe needs to retain delisted tickers with a status flag, not delete them.
2. **Look-ahead bias in fundamentals.** A 10-K for fiscal year 2025 isn't public/known
   until it's filed (weeks/months after fiscal year-end). A backtest or "as of" screen must
   use the filing date, not the fiscal period end date, as the point at which a fact becomes
   knowable — this is a subtle but critical distinction EDGAR's own timestamps support
   (filing accepted date vs. period of report) but many simple pipelines conflate.
3. **Restatements.** When a company restates prior financials (10-K/A), a screener needs a
   policy: does the "as reported at the time" value stay in historical screens/backtests,
   while the "current" company page shows the restated number? Silently overwriting history
   with restated values breaks backtest integrity.
4. **Fiscal year misalignment.** Not every company's fiscal year ends in December. "TTM"
   and "latest FY" must be computed consistently across companies with different fiscal
   calendars, or cross-company screens will implicitly compare different time windows.
5. **Currency and units.** Rare for EDGAR filers (mostly USD) but foreign private issuers
   and ADRs can complicate this — needs explicit handling, not an assumption.
6. **Missing-data handling.** A screen filter on "ROIC > 15%" needs a defined behavior for
   companies where the required tag simply wasn't reported (non-standard XBRL extension
   tags, financial-sector companies with different statement structures) — silently
   excluding them skews results toward "easy to parse" companies (which correlates with
   company type, not quality) rather than the "true" universe.
7. **Negative-denominator ratios.** P/E with negative earnings, PEG with negative growth,
   etc. need explicit UI treatment (e.g., "N/M" not a nonsensical negative multiple) —
   naively computed, these actively mislead screens (a company with a huge loss can show a
   "cheap" negative or tiny positive P/E depending on sign handling).
8. **Sector-relative filters need a real, current sector map.** SIC codes are old and
   coarse (per vendor-data-study.md); a "cheap vs. sector" filter is only as good as the
   sector bucket it's compared against — the internal SIC→bucket mapping table quality
   directly determines this filter's usefulness.

---

## 6. MVP cut (P0) vs. later (P1/P2)

Following the priority discipline already established in `us-investor-data-points.md`:

**P0 — ship in v1:**
Market cap band, sector/industry, P/E (trailing), EV/EBITDA, Price/Sales, Price/Book, FCF
yield, gross/operating/net margin, ROE, ROIC, revenue growth (3/5yr CAGR), EPS growth
(3/5yr CAGR), Debt/Equity, current ratio, dividend yield, dividend growth streak, buyback
yield, insider buying flag, 52-week high/low proximity, basic AND-of-ranges query builder,
save/name/share a screen, sortable customizable results table, 4–5 launch presets (Magic
Formula, Quality Compounders, Dividend Growth, Deep Value, GARP).

**P1 — strong differentiator, soon after launch:**
Valuation vs. own 5–10yr history, valuation vs. sector median, margin trend flag, growth
consistency score, total shareholder yield, institutional ownership + trend, short
interest, OR/NOT logic and raw query/formula mode, natural-language query entry, "near
miss" explanation on results, alerts on screen membership changes.

**P2 — premium/advanced:**
Piotroski F-Score, Altman Z-Score, index-membership filters, screen backtesting, and any
filter that depends on a paid vendor feed the vendor-data-study.md doc flags as P2
(short-interest days-to-cover, forward-estimate-based filters if a cheaper vendor tier
doesn't cover them).

---

## 7. How this beats the incumbents specifically

- **vs. Finviz:** Finviz has more raw filters but almost no derived/composite ones (no
  relative-to-history valuation, no quality-flag booleans, no query language beyond basic
  AND-of-ranges) and a dated, dense UI. The win isn't filter *count*, it's filter
  *intelligence* and readability.
- **vs. Stock Rover:** Stock Rover is powerful but admittedly has a steep learning curve
  ("weeks to learn," per the product thesis doc). The guided builder + presets + plain-
  language explanations of what each filter means is the wedge — power without the ramp.
- **vs. broker-bundled screeners:** These are generally shallow (price/valuation only, no
  quality/cash-flow/ownership signals) and exist to keep users inside the broker, not to be
  genuinely good. Depth on the FCF-quality, capital-allocation, and insider-signal filters
  (Sections 2.3–2.6 above) — all free from EDGAR — is where this product can be strictly
  better with zero data-cost disadvantage.

---

## 8. The monetization angle: what people actually pay for in a screener

Per "What we are building," the model is free core + premium subscription + broker
affiliate + ads + B2B API, with $10k/month (~1,000 subscribers) as the first real
milestone. A screener is one of the two crown-jewel surfaces (alongside company pages),
so it's worth being explicit about which *parts of the screener itself* are the paywall,
not just "screener is free, something else is paid." Evidence from how Screener.in,
Finviz, and Stock Rover actually monetize, mapped onto the filter/feature list above:

### 8.1 What stays free (and should — this is the trust/growth engine)
- The full guided filter builder, using every P0/P1 filter in Section 2.
- All the named presets (Magic Formula, Piotroski, Deep Value, etc.) — these are
  marketing surfaces as much as features; gating them kills the "aha" moment that gets
  someone to make an account at all.
- A reasonable number of saved screens (e.g., 3–5) and public/shareable screen pages —
  the shareable public screen is an SEO growth channel per the product thesis, so gating
  it away would cut off the exact distribution loop the business depends on.
- Basic sort/filter on the results table.

Screener.in itself proves this model: the screener and company pages are entirely free,
and it still converts a small % to a paid tier for depth/export/automation — the lesson
being that people don't pay to unlock *filtering*, they pay to unlock *leverage on top of*
filtering they've already gotten hooked on.

### 8.2 What's genuinely worth paying for (ranked by observed willingness-to-pay)

| Feature | Why people pay | Precedent |
|---|---|---|
| **Unlimited saved/tracked screens + run-on-schedule alerts** ("email me daily when a new stock enters this screen") | Turns a one-time query into a standing research process — this is a retention/habit feature, and habit is what converts free→paid | Screener.in Premium, Finviz Elite alerts |
| **Raw query/formula mode + relative/dynamic thresholds** (valuation vs. own history, vs. sector median) | Power users — the exact audience most likely to pay — explicitly seek this; it's the single most-requested feature type in Screener.in's own community | Screener.in's custom-query formula screen is a paid-tier-adjacent power feature |
| **Export to Excel/CSV/Google Sheets, bulk data export** | Analysts and semi-professional investors build their own models downstream; this is the single highest-converting premium feature across nearly every competitor (Finviz Elite, Stock Rover, Simply Wall St) | Universal pattern |
| **Composite scores (Piotroski, Altman Z, custom quality score) as filterable/sortable fields** | These are computationally/IP-differentiated — not something a free EDGAR pull gives you directly — so it's defensible to gate | New score types are Stock Rover's main premium hook |
| **Backtesting a screen** | High perceived value ("what would this have returned"), expensive to compute well (needs point-in-time snapshots), and a feature that mostly matters to already-serious investors — natural premium ceiling feature | Portfolio123, Stock Rover Pro charge specifically for this |
| **Real-time/faster data refresh** (vs. end-of-day for free tier) | Classic freemium lever — doesn't require new data sources, just a refresh-cadence gate | Finviz Elite's core pitch is largely "real-time, not delayed" |
| **Ownership/insider filters at full depth** (e.g., full institutional holder list, not just aggregate %) | High-signal, EDGAR-sourced so cheap to produce, but niche enough (only serious investors dig this deep) that gating depth (vs. gating existence) works well | Matches the doc's existing P0 "flag exists free / P2 full detail" pattern |
| **API access to screener results** | This *is* the B2B data API revenue stream from the product thesis — screener queries become a paid programmatic endpoint for other builders (fintech apps, newsletter writers, RIAs) | Distinct revenue line, not just a subscription tier |
| **No ads on results/screen pages** | Simple, low-effort premium lever once ads exist on the free tier | Universal freemium pattern |

### 8.3 What's *not* worth gating (common mistake to avoid)
- Don't gate core filter *breadth* (number of filters available) — this is what Finviz
  does with its Elite tier and it's the most-criticized part of their pricing; it makes
  the free product feel deliberately crippled rather than genuinely useful, which
  undermines the trust-first positioning that's the whole differentiation thesis here.
- Don't gate the presets — they're the on-ramp, not the destination.
- Don't gate "how many results you can see" below a usable threshold (e.g., capping at 10
  rows) — this reads as bait-and-switch, not freemium, and actively damages the trust moat.

### 8.4 A concrete tiering sketch (directional, not final pricing)
- **Free:** full filter builder + all presets + up to ~5 saved screens + public sharing +
  basic sort/export limits (e.g., view-only, no CSV).
- **Premium (the $10k/mo-milestone tier):** unlimited saved screens + alerts on screen
  membership changes + raw query/formula mode + relative/dynamic threshold filters +
  composite scores (Piotroski/Altman) + CSV/Sheets export + real-time refresh.
- **Pro/advanced (later, smaller but higher-ARPU segment):** backtesting + full
  institutional-ownership drill-down + priority data refresh + higher API rate limits.
- **B2B API:** separate SKU entirely — sell programmatic access to screener query results
  and the underlying normalized dataset, billed by usage, aimed at other builders rather
  than end investors.

The throughline: gate **leverage, automation, and export**, not **insight**. An investor
should be able to fully evaluate whether the screener is trustworthy and useful for free —
paying should feel like "graduating" to a workflow tool, not "unlocking the real product."

---

## Summary

A great screener is not "every metric as a slider." It's: (1) a well-chosen, prioritized
set of raw and derived filters — with quality/cash-flow/insider signals as the real
differentiators, since those are free from EDGAR and rarely done well elsewhere; (2) a
query engine expressive enough for AND/OR logic, relative/dynamic thresholds, and eventual
natural-language entry; (3) a small set of named, editable, credible preset screens so the
tool is useful on day one, not just to power users; and (4) rigorous point-in-time data
handling so results — and any future backtests — are actually trustworthy, which is the
thing that turns a screener into a *daily* tool rather than a novelty.
