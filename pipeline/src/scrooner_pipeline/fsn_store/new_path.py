"""Which companies are on the new (hybrid FSN) nightly path, so the old normalize/map writers skip them.

Founder decisions relayed by Dhairya 2026-11-11: once a company is written from the FSN store its nightly
updates come from the hybrid path only, and the old path skips it entirely, at the writer, not cell by cell.

A company is on the new path once an applied FSN cell write has landed for it: it holds
analytics.slot_protected_cell rows whose run is an `fsn.*` rule run in apply mode (the protection rows are
written in the same transaction as the cells, cell_loader.protect_cells, so the switch happens in the same
step as the write), or it has an analytics.company_value_owner row (migration 0119) where that table exists.
A restore that removes the company's FSN protection rows takes it back to the old path.

The skip is behind HYBRID_NEW_PATH (off by default). With it on, a failure to read the set fails closed:
the caller raises (sanity) or skips the whole cohort (reprocess_recent_filers.sh) instead of writing.
"""

from __future__ import annotations

import os
from typing import Any

FLAG = "HYBRID_NEW_PATH"
STATEMENT_TIMEOUT = "15s"

NEW_PATH_SQL = """
select distinct p.company_id
from analytics.slot_protected_cell p
join analytics.rule_run r on r.run_id::text = p.run_id
where r.rule_id like 'fsn.%%' and r.mode = 'apply'
"""


def enabled() -> bool:
    return os.environ.get(FLAG, "off").strip().lower() == "on"


def company_ids(conn: Any) -> set[int]:
    """Every company on the new path (read-only, indexed, statement_timeout 15s)."""
    conn.execute(f"set statement_timeout = '{STATEMENT_TIMEOUT}'")
    ids = {int(r[0]) for r in conn.execute(NEW_PATH_SQL).fetchall()}
    if (
        conn.execute("select to_regclass('analytics.company_value_owner')").fetchone()[
            0
        ]
        is not None
    ):
        ids |= {
            int(r[0])
            for r in conn.execute(
                "select company_id from analytics.company_value_owner"
            ).fetchall()
        }
    conn.execute("reset statement_timeout")
    return ids


def ciks(conn: Any) -> list[str]:
    ids = sorted(company_ids(conn))
    rows = conn.execute(
        "select cik from core.company where id = any(%s) order by cik", (ids,)
    ).fetchall()
    return [r[0] for r in rows]


def excluded_company_ids(conn: Any) -> set[int]:
    """What an old-path writer must skip: the new-path companies when HYBRID_NEW_PATH=on, else nothing.
    A read failure raises (fail closed: the writer stops rather than write a new-path company)."""
    if not enabled():
        return set()
    return company_ids(conn)
