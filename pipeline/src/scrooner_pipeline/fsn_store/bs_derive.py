"""Balance-sheet cells the face does not print as one line, from the SAME accession only (never invented).

total_liabilities_resolved, for a filing whose balance sheet prints no total-liabilities line:
  * calc route (`fsn.derive_total_liabilities_calc@1`): the filing's own calculation arcs give
    L&E = sum(weight * child). Each child is classed by the balance-sheet lane's own line classifier
    (bs_totals_detect.classify_line, imported): liability / equity / NCI / temporary equity. A capitalization
    subtotal (utilities: equity + long-term debt) is expanded through its own arcs. Published only when every
    valued child sums to the printed L&E in that column (tolerance = the filer's rounding unit) and at least one
    liability and one equity child are valued. Value = sum(weight * liability children).
  * identity route (`fsn.derive_total_liabilities_identity@1`), only when no calc arcs exist under L&E:
    L&E - total equity (including NCI) - temporary equity, every term a printed face line of the same column,
    with no NCI line printed outside the equity total and every temporary-equity line valued.
current_assets_resolved / current_liabilities_resolved, for a filing whose balance sheet has no current
section at all (no AssetsCurrent / LiabilitiesCurrent element and no printed "total current" line): a
`not_presented` cell `unclassified_balance_sheet` (banks, insurers, REITs, broker-dealers), with the
accession and the face as evidence.
Candidates follow fsn_store.select: a face column of the filing (the BS anchor total valued, the column length
belonging to the form), every check of the column passing, the LATEST accepted filing wins and is never replaced
by an older copy (if the derivation fails on the latest copy, no cell is produced).
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.fsn_store import select as sel

LANE_DIR = Path(__file__).resolve().parents[3] / "scripts" / "slot_records"
TL, CA, CL = (
    "total_liabilities_resolved",
    "current_assets_resolved",
    "current_liabilities_resolved",
)
LE_TAGS = ("LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital")
RULE_CALC = "fsn.derive_total_liabilities_calc@1"
RULE_IDENTITY = "fsn.derive_total_liabilities_identity@1"
RULE_UNCLASSIFIED = "fsn.unclassified_balance_sheet@1"
EQUITY_INCL = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    "PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest",
)
CURRENT_LABEL = re.compile(r"total current (assets|liabilities)", re.I)
REASON = "unclassified_balance_sheet"
REASON_TL = "total_liabilities_not_printed"
RULE_TL_NOT_PRINTED = "fsn.total_liabilities_not_printed@1"
REASON_TEXT = "The balance sheet is not split into current and non-current sections, so no current total is printed."


def _classify():
    if str(LANE_DIR) not in sys.path:
        sys.path.insert(0, str(LANE_DIR))
    import bs_totals_detect  # noqa: PLC0415  (the lane's classifier, imported, never copied)

    return bs_totals_detect.classify_line


MEZZ_WORDS = re.compile(r"redeemable|temporary", re.IGNORECASE)
LIABILITY_WORDS = re.compile(
    r"mandatorily", re.IGNORECASE
)  # ASC 480 mandatorily redeemable: a liability
EQUITY_SEGS = ("equity_total", "equity_component", "nci")


def segments(face: list[dict], classify) -> dict[str, str]:
    """tag -> the BS lane's segment, with one positional override (Verifier, KMB 2024-03-31): a Redeemable* /
    Temporary* line the lane classes `liab` that sits after the last other liability line and before the first equity
    line (outside any printed total liabilities) is temporary equity, `mezz`; "mandatorily redeemable" stays a liability."""
    seg = {f["tag"]: classify(f["tag"], f["label"]) for f in face}
    order = [f for f in face if f["tag"] in seg]
    first_eq = next(
        (i for i, f in enumerate(order) if seg[f["tag"]] in EQUITY_SEGS), None
    )
    if first_eq is None:
        return seg

    def mezz_like(f):
        text = f"{f['tag']} {f['label'] or ''}"
        return bool(MEZZ_WORDS.search(text)) and not LIABILITY_WORDS.search(text)

    i = first_eq - 1
    while i >= 0 and (seg[order[i]["tag"]] != "liab" or mezz_like(order[i])):
        f = order[i]
        if seg[f["tag"]] == "liab":
            seg[f["tag"]] = "mezz"
        i -= 1
    return seg


def _unit(values) -> Decimal:
    unit = Decimal(1000000)
    for v in values:
        while unit > 1 and v != 0 and v % unit != 0:
            unit /= 10
    return unit


def derive_tl(
    face: list[dict],
    arcs: dict[str, list[tuple[str, int]]],
    col: dict[str, tuple[Decimal, int]],
):
    """(value, rule_id, inputs) for one filing column, or (None, reason, {}). face: ordered BS lines
    {tag, label, custom}; arcs: parent -> [(child, weight)] of the filing's BS calc; col: tag -> (value, value_id)."""
    classify = _classify()
    tags = {f["tag"] for f in face}
    if "Liabilities" in tags:
        return None, "printed_total_liabilities", {}
    le = next((t for t in LE_TAGS if t in tags and t in col), None)
    if le is None:
        return None, "no_printed_le_total", {}
    label = {f["tag"]: f["label"] for f in face}
    face_seg = segments(face, classify)

    def seg_of(c):
        return face_seg.get(c) or classify(c, label.get(c, ""))

    if arcs.get(le):
        leaves: list[tuple[str, int]] = []
        stack = [(c, w) for c, w in arcs[le]]
        while stack:
            c, w = stack.pop(0)
            seg = seg_of(c)
            if seg == "excluded_cap_total" and arcs.get(c):
                stack = [(cc, w * ww) for cc, ww in arcs[c]] + stack
                continue
            leaves.append((c, w))
        parts: dict[str, list] = defaultdict(list)
        total = Decimal(0)
        blank: list[str] = []
        for c, w in leaves:
            seg = seg_of(c)
            v = col.get(c)
            if v is None:
                # a line printed blank in this column carries no fact: it counts as zero ONLY if the valued children
                # still tie to the printed L&E below (the BS lane's rule, Verifier BS-V2 fix 3)
                blank.append(c)
                continue
            if seg == "excluded_total_or_noise":
                if v[0] == 0:  # CommitmentsAndContingencies printed as a dash / 0
                    continue
                return None, f"calc_child_noise_valued:{c}", {}
            if seg in ("equity_total", "equity_component", "nci"):
                parts["equity"].append((c, w, v))
            elif seg == "mezz":
                parts["mezz"].append((c, w, v))
            elif seg == "liab":
                parts["liab"].append((c, w, v))
            else:
                return None, f"calc_child_unclassified:{c}:{seg}", {}
            total += w * v[0]
        if not parts["liab"] or not parts["equity"]:
            return None, "calc_children_lack_liability_or_equity", {}
        if abs(total - col[le][0]) > _unit([v[0] for v in col.values()]):
            return None, "calc_children_do_not_tie_le", {}
        value = sum((w * v[0] for _c, w, v in parts["liab"]), Decimal(0))
        inputs = {
            "le": [le, str(col[le][0])],
            **{k: [[c, w, str(v[0])] for c, w, v in xs] for k, xs in parts.items()},
            "blank_children": blank,
        }
        ids = [col[le][1]] + [v[1] for xs in parts.values() for _c, _w, v in xs]
        return (value, ids), RULE_CALC, inputs
    # identity route: no calc arcs under L&E in this filing
    eq = next((t for t in EQUITY_INCL if t in tags and t in col), None)
    nci_lines = [f["tag"] for f in face if face_seg[f["tag"]] == "nci"]
    if eq is None:
        if (
            nci_lines
            or "StockholdersEquity" not in tags
            or "StockholdersEquity" not in col
        ):
            return None, "identity_equity_total_not_printed", {}
        eq = "StockholdersEquity"
    mezz = [f["tag"] for f in face if face_seg[f["tag"]] == "mezz"]
    if any(m not in col for m in mezz):
        return None, "identity_temporary_equity_not_valued", {}
    value = col[le][0] - col[eq][0] - sum((col[m][0] for m in mezz), Decimal(0))
    if value <= 0:
        return None, "identity_non_positive", {}
    inputs = {
        "le": [le, str(col[le][0])],
        "equity": [eq, str(col[eq][0])],
        "mezz": [[m, str(col[m][0])] for m in mezz],
    }
    return (
        (value, [col[le][1], col[eq][1]] + [col[m][1] for m in mezz]),
        RULE_IDENTITY,
        inputs,
    )


def unclassified(face: list[dict]) -> bool:
    tags = {f["tag"] for f in face}
    return not ({"AssetsCurrent", "LiabilitiesCurrent"} & tags) and not any(
        CURRENT_LABEL.search(f["label"] or "") for f in face
    )


def current_reason(face: list[dict], current_in_filing: bool) -> str | None:
    """REASON when the balance sheet is unclassified and no statement of the same filing prints a current total;
    else None (the miss is counted, never reasoned)"""
    if not unclassified(face):
        return None
    return None if current_in_filing else REASON


def load(conn: psycopg.Connection, company_id: int) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, accession, accepted, form, period, fy, fp, fye from fsn.filing where company_id = %s",
            (company_id,),
        )
        filings = {r[0]: sel.Filing(*r) for r in cur.fetchall()}
        cur.execute(
            """select l.filing_id, l.report, l.line, t.tag, coalesce(l.plabel, ''), t.custom
               from fsn.line l join fsn.tag t on t.id = l.tag_id join fsn.filing f on f.id = l.filing_id
               where f.company_id = %s and l.stmt = 'BS' and not l.inpth order by 1, 2, 3""",
            (company_id,),
        )
        face: dict[int, list[dict]] = defaultdict(list)
        for fid, _r, _ln, tag, lab, cu in cur.fetchall():
            face[fid].append({"tag": tag, "label": lab, "custom": cu})
        cur.execute(
            """select a.filing_id, a.grp, p.tag, c.tag, a.weight from fsn.calc_arc a
               join fsn.tag p on p.id = a.parent_tag_id join fsn.tag c on c.id = a.child_tag_id
               join fsn.filing f on f.id = a.filing_id where f.company_id = %s""",
            (company_id,),
        )
        groups: dict[int, dict[int, list]] = defaultdict(lambda: defaultdict(list))
        for fid, grp, p, c, w in cur.fetchall():
            groups[fid][grp].append((p, c, w))
        cur.execute(
            """select v.id, v.filing_id, t.tag, v.ddate, v.value from fsn.value v join fsn.tag t on t.id = v.tag_id
               where v.company_id = %s and v.qtrs = 0 and v.dim_id = 0 and v.iprx = 0 and v.coreg = '' and v.uom = 'USD'
                 and v.value is not null""",
            (company_id,),
        )
        vals: dict[tuple[int, Any], dict[str, tuple[Decimal, int]]] = defaultdict(dict)
        for vid, fid, tag, d, v in cur.fetchall():
            vals[(fid, d)][tag] = (Decimal(v), vid)
        cur.execute(
            """select distinct fc.filing_id, fc.ddate from fsn.filing_check fc join fsn.filing f on f.id = fc.filing_id
               where f.company_id = %s and fc.stmt = 'BS' and not fc.ok""",
            (company_id,),
        )
        failed = set(cur.fetchall())
        # a current total printed in ANY statement of the filing (e.g. Planet Fitness 2015: the registrant shell's
        # balance sheet is stmt BS, the operating predecessor's classified one is filed as stmt UN) means the
        # company does classify: never reason it away as unclassified
        cur.execute(
            """select distinct l.filing_id from fsn.line l join fsn.tag t on t.id = l.tag_id
               join fsn.filing f on f.id = l.filing_id
               where f.company_id = %s and not l.inpth and t.tag in ('AssetsCurrent', 'LiabilitiesCurrent')""",
            (company_id,),
        )
        current_elsewhere = {r[0] for r in cur.fetchall()}
    return {
        "filings": filings,
        "face": face,
        "groups": groups,
        "vals": vals,
        "failed": failed,
        "current_elsewhere": current_elsewhere,
    }


def bs_arcs(
    groups: dict[int, list], face_tags: set[str]
) -> dict[str, list[tuple[str, int]]]:
    """the BS calc group: the group whose parents include the L&E total, most arcs on the face"""
    best = None
    for g, arcs in groups.items():
        parents = {p for p, _c, _w in arcs}
        if not parents & set(LE_TAGS):
            continue
        score = (
            sum(1 for p, c, _w in arcs if p in face_tags and c in face_tags),
            len(arcs),
        )
        if best is None or score > best[0]:
            best = (score, arcs)
    out: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for p, c, w in best[1] if best else []:
        out[p].append((c, int(w)))
    return out


def tl_cell(
    dd, fid: int, accession: str, res, rule: str, inputs: dict
) -> "sel.Cell | None":
    """The total-liabilities cell of one face column whose face prints no total-liabilities line:
    not_presented, reason total_liabilities_not_printed. Doc 02 (decisions 2026-11-04, items 4 and 6): instants are
    never derived, so the calc-tree / L&E-identity check is kept only as evidence of whether the printed lines are
    complete (input_refs.check), never as a served value (Dhairya 2026-11-12). None when the face prints its own
    total: that cell comes from select."""
    if res is None and rule == "printed_total_liabilities":
        return None
    check = (
        rule
        if res is None
        else (
            "calc_children_tie_le" if rule == RULE_CALC else "le_identity_terms_printed"
        )
    )
    return sel.Cell(
        TL,
        dd,
        0,
        "not_presented",
        filing_id=fid,
        rule_id=RULE_TL_NOT_PRINTED,
        reason_code=REASON_TL,
        input_refs={"accession": accession, "check": check},
    )


def rows(
    conn: psycopg.Connection, company_id: int, have: set[tuple[str, Any]]
) -> tuple[list[dict], dict]:
    """CELL-FORMAT rows (sel.to_row) for keys (concept, fsn_end date) not in `have`, and a per-reason count of the
    latest-copy columns where total liabilities could not be derived."""
    d = load(conn, company_id)
    by_col: dict[Any, list[tuple]] = defaultdict(
        list
    )  # ddate -> [(accepted, fid)] filings printing the BS column
    for (fid, dd), col in d["vals"].items():
        f = d["filings"].get(fid)
        if f is None or not d["face"].get(fid):
            continue
        face_tags = {x["tag"] for x in d["face"][fid]}
        # a FACE column: the balance sheet's own closing total is valued at the date (L&E prints on the face, not
        # in segment notes; Assets only when the face has no L&E line). Segment-split faces (homebuilders,
        # conglomerates) carry most lines per member, so a "most lines valued" test would wrongly reject them.
        closing = [t for t in LE_TAGS if t in face_tags] or ["Assets"]
        if any(t in col for t in closing) and (fid, dd) not in d["failed"]:
            by_col[dd].append((f.accepted, fid))
    out, misses = [], defaultdict(int)
    for dd, cands in by_col.items():
        _acc, fid = max(
            cands, key=lambda x: (x[0] is not None, x[0])
        )  # the latest accepted copy decides
        face, col = d["face"][fid], d["vals"][(fid, dd)]
        if (TL, dd) not in have:
            res, rule, inputs = derive_tl(
                face, bs_arcs(d["groups"][fid], {x["tag"] for x in face}), col
            )
            if res is None:
                misses[rule] += 1
            cell = tl_cell(dd, fid, d["filings"][fid].accession, res, rule, inputs)
            if cell is not None:
                out.append(cell)
        if unclassified(face) and fid in d["current_elsewhere"]:
            misses["current_total_in_another_statement"] += 1
        if current_reason(face, fid in d["current_elsewhere"]):
            for concept in (CA, CL):
                if (concept, dd) not in have:
                    out.append(
                        sel.Cell(
                            concept,
                            dd,
                            0,
                            "not_presented",
                            filing_id=fid,
                            rule_id=RULE_UNCLASSIFIED,
                            reason_code=REASON,
                            input_refs={
                                "accession": d["filings"][fid].accession,
                                "face_lines": len(face),
                            },
                        )
                    )
    return [sel.to_row(c, company_id, d["filings"]) for c in out], dict(misses)
