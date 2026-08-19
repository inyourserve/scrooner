from contextlib import contextmanager
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from main import app
from routers import screen


@contextmanager
def unused_connection():
    yield object()


@pytest.mark.unit
def test_screen_endpoint_preserves_full_decimal_precision(monkeypatch):
    precise = Decimal("0.1234567890123456789012345678")
    monkeypatch.setattr(screen, "get_connection", unused_connection)
    monkeypatch.setattr(
        screen,
        "run_query",
        lambda _conn, _query: {
            "matched": [{"cik": "0001", "metrics": {"roe": {"value": precise}}}],
            "excluded_missing_data": [],
            "excluded_inactive": [],
        },
    )
    monkeypatch.setattr(screen, "_log_usage", lambda *_args, **_kwargs: None)

    response = TestClient(app).post(
        "/v1/screen",
        json={"metric_predicates": [{"metric_name": "roe", "operator": ">", "value": "0.10"}]},
    )

    assert response.status_code == 200
    assert response.json()["matched"][0]["metrics"]["roe"]["value"] == str(precise)


@pytest.mark.unit
def test_invalid_screen_contract_is_rejected_before_execution(monkeypatch):
    called = False

    def should_not_run(*_args):
        nonlocal called
        called = True
        raise AssertionError("invalid request reached Screener")

    monkeypatch.setattr(screen, "run_query", should_not_run)
    response = TestClient(app).post(
        "/v1/screen",
        json={"metric_predicates": [{"metric_name": "roe", "operator": ">"}]},
    )

    assert response.status_code == 422
    assert called is False


@pytest.mark.unit
def test_metric_catalog_exposes_formula_and_ui_contract(monkeypatch):
    monkeypatch.setattr(
        screen,
        "_load_metric_catalog",
        lambda: [
            {
                "metric_name": "roe",
                "display_name": "Return on equity (ROE)",
                "short_definition": "Net income relative to stockholders' equity.",
                "formula_description": "Net Income / Stockholders' Equity",
                "formula_version": 1,
                "category": "Returns",
                "value_type": "percentage",
                "operators": [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"],
            }
        ],
    )

    response = TestClient(app).get("/v1/metrics")

    assert response.status_code == 200
    metric = response.json()[0]
    assert metric["metric_name"] == "roe"
    assert metric["value_type"] == "percentage"
    assert metric["formula_version"] == 1
    assert metric["operators"][-2:] == ["top_n", "bottom_n"]


@pytest.mark.unit
def test_ask_contract_shows_interpretation_and_does_not_run_by_default(monkeypatch):
    monkeypatch.setattr(screen, "_log_usage", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(screen, "run_query", lambda *_args: pytest.fail("run_query should not run"))

    response = TestClient(app).post("/v1/ask", json={"text": "companies with ROE above 30%"})

    assert response.status_code == 200
    body = response.json()
    assert body["query"]["metric_predicates"][0] == {
        "metric_name": "roe",
        "operator": ">",
        "value": "0.3",
        "value_range": None,
        "n": None,
    }
    assert "result" not in body
    assert body["unrecognized"] == []
    assert body["recognized_query"] == body["query"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_metric,expected_category,expected_operator",
    [
        ("companies with ROE above 30%", "roe", None, ">"),
        ("software companies", None, "7372", None),
        ("debt to equity between 0 and 1", "debt_to_equity", None, "between"),
        ("top 3 by ROIC", "roic", None, "top_n"),
    ],
)
def test_four_verified_queries_interpret_through_browser_contract(
    monkeypatch, text, expected_metric, expected_category, expected_operator
):
    monkeypatch.setattr(screen, "_log_usage", lambda *_args, **_kwargs: None)
    response = TestClient(app).post("/v1/ask", json={"text": text, "run": False})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] is not None
    assert body["recognized_query"] == body["query"]
    assert body["unrecognized"] == []
    assert body["ambiguous"] == []
    if expected_metric:
        predicate = body["query"]["metric_predicates"][0]
        assert predicate["metric_name"] == expected_metric
        assert predicate["operator"] == expected_operator
    else:
        assert body["query"]["categorical_predicates"][0]["value"] == expected_category


@pytest.mark.unit
def test_ask_ambiguous_text_never_runs_even_when_requested(monkeypatch):
    monkeypatch.setattr(screen, "_log_usage", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(screen, "run_query", lambda *_args: pytest.fail("ambiguous query executed"))

    response = TestClient(app).post("/v1/ask", json={"text": "revenue growth above 10%", "run": True})

    assert response.status_code == 200
    assert response.json()["query"] is None
    assert response.json()["ambiguous"]
    assert "result" not in response.json()


@pytest.mark.unit
def test_ask_exposes_recognized_partial_without_making_it_executable(monkeypatch):
    monkeypatch.setattr(screen, "_log_usage", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(screen, "run_query", lambda *_args: pytest.fail("partial query executed"))

    response = TestClient(app).post(
        "/v1/ask",
        json={"text": "roe above 20% and magic number below 5", "run": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] is None
    assert body["recognized_query"]["metric_predicates"][0]["metric_name"] == "roe"
    assert body["unrecognized"] == ["magic number below 5"]
    assert "result" not in body
