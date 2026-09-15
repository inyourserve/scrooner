"""Dataset-versioned Redis cache for the ad-hoc `/v1/screen` endpoint
(doc/faster-loading/fast.md item 3). A deliberate reversal of doc 02's
original "No Redis or Celery initially" lock -- explicit founder
direction, 2026-09-10, see doc/adr/0001-screener-redis-cache-and-
boolean-logic.md for the full reasoning and what was tried first
(precomputed snapshot table + indexing alone, see
doc/learnings/2026-09-10-screener-performance.md).

The cache key (scrooner_pipeline.screener.cache_key.compute_query_hash)
bakes in analytics.screening_dataset_version's current value, so a
snapshot rebuild mints new keys automatically -- correctness never
depends on TTL_SECONDS firing at the right time; that's a memory-hygiene
backstop only, same distinction doc 02's original caching note already
drew ("cache invalidates by bumping dataset_version, never by TTL").

`/v1/screen-runs` also keeps short-lived acceleration pointers here. The
database remains authoritative: immutable pages are cached by user/run/cursor,
and an exact repeated query can point back to its existing persisted run.
Every read degrades to Postgres when Redis is absent or stale.
"""

import json
import os
from decimal import Decimal
from hashlib import sha256

import redis
from redis.exceptions import RedisError

REDIS_URL = os.environ["REDIS_URL"]
TTL_SECONDS = 7 * 24 * 60 * 60

_client = redis.from_url(REDIS_URL, decode_responses=True)


def _default(o):
    if isinstance(o, Decimal):
        return str(o)
    return str(o)


def _key(query_hash: str) -> str:
    return f"screen:{query_hash}"


def _run_key(user_id: str, query_hash: str, query_text: str) -> str:
    # Keep user text out of Redis keys while making reuse exact: two phrases
    # that happen to compile to the same query remain distinct run records.
    text_hash = sha256(query_text.strip().encode()).hexdigest()
    return f"screen-run:{user_id}:{query_hash}:{text_hash}"


def _run_page_key(user_id: str, run_id: str, page_size: int, cursor: str | None) -> str:
    return f"screen-run-page:{user_id}:{run_id}:{page_size}:{cursor or 'first'}"


def get_cached_result(query_hash: str) -> dict | None:
    try:
        raw = _client.get(_key(query_hash))
    except RedisError:
        # Redis accelerates repeated screens; it must never make screening
        # unavailable. A cache outage falls through to Postgres.
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Treat a malformed entry exactly like a miss; the next successful
        # calculation replaces it.
        return None


def set_cached_result(query_hash: str, result: dict) -> None:
    try:
        _client.set(_key(query_hash), json.dumps(result, default=_default), ex=TTL_SECONDS)
    except RedisError:
        # Best-effort write: the database result is still authoritative.
        return


def get_cached_run_id(user_id: str, query_hash: str, query_text: str) -> str | None:
    try:
        value = _client.get(_run_key(user_id, query_hash, query_text))
    except RedisError:
        return None
    return value or None


def set_cached_run_id(user_id: str, query_hash: str, query_text: str, run_id: str) -> None:
    try:
        _client.set(_run_key(user_id, query_hash, query_text), run_id, ex=TTL_SECONDS)
    except RedisError:
        return


def get_cached_run_page(user_id: str, run_id: str, page_size: int, cursor: str | None) -> dict | None:
    try:
        raw = _client.get(_run_page_key(user_id, run_id, page_size, cursor))
    except RedisError:
        return None
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def set_cached_run_page(user_id: str, run_id: str, page_size: int, cursor: str | None, page: dict) -> None:
    try:
        _client.set(
            _run_page_key(user_id, run_id, page_size, cursor),
            json.dumps(page, default=_default),
            ex=TTL_SECONDS,
        )
    except RedisError:
        return


# Auth-verification cache (2026-09-12) -- found sanity-checking every
# authenticated screens endpoint's real end-to-end latency, not just the
# Postgres side: `auth.get_current_user_id` calls Supabase's own
# `GET /auth/v1/user` on EVERY single request, unconditionally, and that
# real network round trip measured live at ~370-710ms -- often MORE than
# the endpoint's own actual work (e.g. rename/delete dropped to ~245ms
# after this same audit's other fixes). None of the other caching in this
# file touched this at all, since it's a layer above the Screener.
#
# A short TTL (30s), not the 7-day TTL_SECONDS everything else here uses:
# this is the one cache in this module with an actual trust tradeoff, not
# just a performance one -- a token revoked (sign-out, password change,
# ban) mid-window would still resolve to its cached user_id for up to 30s.
# Judged acceptable because it doesn't change the underlying trust model:
# a Supabase access token is already valid for its own ~1hr lifetime
# regardless of this cache; this only affects how quickly *revocation*
# (not expiry) propagates, by well under a minute. Keyed by a hash of the
# token itself (never the raw token, even though it's a short-lived
# in-memory-adjacent cache) so a expired/rotated token can never serve a
# stale different token's cached identity.
AUTH_TTL_SECONDS = 30


def _auth_key(token: str) -> str:
    return f"auth-user:{sha256(token.encode()).hexdigest()}"


def get_cached_auth_user_id(token: str) -> str | None:
    try:
        return _client.get(_auth_key(token))
    except RedisError:
        return None


def set_cached_auth_user_id(token: str, user_id: str) -> None:
    try:
        _client.set(_auth_key(token), user_id, ex=AUTH_TTL_SECONDS)
    except RedisError:
        return


# Saved-screens list/detail cache (2026-09-15) -- routers/saved_screens.py's
# list_screens/get_screen were the one remaining piece of the screens/
# screener surface with NO caching at all, found auditing this file for
# "does every read here have the same treatment /v1/screen already got."
# Their own Postgres queries are sub-millisecond (EXPLAIN ANALYZE, checked
# live -- app.saved_screen/app.user_screen_run are tiny per-user tables,
# already correctly indexed) -- the actual cost avoided here is the
# Postgres round trip itself (this project's measured ~270ms/hop from a
# non-co-located client, doc/learnings/2026-09-10-screener-performance.md),
# not query execution. Short TTL (30s, matching AUTH_TTL_SECONDS's own
# reasoning) plus explicit invalidation on every write in this router --
# TTL alone is a memory-hygiene backstop, not the correctness mechanism, so
# a rename/delete/refresh is never visible late to the user who just made
# it. Caches ONLY the saved_screen row itself (id/name/slug/query/
# last_run_id/timestamps) -- never the run's own paginated result data,
# which already has its own, separate, correctness-sensitive caching via
# get_cached_run_page/set_cached_run_page above (keyed by run_id, which
# changes on every refresh, so it does not need this module's invalidation
# at all).
SCREENS_TTL_SECONDS = 30


def _screens_list_key(user_id: str) -> str:
    return f"screens-list:{user_id}"


def get_cached_screens_list(user_id: str) -> list | None:
    try:
        raw = _client.get(_screens_list_key(user_id))
    except RedisError:
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def set_cached_screens_list(user_id: str, screens: list) -> None:
    try:
        _client.set(_screens_list_key(user_id), json.dumps(screens, default=_default), ex=SCREENS_TTL_SECONDS)
    except RedisError:
        return


def invalidate_screens_list(user_id: str) -> None:
    try:
        _client.delete(_screens_list_key(user_id))
    except RedisError:
        return


def _screen_detail_key(user_id: str, slug: str) -> str:
    return f"screen-detail:{user_id}:{slug}"


def get_cached_screen_detail(user_id: str, slug: str) -> dict | None:
    try:
        raw = _client.get(_screen_detail_key(user_id, slug))
    except RedisError:
        return None
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def set_cached_screen_detail(user_id: str, slug: str, screen: dict) -> None:
    try:
        _client.set(_screen_detail_key(user_id, slug), json.dumps(screen, default=_default), ex=SCREENS_TTL_SECONDS)
    except RedisError:
        return


def invalidate_screen_detail(user_id: str, slug: str) -> None:
    try:
        _client.delete(_screen_detail_key(user_id, slug))
    except RedisError:
        return
