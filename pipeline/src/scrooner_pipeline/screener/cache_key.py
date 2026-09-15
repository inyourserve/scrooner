"""Dataset-versioned cache-key canonicalization (doc/faster-loading/
fast.md item 3, doc/adr/0001-screener-redis-cache-and-boolean-logic.md).
Lives in `pipeline`, not `apps/backend`, because it's a property of the
ScreenQuery shape itself (one canonical representation per query),
exactly the kind of thing that would drift into two disagreeing
implementations if duplicated -- apps/backend imports scrooner_pipeline
directly already (doc 16's boundary), so there's no reason for a second
copy.

Critical detail fast.md itself calls out: `A OR B` and `B OR A` must hash
identically, or the cache silently stops matching them and the hit rate
quietly collapses. Fixed here by sorting every AND/OR group's children
(by their own canonical JSON) before hashing -- NOT before compiling to
SQL in query.py, where child order is irrelevant to begin with. `not`
groups have exactly one child (schema.py enforces this), so there's
nothing to sort there.
"""

import hashlib
import json
from decimal import Decimal

from scrooner_pipeline.screener.schema import CategoricalPredicate, MetricPredicate, PredicateGroup, ScreenQuery


def _default(o):
    if isinstance(o, Decimal):
        return str(o)
    return str(o)


def _dump(value) -> str:
    return json.dumps(value, sort_keys=True, default=_default)


def _canon_predicate(p) -> dict:
    if isinstance(p, PredicateGroup):
        return _canon_group(p)
    if isinstance(p, MetricPredicate):
        return {
            "type": "metric",
            "metric_name": p.metric_name,
            "operator": p.operator,
            "value": p.value,
            "value_range": p.value_range,
            "n": p.n,
        }
    if isinstance(p, CategoricalPredicate):
        return {"type": "categorical", "field": p.field, "operator": p.operator, "value": p.value}
    raise TypeError(f"unknown predicate node: {p!r}")


def _canon_group(node: PredicateGroup) -> dict:
    children = [_canon_predicate(c) for c in node.predicates]
    if node.op in ("and", "or"):
        children = sorted(children, key=_dump)
    return {"type": "group", "op": node.op, "predicates": children}


def canonicalize(query: ScreenQuery) -> dict:
    """A JSON-stable representation where semantically-equivalent queries
    (reordered AND/OR children, or the same filters expressed via the
    flat metric_predicates/categorical_predicates lists) always produce
    identical output."""
    flat = [_canon_predicate(p) for p in query.metric_predicates] + [
        _canon_predicate(p) for p in query.categorical_predicates
    ]
    return {
        "flat_and": sorted(flat, key=_dump),
        "where": _canon_group(query.where) if query.where is not None else None,
        "include_inactive": query.include_inactive,
        "sort_by": query.sort_by,
        "sort_desc": query.sort_desc,
        "limit": query.limit,
        # Display metrics change the stored result payload even though they
        # do not change membership. They therefore belong in cache identity;
        # omitting them reused legacy one-column result rows for expanded
        # comparison tables.
        "display_metrics": sorted(set(query.display_metrics)),
    }


def compute_query_hash(query: ScreenQuery, dataset_version: int) -> str:
    payload = {"query": canonicalize(query), "dataset_version": dataset_version}
    blob = _dump(payload).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
