"""Stage 4b -- Market-price ingestion (doc 13). Built ahead of doc 02's
still-open market-price vendor decision, using MOCK data, so the rest of
the pipeline (and the eventual Mapper follow-on that computes the 6
price-dependent metrics) has something real to build and test against
without waiting on that decision.

THIS IS NOT REAL MARKET DATA. Every row this module writes carries
is_mock=true and source='mock' -- never a name that could be mistaken for
a real vendor. Swapping in a real vendor later means: (1) write a new
loader function with the same shape as generate_mock_prices() below,
returning real (company_id, price_date, close_price) rows with
is_mock=False and source=<real vendor name>; (2) clear this table's mock
rows first (delete where is_mock=true), don't let mock and real rows for
the same company/date coexist. Nothing downstream should ever need to
change -- core.market_price's shape doesn't depend on where the price
came from.

Base prices below are arbitrary, deliberately round, order-of-magnitude
placeholders -- not real historical quotes for these companies, not
sourced from anywhere, not to be read as accurate. A seeded random walk
from each gives a small, reproducible daily time series (same output on
every rerun for the same date range) so this stage's own idempotency can
be tested the same way every other stage in this project has been.
"""

import hashlib
from datetime import date, timedelta
from decimal import Decimal
from random import Random

import psycopg
import structlog

logger = structlog.get_logger()

MOCK_BASE_PRICE = {
    "0000019617": Decimal("210"),   # JPM
    "0000320187": Decimal("75"),    # NKE
    "0000320193": Decimal("220"),   # AAPL
    "0000789019": Decimal("430"),   # MSFT
    "0000895728": Decimal("45"),    # ENB
    "0001046179": Decimal("190"),   # TSM
    "0001287750": Decimal("21"),    # ARCC
    "0001512673": Decimal("75"),    # XYZ (Block)
    "0001652044": Decimal("175"),   # GOOGL
    "0001713445": Decimal("110"),   # RDDT
}

TRADING_DAYS = 30  # small, well-scoped -- enough to test the shape, not a full history


def _trading_dates(end_date: date, count: int) -> list[date]:
    """Weekdays only, ending at end_date, going backward -- a simple
    trading-day proxy, not a real market-calendar (no holiday awareness).
    Fine for mock data; a real vendor integration would use the vendor's
    own calendar instead."""
    dates: list[date] = []
    d = end_date
    while len(dates) < count:
        if d.weekday() < 5:  # Mon-Fri
            dates.append(d)
        d -= timedelta(days=1)
    return list(reversed(dates))


def generate_mock_prices(cik: str, end_date: date) -> list[dict]:
    if cik not in MOCK_BASE_PRICE:
        return []
    base = MOCK_BASE_PRICE[cik]
    # Seeded by (cik, end_date) so reruns for the same date produce the
    # same series -- idempotency for a generator, not just a writer.
    seed = int(hashlib.sha256(f"{cik}:{end_date.isoformat()}".encode()).hexdigest(), 16) % (2**32)
    rng = Random(seed)

    rows = []
    price = base
    for d in _trading_dates(end_date, TRADING_DAYS):
        # Small daily move, +/- 2% of the running price -- enough to look
        # like a real series, not modeling any real market behavior.
        pct_move = Decimal(rng.uniform(-2.0, 2.0)) / Decimal(100)
        price = (price * (Decimal(1) + pct_move)).quantize(Decimal("0.01"))
        if price <= 0:
            price = Decimal("0.01")
        rows.append({"price_date": d, "close_price": price})
    return rows


def load_mock_prices_for_company(conn: psycopg.Connection, company_id: int, cik: str, end_date: date) -> int:
    price_rows = generate_mock_prices(cik, end_date)
    if not price_rows:
        return 0
    with conn.cursor() as cur:
        # Delete-then-reinsert per company -- this project's established
        # default for idempotent per-company writes (see mapper/resolve.py,
        # mapper/calculate.py, company_master/history.py's own fix).
        cur.execute("delete from core.market_price where company_id = %s and is_mock = true", (company_id,))
        cur.executemany(
            """
            insert into core.market_price
                (company_id, price_date, close_price, currency, source, is_mock)
            values
                (%(company_id)s, %(price_date)s, %(close_price)s, 'USD', 'mock', true)
            """,
            [{"company_id": company_id, **r} for r in price_rows],
        )
    conn.commit()
    return len(price_rows)


def load_mock_prices(conn: psycopg.Connection, ciks: set[str], end_date: date | None = None) -> dict:
    end_date = end_date or date.today()
    with conn.cursor() as cur:
        cur.execute("select id, cik from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = {cik: cid for cid, cik in cur.fetchall()}

    stats = {"considered": 0, "ok": 0, "no_company": 0, "no_mock_base_price": 0}
    total_rows = 0
    for cik in sorted(ciks):
        stats["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            stats["no_company"] += 1
            continue
        if cik not in MOCK_BASE_PRICE:
            stats["no_mock_base_price"] += 1
            continue
        rows = load_mock_prices_for_company(conn, company_id, cik, end_date)
        total_rows += rows
        stats["ok"] += 1

    logger.info("company_master.market_price.mock_load_done", total_rows=total_rows, **stats)
    return {"total_rows": total_rows, **stats}
