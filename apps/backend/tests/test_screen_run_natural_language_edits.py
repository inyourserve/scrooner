from decimal import Decimal

import pytest

from routers import screen_runs
from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery


@pytest.mark.unit
def test_screen_run_uses_zero_token_template_to_edit_current_query(monkeypatch):
    captured = {}

    def capture(
        text, query, user_id, page_size=50, requested_run_id=None, corrections=None
    ):
        captured.update(
            text=text, query=query, user_id=user_id, corrections=corrections
        )
        return {"normalized_query": query.model_dump(mode="json")}

    monkeypatch.setattr(screen_runs, "create_run_from_query", capture)
    current = ScreenQuery(
        metric_predicates=[
            MetricPredicate(metric_name="trailing_pe", operator="<", value="20"),
            MetricPredicate(metric_name="roe", operator=">", value="0.15"),
        ]
    )

    response = screen_runs.create_screen_run(
        screen_runs.ScreenRunCreate(text="make PE 12", current_query=current),
        user_id="user-1",
    )

    assert response["normalized_query"]["metric_predicates"][0]["value"] == "12"
    assert captured["query"].metric_predicates[0].operator == "<"
    assert captured["query"].metric_predicates[1].value == Decimal("0.15")


@pytest.mark.unit
def test_ambiguous_template_edit_falls_through_without_executing(monkeypatch):
    monkeypatch.setattr(
        screen_runs,
        "create_run_from_query",
        lambda *_args, **_kwargs: pytest.fail("ambiguous edit must not execute"),
    )
    current = ScreenQuery(
        metric_predicates=[
            MetricPredicate(metric_name="trailing_pe", operator="<", value="20"),
            MetricPredicate(metric_name="roe", operator=">", value="0.15"),
        ]
    )

    response = screen_runs.create_screen_run(
        screen_runs.ScreenRunCreate(text="make it 12", current_query=current),
        user_id="user-1",
    )

    assert response["query"] is None
    assert response["unrecognized"] == ["make it 12"]
