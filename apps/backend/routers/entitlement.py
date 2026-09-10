"""Stage 7c -- GET /v1/me/entitlement (doc 16). The "check paid user"
case named directly in the plan. Returns the real tier from
app.user_entitlement -- shape only, no limit enforcement (doc 02's
usage-limits policy is still open).
"""

from fastapi import APIRouter, Depends

from auth import get_current_user_id
from db_pool import get_pooled_connection

router = APIRouter(prefix="/v1", tags=["entitlement"])


@router.get("/me/entitlement")
def get_entitlement(user_id: str = Depends(get_current_user_id)) -> dict:
    # Pure read, single row -- the pooled connection skips the ~1.7s
    # TCP+TLS+auth cost scrooner_pipeline.db.connection.get_connection()'s
    # fresh-connection-per-call pays (see db_pool.py).
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select tier from app.user_entitlement where user_id = %s", (user_id,))
            row = cur.fetchone()
    tier = row[0] if row else "free"
    return {"tier": tier}
