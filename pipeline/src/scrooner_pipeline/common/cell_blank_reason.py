"""Guard-side adapter over lane 1's reason store (``common/cell_store.py``, migration 0100).

Guards build ``BlankReason`` rows (company, data point, dates, rule, a rule-specific reason code,
detail) and hand them to a store with ``replace(company_id, rule_id, run_id, reasons)``:
* ``PgBlankReasonStore`` maps them onto ``cell_store.guard_hidden`` (state ``defect``, defect class
  ``guard_hidden``, a family owner) and ``cell_store.replace_rule_reasons`` (delete scope = run +
  company + rule). The run is a ``analytics.rule_run`` uuid from ``start_rule_run``; the store
  starts one per rule on first use (mode apply, flag on) when the caller does not pass a uuid, and
  ``finish()`` closes them.
* ``InMemoryBlankReasonStore`` has the same scope check, for tests.

Mapping from the first stub (lane 1, 2026-10-22): data_point -> data_point_name; period grain
instant -> I, FY/Q/TTM unchanged, YTD -> TP; basis resolved -> latest (as_filed is the other
value); detail -> input_refs; period_start and period_end are never null (equal for instants).
``reason_code`` must be rule-specific: a state or defect class name is rejected.
A cell the template does not use (D-4 employee count) is state ``not_in_template``, not a defect.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import psycopg

from scrooner_pipeline.common import cell_store
from scrooner_pipeline.common.cell_contract import (
    BLANK_STATES,
    DEFECT_CLASSES,
    OWNERS,
    PERIOD_GRAINS,
    STATES,
    CellKey,
    parse_rule_id,
)

_GRAIN = {"instant": "I", "YTD": "TP"}
_BASIS = {"resolved": "latest"}
FORBIDDEN_CODES = frozenset(STATES | DEFECT_CLASSES)


@dataclass(frozen=True)
class BlankReason:
    company_id: int
    data_point: str
    period_grain: str
    period_start: date
    period_end: date
    basis: str
    rule_id: str
    reason_code: str
    detail: dict[str, Any] = field(default_factory=dict, hash=False, compare=False)
    state: str = "defect"
    owner: str = "data_engineer_l1"

    def __post_init__(self) -> None:
        parse_rule_id(self.rule_id)
        object.__setattr__(
            self, "period_grain", _GRAIN.get(self.period_grain, self.period_grain)
        )
        object.__setattr__(self, "basis", _BASIS.get(self.basis, self.basis))
        if self.period_grain not in PERIOD_GRAINS:
            raise ValueError(
                f"period_grain {self.period_grain!r} not in {sorted(PERIOD_GRAINS)}"
            )
        if self.period_start is None or self.period_end is None:
            raise ValueError(
                "period_start and period_end are required (equal for instants)"
            )
        if self.state not in BLANK_STATES:
            raise ValueError(f"state {self.state!r} is not a blank state")
        if not self.reason_code or self.reason_code in FORBIDDEN_CODES:
            raise ValueError(
                f"reason_code {self.reason_code!r} must be rule-specific, not a state or defect class"
            )
        if self.state == "defect" and self.owner not in OWNERS:
            raise ValueError(f"owner {self.owner!r} not in the frozen owner list")

    def key(self) -> CellKey:
        return CellKey(
            self.company_id,
            self.data_point,
            self.period_grain,
            self.period_start,
            self.period_end,
            self.basis,
        )

    def to_store_row(self) -> cell_store.BlankReason:
        if self.state == "defect":
            return cell_store.guard_hidden(
                self.key(),
                self.rule_id,
                self.reason_code,
                self.owner,
                input_refs=dict(self.detail),
            )
        return cell_store.BlankReason(
            key=self.key(),
            state=self.state,
            rule_id=self.rule_id,
            reason_code=self.reason_code,
            input_refs=dict(self.detail),
        )


class BlankReasonStore:
    def replace(
        self, company_id: int, rule_id: str, run_id: str, reasons: Iterable[BlankReason]
    ) -> int:
        raise NotImplementedError


class InMemoryBlankReasonStore(BlankReasonStore):
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


def _is_uuid(text: str | None) -> bool:
    try:
        uuid.UUID(str(text))
        return True
    except ValueError:
        return False


class PgBlankReasonStore(BlankReasonStore):
    TABLE = "analytics.cell_blank_reason"

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn
        self._runs: dict[str, str] = {}

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

    def run_for(self, rule_id: str, run_id: str | None) -> str:
        if _is_uuid(run_id):
            return str(run_id)
        if rule_id not in self._runs:
            self._runs[rule_id] = cell_store.start_rule_run(
                self.conn, rule_id, "apply", "on", []
            )
        return self._runs[rule_id]

    def replace(
        self, company_id: int, rule_id: str, run_id: str, reasons: Iterable[BlankReason]
    ) -> int:
        self.require_table()
        batch = list(reasons)
        for r in batch:
            if r.company_id != company_id or r.rule_id != rule_id:
                raise ValueError("reason outside the replace scope")
        run = self.run_for(rule_id, run_id)
        return cell_store.replace_rule_reasons(
            self.conn, run, company_id, rule_id, [r.to_store_row() for r in batch]
        )

    def finish(self, stats: dict[str, Any] | None = None) -> None:
        for run in self._runs.values():
            cell_store.finish_rule_run(self.conn, run, stats or {})
        self._runs.clear()
