# yfinance — Deep Study & Usage Plan for Screener

**Status: Draft v1.0, partially superseded 2026-09-06 — see doc 02's decision register.** This doc's core recommendation (dev-tool/offline-cross-check only, §3, never stored or shown to a user, §4) was the basis for the initial 2026-09-06 fix (a hand-curated SIC-override informed by a one-time yfinance lookup, never persisted — `doc/learnings/2026-09-06-sic-catchall-peer-comparison-fix.md`). Later the same day, by explicit founder direction after the ToS tradeoff was surfaced directly, that recommendation was knowingly overridden for one specific use: `core.company.y_sector`/`y_industry` are now real, persisted, production-facing columns (`company_master/yfinance_industry.py`), backfilled for the full active population. Sections 2-4 below (the ToS/reliability risk analysis) remain accurate background — they were read and the risk was accepted anyway, not found to be wrong.
**Companion to:** `vendor-data-study.md` (primary vendor decision), `edgar-python-plugin-usage.md`
(verification-layer precedent), `us-investor-data-points.md` (the gap list this study is
evaluated against)

This doc answers: given `vendor-data-study.md` already picked FMP (pending a Commercial
quote) as the paid vendor for the gaps EDGAR can't cover, **where — if anywhere — does
the free, open-source `yfinance` Python library add value to Screener?**

Short answer up front: yfinance is a genuinely useful *tool*, but it is not a candidate
to replace or supplement FMP/Finnhub in production. It's an unofficial scraper of
Yahoo Finance's internal endpoints, Yahoo's own terms restrict the underlying data to
personal use, and the library breaks/rate-limits often enough that no production,
multi-user, revenue-generating page should depend on it. Its real value to us is the
same shape as EdgarTools' role: **dev-time prototyping and an offline cross-check
tool**, not a data source in the request path.

---

## 1. What yfinance actually is

- **Not an official API.** It's an open-source Python wrapper (Apache-2.0 licensed)
  that calls Yahoo Finance's internal/undocumented endpoints — the same ones the
  finance.yahoo.com website itself uses — and parses the JSON/HTML responses. There is
  no partnership or data-licensing agreement with Yahoo behind it.
- **The maintainers say so themselves.** The project's own README states it is "not
  affiliated, endorsed, or vetted by Yahoo, Inc." and tells users to review Yahoo's
  terms of service directly, noting the Yahoo Finance data "is intended for personal
  use only."
- **What it exposes (via the `Ticker` object), mapped to things we care about:**

  | Category | yfinance attribute(s) | Relevant to Screener section |
  |---|---|---|
  | Price/quote | `history()`, `fast_info` | Snapshot block, price charts |
  | Financial statements | `income_stmt`, `balance_sheet`, `cashflow` (+ quarterly/TTM variants) | Already sourced free from EDGAR — redundant for us |
  | Valuation | `get_valuation_measures()` (P/E, P/S, P/B, EV/EBITDA) | Cross-check for our computed multiples |
  | Analyst estimates | `analyst_price_targets`, `earnings_estimate`, `revenue_estimate`, `growth_estimates`, `eps_trend`, `eps_revisions` | Section 9 (Analyst & Market Sentiment) |
  | Ratings | `recommendations`, `recommendations_summary`, `upgrades_downgrades` | Section 9 |
  | Ownership | `major_holders`, `institutional_holders`, `insider_transactions`, `insider_purchases`, `insider_roster_holders`, `mutualfund_holders` | Section 8 — we already get this free from EDGAR Forms 4/13F |
  | Corporate actions | `dividends`, `splits`, `capital_gains`, `actions` | Section 1, 7 |
  | Earnings | `earnings_dates`, `earnings_history` (beat/miss) | Section 9 |
  | Company info | `info` (includes `sector`, `industry`, `shortRatio`, `sharesShort`, `shortPercentOfFloat`, `beta`, `52WeekChange`, etc.) | Sections 1, 5, 8, 12 |
  | ESG | `sustainability` | Not in our current data-points doc |
  | Options | `option_chain()` | Not in our current data-points doc |
  | News/filings | `news`, `sec_filings` | Section 13 (secondary source; we already pull filings from EDGAR directly) |
  | Sector taxonomy | `yf.Sector` / `yf.Industry` modules | Section 12 |

The breadth is real — on paper, `info` alone touches almost every gap in
`vendor-data-study.md`'s Section 1 gap table (price, beta, short interest all show up
here), plus most of Section 9 (analyst estimates/ratings). That's what makes it tempting
to look at twice. The rest of this doc is why "touches the gap" is not the same as
"safe to build on."

---

## 2. Why it's not a production candidate

### 2.1 Same license problem we already flagged for FMP Personal tier — worse

`vendor-data-study.md` Section 3.1 already established the pattern to watch for: a
vendor's cheap/free tier looks attractive until you read that it's restricted to
personal, non-commercial, single-user use, and Screener is unambiguously a commercial,
multi-user product. Yahoo's own terms apply exactly that restriction to the data
yfinance scrapes — and unlike FMP, there's no Commercial tier to upgrade into. There's
no paid plan, no contract, no path to compliant commercial use of this specific data
pipeline at all. Building any user-facing Screener page on yfinance data would carry
real, unresolved ToS risk for the life of that feature.

### 2.2 It breaks and gets rate-limited on a predictable cadence

This isn't a hypothetical risk — it's the library's most common open GitHub issue
category, and 2025–2026 examples turned up in this research show the pattern
continuing:

- Yahoo added stricter cookie/"crumb" authentication in 2024; the library has had
  repeated open issues since where Yahoo returns a bad or throttled crumb response
  (`crumb = 'Edge: Too Many Requests'`) that isn't even detected as an error properly
  ([issue #2441](https://github.com/ranaroussi/yfinance/issues/2441)).
- Fetching data for as few as ~25 tickers in a short window can trigger a `429 Too Many
  Requests` / `YFRateLimitError`, and the maintainers closed at least one such report
  as "not planned" — i.e., this is Yahoo's server-side throttling working as intended,
  not a bug they can fix ([issue #2288](https://github.com/ranaroussi/yfinance/issues/2288),
  [issue #2480](https://github.com/ranaroussi/yfinance/issues/2480)).
- Because there's no authenticated API contract, "any change on Yahoo's site can break
  yfinance" with no notice — new endpoint shapes, new auth requirements, or fields
  silently returning `None` for certain tickers
  ([Trading Dude, "Why yfinance Keeps Getting Blocked"](https://medium.com/@trading.dude/why-yfinance-keeps-getting-blocked-and-what-to-use-instead-92d84bb2cc01);
  [MarketXLS, "Yahoo Finance API: Complete Guide + Best Alternatives"](https://marketxls.com/blog/yahoo-finance-api-ultimate-guide)).
- Data is also 15–20 minutes delayed during market hours even when it does work — a
  non-issue for a fundamentals-first product like ours, but worth noting since it rules
  out any future real-time use case entirely.

For a screener that will hammer through hundreds or thousands of tickers on any given
sync job, this combination (personal-use-only terms + a scraper that Yahoo actively
throttles at moderate volume) is disqualifying for the production path — the same
"don't build tightly coupled to a fragile single source" lesson `vendor-data-study.md`
already drew from the IEX Cloud shutdown, just with a harder failure mode (legal, not
just operational).

### 2.3 It would also duplicate data we already have for free and trust more

Everything yfinance offers for financial statements, insider transactions, and
institutional ownership is data we already pull directly from the authoritative source
(EDGAR) per `us-investor-data-points.md` Section 14. Using yfinance for those would be
strictly worse (less authoritative, scraped, ToS-encumbered) with zero upside.

---

## 3. Where it does earn a place — dev-tool and offline cross-check only

This is the same architectural slot `edgar-python-plugin-usage.md` carved out for
EdgarTools: **never on the customer-facing request path, always offline/advisory.**
yfinance's specific value-adds on top of that pattern:

### 3.1 Pre-vendor-contract prototyping (highest near-term value)

`vendor-data-study.md` is explicit that the FMP Commercial price is still unconfirmed
and Finnhub is the fallback. Until that contract is signed, yfinance is a free way to:

- Build and iterate the actual UI/UX for the Snapshot block, analyst estimates panel,
  and short-interest display using **real, correctly-shaped data** instead of mocked
  JSON — so by the time FMP/Finnhub billing starts, the integration is a data-source
  swap behind an already-built adapter, not new development.
- Validate our internal data model for analyst estimates, price targets, and
  recommendation distributions against a real-world shape before committing to FMP's
  specific schema.

**Constraint:** this is local/dev-environment only, on a handful of well-known tickers
(AAPL, MSFT, etc.), never run against our full tracked universe, and nothing it touches
should reach a staging or production database that a real user could see.

### 3.2 Offline cross-check tool, same pattern as EdgarTools §3.1/3.5

Once FMP/Finnhub is live, yfinance's `analyst_price_targets`, `recommendations_summary`,
and `info` fields (`shortRatio`, `sharesShort`, `shortPercentOfFloat`, `beta`) can feed
a low-frequency, rotating-sample reconciliation job — the same discrepancy-log pattern
already defined for EdgarTools — to sanity-check that our paid vendor's numbers are in
the right ballpark. Treat mismatches as "investigate," not "yfinance is right," exactly
per the existing EdgarTools risk-mitigation principle, since yfinance is the less
authoritative source here, not a peer.

### 3.3 Free historical price backfill for beta computation, in dev only

`us-investor-data-points.md` flags Beta as "requires price history + computation, not a
disclosed fact" — a gap FMP/Massive is meant to fill. `yfinance.download()` /
`history()` gives free 5-year+ daily price history, good enough to prototype and unit-
test the beta-calculation logic itself (the math, not the production data feed) before
that logic is wired to the paid vendor's price series.

### 3.4 Secondary signal for sector/industry mapping — not a replacement for SIC

`vendor-data-study.md` Section 4 settled on SIC (from EDGAR, free) plus an internal
mapping table as the MVP sector taxonomy, deferring GICS licensing. Yahoo's own
`sector`/`industry` fields (and the `yf.Sector`/`yf.Industry` modules) use a taxonomy
that's structurally closer to GICS groupings than raw SIC is. This doesn't change the
Section 4 recommendation, but it's a useful **free reference point** when hand-building
the SIC → Screener-sector-bucket mapping table, to eyeball whether our buckets land
close to how GICS/Yahoo would group the same company.

### 3.5 Explicitly not pursuing

- **Options chains** (`option_chain()`) — not in our data-points doc at all; Screener
  is a fundamentals product, not an options tool. No action.
- **ESG/sustainability data** (`sustainability`) — not in our data-points doc. No
  action unless it becomes a scoped feature later.
- **News** (`news`) — we'd want a licensed news feed for anything user-facing anyway;
  not a yfinance use case.

---

## 4. Risk mitigation, if we do use it as a dev/cross-check tool

Carrying forward the same discipline `edgar-python-plugin-usage.md` §5 sets for
EdgarTools, with one addition specific to yfinance's sharper legal edge:

- **Never in the production dependency tree.** Not imported by any service that serves
  a user request, ever — enforce this the same way as the EdgarTools rule, not just as
  a convention.
- **Never run at scale.** Keep any cross-check job to a small rotating sample and
  respectful request pacing — the point is a sanity signal, not bulk collection, and
  running it like a bulk vendor invites exactly the rate-limiting/blocking behavior
  documented in Section 2.2.
- **Pin the version** and isolate its environment/container, same as EdgarTools —
  Yahoo-side breakage is more frequent here than SEC-side breakage is for EdgarTools,
  so treat failures as "expected, not urgent" rather than paging anyone.
- **Treat every yfinance-sourced number as unverified input, never as a fact stored in
  our database or shown to a user**, given the personal-use restriction — the
  discrepancy-log pattern (report only, human reviews, no auto-write) from
  `edgar-python-plugin-usage.md` §3.1 applies without exception.
- **No redistribution.** Don't expose any yfinance-derived value through our own
  (future) Data API product — that would turn an internal dev convenience into exactly
  the commercial-redistribution use Yahoo's terms are meant to prevent.

---

## 5. Recommendation

**Adopt yfinance narrowly, as a free dev-time prototyping and offline cross-check
tool — not as a data source, vendor, or fallback for any production feature.**

Concretely:

1. Use it now, in local dev, to prototype the analyst-estimates panel, short-interest
   display, and beta calculation UI/logic while the FMP Commercial quote is pending —
   so real work isn't blocked on vendor procurement timing.
2. Once FMP/Finnhub is live, stand up a low-frequency yfinance cross-check job
   alongside the existing EdgarTools reconciliation job, scoped to analyst
   estimates/targets, short-interest fields, and beta — the categories FMP is
   specifically being paid to provide — as an extra confidence signal on vendor data
   quality, at zero marginal cost.
3. Do not use it for anything EDGAR already gives us for free (financials, insider
   activity, institutional ownership) — no upside, same integration effort.
4. Do not let it anywhere near the production request path or the future Data API —
   the personal-use restriction in Yahoo's terms makes that a compliance risk, not just
   an operational one, and it's avoidable at zero cost by keeping the existing FMP/
   Finnhub plan as the only production source.

This keeps the existing `vendor-data-study.md` decision untouched while capturing real,
free value from yfinance in the two places it's actually safe to use it: speeding up
our own dev work, and adding a second pair of eyes on vendor data quality.

---

## 6. Summary table

| Use case | Frequency | Environment | Production-facing? |
|---|---|---|---|
| Pre-contract prototyping (§3.1) | Ad hoc, dev only | Local dev/notebook | No |
| Analyst estimates / short interest / beta cross-check (§3.2) | Low-frequency rotating sample, once FMP/Finnhub is live | Batch job, isolated | No — advisory only |
| Beta-calculation logic prototyping (§3.3) | Ad hoc, dev only | Local dev | No |
| Sector-mapping sanity reference (§3.4) | One-time, during mapping-table build | Local dev | No |
| Financials / insider / institutional data | — | — | **Not used** — EDGAR already covers this free |
| Options, ESG, news | — | — | **Not pursued** — outside current scope |

## Sources

- [ranaroussi/yfinance — GitHub](https://github.com/ranaroussi/yfinance)
- [yfinance.Ticker — reference docs](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.html)
- [Why yfinance Keeps Getting Blocked, and What to Use Instead — Trading Dude (Medium)](https://medium.com/@trading.dude/why-yfinance-keeps-getting-blocked-and-what-to-use-instead-92d84bb2cc01)
- [Yahoo Finance API: Complete Guide + Best Alternatives (2026) — MarketXLS](https://marketxls.com/blog/yahoo-finance-api-ultimate-guide)
- [Getting Rate limiter issue — GitHub Issue #2288](https://github.com/ranaroussi/yfinance/issues/2288)
- [New rate-limiting — GitHub Issue #2128](https://github.com/ranaroussi/yfinance/issues/2128)
- [YFRateLimitError: Too Many Requests — GitHub Issue #2480](https://github.com/ranaroussi/yfinance/issues/2480)
- [Yahoo may return bad crumb which is not detected properly — GitHub Issue #2441](https://github.com/ranaroussi/yfinance/issues/2441)