"""Process-wide Postgres connection pool for apps/backend (doc/faster-
loading/fast.md's <100ms cached-screen / <300ms new-screen budgets are
unreachable without this). scrooner_pipeline.db.connection.get_connection()
opens a brand-new psycopg connection per call -- correct for pipeline's
one-shot CLI jobs, which each run once and exit, but wrong for a
long-running FastAPI process serving many short requests: measured live
2026-09-10, a fresh connect() against this project's Supabase pooler
costs ~1.7s for TCP+TLS+auth alone, on top of the ~270ms per-round-trip
network latency doc/learnings/2026-09-10-screener-performance.md already
documents -- that ~1.7s would dominate every single request's latency,
cache hit or not, if paid on every call.

A module-level pool, opened via FastAPI's lifespan hook (main.py) rather
than at import time -- `open=False` here, `open_pool()`/`close_pool()`
called from `lifespan()` -- so pool startup happens inside an event loop
FastAPI actually controls, not whatever context first imports this
module. Small max_size deliberately -- root CLAUDE.md's own "shared
Supabase pooler caps total concurrent client connections at ~15" note
applies here exactly as it does to any other service sharing this
project's connection string.
"""

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg_pool import ConnectionPool

from scrooner_pipeline.common.config import settings

_pool = ConnectionPool(
    settings.database_url,
    min_size=1,
    max_size=5,
    open=False,
    # Most use of this pool is read-only (the Screener never writes) or a
    # single-statement write (_log_usage's one INSERT) -- neither needs an
    # explicit multi-statement transaction, and autocommit avoids paying an
    # implicit BEGIN on first use plus a ROLLBACK round trip on every
    # checkout (measured live 2026-09-10: ~0.55s extra per request from
    # this dev machine alone) that psycopg3's default (autocommit=False)
    # costs otherwise. No caller here needs a multi-statement transaction
    # any more (create_run_from_query is a single CTE statement since
    # 2026-09-20); if one ever does, psycopg3's `conn.transaction()` scopes
    # a real transaction inside an autocommit connection.
    kwargs={"autocommit": True},
)

# Dedicated, tiny pool for fire-and-forget usage logging. It must NOT share
# _pool: measured live 2026-09-10, background work on the shared pool
# blocked the main response by ~260ms. It must also not open a fresh
# connection per call (~1.7s connect each, unbounded under a burst of
# concurrent requests) -- this project's pooler caps TOTAL client
# connections at ~15 across every service, so a bounded pool here keeps
# usage logging from ever starving request traffic. min_size=0: no
# connection is held until the first log call.
_usage_pool = ConnectionPool(
    settings.database_url,
    min_size=0,
    max_size=2,
    open=False,
    kwargs={"autocommit": True},
)


def open_pool() -> None:
    """Open and validate the bounded pool during application startup."""
    _pool.open(wait=True)
    _usage_pool.open(wait=False)


def close_pool() -> None:
    """Return database resources during graceful application shutdown."""
    _pool.close()
    _usage_pool.close()


@contextmanager
def get_pooled_connection() -> Iterator[psycopg.Connection]:
    with _pool.connection() as conn:
        yield conn


@contextmanager
def get_usage_connection() -> Iterator[psycopg.Connection]:
    with _usage_pool.connection() as conn:
        yield conn
