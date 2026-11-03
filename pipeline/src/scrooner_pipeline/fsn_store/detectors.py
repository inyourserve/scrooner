"""Ported lane detectors for `mapping.map_filing(..., detectors=[...])` (FORMATS-v1.1 detector hook).

capex / D&A (lane `capex_da_cash_debt`, Verifier-passed file 6f53c945): the lane's own per-(filing, column)
evaluation, `cf_da_capex_variants.evaluate` (pipeline/scripts/slot_records, imported, never retyped), is run on
every cash-flow face column of ONE filing. Its release rule (emit_capex_da_cash.py) then decides per filing:

* capex: a column publishes when the lane's interim value exists and the cell has exactly one member line;
* D&A: a column publishes when `da_class` is is_anchor / single_line_ties_is / single_line_clean; the line is the
  single asset_da cash-flow line, or for is_anchor the income statement's printed D&A line.

One line per concept per filing (fsn_store.select takes one mapped line per concept and calls two values a defect):
the line is MAPPED only when every face column of the filing that prints a candidate publishes through that same
line AND the store's raw print equals the lane's value in each of them (the lane reads signs as presented). In every
other case the filing is HELD for that concept: each of its capex / D&A lines is returned `unmapped` with the lane's
reasons as evidence, so no rival value reaches select. Decided per filing, never per company (HD prints one D&A line
before FY2025). A combined line the lane holds as `da_combined_with_other_items` (MSFT "Depreciation, amortization,
and other") is returned `combined`.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

LANE_DIR = Path(__file__).resolve().parents[3] / "scripts" / "slot_records"
DA_EMIT = {
    "is_anchor",
    "single_line_ties_is",
    "single_line_clean",
}  # emit_capex_da_cash.DA_EMIT
CAPEX = "capex_resolved"
DA = "depreciation_and_amortization_resolved"
RULE = {
    CAPEX: "cf.capex_single_member@1",
    DA: "cf.da_single_line@1",
    "is_anchor": "cf.da_is_anchor@1",
    "held": "cf.capex_da_held@1",
}
NET_REASON = "da_net_line_below_intangible_amortization"  # the lane's Verifier V10 reason (KEY FY2021)
NET_CARRIED = "da_net_line_failed_in_another_filing"  # the lane's company rule (Verifier V11, KEY FY2023)
_NET = re.compile(r"\bnet\b", re.I)


def _norm(label: str) -> str:
    return label.strip().lower()


def _lane():
    if str(LANE_DIR) not in sys.path:
        sys.path.insert(0, str(LANE_DIR))
    import cf_da_capex_variants as lane  # noqa: PLC0415  (the lane module, imported, never copied)

    return lane


def _dec(x: Any) -> Decimal | None:
    try:
        return None if x in (None, "") else Decimal(str(x))
    except Exception:  # noqa: BLE001
        return None


def face_columns(f: dict[str, Any]) -> list[tuple[str, int]]:
    """the columns cf_da_capex_variants.main evaluates: 1-4 quarters, since 2014, a CF section total printed"""
    lane = _lane()
    cf = [r for r in f["face"] if r["stmt"] == "CF"]
    out = []
    for col, vals in f["values"].items():
        ddate, q = col.split("|")
        if int(q) not in (1, 2, 3, 4) or ddate < "20140101" or not cf:
            continue
        if any(t in vals for t in lane.OP_TOTAL + lane.INV_TOTAL):
            out.append((ddate, int(q)))
    return sorted(out)


def decide(
    f: dict[str, Any], net_labels: frozenset[str] | set[str] = frozenset()
) -> dict[str, dict[str, Any]]:
    """{concept: {"status": "mapped"|"held", "tag": tag|None, "stmt": "CF"|"IS", "columns": [...], "reasons": [...]}}
    for the concepts the lane evaluates on this filing. Pure: no database.

    `net_labels`: the lowercased "net" D&A labels that failed the lane's V10 check in ANOTHER filing of the company
    (company_net_labels). The lane's company rule (V11, KEY FY2023) holds such a label in every period, so a column
    whose asset D&A line carries one is held here (reason NET_CARRIED), exactly as the lane does."""
    lane = _lane()
    per: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ddate, q in face_columns(f):
        vals = f["values"][f"{ddate}|{q}"]
        for c in lane.evaluate(f["cik"], ddate, q, f):
            col = f"{ddate}|{q}"
            if c["family"] == "capex":
                lines = c["lines"]
                if c["interim"] is not None and len(lines) == 1:
                    tag = lines[0]["tag"]
                    per[CAPEX].append(
                        {
                            "col": col,
                            "pub": True,
                            "tag": tag,
                            "stmt": "CF",
                            "value": _dec(c["interim"]),
                            "raw": _dec(vals.get(tag)),
                        }
                    )
                else:
                    reason = (
                        c["interim_reason"] or "multi_member_composition_unverified"
                    )
                    per[CAPEX].append({"col": col, "pub": False, "reason": reason})
            else:
                carried = c["value"] is not None and any(
                    x["nature"] == "asset_da" and _norm(x["label"]) in net_labels
                    for x in c["lines"]
                )
                if carried:
                    per[DA].append(
                        {
                            "col": col,
                            "pub": False,
                            "reason": NET_CARRIED,
                            "combined": [],
                        }
                    )
                elif c["value"] is not None and c.get("da_class") in DA_EMIT:
                    if c["da_class"] == "is_anchor":
                        total = _dec(c.get("is_da_total"))
                        tags = [
                            r["tag"]
                            for r in f["face"]
                            if r["stmt"] == "IS" and _dec(vals.get(r["tag"])) == total
                        ]
                        tag, stmt = (tags[0] if len(set(tags)) == 1 else None), "IS"
                    else:
                        asset = [x for x in c["lines"] if x["nature"] == "asset_da"]
                        tag, stmt = (asset[0]["tag"] if len(asset) == 1 else None), "CF"
                    per[DA].append(
                        {
                            "col": col,
                            "pub": tag is not None,
                            "tag": tag,
                            "stmt": stmt,
                            "da_class": c["da_class"],
                            "value": _dec(c["value"]),
                            "raw": _dec(vals.get(tag)) if tag else None,
                            "reason": None if tag else "is_anchor_line_not_unique",
                            "labels": sorted(
                                {
                                    _norm(x["label"])
                                    for x in c["lines"]
                                    if x["nature"] == "asset_da"
                                }
                            ),
                        }
                    )
                else:
                    reason = c["reason"] or "da_multi_member_unverified"
                    per[DA].append(
                        {
                            "col": col,
                            "pub": False,
                            "reason": reason,
                            "net_failed": sorted(
                                {
                                    _norm(x["label"])
                                    for x in c["lines"]
                                    if x["nature"] == "asset_da"
                                    and _NET.search(x["label"])
                                }
                            )
                            if reason == NET_REASON
                            else [],
                            "combined": [
                                x["tag"]
                                for x in c["lines"]
                                if x["nature"] == "combined_other"
                            ]
                            if reason == "da_combined_with_other_items"
                            else [],
                        }
                    )
    out: dict[str, dict[str, Any]] = {}
    for concept, cols in per.items():
        tag_set = {(x["stmt"], x["tag"]) for x in cols if x["pub"]}
        held = [x for x in cols if not x["pub"]]
        sign = [x["col"] for x in cols if x["pub"] and x["raw"] != x["value"]]
        if not held and len(tag_set) == 1 and not sign:
            stmt, tag = next(iter(tag_set))
            classes: list[str] = sorted(
                {str(x["da_class"]) for x in cols if x.get("da_class")}
            )
            out[concept] = {
                "status": "mapped",
                "tag": tag,
                "stmt": stmt,
                "columns": [x["col"] for x in cols],
                "rule_id": RULE["is_anchor"]
                if classes == ["is_anchor"]
                else RULE[concept],
                "da_class": classes,
                "labels": sorted({lb for x in cols for lb in x.get("labels", [])}),
            }
        else:
            reasons = sorted({x["reason"] for x in held if x.get("reason")})
            if len(tag_set) > 1:
                reasons.append("different_line_per_column")
            if sign:
                reasons.append("store_print_differs_from_lane_value")
            out[concept] = {
                "status": "held",
                "tag": None,
                "columns": [x["col"] for x in cols],
                "reasons": reasons,
                "combined": sorted({t for x in held for t in x.get("combined", [])}),
                "net_failed": sorted(
                    {lb for x in held for lb in x.get("net_failed", [])}
                ),
            }
    return out


# ---------------------------------------------------------------- the store adapter
def filing_object(conn: psycopg.Connection, filing_id: int) -> dict[str, Any] | None:
    """the lane's filing object (cf_face_extract.py shape) for one fsn.filing: CF and IS face rows, undimensioned USD
    duration values of the face tags (primary registrant), cal arcs between two face tags"""
    with conn.cursor() as cur:
        cur.execute(
            "select accession, cik, form, period, filed, fy, fp, fsn_set from fsn.filing where id = %s",
            (filing_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        acc, cik, form, period, filed, fy, fp, fsn_set = row
        cur.execute(
            """select l.stmt, l.report, l.line, t.tag, coalesce(l.plabel, ''), l.negating, t.custom, l.inpth
               from fsn.line l join fsn.tag t on t.id = l.tag_id
               where l.filing_id = %s and l.stmt in ('CF', 'IS')""",
            (filing_id,),
        )
        face = [
            {
                "stmt": s,
                "report": r,
                "line": ln,
                "tag": t,
                "plabel": lab,
                "negating": bool(n),
                "custom": bool(cu),
                "inpth": bool(ip),
            }
            for s, r, ln, t, lab, n, cu, ip in cur.fetchall()
        ]
        if not face:
            return None
        tags = sorted({x["tag"] for x in face})
        cur.execute(
            """select t.tag, v.ddate, v.qtrs, v.value
               from fsn.value v join fsn.tag t on t.id = v.tag_id
               where v.filing_id = %s and v.dim_id = 0 and v.uom = 'USD' and v.qtrs > 0 and v.iprx = 0 and v.coreg = ''
                 and v.value is not null and t.tag = any(%s)""",
            (filing_id, tags),
        )
        values: dict[str, dict[str, str]] = defaultdict(dict)
        for t, d, q, v in cur.fetchall():
            values[f"{d:%Y%m%d}|{q}"][t] = str(v)
        cur.execute(
            """select a.grp, p.tag, c.tag, a.weight from fsn.calc_arc a
               join fsn.tag p on p.id = a.parent_tag_id join fsn.tag c on c.id = a.child_tag_id
               where a.filing_id = %s and p.tag = any(%s) and c.tag = any(%s)""",
            (filing_id, tags, tags),
        )
        cal = [[str(g), p, c, int(w)] for g, p, c, w in cur.fetchall()]
    face.sort(key=lambda x: (x["stmt"], x["report"], x["line"]))
    return {
        "adsh": acc,
        "cik": int(cik),
        "ticker": cik,
        "form": form,
        "period": f"{period:%Y%m%d}" if period else "",
        "fy": fy,
        "fp": fp,
        "filed": f"{filed:%Y%m%d}" if filed else "",
        "fsn_period": fsn_set,
        "face": face,
        "values": dict(values),
        "cal": cal,
    }


def company_net_labels(conn: psycopg.Connection, filing_id: int) -> set[str]:
    """The lane's company rule (Verifier V11, KEY FY2023), carried across filings: the lowercased "net" D&A labels
    that fail the V10 check (`da_net_line_below_intangible_amortization`) in ANY OTHER periodic filing of the same
    registrant. Only filings that print a cash-flow line labelled "net" are evaluated (SQL pre-screen), so a company
    without such a line costs one query. The lane applies the rule over its best filing per column; this reads every
    filing of the registrant, which can only hold MORE cells than the lane, never publish a value it holds."""
    with conn.cursor() as cur:
        cur.execute(
            """select o.id from fsn.filing f join fsn.filing o on o.cik = f.cik and o.id <> f.id
               where f.id = %s and exists (
                   select 1 from fsn.line l where l.filing_id = o.id and l.stmt = 'CF'
                     and coalesce(l.plabel, '') ~* '\\ynet\\y')""",
            (filing_id,),
        )
        others = [r[0] for r in cur.fetchall()]
    out: set[str] = set()
    for oid in others:
        of = filing_object(conn, oid)
        if of is not None:
            out.update(decide(of).get(DA, {}).get("net_failed", []))
    return out


def capex_da_detector(
    conn: psycopg.Connection, filing_id: int, decisions: list[tuple]
) -> list[tuple]:
    """FORMATS-v1.1 detector: overrides (filing_id, report, line, concept_id, status, rule_id, era, evidence)."""
    f = filing_object(conn, filing_id)
    if f is None:
        return []
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            ([CAPEX, DA],),
        )
        cid = dict(cur.fetchall())
    by_line = {(r["stmt"], r["report"], r["line"]): r for r in f["face"]}
    seeded = defaultdict(list)  # concept -> [(report, line)] the seed mapped to it
    for d in decisions:
        if d[3] is not None and d[4] in ("mapped", "combined"):
            for name, i in cid.items():
                if d[3] == i:
                    seeded[name].append((d[1], d[2]))
    out = []
    decided = decide(f)
    if any(_NET.search(lb) for lb in decided.get(DA, {}).get("labels", [])):
        # a published "net" D&A line: the lane holds it when the same label failed V10 in another period (V11)
        net_labels = company_net_labels(conn, filing_id)
        if net_labels:
            decided = decide(f, net_labels)
    for concept in cid:
        if concept not in decided and seeded[concept]:
            # no cash-flow face column in the lane's window (a filing whose columns all end before 2014): the lane
            # never evaluated it, so nothing it says can map a line; the seed's lines are held (no rival values)
            decided[concept] = {
                "status": "held",
                "tag": None,
                "columns": [],
                "reasons": ["no_face_column_in_lane_window"],
            }
    for concept, dec in decided.items():
        if concept not in cid:
            continue
        chosen = None
        if dec["status"] == "mapped":
            rows = [
                (k, r)
                for k, r in by_line.items()
                if r["stmt"] == dec["stmt"]
                and r["tag"] == dec["tag"]
                and not r["inpth"]
            ]
            chosen = rows[0][0] if rows else None
        candidates = {
            (r["report"], r["line"])
            for k, r in by_line.items()
            if (dec["status"] == "mapped" and r["tag"] == dec["tag"])
            or r["tag"] in dec.get("combined", [])
        }
        touched = set(seeded[concept]) | candidates
        for report, line in sorted(touched):
            stmt = next((k[0] for k in by_line if k[1:] == (report, line)), None)
            tag = by_line.get((stmt, report, line), {}).get("tag")
            if chosen and (stmt, report, line) == chosen:
                out.append(
                    (
                        filing_id,
                        report,
                        line,
                        cid[concept],
                        "mapped",
                        dec["rule_id"],
                        None,
                        {
                            "detector": "capex_da",
                            "tag": tag,
                            "columns": dec["columns"],
                            "da_class": dec.get("da_class"),
                        },
                    )
                )
            elif dec["status"] == "held" and tag in dec.get("combined", []):
                out.append(
                    (
                        filing_id,
                        report,
                        line,
                        None,
                        "combined",
                        RULE["held"],
                        None,
                        {
                            "detector": "capex_da",
                            "tag": tag,
                            "held": dec["reasons"],
                            "concept": concept,
                        },
                    )
                )
            else:
                out.append(
                    (
                        filing_id,
                        report,
                        line,
                        None,
                        "unmapped",
                        RULE["held"],
                        None,
                        {
                            "detector": "capex_da",
                            "tag": tag,
                            "concept": concept,
                            "held": dec.get("reasons") or ["not_the_lane_member"],
                        },
                    )
                )
        if chosen and (chosen[1], chosen[2]) not in touched:
            out.append(
                (
                    filing_id,
                    chosen[1],
                    chosen[2],
                    cid[concept],
                    "mapped",
                    dec["rule_id"],
                    None,
                    {
                        "detector": "capex_da",
                        "tag": dec["tag"],
                        "columns": dec["columns"],
                        "da_class": dec.get("da_class"),
                    },
                )
            )
    return out


DEFAULT = [capex_da_detector]
