"""Module 2 — SEC Identity / CIK mapping (doc 06). Read-side lookups over
raw.company_universe (populated by collector.universe). CIK is the stable
identity per doc 07 §9 — this module never chooses one ticker as "the"
ticker for a CIK; a company can have several, that's just returned as-is.
"""

import psycopg


def get_all_ciks(conn: psycopg.Connection) -> list[str]:
    """Distinct CIKs known to the Collector — what downstream modules
    (Day 3's companyfacts/submissions collectors) iterate over."""
    with conn.cursor() as cur:
        cur.execute("select distinct cik from raw.company_universe order by cik")
        return [row[0] for row in cur.fetchall()]


def get_cik_for_ticker(conn: psycopg.Connection, ticker: str) -> str | None:
    with conn.cursor() as cur:
        cur.execute(
            "select cik from raw.company_universe where ticker = %s limit 1",
            (ticker.upper(),),
        )
        row = cur.fetchone()
        return row[0] if row else None


def get_tickers_for_cik(conn: psycopg.Connection, cik: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select ticker from raw.company_universe where cik = %s order by ticker",
            (cik,),
        )
        return [row[0] for row in cur.fetchall()]
