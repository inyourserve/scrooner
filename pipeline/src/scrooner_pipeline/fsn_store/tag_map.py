"""Per-company tag map from the FSN store: which statement tag is what, decided by the filing's own structure.

Founder 2026-11-11: "FSN for learning (which tag is what), SEC for mapping". Engineering owns the table
(analytics.company_tag_map, migration 0123) and the companyfacts mapper that reads it; this module emits its rows.
Read-only: nothing in the store or analytics is written.

Per filing, every statement line (BS IS CF EQ CI CP UN; not notes) gets a decision and `decided_by`:
  structural      an abstract header (no value): excluded `abstract_header`; a cover or parenthetical statement row
                  (stmt CP, or inpth): excluded `cover_or_parenthetical`
  rule            BS / IS / CF lines as the mapper decides them NOW (seed concept_rule rows plus detectors.DEFAULT),
                  computed in memory: no fsn.line_map row is needed or written (lines loaded after the last mapping
                  run are decided too)
  calc_ancestor   an otherwise undecided line whose tag sits under a mapped line in the filing's own calc tree (same
                  filing, the ancestor printed on the same statement): combined, combine_role `component_of`, the
                  ancestor's concept, sign = the product of the arc weights on the path, path recorded in `reason`
  (none)          everything else: the residue for the library (Ritwik, the Tag Expert); never emitted as a row

Tag key: taxonomy + tag. Standard tags: taxonomy `us-gaap` / `srt` / `dei` / `ifrs`, version-free. A company
extension: taxonomy `ext` (FSN gives the accession as its version, not the company prefix; the seeder resolves the
prefix from core.concept by tag name for the company).

Eras: consecutive stored filings (period, then acceptance order) with the same decision. era_from / era_to are the
first and last filing period; the era of the latest filing is open (era_to = None). Evidence: the era's latest filing
(accession, report, line, the filer's own label). One tag printed twice in a filing with different decisions keeps
the face (non-parenthetical) decision; two different face decisions make the filing undecided for that tag (residue
reason `different_decisions_in_one_filing`), so a consumer never picks one silently.
"""

from __future__ import annotations

import csv
import re
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

import psycopg

from scrooner_pipeline.fsn_store import mapping

# analytics.company_tag_map (Engineering, migration 0123, schema revision adopted from Ritwik's tag library)
COLUMNS = [
    "company_id",
    "cik",
    "taxonomy",
    "tag",
    "stmt",
    "decision",
    "canonical_concept",
    "parent_concept",
    "combine_sign",
    "components",
    "reason_class",
    "reason",
    "era_from",
    "era_to",
    "evidence_adsh",
    "evidence_report",
    "evidence_line",
    "evidence_plabel",
    "evidence_cal_parent",
    "decided_by",
    "rule_id",
]
RESIDUE_COLUMNS = [
    "company_id",
    "cik",
    "taxonomy",
    "tag",
    "stmt",
    "era_from",
    "era_to",
    "filings",
    "reason",
    "evidence_adsh",
    "evidence_report",
    "evidence_line",
    "evidence_plabel",
]
STATEMENTS = ("BS", "IS", "CF", "EQ", "CI", "CP", "UN")
TAXONOMY = {"us-gaap": "us-gaap", "srt": "srt", "dei": "dei", "ifrs-full": "ifrs"}
MAPPED_STMTS = ("BS", "IS", "CF")
PRESENTATION_ONLY = re.compile(
    r"(Abstract|Axis|Domain|Member|Table|LineItems)$"
)  # what mapping.map_filing decides


def taxonomy_of(version: str, custom: bool) -> str:
    if custom:
        return "ext"
    base = version.split("/", 1)[0]
    return TAXONOMY.get(base, base)


def _filings(conn: psycopg.Connection, company_id: int) -> list[tuple]:
    return conn.execute(
        """select id, accession, form, period from fsn.filing where company_id = %s
           order by period nulls first, accepted, id""",
        (company_id,),
    ).fetchall()


def _lines(conn: psycopg.Connection, filing_id: int) -> list[dict[str, Any]]:
    return [
        {
            "stmt": s,
            "report": r,
            "line": ln,
            "plabel": lab,
            "tag": t,
            "version": v,
            "custom": bool(cu),
            "abstract": bool(ab),
            "inpth": bool(ip),
        }
        for s, r, ln, lab, t, v, cu, ab, ip in conn.execute(
            """select l.stmt, l.report, l.line, coalesce(l.plabel, ''), t.tag, t.version, t.custom, t.abstract, l.inpth
               from fsn.line l join fsn.tag t on t.id = l.tag_id
               where l.filing_id = %s and l.stmt = any(%s) order by l.report, l.line""",
            (filing_id, list(STATEMENTS)),
        ).fetchall()
    ]


def _arcs(conn: psycopg.Connection, filing_id: int) -> dict[str, list[tuple[str, int]]]:
    """child tag -> [(parent tag, weight)] of the filing's calc tree"""
    out: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for p, c, w in conn.execute(
        """select p.tag, c.tag, a.weight from fsn.calc_arc a join fsn.tag p on p.id = a.parent_tag_id
           join fsn.tag c on c.id = a.child_tag_id where a.filing_id = %s""",
        (filing_id,),
    ).fetchall():
        out[c].append((p, int(w)))
    return out


def calc_ancestor(
    tag: str,
    stmt: str,
    arcs: dict[str, list[tuple[str, int]]],
    mapped: dict[tuple[str, str], str],
) -> tuple[str, int, list[str]] | None:
    """the nearest calc ancestor of `tag` that is a mapped line on the same statement: (concept, sign, path).
    Breadth-first over parents; a tag with two different nearest mapped ancestors is ambiguous (None)."""
    frontier = [(tag, 1, [tag])]
    seen = {tag}
    while frontier:
        hits = []
        nxt = []
        for t, sign, path in frontier:
            for p, w in arcs.get(t, ()):
                if p in seen:
                    continue
                s2, path2 = sign * w, [*path, p]
                if (stmt, p) in mapped:
                    hits.append((mapped[(stmt, p)], s2, path2))
                else:
                    nxt.append((p, s2, path2))
        if hits:
            concepts = {(h[0], h[1]) for h in hits}
            return hits[0] if len(concepts) == 1 else None
        for t, _, _ in nxt:
            seen.add(t)
        frontier = nxt
    return None


def load_library(path: Path | None) -> dict[tuple[str, str], dict[str, str]]:
    """the Tag Expert's standard-tag library, {(stmt, tag): row}; an absent file is an empty library"""
    if path is None or not Path(path).exists():
        return {}
    with Path(path).open(newline="") as fh:
        return {
            (r["stmt"], r["tag"]): r for r in csv.DictReader(fh) if r.get("decision")
        }


def apply_library(rec: dict[str, Any], lib: dict[str, str]) -> None:
    caveat = lib.get("caveat") or None
    if lib["decision"] == "map":
        rec.update(
            disposition="mapped",
            concept=lib["concept"],
            decided_by="library",
            reason=caveat,
        )
    elif lib["decision"] == "component":
        rec.update(
            disposition="combined",
            combine_role="component_of",
            concept=lib["parent_concept"],
            sign=1,
            decided_by="library",
            reason=caveat,
        )
    elif lib["decision"] == "excluded":
        rec.update(
            disposition="excluded",
            decided_by="library",
            reason=lib.get("reason_class") or caveat or "library_excluded",
        )


def library_agrees(rec: dict[str, Any], lib: dict[str, str]) -> bool:
    if lib["decision"] == "map":
        return rec["disposition"] == "mapped" and rec["concept"] == lib["concept"]
    if lib["decision"] == "component":
        return (
            rec["disposition"] == "combined" and rec["concept"] == lib["parent_concept"]
        )
    return rec["disposition"] == "excluded"


def filing_decisions(
    conn: psycopg.Connection,
    filing_id: int,
    rules: dict[str, Any],
    detectors: list[Callable] | None,
    concept_names: dict[int, str],
    library: dict[tuple[str, str], dict[str, str]] | None = None,
    disagreements: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """one decision per statement line of one filing (see the module docstring)"""
    lines = _lines(conn, filing_id)
    collected: list[tuple] = []
    mapping.map_filing(
        conn, filing_id, rules, write=False, detectors=detectors, collect=collected
    )
    by_line = {(d[1], d[2]): d for d in collected}
    rules_by_id = {r["rule_id"]: r for r in rules.get("positional", [])}
    mapped: dict[tuple[str, str], str] = {}
    out: list[dict[str, Any]] = []
    for ln in lines:
        d = (
            by_line.get((ln["report"], ln["line"]))
            if ln["stmt"] in MAPPED_STMTS
            else None
        )
        rec = {
            **ln,
            "disposition": None,
            "concept": None,
            "combine_role": None,
            "sign": None,
            "reason": None,
            "rule_id": None,
            "decided_by": None,
            "components": None,
        }
        if ln["abstract"] or PRESENTATION_ONLY.search(ln["tag"]):
            # R1: an abstract header or a dimension element (Axis / Domain / Member) carries no value of its own
            rec.update(
                disposition="excluded",
                reason="presentation-only",
                decided_by="structural",
            )
        elif ln["stmt"] == "CP" or ln["inpth"]:
            rec.update(
                disposition="excluded",
                reason="cover_or_parenthetical",
                decided_by="structural",
            )
        elif (
            d is not None
            and d[4] == "mapped"
            and d[3] is not None
            and (d[7] or {}).get("match") == "calc_position"
        ):
            # a calc_position rule (bs.liab_cal_child, bs.debt_member_parent) maps a MEMBER line under its parent's
            # concept: a component of that concept, never the concept itself
            pos = (rules_by_id.get(d[5]) or {}).get("position") or {}
            rec.update(
                disposition="combined",
                combine_role="component_of",
                concept=concept_names.get(d[3]),
                sign=int(pos.get("sign") or 1),
                rule_id=d[5],
                decided_by="rule",
                reason=f"calc_position slot {(d[7] or {}).get('slot')}",
            )
            mapped.setdefault((ln["stmt"], ln["tag"]), rec["concept"])
        elif d is not None and d[4] == "mapped" and d[3] is not None:
            rec.update(
                disposition="mapped",
                concept=concept_names.get(d[3]),
                rule_id=d[5],
                decided_by="rule",
            )
            mapped[(ln["stmt"], ln["tag"])] = rec["concept"]
        elif d is not None and d[4] == "combined":
            comps = (d[7] or {}).get("components") or (d[7] or {}).get("concept")
            rec.update(
                disposition="combined",
                combine_role="combined_line",
                rule_id=d[5],
                decided_by="rule",
                components=",".join(comps) if isinstance(comps, list) else comps,
                reason=f"one line combining {comps}" if comps else "combined line",
            )
        elif d is not None and d[4] == "excluded":
            rec.update(
                disposition="excluded",
                reason=(d[7] or {}).get("why") or "excluded",
                rule_id=d[5],
                decided_by="rule",
            )
        elif d is not None and d[5]:
            # a rule or detector looked at the line and held it (demote, capex/D&A hold): say which, and why
            ev = d[7] or {}
            held = ev.get("held") or ev.get("demoted_from")
            rec["reason"] = f"held by {d[5]}" + (f": {held}" if held else "")
        out.append(rec)
    held = lambda rec: (rec["reason"] or "").startswith("held by")  # noqa: E731  a detector refused it
    arcs = _arcs(conn, filing_id) if any(r["disposition"] is None for r in out) else {}
    # the Tag Expert's standard-tag library (data-team/tags/library/standard-tag-library.csv): one decision per
    # (stmt, standard tag). Company structure decided above wins; a library row that disagrees with it is reported.
    for rec in out:
        lib = (
            (library or {}).get((rec["stmt"], rec["tag"]))
            if not rec["custom"]
            else None
        )
        if not lib:
            continue
        if rec["disposition"] is not None:
            if (
                rec["decided_by"] == "rule"
                and disagreements is not None
                and not library_agrees(rec, lib)
            ):
                disagreements.append(
                    {
                        "stmt": rec["stmt"],
                        "tag": rec["tag"],
                        "rule_id": rec["rule_id"],
                        "rule_disposition": rec["disposition"],
                        "rule_concept": rec["concept"],
                        "library_decision": lib["decision"],
                        "library_concept": lib.get("concept")
                        or lib.get("parent_concept"),
                        "report": rec["report"],
                        "line": rec["line"],
                        "plabel": rec["plabel"],
                    }
                )
            continue
        if held(rec):
            continue
        apply_library(rec, lib)
        if rec["disposition"] == "mapped":
            mapped.setdefault((rec["stmt"], rec["tag"]), rec["concept"])
    # the same tag printed as a CONCEPT on another statement of this filing (NetIncomeLoss on IS and on EQ / CI;
    # StockholdersEquity on BS and EQ; cash on BS and CF): the same fact, so the same concept. A tag mapped to two
    # different concepts on different statements is ambiguous and decides nothing.
    concept_of_tag: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for rec in out:
        if rec["disposition"] == "mapped":
            concept_of_tag[rec["tag"]].add((rec["concept"], rec["stmt"]))
    for rec in out:
        if rec["disposition"] is not None or held(rec):
            continue
        hits = concept_of_tag.get(rec["tag"], set())
        if len({c for c, _ in hits}) == 1:
            concept, stmt = sorted(hits)[0]
            rec.update(
                disposition="mapped",
                concept=concept,
                decided_by="cross_statement",
                reason=f"same tag mapped on {stmt} in this filing",
            )
    # R2 (first pass, so extensions can hang under these lines): a standard element printed on a statement is its
    # own concept (the companyfacts series of that element). The rules and detectors above have already taken
    # every line the structure gives to a catalog concept or excluded, so a known misuse never reaches this point;
    # a line a detector held stays undecided. The calc parent on the same statement, if any, is kept as evidence.
    for rec in out:
        if rec["disposition"] is not None or held(rec) or rec["custom"]:
            continue
        hit = calc_ancestor(rec["tag"], rec["stmt"], arcs, mapped)
        rec.update(
            disposition="mapped",
            concept=f"{taxonomy_of(rec['version'], False)}:{rec['tag']}",
            decided_by="standard_tag",
            reason="calc path " + " > ".join(hit[2]) if hit else None,
        )
    for rec in out:
        if rec["disposition"] == "mapped":
            mapped.setdefault((rec["stmt"], rec["tag"]), rec["concept"])
    # R3: a company extension takes its place in the filing's calc tree: a component of the nearest decided
    # ancestor on the same statement (a catalog concept or a standard element), with the path's sign
    for rec in out:
        if rec["disposition"] is not None or held(rec):
            continue
        hit = calc_ancestor(rec["tag"], rec["stmt"], arcs, mapped)
        if hit:
            concept, sign, path = hit
            rec.update(
                disposition="combined",
                combine_role="component_of",
                concept=concept,
                sign=sign,
                decided_by="calc_ancestor",
                reason="calc path " + " > ".join(path),
            )
    return out


def company_tag_map(
    conn: psycopg.Connection,
    company_id: int,
    rules: dict[str, Any] | None = None,
    detectors: list[Callable] | None = None,
    library: dict[tuple[str, str], dict[str, str]] | None = None,
    disagreements: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(rows in the company_tag_map contract, residue rows) for one company"""
    from scrooner_pipeline.fsn_store import detectors as det  # noqa: PLC0415  (imports the lane modules)

    rules = rules or mapping.load_rules(conn)
    detectors = det.DEFAULT if detectors is None else detectors
    names = dict(
        conn.execute("select id, name from analytics.canonical_concept").fetchall()
    )
    filings = _filings(conn, company_id)
    cik = (
        conn.execute(
            "select cik from core.company where id = %s", (company_id,)
        ).fetchone()
        or [None]
    )[0]
    per_key: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(
        list
    )
    for i, (fid, acc, form, period) in enumerate(filings):
        seen: dict[tuple[str, str, str], dict[str, Any]] = {}
        for rec in filing_decisions(
            conn, fid, rules, detectors, names, library, disagreements
        ):
            key = (rec["stmt"], taxonomy_of(rec["version"], rec["custom"]), rec["tag"])
            rec = {**rec, "accession": acc, "period": period}
            cur = seen.get(key)
            if cur is None:
                seen[key] = rec
                continue
            sig_new = (
                rec["disposition"],
                rec["concept"],
                rec["combine_role"],
                rec["sign"],
            )
            sig_cur = (
                cur["disposition"],
                cur["concept"],
                cur["combine_role"],
                cur["sign"],
            )
            if sig_new == sig_cur:
                continue
            if (
                rec["reason"] == "cover_or_parenthetical"
                or rec["reason"] == "abstract_header"
            ):
                continue  # the face line decides
            if cur["reason"] in ("cover_or_parenthetical", "abstract_header"):
                seen[key] = rec
                continue
            seen[key] = {
                **cur,
                "disposition": None,
                "concept": None,
                "combine_role": None,
                "sign": None,
                "decided_by": None,
                "reason": "different_decisions_in_one_filing",
            }
        for key, rec in seen.items():
            per_key[key].append((i, rec))
    rows: list[dict[str, Any]] = []
    residue: list[dict[str, Any]] = []
    last_index = len(filings) - 1
    for (stmt, taxonomy, tag), recs in sorted(per_key.items()):
        eras: list[list[tuple[int, dict[str, Any]]]] = []
        for i, rec in recs:
            sig = (
                rec["disposition"],
                rec["concept"],
                rec["combine_role"],
                rec["sign"],
                rec["reason"] if rec["disposition"] is None else None,
            )
            if eras and eras[-1][-1][1]["_sig"] == sig:
                eras[-1].append((i, {**rec, "_sig": sig}))
            else:
                eras.append([(i, {**rec, "_sig": sig})])
        for k, era in enumerate(eras):
            first, last = era[0][1], era[-1][1]
            is_open = k == len(eras) - 1 and era[-1][0] == last_index
            base = {
                "company_id": company_id,
                "cik": cik,
                "taxonomy": taxonomy,
                "tag": tag,
                "stmt": stmt,
                "era_from": first["period"],
                "era_to": None if is_open else last["period"],
                "filings": len(era),
                "evidence_adsh": last["accession"],
                "evidence_report": last["report"],
                "evidence_line": last["line"],
                "evidence_plabel": last["plabel"],
                "reason": last["reason"],
            }
            if last["disposition"] is None:
                residue.append({**base, "reason": last["reason"] or "no_decision"})
                continue
            rows.append({**base, **contract_fields(last)})
    return rows, residue


def contract_fields(rec: dict[str, Any]) -> dict[str, Any]:
    """one decided line in the company_tag_map vocabulary: concept | component | combined | excluded"""
    disp, role = rec["disposition"], rec["combine_role"]
    out: dict[str, Any] = {
        "canonical_concept": None,
        "parent_concept": None,
        "combine_sign": None,
        "components": None,
        "reason_class": None,
        "evidence_cal_parent": None,
        "decided_by": rec["decided_by"],
        "rule_id": rec["rule_id"],
        "reason": rec["reason"],
    }
    if disp == "mapped":
        out.update(
            decision="concept",
            canonical_concept=rec["concept"],
            reason_class={
                "standard_tag": "standard_element",
                "cross_statement": "same_fact_other_statement",
            }.get(rec["decided_by"], "statement_line"),
        )
    elif disp == "combined" and role == "component_of":
        by_calc = rec["decided_by"] == "calc_ancestor"
        path = (
            (rec["reason"] or "").removeprefix("calc path ").split(" > ")
            if by_calc
            else []
        )
        out.update(
            decision="component",
            parent_concept=rec["concept"],
            combine_sign=rec["sign"],
            reason_class="calc_ancestor"
            if by_calc
            else (
                "library" if rec["decided_by"] == "library" else "calc_position_rule"
            ),
            evidence_cal_parent=path[1] if len(path) > 1 else None,
        )
    elif disp == "combined":
        out.update(
            decision="combined",
            components=rec.get("components"),
            reason_class="combined_line",
        )
    else:
        out.update(
            decision="excluded",
            reason_class=rec["reason"]
            if rec["decided_by"] in ("structural", "library")
            else "rule_excluded",
        )
    return out


def company_status(
    rows: list[dict[str, Any]], residue: list[dict[str, Any]]
) -> dict[str, Any]:
    """the metric: complete = every statement tag of the company, in every era, has a decision"""
    tags = {(r["stmt"], r["taxonomy"], r["tag"]) for r in [*rows, *residue]}
    open_tags = {(r["stmt"], r["taxonomy"], r["tag"]) for r in residue}
    by: dict[str, int] = defaultdict(int)
    for r in rows:
        by[r["decided_by"]] += 1
    return {
        "tags": len(tags),
        "open_tags": len(open_tags),
        "complete": bool(tags) and not open_tags,
        "decided_by": dict(by),
    }


def write_csv(rows: Iterable[dict[str, Any]], path: Path, columns: list[str]) -> int:
    n = 0
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in columns})
            n += 1
    return n


def write_jsonl(rows: Iterable[dict[str, Any]], path: Path) -> int:
    n = 0
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, default=str) + "\n")
            n += 1
    return n
