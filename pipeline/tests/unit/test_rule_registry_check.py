"""Registry check (lane 3 item 1): consumer counts come from the graph, and a serve-time
classification FAILS when the graph shows stored consumers."""

from __future__ import annotations

import pytest
from scrooner_pipeline.common import rule_registry_check as rc

ROOT = rc.repo_root()
GRAPH = rc.load_graph(ROOT / rc.GRAPH_REL)
ROWS = rc.load_registry(ROOT / rc.REGISTRY_REL)


def _row(**kw):
    base = {
        "rf": "RF-X",
        "frozen_rule_id": "x.y@1",
        "action": "hide",
        "guarded_nodes": "gross_margin",
        "classification": "serve_time",
        "consumers_direct": "0",
        "consumers_transitive": "0",
    }
    base.update(kw)
    return base


@pytest.mark.parametrize(
    ("node", "direct"),
    [
        ("market_cap", 7),
        ("shares_outstanding", 12),
        ("gross_margin", 0),
        ("cost_of_revenue", 4),
    ],
)
def test_known_consumer_counts_from_the_graph(node, direct):
    got, _ = rc.stored_consumers(GRAPH, {node})
    assert len(got) == direct


def test_committed_registry_and_seeds_are_clean():
    assert rc.run(ROOT) == []


@pytest.mark.parametrize(
    "node",
    ["market_cap", "shares_outstanding", "cost_of_revenue", "total_debt_resolved"],
)
def test_serve_time_hide_of_node_with_stored_consumers_fails(node):
    f = rc.check_registry(GRAPH, [_row(guarded_nodes=node)])
    assert [x.code for x in f] == ["serve_time_has_consumers"]


def test_serve_time_hide_of_true_leaf_passes():
    assert rc.check_registry(GRAPH, [_row()]) == []
    ok, trans = rc.serve_time_allowed(GRAPH, {"gross_margin"})
    assert ok and not trans


def test_declared_serve_time_on_stored_rule_is_a_mismatch():
    f = rc.check_registry(
        GRAPH,
        [
            _row(
                action="writer_change",
                guarded_nodes="market_cap",
                consumers_direct="7",
                consumers_transitive="7",
            )
        ],
    )
    assert "classification_mismatch" in [x.code for x in f]


def test_display_only_ignores_consumers():
    f = rc.check_registry(
        GRAPH,
        [
            _row(
                action="display_only",
                guarded_nodes="market_cap",
                consumers_direct="7",
                consumers_transitive="7",
            )
        ],
    )
    assert f == []


def test_unknown_node_and_stale_counts_fail():
    codes = [
        x.code for x in rc.check_registry(GRAPH, [_row(guarded_nodes="no_such_node")])
    ]
    assert "unknown_node" in codes
    stale = _row(
        action="writer_change",
        guarded_nodes="market_cap",
        classification="recompute_cascade",
        consumers_direct="6",
        consumers_transitive="7",
    )
    assert [x.code for x in rc.check_registry(GRAPH, [stale])] == ["count_mismatch"]


def test_mutation_removing_a_graph_edge_is_caught():
    """If a stored consumer disappears from the graph the committed counts no longer match."""
    mutated = dict(GRAPH)
    pe = mutated["price_to_book"]
    mutated["price_to_book"] = rc.Node(
        pe.name, pe.kind, pe.basis, tuple(i for i in pe.inputs if i != "market_cap")
    )
    assert any(f.code == "count_mismatch" for f in rc.check_registry(mutated, ROWS))


def test_mutation_flipping_a_committed_row_to_serve_time_is_caught():
    mutated = [dict(r) for r in ROWS]
    for r in mutated:
        if r["rf"] == "RF-15":
            r["action"], r["classification"] = "hide", "serve_time"
    assert any(
        f.code == "serve_time_has_consumers" for f in rc.check_registry(GRAPH, mutated)
    )


def test_seed_drift_detects_unknown_metric():
    g = {k: v for k, v in GRAPH.items() if k != "gross_margin"}
    assert any(
        f.code == "seed_not_in_graph" and f.rule == "gross_margin"
        for f in rc.check_seed_drift(g)
    )
