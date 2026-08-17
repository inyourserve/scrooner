"""Module 1 — Company Universe (doc 06). Fetches SEC's own ticker/CIK list
and mirrors it into raw.company_universe, verbatim. No interpretation: see
doc 08 for why this table has no exchange/status column.
"""

import psycopg
import structlog

from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


def fetch_company_tickers(client: SECClient) -> list[dict]:
    """Returns one row per (cik, ticker) pair — company_tickers.json is
    one-to-many (verified live 2026-08-14: 18% of CIKs have >1 ticker)."""
    payload = client.get_json(COMPANY_TICKERS_URL)
    rows = []
    for entry in payload.values():
        # SEC's cik_str is a plain int (e.g. 320193); normalize to the
        # zero-padded 10-digit form used everywhere else (CIK0000320193 in
        # submissions/filing URLs), so cik is joinable/consistent across
        # every raw.* table without each caller re-deriving the format.
        cik = str(entry["cik_str"]).zfill(10)
        rows.append(
            {
                "cik": cik,
                "ticker": entry["ticker"],
                "company_name": entry["title"],
            }
        )
    return rows


def upsert_company_universe(conn: psycopg.Connection, rows: list[dict]) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into raw.company_universe (cik, ticker, company_name, collected_at)
            values (%(cik)s, %(ticker)s, %(company_name)s, now())
            on conflict (cik, ticker) do update
                set company_name = excluded.company_name,
                    collected_at = excluded.collected_at
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def collect_company_universe(conn: psycopg.Connection) -> int:
    with SECClient() as client:
        rows = fetch_company_tickers(client)
    count = upsert_company_universe(conn, rows)
    logger.info("company_universe.collected", rows=count)
    return count
