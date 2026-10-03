"""Public company-page endpoint (2026-10-03, by explicit founder direction:
Next.js must never hold a direct Postgres connection, consistency with the
Screener's architecture). Moves apps/app/lib/company/db.ts::getCompanyPageData
and its Redis cache (lib/company/cache.ts) here -- same query (a faithful
port, see company_page.py's own docstring), same key naming/TTL, same
fail-open contract as every other cache in this file. No auth: a public,
SEO-indexed page (doc 17), same "free to try" posture as /v1/metrics.
"""

from fastapi import APIRouter, HTTPException

from company_page import get_company_page_data
from db_pool import get_pooled_connection
from cache import CACHE_MISS, get_cached_company_page, set_cached_company_page

router = APIRouter(prefix="/v1", tags=["company"])


@router.get("/company/{ticker}")
def get_company(ticker: str) -> dict:
    cached = get_cached_company_page(ticker)
    if cached is CACHE_MISS:
        with get_pooled_connection() as conn:
            data = get_company_page_data(conn, ticker)
        set_cached_company_page(ticker, data)
    else:
        data = cached
    if data is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return data
