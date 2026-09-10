"""Authenticated, immutable screener runs with stored-result pagination."""

import base64
import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth import get_current_user_id
from cache import get_cached_result, set_cached_result
from dataset_version_cache import get_cached_dataset_version
from scrooner_pipeline.ai_query.rules import interpret
from db_pool import get_pooled_connection
from scrooner_pipeline.screener.cache_key import compute_query_hash
from scrooner_pipeline.screener.query import run_query
from scrooner_pipeline.screener.schema import ScreenQuery


def _json_default(value):
    # Never jsonable_encoder() a Decimal here -- it silently converts to a
    # lossy float (confirmed live: Decimal("0.1234567890123456789012345678")
    # -> 0.12345678901234568). Every reported financial value in this
    # codebase stays Decimal end to end and is serialized as an exact
    # string at the JSON boundary (doc 04's correctness controls) -- this
    # is that boundary for screen_run/screen_run_result's stored JSONB.
    return str(value)


router = APIRouter(prefix="/v1", tags=["screen_runs"])


class ScreenRunCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    page_size: int = Field(default=50, ge=1, le=100)


def _encode_cursor(position: int) -> str:
    return base64.urlsafe_b64encode(str(position).encode()).decode().rstrip("=")


def _decode_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        position = int(base64.urlsafe_b64decode(padded).decode())
        if position < 0:
            raise ValueError
        return position
    except (ValueError, UnicodeDecodeError) as error:
        raise HTTPException(status_code=400, detail="Invalid pagination cursor") from error


def _read_page(conn, run_id: str, user_id: str, page_size: int, cursor: str | None) -> dict:
    start = _decode_cursor(cursor)
    with conn.cursor() as cur:
        cur.execute(
            """
            select query_text, normalized_query, total_count, exclusions, created_at
            from app.screen_run where id = %s and user_id = %s
            """,
            (run_id, user_id),
        )
        run = cur.fetchone()
        if run is None:
            raise HTTPException(status_code=404, detail="Screen run not found")
        cur.execute(
            """
            select position, result from app.screen_run_result
            where run_id = %s and position >= %s
            order by position limit %s
            """,
            (run_id, start, page_size + 1),
        )
        rows = cur.fetchall()

    visible = rows[:page_size]
    previous_cursor = _encode_cursor(max(0, start - page_size)) if start > 0 else None
    next_cursor = _encode_cursor(visible[-1][0] + 1) if len(rows) > page_size and visible else None
    return {
        "run_id": str(run_id),
        "query_text": run[0],
        "normalized_query": run[1],
        "total_count": run[2],
        "excluded_missing_data": run[3].get("excluded_missing_data", []),
        "excluded_inactive": run[3].get("excluded_inactive", []),
        "items": [row[1] for row in visible],
        "next_cursor": next_cursor,
        "cursor": cursor,
        "previous_cursor": previous_cursor,
        "ran_at": str(run[4]),
    }


def create_run_from_query(text: str, query: ScreenQuery, user_id: str, page_size: int = 50) -> dict:
    with get_pooled_connection() as conn:
        dataset_version = get_cached_dataset_version(conn)
        query_hash = compute_query_hash(query, dataset_version)
        result = get_cached_result(query_hash)
        if result is None:
            result = run_query(conn, query, dataset_version=dataset_version)
            set_cached_result(query_hash, result)
        matches = result["matched"]
        exclusions = {
            "excluded_missing_data": result["excluded_missing_data"],
            "excluded_inactive": result["excluded_inactive"],
        }
        # Generated here, not read back from the DB's own `default now()` --
        # the whole point of building the first page from memory below is
        # to avoid a round trip; a column default would force one just to
        # learn its own value.
        ran_at = datetime.now(timezone.utc)
        normalized_query = json.loads(query.model_dump_json())
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into app.screen_run
                        (user_id, query_text, normalized_query, total_count, exclusions, created_at)
                    values (%s, %s, %s, %s, %s, %s) returning id
                    """,
                    (
                        user_id,
                        text,
                        json.dumps(normalized_query),
                        len(matches),
                        json.dumps(exclusions, default=_json_default),
                        ran_at,
                    ),
                )
                run_id = cur.fetchone()[0]
                cur.executemany(
                    """
                    insert into app.screen_run_result (run_id, position, company_id, result)
                    values (%s, %s, %s, %s)
                    """,
                    [
                        (run_id, position, company["company_id"], json.dumps(company, default=_json_default))
                        for position, company in enumerate(matches)
                    ],
                )

    # Build the first page directly from what was just computed/inserted --
    # `_read_page` re-SELECTing the exact rows this same request just wrote
    # cost two more round trips for nothing (measured live 2026-09-10: this
    # endpoint was taking 5.7-8.2s end to end, with ~2s of that after the
    # Screener's own query already completed). `_json_default`-round-tripped
    # through json.loads so the shape matches exactly what a later GET
    # (reading the stored JSONB back) returns -- Decimal-as-string, not a
    # native Decimal object, on both the first response and every one after.
    visible = json.loads(json.dumps(matches[:page_size], default=_json_default))
    next_cursor = _encode_cursor(page_size) if len(matches) > page_size else None
    return {
        "run_id": str(run_id),
        "query_text": text,
        "normalized_query": normalized_query,
        "total_count": len(matches),
        "excluded_missing_data": exclusions["excluded_missing_data"],
        "excluded_inactive": exclusions["excluded_inactive"],
        "items": visible,
        "next_cursor": next_cursor,
        "cursor": None,
        "previous_cursor": None,
        "ran_at": str(ran_at),
    }


@router.post("/screen-runs")
def create_screen_run(body: ScreenRunCreate, user_id: str = Depends(get_current_user_id)) -> dict:
    interpretation = interpret(body.text.strip())
    if interpretation.query is None or interpretation.unrecognized or interpretation.ambiguous:
        return {
            "query": None,
            "recognized_query": interpretation.recognized_query.model_dump() if interpretation.recognized_query else None,
            "unrecognized": interpretation.unrecognized,
            "ambiguous": [
                {"phrase": item.phrase, "candidates": item.candidates}
                for item in interpretation.ambiguous
            ],
            "explanation": interpretation.explanation,
        }
    return create_run_from_query(body.text.strip(), interpretation.query, user_id, body.page_size)


@router.get("/screen-runs/{run_id}")
def get_screen_run(
    run_id: UUID,
    cursor: str | None = None,
    page_size: int = Query(default=50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    # Pure read -- opening/paginating a saved run reuses the process pool.
    with get_pooled_connection() as conn:
        return _read_page(conn, str(run_id), user_id, page_size, cursor)
