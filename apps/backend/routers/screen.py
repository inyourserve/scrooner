"""Stage 7b -- Public endpoints (doc 16). Thin wrappers only -- all real
logic stays in `pipeline`'s already-verified screener/ai_query modules,
imported directly, never reimplemented here (doc 16's boundary table).
No auth: matches doc 01's "free product for discovery" -- running a
screen or an English query costs nothing to try.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from metric_catalog import OPERATOR_ORDER, presentation_for
from scrooner_pipeline.ai_query.rules import interpret
from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.screener.query import run_query
from scrooner_pipeline.screener.schema import ScreenQuery

router = APIRouter(prefix="/v1", tags=["screen"])


def _load_metric_catalog() -> list[dict]:
    """Return only metrics accepted by the Screener's live catalog query.

    The same ``requires_price = false`` predicate is intentionally used by
    ``screener.resolve.load_screenable_metric_catalog``. Until that engine
    boundary widens, the UI must not advertise price metrics it would reject.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select metric_name, formula_description, formula_version
                from analytics.metric_definition
                where requires_price = false and status = 'active'
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
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into app.usage_event (user_id, event_type) values (%s, %s)",
                (user_id, event_type),
            )
        conn.commit()


@router.post("/screen")
def post_screen(query: ScreenQuery) -> dict:
    with get_connection() as conn:
        result = run_query(conn, query)
    _log_usage("screen_run")
    return result


@router.get("/metrics")
def get_metrics() -> list[dict]:
    return _load_metric_catalog()


class AskRequest(BaseModel):
    text: str
    run: bool = False


@router.post("/ask")
def post_ask(body: AskRequest) -> dict:
    result = interpret(body.text)
    response = {
        "explanation": result.explanation,
        "query": result.query.model_dump() if result.query else None,
        "recognized_query": result.recognized_query.model_dump() if result.recognized_query else None,
        "unrecognized": result.unrecognized,
        "ambiguous": [{"phrase": a.phrase, "candidates": a.candidates} for a in result.ambiguous],
    }
    if body.run and result.query is not None:
        with get_connection() as conn:
            response["result"] = run_query(conn, result.query)
    _log_usage("ask_run")
    return response
