# 25 — Scrooner: Real Market-Price Integration (Alpaca) Execution Plan

Doc 02's market-price vendor decision resolved 2026-08-17: Alpaca Markets, free/Basic tier for now. This is the execution plan for Company Master 4b's real-data follow-on — the piece doc 13 deliberately left as a stub pending this exact decision. Built against the two endpoints requested for review, read directly (not from memory) and then live-tested against the real Alpaca account before this plan was written, same discipline as every prior vendor/API evaluation in this project.

> **Status:** Built and verified against the golden-10 (2026-08-17). Original plan below is unchanged except where marked — three explicit user refinements (delayed_sip feed instead of iex, a genuinely separate table instead of `core.market_price`'s `is_mock` flag, daily/on-demand cadence for now) were incorporated during the build, and one real bug was found and fixed during verification (see §7). **Owner:** Founder / Product.

---

## 1. What was read and verified live

**`GET /v2/stocks/bars/latest`** (`stocklatestbars`) — batched, multi-symbol (`symbols=AAPL,MSFT,JPM`, comma-separated). Returns one OHLCV+VWAP bar per symbol, keyed by symbol, at whatever the most recent bar is. **`GET /v2/stocks/{symbol}/trades/latest`** (`stocklatesttradesingle`) — single-symbol, most recent individual trade tick.

Live-tested against the real Alpaca account (credentials now in `pipeline/.env`), not assumed from the docs alone:

```
GET /v2/stocks/bars/latest?symbols=AAPL,MSFT,JPM
X-Feed: iex
X-Ratelimit-Limit: 200
{"bars":{"JPM":{"c":364.99,...,"t":"2026-08-17T16:27:00Z"},
         "MSFT":{"c":482.875,...},
         "AAPL":{"c":303.51,...}}}
```

Confirmed, live, not from the docs alone:

- **Free/Basic-tier accounts default to the `feed=iex` data source**, not the full consolidated SIP tape — the `X-Feed: iex` response header confirms this directly. IEX is one real exchange (~2-3% of US equity volume), not the composite "last sale" price most retail tools show. Prices are usually very close to the consolidated tape but **not guaranteed identical** — this needs an honest label on the company page, the same discipline as doc 23's `EntityPublicFloat`-is-not-Market-Cap distinction.
- **Rate limit: 200 requests/minute** on this account (`X-Ratelimit-Limit: 200`), confirmed via response headers exactly as the docs described.
- **Bars are minute-granularity, not literally "end of day"** — the returned bar's timestamp (`t`) was the *current* minute during live market hours, not a prior day's close. Outside market hours, "latest" naturally returns the last bar from when the market was open — the timestamp itself is what makes this honest (no separate staleness flag needed, same principle as doc 04's "every number shows source, period, formula/version, data date").
- **Batching works exactly as documented**: 3 symbols in one call, one row each, correctly keyed. For the golden-10, this means **the entire universe's current prices are one API call.**
- **Neither endpoint provides historical/point-in-time prices** — both are "latest" only. A price chart or a historical-period market cap calculation is a real, separate gap, not covered by what was reviewed here (and already explicitly out of MVP scope per doc 17 §3's "no price chart").

## 2. What this actually unblocks

Checked against doc 02's V1 metric list: **all 6 price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield) only need the *current* price**, not a historical series — Market Cap = shares outstanding × current price; P/E = current price ÷ diluted EPS (TTM); P/S and P/B divide Market Cap by already-computed TTM figures; Dividend Yield and FCF Yield both divide an already-computed TTM figure by current price (or Market Cap). **`stocklatestbars` alone is sufficient for the full locked metric list** — no historical backfill needed for this phase.

## 3. Existing shape this plugs into, unchanged

`core.market_price` (migration 0006) already has the right shape for this — `(company_id, price_date, close_price, currency, source, is_mock)` — and `company_master/market_price.py`'s own docstring already wrote the swap-in contract before a vendor was chosen: *"write a new loader function with the same shape as `generate_mock_prices()`... clear this table's mock rows first... nothing downstream should ever need to change."* This plan follows that contract exactly rather than redesigning it.

## 4. Proposed build shape

1. **`common/alpaca_client.py`** — thin REST client, `APCA-API-KEY-ID`/`APCA-API-SECRET-KEY` headers (from `settings.alpaca_api_key`/`alpaca_api_secret`, already wired into `config.py`), same retry-on-transient-error shape as `common/sec_client.py`. Explicitly pass `feed=iex` on every request rather than relying on the implicit account-tier default — makes the free-tier limitation a visible line of code, not a silent behavior that changes if the account's plan ever changes.
2. **`company_master/market_price_alpaca.py`** — real loader, mirroring `market_price.py`'s per-company function shape: resolve each golden company's current ticker (`core.listing`, `effective_to is null`), batch all tickers into one `stocklatestbars` call, map results back to `company_id`, upsert into `core.market_price` with `source='alpaca'`, `is_mock=false`. Before inserting: `delete from core.market_price where company_id = any(...) and is_mock = true` — doc 13's own stated procedure, mock and real must never coexist for the same company/date.
3. **CLI command** in `jobs/company_master.py` (`update-market-price` or similar), same pattern as `load-mock-prices`.
4. **Company page**: replace the currently-null price-dependent top-ratio fields once the Mapper follow-on (next item) computes them — and label the price source explicitly (e.g. "IEX real-time" with the bar's own timestamp), never presented as an official consolidated last-sale price.

## 5. What this plan deliberately does NOT do

- **Does not compute Market Cap/P/E/P/S/P/B/Dividend Yield/FCF Yield.** That's the Mapper's job per doc 13's own locked boundary rule ("Company Master must not calculate Market Cap/P/E/... — Mapper's job even once 4b supplies the missing price input"), and is its own separate, still-not-built follow-on task, already named everywhere else in this project (doc 09b, doc 20, root `CLAUDE.md`). This plan only gets real prices into `core.market_price`.
- **Does not add historical price backfill or a price chart** — not covered by the two endpoints reviewed, and price charts are already explicitly out of MVP scope (doc 17 §3).
- **Does not silently upgrade past the free/IEX tier.** If SIP (full consolidated tape) is ever needed, that's a real cost decision for the user to make, not something this plan assumes.

## 6. Open question for the user, not assumed here

**Refresh cadence isn't decided.** Given the rate-limit headroom (200 req/min, 1 call covers the whole golden-10), this could run once a day, on every company-page request, or on some other cadence — a product/cost trade-off (more frequent = closer to "live" but more calls against the free-tier limit as the universe grows), not a technical constraint. Worth a explicit decision before building, not defaulted here.

**Resolved by explicit user direction, same day**: `feed=delayed_sip` (not the free-tier default `iex`) — confirmed live before building: real ~15-16 minute delay (bar timestamp vs. request time), and full consolidated-tape trade counts (10-70x higher than IEX in a live side-by-side check), a better fit for a fundamental screener than real-time-but-single-exchange data. **Separate table** (`core.market_price_alpaca`, not `core.market_price` with `is_mock=false`) — mock and real data can never coexist in the same table at all now, a stronger guarantee than a boolean flag. **Cadence: once daily or on-demand, for now, during dev** — no scheduler built (Part 14/Infra's hosting decision is still open); the CLI command (`scrooner-company-master update-market-price`) is runnable both ways today.

## 7. Built shape (as implemented, not just proposed)

- `db/migrations/0012_market_price_alpaca.sql` — `core.market_price_alpaca`, one row per `(company_id, price_date)`, includes the bar's own `bar_timestamp` (not just `fetched_at`) so real data recency is always checkable, not just claimed.
- `common/alpaca_client.py` — thin client, `feed=delayed_sip` hard-coded (not left to account-tier default).
- `company_master/market_price_alpaca.py` — the loader. Ingests price only, same locked boundary as doc 13 (never computes Market Cap/P/E/etc.).
- CLI: `scrooner-company-master update-market-price`.

**One real bug found and fixed during verification, not before**: the first version resolved each company's ticker via a generic `core.listing` query, building a `{cik: ticker}` dict — but `core.listing` holds *every* listing a company has ever had, not just its primary common stock. JPM alone has 9 rows (5 preferred-share classes plus several structured notes/ETNs it issues under its own CIK — the same "one CIK, many securities" pattern doc 23 already found for Form 15/Chase Capital), ENB has 14 (OTC pink-sheet variants). The dict comprehension silently kept whichever row Postgres returned last, so the first live run queried Alpaca for things like "VYLD" (a JPM-issued ETN) instead of "JPM" itself — 3 of 10 companies got no bar back at all, and the 7 that did included wrong tickers for JPM and Alphabet. Fixed by sourcing the primary ticker from `golden_companies.json`'s own already-curated `ticker` field instead of querying `core.listing` generically — correct for all 10 on rerun. `core.listing` has no "is primary" flag to solve this for a wider universe yet; correctly left as a known, named gap rather than guessed at, same discipline as everywhere else in this project.

**Verified real values, golden-10, 2026-08-17 ~16:20 UTC**: AAPL $303.69, MSFT $483.37, JPM $365.04, GOOGL $344.34, TSM $435.40 — all plausible, all with a real `bar_timestamp` roughly 15-20 minutes behind the request, confirming the delayed_sip feed is working as designed, not silently falling back to something else.

## 8. Follow-up: the golden-file ticker stopgap replaced with real classification

The fix in §7 (source the primary ticker from `golden_companies.json`) was explicitly a stopgap, named as such at the time. By user direction, replaced same-day with a real, general mechanism — **explicitly not using Alpaca for this**, to keep the price vendor's role scoped to price only:

- New `company_master/security_type.py` classifies every current listing via **OpenFIGI** (free, unauthenticated, already proven for Ownership Stage 4's CUSIP crosswalk) — `idType=TICKER` mapping, storing OpenFIGI's own raw `securityType` string (`"Common Stock"`, `"ADR"`, `"ETP"`, `"CDI"`, etc.) verbatim in a new `core.listing.security_type` column. A `NULL` means no OpenFIGI match under a plain US query, treated as inconclusive, never as a negative signal.
- Checked live across the **full** golden-10 (38 listings, not a sample) before trusting this: JPM's 2 ETNs correctly classify as `"ETP"`, Block's Australian CDI as `"CDI"`, all 13 of Enbridge's Canadian preferred-share OTC tickers return no match at all (OpenFIGI simply doesn't cover them under a US query) — none of them get misclassified as primary.
- **One real nuance found only by checking all 10, not the first few**: TSM's own actual working ticker classifies as `"ADR"` (American Depositary Receipt), not `"Common Stock"` — a naive Common-Stock-only filter would have wrongly excluded the one ticker this pipeline actually needs. `PRIMARY_SECURITY_TYPES = {"Common Stock", "ADR"}` in `security_type.py` accounts for this.
- 8 of 10 companies resolve to exactly one `Common Stock`/`ADR` listing, unambiguous. 2 have **more than one legitimately valid candidate** — not a data error: Alphabet's GOOGL (Class A) and GOOG (Class C) are both real common stock; TSM (the ADR) and TSMWF (the underlying ordinary shares, OTC) are both real primary securities for the same company. `resolve_primary_tickers()` breaks this tie using `golden_companies.json`'s own curated choice — now a small, secondary role, not the primary source of truth it was in §7.
- A second real, live-caught bug during this build: OpenFIGI's real unauthenticated rate limit is tighter than its own headline "~5,000/day" figure suggests — a 0.3s request pace produced real HTTP 429s. Fixed with a 1.5s pace plus exponential-backoff retry on 429 specifically.
- `market_price_alpaca.py`'s ticker resolution now calls `resolve_primary_tickers()` instead of taking a bare `{cik: ticker}` dict from the caller — re-verified end to end afterward: all 10 golden companies still resolve to the correct real ticker, including both tie-break cases (GOOGL not GOOG, TSM not TSMWF).
