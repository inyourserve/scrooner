"""Reason-store contract for concept-level blanks (stub until migration 0100 is applied).

Why (WO-REVIEW-data-engineer.md F1): ``analytics.canonical_fact.value`` is ``numeric not null``,
so a guard that hides a concept cell can only delete the row, and the blank is then reasonless.
The reason must be stored beside the cell, keyed by DATES not ``core.period.id`` (a period
repair or relabel must not orphan it), scoped by run.

Planned table (migration 0100, lane 1; column names here are ASSUMED until it is committed):

    analytics.cell_blank_reason(
        company_id bigint, data_point text, period_grain text,
        period_start date, period_end date, basis text,
        rule_id text, reason_code text, detail jsonb, run_id text,
        primary key (company_id, data_point, period_grain, period_start, period_end, basis, run_id))

Rules for writers (AT-DE-03):
* A writer replaces ONLY its own rule's rows for the companies it processed
  (``company_id`` + ``rule_id`` + ``run_id``). Never ``delete ... where company_id``.
* If a guard hides a cell it MUST persist the reason through a store; a missing table is an
  error, never a silent skip (``PgBlankReasonStore.require_table``).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

import psycopg
from psycopg.types.json import Jsonb

REASON_CODES = frozenset(
    {
        # frozen list subset used by the guards in lane 3; the full enum is founder item D-1
        "not_in_template",
        "guard_hidden",
        "undefined_by_math",
        "definition_pending",
    }
)


@dataclass(frozen=True)
class BlankReason:
    company_id: int
    data_point: str
    period_grain: str  # "instant" | "FY" | "Q" | "TTM"
    period_start: date | None
    period_end: date | None
    basis: str  # e.g. "reported", "resolved"
    rule_id: str  # family.rule@N
    reason_code: str
    detail: dict[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __post_init__(self) -> None:
        if self.reason_code not in REASON_CODES:
            raise ValueError(f"reason_code {self.reason_code!r} not in the frozen list")
        if "@" not in self.rule_id:
            raise ValueError(f"rule_id {self.rule_id!r} must be family.rule@N")


class BlankReasonStore(Protocol):
    def replace(
        self, company_id: int, rule_id: str, run_id: str, reasons: Iterable[BlankReason]
    ) -> int:
        """Replace this rule's rows for this company in this run. Returns rows written."""
        ...


class InMemoryBlankReasonStore:
    """Test double with the exact delete scope of the Pg store."""

    def __init__(self) -> None:
        self.rows: dict[tuple[int, str, str], list[BlankReason]] = {}

    def replace(
        self, company_id: int, rule_id: str, run_id: str, reasons: Iterable[BlankReason]
    ) -> int:
        reasons = list(reasons)
        for r in reasons:
            if r.company_id != company_id or r.rule_id != rule_id:
                raise ValueError("reason outside the replace scope")
        self.rows[(company_id, rule_id, run_id)] = reasons
        return len(reasons)

    def all(self) -> list[BlankReason]:
        return [r for rs in self.rows.values() for r in rs]


class PgBlankReasonStore:
    TABLE = "analytics.cell_blank_reason"

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def table_exists(self) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("select to_regclass(%s) is not null", (self.TABLE,))
            row = cur.fetchone()
            return bool(row and row[0])

    def require_table(self) -> None:
        if not self.table_exists():
            raise RuntimeError(
                f"{self.TABLE} does not exist (migration 0100 not applied): a guard may not hide a cell"
            )

    def replace(
        self, company_id: int, rule_id: str, run_id: str, reasons: Iterable[BlankReason]
    ) -> int:
        self.require_table()
        reasons = list(reasons)
        for r in reasons:
            if r.company_id != company_id or r.rule_id != rule_id:
                raise ValueError("reason outside the replace scope")
        with self.conn.cursor() as cur:
            cur.execute(
                f"delete from {self.TABLE} where company_id = %s and rule_id = %s and run_id = %s",
                (company_id, rule_id, run_id),
            )
            if reasons:
                cur.executemany(
                    f"""insert into {self.TABLE}
                    (company_id, data_point, period_grain, period_start, period_end, basis,
                     rule_id, reason_code, detail, run_id)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    [
                        (
                            r.company_id,
                            r.data_point,
                            r.period_grain,
                            r.period_start,
                            r.period_end,
                            r.basis,
                            r.rule_id,
                            r.reason_code,
                            Jsonb(r.detail),
                            run_id,
                        )
                        for r in reasons
                    ],
                )
        return len(reasons)
