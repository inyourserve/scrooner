import pytest

import cache
from company_page import _assemble_statement
from routers import company as company_router


@pytest.mark.unit
def test_assemble_statement_dedupes_periods_and_sorts_lines():
    rows = [
        {"statement": "income_statement", "display_order": 2, "display_label": "Revenue",
         "fiscal_year": 2025, "fiscal_period": "FY", "period_end": "2025-12-31", "value": "100"},
        {"statement": "income_statement", "display_order": 1, "display_label": "COGS",
         "fiscal_year": 2025, "fiscal_period": "FY", "period_end": "2025-12-31", "value": "40"},
        {"statement": "income_statement", "display_order": 2, "display_label": "Revenue",
         "fiscal_year": 2024, "fiscal_period": "FY", "period_end": "2024-12-31", "value": "90"},
        # A different statement entirely, and a quarterly row -- both must
        # be excluded from an "annual, income_statement" assembly.
        {"statement": "balance_sheet", "display_order": 1, "display_label": "Assets",
         "fiscal_year": 2025, "fiscal_period": "FY", "period_end": "2025-12-31", "value": "500"},
        {"statement": "income_statement", "display_order": 1, "display_label": "COGS",
         "fiscal_year": 2025, "fiscal_period": "Q4", "period_end": "2025-12-31", "value": "10"},
    ]

    result = _assemble_statement(rows, "income_statement", "annual")

    assert result["periods"] == [
        {"fiscal_year": 2024, "fiscal_period": "FY", "period_end": "2024-12-31"},
        {"fiscal_year": 2025, "fiscal_period": "FY", "period_end": "2025-12-31"},
    ]
    # Lines sorted by display_order; a period with no value for a line is None.
    assert result["lines"] == [
        {"label": "COGS", "values": [None, "40"]},
        {"label": "Revenue", "values": ["90", "100"]},
    ]


@pytest.mark.unit
def test_assemble_statement_quarterly_excludes_fy_rows():
    rows = [
        {"statement": "income_statement", "display_order": 1, "display_label": "Revenue",
         "fiscal_year": 2025, "fiscal_period": "FY", "period_end": "2025-12-31", "value": "400"},
        {"statement": "income_statement", "display_order": 1, "display_label": "Revenue",
         "fiscal_year": 2025, "fiscal_period": "Q4", "period_end": "2025-12-31", "value": "100"},
    ]

    result = _assemble_statement(rows, "income_statement", "quarterly")

    assert result["periods"] == [{"fiscal_year": 2025, "fiscal_period": "Q4", "period_end": "2025-12-31"}]
    assert result["lines"] == [{"label": "Revenue", "values": ["100"]}]


@pytest.mark.unit
def test_get_company_uses_cache_on_hit_without_touching_the_db(monkeypatch):
    cached_page = {"company": {"ticker": "AAPL"}}
    monkeypatch.setattr(company_router, "get_cached_company_page", lambda ticker: cached_page)
    monkeypatch.setattr(
        company_router,
        "get_pooled_connection",
        lambda: (_ for _ in ()).throw(AssertionError("must not touch the DB on a cache hit")),
    )

    assert company_router.get_company("aapl") == cached_page


@pytest.mark.unit
def test_get_company_404s_and_caches_the_miss_on_a_real_db_miss(monkeypatch):
    class FakeConnection:
        pass

    from contextlib import contextmanager

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    cached_writes = []
    monkeypatch.setattr(company_router, "get_cached_company_page", lambda ticker: cache.CACHE_MISS)
    monkeypatch.setattr(company_router, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(company_router, "get_company_page_data", lambda conn, ticker: None)
    monkeypatch.setattr(
        company_router,
        "set_cached_company_page",
        lambda ticker, data: cached_writes.append((ticker, data)),
    )

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        company_router.get_company("zzznotreal")
    assert excinfo.value.status_code == 404
    # The not-found result is itself cached -- a persistently bad ticker
    # shouldn't re-query Postgres on every request.
    assert cached_writes == [("zzznotreal", None)]
