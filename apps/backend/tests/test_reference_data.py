from contextlib import contextmanager

import pytest

import cache
from reference_data import slugify
from routers import reference_data as reference_router


@pytest.mark.unit
def test_slugify_matches_db_ts_behavior():
    assert slugify("Software - Application") == "software-application"
    assert slugify("Banks - Regional") == "banks-regional"
    assert slugify("  Oil & Gas  ") == "oil-gas"


@pytest.mark.unit
def test_get_directory_uses_cache_on_hit_without_touching_the_db(monkeypatch):
    cached_rows = [
        {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology",
        }
    ]
    monkeypatch.setattr(
        reference_router, "get_cached_reference", lambda name: cached_rows
    )
    monkeypatch.setattr(
        reference_router,
        "get_pooled_connection",
        lambda: (_ for _ in ()).throw(
            AssertionError("must not touch the DB on a cache hit")
        ),
    )

    assert reference_router.get_directory() == cached_rows


@pytest.mark.unit
def test_get_directory_queries_and_caches_on_a_real_miss(monkeypatch):
    class FakeConnection:
        pass

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    rows = [
        {
            "ticker": "MSFT",
            "company_name": "Microsoft Corp.",
            "exchange": "NASDAQ",
            "sector": "Technology",
        }
    ]
    cached_writes = []
    monkeypatch.setattr(
        reference_router, "get_cached_reference", lambda name: cache.CACHE_MISS
    )
    monkeypatch.setattr(reference_router, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(reference_router, "load_full_directory", lambda conn: rows)
    monkeypatch.setattr(
        reference_router,
        "set_cached_reference",
        lambda name, data: cached_writes.append((name, data)),
    )

    assert reference_router.get_directory() == rows
    assert cached_writes == [("directory", rows)]


@pytest.mark.unit
def test_get_sector_404s_and_caches_the_miss_on_an_unknown_slug(monkeypatch):
    class FakeConnection:
        pass

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    cached_writes = []
    monkeypatch.setattr(
        reference_router, "get_cached_reference", lambda name: cache.CACHE_MISS
    )
    monkeypatch.setattr(reference_router, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(
        reference_router, "get_companies_by_sector_slug", lambda conn, slug: None
    )
    monkeypatch.setattr(
        reference_router,
        "set_cached_reference",
        lambda name, data: cached_writes.append((name, data)),
    )

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        reference_router.get_sector("not-a-real-sector")
    assert excinfo.value.status_code == 404
    # A bad slug is itself a cacheable result -- it shouldn't re-query
    # Postgres on every request, same discipline as company.py's 404 cache.
    assert cached_writes == [("sector:not-a-real-sector", None)]


@pytest.mark.unit
def test_get_sector_returns_cached_data_on_a_hit_without_touching_the_db(monkeypatch):
    cached = {"sector": "Technology", "companies": [{"ticker": "AAPL"}]}
    monkeypatch.setattr(reference_router, "get_cached_reference", lambda name: cached)
    monkeypatch.setattr(
        reference_router,
        "get_pooled_connection",
        lambda: (_ for _ in ()).throw(
            AssertionError("must not touch the DB on a cache hit")
        ),
    )

    assert reference_router.get_sector("technology") == cached


@pytest.mark.unit
def test_get_companies_with_no_tickers_returns_empty_without_cache_or_db(monkeypatch):
    monkeypatch.setattr(
        reference_router,
        "get_cached_reference",
        lambda name: (_ for _ in ()).throw(
            AssertionError("must not touch the cache for an empty ticker list")
        ),
    )
    monkeypatch.setattr(
        reference_router,
        "get_pooled_connection",
        lambda: (_ for _ in ()).throw(
            AssertionError("must not touch the DB for an empty ticker list")
        ),
    )

    assert reference_router.get_companies(tickers="  , ,") == []


@pytest.mark.unit
def test_get_companies_normalizes_ticker_list_into_a_stable_sorted_cache_key(
    monkeypatch,
):
    seen_keys = []

    def fake_get_cached_reference(name):
        seen_keys.append(name)
        return cache.CACHE_MISS

    class FakeConnection:
        pass

    @contextmanager
    def pooled_connection():
        yield FakeConnection()

    monkeypatch.setattr(
        reference_router, "get_cached_reference", fake_get_cached_reference
    )
    monkeypatch.setattr(reference_router, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(
        reference_router, "get_companies_by_tickers", lambda conn, tickers: []
    )
    monkeypatch.setattr(
        reference_router, "set_cached_reference", lambda name, data: None
    )

    # Mixed case, whitespace, and reverse order must all resolve to the
    # same cache key -- the cache key is the normalized ticker set, not
    # the caller's raw query string.
    reference_router.get_companies(tickers=" msft, aapl ,AAPL")
    assert seen_keys == ["companies:AAPL,MSFT"]
