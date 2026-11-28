"""One loader for the rule stores (PIPELINE.md section 7, step M2). Stdlib only, no DB, read-only.

Today three stores hold rules: the predictor's `rules/*.csv` (kind/when/then JSON rows), the resolver's
`line_map/rules/*.csv` (roles, polarity, ...) and the proposal inbox `rules/inbox/`. This module reads them
into ONE normalised record, `Rule`, and exposes indexed views that the predictor and the resolver can read
instead of opening their own files. It changes no rule content and no output: the parity test
(`library/test_rule_store.py`) proves each view equals what the predictor (`exam/tools/predict.load_kb`) and the
resolver (`resolve_all.ROLES`, `POLARITY`) read directly.

Unified schema (the target store, section 7 M2): rule_id, class, element, action, scope, version, evidence,
test_id, status. `store` and `source` say where the row lives today; once the stores merge they go away.
"""

from __future__ import annotations

import csv
import glob
import json
import os
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = HERE
RESOLVER_RULES_DIR = os.path.normpath(os.path.join(HERE, "..", "line_map", "rules"))

PREDICTOR, RESOLVER, INBOX = "predictor", "resolver", "inbox"


@dataclass(frozen=True)
class Rule:
    rule_id: str
    cls: str  # predictor kind (tag, override, ...) or resolver class (role_alt, role_parent, polarity)
    element: str  # XBRL element, or the data point for data-point-level rules
    action: str  # map | component | combined | excluded | sign:+ ... (empty for non-decision rules)
    scope: str  # all | <TICKER> | <statement>:<data_point>
    version: str
    evidence: str
    test_id: str  # empty until the owning test is named (target: required)
    status: str  # active | proposed | retired
    store: str
    source: str
    data: dict = field(default_factory=dict, compare=False, hash=False)


def _csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def load_predictor(rules_dir: str | None = None) -> list[Rule]:
    """Every `rules/*.csv` row, same file order and JSON parse as predict.load_kb."""
    out: list[Rule] = []
    for f in sorted(glob.glob(os.path.join(rules_dir or RULES_DIR, "*.csv"))):
        for r in _csv(f):
            w, t = json.loads(r["when"] or "{}"), json.loads(r["then"] or "{}")
            scope = r["scope"]
            out.append(
                Rule(
                    r["rule_id"], r["kind"], w.get("tag") or w.get("label_regex") or r["data_point"],
                    t.get("decision") or t.get("concept") or t.get("data_point") or "", scope,
                    r["version"], r["evidence"], "", "active", PREDICTOR, os.path.basename(f),
                    {"when": w, "then": t, "data_point": r["data_point"]},
                )
            )  # fmt: skip
    return out


def load_inbox(rules_dir: str | None = None) -> list[Rule]:
    """Open proposals (`rules/inbox/*.csv` rows with a rule_id; STATUS.csv and TEMPLATE.csv are bookkeeping)."""
    out: list[Rule] = []
    d = os.path.join(rules_dir or RULES_DIR, "inbox")
    for f in sorted(glob.glob(os.path.join(d, "*.csv"))):
        if os.path.basename(f) in ("STATUS.csv", "TEMPLATE.csv"):
            continue
        for r in _csv(f):
            if not r.get("rule_id"):
                continue
            out.append(
                Rule(
                    r["rule_id"], r.get("kind", ""), r.get("data_point", ""), "", r.get("scope", ""),
                    r.get("version", ""), r.get("evidence", ""), "", "proposed", INBOX, os.path.basename(f), dict(r),
                )
            )  # fmt: skip
    return out


def load_resolver(resolver_dir: str | None = None) -> list[Rule]:
    """roles.csv (one rule per alternative element, one for the parent, one for the fallback) and polarity.csv."""
    d = resolver_dir or RESOLVER_RULES_DIR
    out: list[Rule] = []
    for r in _csv(os.path.join(d, "roles.csv")):
        dp, stmt = r["data_point"], r["stmt"]
        scope = f"{stmt}:{dp}"
        ev = r.get("ruling", "")
        for cls, els in (
            ("role_alt", [x for x in r["alternatives"].split("|") if x]),
            ("role_parent", [x for x in [r["parent"]] if x]),
            ("role_fallback", [x for x in [r["fallback"]] if x and " " not in x]),
        ):
            for e in els:
                out.append(
                    Rule(f"res.roles.{dp}.{cls}.{e}", cls, e, "map", scope, "", ev, "", "active", RESOLVER, "roles.csv",
                         {"data_point": dp, "stmt": stmt})
                )  # fmt: skip
    for r in _csv(os.path.join(d, "polarity.csv")):
        out.append(
            Rule(f"res.polarity.{r['data_point']}", "polarity", r["data_point"], "sign:" + r["sign"], "all", "", r["why"],
                 "", "active", RESOLVER, "polarity.csv", dict(r))
        )  # fmt: skip
    return out


def load_all(
    rules_dir: str | None = None, resolver_dir: str | None = None
) -> list[Rule]:
    return (
        load_predictor(rules_dir) + load_resolver(resolver_dir) + load_inbox(rules_dir)
    )


# ---- indexed views: what the predictor and the resolver read ------------------------------------------------------


def tag_decisions(rules: list[Rule]) -> dict[tuple[str, str], dict]:
    """(stmt, element) -> then-dict plus `rid`: the predictor's K['lib']."""
    return {
        (r.data["when"]["stmt"], r.data["when"]["tag"]): dict(
            r.data["then"], rid=r.rule_id
        )
        for r in rules
        if r.store == PREDICTOR and r.cls == "tag"
    }


def overrides(rules: list[Rule]) -> dict[tuple[str, str], dict]:
    """(cik, element) -> concept, rid, decision: the predictor's K['ov']."""
    return {
        (r.data["when"]["cik"], r.data["when"]["tag"]): dict(
            concept=r.data["then"]["concept"],
            rid=r.rule_id,
            decision=r.data["then"].get("decision", "map"),
        )
        for r in rules
        if r.store == PREDICTOR and r.cls == "override"
    }


def role_rows(rules: list[Rule]) -> dict[str, dict[str, set[str]]]:
    """data_point -> {'alt': {...}, 'parent': {...}, 'fallback': {...}}: the resolver's roles.csv, element level."""
    out: dict[str, dict[str, set[str]]] = {}
    for r in rules:
        if r.store == RESOLVER and r.cls.startswith("role_"):
            out.setdefault(r.data["data_point"], {}).setdefault(r.cls[5:], set()).add(
                r.element
            )
    return out


def polarity(rules: list[Rule]) -> dict[str, dict]:
    return {r.data["data_point"]: r.data for r in rules if r.cls == "polarity"}


def _base(concept: str) -> str:
    c = {"revenue_sanity_resolved": "revenue"}.get(
        (concept or "").strip(), (concept or "").strip()
    )
    return c[:-9] if c.endswith("_resolved") else c


def conflicts(rules: list[Rule]) -> list[tuple[str, str, str, str, str]]:
    """Overlap on (statement, element) between the predictor's tag rules and the resolver's alternative elements.
    Returns (kind, stmt, element, resolver_data_points, predictor_rule_id):
      HARD = predictor maps the element to a concept the resolver does not list it under;
      SOFT = predictor decides component, combined or excluded for an element the resolver takes directly.
    Sorted, so it can be compared with the reviewed baseline."""
    lib = tag_decisions(rules)
    dps: dict[tuple[str, str], set[str]] = {}
    for r in rules:
        if r.store == RESOLVER and r.cls == "role_alt":
            dps.setdefault((r.data["stmt"], r.element), set()).add(r.data["data_point"])
    out = []
    for (stmt, el), mine in dps.items():
        t = lib.get((stmt, el))
        if not t:
            continue
        if t.get("decision") == "map":
            if _base(t.get("concept", "")) not in mine:
                out.append(("HARD", stmt, el, "|".join(sorted(mine)), t["rid"]))
        else:
            out.append(("SOFT", stmt, el, "|".join(sorted(mine)), t["rid"]))
    return sorted(out)
