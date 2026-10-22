"""Frozen vocabulary of the cell-state contract (data-team/strategy/
FREEZE-REGISTER-2026-10-22.md sections 1-3). Pure: no database access.

One home for the enums so the writers (common/cell_store.py), the SQL CHECK
constraints of migration 0100 and the tests cannot drift: a test parses the
migration and requires every CHECK list to equal the set defined here.

A cell is identified by its key, never by core.period.id or a fiscal label:
(company_id, data_point_name, period_grain, period_start, period_end, basis).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

# Register section 1: the eight cell states.
STATES = frozenset(
    {
        "value",
        "derived",
        "evidenced_zero",
        "undefined_by_math",
        "history_horizon",
        "not_presented",
        "not_in_template",
        "defect",
    }
)
# A blank cell can be in any state that is not a valued one.
BLANK_STATES = STATES - {"value", "derived"}

DEFECT_CLASSES = frozenset(
    {
        "vocabulary",
        "composition",
        "period",
        "ingestion",
        "resolver",
        "identity",
        "evidence_pending",
        "definition_pending",
        "guard_hidden",
        "finding_open",
        "filer_error",
        "unclassified",
    }
)
# The mechanism behind a guard_hidden cell (RULE-REGISTRY-DRAFT proposal): the
# table class of the family that hid it. guard_hidden / finding_open describe
# the mechanism itself, so they are not root causes.
ROOT_CAUSE_CLASSES = DEFECT_CLASSES - {"guard_hidden", "finding_open"}

OWNERS = frozenset(
    {
        "data_engineer_l1",
        "data_engineer_l2",
        "period_engineer",
        "tag_mapper",
        "standardization_lead",
        "accountant",
        "sector_analyst",
        "verifier",
        "triage",
        "company_master",
    }
)

# Register section 1: default owner per class (guard_hidden and finding_open
# take the owner of the rule family, so they have no default here).
DEFAULT_OWNER_BY_CLASS = {
    "vocabulary": "tag_mapper",
    "composition": "standardization_lead",
    "period": "period_engineer",
    "ingestion": "data_engineer_l2",
    "resolver": "data_engineer_l1",
    "identity": "data_engineer_l1",
    "evidence_pending": "sector_analyst",
    "definition_pending": "accountant",
    "filer_error": "verifier",
    "unclassified": "triage",
}

PERIOD_GRAINS = frozenset({"FY", "Q", "TTM", "I", "TP"})
BASES = frozenset({"latest", "as_filed"})

EVIDENCE_KINDS = frozenset(
    {
        "filing_check",
        "detector_audit",
        "verifier_sample",
        "exception",
        "accountant_ruling",
    }
)
EVIDENCE_LEVELS = frozenset({"FILING-CHECKED", "DATA-INFERRED"})

REGISTRANT_ROLES = frozenset({"primary", "co_registrant", "quarantined"})
RUN_MODES = frozenset({"dry_run", "apply", "rollback"})
FLAG_STATES = frozenset({"off", "on"})

# family.rule@N (register 3.1); certify detectors are cert.I<k>.<rule>@N.
RULE_ID_PATTERN = r"^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$"
_RULE_ID_RE = re.compile(RULE_ID_PATTERN)


def parse_rule_id(rule_id: str) -> tuple[str, int]:
    """Return (name, version) of a rule ID, or raise ValueError."""
    if not isinstance(rule_id, str) or not _RULE_ID_RE.match(rule_id):
        raise ValueError(f"not a rule ID of the form family.rule@N: {rule_id!r}")
    name, _, version = rule_id.rpartition("@")
    return name, int(version)


@dataclass(frozen=True)
class CellKey:
    """The frozen cell key. period_start == period_end for instants."""

    company_id: int
    data_point_name: str
    period_grain: str
    period_start: date
    period_end: date
    basis: str = "latest"

    def __post_init__(self) -> None:
        if not self.data_point_name:
            raise ValueError("data_point_name is required")
        if self.period_grain not in PERIOD_GRAINS:
            raise ValueError(f"unknown period_grain {self.period_grain!r}")
        if self.basis not in BASES:
            raise ValueError(f"unknown basis {self.basis!r}")
        if self.period_start > self.period_end:
            raise ValueError("period_start is after period_end")
        if self.period_grain == "I" and self.period_start != self.period_end:
            raise ValueError("an instant (grain I) needs period_start == period_end")

    def as_tuple(self) -> tuple:
        return (
            self.company_id,
            self.data_point_name,
            self.period_grain,
            self.period_start,
            self.period_end,
            self.basis,
        )


def validate_defect(
    state: str,
    defect_class: str | None,
    owner: str | None,
    root_cause_class: str | None,
) -> None:
    """Same rules as the CHECK constraints of analytics.cell_blank_reason."""
    if state not in STATES:
        raise ValueError(f"unknown state {state!r}")
    if state == "defect":
        if defect_class not in DEFECT_CLASSES:
            raise ValueError(
                f"defect needs a defect_class from the frozen list, got {defect_class!r}"
            )
        if owner not in OWNERS:
            raise ValueError(
                f"defect needs an owner from the frozen list, got {owner!r}"
            )
        if root_cause_class is not None and root_cause_class not in ROOT_CAUSE_CLASSES:
            raise ValueError(f"unknown root_cause_class {root_cause_class!r}")
    elif defect_class is not None or owner is not None or root_cause_class is not None:
        raise ValueError(
            "only state 'defect' may carry defect_class, owner or root_cause_class"
        )
