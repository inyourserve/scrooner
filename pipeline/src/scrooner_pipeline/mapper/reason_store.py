"""Lane 2's reason sink for guard-hidden cells (migration 0100, lane 1).

  * ``BlankReason``        one reason a guard produced (lane-2 shape); the key
                           fields are the frozen cell key.
  * ``ReasonSink``         what a guard calls; the guard never touches SQL.
  * ``NullReasonSink``     default; drops the row (the metric_value row still
                           carries ``is_null_reason``).
  * ``InMemoryReasonSink`` for tests and the dry-run CSV.
  * ``DbReasonSink``       maps to lane 1's store: ``cell_store.guard_hidden`` ->
                           ``replace_rule_reasons`` into ``analytics.cell_blank_reason``
                           under a ``rule_run`` id from ``start_rule_run``.

Mapping (Chief 2026-10-22): data_point_name -> data_point_name; period_grain as
given ('I' for instants, then period_start == period_end, enforced by CellKey);
basis 'latest'; run_id = the rule_run id the CALLER started; detail ->
input_refs; state 'defect', class guard_hidden. The sink buffers; ``flush`` writes
(one delete+insert per company and rule, never wider) and never commits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

# Frozen cell key (FREEZE-REGISTER section 2); run_id is added by the store.
CELL_KEY_FIELDS = (
    "company_id",
    "data_point_name",
    "period_grain",
    "period_start",
    "period_end",
    "basis",
)


@dataclass(frozen=True)
class BlankReason:
    company_id: int
    data_point_name: str
    period_grain: str
    period_start: date | None
    period_end: date | None
    rule_id: str
    reason_code: str
    basis: str = "latest"
    state: str = "defect"
    defect_class: str = "guard_hidden"
    owner: str = "data_engineer_l2"
    root_cause_class: str | None = None
    evidence_ref: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)

    def key(self) -> tuple:
        return tuple(getattr(self, name) for name in CELL_KEY_FIELDS)


class ReasonSink(Protocol):
    def add(self, reason: BlankReason) -> None: ...


class NullReasonSink:
    def add(self, reason: BlankReason) -> None:
        return None


class InMemoryReasonSink:
    def __init__(self) -> None:
        self.rows: list[BlankReason] = []

    def add(self, reason: BlankReason) -> None:
        self.rows.append(reason)


class DbReasonSink:
    """Buffers reasons and writes them through lane 1's cell_store."""

    def __init__(self, conn: Any, run_id: str) -> None:
        self.conn = conn
        self.run_id = run_id
        self._buffer: list[BlankReason] = []

    def add(self, reason: BlankReason) -> None:
        if reason.period_start is None or reason.period_end is None:
            raise ValueError("a stored reason needs period_start and period_end")
        self._buffer.append(reason)

    def flush(self) -> int:
        from scrooner_pipeline.common import cell_contract as cc
        from scrooner_pipeline.common import cell_store as cs

        grouped: dict[tuple[int, str], list[Any]] = {}
        for r in self._buffer:
            key = cc.CellKey(
                r.company_id,
                r.data_point_name,
                r.period_grain,
                r.period_start,  # type: ignore[arg-type]
                r.period_end,  # type: ignore[arg-type]
                r.basis,
            )
            grouped.setdefault((r.company_id, r.rule_id), []).append(
                cs.guard_hidden(
                    key,
                    r.rule_id,
                    r.reason_code,
                    r.owner,
                    root_cause_class=r.root_cause_class,
                    input_refs=dict(r.detail),
                )
            )
        written = 0
        for (company_id, rule_id), reasons in grouped.items():
            written += cs.replace_rule_reasons(
                self.conn, self.run_id, company_id, rule_id, reasons
            )
        self._buffer = []
        return written
