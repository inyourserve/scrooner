import pytest
from redis.exceptions import ConnectionError

import cache


@pytest.mark.unit
def test_cache_read_failure_falls_back_to_database(monkeypatch):
    monkeypatch.setattr(
        cache._client,
        "get",
        lambda _key: (_ for _ in ()).throw(ConnectionError("offline")),
    )

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
    monkeypatch.setattr(
        cache._client, "set", lambda key, *_args, **_kwargs: keys.append(key)
    )

    cache.set_cached_run_id("user-a", "query", "ROE above 20%", "run-1")
    cache.set_cached_run_id("user-b", "query", "ROE above 20%", "run-2")
    cache.set_cached_run_id("user-a", "query", "ROE above 30%", "run-3")

    assert len(set(keys)) == 3
    assert all("ROE" not in key for key in keys)


@pytest.mark.unit
def test_cached_run_page_round_trips_json(monkeypatch):
    stored = {}
    monkeypatch.setattr(
        cache._client, "set", lambda key, value, **_kwargs: stored.update({key: value})
    )
    monkeypatch.setattr(cache._client, "get", lambda key: stored.get(key))

    page = {"run_id": "run-1", "items": [{"company_id": 1}]}
    cache.set_cached_run_page("user-a", "run-1", 50, None, page)

    assert cache.get_cached_run_page("user-a", "run-1", 50, None) == page
    assert cache.get_cached_run_page("user-b", "run-1", 50, None) is None


@pytest.mark.unit
def test_get_cached_run_lookup_is_one_pipelined_round_trip(monkeypatch):
    # create_run_from_query's hot-path read: assert it's exactly one
    # .pipeline().execute() call, not two sequential .get() calls.
    calls = []

    class FakePipeline:
        def __init__(self):
            self.queued = []

        def get(self, key):
            self.queued.append(key)
            return self

        def execute(self):
            calls.append(list(self.queued))
            return ["run-1", None]

    monkeypatch.setattr(cache._client, "pipeline", lambda transaction=True: FakePipeline())

    run_id, result = cache.get_cached_run_lookup("user-a", "query-hash", "ROE above 20%")

    assert run_id == "run-1"
    assert result is None
    assert len(calls) == 1 and len(calls[0]) == 2


@pytest.mark.unit
def test_get_cached_run_lookup_falls_back_on_pipeline_error(monkeypatch):
    monkeypatch.setattr(
        cache._client,
        "pipeline",
        lambda transaction=True: (_ for _ in ()).throw(ConnectionError("offline")),
    )

    assert cache.get_cached_run_lookup("user-a", "query-hash", "text") == (None, None)


@pytest.mark.unit
def test_set_cached_run_write_is_one_pipelined_round_trip_and_round_trips(monkeypatch):
    stored = {}
    executed_batches = []

    class FakePipeline:
        def __init__(self):
            self.queued = []

        def set(self, key, value, **_kwargs):
            self.queued.append((key, value))
            return self

        def execute(self):
            for key, value in self.queued:
                stored[key] = value
            executed_batches.append(len(self.queued))

    monkeypatch.setattr(cache._client, "pipeline", lambda transaction=True: FakePipeline())
    monkeypatch.setattr(cache._client, "get", lambda key: stored.get(key))

    cache.set_cached_run_write(
        query_hash="query-hash",
        result={"matched": []},
        user_id="user-a",
        query_text="ROE above 20%",
        run_id="run-1",
        page_size=50,
        page={"run_id": "run-1", "items": []},
    )

    assert executed_batches == [3], "result + run-id pointer + first page, one round trip"
    assert cache.get_cached_result("query-hash") == {"matched": []}
    assert cache.get_cached_run_page("user-a", "run-1", 50, None) == {
        "run_id": "run-1",
        "items": [],
    }


@pytest.mark.unit
def test_set_cached_run_write_skips_result_when_already_cached(monkeypatch):
    executed_batches = []

    class FakePipeline:
        def __init__(self):
            self.queued = []

        def set(self, key, value, **_kwargs):
            self.queued.append((key, value))
            return self

        def execute(self):
            executed_batches.append(len(self.queued))

    monkeypatch.setattr(cache._client, "pipeline", lambda transaction=True: FakePipeline())

    cache.set_cached_run_write(
        query_hash="query-hash",
        result=None,  # already cached -- caller must not re-set it
        user_id="user-a",
        query_text="ROE above 20%",
        run_id="run-1",
        page_size=50,
        page={"run_id": "run-1", "items": []},
    )

    assert executed_batches == [2], "only the run-id pointer + page, no result write"
