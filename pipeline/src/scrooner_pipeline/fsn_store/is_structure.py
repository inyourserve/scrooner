"""Income-statement lines mapped by the filing's own structure, not by tag name (xbrl-structure skill).

A slot is found by POSITION relative to an anchor line the seed already maps (the income-tax line), a LABEL class,
and a VALUE TIE on the filing's own prints in every face column (rounding only). A tag name is never enough: the
same line is printed under a custom tag (MCD "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"), a domestic-only
tag (ES, NI, ZION: ...BeforeIncomeTaxesDomestic) or another concept's tag (ITW, PG, CVNA: IncomeLossIncludingPortion-
AttributableToNoncontrollingInterest; TPG: IncomeLossAttributableToParent), and each of those tags means something
else at other filers (data-team/tags/cards/net-income-and-shares.md sec. 5).

Detectors here follow FORMATS-v1.1: additive (they act only where the seed mapped no line to the concept in the
filing) and they map only a line the seed left unmapped, so no line another rule serves changes.

Slot `pretax` (cohort dry run 41708119011: 39 companies, 1,987 keys with no pre-tax line mapped in any filing):
the monetary line printed directly above the income-tax line, labelled "before (income) tax(es)" / "pre-tax", where
in every face column that prints it the next monetary line after the tax line equals it minus tax.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import psycopg

from scrooner_pipeline.fsn_store import detectors as det

PRETAX = "income_before_tax_resolved"
PRETAX_RULE = "is.pretax_above_tax_line_tie@1"
TAX_TAG = "IncomeTaxExpenseBenefit"
BEFORE_TAX = re.compile(
    r"before (provision for |\(?provision\)? ?for |benefit from |\(benefit\) |)?(income )?tax|pre-?tax",
    re.I,
)
NOT_PRETAX = re.compile(
    r"discontinued|non-?controlling|minority|per share|comprehensive", re.I
)


def money_lines(face: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """the face's monetary lines in print order: no abstract headers, no per-share or share-count lines"""
    return [
        r
        for r in face
        if not r["tag"].endswith("Abstract") and not det._PER_SHARE.search(r["tag"])
    ]


def column_tie(
    values: dict[str, dict[str, tuple]], lhs: list[tuple[str, int]], rhs: str
) -> dict[str, Any]:
    """per column: sum(sign * value of lhs tags) = value of rhs, within the rounding of every print used.
    Columns where an lhs tag or rhs does not print are skipped. ok = at least one column checked, none failed."""
    from scrooner_pipeline.fsn_store.checks import tol_of  # noqa: PLC0415

    checked, failed = [], []
    for col, vals in sorted(values.items()):
        if rhs not in vals or any(t not in vals for t, _ in lhs):
            continue
        total = sum((s * vals[t][0] for t, s in lhs), Decimal(0))
        tol = tol_of([*(vals[t][1] for t, _ in lhs), vals[rhs][1]])
        checked.append(col)
        if abs(total - vals[rhs][0]) > tol:
            failed.append(
                {
                    "col": col,
                    "lhs": str(total),
                    "rhs": str(vals[rhs][0]),
                    "tol": str(tol),
                }
            )
    return {"ok": bool(checked) and not failed, "checked": checked, "failed": failed}


def pretax_slot(
    face: list[dict[str, Any]], values: dict[str, dict[str, tuple]]
) -> dict[str, Any]:
    """{"status": "mapped"|"held", "gate", "line", "tag", "label", "tie"}"""
    money = money_lines(face)
    i_tax = next((i for i, r in enumerate(money) if r["tag"] == TAX_TAG), None)
    if i_tax is None or i_tax == 0:
        return {"status": "held", "gate": "hold_pretax_no_tax_line"}
    cand = money[i_tax - 1]
    out = {
        "line": cand["line"],
        "tag": cand["tag"],
        "label": cand["label"],
        "custom": cand["custom"],
    }
    if not BEFORE_TAX.search(cand["label"]) or NOT_PRETAX.search(cand["label"]):
        return {**out, "status": "held", "gate": "hold_pretax_label_not_before_tax"}
    if i_tax + 1 >= len(money):
        return {**out, "status": "held", "gate": "hold_pretax_no_line_after_tax"}
    after = money[i_tax + 1]
    if after["tag"] == cand["tag"]:
        return {**out, "status": "held", "gate": "hold_pretax_same_tag_after_tax"}
    tie = column_tie(values, [(cand["tag"], 1), (TAX_TAG, -1)], after["tag"])
    out["tie"] = {**tie, "after": after["tag"]}
    if not tie["ok"]:
        return {
            **out,
            "status": "held",
            "gate": "hold_pretax_tie_" + ("failed" if tie["failed"] else "uncheckable"),
        }
    return {
        **out,
        "status": "mapped",
        "gate": "P1_above_tax_line_tie",
        "rule_id": PRETAX_RULE,
    }


def pretax_detector(
    conn: psycopg.Connection, filing_id: int, decisions: list[tuple]
) -> list[tuple]:
    """FORMATS-v1.1 detector: maps the pre-tax line of a filing whose seed mapped none (see pretax_slot)."""
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (PRETAX,)
        )
        row = cur.fetchone()
    if row is None:
        return []
    cid = row[0]
    if any(d[3] == cid and d[4] in ("mapped", "combined") for d in decisions):
        return []  # additive
    rows, coreg = det.is_face_rows(conn, filing_id)
    if not rows:
        return []
    rep, face = det._is_lane().primary_face(rows, coreg)
    if not face:
        return []
    slot = pretax_slot(
        face, det.face_values(conn, filing_id, sorted({r["tag"] for r in face}))
    )
    if slot["status"] != "mapped":
        return []
    seen = {(d[1], d[2]): d for d in decisions}.get((rep, slot["line"]))
    if seen is None or seen[4] != "unmapped":
        return []  # never re-map a line another rule or detector owns (AFG prints pretax under OperatingIncomeLoss)
    return [
        (
            filing_id,
            rep,
            slot["line"],
            cid,
            "mapped",
            slot["rule_id"],
            None,
            {
                "detector": "is_structure.pretax",
                "tag": slot["tag"],
                "custom": slot["custom"],
                "gate": slot["gate"],
                "tie_columns": slot["tie"]["checked"],
                "tie_after": slot["tie"]["after"],
            },
        )
    ]
