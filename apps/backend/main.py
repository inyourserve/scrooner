"""Scrooner's internal product API (doc 16, Part 7). NOT apps/data-api --
see doc 16's naming clarification. Thin FastAPI wrapper over pipeline's
already-verified screener/ai_query -- no logic lives here beyond routing,
auth, and entitlement/usage-log bookkeeping.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from dataset_version_cache import get_cached_dataset_version, get_cached_metric_catalog
from db_pool import close_pool, get_pooled_connection, open_pool
from observability import api_request_metrics, observe_http_request
from routers import company, entitlement, saved_screens, screen, screen_runs


def _warm_screener_caches() -> None:
    # dataset_version/metric_catalog are each one ~270-300ms round trip
    # from a non-co-located host (doc/learnings/2026-10-02-create-screen-
    # latency-audit.md) and are cached in-process for 300s
    # (dataset_version_cache.py) -- cheap in steady state, but without
    # this, the FIRST real create-screen request after every deploy/
    # restart pays both round trips on top of its own work. Calling them
    # once here, with a connection the pool already opened at startup,
    # means no real user request ever has to be the one that warms this.
    with get_pooled_connection() as conn:
        get_cached_dataset_version(conn)
        get_cached_metric_catalog(conn)


@asynccontextmanager
async def lifespan(_: FastAPI):
    open_pool()
    try:
        _warm_screener_caches()
    except Exception:
        # Best-effort: a cold cache just means the first real request pays
        # the round trip itself, exactly like before this existed. Startup
        # must never fail because of this.
        pass
    try:
        yield
    finally:
        close_pool()


app = FastAPI(title="Scrooner Backend API", lifespan=lifespan)
app.middleware("http")(observe_http_request)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/metrics")
def health_metrics() -> dict:
    """Content-free, process-local request telemetry for beta operations."""
    return api_request_metrics.snapshot()


app.include_router(screen.router)
app.include_router(entitlement.router)
app.include_router(saved_screens.router)
app.include_router(screen_runs.router)
app.include_router(company.router)
