"""Faithful Python port of 5 of apps/app/lib/company/db.ts's reference-
data queries (doc 54, 2026-10-13): the full company directory, a lookup
by ticker list, sector/industry lists, and their per-slug company lists.
Moved here by the same founder direction and reasoning as
company_page.py (2026-10-03) -- Next.js must never hold a direct
Postgres connection -- plus a second reason specific to this data: it
backs the site's least-personalized, most-repeat-traffic pages
(homepage, /stocks, /stocks/sector, /stocks/industry, /explore), all
previously running `force-dynamic` with zero caching at all (doc 54's
finding). SQL is copied verbatim from db.ts with the one mechanical
substitution company_page.py already established (${EQUITY_ONLY_SQL} ->
its own literal text, inlined -- it was never a parameter, just a
reusable SQL fragment in the TS client). `slugify()` is also ported
1:1 -- it's the one place a display name becomes a URL segment, and the
same function must be used to match a URL slug back to its real name,
per db.ts's own comment on this (never duplicate this logic, or a slug
and its target can silently drift).
"""

import re

import psycopg
import psycopg.rows

_EQUITY_ONLY_SQL = (
    "(l.security_type is null or l.security_type in "
    "('Common Stock', 'ADR', 'REIT', 'MLP', 'Tracking Stk', 'Ltd Part'))"
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def load_full_directory(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(
            f"""
            select distinct on (lower(l.ticker))
              l.ticker,
              coalesce(c.display_name, c.company_name) as company_name,
              l.exchange,
              c.sector
            from core.company c
            join core.listing l on l.company_id = c.id
            where c.status = 'active'
              and l.effective_to is null
              and l.ticker is not null
              and {_EQUITY_ONLY_SQL}
            order by lower(l.ticker), c.company_name
            """
        )
        return cur.fetchall()


def get_companies_by_tickers(conn: psycopg.Connection, tickers: list[str]) -> list[dict]:
    if not tickers:
        return []
    normalized = [t.upper() for t in tickers]
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(
            f"""
            select distinct on (upper(l.ticker))
              l.ticker, coalesce(c.display_name, c.company_name) as company_name, l.exchange, c.sector
            from core.company c
            join core.listing l on l.company_id = c.id
            where c.status = 'active'
              and l.effective_to is null
              and upper(l.ticker) = any(%(tickers)s)
              and {_EQUITY_ONLY_SQL}
            order by upper(l.ticker), c.company_name
            """,
            {"tickers": normalized},
        )
        return cur.fetchall()


def get_sector_list(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(
            """
            select c.y_sector as sector, count(distinct c.id) as company_count
            from core.company c
            join core.listing l on l.company_id = c.id and l.effective_to is null
            where c.status = 'active' and c.y_sector is not null and c.y_sector != ''
            group by c.y_sector
            order by c.y_sector
            """
        )
        rows = cur.fetchall()
    for row in rows:
        row["slug"] = slugify(row["sector"])
        row["company_count"] = str(row["company_count"])
    return rows


def get_industry_list(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(
            """
            select c.y_industry, count(distinct c.id) as company_count
            from core.company c
            join core.listing l on l.company_id = c.id and l.effective_to is null
            where c.status = 'active' and c.y_industry is not null and c.y_industry != ''
            group by c.y_industry
            order by c.y_industry
            """
        )
        rows = cur.fetchall()
    for row in rows:
        row["slug"] = slugify(row["y_industry"])
        row["company_count"] = str(row["company_count"])
    return rows


def get_companies_by_sector_slug(conn: psycopg.Connection, slug: str) -> dict | None:
    sectors = get_sector_list(conn)
    match = next((row for row in sectors if row["slug"] == slug), None)
    if match is None:
        return None
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(
            f"""
            with deduped as (
              select distinct on (c.id) l.ticker, coalesce(c.display_name, c.company_name) as company_name, l.exchange, c.sector
              from core.company c
              join core.listing l on l.company_id = c.id and l.effective_to is null
              where c.status = 'active' and c.y_sector = %(sector)s and {_EQUITY_ONLY_SQL}
              order by c.id, (l.security_type = 'Common Stock') desc nulls last
            )
            select * from deduped order by company_name
            """,
            {"sector": match["sector"]},
        )
        companies = cur.fetchall()
    return {"sector": match["sector"], "companies": companies}


def get_companies_by_industry_slug(conn: psycopg.Connection, slug: str) -> dict | None:
    industries = get_industry_list(conn)
    match = next((row for row in industries if row["slug"] == slug), None)
    if match is None:
        return None
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(
            f"""
            with deduped as (
              select distinct on (c.id) l.ticker, coalesce(c.display_name, c.company_name) as company_name, l.exchange, c.sector
              from core.company c
              join core.listing l on l.company_id = c.id and l.effective_to is null
              where c.status = 'active' and c.y_industry = %(industry)s and {_EQUITY_ONLY_SQL}
              order by c.id, (l.security_type = 'Common Stock') desc nulls last
            )
            select * from deduped order by company_name
            """,
            {"industry": match["y_industry"]},
        )
        companies = cur.fetchall()
    return {"industry": match["y_industry"], "companies": companies}
