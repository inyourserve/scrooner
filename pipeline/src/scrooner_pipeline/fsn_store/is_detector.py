"""Income-statement net-income detector for `mapping.map_filing(..., detectors=[...])` (FORMATS-v1.1 hook).

The income-statement seed (data-team/47-fsn-store/concept_rules/is.jsonl) maps only the unconditional standard tag
NetIncomeLoss. Two Verifier-passed lane rules are conditional on the filing's own face and so stay out of the seed
(concept_rules/is_not_extracted.md); this detector runs them per filing by importing the lane's own code
(pipeline/scripts/slot_records/is_detect.py: primary_face, net_income_slot, never retyped):

* G1b  ProfitLoss is the parent's net income when the face prints no NetIncomeLoss line and nothing below
       ProfitLoss takes a share (no noncontrolling-interest line on IS/CI, no preferred line below it).
       MA ("Net Income" tagged ProfitLoss, EPS computed on it), OSK.
* G2b  the face bridges ProfitLoss straight to "net income attributable to <parent>" tagged
       NetIncomeLossAvailableToCommonStockholdersBasic through noncontrolling / subsidiary-preferred lines only;
       then that line is the parent's net income. ELS (OP-unit NCI), ETR / ES combined utility filings.
* alt  when the face prints NetIncomeLoss but that tag has no undimensioned primary-registrant value in the filing
       (Exelon's combined filings: NetIncomeLoss is only the subsidiaries' member columns) and the G2b bridge holds,
       the bridge line is mapped instead and the NetIncomeLoss line is unmapped (lane: net_income_slot "alt").

Every other gate leaves the seed's decision untouched (the lane's holds on a printed NetIncomeLoss line are not
ported here). Queue item 2026-11-09 (income-statement quarters missing; MA, PNC, EXC, ELS, OSK).
"""

from __future__ import annotations

import sys
from typing import Any

import psycopg

from scrooner_pipeline.fsn_store.detectors import LANE_DIR

NI = "net_income_resolved"
RULE_G1B = "is.net_income_profit_loss_no_nci@1"
RULE_G2B = "is.net_income_available_to_common_bridge@1"
RULE_ALT_OFF = "is.net_income_line_no_parent_value@1"


def _lane():
    if str(LANE_DIR) not in sys.path:
        sys.path.insert(0, str(LANE_DIR))
    import is_detect

    return is_detect


def face_rows(
    conn: psycopg.Connection, filing_id: int
) -> tuple[list[dict[str, Any]], bool]:
    """The lane's IS/CI face rows (fsn_is_pre.pre_record shape) of one filing, and whether it is a combined
    (co-registrant) filing."""
    with conn.cursor() as cur:
        cur.execute("select aciks from fsn.filing where id = %s", (filing_id,))
        row = cur.fetchone()
        if row is None:
            return [], False
        cur.execute(
            """select l.stmt, l.report, l.line, t.tag, coalesce(l.plabel, ''), t.custom
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
                "label": lab,
                "custom": bool(cu),
            }
            for s, r, ln, t, lab, cu in cur.fetchall()
        ]
    return rows, bool(row[0])


def decide(
    rows: list[dict[str, Any]], coregistrant: bool, has_parent_value: Any
) -> dict[str, Any] | None:
    """{action, report, line, tag, rule_id, gate[, off]} for one filing, or None (the seed stands).
    `has_parent_value(tag)` says whether the filing has an undimensioned primary-registrant value of the tag."""
    lane = _lane()
    rep, face = lane.primary_face(rows, coregistrant)
    if not face:
        return None
    slot = lane.net_income_slot(face, rows)
    gate = slot.get("gate")
    if gate == "G1b_profit_loss_no_nci":
        return {
            "report": rep,
            "line": slot["line"],
            "tag": slot["tag"],
            "rule_id": RULE_G1B,
            "gate": gate,
        }
    if gate == "G2b_available_to_common_bridge":
        return {
            "report": rep,
            "line": slot["line"],
            "tag": slot["tag"],
            "rule_id": RULE_G2B,
            "gate": gate,
            "tie": slot.get("tie"),
        }
    alt = slot.get("alt")
    if (
        alt
        and gate in ("G1_printed_line", "G2_nci_identity")
        and not has_parent_value(slot["tag"])
    ):
        return {
            "report": rep,
            "line": alt["line"],
            "tag": alt["tag"],
            "rule_id": RULE_G2B,
            "gate": "G2b_alt_no_parent_value",
            "tie": alt.get("tie"),
            "off": {"report": rep, "line": slot["line"], "tag": slot["tag"]},
        }
    return None


def is_net_income_detector(
    conn: psycopg.Connection, filing_id: int, decisions: list[tuple]
) -> list[tuple]:
    """FORMATS-v1.1 detector: overrides (filing_id, report, line, concept_id, status, rule_id, era, evidence)."""
    rows, coreg = face_rows(conn, filing_id)
    if not rows:
        return []
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (NI,))
        r = cur.fetchone()
        if r is None:
            return []
        ni_id = r[0]

    def has_parent_value(tag: str) -> bool:
        return (
            conn.execute(
                """select 1 from fsn.value v join fsn.tag t on t.id = v.tag_id
               where v.filing_id = %s and t.tag = %s and v.dim_id = 0 and v.coreg = '' and v.iprx = 0
                 and v.value is not null limit 1""",
                (filing_id, tag),
            ).fetchone()
            is not None
        )

    d = decide(rows, coreg, has_parent_value)
    if d is None:
        return []
    known = {(x[1], x[2]) for x in decisions}
    if (
        d["report"],
        d["line"],
    ) not in known:  # a CI-only face: map_filing decides IS/BS/CF lines only
        return []
    out = []
    ev = {
        "detector": "is_net_income",
        "gate": d["gate"],
        "tag": d["tag"],
        "tie": d.get("tie"),
    }
    # one NI line per filing: any other line the seed mapped to NI is unmapped with the reason
    for x in decisions:
        if (
            x[3] == ni_id
            and x[4] == "mapped"
            and (x[1], x[2]) != (d["report"], d["line"])
        ):
            out.append(
                (
                    filing_id,
                    x[1],
                    x[2],
                    None,
                    "unmapped",
                    RULE_ALT_OFF if d.get("off") else d["rule_id"],
                    None,
                    {
                        "detector": "is_net_income",
                        "concept": NI,
                        "held": [d["gate"]],
                        "tag": (x[7] or {}).get("tag"),
                    },
                )
            )
    out.append(
        (filing_id, d["report"], d["line"], ni_id, "mapped", d["rule_id"], None, ev)
    )
    return out
