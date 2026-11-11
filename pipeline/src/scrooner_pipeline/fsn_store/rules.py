"""concept_rule seeds (FORMATS-v1 §2) -> fsn.concept_rule. Validate everything, refuse the file on the first error."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.common.cell_contract import parse_rule_id

STMTS = ("BS", "IS", "CF")
KINDS = ("std_tag", "calc_position", "combined", "demote")
RELATIONS = ("child_of", "sibling_after", "parent_of")


def validate(rows: list[dict[str, Any]], concept_ids: dict[str, int]) -> list[str]:
    errors = []
    seen: set[tuple] = set()
    for i, r in enumerate(rows, 1):
        c = r.get("canonical_concept")
        if c not in concept_ids:
            errors.append(f"line {i}: unknown canonical_concept {c!r}")
        if r.get("stmt") not in STMTS:
            errors.append(f"line {i}: stmt must be one of {STMTS}")
        k = r.get("match_kind")
        if k not in KINDS:
            errors.append(f"line {i}: match_kind must be one of {KINDS}")
        tag = r.get("tag")
        if k in ("std_tag", "combined") and not (isinstance(tag, str) and ":" in tag):
            errors.append(f"line {i}: {k} needs tag as prefix:tag")
        if k == "demote" and not (tag or r.get("tag_pattern")):
            errors.append(f"line {i}: demote needs tag or tag_pattern")
        if r.get("tag_pattern"):
            import re as _re

            try:
                _re.compile(r["tag_pattern"])
            except _re.error:
                errors.append(f"line {i}: tag_pattern is not a valid regex")
        if k == "calc_position":
            pos = r.get("position") or {}
            if (
                not pos.get("slot")
                or not pos.get("anchor_concept")
                or pos.get("relation") not in RELATIONS
                or pos.get("sign") not in (1, -1)
            ):
                errors.append(
                    f"line {i}: calc_position needs position {{slot, anchor_concept, relation, sign}}"
                )
        if k == "combined":
            comps = r.get("components")
            if not comps or any(x not in concept_ids for x in comps):
                errors.append(
                    f"line {i}: combined needs components that are canonical concepts"
                )
        if not isinstance(r.get("priority"), int):
            errors.append(f"line {i}: priority must be an integer")
        for f in ("era_from", "era_to"):
            if r.get(f):
                try:
                    date.fromisoformat(r[f])
                except ValueError:
                    errors.append(f"line {i}: {f} is not an ISO date")
        try:
            parse_rule_id(r.get("rule_id") or "")
        except ValueError:
            errors.append(f"line {i}: rule_id must be family.rule@N")
        if not r.get("source_commit") or not r.get("evidence"):
            errors.append(f"line {i}: source_commit and evidence are required")
        key = (c, r.get("stmt"), k, tag or "", r.get("priority"))
        if key in seen:
            errors.append(
                f"line {i}: duplicate (concept, stmt, match_kind, tag, priority)"
            )
        seen.add(key)
    return errors


def seed(conn: psycopg.Connection, path: Path, *, apply: bool) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    with conn.cursor() as cur:
        cur.execute("select name, id from analytics.canonical_concept")
        concept_ids = dict(cur.fetchall())
    errors = validate(rows, concept_ids)
    if errors:
        return {"rows": len(rows), "errors": errors[:50], "written": 0}
    if not apply:
        return {
            "rows": len(rows),
            "errors": [],
            "written": 0,
            "rule_ids": sorted({r["rule_id"] for r in rows}),
        }
    rule_ids = sorted({r["rule_id"] for r in rows})
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(
                "delete from fsn.concept_rule where rule_id = any(%s)", (rule_ids,)
            )
            cur.executemany(
                """
                insert into fsn.concept_rule (canonical_concept_id, stmt, match_kind, tag, tag_pattern, position, components,
                                              priority, era_from, era_to, rule_id, source_commit, evidence)
                values (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        concept_ids[r["canonical_concept"]],
                        r["stmt"],
                        r["match_kind"],
                        r.get("tag"),
                        r.get("tag_pattern"),
                        json.dumps(r["position"]) if r.get("position") else None,
                        r.get("components"),
                        r["priority"],
                        r.get("era_from"),
                        r.get("era_to"),
                        r["rule_id"],
                        r["source_commit"],
                        r["evidence"],
                    )
                    for r in rows
                ],
            )
    return {"rows": len(rows), "errors": [], "written": len(rows), "rule_ids": rule_ids}


def retired_ids(path: Path) -> list[str]:
    """Rule ids listed in a retired file (one per line, '#' starts a comment)."""
    if not path.exists():
        return []
    return [
        x.split("#", 1)[0].strip()
        for x in path.read_text().splitlines()
        if x.split("#", 1)[0].strip()
    ]


def retire(conn: psycopg.Connection, path: Path, *, apply: bool) -> dict[str, Any]:
    """Delete withdrawn seed rows (concept_rules/_retired.txt) from fsn.concept_rule. seed() replaces only the rule ids
    its file carries, so without this a database seeded earlier keeps a removed rule and keeps mapping by it."""
    ids = retired_ids(path)
    if not ids:
        return {"retired": [], "deleted": 0}
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from fsn.concept_rule where rule_id = any(%s)", (ids,)
        )
        present = cur.fetchone()[0]
    if not apply:
        return {"retired": ids, "deleted": 0, "present": present}
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("delete from fsn.concept_rule where rule_id = any(%s)", (ids,))
            deleted = cur.rowcount
    return {"retired": ids, "deleted": deleted}
