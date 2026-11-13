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

only_rule (--only-rule family.rule@N): load only the file's rows of that rule and replace only that rule's rows, so the
rows other writers own (docmap@1, era_extend@1, a rewritten map) stay. A tagless status row of the rule is dropped (listed
in 'superseded_by_live') where a live row of another rule already decides the same concept in an overlapping era: a
served value or an earlier decision is never covered by a second reason. Overlaps are checked against those live rows.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
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
    """A note-sourced / template-OUT CANDIDATE row that would serve a value (the Verifier sample failed for those).
    Status rows (not_presented / not_in_template, tagless) never serve a value, so they always load: they are the
    cell's reason, e.g. reason_class held_read_verified_pass_of_note_sourced_candidate."""
    if str(raw.get("decision") or "").strip() in ("not_presented", "not_in_template"):
        return False
    text = " ".join(
        str(raw.get(k) or "") for k in ("decided_by", "rule_id", "reason_class")
    ).lower()
    return any(m in text for m in HELD_MARKERS)


COLUMNS = (
    "company_id cik taxonomy tag stmt decision canonical_concept_id parent_concept_id sign scale serve_note components "
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


# Instants are never derived (doc 02): a component sum is allowed for DURATION concepts only; the one instant
# exception is total debt (founder definition, doc 02 2026-11-04 item 5).
# Second exception (Dhairya ruling (c) 2026-11-13, rule per_share.shares_outstanding.multi_class_sum): the BS/EQ face
# prints the share count only per class member (>= 2 members); the data point is the sum of the class members at the date.
INSTANT_SUM_ALLOWED = {
    "total_debt",
    "total_debt_resolved",
    "shares_outstanding",
    "shares_outstanding_resolved",
}


def instant_sum_refused(parent_name: str | None, statement: str | None) -> bool:
    return statement == "balance_sheet" and (parent_name or "").removesuffix(
        "_resolved"
    ) not in {"total_debt", "shares_outstanding"}


OPEN_PERIOD_RULE_ID = "tagmap.open_period@1"
OPEN_PERIOD_REASON = "not printed in this filing"


def read_open_periods(path: Path) -> list[dict]:
    """open_periods_*.csv (company_id, stmt, concept, period, why): each OPEN period becomes a tagless
    'not_presented' row (company, stmt, concept, era = that period) with the library's reason and rule."""
    with path.open(newline="") as fh:
        raw = list(csv.DictReader(fh))
    return [
        {
            "company_id": r["company_id"],
            "stmt": r["stmt"],
            "decision": "not_presented",
            "canonical_concept": r["concept"],
            "era_from": r["period"],
            "era_to": r["period"],
            "reason": OPEN_PERIOD_REASON,
            "reason_class": "open_period",
            "rule_id": OPEN_PERIOD_RULE_ID,
            "decided_by": "open_period",
            "evidence_plabel": r.get("why"),
        }
        for r in raw
    ]


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
    n["scale"] = (
        Decimal(str(r.get("scale"))) if r.get("scale") is not None else Decimal(1)
    )
    if n["scale"] <= 0:
        raise ValueError("scale must be > 0")
    if (
        n["scale"] != 1
    ):  # a scale is valid only from a filing-checked company override, with its evidence
        by = str(n["decided_by"] or "").lower().replace("-", "_")
        if not by.startswith("company_override"):
            raise ValueError(
                f"scale {n['scale']} refused: only a company override (decided_by company_override) may scale"
            )
        if not (n["evidence_adsh"] or "").strip():
            raise ValueError("scale needs the override's evidence_adsh")
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
                    if a["decision"] == "excluded" and b["decision"] == "excluded":
                        same = (
                            False  # excluded rows never feed anything: they may overlap
                        )
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
    "parent_concept_id, sign, scale, components, serve_note, reason_class, reason, era_from, era_to, evidence_adsh, "
    "evidence_report, evidence_line, evidence_plabel, evidence_cal_parent, decided_by, rule_id) values "
    "(%(company_id)s, %(cik)s, %(taxonomy)s, %(tag)s, %(stmt)s, %(decision)s, %(canonical_concept_id)s, "
    "%(parent_concept_id)s, %(sign)s, %(scale)s, %(components)s, %(serve_note)s, %(reason_class)s, %(reason)s, %(era_from)s, "
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
    open_periods: Path | None = None,
    only_rule: str | None = None,
) -> dict:
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company")
        company_by_cik = dict(cur.fetchall())
        cur.execute("select name, id, statement from analytics.canonical_concept")
        _cc = cur.fetchall()
        concept_by_name = {n: i for n, i, _ in _cc}
        concept_stmt = {i: (n, st) for n, i, st in _cc}
    by_company: dict[int, list[dict]] = defaultdict(list)
    undecided: list[dict] = []
    refused_instant: list[dict] = []
    held_verifier = 0
    errors: list[str] = []
    warnings: list[str] = []
    all_rows = read_rows(path) + (
        read_open_periods(open_periods) if open_periods else []
    )
    for i, raw in enumerate(all_rows, start=1):
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
        if n["decision"] == "component":
            pname, pstmt = concept_stmt[n["parent_concept_id"]]
            if instant_sum_refused(pname, pstmt):
                refused_instant.append(
                    {
                        "company_id": n["company_id"],
                        "cik": n["cik"],
                        "parent_concept": pname,
                        "tag": n["tag"],
                        "era_from": n["era_from"],
                    }
                )
                errors.append(
                    f"row {i}: instant component sum refused: {pname} <- {n['tag']} (instants are never derived; only total_debt)"
                )
                continue
        if only_rule is not None and n["rule_id"] != only_rule:
            continue  # another writer's row: neither loaded nor replaced
        by_company[n["company_id"]].append(n)
    superseded: list[dict] = []
    if only_rule is not None and by_company:
        live: dict[int, list[dict]] = defaultdict(list)
        with conn.cursor() as cur:
            cur.execute(
                "select company_id, taxonomy, tag, stmt, decision, canonical_concept_id, parent_concept_id, era_from, era_to, rule_id "
                "from analytics.company_tag_map where company_id = any(%s) and rule_id <> %s",
                (sorted(by_company), only_rule),
            )
            cols = [d.name for d in cur.description]
            for t in cur.fetchall():
                live[t[0]].append(dict(zip(cols, t)))

        def clash(a, b):
            return (a["era_to"] is None or a["era_to"] >= b["era_from"]) and (
                b["era_to"] is None or b["era_to"] >= a["era_from"]
            )

        for company_id, rows in by_company.items():
            kept = []
            for n in rows:
                hit = None
                if n["decision"] in TAGLESS:
                    hit = next(
                        (
                            x
                            for x in live[company_id]
                            if x["decision"] in ("concept", "component", *TAGLESS)
                            and (x["canonical_concept_id"] or x["parent_concept_id"])
                            == n["canonical_concept_id"]
                            and clash(x, n)
                        ),
                        None,
                    )
                if hit:
                    superseded.append(
                        {
                            "company_id": company_id,
                            "canonical_concept_id": n["canonical_concept_id"],
                            "era_from": n["era_from"],
                            "by_rule": hit["rule_id"],
                            "by_decision": hit["decision"],
                        }
                    )
                else:
                    kept.append(n)
            by_company[company_id] = kept
            before = set(check_overlaps(live[company_id]))
            errors.extend(
                e for e in check_overlaps(kept + live[company_id]) if e not in before
            )
    else:
        for rows in by_company.values():
            errors.extend(check_overlaps(rows))
    stats: dict[str, Any] = {
        "companies": len(by_company),
        "rows": sum(map(len, by_company.values())),
        "undecided_skipped": len(undecided) - held_verifier,
        "held_verifier_sample_failed": held_verifier,
        "refused_instant_components": refused_instant,
        "completeness": completeness(
            [r for rs in by_company.values() for r in rs], undecided
        ),
        "warnings": sorted(set(warnings)),
        "errors": errors,
        "applied": False,
        "only_rule": only_rule,
        "superseded_by_live": superseded,
    }
    stats["winner_tag_gaps"], stats["winner_tag_gap_details"] = winner_tag_gaps(
        conn,
        [r for rs in by_company.values() for r in rs],
        {i: n for n, i in concept_by_name.items()},
    )
    if errors or not apply:
        return stats  # all-or-nothing on validation
    for company_id, rows in sorted(by_company.items()):
        with conn.transaction():
            if only_rule is not None:
                conn.execute(
                    "delete from analytics.company_tag_map where company_id = %s and rule_id = %s",
                    (company_id, only_rule),
                )
            else:
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
) -> tuple[dict, list[dict]]:
    """Read-only count of winner-tag gaps per (company, concept): periods inside a concept row's era where an
    excluded alternate tag of the same concept (reason_class alternate_tag_overlapping) has an authoritative
    core.fact but the winner tag has none. The mapper blanks these ("no fact under <tag> for this period")."""
    by_company: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        by_company[r["company_id"]].append(r)
    out: dict = {}
    details: list[dict] = []
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
                """select c.tag, p.end_date, fl.accession_number from core.fact f
                   join core.concept c on c.id = f.concept_id
                   join core.period p on p.id = f.period_id
                   join core.filing fl on fl.id = f.filing_id
                   where f.company_id = %s and f.is_authoritative and c.tag = any(%s)
                   order by fl.filing_date desc nulls last""",
                (company_id, tags),
            )
            ends: dict[str, set] = defaultdict(set)
            held_in: dict[tuple[str, date], str] = {}
            for tag, end, acc in cur.fetchall():
                ends[tag].add(end)
                held_in.setdefault((tag, end), acc)  # the latest filing holding it
        open_rows = [r for r in rs if r["decision"] == "not_presented"]
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
                    # an OPEN period (tagless not_presented row) is already a reasoned blank
                    and not any(
                        o["canonical_concept_id"] == w["canonical_concept_id"]
                        and o["stmt"] == w["stmt"]
                        and o["era_from"] <= e <= (o["era_to"] or date.max)
                        for o in open_rows
                    )
                }
                if gap:
                    out[(company_id, cname, w["tag"], a["tag"])] = len(gap)
                    for e in sorted(gap):
                        details.append(
                            {
                                "company_id": company_id,
                                "concept": cname,
                                "period_end": e,
                                "winner_tag": w["tag"],
                                "fact_exists_under": a["tag"],
                                "filing": held_in.get((a["tag"], e)),
                            }
                        )
    return out, details
