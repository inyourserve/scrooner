"""Reference-data endpoints for apps/app's least-personalized, most-
repeat-traffic public pages (doc 54, 2026-10-13): the homepage quick
picks, the full company directory, sector/industry lists, and their
per-slug company lists. Previously queried Postgres directly from
Next.js with `force-dynamic` and zero caching on every request -- moved
here by the same founder direction as company.py (2026-10-03: Next.js
must never hold a direct DB connection), plus doc 54's own recommended
resolution of its Option A/B decision point (centralize in apps/backend
with the existing Redis contract, consistent with that move, rather
than rebuild a second Redis client inside apps/app). No auth: all of
this is public, SEO-indexed data, same posture as company.py/metrics.
"""

from fastapi import APIRouter, HTTPException

from cache import CACHE_MISS, get_cached_reference, set_cached_reference
from db_pool import get_pooled_connection
from reference_data import (
    get_companies_by_industry_slug,
    get_companies_by_sector_slug,
    get_companies_by_tickers,
    get_industry_list,
    get_sector_list,
    load_full_directory,
)

router = APIRouter(prefix="/v1", tags=["reference-data"])


@router.get("/directory")
def get_directory() -> list[dict]:
    cached = get_cached_reference("directory")
    if cached is not CACHE_MISS:
        return cached
    with get_pooled_connection() as conn:
        rows = load_full_directory(conn)
    set_cached_reference("directory", rows)
    return rows


@router.get("/sectors")
def get_sectors() -> list[dict]:
    cached = get_cached_reference("sectors")
    if cached is not CACHE_MISS:
        return cached
    with get_pooled_connection() as conn:
        rows = get_sector_list(conn)
    set_cached_reference("sectors", rows)
    return rows


@router.get("/industries")
def get_industries() -> list[dict]:
    cached = get_cached_reference("industries")
    if cached is not CACHE_MISS:
        return cached
    with get_pooled_connection() as conn:
        rows = get_industry_list(conn)
    set_cached_reference("industries", rows)
    return rows


@router.get("/sectors/{slug}")
def get_sector(slug: str) -> dict:
    cache_key = f"sector:{slug}"
    cached = get_cached_reference(cache_key)
    if cached is not CACHE_MISS:
        data = cached
    else:
        with get_pooled_connection() as conn:
            data = get_companies_by_sector_slug(conn, slug)
        set_cached_reference(cache_key, data)
    if data is None:
        raise HTTPException(status_code=404, detail="Sector not found")
    return data


@router.get("/industries/{slug}")
def get_industry(slug: str) -> dict:
    cache_key = f"industry:{slug}"
    cached = get_cached_reference(cache_key)
    if cached is not CACHE_MISS:
        data = cached
    else:
        with get_pooled_connection() as conn:
            data = get_companies_by_industry_slug(conn, slug)
        set_cached_reference(cache_key, data)
    if data is None:
        raise HTTPException(status_code=404, detail="Industry not found")
    return data


# Homepage quick picks (a fixed ~11-ticker list) -- query-string tickers
# rather than a path segment, since the caller already has the exact
# ticker list and gains nothing from a server-side default list living
# here too (that would just be a second place doc 02's homepage content
# could drift from apps/app's own). Cache key is the sorted ticker list
# itself, so this endpoint is correct for any caller, not just the one
# fixed list apps/app happens to use today.
@router.get("/companies")
def get_companies(tickers: str) -> list[dict]:
    ticker_list = sorted({t.strip().upper() for t in tickers.split(",") if t.strip()})
    if not ticker_list:
        return []
    cache_key = "companies:" + ",".join(ticker_list)
    cached = get_cached_reference(cache_key)
    if cached is not CACHE_MISS:
        return cached
    with get_pooled_connection() as conn:
        rows = get_companies_by_tickers(conn, ticker_list)
    set_cached_reference(cache_key, rows)
    return rows
