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


# ---------------------------------------------------------------- net income (income-statement lane)
# The seed (concept_rules/is.jsonl) maps net income only from `NetIncomeLoss`. The IS lane's Verifier-passed slot rule
# (is_detect.net_income_slot, imported, never retyped) also serves two other printed lines, listed in
# is_not_extracted.md as "not expressible as a seed":
#   G1b  `ProfitLoss` when nothing printed on the IS/CI face takes a share away (no noncontrolling-interest line, no
#        preferred line): then the consolidated line is the parent's (ITW, Guidewire, Viatris);
#   G2b  `NetIncomeLossAvailableToCommonStockholdersBasic` when the face bridges `ProfitLoss` straight to it through
#        noncontrolling-interest lines only, with no parent preferred dividends before it (CAT, CF, Fox, Ball).
# Cohort dry run 41708119011: 25 companies had no net-income line mapped in ANY stored filing (no_mapped_line,
# 1,353 keys), most of them these two layouts. This detector is ADDITIVE: it acts only on a filing whose seed mapped
# no net-income line, so no line the seed serves today changes. G2b also needs the value tie the lane's replay ran:
# in every face column where all bridge lines print, ProfitLoss - NCI lines = the available-to-common line within
# rounding; one failing column, or no column to check, holds the filing (nothing mapped).
NI = "net_income_resolved"
NI_RULE = {
    "G1b_profit_loss_no_nci": "is.net_income_profit_loss_no_nci@1",
    "G2b_available_to_common_bridge": "is.net_income_available_to_common_bridge@1",
    "G2c_bottom_line_tie": "is.net_income_bottom_line_tie@1",
}


def _is_lane():
    if str(LANE_DIR) not in sys.path:
        sys.path.insert(0, str(LANE_DIR))
    import is_detect as lane  # noqa: PLC0415  (the lane module, imported, never copied)

    return lane


def is_face_rows(
    conn: psycopg.Connection, filing_id: int
) -> tuple[list[dict[str, Any]], bool]:
    """The lane's IS/CI face rows (fsn_is_pre.pre_record shape: parentheticals dropped) of one filing, and whether
    the filing is a combined (co-registrant) filing, which makes the lane pick the face that prints EPS."""
    with conn.cursor() as cur:
        cur.execute(
            "select coalesce(cardinality(aciks), 0) > 0 from fsn.filing where id = %s",
            (filing_id,),
        )
        row = cur.fetchone()
        if row is None:
            return [], False
        cur.execute(
            """select l.stmt, l.report, l.line, t.tag, t.custom, coalesce(l.plabel, ''), l.negating
               from fsn.line l join fsn.tag t on t.id = l.tag_id
               where l.filing_id = %s and l.stmt in ('IS', 'CI') and not l.inpth""",
            (filing_id,),
        )
        rows = [
            {
                "stmt": s,
                "report": r,
                "line": ln,
                "tag": t,
                "custom": bool(cu),
                "label": lab,
                "negating": bool(n),
            }
            for s, r, ln, t, cu, lab, n in cur.fetchall()
        ]
    rows.sort(key=lambda x: (x["report"], x["line"]))
    return rows, bool(row[0])


def face_values(
    conn: psycopg.Connection, filing_id: int, tags: list[str]
) -> dict[str, dict[str, tuple]]:
    """{ddate|qtrs: {tag: (value, dcml)}}: undimensioned USD duration prints of `tags`, primary registrant"""
    with conn.cursor() as cur:
        cur.execute(
            """select t.tag, v.ddate, v.qtrs, v.value, v.dcml
               from fsn.value v join fsn.tag t on t.id = v.tag_id
               where v.filing_id = %s and v.dim_id = 0 and v.uom = 'USD' and v.qtrs > 0 and v.iprx = 0 and v.coreg = ''
                 and v.value is not null and t.tag = any(%s)""",
            (filing_id, tags),
        )
        out: dict[str, dict[str, tuple]] = defaultdict(dict)
        for t, d, q, v, dc in cur.fetchall():
            out[f"{d:%Y%m%d}|{q}"][t] = (Decimal(v), dc)
    return dict(out)


def bridge_tie(
    slot: dict[str, Any], values: dict[str, dict[str, tuple]]
) -> dict[str, Any]:
    """G2b value tie per face column: ProfitLoss - sum(bridge lines) = available-to-common, within rounding.
    {"ok": bool, "checked": [cols], "failed": [{col, lhs, rhs, tol}]}"""
    from scrooner_pipeline.fsn_store.checks import tol_of  # noqa: PLC0415

    atc, pl, bridge = slot["tag"], slot["tie"]["profit_loss"], slot["tie"]["nci"]
    checked, failed = [], []
    for col, vals in sorted(values.items()):
        if atc not in vals or pl not in vals or any(b not in vals for b in bridge):
            continue
        lhs = vals[pl][0] - sum((vals[b][0] for b in bridge), Decimal(0))
        rhs = vals[atc][0]
        tol = tol_of([vals[pl][1], vals[atc][1], *(vals[b][1] for b in bridge)])
        checked.append(col)
        if abs(lhs - rhs) > tol:
            failed.append(
                {"col": col, "lhs": str(lhs), "rhs": str(rhs), "tol": str(tol)}
            )
    return {"ok": bool(checked) and not failed, "checked": checked, "failed": failed}


# G2c (new in the store, not a lane rule; Verifier sample pending): the face's bottom line. Where the face prints
# neither NetIncomeLoss nor ProfitLoss, no noncontrolling-interest line and no preferred line anywhere on IS/CI, the
# lane finds no printed net-income line (Booking, Monster, Watts, Hexcel print "Net income" under the available-to-
# common tag; AeroVironment under the continuing-operations-including-NCI tag). Then the last monetary line before
# the per-share block is the parent's net income IF, in every face column, it equals pretax - tax plus each line
# printed between the tax line and it (a line equal to the running total is a subtotal and is not added).
BOTTOM_TAGS = {
    "NetIncomeLossAvailableToCommonStockholdersBasic",
    "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest",
}
NET_LABEL = re.compile(
    r"\bnet (income|earnings|loss|\(loss\) income|income \(loss\)|\(loss\) earnings|earnings \(loss\))",
    re.I,
)
_PER_SHARE = re.compile(
    r"Per(Basic|Diluted|BasicAndDiluted)?Share|PerOutstanding|WeightedAverage|SharesOutstanding"
)
_PRETAX = re.compile(r"^IncomeLossFromContinuingOperationsBeforeIncomeTaxes")
_DISCONTINUED = re.compile(r"DiscontinuedOperation")


def bottom_line(
    face: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    values: dict[str, dict[str, tuple]],
) -> dict[str, Any]:
    """G2c on the lane's primary face. {"gate", "line", "tag", "label", "tie"}"""
    from scrooner_pipeline.fsn_store.checks import tol_of  # noqa: PLC0415

    lane = _is_lane()
    every = [r for r in rows if r["stmt"] in ("IS", "CI")]
    if any(r["tag"] in ("NetIncomeLoss", "ProfitLoss") for r in face):
        return {"gate": "hold_bottom_line_standard_line_printed"}
    # any line that takes a share of the income away from common holders of the parent disqualifies the face: a
    # standard NCI tag, a custom tag or a label naming noncontrolling / minority interests, or anything preferred.
    # (NCI_CUSTOM_RX is applied to custom tags only, as in the lane: standard pretax tags carry the word in their name)
    if any(
        (not r["custom"] and lane.NCI_RX.search(r["tag"]))
        or (
            r["custom"]
            and lane.NCI_CUSTOM_RX.search(r["tag"])
            and "Comprehensive" not in r["tag"]
        )
        or (lane.NCI_LABEL.search(r["label"]) and "Comprehensive" not in r["tag"])
        or lane.PREFERRED_TAG.search(r["tag"])
        or lane.PREFERRED_LABEL.search(r["label"])
        for r in every
    ):
        return {"gate": "hold_bottom_line_nci_or_preferred"}
    money = [
        r
        for r in face
        if not r["tag"].endswith("Abstract") and not _PER_SHARE.search(r["tag"])
    ]
    i_tax = next((i for i, r in enumerate(money) if r["tag"] == lane.TAX), None)
    i_pre = next((i for i, r in enumerate(money) if _PRETAX.search(r["tag"])), None)
    if i_tax is None or i_pre is None or i_pre > i_tax:
        return {"gate": "hold_bottom_line_no_pretax_and_tax"}
    after = money[i_tax + 1 :]
    # the bottom line: the last monetary line before the first per-share line of the face
    first_ps = next((r["line"] for r in face if _PER_SHARE.search(r["tag"])), None)
    if first_ps is None:
        return {"gate": "hold_bottom_line_no_per_share_block"}
    above = [r for r in after if r["line"] < first_ps]
    if not above:
        return {"gate": "hold_bottom_line_none"}
    cand, between = above[-1], above[:-1]
    out = {"line": cand["line"], "tag": cand["tag"], "label": cand["label"]}
    if (
        cand["tag"] not in BOTTOM_TAGS
        or cand["custom"]
        or not NET_LABEL.search(cand["label"])
    ):
        return {**out, "gate": "hold_bottom_line_not_a_net_income_line"}
    if cand["tag"] != "NetIncomeLossAvailableToCommonStockholdersBasic" and any(
        _DISCONTINUED.search(r["tag"]) for r in face
    ):
        return {**out, "gate": "hold_bottom_line_continuing_ops_with_discontinued"}
    pre, tax = money[i_pre]["tag"], lane.TAX
    checked, failed = [], []
    for col, vals in sorted(values.items()):
        if cand["tag"] not in vals:
            continue
        if pre not in vals or tax not in vals:
            failed.append({"col": col, "missing": "pretax or tax"})
            continue
        running, used = vals[pre][0] - vals[tax][0], [vals[pre][1], vals[tax][1]]
        for b in between:
            if b["tag"] not in vals:
                continue  # not printed in this column: adds nothing; the tie below must still hold
            v, dc = vals[b["tag"]]
            if abs(v - running) <= tol_of([*used, dc]):
                continue  # a printed subtotal (Hexcel "Income before equity in earnings")
            running += v
            used.append(dc)
        rhs, tol = vals[cand["tag"]][0], tol_of([*used, vals[cand["tag"]][1]])
        checked.append(col)
        if abs(running - rhs) > tol:
            failed.append(
                {"col": col, "lhs": str(running), "rhs": str(rhs), "tol": str(tol)}
            )
    tie = {"ok": bool(checked) and not failed, "checked": checked, "failed": failed}
    if not tie["ok"]:
        return {
            **out,
            "gate": "hold_bottom_line_tie_" + ("failed" if failed else "uncheckable"),
            "tie": tie,
        }
    return {**out, "gate": "G2c_bottom_line_tie", "tie": tie}


def decide_net_income(
    rows: list[dict[str, Any]],
    coregistrant: bool,
    values: dict[str, dict[str, tuple]] | None,
) -> dict[str, Any]:
    """The lane's net-income slot for one filing's IS/CI rows, plus the G2b value tie, then G2c.
    {"status": "mapped"|"held", "gate", "report", "line", "tag", ...}"""
    lane = _is_lane()
    rep, face = lane.primary_face(rows, coregistrant)
    if not face:
        return {"status": "held", "gate": "no_income_statement_face"}
    slot = lane.net_income_slot(face, rows)
    gate = slot.get("gate")
    out = {
        "gate": gate,
        "report": rep,
        "line": slot.get("line"),
        "tag": slot.get("tag"),
    }
    if gate == "no_printed_net_income_line":
        b = bottom_line(face, rows, values or {})
        out = {**out, **b, "lane_gate": gate}
        if b["gate"] == "G2c_bottom_line_tie":
            return {**out, "status": "mapped", "rule_id": NI_RULE[b["gate"]]}
        return {**out, "status": "held"}
    if gate not in NI_RULE:
        return {**out, "status": "held"}
    if gate == "G2b_available_to_common_bridge":
        tie = bridge_tie(slot, values or {})
        out["tie"] = tie
        if not tie["ok"]:
            return {
                **out,
                "status": "held",
                "gate": "hold_bridge_tie_"
                + ("failed" if tie["failed"] else "uncheckable"),
            }
    return {**out, "status": "mapped", "rule_id": NI_RULE[gate]}


def net_income_detector(
    conn: psycopg.Connection, filing_id: int, decisions: list[tuple]
) -> list[tuple]:
    """FORMATS-v1.1 detector: maps the lane's G1b / G2b net-income line of a filing whose seed mapped none."""
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (NI,))
        row = cur.fetchone()
    if row is None:
        return []
    ni_id = row[0]
    if any(d[3] == ni_id and d[4] in ("mapped", "combined") for d in decisions):
        return []  # additive: the seed already serves this filing's net income
    rows, coreg = is_face_rows(conn, filing_id)
    if not rows:
        return []
    lane = _is_lane()
    _, face = lane.primary_face(rows, coreg)
    tags = sorted({r["tag"] for r in face})
    dec = decide_net_income(rows, coreg, face_values(conn, filing_id, tags))
    if dec["status"] != "mapped":
        return []
    current = {(d[1], d[2]): d for d in decisions}
    seen = current.get((dec["report"], dec["line"]))
    if seen is None or seen[4] != "unmapped":
        return []  # only an unmapped IS line is ever mapped here (never a line another rule or detector owns)
    return [
        (
            filing_id,
            dec["report"],
            dec["line"],
            ni_id,
            "mapped",
            dec["rule_id"],
            None,
            {
                "detector": "is_net_income",
                "tag": dec["tag"],
                "gate": dec["gate"],
                "tie_columns": (dec.get("tie") or {}).get("checked"),
            },
        )
    ]


def _pretax(
    conn: psycopg.Connection, filing_id: int, decisions: list[tuple]
) -> list[tuple]:
    from scrooner_pipeline.fsn_store.is_structure import pretax_detector  # noqa: PLC0415  (imports this module)

    return pretax_detector(conn, filing_id, decisions)


DEFAULT = [capex_da_detector, net_income_detector, _pretax]
