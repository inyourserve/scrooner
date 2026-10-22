"""Lane 2's view of the unified rule flags (common/rule_flags.py, lane 1).

The flag logic and the rule registry live in
`scrooner_pipeline.common.rule_flags`; this module re-exports what the lane-2
metric stages use and keeps the in-process decision log (a guard returns plain
values, the reason it blanked one travels here, and the dry-run records what
it WOULD have done).

Modes: off (default, legacy byte for byte), dry_run (decision recorded, legacy
value written), on. Environment: SCROONER_RULES_ENABLED / SCROONER_RULES_DRYRUN,
set only by the manual dispatch of pipeline-recompute.yml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from scrooner_pipeline.common.rule_flags import (  # noqa: F401  (re-exports)
    DRY_RUN,
    ENV_DRYRUN,
    ENV_ENABLED,
    OFF,
    ON,
    RULES,
    parse_rule_ids,
    rule_mode,
)

# Rule IDs implemented in this lane (FREEZE-REGISTER 3.2); registered in
# common/rule_flags.RULES.
RF01_CONSECUTIVE_WINDOW = "ttm.consecutive_window@1"
RF02_AGE_GUARD = "ttm.age_guard@2"
RF10_BS_DATE_ANCHOR = "pershare.balance_sheet_date_anchor@1"
# total_shareholder_yield (Chief rulings 2026-10-22): stale/misaligned components
# are tsy.stale_component@1; a component with no buyback/dividend TTM (priced as
# 0 today) is lane 1's RF-08 composite.unknown_not_zero@1 applied to TSY. Real
# zeros return as evidenced_zero when RF-36 and cell_evidence land.
RF_TSY_STALE = "tsy.stale_component@1"
RF_TSY_UNEVIDENCED_ZERO = "composite.unknown_not_zero@1"


@dataclass(frozen=True)
class GuardDecision:
    """One decision of one guard on one cell (fields follow the frozen cell key).

    outcome: ``hidden`` (value would be/was blanked), ``kept`` (guard passed),
    ``changed`` (a different value would be/was written).
    """

    rule_id: str
    mode: str
    company_id: int
    data_point: str
    period_grain: str
    period_start: date | None
    period_end: date | None
    outcome: str
    reason_code: str | None
    old_value: Decimal | None
    new_value: Decimal | None
    detail: str = ""
    consumers: tuple[str, ...] = ()
    basis: str = "latest"


@dataclass
class DecisionLog:
    """In-process record of guard decisions for one run.

    Metric code returns plain values (many tests monkeypatch those helpers), so
    the reason a guard blanked a value travels here. It is single-threaded by
    design: the mapper stages are single-threaded loops.
    """

    decisions: list[GuardDecision] = field(default_factory=list)

    def add(self, decision: GuardDecision) -> None:
        self.decisions.append(decision)

    def reason_for(self, company_id: int, data_point: str) -> str | None:
        """Reason code of the latest ``hidden`` decision for the cell, in mode ``on`` only."""
        for d in reversed(self.decisions):
            if (
                d.company_id == company_id
                and d.data_point == data_point
                and d.mode == ON
                and d.outcome == "hidden"
            ):
                return d.reason_code
        return None

    def clear_company(self, company_id: int) -> None:
        self.decisions = [d for d in self.decisions if d.company_id != company_id]

    def drain(self) -> list[GuardDecision]:
        out, self.decisions = self.decisions, []
        return out


DECISIONS = DecisionLog()


def decision_as_row(d: GuardDecision) -> dict[str, Any]:
    return {
        "rule_id": d.rule_id,
        "mode": d.mode,
        "company_id": d.company_id,
        "data_point": d.data_point,
        "period_grain": d.period_grain,
        "period_start": d.period_start,
        "period_end": d.period_end,
        "basis": d.basis,
        "outcome": d.outcome,
        "reason_code": d.reason_code,
        "old_value": d.old_value,
        "new_value": d.new_value,
        "consumers": ";".join(d.consumers),
        "detail": d.detail,
    }
