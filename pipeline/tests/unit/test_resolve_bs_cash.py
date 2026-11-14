"""Cash = the balance-sheet face total labelled cash and cash equivalents (ruling 2026-11-14, AXP 2023: 46,596, not CashAndDueFromBanks 7,118).
data-team/tags/line_map/tools/resolve_bs.py cash_subtotal: a picked component climbs to its face calc parent while that parent's own label is
'(Total) cash and cash equivalents'; a total that names other items (short-term investments, restricted cash) is not cash."""

from __future__ import annotations

import sys
from decimal import Decimal as D
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[3] / "data-team" / "tags" / "line_map" / "tools"
sys.path.insert(0, str(TOOLS))
import resolve_bs as B  # noqa: E402

pytestmark = pytest.mark.unit


def _l(tag, val, lb, ln):
    return dict(tag=tag, val=D(val), lb=lb, ln=ln, rep=6, custom=False)


def _axp(total_label):
    lines = [_l("CashAndDueFromBanks", 7118, "Cash and due from banks", 10), _l("InterestBearingDepositsInBanks", 39478, "Interest-bearing deposits in other banks", 11),
             _l("ShortTermInvestments", 0, "Short-term investment securities", 12),
             _l("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", 46596, total_label, 13)]
    arcs = {"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": {"g": [("CashAndDueFromBanks", 1), ("InterestBearingDepositsInBanks", 1), ("ShortTermInvestments", 1)]}}
    return lines, arcs


def test_component_climbs_to_the_face_total_labelled_cash_and_cash_equivalents():
    lines, arcs = _axp("Total cash and cash equivalents")
    r = B.pick(B.ROLES["cash_and_equivalents"], lines, {}, "cash_and_equivalents")
    assert r["value"] == D(7118)                       # the tag rank alone picks the first component
    out = B.cash_subtotal(r, lines, arcs)
    assert out["value"] == D(46596) and out["nodes"].startswith("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents=46596 [R6.htm:13]")
    assert out["flags"] == "cash_face_subtotal"
    p = B.cash_subtotal(r, *_axp("Total cash and cash equivalents (includes restricted cash: 2"))
    assert p["value"] == D(46596) and "label_parenthetical" in p["flags"]


def test_a_total_that_names_other_items_or_no_calc_arc_keeps_the_pick():
    r = B.pick(B.ROLES["cash_and_equivalents"], *_axp("x")[:1], {}, "cash_and_equivalents")
    for lb in ("Total cash, cash equivalents and short-term investments", "Total cash, cash equivalents, and marketable securities"):
        lines, arcs = _axp(lb)
        assert B.cash_subtotal(r, lines, arcs) is r
    lines, _ = _axp("Total cash and cash equivalents")
    assert B.cash_subtotal(r, lines, {}) is r


def test_restricted_inclusive_total_is_the_cell_when_the_face_has_no_cash_total():
    # ruling 2026-11-14 (WFC 2019-22, PGR 2017-25; as GE, INTC, PG): mapped, flagged includes_restricted
    r = B.pick(B.ROLES["cash_and_equivalents"], *_axp("x")[:1], {}, "cash_and_equivalents")
    for lb in ("Total cash, cash equivalents, and restricted cash", "Total cash, cash equivalents, restricted cash, and restricte"):
        out = B.cash_subtotal(r, *_axp(lb))
        assert out["value"] == D(46596) and out["status"] == "mapped" and "includes_restricted" in out["flags"]
    # a cash-and-cash-equivalents total printed elsewhere on the face wins: the restricted-inclusive parent is not climbed
    lines, arcs = _axp("Total cash, cash equivalents, and restricted cash")
    lines.append(_l("CashAndCashEquivalentsAtCarryingValue", 46000, "Cash and cash equivalents", 20))
    assert B.cash_subtotal(r, lines, arcs) is r


def test_climbs_every_level_and_refuses_two_candidate_parents():
    lines, arcs = _axp("Cash and cash equivalents")
    lines.append(_l("CashAndCashEquivalentsAtCarryingValue", 46600, "Total cash and cash equivalents", 15))
    lines.append(_l("OtherCash", 4, "Other", 14))
    arcs["CashAndCashEquivalentsAtCarryingValue"] = {"g": [("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", 1), ("OtherCash", 1)]}
    r = B.pick(B.ROLES["cash_and_equivalents"], lines[:1], {}, "cash_and_equivalents")
    out = B.cash_subtotal(r, lines, arcs)
    assert out["value"] == D(46600) and "CashAndDueFromBanks, CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents" in out["why"]
    lines, arcs = _axp("Total cash and cash equivalents")
    lines.append(_l("CashAndCashEquivalentsAtCarryingValue", 7118, "Cash and cash equivalents", 9))
    arcs["CashAndCashEquivalentsAtCarryingValue"] = {"g": [("CashAndDueFromBanks", 1)]}
    assert B.cash_subtotal(r, lines, arcs) is r          # two labelled parents: ambiguous, the pick stands
