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
