"""Scrooner's internal product API (doc 16, Part 7). NOT apps/data-api --
see doc 16's naming clarification. Thin FastAPI wrapper over pipeline's
already-verified screener/ai_query -- no logic lives here beyond routing,
auth, and entitlement/usage-log bookkeeping.
"""

from fastapi import FastAPI

from routers import entitlement, saved_screens, screen

app = FastAPI(title="Scrooner Backend API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(screen.router)
app.include_router(entitlement.router)
app.include_router(saved_screens.router)
