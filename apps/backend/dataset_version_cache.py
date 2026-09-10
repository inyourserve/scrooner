"""In-process TTL cache for analytics.screening_dataset_version's current
value. Fetching it costs one full round trip to Postgres (~270ms
measured from this dev machine, doc/learnings/2026-09-10-screener-
performance.md) -- on a cache-hit /v1/screen request, that round trip
plus usage logging's own round trip were the entire remaining latency
after Redis caching + connection pooling closed everything else.

Safe to cache briefly: the version only changes when
`scrooner-screen build-snapshot` runs (a deliberate, operator-triggered
batch job, at most once/day per root CLAUDE.md's own "no scheduled
reprocessing chain" note) -- never per-request. A bounded staleness
window here means "which snapshot generation is current" can lag a real
rebuild by up to TTL_SECONDS; it does NOT mean a cached *result* is ever
served under the wrong version number (query_hash still bakes in
whatever version this function returns, and a query never gets a result
computed under a different version than the one in its own hash) --
doc 02's original "invalidate by dataset_version, never TTL" concern was
about the actual screen results, which this doesn't touch.
"""

import time

import psycopg

from scrooner_pipeline.screener.snapshot import get_dataset_version

TTL_SECONDS = 30

_cached_version: int | None = None
_expires_at: float = 0.0


def get_cached_dataset_version(conn: psycopg.Connection) -> int:
    global _cached_version, _expires_at
    now = time.monotonic()
    if _cached_version is not None and now < _expires_at:
        return _cached_version
    _cached_version = get_dataset_version(conn)
    _expires_at = now + TTL_SECONDS
    return _cached_version
