import pytest

from scrooner_pipeline.ai_query.screen_templates import load_screen_templates, prewarm_queries
from scrooner_pipeline.screener.cache_key import compute_query_hash


@pytest.mark.unit
def test_stored_screen_templates_are_unique_and_cached():
    templates = load_screen_templates()

    assert len({template.id for template in templates}) == len(templates)
    assert load_screen_templates() is templates


@pytest.mark.unit
def test_every_prewarm_variant_has_a_distinct_canonical_cache_key():
    variants = prewarm_queries()
    hashes = [compute_query_hash(query, dataset_version=7) for _, query in variants]

    assert len(variants) == 15
    assert len(hashes) == len(set(hashes))
