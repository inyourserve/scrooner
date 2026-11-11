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

from typing import Any

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
# Verifier sample failed about 40% on note-sourced and template-OUT candidates (2026-11-11): not loaded, the
# points stay open (no value, no reason row). Matched against decided_by / rule_id / reason_class.
HELD_MARKERS = ("note_sourced", "note-sourced", "template_out", "template-out")


def held_by_verifier(raw: dict) -> bool:
    text = " ".join(
        str(raw.get(k) or "") for k in ("decided_by", "rule_id", "reason_class")
    ).lower()
    return any(m in text for m in HELD_MARKERS)


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
    n: dict[str, Any] = {c: r.get(c) for c in COLUMNS}
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

    def clash(a, b):
        return (a["era_to"] is None or a["era_to"] >= b["era_from"]) and (
            b["era_to"] is None or b["era_to"] >= a["era_from"]
        )

    for key, group in by_key.items():
        group.sort(key=lambda r: r["era_from"])
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                if a["tag"] is None:
                    same = True
                else:  # one tag may feed two concepts; an excluded detail row may coexist with a component row
                    ca = a["canonical_concept_id"] or a["parent_concept_id"]
                    cb = b["canonical_concept_id"] or b["parent_concept_id"]
                    same = ca == cb
                if same and clash(a, b):
                    errors.append(
                        f"overlapping eras for {key}: {a['era_from']}..{a['era_to']} vs {b['era_from']}..{b['era_to']}"
                    )
    # two 'concept' rows of one (company, stmt, concept) never overlap, even under different tags
    by_concept: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        if r["decision"] == "concept":
            by_concept[(r["company_id"], r["stmt"], r["canonical_concept_id"])].append(
                r
            )
    for key, group in by_concept.items():
        group.sort(key=lambda r: r["era_from"])
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                if clash(a, b):
                    errors.append(
                        f"two concept rows overlap for (company, stmt, concept) {key}: "
                        f"{a['tag']} {a['era_from']}..{a['era_to']} vs {b['tag']} {b['era_from']}..{b['era_to']}"
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
    held_verifier = 0
    errors: list[str] = []
    warnings: list[str] = []
    for i, raw in enumerate(read_rows(path), start=1):
        if held_by_verifier(raw):
            held_verifier += 1
            undecided.append(
                {
                    "cik": str(raw.get("cik") or "").zfill(10),
                    "company_id": raw.get("company_id"),
                    "stmt": raw.get("stmt"),
                }
            )
            continue
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
    stats: dict[str, Any] = {
        "companies": len(by_company),
        "rows": sum(map(len, by_company.values())),
        "undecided_skipped": len(undecided) - held_verifier,
        "held_verifier_sample_failed": held_verifier,
        "completeness": completeness(
            [r for rs in by_company.values() for r in rs], undecided
        ),
        "warnings": sorted(set(warnings)),
        "errors": errors,
        "applied": False,
    }
    stats["winner_tag_gaps"] = winner_tag_gaps(
        conn,
        [r for rs in by_company.values() for r in rs],
        {i: n for n, i in concept_by_name.items()},
    )
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


def winner_tag_gaps(
    conn: psycopg.Connection, rows: list[dict], concept_names: dict[int, str]
) -> dict:
    """Read-only count of winner-tag gaps per (company, concept): periods inside a concept row's era where an
    excluded alternate tag of the same concept (reason_class alternate_tag_overlapping) has an authoritative
    core.fact but the winner tag has none. The mapper blanks these ("no fact under <tag> for this period")."""
    by_company: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        by_company[r["company_id"]].append(r)
    out: dict = {}
    for company_id, rs in by_company.items():
        wins = [r for r in rs if r["decision"] == "concept"]
        alts = [
            r
            for r in rs
            if r["decision"] == "excluded"
            and r["reason_class"] == "alternate_tag_overlapping"
        ]
        tags = sorted({r["tag"] for r in wins + alts})
        if not alts or not tags:
            continue
        with conn.cursor() as cur:
            cur.execute(
                """select c.tag, p.end_date from core.fact f join core.concept c on c.id = f.concept_id
                   join core.period p on p.id = f.period_id
                   where f.company_id = %s and f.is_authoritative and c.tag = any(%s)""",
                (company_id, tags),
            )
            ends: dict[str, set] = defaultdict(set)
            for tag, end in cur.fetchall():
                ends[tag].add(end)
        for w in wins:
            cname = concept_names.get(w["canonical_concept_id"], "")
            for a in alts:
                if a["stmt"] != w["stmt"] or a["tag"] == w["tag"]:
                    continue
                if a["canonical_concept_id"] is not None:
                    if a["canonical_concept_id"] != w["canonical_concept_id"]:
                        continue
                elif f"same concept {cname} " not in (a["reason"] or ""):
                    continue
                gap = {
                    e
                    for e in ends.get(a["tag"], set())
                    if w["era_from"] <= e <= (w["era_to"] or date.max)
                    and a["era_from"] <= e <= (a["era_to"] or date.max)
                    and e not in ends.get(w["tag"], set())
                }
                if gap:
                    out[(company_id, cname, w["tag"], a["tag"])] = len(gap)
    return out
