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

Raised from 30s to 300s (matching CATALOG_TTL_SECONDS below) 2026-10-02
-- a rebuild is at most once/day, so a 30s window bought nothing but
extra ~270-300ms cold round trips on the create-screen hot path during
any gap in sustained traffic (measured live: a single cold snapshot
query from this dev machine to Supabase costs 1.6-2.3s on its own,
dominated by network, not computation -- see
doc/learnings/2026-10-02-create-screen-latency-audit.md). No
correctness tradeoff: still well under the ~1/day real change rate.
"""

import time

import psycopg

from scrooner_pipeline.screener.resolve import load_screenable_metric_catalog
from scrooner_pipeline.screener.snapshot import get_dataset_version

TTL_SECONDS = 300

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


# Same idea for the screenable metric catalog (metric_name -> id): it only
# changes when a metric_definition is added, which also needs a snapshot
# rebuild before it is screenable, so a short TTL is safe. Saves one
# ~280ms round trip on every Redis-miss screen run (measured 2026-09-26).
CATALOG_TTL_SECONDS = 300

_cached_catalog: dict[str, int] | None = None
_catalog_expires_at: float = 0.0


def get_cached_metric_catalog(conn: psycopg.Connection) -> dict[str, int]:
    global _cached_catalog, _catalog_expires_at
    now = time.monotonic()
    if _cached_catalog is not None and now < _catalog_expires_at:
        return _cached_catalog
    _cached_catalog = load_screenable_metric_catalog(conn)
    _catalog_expires_at = now + CATALOG_TTL_SECONDS
    return _cached_catalog
