"""Frozen vocabularies (FREEZE-REGISTER-2026-10-22 section 1) and the data shapes
shared by the reason rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STATES = (
    "value",
    "derived",
    "evidenced_zero",
    "undefined_by_math",
    "history_horizon",
    "not_presented",
    "not_in_template",
    "defect",
)
LEGIT_STATES = frozenset(
    {
        "evidenced_zero",
        "undefined_by_math",
        "history_horizon",
        "not_presented",
        "not_in_template",
    }
)
DEFECT_CLASSES = (
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
)
OWNERS = (
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
)
# migration 0100 cell_blank_reason.root_cause_class check: guard_hidden is a hide,
# never a root cause, and finding_open is not listed.
ROOT_CAUSE_CLASSES = frozenset(DEFECT_CLASSES) - {"guard_hidden", "finding_open"}
EVIDENCE_LEVELS = ("FILING-CHECKED", "DATA-INFERRED")

CellKey = tuple[int, str]  # (company_id, data_point_name)


@dataclass(frozen=True)
class BaselineCell:
    """One cohort cell of the frozen scoreboard export (blank or valued-with-reason).
    A cohort cell absent from the export is valued with no defect."""

    company_id: int
    ticker: str
    data_point: str
    kind: str
    valued: bool
    gap_reason: str
    defect_class: str
    owner: str
    candidate_state: str
    root_cause_class: str

    @property
    def key(self) -> CellKey:
        return (self.company_id, self.data_point)

    @property
    def reasonless(self) -> bool:
        """Blank with no stored reason: the 13,349 cells this package closes."""
        return (not self.valued) and not self.gap_reason

    @property
    def classified(self) -> bool:
        """Blank with a reason that maps to a real class (not `unclassified`)."""
        return (
            (not self.valued)
            and bool(self.defect_class)
            and (self.defect_class != "unclassified")
        )


@dataclass(frozen=True)
class Closure:
    """A rule's decision for one reasonless cell."""

    company_id: int
    ticker: str
    data_point: str
    rule_id: str
    state: str  # frozen state, 'defect' when the evidence is not yet audited
    defect_class: str | None
    owner: str | None
    candidate_state: str | None  # the legitimate state the evidence supports
    wording_key: str | None
    candidate_wording_key: str | None
    evidence_level: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.state not in STATES:
            raise ValueError(f"state {self.state!r} not in the frozen enum")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise ValueError(f"evidence level {self.evidence_level!r}")
        if (self.state == "defect") != (self.defect_class is not None):
            raise ValueError("defect_class is set exactly when state is 'defect'")
        if (self.state == "defect") != (self.owner is not None):
            raise ValueError("owner is set exactly when state is 'defect'")
        if self.defect_class == "unclassified":
            raise ValueError(
                "a closure may not be 'unclassified' (that is the residue)"
            )
        if self.defect_class is not None and self.defect_class not in DEFECT_CLASSES:
            raise ValueError(f"defect class {self.defect_class!r}")
        if self.owner is not None and self.owner not in OWNERS:
            raise ValueError(f"owner {self.owner!r}")
        if not self.evidence:
            # a reason without an evidence reference is a fabricated reason
            raise ValueError("a closure must carry an evidence reference")

    @property
    def key(self) -> CellKey:
        return (self.company_id, self.data_point)

    @property
    def effective_state(self) -> str:
        """The legitimate state this closure stands for (itself, or its candidate)."""
        return self.candidate_state or self.state

    @property
    def is_pending(self) -> bool:
        return self.state == "defect"


def to_blank_reason_row(
    c: Closure, period_grain: str, period_start: str, period_end: str
) -> dict[str, Any]:
    """Shape a closure as a row of analytics.cell_blank_reason (migration 0100).
    The period of the expected latest cell is supplied by the caller; this
    package does not infer periods. `run_id` is added by the writer."""
    return {
        "company_id": c.company_id,
        "data_point_name": c.data_point,
        "period_grain": period_grain,
        "period_start": period_start,
        "period_end": period_end,
        "basis": "latest",
        "state": c.state,
        "defect_class": c.defect_class,
        "owner": c.owner,
        "root_cause_class": c.defect_class
        if c.defect_class in ROOT_CAUSE_CLASSES
        else None,
        "rule_id": c.rule_id,
        "reason_code": (c.candidate_state or c.state),
        "reason_text": c.wording_key,
        "input_refs": c.evidence,
    }
