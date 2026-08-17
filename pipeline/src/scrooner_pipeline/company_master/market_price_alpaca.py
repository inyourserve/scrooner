"""Real market-price ingestion via Alpaca (doc 25). Company Master 4b's
real-data follow-on, now that doc 02's vendor decision is resolved.

Writes to core.market_price_alpaca -- a table genuinely separate from
core.market_price (mock data, doc 13 Part 4b), by explicit user
direction, not the is_mock-flag-on-one-shared-table design that
module's own docstring originally proposed. Mock and real data can
never land in the same table here, let alone the same row.

This module ingests price only -- it must NOT compute Market Cap, P/E,
or any other price-dependent metric. That stays the Mapper's job even
once real prices are available (doc 13's own locked boundary rule,
unchanged by which vendor supplies the price).

Primary ticker source: the caller passes an explicit {cik: ticker} map
(the golden_companies.json file's own curated "ticker" field), NOT a
generic core.listing query -- found live, the hard way, that core.listing
holds every listing a company has ever had, not just its primary common
stock: JPM alone has 9 rows (5 preferred-share classes plus several
structured-note tickers it issues under its own CIK, same "one CIK, many
securities" pattern doc 23 already found for Form 15), ENB has 14 (OTC
pink-sheet variants of the same Canadian listing). A naive
{cik: ticker for ...} dict comprehension over that silently kept
whichever row postgres happened to return last -- wrong tickers (a JPM
ETN called "VYLD", not JPM's own common stock) got queried instead of
the real one. core.listing has no "is primary" flag to resolve this
generically yet -- a real design gap for any future wider universe, not
solved here, correctly scoped to the golden-10's already-known-correct
tickers for now.
"""

from datetime import date, datetime

import psycopg
import structlog

from scrooner_pipeline.common.alpaca_client import FEED, AlpacaClient

logger = structlog.get_logger()


def update_market_price(conn: psycopg.Connection, ticker_by_cik: dict[str, str]) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ticker_by_cik),))
        company_id_by_cik = dict(cur.fetchall())

    ticker_to_company_id = {
        ticker: company_id_by_cik[cik] for cik, ticker in ticker_by_cik.items() if cik in company_id_by_cik
    }
    stats = {
        "considered": len(ticker_by_cik),
        "no_company": len(ticker_by_cik) - len(ticker_to_company_id),
        "matched": 0,
        "no_bar": 0,
    }
    if not ticker_to_company_id:
        logger.warning("market_price_alpaca.no_companies")
        return stats

    with AlpacaClient() as alpaca:
        bars = alpaca.latest_bars(sorted(ticker_to_company_id))

    today = date.today()
    rows = []
    for ticker, bar in bars.items():
        company_id = ticker_to_company_id.get(ticker)
        if company_id is None:
            continue
        bar_timestamp = datetime.fromisoformat(bar["t"].replace("Z", "+00:00"))
        rows.append(
            {
                "company_id": company_id,
                "symbol": ticker,
                "price_date": today,
                "price": bar["c"],
                "bar_timestamp": bar_timestamp,
                "feed": FEED,
            }
        )
        stats["matched"] += 1
    stats["no_bar"] = len(ticker_to_company_id) - stats["matched"]

    if rows:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into core.market_price_alpaca
                    (company_id, symbol, price_date, price, bar_timestamp, feed)
                values
                    (%(company_id)s, %(symbol)s, %(price_date)s, %(price)s, %(bar_timestamp)s, %(feed)s)
                on conflict (company_id, price_date) do update
                    set price = excluded.price,
                        bar_timestamp = excluded.bar_timestamp,
                        symbol = excluded.symbol,
                        feed = excluded.feed,
                        fetched_at = now()
                """,
                rows,
            )
        conn.commit()

    logger.info("market_price_alpaca.done", **stats)
    return stats
