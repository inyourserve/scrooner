"""Per-rule release flags for value-changing Tier 0 guards (Data Engineer lane 2).

Why this exists (data-team/strategy/team/WO-REVIEW-release-manager.md section 2,
FREEZE-REGISTER-2026-10-22.md section 3): a guard that changes STORED metrics
must not reach the nightly run before a reviewed dry-run, a Verifier sample and
a rehearsed rollback. So every such guard is gated by a rule ID and has three
modes:

  off      (default)  the legacy behaviour, byte for byte.
  dry_run             the guard is evaluated and its decision is recorded in
                      DECISIONS, but the legacy value is still what is written.
  on                  the guard's value/blank is written.

The flags are read from the process environment, never from code:

  SCROONER_RULES_ENABLED   comma separated rule IDs that run in mode "on"
  SCROONER_RULES_DRYRUN    comma separated rule IDs that run in mode "dry_run"

The environment variables are set ONLY by a manual workflow_dispatch input on
pipeline-recompute.yml (the Release Manager owns that workflow edit). They are
deliberately not GitHub repository variables: a variable would also reach the
nightly run and split the population on the first live run (the RU-1 problem).
Unset or empty means every rule is off. A rule in both lists is rejected: an
ambiguous flag must stop the run, not pick a side.

Rule IDs have the shape ``family.rule@N`` (frozen scheme, FREEZE-REGISTER 3.1).
IDs this module does not know are accepted and ignored here, because other
lanes read the same variables for their own rules; only a malformed ID is an
error (a typo that silently meant "off" would hide a guard, one that silently
meant "on" would publish one).
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

ENV_ENABLED = "SCROONER_RULES_ENABLED"
ENV_DRYRUN = "SCROONER_RULES_DRYRUN"

OFF = "off"
DRY_RUN = "dry_run"
ON = "on"

# Rule IDs implemented in this lane (FREEZE-REGISTER 3.2).
RF01_CONSECUTIVE_WINDOW = "ttm.consecutive_window@1"
RF02_AGE_GUARD = "ttm.age_guard@1"
RF10_BS_DATE_ANCHOR = "pershare.balance_sheet_date_anchor@1"

_RULE_ID = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*@[0-9]+$")


def parse_rule_ids(raw: str | None) -> frozenset[str]:
    """Parse a comma separated list of rule IDs; blank entries are ignored."""
    if not raw:
        return frozenset()
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if not _RULE_ID.match(part):
            raise ValueError(
                f"malformed rule id {part!r}; expected family.rule@N (e.g. {RF01_CONSECUTIVE_WINDOW})"
            )
        ids.append(part)
    return frozenset(ids)


def rule_mode(rule_id: str, environ: Mapping[str, str] | None = None) -> str:
    """off | dry_run | on for one rule, from the environment (default OFF)."""
    env = os.environ if environ is None else environ
    enabled = parse_rule_ids(env.get(ENV_ENABLED))
    dry = parse_rule_ids(env.get(ENV_DRYRUN))
    both = enabled & dry
    if both:
        raise ValueError(
            f"rule(s) {sorted(both)} are in both {ENV_ENABLED} and {ENV_DRYRUN}"
        )
    if rule_id in enabled:
        return ON
    if rule_id in dry:
        return DRY_RUN
    return OFF


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
