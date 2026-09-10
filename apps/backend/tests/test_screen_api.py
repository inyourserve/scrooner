from contextlib import contextmanager
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from main import app
from metric_catalog import METRIC_PRESENTATION, presentation_for
from routers import screen


@contextmanager
def unused_connection():
    yield object()


@pytest.mark.unit
def test_screen_endpoint_preserves_full_decimal_precision(monkeypatch):
    precise = Decimal("0.1234567890123456789012345678")
    monkeypatch.setattr(screen, "get_pooled_connection", unused_connection)
    monkeypatch.setattr(screen, "get_cached_dataset_version", lambda _conn: 1)
    monkeypatch.setattr(screen, "get_cached_result", lambda _hash: None)
    monkeypatch.setattr(screen, "set_cached_result", lambda _hash, _result: None)
    monkeypatch.setattr(
        screen,
        "run_query",
        lambda _conn, _query, dataset_version=None: {
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
def test_current_presentation_catalog_has_no_generic_fallbacks():
    # 82 as of 2026-09-10: widened from 47 the same day the Screener's
    # catalog stopped excluding price-dependent metrics (market_cap,
    # trailing_pe, etc.) -- this number is a change-detector, not a
    # magic constant; bump it deliberately when a new metric_definition
    # is added, same as before.
    assert len(METRIC_PRESENTATION) == 82
    for metric_name in METRIC_PRESENTATION:
        presentation = presentation_for(metric_name)
        assert presentation.category != "Other"
        assert presentation.short_definition != "Defined Scrooner metric."


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
def test_ask_can_interpret_and_run_a_valid_screen_in_one_request(monkeypatch):
    expected_result = {
        "matched": [],
        "excluded_missing_data": [],
        "excluded_inactive": [],
    }
    executed = []

    def run_once(_conn, query, dataset_version=None):
        executed.append(query)
        return expected_result

    monkeypatch.setattr(screen, "get_pooled_connection", unused_connection)
    monkeypatch.setattr(screen, "get_cached_dataset_version", lambda _conn: 1)
    monkeypatch.setattr(screen, "get_cached_result", lambda _hash: None)
    monkeypatch.setattr(screen, "set_cached_result", lambda _hash, _result: None)
    monkeypatch.setattr(screen, "run_query", run_once)
    monkeypatch.setattr(screen, "_log_usage", lambda *_args, **_kwargs: None)

    response = TestClient(app).post(
        "/v1/ask",
        json={"text": "companies with ROE above 30%", "run": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(executed) == 1
    assert executed[0].metric_predicates[0].metric_name == "roe"
    assert body["query"] == body["recognized_query"]
    assert body["result"] == {**expected_result, "cache_hit": False}


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
