"""Equivalence of an EDGAR-built filing (fsn_store.xbrl_fsn) with the same filing in a SEC FSN set.

Compared on the shard view, the rows fsn_store.shard keeps and fsn_store.load stores: every
non-dimensional num row and every dimensional num row of a tag on a statement; the pre rows of the
statements and the cover (stmt in STATEMENT_STMTS); every cal arc; the ren rows; the sub columns the
loader reads.

Pass criteria (design note 2026-11-09, "Equivalence test"):
- num: the same keys (tag, version, ddate, qtrs, uom, dimh, iprx, coreg) and, per key, the same
  value and dcml (durp/datp within 1e-5; footnote is reported, not gated: SEC hangs a footnote on
  one of two identical duplicate facts in an order the instance does not carry).
- pre items: per report, the same ordered sequence of line items that carry a fact (stmt, inpth,
  tag, version, prole, plabel, negating). Structural rows (abstracts, axes, domains, members)
  are reported as a residual count, not gated.
- cal: the same arcs (parent, child, weight) in the same groups; SEC's group and arc numbering
  follows no order the linkbase carries, so numbers are not compared.
- sub: cik, form, period, fy, fp, fye, filed, accepted (to the minute, as SEC rounds it), aciks.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from scrooner_pipeline.fsn_store.xbrl_fsn import shard_filter

NUM_KEY = ("tag", "version", "ddate", "qtrs", "uom", "dimh", "iprx", "coreg")
SUB_COLS = ("cik", "form", "period", "fy", "fp", "fye", "filed", "accepted", "aciks")
PRE_COLS = ("stmt", "inpth", "tag", "version", "prole", "plabel", "negating")


def shard_view(
    tables: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    return shard_filter(tables)


def _num_key(r: dict[str, str]) -> tuple[str, ...]:
    return tuple(r.get(c, "") for c in NUM_KEY)


def compare_num(exp: list[dict[str, str]], got: list[dict[str, str]]) -> dict[str, Any]:
    e = {_num_key(r): r for r in exp}
    g = {_num_key(r): r for r in got}
    missing = sorted(k for k in e if k not in g)
    extra = sorted(k for k in g if k not in e)
    diff: Counter[str] = Counter()
    examples: dict[str, Any] = {}
    for k in e.keys() & g.keys():
        for c in ("value", "dcml", "durp", "datp", "footnote", "dimn"):
            a, b = e[k].get(c, ""), g[k].get(c, "")
            same = (
                abs(float(a or 0) - float(b or 0)) < 1e-5
                if c in ("durp", "datp")
                else a == b
            )
            if not same:
                diff[c] += 1
                examples.setdefault(c, [list(k), a, b])
    gated = (
        len(missing) + len(extra) + sum(n for c, n in diff.items() if c != "footnote")
    )
    return {
        "fsn": len(e),
        "ours": len(g),
        "missing": len(missing),
        "extra": len(extra),
        "column_diffs": dict(diff),
        "examples": {
            "missing": [list(k) for k in missing[:3]],
            "extra": [list(k) for k in extra[:3]],
            **examples,
        },
        "pass": gated == 0,
    }


def _lines(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by: dict[str, list[dict[str, str]]] = {}
    for r in sorted(rows, key=lambda r: (int(r["report"]), int(r["line"]))):
        by.setdefault(r["report"], []).append(r)
    return by


def compare_pre(
    exp: list[dict[str, str]],
    got: list[dict[str, str]],
    fact_tags: set[tuple[str, str]],
) -> dict[str, Any]:
    e, g = _lines(exp), _lines(got)
    exact = item_diffs = structural = 0
    examples = []
    for rep in sorted(e.keys() | g.keys(), key=int):
        a = [tuple(r[c] for c in PRE_COLS) for r in e.get(rep, [])]
        b = [tuple(r[c] for c in PRE_COLS) for r in g.get(rep, [])]
        if a == b:
            exact += 1
            continue
        ai = [x for x in a if (x[2], x[3]) in fact_tags]
        bi = [x for x in b if (x[2], x[3]) in fact_tags]
        if ai != bi:
            item_diffs += 1
            examples.append({"report": rep, "fsn": ai[:40], "ours": bi[:40]})
        structural += abs(len(a) - len(b)) + sum(
            1 for x in set(a) ^ set(b) if (x[2], x[3]) not in fact_tags
        )
    return {
        "reports": len(e.keys() | g.keys()),
        "reports_exact": exact,
        "reports_item_diffs": item_diffs,
        "structural_row_diffs": structural,
        "fsn_rows": len(exp),
        "ours_rows": len(got),
        "examples": examples[:2],
        "pass_items": item_diffs == 0,
        "pass_exact": exact == len(e.keys() | g.keys()),
    }


def compare_cal(exp: list[dict[str, str]], got: list[dict[str, str]]) -> dict[str, Any]:
    def groups(rows: list[dict[str, str]]) -> Counter:
        by: dict[str, list[tuple[str, ...]]] = {}
        for r in rows:
            by.setdefault(r["grp"], []).append(
                (r["ptag"], r["pversion"], r["ctag"], r["cversion"], r["negative"])
            )
        return Counter(tuple(sorted(v)) for v in by.values())

    def norm(rows: list[dict[str, str]]) -> list[dict[str, str]]:
        # SEC writes negative as the weight (+1 / -1); older sets wrote a boolean 0/1
        return [
            {**r, "negative": "-1" if r["negative"] in ("-1", "-1.0") else "1"}
            for r in rows
        ]

    a, b = groups(norm(exp)), groups(norm(got))
    return {
        "fsn_arcs": len(exp),
        "ours_arcs": len(got),
        "fsn_groups": sum(a.values()),
        "ours_groups": sum(b.values()),
        "groups_only_fsn": sum((a - b).values()),
        "groups_only_ours": sum((b - a).values()),
        "pass": a == b,
    }


def compare(
    expected: dict[str, list[dict[str, str]]], got: dict[str, list[dict[str, str]]]
) -> dict[str, Any]:
    """One filing: expected = its rows in the SEC FSN set, got = xbrl_fsn.convert output."""
    e, g = shard_view(expected), shard_view(got)
    fact_tags = {(r["tag"], r["version"]) for r in e["num"]} | {
        (r["tag"], r["version"]) for r in g["num"]
    }
    sub_e, sub_g = (expected.get("sub") or [{}])[0], (got.get("sub") or [{}])[0]
    sub_diff = {
        c: [sub_e.get(c, ""), sub_g.get(c, "")]
        for c in SUB_COLS
        if sub_e.get(c, "") != sub_g.get(c, "")
    }
    out: dict[str, Any] = {
        "num": compare_num(e["num"], g["num"]),
        "pre": compare_pre(e["pre"], g["pre"], fact_tags),
        "cal": compare_cal(expected.get("cal", []), got.get("cal", [])),
        "sub": {"diff": sub_diff, "pass": not sub_diff},
    }
    out["pass"] = all(
        (
            out["num"]["pass"],
            out["pre"]["pass_items"],
            out["cal"]["pass"],
            out["sub"]["pass"],
        )
    )
    return out
