"""Direct tests for mapper/calculate_shapes/ -- the "one sub-tree node
per formula shape" refactor (2026-09-28, requested directly: "keep one
main tree -> calculate.py, create more sub tree node for each
calculation, so it will be scalable").

test_metric_formulas.py already exercises every shape's behavior
end-to-end via calculate.py's own `_compute()` re-export (unchanged by
this refactor, confirmed byte-identical against the pre-refactor test
suite). This file additionally tests each shape module's own compute()
function directly, imported from its own file -- proving the "sub-tree
node" property itself: each module is independently importable and
testable without going through calculate.py at all."""

from decimal import Decimal

import pytest

from scrooner_pipeline.mapper.calculate_shapes import SHAPE_REGISTRY, compute
from scrooner_pipeline.mapper.calculate_shapes import (
    additive,
    days,
    ratio,
    roic,
    sum_diff,
    sum_diff_ratio,
)
from scrooner_pipeline.mapper.calculate_shapes.materiality import (
    CONCEPT_MATERIALITY_FLOORS,
    materiality_floor_violation,
)


@pytest.mark.unit
def test_shape_registry_has_every_shape_the_engine_uses():
    # Mirrors main_calculator.py's own unregistered_metrics() completeness
    # check, one layer in: every shape calculate.py's FORMULA_SHAPES dict
    # can name must have a registry entry, or a metric using it crashes
    # with a bare KeyError (the exact doc-18 finding pipeline/CLAUDE.md
    # already documents for the module-level registry).
    assert set(SHAPE_REGISTRY) == {
        "ratio",
        "sum_diff",
        "sum_diff_ratio",
        "additive",
        "days",
        "roic",
    }


@pytest.mark.unit
def test_dispatcher_raises_on_unknown_shape():
    with pytest.raises(ValueError, match="unknown formula shape"):
        compute("not_a_real_shape", {})


@pytest.mark.unit
class TestRatioModule:
    def test_basic_division(self):
        value, reason = ratio.compute(
            {"numerator": [Decimal("30")], "denominator": [Decimal("100")]}
        )
        assert value == Decimal("0.3")
        assert reason is None

    def test_missing_inputs(self):
        assert ratio.compute({"denominator": [Decimal("1")]}) == (
            None,
            "missing:numerator",
        )
        assert ratio.compute({"numerator": [Decimal("1")]}) == (
            None,
            "missing:denominator",
        )

    def test_zero_denominator(self):
        value, reason = ratio.compute(
            {"numerator": [Decimal("1")], "denominator": [Decimal("0")]}
        )
        assert value is None
        assert reason == "zero_denominator"

    def test_materiality_floor(self):
        value, reason = ratio.compute(
            {"numerator": [Decimal("-20000000")], "denominator": [Decimal("1")]},
            frozenset({"revenue"}),
        )
        assert value is None
        assert reason == "immaterial_revenue_base"


@pytest.mark.unit
class TestSumDiffModule:
    def test_basic_subtraction(self):
        value, reason = sum_diff.compute(
            {"add": [Decimal("10"), Decimal("5")], "subtract": [Decimal("3")]}
        )
        assert value == Decimal("12")
        assert reason is None

    def test_no_materiality_floor_concept_has_none(self):
        # sum_diff has no denominator role at all -- passing a
        # denominator_concept_names set (even one with a real floor
        # entry) must have zero effect, there's nothing to check it
        # against.
        value, reason = sum_diff.compute(
            {"add": [Decimal("1")], "subtract": [Decimal("0")]},
            frozenset({"revenue"}),
        )
        assert value == Decimal("1")
        assert reason is None


@pytest.mark.unit
class TestSumDiffRatioModule:
    def test_basic(self):
        value, reason = sum_diff_ratio.compute(
            {
                "add": [Decimal("100")],
                "subtract": [Decimal("40")],
                "denominator": [Decimal("100")],
            }
        )
        assert value == Decimal("0.6")
        assert reason is None

    def test_materiality_floor(self):
        value, reason = sum_diff_ratio.compute(
            {
                "add": [Decimal("1")],
                "subtract": [Decimal("20000001")],
                "denominator": [Decimal("1")],
            },
            frozenset({"revenue"}),
        )
        assert value is None
        assert reason == "immaterial_revenue_base"


@pytest.mark.unit
class TestAdditiveModule:
    def test_sums_all_add_inputs(self):
        value, reason = additive.compute(
            {"add": [Decimal("10"), Decimal("5"), Decimal("2")]}
        )
        assert value == Decimal("17")
        assert reason is None

    def test_missing_add(self):
        assert additive.compute({}) == (None, "missing:add")


@pytest.mark.unit
class TestDaysModule:
    def test_basic(self):
        value, reason = days.compute(
            {"numerator": [Decimal("100")], "denominator": [Decimal("1000")]}
        )
        assert value == Decimal("100") / Decimal("1000") * 365
        assert reason is None

    def test_materiality_floor(self):
        value, reason = days.compute(
            {"numerator": [Decimal("1000")], "denominator": [Decimal("1")]},
            frozenset({"total_assets"}),
        )
        assert value is None
        assert reason == "immaterial_total_assets_base"


@pytest.mark.unit
class TestRoicModule:
    def test_exact_computation(self):
        value, reason = roic.compute(
            {
                "nopat_base": [Decimal("20")],
                "tax_rate_numerator": [Decimal("5")],
                "tax_rate_denominator": [Decimal("25")],
                "invested_capital_add": [Decimal("30"), Decimal("40")],
                "invested_capital_subtract": [Decimal("10")],
            }
        )
        assert value == Decimal(4) / Decimal(15)
        assert reason is None

    def test_zero_invested_capital(self):
        value, reason = roic.compute(
            {
                "nopat_base": [Decimal("10")],
                "tax_rate_numerator": [Decimal("1")],
                "tax_rate_denominator": [Decimal("10")],
                "invested_capital_add": [Decimal("5")],
                "invested_capital_subtract": [Decimal("5")],
            }
        )
        assert value is None
        assert reason == "zero_invested_capital"

    def test_no_materiality_floor_applied_to_invested_capital(self):
        # Deliberate, per roic.py's own module docstring -- invested
        # capital going near-zero hasn't been evidenced as a shell-
        # company signal the way total_assets was, so passing its
        # concept names through must have no effect.
        value, reason = roic.compute(
            {
                "nopat_base": [Decimal("1")],
                "tax_rate_numerator": [Decimal("0")],
                "tax_rate_denominator": [Decimal("1")],
                "invested_capital_add": [Decimal("1")],
                "invested_capital_subtract": [Decimal("0")],
            },
            frozenset({"total_debt", "stockholders_equity"}),
        )
        assert value == Decimal("1")
        assert reason is None


@pytest.mark.unit
def test_materiality_registry_and_helper_reexported_correctly():
    assert CONCEPT_MATERIALITY_FLOORS["revenue"] == Decimal("1000000")
    assert (
        materiality_floor_violation(frozenset({"revenue"}), Decimal("1"))
        == "immaterial_revenue_base"
    )
    assert materiality_floor_violation(frozenset({"revenue"}), Decimal("2000000")) is None
