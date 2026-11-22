"""AI query eval set (SYSTEMS.md #18): shape, coverage and the baseline gate.

The deterministic interpreter's exact-match rate on the eval set may not drop
below the committed baseline (tests/fixtures/ai_query/baseline.json), and no
ask that must produce no list (an opinion, a pick, a vague or contradictory
ask) may ever produce an executable query.
"""

import json
from decimal import Decimal

import pytest
from scrooner_pipeline.ai_query import llm_interpreter
from scrooner_pipeline.ai_query.aliases import (
    METRIC_ALIASES,
    SECTOR_ALIASES,
    SECTOR_BUCKET_ALIASES,
)
from scrooner_pipeline.ai_query.evaluation import (
    BASELINE_PATH,
    canonical,
    load_eval_set,
    score,
)
from scrooner_pipeline.ai_query.rules import interpret
from scrooner_pipeline.metrics.registry import get_registry
from scrooner_pipeline.screener.schema import (
    CategoricalPredicate,
    MetricPredicate,
    PredicateGroup,
    ScreenQuery,
)

CASES = load_eval_set()
REQUIRED_CATEGORIES = {
    "alias",
    "registry_label",
    "comparison",
    "between",
    "boolean",
    "sector",
    "ranked",
    "growth",
    "refusal",
    "include_missing",
}


def _leaves(query: ScreenQuery):
    yield from query.metric_predicates
    yield from query.categorical_predicates

    def visit(node):
        if isinstance(node, PredicateGroup):
            for child in node.predicates:
                yield from visit(child)
        else:
            yield node

    if query.where is not None:
        yield from visit(query.where)


@pytest.mark.unit
def test_eval_set_shape():
    assert len(CASES) >= 150
    assert len({c.id for c in CASES}) == len(CASES)
    assert REQUIRED_CATEGORIES <= {c.category for c in CASES}
    assert sum(1 for c in CASES if c.category == "refusal") >= 15
    for c in CASES:
        if c.category in {"refusal", "diagnostic_refusal"}:
            assert c.expected is None, c.id


@pytest.mark.unit
def test_eval_set_covers_every_alias_registry_metric_and_sector():
    asks = {c.ask for c in CASES}
    for alias in METRIC_ALIASES:
        assert any(a.startswith(alias + " ") for a in asks), alias
    registry = get_registry()
    expected_metrics = {
        p.metric_name
        for c in CASES
        if c.expected is not None
        for p in _leaves(c.expected)
        if isinstance(p, MetricPredicate)
    }
    assert expected_metrics <= set(registry)
    missing = set(registry) - expected_metrics - llm_interpreter.DIAGNOSTIC_METRICS
    assert not missing, sorted(missing)
    sectors = {
        p.value
        for c in CASES
        if c.expected is not None
        for p in _leaves(c.expected)
        if isinstance(p, CategoricalPredicate)
    }
    assert set(SECTOR_ALIASES.values()) | set(SECTOR_BUCKET_ALIASES.values()) <= sectors
    assert any(
        p.include_missing
        for c in CASES
        if c.expected is not None
        for p in _leaves(c.expected)
        if isinstance(p, MetricPredicate)
    )


@pytest.mark.unit
def test_canonical_ignores_order_and_spelling_but_not_meaning():
    roe = MetricPredicate(metric_name="roe", operator=">", value=Decimal("0.15"))
    roe2 = MetricPredicate(metric_name="roe", operator=">", value=Decimal("0.150"))
    tech = CategoricalPredicate(field="sector", operator="=", value="Technology")
    flat = ScreenQuery(metric_predicates=[roe], categorical_predicates=[tech])
    tree = ScreenQuery(where=PredicateGroup(op="and", predicates=[tech, roe2]))
    assert canonical(flat) == canonical(tree)
    roe_inc = MetricPredicate(
        metric_name="roe", operator=">", value=Decimal("0.15"), include_missing=True
    )
    assert canonical(ScreenQuery(metric_predicates=[roe])) != canonical(
        ScreenQuery(metric_predicates=[roe_inc])
    )
    either = ScreenQuery(where=PredicateGroup(op="or", predicates=[roe, tech]))
    assert canonical(either) != canonical(flat)


@pytest.mark.unit
def test_no_query_where_none_is_correct():
    """Hard rule: an opinion, pick or vague ask never yields an executable query."""
    leaked = [
        c.id for c in CASES if c.expected is None and interpret(c.ask).query is not None
    ]
    assert not leaked


@pytest.mark.unit
def test_deterministic_hit_rate_does_not_drop_below_baseline():
    baseline = json.loads(BASELINE_PATH.read_text())
    report = score(interpret, CASES)
    print("\n" + report.summary())
    assert report.total == baseline["total"], (
        "eval set size changed: re-measure and update baseline.json in the same commit"
    )
    assert report.hits >= baseline["hits"], report.summary()


@pytest.mark.unit
def test_wired_entry_point_matches_deterministic_without_a_client():
    report = score(llm_interpreter.interpret, CASES)
    assert report.hits == score(interpret, CASES).hits
