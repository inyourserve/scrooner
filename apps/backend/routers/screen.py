"""Stage 7b -- Public endpoints (doc 16). Thin wrappers only -- all real
logic stays in `pipeline`'s already-verified screener/ai_query modules,
imported directly, never reimplemented here (doc 16's boundary table).
No auth: matches doc 01's "free product for discovery" -- running a
screen or an English query costs nothing to try.
"""

from functools import lru_cache

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from cache import get_cached_result, set_cached_result
from dataset_version_cache import get_cached_dataset_version
from db_pool import get_pooled_connection
from metric_catalog import OPERATOR_ORDER, presentation_for
from scrooner_pipeline.ai_query.rules import interpret
from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.screener.cache_key import compute_query_hash
from scrooner_pipeline.screener.query import run_query
from scrooner_pipeline.screener.schema import ScreenQuery

router = APIRouter(prefix="/v1", tags=["screen"])


@lru_cache(maxsize=1)
def _load_metric_catalog() -> list[dict]:
    """Return every metric accepted by the Screener's live catalog query.

    Price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield,
    FCF Yield, EV/EBITDA, EV/Sales, PEG, Buyback Yield, Total Shareholder
    Yield) were excluded here until 2026-09-10 via `requires_price =
    false`, matching `screener.resolve.load_screenable_metric_catalog`'s
    own matching restriction at the time. Both widened together, now that
    those metrics have real, substantial coverage (checked live:
    market_cap 84.5% of active companies, trailing_pe 62.7%) -- see
    doc/learnings/2026-09-10-screener-performance.md.
    """
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select metric_name, formula_description, formula_version
                from analytics.metric_definition
                where status = 'active'
                order by metric_name
                """
            )
            rows = cur.fetchall()

    catalog = []
    for metric_name, formula_description, formula_version in rows:
        presentation = presentation_for(metric_name)
        catalog.append(
            {
                "metric_name": metric_name,
                "display_name": presentation.display_name,
                "short_definition": presentation.short_definition,
                "formula_description": formula_description,
                "formula_version": formula_version,
                "category": presentation.category,
                "value_type": presentation.value_type,
                "operators": OPERATOR_ORDER,
            }
        )
    return sorted(catalog, key=lambda metric: (metric["category"], metric["display_name"]))


def _log_usage(event_type: str, user_id: str | None = None) -> None:
    # Deliberately its OWN one-off connection (scrooner_pipeline.db.
    # connection.get_connection()), NOT db_pool's shared pool -- measured
    # live 2026-09-10: running this via BackgroundTasks against the SHARED
    # pool blocked the main request's own response for ~260ms (matching
    # exactly one Supabase round trip), even though the background task
    # runs after the response body is logically sent; a plain isolated
    # connection here does not exhibit that, confirmed via a controlled
    # side-by-side test. This function always runs after the response is
    # already on the wire, so its own connection's setup cost is invisible
    # to the caller regardless of how slow it is.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into app.usage_event (user_id, event_type) values (%s, %s)",
                (user_id, event_type),
            )
        conn.commit()


@router.post("/screen")
def post_screen(query: ScreenQuery, background_tasks: BackgroundTasks) -> dict:
    # Usage logging is deliberately NOT on the response's critical path --
    # it's incidental bookkeeping, not part of doc 16's actual API
    # contract, and its own round trip was, after caching + connection
    # pooling, half of what remained of a cache-hit request's latency
    # (measured live 2026-09-10). BackgroundTasks runs it after the
    # response is already sent.
    background_tasks.add_task(_log_usage, "screen_run")
    with get_pooled_connection() as conn:
        dataset_version = get_cached_dataset_version(conn)
        query_hash = compute_query_hash(query, dataset_version)
        cached = get_cached_result(query_hash)
        if cached is not None:
            return {**cached, "cache_hit": True}
        result = run_query(conn, query, dataset_version=dataset_version)
    set_cached_result(query_hash, result)
    return {**result, "cache_hit": False}


@router.get("/metrics")
def get_metrics() -> list[dict]:
    return _load_metric_catalog()


class AskRequest(BaseModel):
    text: str
    run: bool = False


@router.post("/ask")
def post_ask(body: AskRequest, background_tasks: BackgroundTasks) -> dict:
    background_tasks.add_task(_log_usage, "ask_run")
    result = interpret(body.text)
    response = {
        "explanation": result.explanation,
        "query": result.query.model_dump() if result.query else None,
        "recognized_query": result.recognized_query.model_dump() if result.recognized_query else None,
        "unrecognized": result.unrecognized,
        "ambiguous": [{"phrase": a.phrase, "candidates": a.candidates} for a in result.ambiguous],
    }
    if body.run and result.query is not None:
        with get_pooled_connection() as conn:
            dataset_version = get_cached_dataset_version(conn)
            query_hash = compute_query_hash(result.query, dataset_version)
            cached = get_cached_result(query_hash)
            if cached is not None:
                response["result"] = {**cached, "cache_hit": True}
            else:
                run_result = run_query(conn, result.query, dataset_version=dataset_version)
                set_cached_result(query_hash, run_result)
                response["result"] = {**run_result, "cache_hit": False}
    return response
