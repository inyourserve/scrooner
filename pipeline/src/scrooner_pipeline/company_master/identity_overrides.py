"""Durable identity overrides (rule identity.cik_name_ticker@1, RF-20).

Problem: the Company Master writers recompute their columns on every run from
sources that can be wrong or stale (status from filing recency, display_name
from yfinance, primary_ticker from listings). A manual correction written
straight into core.company is silently undone by the next nightly. So an
evidence-backed correction is recorded as a row of core.company_identity_audit
(migration 0100: old value, new value, accession, locator, rule, run) and the
writers consult this module: while the audit row is not reversed, the writer
leaves that company's field alone (or writes the audited value).

Field names used in the audit table:
  status          new_value = JSON {"status": ..., "reason": ...}
  display_name    new_value = the name
  primary_ticker  new_value = the ticker
  market_cap_hold new_value = JSON {"event_date": "YYYY-MM-DD"|null, "reason": ...}
  pseudo_ticker   new_value = JSON {"reason": ...}   (bond / preferred / subsidiary-security
                  "ticker": no market cap, outside the universe)
Authorization is the DATA, not an environment flag: an audit row exists only
after a reviewed apply (scripts/identity_fixes.py), and the nightly must honor
it or the fix would not be durable. With the table absent (migration 0100 not
applied) every function here is a no-op, so the code can ship first.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

import psycopg

OVERRIDE_FIELDS = (
    "status",
    "display_name",
    "primary_ticker",
    "market_cap_hold",
    "pseudo_ticker",
)


def _table_exists(conn: psycopg.Connection) -> bool:
    with conn.cursor() as cur:
        cur.execute("select to_regclass('core.company_identity_audit') is not null")
        return bool(cur.fetchone()[0])


def load_overrides(
    conn: psycopg.Connection, field: str, company_ids: Iterable[int] | None = None
) -> dict[int, str]:
    """company_id -> new_value of the latest unreversed audit row for `field`."""
    if field not in OVERRIDE_FIELDS:
        raise ValueError(f"not an override field: {field!r}")
    if not _table_exists(conn):
        return {}
    ids = None if company_ids is None else sorted(set(company_ids))
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (company_id) company_id, new_value
            from core.company_identity_audit
            where field = %s and reversed_at is null
              and (%s::bigint[] is null or company_id = any(%s))
            order by company_id, applied_at desc, id desc
            """,
            (field, ids, ids),
        )
        return {cid: val for cid, val in cur.fetchall() if val is not None}


@dataclass(frozen=True)
class MarketCapHold:
    event_date: date | None
    reason: str


def load_market_cap_holds(
    conn: psycopg.Connection, company_ids: Iterable[int]
) -> dict[int, MarketCapHold]:
    """Holds from either field (a dated event hold or a pseudo-ticker hold),
    one batched read for a whole run."""
    ids = list(company_ids)
    out: dict[int, MarketCapHold] = {}
    for field in (
        "pseudo_ticker",
        "market_cap_hold",
    ):  # the dated hold wins when both exist
        for cid, raw in load_overrides(conn, field, ids).items():
            data = json.loads(raw)
            ev = data.get("event_date")
            out[cid] = MarketCapHold(
                date.fromisoformat(ev) if ev else None, data["reason"]
            )
    return out


def load_market_cap_hold(
    conn: psycopg.Connection, company_id: int
) -> MarketCapHold | None:
    return load_market_cap_holds(conn, [company_id]).get(company_id)


def hold_blocks_share_count(
    hold: MarketCapHold, newest_share_as_of: date | None
) -> str | None:
    """Reason string when the hold stops a market cap, else None. A pseudo-ticker
    hold (no event date) always blocks. An event hold blocks until a share count
    dated on or after the event exists."""
    if hold.event_date is None:
        return f"hold:{hold.reason}"
    if newest_share_as_of is None or newest_share_as_of < hold.event_date:
        return f"hold:{hold.reason}"
    return None
