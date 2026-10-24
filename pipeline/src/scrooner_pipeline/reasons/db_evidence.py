"""Read-only evidence loaders: ONE connection, explicit statement_timeout, read-only
transaction, a guard on the number of application sessions already open.

Nothing here writes. The connection is opened with default_transaction_read_only
and every statement runs under the timeout; a refused guard raises before any
evidence query is issued."""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from typing import Any

import psycopg

from scrooner_pipeline.reasons.inputs import Evidence, LineEvidence, TagPresence
from scrooner_pipeline.reasons.model import CellKey
from scrooner_pipeline.reasons.rules import (
    FAMILIES,
    LINE_DATA_POINTS,
    family_signal,
)

STATEMENT_TIMEOUT_MS = 20_000
MAX_APP_BACKENDS = 12


class BackendGuardError(RuntimeError):
    pass


def connect_read_only(url: str | None = None) -> psycopg.Connection[Any]:
    dsn = url or os.environ["DATABASE_URL"]
    return psycopg.connect(
        dsn,
        connect_timeout=15,
        autocommit=False,
        options=(
            f"-c statement_timeout={STATEMENT_TIMEOUT_MS} "
            "-c default_transaction_read_only=on "
            "-c idle_in_transaction_session_timeout=60000"
        ),
    )


def check_backend_guard(
    conn: psycopg.Connection[Any], limit: int = MAX_APP_BACKENDS
) -> int:
    """Application sessions (role postgres through the pooler) must be at or below
    `limit` before we add ours. Supabase's own service sessions are not ours."""
    with conn.cursor() as cur:
        cur.execute("select count(*) from pg_stat_activity where usename = 'postgres'")
        row = cur.fetchone()
    n = int(row[0]) if row else 0
    if n > limit:
        raise BackendGuardError(
            f"{n} application backends open (limit {limit}); not starting"
        )
    return n


def load_line_evidence(
    conn: psycopg.Connection[Any], company_ids: Sequence[int]
) -> dict[CellKey, LineEvidence]:
    out: dict[CellKey, LineEvidence] = {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id, data_point, statement, line_present, combined,
                   matched_label, accession_number, form
            from analytics.company_filing_line_evidence
            where company_id = any(%(ids)s) and data_point = any(%(dps)s)
            """,
            {"ids": list(company_ids), "dps": sorted(LINE_DATA_POINTS)},
        )
        for cid, dp, stmt, present, comb, label, acc, form in cur.fetchall():
            out[(int(cid), dp)] = LineEvidence(
                stmt, present, bool(comb), label, acc, form
            )
    return out


def load_tag_presence(
    conn: psycopg.Connection[Any], company_ids: Sequence[int]
) -> dict[int, TagPresence]:
    """Per company: distinct tags filed, and which activity families have a signal
    tag. Tags are pulled by a coarse SQL include filter and classified by the same
    Python predicate the unit tests exercise (`family_signal`)."""
    coarse = "|".join(f"({f.include})" for f in FAMILIES.values())
    counts: dict[int, int] = {}
    fams: dict[int, set[str]] = {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id, count(*) from analytics.company_sec_tag
            where company_id = any(%(ids)s) group by 1
            """,
            {"ids": list(company_ids)},
        )
        for cid, n in cur.fetchall():
            counts[int(cid)] = int(n)
        cur.execute(
            """
            select distinct t.company_id, c.tag
            from analytics.company_sec_tag t join core.concept c on c.id = t.concept_id
            where t.company_id = any(%(ids)s) and c.tag ~ %(coarse)s
            """,
            {"ids": list(company_ids), "coarse": coarse},
        )
        for cid, tag in cur.fetchall():
            for fam in FAMILIES:
                if family_signal(tag, fam):
                    fams.setdefault(int(cid), set()).add(fam)
    return {
        cid: TagPresence(n, frozenset(fams.get(cid, ()))) for cid, n in counts.items()
    }


def load_evidence(
    conn: psycopg.Connection[Any], company_ids: Iterable[int]
) -> Evidence:
    ids = sorted(set(company_ids))
    return Evidence(
        line=load_line_evidence(conn, ids),
        tags=load_tag_presence(conn, ids),
        source="database (read-only)",
    )
