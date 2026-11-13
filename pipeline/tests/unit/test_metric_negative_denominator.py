"""Founder 2026-11-13: a zero or negative denominator that can go negative is null with a reason.

Zero keeps its own reason (zero_denominator / zero_invested_capital); negative is
negative_ratio_undefined ("not meaningful"). Margins (revenue denominator) keep their behaviour.
Registry engine and live shapes (mapper/calculate_shapes) must agree.
"""

from __future__ import annotations

from decimal import Decimal as D

import pytest

from scrooner_pipeline.mapper.calculate_shapes import compute as legacy_compute
from scrooner_pipeline.mapper.calculate_shapes.materiality import (
    NEGATIVE_UNDEFINED_DENOMINATORS as NEG,
)
from scrooner_pipeline.metrics.engine import DictEnv, evaluate
from scrooner_pipeline.metrics.registry import get_registry

REG = get_registry()
GENERIC = [m for m in REG.values() if m.expression_status == "engine_wired"]

NEG_METRICS = {
    "roe": {"net_income": D(10), "stockholders_equity": D(-5)},
    "debt_to_equity": {"total_debt_resolved": D(10), "stockholders_equity": D(-5)},
    "ocf_to_net_income": {"cfo": D(10), "net_income": D(-5)},
    "payout_ratio": {"dividends_per_share": D(1), "diluted_eps": D(-2)},
}


@pytest.mark.unit
@pytest.mark.parametrize("mid", sorted(NEG_METRICS))
def test_negative_denominator_is_null_not_meaningful_and_zero_keeps_its_reason(mid):
    m = REG[mid]
    vals = dict(NEG_METRICS[mid])
    res = evaluate(m, DictEnv(values=vals))
    assert (res.value, res.reason) == (None, "negative_ratio_undefined")
    den = [c for c, r in m.input_roles() if r == "denominator"][0]
    vals[den] = D(0)
    assert evaluate(m, DictEnv(values=vals)).reason == "zero_denominator"
    vals[den] = D(5)
    assert evaluate(m, DictEnv(values=vals)).reason is None


@pytest.mark.unit
def test_roic_pe_ev_ebitda_negative_and_margins_unchanged():
    env = DictEnv(values={"operating_income": D(10), "income_tax_expense": D(2), "income_before_tax": D(10),
                          "total_debt_resolved": D(1), "stockholders_equity": D(-5), "cash_and_equivalents": D(0)})
    assert evaluate(REG["roic"], env).reason == "negative_ratio_undefined"
    env.values["stockholders_equity"] = D(-1)  # invested capital exactly zero
    assert evaluate(REG["roic"], env).reason == "zero_invested_capital"
    env.values["stockholders_equity"] = D(5)
    assert evaluate(REG["roic"], env).value == D(8) / D(6)
    pe = evaluate(REG["trailing_pe"], DictEnv(values={"price": D(1)}, ttm={"diluted_eps": D(-1)}))
    assert pe.reason == "negative_ratio_undefined"
    ev_env = DictEnv(values={"market_cap": D(5), "total_debt_resolved": D(1), "cash_and_equivalents": D(1)},
                     ttm={"ebitda": D(-3)})
    assert evaluate(REG["ev_ebitda"], ev_env).reason == "negative_ratio_undefined"
    # margins: revenue is the denominator; not part of this rule
    assert "neg" not in REG["net_margin"].null_rules
    assert evaluate(REG["net_margin"], DictEnv(values={"net_income": D(1), "revenue": D(-4000000000)})).value == D("-0.00000000025")


@pytest.mark.unit
def test_registry_neg_flag_agrees_with_live_shape_by_denominator_concept():
    for m in GENERIC:
        if m.metric_id == "roic":
            continue
        dens = {c for c, r in m.input_roles() if r == "denominator"}
        assert bool(dens & NEG) == ("neg" in m.null_rules), m.metric_id


@pytest.mark.unit
def test_live_shapes_give_the_same_reasons():
    assert legacy_compute("ratio", {"numerator": [D(1)], "denominator": [D(-5)]}, frozenset({"stockholders_equity"})) == (
        None, "negative_ratio_undefined")
    assert legacy_compute("ratio", {"numerator": [D(1)], "denominator": [D(0)]}, frozenset({"stockholders_equity"})) == (
        None, "zero_denominator")
    # revenue denominator is not in the rule
    assert legacy_compute("ratio", {"numerator": [D(1)], "denominator": [D(-4000000000)]}, frozenset({"revenue"}))[0] == D("-0.00000000025")
    roic = {"nopat_base": [D(10)], "tax_rate_numerator": [D(2)], "tax_rate_denominator": [D(10)],
            "invested_capital_add": [D(1)], "invested_capital_subtract": [D(6)]}
    assert legacy_compute("roic", roic) == (None, "negative_ratio_undefined")
