"""Everything the legacy hand-kept copies held, generated from the registry.

  pipeline definitions   -> mapper/definitions.py, mapper/expanded_definitions.py (METRIC_DEFINITIONS)
  generic-engine tables  -> mapper/calculate.py (FORMULA_SHAPES, FY_ONLY_METRICS, ZERO_WHEN_ABSENT_CONCEPTS)
  growth table           -> mapper/ttm.py (GROWTH_METRICS)
  backend catalog        -> apps/backend/metric_catalog.py (presentation fields)
  user-facing text       -> formula_text()

Order is registry order (file name, then row); no consumer depends on it.
"""

from __future__ import annotations

from scrooner_pipeline.metrics import expr
from scrooner_pipeline.metrics.registry import Metric, get_registry


def v1_definition_rows() -> list[tuple[str, str, bool, bool, list[tuple[str, str]]]]:
    """(metric_name, formula_description, requires_price, quarterly_needs_ttm, inputs) for the locked V1 list."""
    return [
        (
            m.metric_id,
            m.formula_description,
            m.requires_price,
            bool(m.quarterly_needs_ttm),
            m.input_roles(),
        )
        for m in get_registry().values()
        if m.tier == "v1_locked"
    ]


def expanded_definition_rows() -> list[tuple[str, str, bool, list[tuple[str, str]]]]:
    """(metric_name, formula_description, requires_price, inputs) for the expanded list."""
    return [
        (m.metric_id, m.formula_description, m.requires_price, m.input_roles())
        for m in get_registry().values()
        if m.tier == "expanded"
    ]


def formula_shapes() -> dict[str, str]:
    return {m.metric_id: m.shape for m in get_registry().values() if m.shape}


def fy_only_metrics() -> set[str]:
    return {
        m.metric_id
        for m in get_registry().values()
        if m.expression_status == "engine_wired" and m.fy_only
    }


def zero_when_absent_concepts() -> dict[str, frozenset[str]]:
    return {
        m.metric_id: m.zero_when_absent
        for m in get_registry().values()
        if m.zero_when_absent
    }


def growth_metrics() -> dict[str, tuple[str, int]]:
    out = {}
    for m in get_registry().values():
        if m.expression_status == "growth_wired":
            call = m.ast
            out[m.metric_id] = (call.args[0].name, int(call.args[1].value))
    return out


def presentation() -> dict[str, tuple[str, str, str, str]]:
    """metric_id -> (display_name, short_definition, category, value_type)."""
    return {
        m.metric_id: (m.label, m.short_definition, m.family, m.value_type)
        for m in get_registry().values()
        if m.tier != "planned"  # planned bank/insurer families are not served yet
    }


def formula_text(m: Metric) -> str:
    """The user-facing formula line: the label, the published formula, and the period rule."""
    period = {
        "fy_only": " Fiscal years only.",
        "ttm": " Uses trailing-twelve-month inputs.",
    }.get(m.period_rule, "")
    return f"{m.label} = {m.formula_description}{period}"


def inputs_of(m: Metric) -> list[str]:
    """Concept and metric ids the formula reads, in first-appearance order ([] for procedural)."""
    return expr.names(m.ast) if m.ast is not None else [c for c, _ in m.seed_inputs]
