"""Line -> canonical concept (design §3), per filing × statement, from fsn.concept_rule.

Rule 1 (std_tag): a line whose (prefix:tag) matches a rule of its statement and era.
Rule 3 (combined): a line whose tag is declared combined -> status 'combined' (never a single concept).
Rule 2 (calc_position) is applied only where a seed row declares a slot; the slot semantics come from the
lane detectors and are resolved by `position_match` (child_of / sibling_after / parent_of an anchor concept
already mapped in the same statement). Everything else is 'unmapped'. Writes fsn.line_map (replace per filing).
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from typing import Any, Callable, Protocol

import psycopg
from scrooner_pipeline.fsn_store.stmt_effective import effective_stmt_sql


class LineDecision(Protocol):
    """What a ported lane detector returns per line it overrides: (report, line, concept_id or None,
    status 'mapped'|'combined'|'unmapped'|'excluded', rule_id, evidence dict)."""


Detector = Callable[[psycopg.Connection, int, list[tuple]], list[tuple]]

PREFIX_OF_VERSION = {
    "us-gaap": "us-gaap",
    "srt": "srt",
    "dei": "dei",
    "ifrs-full": "ifrs",
}


def _prefix(version: str) -> str:
    base = version.split("/", 1)[0]
    return PREFIX_OF_VERSION.get(base, base)


def load_rules(conn: psycopg.Connection) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select r.id, c.name, r.canonical_concept_id, r.stmt, r.match_kind, r.tag, r.position, r.components,
                   r.priority, r.era_from, r.era_to, r.rule_id, r.tag_pattern
            from fsn.concept_rule r join analytics.canonical_concept c on c.id = r.canonical_concept_id
            order by r.priority
            """
        )
        rows = cur.fetchall()
    import re

    by_tag: dict[tuple[str, str], list[dict]] = defaultdict(list)
    positional: list[dict] = []
    demote: list[dict] = []
    for (
        rid,
        name,
        cid,
        stmt,
        kind,
        tag,
        pos,
        comps,
        prio,
        efrom,
        eto,
        rule_id,
        pattern,
    ) in rows:
        r = {
            "id": rid,
            "concept": name,
            "concept_id": cid,
            "stmt": stmt,
            "kind": kind,
            "tag": tag,
            "position": pos,
            "components": comps,
            "priority": prio,
            "era_from": efrom,
            "era_to": eto,
            "rule_id": rule_id,
            "pattern": re.compile(pattern) if pattern else None,
        }
        if kind == "calc_position":
            positional.append(r)
        elif kind == "demote":
            demote.append(r)
        else:
            by_tag[(stmt, tag)].append(r)
    return {"by_tag": by_tag, "positional": positional, "demote": demote}


def _in_era(r: dict, period: date | None) -> bool:
    if period is None:
        return r["era_from"] is None and r["era_to"] is None or True
    if r["era_from"] and period < r["era_from"]:
        return False
    if r["era_to"] and period >= r["era_to"]:
        return False
    return True


def _demoted(
    rules: dict[str, Any], stmt: str, key: str, concept: str, period: date | None
) -> dict | None:
    """A demote rule (tag or tag_pattern) for this concept on this statement: the std_tag match is withdrawn."""
    for r in rules.get("demote", []):
        if r["stmt"] != stmt or r["concept"] != concept or not _in_era(r, period):
            continue
        if (r["tag"] and r["tag"] == key) or (
            r["pattern"] and r["pattern"].search(key)
        ):
            return r
    return None


def map_filing(
    conn: psycopg.Connection,
    filing_id: int,
    rules: dict[str, Any],
    *,
    write: bool = True,
    detectors: list[Detector] | None = None,
) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("select period from fsn.filing where id = %s", (filing_id,))
        period = cur.fetchone()[0]
        cur.execute(
            f"""
            select l.report, l.line, {effective_stmt_sql("l")}, t.tag, t.version, t.custom, l.inpth
            from fsn.line l join fsn.tag t on t.id = l.tag_id
            where l.filing_id = %s and {effective_stmt_sql("l")} in ('BS', 'IS', 'CF')
            order by l.report, l.line
            """,
            (filing_id,),
        )
        lines = cur.fetchall()
        cur.execute(
            """
            select p.tag, p.version, c.tag, c.version
            from fsn.calc_arc a join fsn.tag p on p.id = a.parent_tag_id join fsn.tag c on c.id = a.child_tag_id
            where a.filing_id = %s
            """,
            (filing_id,),
        )
        arcs = cur.fetchall()
    parents_of: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    children_of: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for pt, pv, ct, cv in arcs:
        parents_of[(ct, cv)].add((pt, pv))
        children_of[(pt, pv)].add((ct, cv))
    out: list[tuple] = []
    mapped_concept_by_tag: dict[tuple[str, tuple[str, str]], str] = {}
    counts: dict[str, int] = defaultdict(int)
    pending_positional: list[tuple] = []
    for report, line, stmt, tag, version, custom, inpth in lines:
        if inpth:
            out.append(
                (
                    filing_id,
                    report,
                    line,
                    None,
                    "excluded",
                    None,
                    None,
                    {"why": "parenthetical"},
                )
            )
            counts["excluded"] += 1
            continue
        key = f"{_prefix(version)}:{tag}" if not custom else f"{version}:{tag}"
        cands = [r for r in rules["by_tag"].get((stmt, key), []) if _in_era(r, period)]
        d = _demoted(rules, stmt, key, cands[0]["concept"], period) if cands else None
        if d is not None:
            out.append(
                (
                    filing_id,
                    report,
                    line,
                    None,
                    "unmapped",
                    d["rule_id"],
                    None,
                    {"tag": key, "demoted_from": cands[0]["concept"]},
                )
            )
            counts["demoted"] += 1
            continue
        if cands:
            r = cands[0]
            status = "combined" if r["kind"] == "combined" else "mapped"
            out.append(
                (
                    filing_id,
                    report,
                    line,
                    r["concept_id"],
                    status,
                    r["rule_id"],
                    None,
                    {"match": r["kind"], "tag": key, "components": r["components"]},
                )
            )
            counts[status] += 1
            if status == "mapped":
                mapped_concept_by_tag[(stmt, (tag, version))] = r["concept"]
            continue
        if custom:
            pending_positional.append((report, line, stmt, tag, version))
            continue
        out.append(
            (filing_id, report, line, None, "unmapped", None, None, {"tag": key})
        )
        counts["unmapped"] += 1
    # rule 2: custom tags by calc position relative to an already-mapped anchor on the same statement
    for report, line, stmt, tag, version in pending_positional:
        hit = None
        for r in rules["positional"]:
            if r["stmt"] != stmt or not _in_era(r, period):
                continue
            pos = r["position"] or {}
            anchor = pos.get("anchor_concept")
            rel = pos.get("relation")
            if rel == "child_of":
                ok = any(
                    mapped_concept_by_tag.get((stmt, p)) == anchor
                    for p in parents_of.get((tag, version), ())
                )
            elif rel == "parent_of":
                ok = any(
                    mapped_concept_by_tag.get((stmt, c)) == anchor
                    for c in children_of.get((tag, version), ())
                )
            else:
                ok = False  # sibling_after needs the detector's slot order: left to the lane's seed semantics
            if ok:
                hit = r
                break
        if hit:
            out.append(
                (
                    filing_id,
                    report,
                    line,
                    hit["concept_id"],
                    "mapped",
                    hit["rule_id"],
                    None,
                    {
                        "match": "calc_position",
                        "tag": f"{version}:{tag}",
                        "slot": (hit["position"] or {}).get("slot"),
                    },
                )
            )
            counts["mapped"] += 1
        else:
            out.append(
                (
                    filing_id,
                    report,
                    line,
                    None,
                    "unmapped",
                    None,
                    None,
                    {"tag": f"{version}:{tag}", "custom": True},
                )
            )
            counts["unmapped"] += 1
    for det in detectors or []:
        overrides = {(o[1], o[2]): o for o in det(conn, filing_id, out)}
        if overrides:
            out = [overrides.get((r[1], r[2]), r) for r in out]
            counts["detector_overrides"] += len(overrides)
    if write:
        with conn.cursor() as cur:
            cur.execute("delete from fsn.line_map where filing_id = %s", (filing_id,))
            cur.executemany(
                "insert into fsn.line_map (filing_id, report, line, canonical_concept_id, status, rule_id, era, evidence) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
                [(*r[:7], json.dumps(r[7], default=str)) for r in out],
            )
    return dict(counts)


def map_company(
    conn: psycopg.Connection,
    company_id: int,
    rules: dict[str, Any] | None = None,
    detectors: list[Detector] | None = None,
) -> dict[str, int]:
    rules = rules or load_rules(conn)
    with conn.cursor() as cur:
        cur.execute(
            "select id from fsn.filing where company_id = %s or %s = any(select c.id from core.company c where c.cik = any(aciks))",
            (company_id, company_id),
        )
        ids = [r[0] for r in cur.fetchall()]
    tot: dict[str, int] = defaultdict(int)
    for fid in ids:
        for k, v in map_filing(conn, fid, rules, detectors=detectors).items():
            tot[k] += v
    tot["filings"] = len(ids)
    return dict(tot)
