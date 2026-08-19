from decimal import Decimal

import pytest

from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
@pytest.mark.parametrize("text,metric,operator,value", [
    ("companies that have return on equity at least 25%", "roe", ">=", Decimal("0.25")),
    ("with debt-to-equity below 1.5", "debt_to_equity", "<", Decimal("1.5")),
    ("where free cash flow greater than 100", "fcf", ">", Decimal("100")),
])
def test_supported_filler_alias_operator_and_percentage_phrases(text, metric, operator, value):
    result = interpret(text)

    assert result.is_confident
    predicate = result.query.metric_predicates[0]
    assert (predicate.metric_name, predicate.operator, predicate.value) == (metric, operator, value)


@pytest.mark.unit
def test_between_rank_and_sector_queries():
    between = interpret("debt to equity between 0 and 1")
    ranked = interpret("top 5 by return on invested capital")
    sector = interpret("software companies")

    assert between.query.metric_predicates[0].value_range == (Decimal("0"), Decimal("1"))
    assert ranked.query.metric_predicates[0].operator == "top_n"
    assert ranked.query.metric_predicates[0].n == 5
    assert sector.query.categorical_predicates[0].value == "7372"


@pytest.mark.unit
@pytest.mark.parametrize("text", ["magic number above 10", "roe approximately wonderful", ""])
def test_unknown_or_malformed_language_never_executes(text):
    result = interpret(text)

    assert result.query is None
    assert not result.is_confident


@pytest.mark.unit
def test_partially_recognized_query_is_rejected_as_a_whole():
    result = interpret("roe above 20% and magic number below 5")

    assert result.query is None
    assert result.unrecognized == ["magic number below 5"]
    assert result.recognized_query is not None
    assert result.recognized_query.metric_predicates[0].metric_name == "roe"
    assert result.is_confident is False
