from decimal import Decimal

import pytest

from scrooner_pipeline.ai_query.rules import interpret


@pytest.mark.unit
def test_plain_english_query_is_explicitly_interpreted():
    result = interpret("companies with ROE above 30%")

    assert result.is_confident is True
    assert result.query is not None
    assert result.query.metric_predicates[0].metric_name == "roe"
    assert result.query.metric_predicates[0].operator == ">"
    assert result.query.metric_predicates[0].value == Decimal("0.30")


@pytest.mark.unit
def test_ambiguous_query_never_produces_an_executable_partial_query():
    result = interpret("revenue growth above 10%")

    assert result.query is None
    assert result.is_confident is False
    assert result.ambiguous[0].candidates == ["revenue_growth_yoy", "revenue_growth_3y_cagr"]
