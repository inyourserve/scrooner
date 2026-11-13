"""What a metric cell records, and the rules that stop it computing from an unproven input.

Each metric cell record carries (Ritwik's approver requirements, 2026-11-13):
  * formula_ref `metric_id@version` plus the formula fingerprint and REGISTRY_VERSION;
  * its input cells, each PROVEN or a REASON (never a silent fallback);
  * the period basis;
  * a recomputation check (engine re-evaluation of the stored value from the recorded inputs).

Rule (c): a metric never computes from an input whose cell is not served. An input is served
only when its cell_proof verdict is PROVEN. A DISAGREE, UNCHECKED, held or missing input gives
a null with a reason. The single exception, evidence-gated: an input the filing does not present
(verdict NOT_PRESENTED) counts as zero for a concept the registry lists as `zero_when_absent`
for that metric (quick_ratio's inventory), because the evidence for the zero is the proof.

Version invalidation: `detector_version` of a metric proof row is `formula_ref#fingerprint|reg:<REGISTRY_VERSION>`.
`proof_is_stale` is true when the metric's version or its formula fingerprint changed; a label
edit changes REGISTRY_VERSION but not the fingerprint, so it does not stale proofs. A formula edit
without a version bump is caught by tests/unit/test_metric_registry_agreement.py via formula_lock.json.
No DDL: the proof row's existing `detector_version` and `checks` jsonb carry it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal

from scrooner_pipeline.metrics.engine import DictEnv, evaluate
from scrooner_pipeline.metrics.registry import Metric, compute_registry_version

SERVED_STATUSES = frozenset({"PROVEN"})
RULE_ID = "proof.metric_recompute@1"


def formula_fingerprint(m: Metric) -> str:
    """Hash of everything that changes what the metric computes (not its label or description)."""
    payload = json.dumps(
        {
            "id": m.metric_id,
            "version": m.version,
            "expression": m.expression,
            "status": m.expression_status,
            "seed_inputs": list(m.seed_inputs),
            "period_rule": m.period_rule,
            "ttm_rows": m.ttm_rows,
            "null_rules": m.null_rules,
            "requires_price": m.requires_price,
            "perimeter": list(m.perimeter),
            "calculator": m.calculator,
            "perimeter_spec": m.perimeter_spec,
            "applies_to": m.applies_to,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def detector_version(m: Metric, registry_version: str | None = None) -> str:
    return f"{m.formula_ref}#{formula_fingerprint(m)}|reg:{registry_version or compute_registry_version()}"


def value_stamp(m: Metric) -> dict[str, str | int]:
    """What each computed metric value carries (migration 0126 adds the metric_value columns)."""
    return {
        "formula_version": m.version,
        "formula_fingerprint": formula_fingerprint(m),
        "registry_version": compute_registry_version(),
    }


def proof_is_stale(proof_detector_version: str | None, m: Metric) -> bool:
    """True when a stored metric proof was made under a different version or formula."""
    if not proof_detector_version or "#" not in proof_detector_version:
        return True
    head = proof_detector_version.split("|", 1)[0]
    ref, _, fp = head.partition("#")
    return ref != m.formula_ref or fp != formula_fingerprint(m)


@dataclass(frozen=True)
class InputCell:
    concept: str
    status: str  # cell_proof verdict: PROVEN | DISAGREE | UNCHECKED | NOT_PRESENTED | HELD | MISSING
    value: Decimal | None = None
    reason: str | None = None
    proof_id: int | None = None
    rule_id: str | None = None  # company_tag_map.rule_id that selected this input's tag
    rules_commit: str | None = (
        None  # frozen rules commit behind that rule (predictor output)
    )


@dataclass(frozen=True)
class PeriodBasis:
    period_label: str  # FY | Q1..Q4 | TTM
    period_start: date | None
    period_end: date | None
    rule: str  # the registry period_rule applied


@dataclass(frozen=True)
class CellRecord:
    metric_id: str
    formula_ref: str
    fingerprint: str
    registry_version: str
    period: PeriodBasis
    inputs: tuple[InputCell, ...]
    value: Decimal | None
    reason: str | None
    recompute: dict = field(default_factory=dict)

    @property
    def verdict(self) -> str:
        if self.value is None:
            return "NOT_PRESENTED"  # a blank with its reason
        if self.recompute.get("status") == "mismatch":
            return "DISAGREE"
        if all(
            c.status == "PROVEN" or (c.status == "NOT_PRESENTED" and c.value == 0)
            for c in self.inputs
        ):
            return "PROVEN"
        return "UNCHECKED"


def _grain(label: str) -> str:
    return "FY" if label == "FY" else "TTM" if label == "TTM" else "Q"


def gate_inputs(m: Metric, cells: dict[str, InputCell], served=SERVED_STATUSES):
    """Turn proof-gated input cells into evaluation values. Returns (values, blocked_reason).
    A non-served input yields value None for the engine and a blocking reason."""
    values: dict[str, Decimal | None] = {}
    blocked: str | None = None
    for concept, cell in cells.items():
        if cell.status in served and cell.value is not None:
            values[concept] = cell.value
        elif cell.status == "NOT_PRESENTED" and concept in m.zero_when_absent:
            values[concept] = Decimal(0)
        else:
            values[concept] = None
            if blocked is None:
                blocked = f"input_not_served:{concept}:{cell.status}"
    return values, blocked


def build_cell_record(
    m: Metric,
    cells: dict[str, InputCell],
    period: PeriodBasis,
    *,
    env_extra: DictEnv | None = None,
    stored_value: Decimal | None = None,
    served=SERVED_STATUSES,
) -> CellRecord:
    """Compute a metric cell from proof-gated inputs, with the recomputation check.

    `stored_value` is what production shows today, if any; the recompute check compares it with the
    engine value computed from the recorded inputs (status match | mismatch | n/a)."""
    values, blocked = gate_inputs(m, cells, served)
    env = env_extra or DictEnv()
    env = DictEnv(
        values={**env.values, **values},
        ttm=env.ttm,
        annual=env.annual,
        quarterly=env.quarterly,
        opening=env.opening,
        lags=env.lags,
    )
    ordered = tuple(
        replace(c, value=Decimal(0))
        if c.status == "NOT_PRESENTED" and values.get(c.concept) == Decimal(0)
        else c
        for c in cells.values()
    )
    if blocked is not None:
        res_value, res_reason = None, blocked
    else:
        res = evaluate(m, env, check_period=period.period_label)
        res_value, res_reason = res.value, res.reason
    if stored_value is None or res_value is None:
        recompute = {
            "status": "n/a",
            "recomputed": None if res_value is None else str(res_value),
            "stored": None if stored_value is None else str(stored_value),
        }
    else:
        recompute = {
            "status": "match" if stored_value == res_value else "mismatch",
            "recomputed": str(res_value),
            "stored": str(stored_value),
        }
    return CellRecord(
        metric_id=m.metric_id,
        formula_ref=m.formula_ref,
        fingerprint=formula_fingerprint(m),
        registry_version=compute_registry_version(),
        period=period,
        inputs=ordered,
        value=res_value,
        reason=res_reason,
        recompute=recompute,
    )


def to_cell_proof_row(rec: CellRecord, company_id: int, m: Metric) -> dict:
    """The analytics.cell_proof row for this metric cell (insert is Engineering's proof job, not here)."""
    verdict = rec.verdict
    row = {
        "company_id": company_id,
        "data_point_name": rec.metric_id,
        "period_grain": _grain(rec.period.period_label),
        "period_start": rec.period.period_start,
        "period_end": rec.period.period_end,
        "basis": "latest",
        "shown_value": rec.value,
        "position_value": rec.value if verdict == "PROVEN" else None,
        "position_source": None,
        "position_is_expected_line": True if verdict == "PROVEN" else None,
        "checks": {
            "metric_recompute": rec.recompute,
            "metric_inputs": [
                {
                    "concept": c.concept,
                    "status": c.status,
                    "value": None if c.value is None else str(c.value),
                    "reason": c.reason,
                    "proof_id": c.proof_id,
                    "rule_id": c.rule_id,
                    "rules_commit": c.rules_commit,
                }
                for c in rec.inputs
            ],
            "period_basis": {"label": rec.period.period_label, "rule": rec.period.rule},
            "formula": {
                "ref": rec.formula_ref,
                "fingerprint": rec.fingerprint,
                "registry_version": rec.registry_version,
            },
        },
        "verdict": verdict,
        "reason_code": None,
        "reason_text": None,
        "rule_id": RULE_ID,
        "detector_version": detector_version(m, rec.registry_version),
    }
    if verdict in ("DISAGREE", "NOT_PRESENTED"):
        reason = rec.reason or "metric_recompute_mismatch"
        row["reason_code"] = reason.split(":", 1)[0]
        row["reason_text"] = reason
    return row
