"""Stage 7c -- Saved screen CRUD (doc 16, doc 03's create/name/view/rerun/
delete). Stores the ScreenQuery, not a result -- doc 16 Sec 4: the
Screener is already deterministic (doc 14b), so "rerun" is just "run
again" (POST /v1/screen with the stored query), not a new operation
here. Rename only via PATCH, not a query edit -- doc 16's own scoping
keeps query changes as delete-and-recreate, not in-place mutation.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user_id
from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.screener.schema import ScreenQuery

router = APIRouter(prefix="/v1", tags=["saved_screens"])


class SavedScreenCreate(BaseModel):
    name: str
    query: ScreenQuery


class SavedScreenRename(BaseModel):
    name: str


@router.get("/screens")
def list_screens(user_id: str = Depends(get_current_user_id)) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id, name, query, created_at, updated_at from app.saved_screen where user_id = %s order by id",
                (user_id,),
            )
            rows = cur.fetchall()
    return [
        {"id": r[0], "name": r[1], "query": r[2], "created_at": str(r[3]), "updated_at": str(r[4])}
        for r in rows
    ]


@router.post("/screens")
def create_screen(body: SavedScreenCreate, user_id: str = Depends(get_current_user_id)) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into app.saved_screen (user_id, name, query) values (%s, %s, %s) returning id",
                # model_dump_json(), not json.dumps(model_dump()) -- found live
                # 2026-08-17: raw json.dumps can't serialize Decimal (a
                # MetricPredicate.value), and bypasses the same
                # Decimal-as-string handling FastAPI's response encoder
                # already gets right automatically. Pydantic's own JSON
                # serializer handles it correctly, same guarantee, explicit.
                (user_id, body.name, body.query.model_dump_json()),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
    return {"id": new_id, "name": body.name}


def _get_owned_screen(conn, screen_id: int, user_id: str):
    with conn.cursor() as cur:
        cur.execute("select user_id from app.saved_screen where id = %s", (screen_id,))
        row = cur.fetchone()
    # str(row[0]), not row[0] -- found live 2026-08-17: psycopg returns a
    # uuid.UUID object for a `uuid` column, never equal to the plain string
    # user_id this app gets back from Supabase Auth, so this check failed
    # closed for EVERY caller, including the rightful owner (a functional
    # bug, not a security hole -- it never let an unauthorized delete
    # through, it blocked authorized ones too).
    if row is None or str(row[0]) != user_id:
        raise HTTPException(status_code=404, detail="Screen not found")


@router.patch("/screens/{screen_id}")
def rename_screen(screen_id: int, body: SavedScreenRename, user_id: str = Depends(get_current_user_id)) -> dict:
    with get_connection() as conn:
        _get_owned_screen(conn, screen_id, user_id)
        with conn.cursor() as cur:
            cur.execute(
                "update app.saved_screen set name = %s, updated_at = now() where id = %s",
                (body.name, screen_id),
            )
        conn.commit()
    return {"id": screen_id, "name": body.name}


@router.delete("/screens/{screen_id}")
def delete_screen(screen_id: int, user_id: str = Depends(get_current_user_id)) -> dict:
    with get_connection() as conn:
        _get_owned_screen(conn, screen_id, user_id)
        with conn.cursor() as cur:
            cur.execute("delete from app.saved_screen where id = %s", (screen_id,))
        conn.commit()
    return {"deleted": screen_id}
