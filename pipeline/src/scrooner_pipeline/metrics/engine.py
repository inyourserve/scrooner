"""Evaluate a registry formula in Decimal. AST walk only: no eval, no float.

Contract (matches the live generic engine, mapper/calculate.py + calculate_shapes, and the
growth engine, mapper/ttm.py `_growth_value`, which the agreement tests hold it to):
  * an input that is absent makes the metric null with reason `incomplete:<role>` (generic
    shapes) or `missing:<name>` (other formulas), unless the registry lists it under
    `zero_when_absent` for this metric (then it counts as zero);
  * a zero divisor is null, with the reason the registry names for that division
    (`div0=`, in evaluation order);
  * `floor=denominator`: a divisor whose concept is below its materiality floor is null,
    `immaterial_<concept>_base`; the floors table stays in calculate_shapes/materiality.py.
Note the live rule is `divisor == 0`, not `divisor <= 0`: a negative denominator computes
(negative equity gives a negative ROE). Reported as an open decision, not changed here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from scrooner_pipeline.mapper.calculate_shapes.materiality import (
    CONCEPT_MATERIALITY_FLOORS,
)
from scrooner_pipeline.metrics import expr
from scrooner_pipeline.metrics.registry import Metric


@dataclass(frozen=True)
class Result:
    value: Decimal | None
    reason: str | None
    formula_ref: str


@dataclass
class DictEnv:
    """Inputs for one period. `values` holds the point value of each concept/metric (None or absent
    = not available); the other maps feed the operators."""

    values: dict[str, Decimal | None] = field(default_factory=dict)
    ttm: dict[str, Decimal | None] = field(default_factory=dict)
    annual: dict[str, Decimal | None] = field(default_factory=dict)
    quarterly: dict[str, Decimal | None] = field(default_factory=dict)
    opening: dict[str, Decimal | None] = field(
        default_factory=dict
    )  # opening balance, for avg()
    lags: dict[tuple[str, int], Decimal | None] = field(default_factory=dict)

    def value(self, name):
        return self.values.get(name)

    def op(self, func, name):
        return {"ttm": self.ttm, "annual": self.annual, "quarterly": self.quarterly}[
            func
        ].get(name)

    def avg(self, name):
        close, open_ = self.values.get(name), self.opening.get(name)
        return None if close is None or open_ is None else (close + open_) / 2

    def lag(self, name, years):
        return self.lags.get((name, years))


class _Null(Exception):
    def __init__(self, reason: str):
        self.reason = reason


def growth_value(
    value_t: Decimal,
    value_prior: Decimal,
    lag_years: int,
    floor: Decimal = Decimal("0"),
):
    """Same arithmetic and reasons as mapper/ttm.py `_growth_value`."""
    if value_prior == 0:
        return None, "zero_base_value"
    if abs(value_prior) < floor:
        return None, "immaterial_prior_base"
    if lag_years == 1:
        return (value_t - value_prior) / value_prior, None
    ratio = value_t / value_prior
    if ratio < 0:
        return None, "negative_ratio_undefined_cagr"
    return ratio ** (Decimal(1) / Decimal(lag_years)) - 1, None


def evaluate(metric: Metric, env, *, check_period: str | None = None) -> Result:
    """Evaluate `metric` against `env`. `check_period` (an fiscal_period label like FY, Q1, TTM)
    applies the registry's period rule first."""
    ref = metric.formula_ref
    if metric.ast is None:
        return Result(None, f"procedural:computed_by:{metric.calculator}", ref)
    if check_period is not None and metric.fy_only and check_period != "FY":
        return Result(None, "period_not_applicable:fy_only", ref)
    zero_ok = metric.zero_when_absent
    div_reasons = [
        x for x in metric.null_rules.get("div0", "zero_denominator").split(",") if x
    ]
    floor_rule = metric.null_rules.get("floor") == "denominator"
    cls = (
        metric.classification() if metric.expression_status == "engine_wired" else None
    )
    if cls:
        for concept, role in cls[1]:
            if concept not in zero_ok and env.value(concept) is None:
                return Result(None, f"incomplete:{role}", ref)
    div_index = [0]

    def get(name):
        v = env.value(name)
        if v is None:
            if name in zero_ok:
                return Decimal(0)
            raise _Null(f"missing:{name}")
        return v

    def ev(node):
        if isinstance(node, expr.Num):
            return node.value
        if isinstance(node, expr.Name):
            return get(node.name)
        if isinstance(node, expr.Neg):
            return -ev(node.arg)
        if isinstance(node, expr.Bin):
            a = ev(node.left)
            if node.op == "/":
                d = ev(node.right)
                idx = div_index[0]
                div_index[0] += 1
                if d == 0:
                    raise _Null(div_reasons[min(idx, len(div_reasons) - 1)])
                if floor_rule:
                    bot = expr.chain(node.right)
                    if bot is not None:
                        for _, concept in bot:
                            fl = CONCEPT_MATERIALITY_FLOORS.get(concept)
                            if fl is not None and abs(d) < fl:
                                raise _Null(f"immaterial_{concept}_base")
                return a / d
            b = ev(node.right)
            return {"+": a + b, "-": a - b, "*": a * b}[node.op]
        if isinstance(node, expr.Call):
            f = node.func
            if f == "abs":
                return abs(ev(node.args[0]))
            name = node.args[0].name
            if f == "avg":
                v = env.avg(name)
            elif f in ("ttm", "annual", "quarterly"):
                v = env.op(f, name)
            elif f == "lag":
                v = env.lag(name, int(node.args[1].value))
            else:  # growth
                n = int(node.args[1].value)
                cur, prior = env.value(name), env.lag(name, n)
                if cur is None:
                    raise _Null(f"missing:{name}")
                if prior is None:
                    raise _Null(f"missing_prior:{name}")
                value, reason = growth_value(
                    cur, prior, n, CONCEPT_MATERIALITY_FLOORS.get(name, Decimal("0"))
                )
                if reason:
                    raise _Null(reason)
                return value
            if v is None:
                raise _Null(f"missing:{f}({name})")
            return v
        raise TypeError(node)  # pragma: no cover

    try:
        return Result(ev(metric.ast), None, ref)
    except _Null as n:
        return Result(None, n.reason, ref)
