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

`/v1/screen-runs` (screen_runs.py) is NOT cached here -- it already
persists its result permanently per-run (app.screen_run_result), a
stronger guarantee than a shared cache and one this module would only
complicate.
"""

import json
import os
from decimal import Decimal

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
