"""Shared constants, hashing and small SQL helpers for the orchestrator (tables: migration 0136)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import psycopg

# PIPELINE.md stage numbers. A worker runs them in this order: stage 5 (certify request) is last.
STAGE_NAMES = {
    1: "ingest",
    2: "know",
    3: "resolve",
    4: "prove",
    5: "certify_request",
    6: "serve",
}
STAGE_ORDER = (1, 2, 3, 4, 6, 5)

CAUSES = ("new_filing", "rule_version", "rank_change", "template_change")
# where a cause enters the chain unless the event's versions carry an explicit "from_stage"
# (stages 3 and 4 run as one flow command, scripts/top100_flow.sh, so a template change enters at 3 too)
DEFAULT_FROM_STAGE = {
    "new_filing": 1,
    "rank_change": 3,
    "rule_version": 3,
    "template_change": 3,
}

MAX_ATTEMPTS = 3  # failures per work item before it is dead-lettered (PIPELINE.md "Failure handling")


def versions_hash(versions: dict[str, Any]) -> str:
    """sha256 of the canonical JSON (sorted keys, compact), the idempotency half of (cik, cause, versions)."""
    blob = json.dumps(versions, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def emit_event(
    conn: psycopg.Connection,
    *,
    cik: str,
    cause: str,
    versions: dict[str, Any],
    source: str,
) -> bool:
    """Record one trigger. Returns True when the row is new, False when an identical (cik, cause, versions) exists."""
    if cause not in CAUSES:
        raise ValueError(f"unknown cause {cause!r}")
    cur = conn.execute(
        """insert into ops.pipeline_event (cik, cause, versions, versions_hash, source)
           values (%s, %s, %s::jsonb, %s, %s)
           on conflict (cik, cause, versions_hash) do nothing returning id""",
        (
            cik,
            cause,
            json.dumps(versions, sort_keys=True, default=str),
            versions_hash(versions),
            source,
        ),
    )
    return cur.fetchone() is not None


def stage_index(stage: int) -> int:
    return STAGE_ORDER.index(stage)
