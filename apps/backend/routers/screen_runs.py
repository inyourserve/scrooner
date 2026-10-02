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
    get_cached_run_lookup,
    get_cached_run_page,
    set_cached_run_page,
    set_cached_run_write,
)
from dataset_version_cache import get_cached_dataset_version, get_cached_metric_catalog
from scrooner_pipeline.ai_query.edit_templates import interpret_edit
from scrooner_pipeline.ai_query.rules import interpret
from db_pool import get_pooled_connection
from scrooner_pipeline.screener.cache_key import compute_query_hash
from scrooner_pipeline.screener.query import load_screen_result_page, run_query
from scrooner_pipeline.screener.schema import ScreenQuery


def _json_default(value):
    # Never jsonable_encoder() a Decimal here -- it silently converts to a
    # lossy float (confirmed live: Decimal("0.1234567890123456789012345678")
    # -> 0.12345678901234568). Every reported financial value in this
    # codebase stays Decimal end to end and is serialized as an exact
    # string at the JSON boundary (doc 04's correctness controls) -- this
    # is that boundary for every screen-run page this router returns.
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
    current_query: ScreenQuery | None = None
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
        raise HTTPException(
            status_code=400, detail="Invalid pagination cursor"
        ) from error


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
    requested = list(
        dict.fromkeys([*query.display_metrics, *DEFAULT_COMPARISON_METRICS])
    )
    return query.model_copy(update={"display_metrics": requested[:20]})


def prepare_screen_run_query(query: ScreenQuery) -> ScreenQuery:
    """Apply the canonical presentation defaults used by live and warm runs."""
    return _apply_default_display_metrics(_apply_default_sort(query))


def _read_page(
    conn, run_id: str, user_id: str, page_size: int, cursor: str | None
) -> dict:
    cached = get_cached_run_page(user_id, run_id, page_size, cursor)
    if cached is not None:
        return cached

    start = _decode_cursor(cursor)
    with conn.cursor() as cur:
        # `run_id` is app.user_screen_run.id; the `user_id` filter is the
        # ownership check. Postgres arrays are 1-based, slices inclusive.
        # Exclusion lists are resolved against the run's own snapshot
        # version here, server-side, so only CIKs/names cross the network
        # (not full rows for thousands of excluded companies).
        cur.execute(
            """
            select u.query_text, r.normalized_query, r.dataset_version, cardinality(r.company_ids),
                   r.company_ids[%s:%s], u.ran_at,
                   coalesce((
                       select jsonb_agg(jsonb_build_object(
                                  'cik', m.cik, 'company_name', s.company_name,
                                  'missing_metrics', string_to_array(m.metrics, ','))
                              order by m.ord)
                       from unnest(r.excluded_missing_ciks, r.excluded_missing_metrics) with ordinality as m(cik, metrics, ord)
                       join analytics.company_screening_snapshot s
                         on s.dataset_version = r.dataset_version and s.cik = m.cik
                   ), '[]'::jsonb),
                   case when coalesce((r.normalized_query ->> 'include_inactive')::boolean, false) then '{}'::text[]
                        else array(select s.cik from analytics.company_screening_snapshot s
                                   where s.dataset_version = r.dataset_version and s.status != 'active'
                                   order by s.company_id)
                   end
            from app.user_screen_run u
            join app.screen_result r on r.id = u.screen_result_id
            where u.id = %s and u.user_id = %s
            """,
            (start + 1, start + page_size, run_id, user_id),
        )
        run = cur.fetchone()
    if run is None:
        raise HTTPException(status_code=404, detail="Screen run not found")
    (
        query_text,
        normalized_query,
        dataset_version,
        total_count,
        page_ids,
        ran_at,
        missing,
        inactive,
    ) = run

    # Values come from the run's OWN snapshot version (migration 0074), so
    # a page always shows the numbers the run matched on, never today's.
    items = load_screen_result_page(
        conn, ScreenQuery.model_validate(normalized_query), dataset_version, page_ids
    )
    if items is None:
        raise HTTPException(
            status_code=410,
            detail="This screen run's data version has been retired; run the screen again",
        )

    previous_cursor = _encode_cursor(max(0, start - page_size)) if start > 0 else None
    next_cursor = (
        _encode_cursor(start + page_size) if start + page_size < total_count else None
    )
    page = {
        "run_id": str(run_id),
        "query_text": query_text,
        "normalized_query": normalized_query,
        "total_count": total_count,
        "excluded_missing_data": missing,
        "excluded_inactive": inactive,
        "items": json.loads(json.dumps(items, default=_json_default)),
        "next_cursor": next_cursor,
        "cursor": cursor,
        "previous_cursor": previous_cursor,
        "ran_at": str(ran_at),
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
    query = prepare_screen_run_query(query)
    run_id_to_create = requested_run_id or uuid4()
    with get_pooled_connection() as conn:
        dataset_version = get_cached_dataset_version(conn)
        query_hash = compute_query_hash(query, dataset_version)
        # One pipelined round trip for both independent lookups (was two
        # sequential GETs) -- see cache.get_cached_run_lookup.
        cached_run_id, result = get_cached_run_lookup(user_id, query_hash, text)
        if requested_run_id is None and cached_run_id is not None:
            try:
                cached_page = _read_page(conn, cached_run_id, user_id, page_size, None)
                cached_page["corrections"] = corrections or []
                return cached_page
            except HTTPException as error:
                if error.status_code not in (404, 410):
                    raise
                # A stale Redis pointer (or a retired version) must not
                # prevent a fresh run.

        freshly_computed_result = result is None
        if result is None:
            result = run_query(
                conn,
                query,
                dataset_version=dataset_version,
                catalog=get_cached_metric_catalog(conn),
            )
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
        # One round trip that uploads only IDs (migration 0074). Measured
        # live 2026-09-26 for a 2,060-match run: storing a JSONB copy of
        # every company's values meant uploading 2.26 MB (+ up to ~290 KB
        # of exclusions JSON), 1.7-2.8s on this link, while the same insert
        # took 104ms server-side. The values already live in the versioned
        # snapshot; pages rebuild them from `dataset_version` (_read_page).
        # A single statement is atomic on its own, so no conn.transaction()
        # (autocommit pool, see db_pool.py).
        excluded_missing = result["excluded_missing_data"]
        with conn.cursor() as cur:
            cur.execute(
                """
                with new_result as (
                    insert into app.screen_result
                        (query_hash, dataset_version, normalized_query, total_count, company_ids,
                         excluded_missing_ciks, excluded_missing_metrics, computed_at)
                    values (%(query_hash)s, %(dataset_version)s, %(normalized_query)s, %(total_count)s, %(company_ids)s,
                            %(missing_ciks)s, %(missing_metrics)s, %(ran_at)s)
                    returning id
                )
                insert into app.user_screen_run (id, user_id, screen_result_id, query_text, ran_at)
                values (%(run_id)s, %(user_id)s, (select id from new_result), %(text)s, %(ran_at)s)
                returning id
                """,
                {
                    "query_hash": query_hash,
                    # The version the result was actually computed on (a
                    # Redis-cached result carries its own), which is the
                    # version its pages must read back.
                    "dataset_version": result.get("dataset_version", dataset_version),
                    "normalized_query": json.dumps(normalized_query),
                    "total_count": len(matches),
                    "company_ids": [company["company_id"] for company in matches],
                    "missing_ciks": [entry["cik"] for entry in excluded_missing],
                    "missing_metrics": [
                        ",".join(entry["missing_metrics"]) for entry in excluded_missing
                    ],
                    "ran_at": ran_at,
                    "run_id": run_id_to_create,
                    "user_id": user_id,
                    "text": text,
                },
            )
            run_id = cur.fetchone()[0]

    # Build the first page directly from what was just computed/inserted --
    # `_read_page` re-SELECTing the exact rows this same request just wrote
    # cost two more round trips for nothing (measured live 2026-09-10: this
    # endpoint was taking 5.7-8.2s end to end, with ~2s of that after the
    # Screener's own query already completed). `_json_default`-round-tripped
    # through json.loads so the shape matches exactly what a later GET
    # (rebuilt from the snapshot, _read_page) returns -- Decimal-as-string, not a
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
    # One pipelined round trip for all three writes (was up to three
    # sequential SETs) -- see cache.set_cached_run_write. `result` is
    # passed only when this request computed it fresh; a cache-hit result
    # is already in Redis under its own TTL.
    set_cached_run_write(
        query_hash=query_hash,
        result=result if freshly_computed_result else None,
        user_id=user_id,
        query_text=text,
        run_id=str(run_id),
        page_size=page_size,
        page=page,
    )
    return page


@router.post("/screen-runs")
def create_screen_run(
    body: ScreenRunCreate, user_id: str = Depends(get_current_user_id)
) -> dict:
    if body.query is not None:
        return create_run_from_query(
            body.text.strip(), body.query, user_id, body.page_size, body.run_id
        )
    text = body.text.strip()
    interpretation = (
        interpret_edit(text, body.current_query)
        if body.current_query is not None
        else None
    )
    if interpretation is None:
        interpretation = interpret(text)
    if (
        interpretation.query is None
        or interpretation.unrecognized
        or interpretation.ambiguous
    ):
        return {
            "query": None,
            "recognized_query": interpretation.recognized_query.model_dump()
            if interpretation.recognized_query
            else None,
            "unrecognized": interpretation.unrecognized,
            "ambiguous": [
                {"phrase": item.phrase, "candidates": item.candidates}
                for item in interpretation.ambiguous
            ],
            "corrections": [
                asdict(correction) for correction in interpretation.corrections
            ],
            "explanation": interpretation.explanation,
        }
    return create_run_from_query(
        text,
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
