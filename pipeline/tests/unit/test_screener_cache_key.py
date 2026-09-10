import pytest

from scrooner_pipeline.screener.cache_key import compute_query_hash
from scrooner_pipeline.screener.schema import MetricPredicate, PredicateGroup, ScreenQuery

A = MetricPredicate(metric_name="roe", operator=">", value="0.1")
B = MetricPredicate(metric_name="debt_to_equity", operator="<", value="1")


@pytest.mark.unit
def test_or_children_hash_identically_regardless_of_order():
    q1 = ScreenQuery(where=PredicateGroup(op="or", predicates=[A, B]))
    q2 = ScreenQuery(where=PredicateGroup(op="or", predicates=[B, A]))
    assert compute_query_hash(q1, dataset_version=1) == compute_query_hash(q2, dataset_version=1)


@pytest.mark.unit
def test_flat_and_predicates_hash_identically_regardless_of_order():
    q1 = ScreenQuery(metric_predicates=[A, B])
    q2 = ScreenQuery(metric_predicates=[B, A])
    assert compute_query_hash(q1, dataset_version=1) == compute_query_hash(q2, dataset_version=1)


@pytest.mark.unit
def test_different_dataset_version_changes_the_hash():
    q = ScreenQuery(metric_predicates=[A])
    assert compute_query_hash(q, dataset_version=1) != compute_query_hash(q, dataset_version=2)


@pytest.mark.unit
def test_different_queries_hash_differently():
    q1 = ScreenQuery(metric_predicates=[A])
    q2 = ScreenQuery(metric_predicates=[B])
    assert compute_query_hash(q1, dataset_version=1) != compute_query_hash(q2, dataset_version=1)


@pytest.mark.unit
def test_and_vs_or_of_the_same_children_hash_differently():
    q1 = ScreenQuery(where=PredicateGroup(op="and", predicates=[A, B]))
    q2 = ScreenQuery(where=PredicateGroup(op="or", predicates=[A, B]))
    assert compute_query_hash(q1, dataset_version=1) != compute_query_hash(q2, dataset_version=1)
