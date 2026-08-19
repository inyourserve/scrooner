from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from structlog.testing import capture_logs

from main import app
from observability import api_request_metrics


pytestmark = pytest.mark.unit


def test_request_id_and_content_free_structured_event() -> None:
    api_request_metrics.reset()

    with capture_logs() as logs:
        response = TestClient(app).get("/health?private_query=do-not-record")

    assert response.status_code == 200
    UUID(response.headers["X-Request-ID"])
    event = next(row for row in logs if row["event"] == "api.request.completed")
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert event["method"] == "GET"
    assert event["endpoint"] == "/health"
    assert event["status_code"] == 200
    assert "private_query" not in str(event)
    assert "do-not-record" not in str(event)


def test_metrics_report_count_latency_errors_and_route_templates() -> None:
    api_request_metrics.reset()
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/missing/arbitrary-user-content").status_code == 404
    snapshot = client.get("/health/metrics").json()

    assert snapshot["scope"] == "single_process_since_start"
    assert snapshot["requests"]["count"] == 2
    assert snapshot["requests"]["client_errors"] == 1
    assert snapshot["requests"]["server_errors"] == 0
    assert snapshot["requests"]["server_error_rate"] == 0.0
    assert snapshot["requests"]["latency_ms"]["average"] >= 0
    assert {(row["method"], row["endpoint"]) for row in snapshot["endpoints"]} == {
        ("GET", "/health"),
        ("GET", "<unmatched>"),
    }


def test_server_error_rate_is_calculated_per_endpoint_and_in_total() -> None:
    api_request_metrics.reset()
    api_request_metrics.observe("POST", "/v1/screen", 200, 10)
    api_request_metrics.observe("POST", "/v1/screen", 500, 30)

    snapshot = api_request_metrics.snapshot()

    assert snapshot["requests"]["count"] == 2
    assert snapshot["requests"]["server_errors"] == 1
    assert snapshot["requests"]["server_error_rate"] == 0.5
    assert snapshot["requests"]["latency_ms"] == {"average": 20.0, "maximum": 30}
    assert snapshot["endpoints"][0]["server_error_rate"] == 0.5
