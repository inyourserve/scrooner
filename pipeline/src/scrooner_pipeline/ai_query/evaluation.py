"""Score an NL interpreter against the AI query eval set (SYSTEMS.md #18).

The eval set is `pipeline/tests/fixtures/ai_query/eval_set.jsonl`: one plain-
English ask per line with the expected `ScreenQuery`, or `null` when the only
correct answer is no executable query (an opinion, a stock pick, an ambiguous
or contradictory ask). Expected values are written from the meaning of the
ask, never copied from an interpreter's output, so a miss is a real miss.

A hit is an exact match after canonical ordering: AND/OR children are
compared as sorted sets (their order carries no meaning) and a flat
metric/categorical list is the same filter as a `where` AND group holding the
same leaves. Everything else (operator, Decimal value, n, include_missing,
sort, limit) must be equal.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from scrooner_pipeline.ai_query.interpreter import InterpretationResult
from scrooner_pipeline.screener.schema import (
    RANKED_OPERATORS,
    CategoricalPredicate,
    MetricPredicate,
    PredicateGroup,
    ScreenQuery,
)

EVAL_SET_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "ai_query"
    / "eval_set.jsonl"
)
BASELINE_PATH = EVAL_SET_PATH.with_name("baseline.json")


@dataclass(frozen=True)
class EvalCase:
    id: str
    category: str
    ask: str
    expected: ScreenQuery | None
    note: str | None = None


@dataclass
class EvalReport:
    total: int = 0
    hits: int = 0
    by_category: dict[str, list[int]] = field(default_factory=dict)  # [hits, total]
    failure_classes: Counter = field(default_factory=Counter)
    failures: list[tuple[EvalCase, str, str]] = field(default_factory=list)

    @property
    def hit_rate(self) -> float:
        return self.hits / self.total if self.total else 0.0

    def summary(self) -> str:
        lines = [f"hit rate {self.hits}/{self.total} = {self.hit_rate:.1%}"]
        for cat, (h, t) in sorted(self.by_category.items()):
            lines.append(f"  {cat:20s} {h:4d}/{t:<4d}")
        lines.append("failure classes:")
        for cls, n in self.failure_classes.most_common():
            lines.append(f"  {cls:40s} {n}")
        return "\n".join(lines)


def load_eval_set(path: Path = EVAL_SET_PATH) -> list[EvalCase]:
    cases = []
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            expected = row["expected"]
            cases.append(
                EvalCase(
                    id=row["id"],
                    category=row["category"],
                    ask=row["ask"],
                    expected=None
                    if expected is None
                    else ScreenQuery.model_validate(expected),
                    note=row.get("note"),
                )
            )
    return cases


def _num(value: object) -> object:
    # 2.5 trillion parses to Decimal("2500000000000.0"); it is the same value
    # as Decimal("2500000000000"), so compare numerically, not by spelling.
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, (tuple, list)):
        return [_num(v) for v in value]
    return value


def _leaf_key(node: MetricPredicate | CategoricalPredicate) -> str:
    data = {k: _num(v) for k, v in node.model_dump().items()}
    return json.dumps(data, sort_keys=True)


def _canon_node(node) -> object:
    if isinstance(node, (MetricPredicate, CategoricalPredicate)):
        return _leaf_key(node)
    assert isinstance(node, PredicateGroup)
    if node.op == "not":
        return ("not", _canon_node(node.predicates[0]))
    children = []
    for child in node.predicates:
        c = _canon_node(child)
        # (A and (B and C)) is (A and B and C)
        if isinstance(c, tuple) and c[0] == node.op:
            children.extend(c[1])
        else:
            children.append(c)
    if len(children) == 1:
        return children[0]
    return (node.op, tuple(sorted(children, key=repr)))


def canonical(query: ScreenQuery) -> tuple:
    ranked = sorted(
        _leaf_key(p) for p in query.metric_predicates if p.operator in RANKED_OPERATORS
    )
    if query.where is not None:
        filt = _canon_node(query.where)
    else:
        leaves = [
            p for p in query.metric_predicates if p.operator not in RANKED_OPERATORS
        ] + list(query.categorical_predicates)
        filt = (
            _canon_node(PredicateGroup(op="and", predicates=leaves)) if leaves else None
        )
    return (
        filt,
        tuple(ranked),
        query.include_inactive,
        query.sort_by,
        query.sort_desc if query.sort_by else None,
        query.limit,
        tuple(query.display_metrics),
    )


def _failure_class(case: EvalCase, result: InterpretationResult) -> str:
    if case.expected is None:
        return "emitted_query_where_none_expected"
    if result.query is not None:
        return "wrong_query"
    if result.contradictions:
        return "no_query:false_contradiction"
    if result.ambiguous and not result.unrecognized:
        # A one-candidate "ambiguity" is a near-miss suggestion (difflib).
        if all(len(a.candidates) == 1 for a in result.ambiguous):
            return "no_query:near_miss_suggestion"
        return "no_query:ambiguous"
    if result.recognized_query is not None:
        return "no_query:partly_unrecognized"
    return "no_query:unrecognized"


def score(
    interpret: Callable[[str], InterpretationResult],
    cases: list[EvalCase] | None = None,
) -> EvalReport:
    cases = load_eval_set() if cases is None else cases
    report = EvalReport()
    for case in cases:
        result = interpret(case.ask)
        if case.expected is None:
            hit = result.query is None
        else:
            hit = result.query is not None and canonical(result.query) == canonical(
                case.expected
            )
        report.total += 1
        bucket = report.by_category.setdefault(case.category, [0, 0])
        bucket[1] += 1
        if hit:
            report.hits += 1
            bucket[0] += 1
            continue
        cls = _failure_class(case, result)
        report.failure_classes[f"{case.category}/{cls}"] += 1
        got = result.query.model_dump_json() if result.query else result.explanation
        report.failures.append((case, cls, got))
    return report
