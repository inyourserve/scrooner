# 25 — Scrooner: Real Market-Price Integration (Alpaca) Execution Plan

Doc 02's market-price vendor decision resolved 2026-08-17: Alpaca Markets, free/Basic tier for now. This is the execution plan for Company Master 4b's real-data follow-on — the piece doc 13 deliberately left as a stub pending this exact decision. Built against the two endpoints requested for review, read directly (not from memory) and then live-tested against the real Alpaca account before this plan was written, same discipline as every prior vendor/API evaluation in this project.

> **Status:** Draft (2026-08-17) — a plan, not yet built. **Owner:** Founder / Product · **Review:** before implementation starts.

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
