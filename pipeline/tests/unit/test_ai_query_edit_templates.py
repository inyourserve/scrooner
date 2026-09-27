from decimal import Decimal

import pytest

from scrooner_pipeline.ai_query.edit_templates import interpret_edit, load_edit_templates
from scrooner_pipeline.screener.schema import MetricPredicate, PredicateGroup, ScreenQuery


@pytest.mark.unit
def test_stored_templates_load_once_with_stable_ids():
    templates = load_edit_templates()

    assert [template.id for template in templates] == [
        "set_metric_value",
        "set_single_value_by_pronoun",
    ]
    assert load_edit_templates() is templates


@pytest.mark.unit
def test_explicit_metric_edit_changes_only_the_number():
    current = ScreenQuery(
        metric_predicates=[
            MetricPredicate(metric_name="trailing_pe", operator="<", value="20"),
            MetricPredicate(metric_name="roe", operator=">", value="0.15"),
        ],
        sort_by="market_cap",
        limit=50,
    )

    result = interpret_edit("make PE 15", current)

    assert result is not None and result.is_confident
    assert result.query.metric_predicates[0].operator == "<"
    assert result.query.metric_predicates[0].value == Decimal("15")
    assert result.query.metric_predicates[1].value == Decimal("0.15")
    assert result.query.sort_by == "market_cap"
    assert result.query.limit == 50
    assert current.metric_predicates[0].value == Decimal("20")


@pytest.mark.unit
def test_percentage_edit_is_scaled_exactly():
    current = ScreenQuery(
        metric_predicates=[MetricPredicate(metric_name="roe", operator=">", value="0.20")]
    )

    result = interpret_edit("change return on equity to 25%", current)

    assert result.query.metric_predicates[0].value == Decimal("0.25")


@pytest.mark.unit
def test_pronoun_edit_requires_exactly_one_editable_predicate():
    single = ScreenQuery(
        metric_predicates=[MetricPredicate(metric_name="trailing_pe", operator="<", value="20")]
    )
    multiple = ScreenQuery(
        metric_predicates=[
            MetricPredicate(metric_name="trailing_pe", operator="<", value="20"),
            MetricPredicate(metric_name="roe", operator=">", value="0.20"),
        ]
    )

    assert interpret_edit("make it 15", single).query.metric_predicates[0].value == Decimal("15")
    assert interpret_edit("make it 15", multiple) is None


@pytest.mark.unit
def test_edit_preserves_boolean_tree_and_changes_one_matching_leaf():
    current = ScreenQuery(
        where=PredicateGroup(
            op="or",
            predicates=[
                MetricPredicate(metric_name="trailing_pe", operator="<", value="20"),
                MetricPredicate(metric_name="roe", operator=">", value="0.20"),
            ],
        ),
        display_metrics=["market_cap"],
    )

    result = interpret_edit("set p/e to 12", current)

    assert result.query.where.op == "or"
    assert result.query.where.predicates[0].value == Decimal("12")
    assert result.query.where.predicates[1].value == Decimal("0.20")
    assert result.query.display_metrics == ["market_cap"]


@pytest.mark.unit
def test_duplicate_metric_is_ambiguous_and_never_modified():
    current = ScreenQuery(
        where=PredicateGroup(
            op="or",
            predicates=[
                MetricPredicate(metric_name="roe", operator=">", value="0.10"),
                MetricPredicate(metric_name="roe", operator=">", value="0.20"),
            ],
        )
    )

    assert interpret_edit("set ROE to 30%", current) is None


@pytest.mark.unit
def test_unmatched_language_falls_through_without_guessing():
    current = ScreenQuery(
        metric_predicates=[MetricPredicate(metric_name="trailing_pe", operator="<", value="20")]
    )

    assert interpret_edit("make this screen much better", current) is None
