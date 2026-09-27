import pytest

import template_cache_warmer


@pytest.mark.unit
def test_warmer_skips_hits_and_caches_misses(monkeypatch):
    queries = [("pe_max", object()), ("roe_min", object())]
    cached = {"hash-0": {"matched": []}}
    writes = []
    runs = []

    monkeypatch.setattr(
        template_cache_warmer, "prewarm_queries", lambda: tuple(queries)
    )
    monkeypatch.setattr(
        template_cache_warmer,
        "compute_query_hash",
        lambda query, _version: (
            f"hash-{queries.index(next(item for item in queries if item[1] is query))}"
        ),
    )
    monkeypatch.setattr(
        template_cache_warmer, "get_cached_result", lambda key: cached.get(key)
    )
    monkeypatch.setattr(
        template_cache_warmer,
        "set_cached_result",
        lambda key, result: writes.append((key, result)),
    )
    monkeypatch.setattr(
        template_cache_warmer,
        "run_query",
        lambda _conn, query, dataset_version: (
            runs.append((query, dataset_version)) or {"matched": [1]}
        ),
    )

    result = template_cache_warmer.warm_template_cache(
        object(),
        dataset_version=7,
        prepare_query=lambda query: query,
    )

    assert result == {
        "dataset_version": 7,
        "warmed": 1,
        "already_warm": 1,
        "failures": [],
    }
    assert runs == [(queries[1][1], 7)]
    assert writes == [("hash-1", {"matched": [1]})]


@pytest.mark.unit
def test_one_failed_template_does_not_stop_remaining_warmups(monkeypatch):
    queries = [("broken", "bad"), ("healthy", "good")]
    writes = []

    monkeypatch.setattr(
        template_cache_warmer, "prewarm_queries", lambda: tuple(queries)
    )
    monkeypatch.setattr(
        template_cache_warmer, "compute_query_hash", lambda query, _version: query
    )
    monkeypatch.setattr(template_cache_warmer, "get_cached_result", lambda _key: None)
    monkeypatch.setattr(
        template_cache_warmer,
        "set_cached_result",
        lambda key, result: writes.append((key, result)),
    )

    def run(_conn, query, dataset_version):
        if query == "bad":
            raise ValueError("bad template")
        return {"matched": []}

    monkeypatch.setattr(template_cache_warmer, "run_query", run)

    result = template_cache_warmer.warm_template_cache(
        object(),
        dataset_version=8,
        prepare_query=lambda query: query,
    )

    assert result["warmed"] == 1
    assert result["failures"] == [{"template_id": "broken", "error": "ValueError"}]
    assert writes == [("good", {"matched": []})]
