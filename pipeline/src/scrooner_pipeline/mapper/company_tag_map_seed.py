"""Seeder for analytics.company_tag_map (migration 0122). Input: CSV or JSONL with the table's columns:
company_id or cik; taxonomy, tag, stmt, decision, canonical_concept_id | canonical_concept (name),
parent_concept_id | parent_concept (name), sign (or the older combine_sign; default 1), serve_note, components ('a;b' or 'a|b' in CSV, list in JSONL: member
CONCEPT names of a 'combined' line), reason_class, reason, era_from, era_to, evidence_adsh, evidence_report,
evidence_line, evidence_plabel, evidence_cal_parent, decided_by, rule_id. Extra columns (rank, ticker, ...) are ignored.

  * A row with an EMPTY decision is undecided: skipped (absent, not excluded) and counted per company.
  * rule_id empty -> the --default-rule-id (the library files carry none).
  * Unknown canonical_concept / parent_concept names are errors; unknown names inside a combined line's
    components are warnings (the mapper writes the blank by name), listed in the output.
Per company: validate every row against the table's own checks (and era overlap), then in ONE transaction replace
that company's rows. Dry run by default (reads only); --apply writes. One bad row blocks the whole file.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import psycopg

DEFAULT_RULE_ID = "company_tag_map.library@1"
RULE_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$")
STMTS = {"BS", "IS", "CF", "EQ", "CI", "UN", "CP"}
STATEMENT_STMTS = {
    "BS",
    "IS",
    "CF",
    "EQ",
    "CI",
}  # the statement tags (CP = cover/parenthetical, UN = unclassified)
DECISIONS = {
    "concept",
    "component",
    "combined",
    "excluded",
    "not_presented",
    "not_in_template",
}
TAGLESS = {"not_presented", "not_in_template"}
COLUMNS = (
    "company_id cik taxonomy tag stmt decision canonical_concept_id parent_concept_id sign serve_note components "
    "reason_class reason era_from era_to evidence_adsh evidence_report evidence_line evidence_plabel "
    "evidence_cal_parent decided_by rule_id"
).split()


def read_rows(path: Path) -> list[dict]:
    if path.suffix == ".jsonl":
        raw = [
            json.loads(line) for line in path.read_text().splitlines() if line.strip()
        ]
    else:
        with path.open(newline="") as fh:
            raw = list(csv.DictReader(fh))
    out = []
    for r in raw:
        r = {k: (v if v not in ("",) else None) for k, v in r.items()}
        comps = r.get("components")
        if isinstance(comps, str):
            r["components"] = [c.strip() for c in re.split(r"[;|]", comps) if c.strip()]
        out.append(r)
    return out


def _date(v):
    return v if v is None or isinstance(v, date) else date.fromisoformat(v)


def _int(v):
    return None if v is None else int(v)


def normalize(
    r: dict,
    company_by_cik: dict[str, int],
    concept_by_name: dict[str, int],
    default_rule_id: str = DEFAULT_RULE_ID,
    warnings: list[str] | None = None,
) -> dict:
    """One validated row as insert parameters; raises ValueError with the reason."""
    n = {c: r.get(c) for c in COLUMNS}
    if n["company_id"] is None:
        cik = str(n["cik"] or "").zfill(10)
        if cik not in company_by_cik:
            raise ValueError(f"unknown company (cik {n['cik']!r})")
        n["company_id"] = company_by_cik[cik]
        n["cik"] = cik
    n["company_id"] = int(n["company_id"])
    for side in ("canonical_concept", "parent_concept"):
        name = r.get(side)
        if n[f"{side}_id"] is None and name is not None:
            if name not in concept_by_name:
                raise ValueError(f"unknown {side} {name!r}")
            n[f"{side}_id"] = concept_by_name[name]
        n[f"{side}_id"] = _int(n[f"{side}_id"])
    raw_sign = r.get("sign") if r.get("sign") is not None else r.get("combine_sign")
    n["sign"] = 1 if raw_sign is None else int(raw_sign)
    for k in ("evidence_report", "evidence_line"):
        n[k] = _int(n[k])
    n["era_from"], n["era_to"] = _date(n["era_from"]), _date(n["era_to"])
    n["rule_id"] = n["rule_id"] or default_rule_id
    if n["decision"] in TAGLESS:
        if n["tag"] or n["taxonomy"]:
            raise ValueError(
                "not_presented / not_in_template rows carry no tag or taxonomy"
            )
        if n["canonical_concept_id"] is None or not (n["reason"] or "").strip():
            raise ValueError(
                "not_presented / not_in_template need canonical_concept_id and reason"
            )
    else:
        tag = (n["tag"] or "").strip()
        if not tag or ":" in tag:
            raise ValueError(f"tag must be the local name, got {n['tag']!r}")
        if not n["taxonomy"]:
            raise ValueError("taxonomy missing")
    if n["stmt"] not in STMTS:
        raise ValueError(f"stmt {n['stmt']!r} not in {sorted(STMTS)}")
    d = n["decision"]
    if d not in DECISIONS:
        raise ValueError(f"decision {d!r} not in {sorted(DECISIONS)}")
    if n["sign"] not in (-1, 1):
        raise ValueError("sign must be -1 or 1")
    if n["era_from"] is None:
        raise ValueError("era_from missing")
    if n["era_to"] is not None and n["era_from"] > n["era_to"]:
        raise ValueError("era_from > era_to")
    if not (n["decided_by"] or "").strip():
        raise ValueError("decided_by is required")
    if not RULE_ID_RE.match(n["rule_id"]):
        raise ValueError(f"rule_id {n['rule_id']!r} is not family.rule@N")
    if d == "concept" and n["canonical_concept_id"] is None:
        raise ValueError("concept needs canonical_concept_id")
    if d == "component" and n["parent_concept_id"] is None:
        raise ValueError("component needs parent_concept_id")
    if d == "combined":
        if not n["components"] or len(n["components"]) < 2:
            raise ValueError("combined needs components: the 2+ spanned concept names")
        for name in n["components"]:
            if name not in concept_by_name and warnings is not None:
                warnings.append(f"unknown concept name in combined components: {name}")
    if d == "excluded" and not (
        (n["reason_class"] or "").strip() or (n["reason"] or "").strip()
    ):
        raise ValueError("excluded needs reason_class or reason")
    return n


def check_overlaps(rows: list[dict]) -> list[str]:
    by_key = defaultdict(list)
    for r in rows:
        if r["tag"] is None:
            by_key[
                (r["company_id"], r["stmt"], "concept", r["canonical_concept_id"])
            ].append(r)
        else:
            by_key[(r["company_id"], r["taxonomy"], r["tag"], r["stmt"])].append(r)
    errors = []
    for key, group in by_key.items():
        group.sort(key=lambda r: r["era_from"])
        for a, b in zip(group, group[1:]):
            if a["era_to"] is None or a["era_to"] >= b["era_from"]:
                errors.append(
                    f"overlapping eras for {key}: {a['era_from']}..{a['era_to']} vs {b['era_from']}..{b['era_to']}"
                )
    return errors


INSERT = (
    "insert into analytics.company_tag_map (company_id, cik, taxonomy, tag, stmt, decision, canonical_concept_id, "
    "parent_concept_id, sign, components, serve_note, reason_class, reason, era_from, era_to, evidence_adsh, "
    "evidence_report, evidence_line, evidence_plabel, evidence_cal_parent, decided_by, rule_id) values "
    "(%(company_id)s, %(cik)s, %(taxonomy)s, %(tag)s, %(stmt)s, %(decision)s, %(canonical_concept_id)s, "
    "%(parent_concept_id)s, %(sign)s, %(components)s, %(serve_note)s, %(reason_class)s, %(reason)s, %(era_from)s, "
    "%(era_to)s, %(evidence_adsh)s, %(evidence_report)s, %(evidence_line)s, %(evidence_plabel)s, "
    "%(evidence_cal_parent)s, %(decided_by)s, %(rule_id)s)"
)


def completeness(decided: list[dict], undecided: list[dict]) -> dict:
    """Per company: statement tags (BS/IS/CF/EQ/CI lines) decided vs all, decisions by kind, undecided count."""
    out: dict = {}
    for r in decided:
        c = out.setdefault(
            r["cik"] or r["company_id"],
            {
                "statement_tags": 0,
                "decided": 0,
                "undecided": 0,
                "by_decision": Counter(),
            },
        )
        c["by_decision"][r["decision"]] += 1
        if r["stmt"] in STATEMENT_STMTS:
            c["statement_tags"] += 1
            c["decided"] += 1
    for r in undecided:
        c = out.setdefault(
            r["cik"] or r["company_id"],
            {
                "statement_tags": 0,
                "decided": 0,
                "undecided": 0,
                "by_decision": Counter(),
            },
        )
        if r["stmt"] in STATEMENT_STMTS:
            c["statement_tags"] += 1
        c["undecided"] += 1
    for c in out.values():
        c["by_decision"] = dict(c["by_decision"])
    return out


def seed(
    conn: psycopg.Connection,
    path: Path,
    apply: bool = False,
    default_rule_id: str = DEFAULT_RULE_ID,
) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company")
        company_by_cik = dict(cur.fetchall())
        cur.execute("select name, id from analytics.canonical_concept")
        concept_by_name = dict(cur.fetchall())
    by_company: dict[int, list[dict]] = defaultdict(list)
    undecided: list[dict] = []
    errors: list[str] = []
    warnings: list[str] = []
    for i, raw in enumerate(read_rows(path), start=1):
        if raw.get("decision") is None:  # undecided: absent, not excluded
            cik = str(raw.get("cik") or "").zfill(10)
            undecided.append(
                {
                    "cik": cik,
                    "company_id": raw.get("company_id"),
                    "stmt": raw.get("stmt"),
                }
            )
            continue
        try:
            n = normalize(
                raw, company_by_cik, concept_by_name, default_rule_id, warnings
            )
        except (ValueError, TypeError) as exc:
            errors.append(f"row {i}: {exc}")
            continue
        by_company[n["company_id"]].append(n)
    for rows in by_company.values():
        errors.extend(check_overlaps(rows))
    stats = {
        "companies": len(by_company),
        "rows": sum(map(len, by_company.values())),
        "undecided_skipped": len(undecided),
        "completeness": completeness(
            [r for rs in by_company.values() for r in rs], undecided
        ),
        "warnings": sorted(set(warnings)),
        "errors": errors,
        "applied": False,
    }
    if errors or not apply:
        return stats  # all-or-nothing on validation
    for company_id, rows in sorted(by_company.items()):
        with conn.transaction():
            conn.execute(
                "delete from analytics.company_tag_map where company_id = %s",
                (company_id,),
            )
            with conn.cursor() as cur:
                cur.executemany(INSERT, rows)
    stats["applied"] = True
    return stats
