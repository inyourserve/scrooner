"""Warm result-cache entries for reviewed popular screen-template values.

This is intentionally callable infrastructure rather than an HTTP endpoint:
operations can run it immediately after a screening-snapshot refresh. Cache
identity remains the canonical query plus dataset version used everywhere
else; template IDs are observability labels, never correctness keys.
"""

import json

from cache import get_cached_result, set_cached_result
from scrooner_pipeline.ai_query.screen_templates import prewarm_queries
from scrooner_pipeline.screener.cache_key import compute_query_hash
from scrooner_pipeline.screener.query import run_query


def warm_template_cache(conn, dataset_version: int, prepare_query) -> dict:
    warmed = 0
    already_warm = 0
    failures: list[dict[str, str]] = []

    for template_id, raw_query in prewarm_queries():
        query = prepare_query(raw_query)
        query_hash = compute_query_hash(query, dataset_version)
        if get_cached_result(query_hash) is not None:
            already_warm += 1
            continue
        try:
            result = run_query(conn, query, dataset_version=dataset_version)
            set_cached_result(query_hash, result)
            warmed += 1
        except Exception as error:  # one bad template must not block the rest
            failures.append({"template_id": template_id, "error": type(error).__name__})

    return {
        "dataset_version": dataset_version,
        "warmed": warmed,
        "already_warm": already_warm,
        "failures": failures,
    }


def main() -> None:
    """One-shot operational entry point to run after a snapshot refresh."""
    from routers.screen_runs import prepare_screen_run_query
    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.screener.snapshot import get_dataset_version

    with get_connection() as conn:
        dataset_version = get_dataset_version(conn)
        result = warm_template_cache(conn, dataset_version, prepare_screen_run_query)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
