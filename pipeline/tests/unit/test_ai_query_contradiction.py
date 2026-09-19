import pytest

from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
def test_doc_46_example_d_contradiction_is_rejected_without_execution():
    result = interpret("pe below 10 and pe above 20")
    assert result.query is None
    assert result.contradictions
    assert "trailing_pe" in result.contradictions[0]


@pytest.mark.unit
def test_reversed_bounds_on_same_metric_are_also_contradictory():
    result = interpret("roe above 20% and roe below 10%")
    assert result.query is None
    assert result.contradictions


@pytest.mark.unit
def test_equal_inclusive_bounds_are_a_real_single_point_not_a_contradiction():
    result = interpret("roe >= 20% and roe <= 20%")
    assert result.is_confident
    assert not result.contradictions


@pytest.mark.unit
def test_strict_bounds_meeting_at_the_same_value_are_a_contradiction():
    result = interpret("roe > 20% and roe < 20%")
    assert result.query is None
    assert result.contradictions


@pytest.mark.unit
def test_two_conflicting_equalities_on_the_same_metric_are_a_contradiction():
    result = interpret("roe = 5% and roe = 10%")
    assert result.query is None
    assert result.contradictions


@pytest.mark.unit
def test_between_reversed_bounds_group_is_contradictory():
    # Tests the interval-merge helper directly: rules.py's own "between"
    # grammar treats the whole input as one clause whenever "between"
    # appears anywhere (a documented, separate scope limit), so a real
    # "roe between X and Y and roe below Z" text can't reach this check via
    # interpret() yet -- the merge logic itself is still real and correct.
    from scrooner_pipeline.ai_query.rules import _find_contradictory_group
    from scrooner_pipeline.screener.schema import MetricPredicate
    from decimal import Decimal

    group = [
        MetricPredicate(metric_name="roe", operator="between", value_range=(Decimal("0.3"), Decimal("0.4"))),
        MetricPredicate(metric_name="roe", operator="<", value=Decimal("0.1")),
    ]
    assert _find_contradictory_group(group) == group


@pytest.mark.unit
def test_overlapping_bounds_on_the_same_metric_are_not_flagged():
    result = interpret("roe above 10% and roe below 30%")
    assert result.is_confident
    assert not result.contradictions


@pytest.mark.unit
def test_bounds_on_different_metrics_are_never_flagged():
    result = interpret("market cap above 2 billion and pe below 20")
    assert result.is_confident
    assert not result.contradictions


@pytest.mark.unit
def test_or_combined_disjoint_bounds_on_the_same_metric_are_a_normal_query_not_a_contradiction():
    result = interpret("pe below 10 or pe above 20")
    assert result.is_confident
    assert not result.contradictions
