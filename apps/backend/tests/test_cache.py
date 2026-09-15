import pytest
from redis.exceptions import ConnectionError

import cache


@pytest.mark.unit
def test_cache_read_failure_falls_back_to_database(monkeypatch):
    monkeypatch.setattr(cache._client, "get", lambda _key: (_ for _ in ()).throw(ConnectionError("offline")))

    assert cache.get_cached_result("query") is None


@pytest.mark.unit
def test_cache_write_failure_does_not_fail_request(monkeypatch):
    monkeypatch.setattr(
        cache._client,
        "set",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ConnectionError("offline")),
    )

    assert cache.set_cached_result("query", {"matched": []}) is None


@pytest.mark.unit
def test_malformed_cache_entry_is_a_miss(monkeypatch):
    monkeypatch.setattr(cache._client, "get", lambda _key: "not-json")

    assert cache.get_cached_result("query") is None


@pytest.mark.unit
def test_repeat_run_key_is_user_and_text_scoped(monkeypatch):
    keys = []
    monkeypatch.setattr(cache._client, "set", lambda key, *_args, **_kwargs: keys.append(key))

    cache.set_cached_run_id("user-a", "query", "ROE above 20%", "run-1")
    cache.set_cached_run_id("user-b", "query", "ROE above 20%", "run-2")
    cache.set_cached_run_id("user-a", "query", "ROE above 30%", "run-3")

    assert len(set(keys)) == 3
    assert all("ROE" not in key for key in keys)


@pytest.mark.unit
def test_cached_run_page_round_trips_json(monkeypatch):
    stored = {}
    monkeypatch.setattr(cache._client, "set", lambda key, value, **_kwargs: stored.update({key: value}))
    monkeypatch.setattr(cache._client, "get", lambda key: stored.get(key))

    page = {"run_id": "run-1", "items": [{"company_id": 1}]}
    cache.set_cached_run_page("user-a", "run-1", 50, None, page)

    assert cache.get_cached_run_page("user-a", "run-1", 50, None) == page
    assert cache.get_cached_run_page("user-b", "run-1", 50, None) is None
