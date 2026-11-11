"""Predecessor routing (core.company_history_source, migration 0121).

A company's pre-reorganisation history sits in another CIK's SEC data (XOM: holding company
0002115436, history under 0000034088). The collector stores that CIK's raw payloads like any other
(lossless, no mapping); the normalizer attributes the rows whose period falls inside the
'predecessor' window to the SUCCESSOR's core.company id. Facts keep their own (predecessor)
accession numbers, so they never collide with the successor's own comparatives (a different
filing_id in the same unique key)."""

from __future__ import annotations

from datetime import date
from typing import NamedTuple

import psycopg


class Route(NamedTuple):
    company_id: int
    valid_from: date
    valid_to: date

    def contains(self, d: date | None) -> bool:
        return d is not None and self.valid_from <= d <= self.valid_to


def _table_exists(conn: psycopg.Connection) -> bool:
    return conn.execute("select to_regclass('core.company_history_source')").fetchone()[0] is not None


def predecessor_source_ciks(conn: psycopg.Connection) -> set[str]:
    """Every source CIK with a 'predecessor' window (the collector fetches these too)."""
    if not _table_exists(conn):
        return set()
    rows = conn.execute(
        "select distinct source_cik from core.company_history_source where relation = 'predecessor'"
    ).fetchall()
    return {r[0] for r in rows}


def predecessor_routes(conn: psycopg.Connection, cik: str) -> list[Route]:
    if not _table_exists(conn):
        return []
    rows = conn.execute(
        """select company_id, valid_from, valid_to from core.company_history_source
           where source_cik = %s and relation = 'predecessor' order by valid_from""",
        (cik,),
    ).fetchall()
    return [Route(*r) for r in rows]
