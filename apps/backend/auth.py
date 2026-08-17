"""Stage 7a -- Supabase Auth verification (doc 16). Supabase Auth is
already locked (doc 02); this consumes it, adds no new auth system.

Verifies the incoming bearer token by asking Supabase's own Auth API to
resolve it (GET /auth/v1/user), rather than validating the JWT signature
locally -- this project's env doesn't hold the project's JWT signing
secret (only SUPABASE_SERVICE_ROLE_KEY, a different credential), and
delegating verification to the identity provider that issued the token is
a standard, correct pattern, not a workaround. Costs one network round
trip per authenticated request; revisit if that latency ever matters at
real traffic volume (doc 05's "evidence before expansion" -- not
optimized preemptively).
"""

import os

import httpx
from fastapi import Header, HTTPException

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


async def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = resp.json()
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token did not resolve to a user")
    return user_id
