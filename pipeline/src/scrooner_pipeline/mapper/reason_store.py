"""Interface stub for the cell reason store (migration 0100, lane 1).

Lane 1 owns migration 0100 (`analytics.cell_blank_reason`, run scoped, keyed by
DATES not by core.period ids; WO-REVIEW-data-engineer.md section 2.4 and
FREEZE-REGISTER section 2). It is not on origin/main yet, so this module only
fixes the shape lane 2's guards write against:

  * ``BlankReason``       one reason row; the key fields are the frozen cell key
                          (company, data_point_name, period_grain, period_start,
                          period_end, basis) plus the run id.
  * ``ReasonSink``        what a guard calls; the guard never touches SQL.
  * ``NullReasonSink``    default; drops the row (the metric_value row still
                          carries ``is_null_reason``, so nothing is lost for
                          metric cells).
  * ``InMemoryReasonSink`` for tests and the dry-run CSV.
  * ``DbReasonSink``      raises ``ReasonStoreUnavailable`` until 0100 is applied
                          and lane 1 supplies the writer; ASSUMED column names
                          are listed in ``ASSUMED_COLUMNS`` so the swap is a
                          one-file change reviewed against the real DDL.

Nothing here writes to a database.
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

# ASSUMED (migration 0100 is not written yet): the non-key columns a guard fills.
ASSUMED_COLUMNS = (
    "run_id",
    "rule_id",
    "reason_code",
    "state",
    "defect_class",
    "owner",
    "evidence_ref",
    "detail",
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
    evidence_ref: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)

    def key(self) -> tuple:
        return tuple(getattr(self, name) for name in CELL_KEY_FIELDS)


class ReasonStoreUnavailable(RuntimeError):
    pass


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
    """Placeholder for lane 1's writer; refuses to run until 0100 exists."""

    def add(self, reason: BlankReason) -> None:
        raise ReasonStoreUnavailable(
            "analytics.cell_blank_reason (migration 0100) is not available on this branch; "
            "wire lane 1's writer here after it lands (origin/work/data-engineer/lane1-reason-store: common/cell_store.guard_hidden + write_blank_reasons; map BlankReason -> CellKey + guard_hidden(rule_id, reason_code, owner, input_refs=detail))"
        )
