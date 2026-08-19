import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.unit
def test_health_endpoint_is_offline_and_reports_ok():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
