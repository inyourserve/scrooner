"""Rule registry check: computes stored-consumer counts from the metric dependency
graph and FAILS a rule whose classification contradicts them (data-team lane 3, item 1).

Why: a "serve-time" hide of a node that stored metrics read leaks the wrong value
through those metrics (market_cap has 7 stored consumers, shares_outstanding 12,
cost_of_revenue 4; gross_margin has 0). The classification must be computed from
the graph, not asserted in prose.

Inputs (both under data-team/strategy/data/):
  metric_dependency_graph.csv  node, kind, period_basis, direct_inputs(node:role)
  rule_registry_draft.csv      rf, frozen_rule_id, action, guarded_nodes, classification,
                               consumers_direct, consumers_transitive, ...

Evidence label: CODE-READ + DATA-INFERRED (the graph is a hand-extracted CSV of the
2026-10-21 code; ``check_seed_drift`` ties it back to the code's own metric seeds so a
metric added in code without a graph row, or with inputs the graph lacks, fails).

Run: ``python -m scrooner_pipeline.common.rule_registry_check`` (exit 1 on any failure).
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

GRAPH_REL = Path("data-team/strategy/data/metric_dependency_graph.csv")
REGISTRY_REL = Path("data-team/strategy/data/rule_registry_draft.csv")

# actions that change a stored value or state
STORED_ACTIONS = {"writer_change", "state_at_metric"}
# actions that only hide or relabel at serve time: legal ONLY for true leaves
HIDE_ACTIONS = {"hide"}
# acts on a display panel; the stored value is unaffected, consumers are irrelevant
DISPLAY_ACTIONS = {"display_only"}

UPSTREAM_ALL = "upstream (all concepts)"
UPSTREAM_DURATION = "upstream (all duration leaves)"


@dataclass(frozen=True)
class Node:
    name: str
    kind: str
    basis: str
    inputs: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    rule: str
    code: str
    message: str


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "data-team").is_dir() and (p / "pipeline").is_dir():
            return p
    raise FileNotFoundError(
        "repo root (data-team/ and pipeline/) not found above " + str(here)
    )


def load_graph(path: Path) -> dict[str, Node]:
    graph: dict[str, Node] = {}
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            raw = row["direct_inputs(node:role)"]
            inputs = tuple(p.split(":")[0] for p in raw.split(";") if p)
            graph[row["data_point"]] = Node(
                row["data_point"], row["kind"], row["period_basis"], inputs
            )
    return graph


def load_registry(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def consumer_index(graph: dict[str, Node]) -> dict[str, set[str]]:
    idx: dict[str, set[str]] = {}
    for node in graph.values():
        for src in node.inputs:
            idx.setdefault(src, set()).add(node.name)
    return idx


def resolve_nodes(graph: dict[str, Node], guarded: str) -> tuple[set[str], set[str]]:
    """Return (nodes, unknown). 'upstream (...)' expands to the leaf concepts."""
    token = guarded.strip()
    if token == UPSTREAM_ALL:
        return {n.name for n in graph.values() if n.kind == "leaf_concept"}, set()
    if token == UPSTREAM_DURATION:
        return (
            {
                n.name
                for n in graph.values()
                if n.kind == "leaf_concept" and n.basis == "duration"
            },
            set(),
        )
    names = {t for t in token.split(";") if t}
    unknown = {n for n in names if n not in graph}
    return names - unknown, unknown


def stored_consumers(
    graph: dict[str, Node], nodes: set[str]
) -> tuple[set[str], set[str]]:
    """(direct, transitive) stored consumers of ``nodes``, excluding ``nodes`` themselves."""
    idx = consumer_index(graph)
    direct: set[str] = set()
    for n in nodes:
        direct |= idx.get(n, set())
    direct -= nodes
    seen = set(direct)
    stack = list(direct)
    while stack:
        cur = stack.pop()
        for nxt in idx.get(cur, ()):
            if nxt not in seen and nxt not in nodes:
                seen.add(nxt)
                stack.append(nxt)
    return direct, seen


def expected_classification(action: str, transitive: int) -> str | None:
    """None means the combination is forbidden (a hide of a node with stored consumers)."""
    if action in DISPLAY_ACTIONS:
        return "serve_time"
    if action in HIDE_ACTIONS:
        return "serve_time" if transitive == 0 else None
    if action in STORED_ACTIONS:
        return "recompute_leaf" if transitive == 0 else "recompute_cascade"
    return None


def serve_time_allowed(
    graph: dict[str, Node], nodes: set[str]
) -> tuple[bool, set[str]]:
    """The question a registry reviewer asks: may this node set be hidden at serve time only?"""
    _, trans = stored_consumers(graph, nodes)
    return (not trans), trans


def check_registry(graph: dict[str, Node], rows: list[dict[str, str]]) -> list[Finding]:
    out: list[Finding] = []
    for row in rows:
        rid = f"{row['rf']} {row['frozen_rule_id']}"
        action = row["action"]
        nodes, unknown = resolve_nodes(graph, row["guarded_nodes"])
        if unknown:
            out.append(Finding(rid, "unknown_node", f"not in graph: {sorted(unknown)}"))
        if not nodes:
            out.append(Finding(rid, "no_nodes", "rule guards no known node"))
            continue
        direct, trans = stored_consumers(graph, nodes)
        want = expected_classification(action, len(trans))
        if want is None:
            if action in HIDE_ACTIONS:
                out.append(
                    Finding(
                        rid,
                        "serve_time_has_consumers",
                        f"serve-time hide of nodes with {len(trans)} stored consumers "
                        f"{sorted(trans)[:6]}: the wrong value would leak through them; "
                        "must be a stored (recompute) rule",
                    )
                )
            else:
                out.append(Finding(rid, "bad_action", f"unknown action {action!r}"))
            continue
        if row["classification"] != want:
            out.append(
                Finding(
                    rid,
                    "classification_mismatch",
                    f"declared {row['classification']!r}, graph says {want!r} "
                    f"({len(direct)} direct / {len(trans)} transitive consumers)",
                )
            )
        if (
            row["classification"] == "serve_time"
            and action not in DISPLAY_ACTIONS
            and trans
        ):
            out.append(
                Finding(
                    rid, "serve_time_has_consumers", f"{len(trans)} stored consumers"
                )
            )
        for col, got in (
            ("consumers_direct", len(direct)),
            ("consumers_transitive", len(trans)),
        ):
            if str(got) != row[col]:
                out.append(
                    Finding(
                        rid,
                        "count_mismatch",
                        f"{col}: declared {row[col]}, computed {got}",
                    )
                )
    return out


def ultimate_inputs(graph: dict[str, Node], name: str) -> set[str]:
    seen: set[str] = set()
    stack = list(graph[name].inputs) if name in graph else []
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur in graph:
            stack.extend(graph[cur].inputs)
    return seen


def check_seed_drift(graph: dict[str, Node]) -> list[Finding]:
    """Code -> graph: every seeded metric must be a graph node and its seeded inputs must
    be reachable from the graph node's inputs (price metrics reach shares via market_cap)."""
    from scrooner_pipeline.mapper import definitions, expanded_definitions

    out: list[Finding] = []
    for module in (definitions, expanded_definitions):
        for entry in module.METRIC_DEFINITIONS:
            name, inputs = entry[0], entry[-1]
            if name not in graph:
                out.append(
                    Finding(
                        name,
                        "seed_not_in_graph",
                        f"seeded in {module.__name__}, absent from graph",
                    )
                )
                continue
            reach = ultimate_inputs(graph, name)
            missing = {i[0] for i in inputs} - reach
            if missing:
                out.append(
                    Finding(
                        name,
                        "seed_input_not_in_graph",
                        f"inputs {sorted(missing)} not reachable",
                    )
                )
    return out


# Rule IDs that exist in code (behind a flag) but have no registry row yet. Each needs a Chief
# RF number; the check lists them as findings once removed from this set.
PENDING_REGISTRY_IDS = frozenset(
    {
        "employee_count.no_yfinance_tier@1",  # D-4, founder-approved, no RF number yet
        "debt.metrics_pending_ac1@1",  # AC-1 interim hide of the ten consumers
        "mcap.ads_conversion@1",  # NA-15, registered in common/rule_flags, no registry row yet
        "revenue.structure_total@1",  # NA-9 / RF-48, in the NA doc, not in the registry draft rows
    }
)

_RULE_CONST = re.compile(r'^RULE\w*\s*=\s*"([a-z_]+\.[a-z_]+@\d+)"', re.M)


def code_rule_ids(root: Path) -> dict[str, str]:
    """rule id -> first file that defines it, from RULE* string constants under pipeline/src."""
    found: dict[str, str] = {}
    for path in sorted((root / "pipeline" / "src").rglob("*.py")):
        for m in _RULE_CONST.finditer(path.read_text()):
            found.setdefault(m.group(1), str(path.relative_to(root)))
    return found


def check_code_rule_ids(root: Path, rows: list[dict[str, str]]) -> list[Finding]:
    """Every flagged rule ID in code must be in the registry (AT-DE-04), and every registered
    rule family that has a flag in code must be spelled the same."""
    registered = {r["frozen_rule_id"].split(" ")[0] for r in rows}
    out = []
    for rid, where in code_rule_ids(root).items():
        if rid not in registered and rid not in PENDING_REGISTRY_IDS:
            out.append(Finding(rid, "rule_not_in_registry", f"defined in {where}"))
    return out


def run(root: Path | None = None) -> list[Finding]:
    root = root or repo_root()
    graph = load_graph(root / GRAPH_REL)
    rows = load_registry(root / REGISTRY_REL)
    findings = check_registry(graph, rows)
    findings += check_seed_drift(graph)
    findings += check_code_rule_ids(root, rows)
    return findings


def main() -> int:
    findings = run()
    for f in findings:
        print(f"FAIL {f.rule}: {f.code}: {f.message}")
    print(f"registry check: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
