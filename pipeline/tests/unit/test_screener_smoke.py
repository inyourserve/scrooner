from decimal import Decimal

import pytest

from scrooner_pipeline.screener.evaluate import evaluate_comparison, rank_top_bottom
from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery


@pytest.mark.unit
def test_screener_validates_and_evaluates_without_treating_null_as_zero():
    query = ScreenQuery(
        metric_predicates=[MetricPredicate(metric_name="roe", operator=">", value=Decimal("0.30"))]
    )

    assert query.metric_predicates[0].value == Decimal("0.30")
    assert evaluate_comparison(Decimal("0.31"), ">", Decimal("0.30")) is True
    assert evaluate_comparison(None, ">", Decimal("0.30")) is False
    assert rank_top_bottom(
        [("a", Decimal("0.20")), ("missing", None), ("b", Decimal("0.40"))],
        "top_n",
        2,
    ) == ["b", "a"]
