"""Dry-run diff rows, rule-run manifest and restore plan for value-changing rule families.

Design (WO-REVIEW-release-manager.md 2.2 items 2-3, WO-REVIEW-data-engineer.md AT-DE-05/07):

* Before the first live run a family runs in dry-run mode and returns ``PlannedChange`` rows
  (company, data point, period end, before value, after value, reason code). Nothing is written.
* The rows are saved as a JSONL file (the before-image) next to a manifest naming the rule ID,
  flag state, ciks and counts. The manifest is also what migration 0100's ``analytics.rule_run``
  will store; until it lands the JSONL pair is the contract.
* Rollback is never hand SQL: the stored value of every row in the manifest is recomputed by the
  recompute workflow for the manifest ciks with the rule OFF (``restore_command``). The JSONL
  before-image is the evidence that the recompute reproduced the old values
  (``verify_restored``).
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class PlannedChange:
    rule_id: str
    cik: str
    company_id: int
    data_point: str
    period_end: date | None
    before: Decimal | None
    after: Decimal | None  # None = the cell becomes blank
    reason: str  # frozen reason code, e.g. "not_in_template"


def _enc(o: object) -> str:
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, date):
        return o.isoformat()
    raise TypeError(type(o))


def write_before_image(path: Path, changes: Iterable[PlannedChange]) -> int:
    n = 0
    with path.open("w") as fh:
        for c in changes:
            fh.write(json.dumps(asdict(c), default=_enc, sort_keys=True) + "\n")
            n += 1
    return n


def read_before_image(path: Path) -> list[PlannedChange]:
    out: list[PlannedChange] = []
    for line in path.read_text().splitlines():
        d = json.loads(line)
        out.append(
            PlannedChange(
                rule_id=d["rule_id"],
                cik=d["cik"],
                company_id=d["company_id"],
                data_point=d["data_point"],
                period_end=date.fromisoformat(d["period_end"])
                if d["period_end"]
                else None,
                before=Decimal(d["before"]) if d["before"] is not None else None,
                after=Decimal(d["after"]) if d["after"] is not None else None,
                reason=d["reason"],
            )
        )
    return out


def manifest(
    rule_id: str, changes: list[PlannedChange], *, flag_state: str
) -> dict[str, object]:
    ciks = sorted({c.cik for c in changes})
    return {
        "rule_id": rule_id,
        "flag_state": flag_state,
        "ciks": ciks,
        "cells_changed": len(changes),
        "cells_to_blank": sum(1 for c in changes if c.after is None),
        "cells_value_changed": sum(1 for c in changes if c.after is not None),
    }


def restore_command(man: dict[str, object]) -> str:
    """The recompute-workflow dispatch that restores the manifest's ciks with the rule OFF."""
    ciks = ",".join(man["ciks"])  # type: ignore[arg-type]
    return f"gh workflow run pipeline-recompute.yml -f ciks={ciks} -f rules_enabled=''  # rule {man['rule_id']} OFF"


def verify_restored(
    before: list[PlannedChange],
    current: dict[tuple[str, str, date | None], Decimal | None],
) -> list[PlannedChange]:
    """Rows whose current value does not equal the recorded ``before`` (empty list = restored)."""
    return [
        c
        for c in before
        if current.get((c.cik, c.data_point, c.period_end)) != c.before
    ]
