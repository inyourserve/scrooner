"""Buybacks and dividends paid as a `mapping.map_filing` detector (FORMATS-v1.1 detector hook).

The run 7 cash-flow lane (pipeline/scripts/slot_records/cf_family_replay.py, imported, never retyped) reads every
cash-flow face column of ONE filing: `read_cell` classifies each financing line (`buyback_class`,
`dividend_class`: label and tag rules, custom tags included) and `verdict_bb` / `verdict_div` apply the lane's gates
(face column, cash-flow identity, financing section tie, perimeter, sign). The seed maps only a few standard tags;
this detector extends the mapping to every line the lane calls the company's own common buyback / common dividend
line, whatever its tag, and withdraws a seed match the lane does not count (an NCI or preferred dividend printed
under PaymentsOfDividends, a tax-withholding line).

One line per concept per filing (fsn_store.select reads one mapped line), decided per filing (see decide()):
* MAPPED: exactly one common line and the lane publishes it (every other column neutral), whatever its tag;
* HELD on a DEFINITIONAL lane hold (combined, net, unresolved, sign unclear, two common lines, only excluded lines):
  every family line and seed match of the filing is returned `unmapped` with the lane's verdicts as evidence. A
  dividend the lane would sum over two common lines (regular + special) is held: the store does not sum lines;
* otherwise the seed decision stands: the lane's STRUCTURAL gates (calc linkbase, identity / section tie) are the
  store's own column checks' business, and holding a filing's latest copy would let an older vintage win.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

LANE_DIR = Path(__file__).resolve().parents[3] / "scripts" / "slot_records"
BUYBACKS = "share_buybacks_resolved"
DIVIDENDS = "dividends_paid_resolved"
RULE = {
    BUYBACKS: "cf.buybacks_common_line@1",
    DIVIDENDS: "cf.dividends_paid_common_line@1",
    "held": "cf.buybacks_dividends_held@1",
}
# lane verdicts that do not stop a filing's line from mapping: the column is not a face column, or the line is
# printed with no value in that column (a dash), or the lane publishes it
NEUTRAL = {"publishable", "not_a_face_column", "no_value_this_column"}
# the lane's STRUCTURAL column gates: the store checks every column itself (fsn.filing_check) and the financing calc
# only scopes which lines are members, so these never withdraw a seed match (they would hold a filing's latest copy
# and let an older vintage win). They do stop a NEW (unseeded) line from mapping.
STRUCTURAL = {
    "hold_no_statement_cal",
    "hold_no_financing_calc",
    "hold_identity_terms_missing",
    "hold_identity_gap",
    "hold_section_gap",
    "stub_column",
}


def _lane():
    if str(LANE_DIR) not in sys.path:
        sys.path.insert(0, str(LANE_DIR))
    import cf_family_replay as lane  # noqa: PLC0415  (the run 7 lane module, imported, never copied)

    return lane


def lane_inputs(
    conn: psycopg.Connection, filing_id: int
) -> tuple[str, dict, dict, dict] | None:
    """(accession, face, vals, arcs) of one fsn.filing in the shapes cf_family_replay.load() builds from the
    cohort files (cf_face_rows / cf_num_rows / cf_cal_rows filters)."""
    lane = _lane()
    with conn.cursor() as cur:
        cur.execute("select accession from fsn.filing where id = %s", (filing_id,))
        row = cur.fetchone()
        if row is None:
            return None
        acc = row[0]
        cur.execute(
            """select l.report, l.line, t.tag, coalesce(l.plabel, ''), t.custom, l.negating
               from fsn.line l join fsn.tag t on t.id = l.tag_id
               where l.filing_id = %s and l.stmt = 'CF' and not l.inpth
               order by l.report, l.line""",
            (filing_id,),
        )
        rows = [
            (r, ln, t, lab, bool(cu), bool(ng))
            for r, ln, t, lab, cu, ng in cur.fetchall()
        ]
        if not rows:
            return None
        tags = sorted({r[2] for r in rows})
        cur.execute(
            """select t.tag, v.ddate, v.qtrs, v.value
               from fsn.value v join fsn.tag t on t.id = v.tag_id
               where v.filing_id = %s and v.dim_id = 0 and v.uom = 'USD' and v.qtrs between 1 and 4
                 and v.iprx = 0 and v.coreg = '' and v.value is not null and t.tag = any(%s)
               order by v.id""",
            (filing_id, tags),
        )
        vals: dict[str, dict[tuple[str, str, int], Decimal]] = defaultdict(dict)
        for t, d, q, v in cur.fetchall():
            vals[acc].setdefault((t, f"{d:%Y%m%d}", int(q)), Decimal(v))
        cur.execute(
            """select a.grp, p.tag, c.tag, a.weight from fsn.calc_arc a
               join fsn.tag p on p.id = a.parent_tag_id join fsn.tag c on c.id = a.child_tag_id
               where a.filing_id = %s order by a.grp, a.arc""",
            (filing_id,),
        )
        groups: dict[Any, list[tuple[str, str, Decimal]]] = defaultdict(list)
        for g, p, c, w in cur.fetchall():
            groups[g].append((p, c, Decimal(w)))
    # common.fsn_cal_arcs' cash-flow group: the largest group whose parents include the operating total
    cf_group = None
    for g, arcs in groups.items():
        if {p for p, _c, _w in arcs} & {lane.OP_TOTAL, lane.OP_CONT}:
            if cf_group is None or len(arcs) > len(groups[cf_group]):
                cf_group = g
    arcs_cf: dict[str, list[tuple[str, Decimal]]] = defaultdict(list)
    for p, c, w in groups.get(cf_group, []):
        arcs_cf[p].append((c, w))
    face = {acc: list(rows)}
    lane.primary_face(face)
    return acc, face, vals, dict(arcs_cf)


def decide(acc: str, face: dict, vals: dict, arcs: dict) -> dict[str, dict[str, Any]]:
    """concept -> {"status": mapped|held|seed_only|none, "tag", "columns", "reasons", "lines": {tag: class}}

    mapped     exactly one common line, the lane publishes it in at least one column and every other column is
               neutral: the line maps whatever its tag
    held       a DEFINITIONAL hold (combined, net, unresolved, sign, two common lines, only excluded lines): the
               lane does not count these lines as the concept, so seed matches are withdrawn
    seed_only  only STRUCTURAL lane gates stop publication (no calc linkbase, financing calc, identity / section
               tie): the store runs its own column checks, so the seed decision stands and nothing new is mapped
    none       no family line on the primary face (or no USD column): the seed decision stands
    """
    lane = _lane()
    cols = sorted({(d, q) for (_t, d, q) in vals.get(acc, {}) if d >= lane.SINCE})
    out: dict[str, dict[str, Any]] = {}
    for concept, fam, vf in (
        (BUYBACKS, "buybacks", lane.verdict_bb),
        (DIVIDENDS, "dividends_paid", lane.verdict_div),
    ):
        verdicts: Counter[str] = Counter()
        lines: dict[str, str] = {}
        columns = []
        for d, q in cols:
            r = lane.read_cell(acc, d, q, arcs, face, vals)
            r["stub"] = (
                False  # the stub rule is company-wide (durp mode); select keeps its own face/length rules
            )
            verdict, _value = vf(r, r[fam])
            for m in r[fam]["members"]:
                lines.setdefault(m["tag"], m["class"])
            if verdict is None:
                continue
            verdicts[verdict] += 1
            columns.append(f"{d}|{q}:{verdict}")
        common = sorted(t for t, c in lines.items() if c == "common")
        definitional = sorted(set(verdicts) - NEUTRAL - STRUCTURAL)
        if len(common) > 1:
            definitional.append("multiple_common_lines_not_summed_in_store")
        if lines and not common and not verdicts:
            definitional.append(
                "no_common_line"
            )  # only inflow / excluded lines: not the concept
        base = {"lines": lines, "columns": columns}
        if not lines:
            out[concept] = {"status": "none", **base, "reasons": []}
        elif definitional:
            out[concept] = {"status": "held", **base, "reasons": definitional}
        elif (
            len(common) == 1 and "publishable" in verdicts and set(verdicts) <= NEUTRAL
        ):
            out[concept] = {
                "status": "mapped",
                "tag": common[0],
                "rule_id": RULE[concept],
                **base,
                "reasons": [],
            }
        else:
            out[concept] = {
                "status": "seed_only",
                **base,
                "reasons": sorted(set(verdicts) - NEUTRAL),
            }
    return out


def cf_family_detector(
    conn: psycopg.Connection, filing_id: int, decisions: list[tuple]
) -> list[tuple]:
    """FORMATS-v1.1 detector: overrides (filing_id, report, line, concept_id, status, rule_id, era, evidence)."""
    got = lane_inputs(conn, filing_id)
    if got is None:
        return []
    acc, face, vals, arcs = got
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            ([BUYBACKS, DIVIDENDS],),
        )
        cid = dict(cur.fetchall())
    with conn.cursor() as cur:
        cur.execute(
            """select l.report, l.line, t.tag from fsn.line l join fsn.tag t on t.id = l.tag_id
               where l.filing_id = %s and l.stmt = 'CF' and not l.inpth""",
            (filing_id,),
        )
        cf_lines = [(r, ln, t) for r, ln, t in cur.fetchall()]
    primary = {(t, ln) for ln, t, *_ in face[acc]}
    seeded: dict[int, set[tuple[int, int]]] = defaultdict(set)
    for d in decisions:
        if d[3] is not None and d[4] in ("mapped", "combined"):
            seeded[d[3]].add((d[1], d[2]))
    out = []
    for concept, dec in decide(acc, face, vals, arcs).items():
        if concept not in cid or dec["status"] in ("none", "seed_only"):
            continue  # the seed decision stands
        family = {
            (r, ln) for r, ln, t in cf_lines if t in dec["lines"] and (t, ln) in primary
        }
        touched = sorted(family | seeded[cid[concept]])
        for r, ln in touched:
            tag = next((t for rr, ll, t in cf_lines if (rr, ll) == (r, ln)), None)
            if dec["status"] == "mapped" and tag == dec["tag"] and (r, ln) in family:
                out.append(
                    (
                        filing_id,
                        r,
                        ln,
                        cid[concept],
                        "mapped",
                        dec["rule_id"],
                        None,
                        {
                            "detector": "cf_family",
                            "tag": tag,
                            "columns": dec["columns"],
                        },
                    )
                )
            else:
                why = (
                    dec["reasons"]
                    if dec["status"] == "held"
                    else (
                        ["not_the_lane_member"]
                        if dec["status"] == "mapped"
                        else ["no_family_line_on_primary_face"]
                    )
                )
                out.append(
                    (
                        filing_id,
                        r,
                        ln,
                        None,
                        "unmapped",
                        RULE["held"],
                        None,
                        {
                            "detector": "cf_family",
                            "tag": tag,
                            "concept": concept,
                            "class": dec["lines"].get(tag or ""),
                            "held": why,
                        },
                    )
                )
    return out
