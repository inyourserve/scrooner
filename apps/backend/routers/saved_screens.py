"""Stage 7c -- Saved screen CRUD (doc 16, doc 03's create/name/view/rerun/
delete). Stores the ScreenQuery, not a result -- doc 16 Sec 4: the
Screener is already deterministic (doc 14b), so "rerun" is just "run
again" (POST /v1/screen with the stored query), not a new operation
here. Rename only via PATCH, not a query edit -- doc 16's own scoping
keeps query changes as delete-and-recreate, not in-place mutation.
"""

import re
import unicodedata
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user_id
from cache import (
    get_cached_screen_detail,
    get_cached_screens_list,
    invalidate_screen_detail,
    invalidate_screens_list,
    set_cached_screen_detail,
    set_cached_screens_list,
)
from db_pool import get_pooled_connection
from scrooner_pipeline.screener.schema import ScreenQuery
from routers.screen_runs import _read_page, create_run_from_query

router = APIRouter(prefix="/v1", tags=["saved_screens"])


class SavedScreenCreate(BaseModel):
    name: str
    query: ScreenQuery
    run_id: UUID | None = None


class SavedScreenRename(BaseModel):
    name: str


def _slug_base(name: str) -> str:
    ascii_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-") or "screen"


def _available_slug(conn, user_id: str, name: str) -> str:
    base = _slug_base(name)
    with conn.cursor() as cur:
        cur.execute(
            "select slug from app.saved_screen where user_id = %s and (slug = %s or slug like %s)",
            (user_id, base, f"{base}-%"),
        )
        existing = {row[0] for row in cur.fetchall()}
    if base not in existing:
        return base
    suffix = 2
    while f"{base}-{suffix}" in existing:
        suffix += 1
    return f"{base}-{suffix}"


@router.get("/screens")
def list_screens(user_id: str = Depends(get_current_user_id)) -> list[dict]:
    cached = get_cached_screens_list(user_id)
    if cached is not None:
        return cached
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id, name, slug, query, created_at, updated_at from app.saved_screen where user_id = %s order by updated_at desc, id desc",
                (user_id,),
            )
            rows = cur.fetchall()
    screens = [
        {
            "id": r[0],
            "name": r[1],
            "slug": r[2],
            "query": r[3],
            "created_at": str(r[4]),
            "updated_at": str(r[5]),
        }
        for r in rows
    ]
    set_cached_screens_list(user_id, screens)
    return screens


@router.post("/screens")
def create_screen(
    body: SavedScreenCreate, user_id: str = Depends(get_current_user_id)
) -> dict:
    # No conn.transaction() here -- measured live 2026-09-12: wrapping even
    # a single write in an explicit transaction on this pool costs ~500ms
    # of pure overhead (an explicit BEGIN + COMMIT round trip pair on top
    # of autocommit=True, which already makes one statement atomic on its
    # own). This function has exactly one write (the INSERT); the reads
    # before it (_available_slug, the run_id ownership check) don't need
    # transactional isolation with it for correctness -- a real race on
    # the slug is still caught by (user_id, slug)'s own unique index at
    # insert time, not silently corrupted.
    clean_name = body.name.strip()
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            # Found live 2026-10-03: _available_slug below was built to
            # auto-disambiguate a colliding NAME by appending "-2" to the
            # SLUG ("my screen" -> slug "my-screen", then "my-screen-2")
            # rather than reject it -- so saving the identical name twice
            # silently created two separate rows with the same name, no
            # error. A race between two near-simultaneous saves of the
            # same name can still slip past this check (no DB-level
            # unique constraint on name, matching the slug race's own
            # already-accepted risk tolerance noted below) -- rare enough
            # not to warrant one for a handful-of-rows-per-user table.
            cur.execute(
                "select 1 from app.saved_screen where user_id = %s and lower(name) = lower(%s)",
                (user_id, clean_name),
            )
            if cur.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail=f'You already have a screen named "{clean_name}". Choose a different name.',
                )
        slug = _available_slug(conn, user_id, body.name)
        with conn.cursor() as cur:
            if body.run_id is not None:
                cur.execute(
                    "select 1 from app.user_screen_run where id = %s and user_id = %s",
                    (body.run_id, user_id),
                )
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Screen run not found")
            cur.execute(
                "insert into app.saved_screen (user_id, name, slug, query, last_run_id) values (%s, %s, %s, %s, %s) returning id",
                # model_dump_json(), not json.dumps(model_dump()) -- found live
                # 2026-08-17: raw json.dumps can't serialize Decimal (a
                # MetricPredicate.value), and bypasses the same
                # Decimal-as-string handling FastAPI's response encoder
                # already gets right automatically. Pydantic's own JSON
                # serializer handles it correctly, same guarantee, explicit.
                (
                    user_id,
                    clean_name,
                    slug,
                    body.query.model_dump_json(),
                    body.run_id,
                ),
            )
            new_id = cur.fetchone()[0]
    invalidate_screens_list(user_id)
    return {"id": new_id, "name": clean_name, "slug": slug}


@router.get("/screens/{slug}")
def get_screen(
    slug: str,
    cursor: str | None = None,
    page_size: int = Query(default=50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    # Only the saved_screen row itself (metadata + last_run_id) is cached
    # here -- the run's own paginated page data always goes through
    # _read_page below, which has its own separate, already-correct
    # caching (keyed by run_id, not by slug/cursor/page_size combined with
    # this row's cache lifetime).
    cached_meta = get_cached_screen_detail(user_id, slug)
    if cached_meta is not None:
        meta = cached_meta
    else:
        with get_pooled_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select id, name, slug, query, last_run_id, created_at, updated_at from app.saved_screen where user_id = %s and slug = %s",
                    (user_id, slug),
                )
                row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Screen not found")
            meta = {
                "id": row[0],
                "name": row[1],
                "slug": row[2],
                "query": row[3],
                "last_run_id": str(row[4]) if row[4] is not None else None,
                "created_at": str(row[5]),
                "updated_at": str(row[6]),
            }
        set_cached_screen_detail(user_id, slug, meta)

    payload = {k: v for k, v in meta.items() if k != "last_run_id"}
    payload["run"] = None
    if meta["last_run_id"] is not None:
        with get_pooled_connection() as conn:
            payload["run"] = _read_page(
                conn, meta["last_run_id"], user_id, page_size, cursor
            )
    return payload


@router.post("/screens/{slug}/refresh")
def refresh_screen(slug: str, user_id: str = Depends(get_current_user_id)) -> dict:
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select saved.query, coalesce(run.query_text, '')
                from app.saved_screen saved
                left join app.user_screen_run run on run.id = saved.last_run_id
                where saved.user_id = %s and saved.slug = %s
                """,
                (user_id, slug),
            )
            row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Screen not found")
    query = ScreenQuery.model_validate(row[0])
    run = create_run_from_query(row[1], query, user_id)
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "update app.saved_screen set last_run_id = %s, updated_at = now() where user_id = %s and slug = %s",
                (run["run_id"], user_id, slug),
            )
    invalidate_screen_detail(user_id, slug)
    invalidate_screens_list(user_id)  # updated_at changed -- list order can shift
    return run


@router.patch("/screens/{screen_id}")
def rename_screen(
    screen_id: int, body: SavedScreenRename, user_id: str = Depends(get_current_user_id)
) -> dict:
    # Folded the ownership check into the UPDATE's own WHERE clause instead
    # of a separate SELECT first -- found live 2026-09-12 sanity-checking
    # this endpoint's timing: two sequential round trips for what only
    # needs to be one. Postgres handles the `user_id = %s` (uuid column vs.
    # plain string parameter) comparison the same way every other query in
    # this file already does -- this is a WHERE-clause comparison Postgres
    # casts itself, a different thing from the 2026-08-17 bug (a psycopg-
    # returned uuid.UUID compared to a string *in Python*), so it doesn't
    # reintroduce that.
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "update app.saved_screen set name = %s, updated_at = now() where id = %s and user_id = %s returning slug",
                (body.name, screen_id, user_id),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Screen not found")
    invalidate_screen_detail(user_id, row[0])
    invalidate_screens_list(user_id)
    return {"id": screen_id, "name": body.name}


@router.delete("/screens/{screen_id}")
def delete_screen(screen_id: int, user_id: str = Depends(get_current_user_id)) -> dict:
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "delete from app.saved_screen where id = %s and user_id = %s returning slug",
                (screen_id, user_id),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Screen not found")
    invalidate_screen_detail(user_id, row[0])
    invalidate_screens_list(user_id)
    return {"deleted": screen_id}
