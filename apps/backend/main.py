"""Scrooner's internal product API (doc 16, Part 7). NOT apps/data-api --
see doc 16's naming clarification. Thin FastAPI wrapper over pipeline's
already-verified screener/ai_query -- no logic lives here beyond routing,
auth, and entitlement/usage-log bookkeeping.
"""

from fastapi import FastAPI

from observability import api_request_metrics, observe_http_request
from routers import entitlement, saved_screens, screen

app = FastAPI(title="Scrooner Backend API")
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
