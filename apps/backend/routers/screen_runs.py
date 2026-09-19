"""Authenticated, immutable screener runs with stored-result pagination."""

import base64
import json
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth import get_current_user_id
from cache import (
    get_cached_result,
    get_cached_run_id,
    get_cached_run_page,
    set_cached_result,
    set_cached_run_id,
    set_cached_run_page,
)
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
    # is that boundary for screen_result/screen_result_item's stored JSONB.
    return str(value)


router = APIRouter(prefix="/v1", tags=["screen_runs"])

DEFAULT_COMPARISON_METRICS = [
    "market_cap",
    "trailing_pe",
    "roe",
    "roic",
    "revenue_growth_yoy",
    "eps_growth_yoy",
    "debt_to_equity",
    "fcf_margin",
    "dividend_yield",
]


class ScreenRunCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    page_size: int = Field(default=50, ge=1, le=100)
    query: ScreenQuery | None = None
    run_id: UUID | None = None


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


def _apply_default_sort(query: ScreenQuery) -> ScreenQuery:
    """Choose a useful deterministic order when the query did not specify one.

    The final directional condition best reflects what the user emphasized:
    minimum-quality constraints show strongest values first, while maximum-
    valuation/debt constraints show lowest values first. Complex boolean and
    non-directional conditions retain the engine's stable CIK order.
    """
    if query.sort_by is not None or query.where is not None:
        return query
    # A ratio used as a filter is often a poor default ranking. For example,
    # ROE can become enormous when book equity is close to zero, placing
    # blank-check and distressed companies above useful operating businesses.
    # Market cap gives a stable, decision-friendly first view; users can still
    # sort by any visible metric with one click.
    return query.model_copy(
        update={
            "sort_by": "market_cap",
            "sort_desc": True,
        }
    )


def _apply_default_display_metrics(query: ScreenQuery) -> ScreenQuery:
    requested = list(dict.fromkeys([*query.display_metrics, *DEFAULT_COMPARISON_METRICS]))
    return query.model_copy(update={"display_metrics": requested[:20]})


def _read_page(conn, run_id: str, user_id: str, page_size: int, cursor: str | None) -> dict:
    cached = get_cached_run_page(user_id, run_id, page_size, cursor)
    if cached is not None:
        return cached

    start = _decode_cursor(cursor)
    with conn.cursor() as cur:
        # `run_id` here is app.user_screen_run.id -- the per-user pointer,
        # never app.screen_result.id directly. The `user_id` in the WHERE
        # clause is the actual ownership check (a shared screen_result row
        # has no owner of its own); joining to it is what makes "can this
        # caller see this run_id" meaningful at all.
        cur.execute(
            """
            select u.query_text, r.normalized_query, r.total_count, r.exclusions, u.ran_at, u.screen_result_id
            from app.user_screen_run u
            join app.screen_result r on r.id = u.screen_result_id
            where u.id = %s and u.user_id = %s
            """,
            (run_id, user_id),
        )
        run = cur.fetchone()
        if run is None:
            raise HTTPException(status_code=404, detail="Screen run not found")
        screen_result_id = run[5]
        cur.execute(
            """
            select position, result from app.screen_result_item
            where screen_result_id = %s and position >= %s
            order by position limit %s
            """,
            (screen_result_id, start, page_size + 1),
        )
        rows = cur.fetchall()

    visible = rows[:page_size]
    previous_cursor = _encode_cursor(max(0, start - page_size)) if start > 0 else None
    next_cursor = _encode_cursor(visible[-1][0] + 1) if len(rows) > page_size and visible else None
    page = {
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
    set_cached_run_page(user_id, run_id, page_size, cursor, page)
    return page


def create_run_from_query(
    text: str,
    query: ScreenQuery,
    user_id: str,
    page_size: int = 50,
    requested_run_id: UUID | None = None,
    corrections: list[dict] | None = None,
) -> dict:
    query = _apply_default_display_metrics(_apply_default_sort(query))
    run_id_to_create = requested_run_id or uuid4()
    with get_pooled_connection() as conn:
        dataset_version = get_cached_dataset_version(conn)
        query_hash = compute_query_hash(query, dataset_version)
        cached_run_id = get_cached_run_id(user_id, query_hash, text)
        if requested_run_id is None and cached_run_id is not None:
            try:
                cached_page = _read_page(conn, cached_run_id, user_id, page_size, None)
                cached_page["corrections"] = corrections or []
                return cached_page
            except HTTPException as error:
                if error.status_code != 404:
                    raise
                # A stale Redis pointer must not prevent a fresh run.

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
                # Deduplicated write (2026-09-12): a different user asking
                # the identical query against the same dataset generation
                # used to pay a full insert-then-executemany of a
                # duplicate copy of an already-known result -- measured
                # live at ~2.1s for a 25-row result, pure overhead since
                # Redis had already skipped the actual recomputation.
                # `on conflict ... do nothing returning id` is the
                # race-safe "get or create" for the shared screen_result
                # row; screen_result_item is only ever written once, by
                # whichever request actually creates it.
                cur.execute(
                    """
                    insert into app.screen_result
                        (query_hash, dataset_version, normalized_query, total_count, exclusions, computed_at)
                    values (%s, %s, %s, %s, %s, %s)
                    on conflict (query_hash, dataset_version) do nothing
                    returning id
                    """,
                    (
                        query_hash,
                        dataset_version,
                        json.dumps(normalized_query),
                        len(matches),
                        json.dumps(exclusions, default=_json_default),
                        ran_at,
                    ),
                )
                inserted = cur.fetchone()
                if inserted is not None:
                    screen_result_id = inserted[0]
                    cur.executemany(
                        """
                        insert into app.screen_result_item (screen_result_id, position, company_id, result)
                        values (%s, %s, %s, %s)
                        """,
                        [
                            (screen_result_id, position, company["company_id"], json.dumps(company, default=_json_default))
                            for position, company in enumerate(matches)
                        ],
                    )
                else:
                    cur.execute(
                        "select id from app.screen_result where query_hash = %s and dataset_version = %s",
                        (query_hash, dataset_version),
                    )
                    screen_result_id = cur.fetchone()[0]

                # Always written, even on a reused screen_result -- this is
                # the thin per-user record "my saved screens"/rerun history
                # actually needs, and the only thing this specific request
                # is genuinely the first to create.
                cur.execute(
                    """
                    insert into app.user_screen_run (id, user_id, screen_result_id, query_text, ran_at)
                    values (%s, %s, %s, %s, %s) returning id
                    """,
                    (run_id_to_create, user_id, screen_result_id, text, ran_at),
                )
                run_id = cur.fetchone()[0]

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
    page = {
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
        "corrections": corrections or [],
    }
    set_cached_run_id(user_id, query_hash, text, str(run_id))
    set_cached_run_page(user_id, str(run_id), page_size, None, page)
    return page


@router.post("/screen-runs")
def create_screen_run(body: ScreenRunCreate, user_id: str = Depends(get_current_user_id)) -> dict:
    if body.query is not None:
        return create_run_from_query(body.text.strip(), body.query, user_id, body.page_size, body.run_id)
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
            "corrections": [asdict(correction) for correction in interpretation.corrections],
            "explanation": interpretation.explanation,
        }
    return create_run_from_query(
        body.text.strip(),
        interpretation.query,
        user_id,
        body.page_size,
        body.run_id,
        [asdict(correction) for correction in interpretation.corrections],
    )


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
