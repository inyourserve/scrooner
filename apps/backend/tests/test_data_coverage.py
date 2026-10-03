from contextlib import contextmanager
from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException

from routers import data_coverage


@pytest.mark.unit
def test_coverage_dashboard_returns_datewise_history_and_metric_deltas(monkeypatch):
    history = [
        (date(2026, 10, 3), Decimal("81.20"), Decimal("92.40"), Decimal("88.10"), 5200),
        (date(2026, 10, 2), Decimal("80.90"), Decimal("91.90"), Decimal("88.00"), 5190),
    ]
    metrics = [("free_cash_flow", 3900, 5200, Decimal("75.00"), Decimal("74.50"))]

    class Cursor:
        def __init__(self):
            self.calls = 0

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def execute(self, _sql, _params=None):
            self.calls += 1

        def fetchall(self):
            return history if self.calls == 1 else metrics

    cursor = Cursor()

    class Connection:
        def cursor(self):
            return cursor

    @contextmanager
    def pooled_connection():
        yield Connection()

    monkeypatch.setattr(data_coverage, "get_pooled_connection", pooled_connection)
    result = data_coverage.get_data_coverage(days=30, _="user-a")

    assert result["as_of"] == "2026-10-03"
    assert result["history"][0]["core_score"] == "92.40"
    assert result["weakest_metrics"][0]["delta"] == "0.50"


@pytest.mark.unit
class TestCompanyCoverageEndpoint:
    def test_resolves_ticker_and_returns_summary(self, monkeypatch):
        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def execute(self, _sql, _params=None):
                pass

            def fetchone(self):
                return (5718,)

        class Connection:
            def cursor(self):
                return Cursor()

        @contextmanager
        def pooled_connection():
            yield Connection()

        monkeypatch.setattr(data_coverage, "get_pooled_connection", pooled_connection)
        monkeypatch.setattr(
            data_coverage,
            "summarize_company",
            lambda conn, company_id: {"company_id": company_id, "company_name": "Visa Inc."},
        )
        result = data_coverage.get_company_coverage(ticker="V", _="user-a")
        assert result["company_id"] == 5718
        assert result["company_name"] == "Visa Inc."

    def test_unknown_ticker_raises_404(self, monkeypatch):
        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def execute(self, _sql, _params=None):
                pass

            def fetchone(self):
                return None

        class Connection:
            def cursor(self):
                return Cursor()

        @contextmanager
        def pooled_connection():
            yield Connection()

        monkeypatch.setattr(data_coverage, "get_pooled_connection", pooled_connection)
        with pytest.raises(HTTPException) as exc_info:
            data_coverage.get_company_coverage(ticker="NOTREAL", _="user-a")
        assert exc_info.value.status_code == 404
