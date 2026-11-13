"""R05 (component tolerance) and R16 (bank operating expenses) of the cell-proof ruling audit."""

from __future__ import annotations

from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import NumValue, PreLine

from tests.unit.test_cell_proof import ADSH, DDATE, FY_END, structure


def _debt_world(parts, dcml=-6):
    s = structure()
    for i, (tag, v) in enumerate(parts):
        s.pre.append(PreLine(4, 20 + i, "BS", tag, "us-gaap/2025", tag, False))
        s.num[(tag, DDATE, 0)].append(
            NumValue(tag, "us-gaap/2025", DDATE, 0, "USD", Decimal(v), dcml)
        )
    claim = pv.Claim("component", "BS", parts=tuple((1, t) for t, _v in parts))
    return s, claim


def _debt_cell(claim, value):
    return pv.Shown(
        3,
        "total_debt_resolved",
        "I",
        FY_END,
        FY_END,
        Decimal(value),
        ("A", "B"),
        ADSH,
        (1,),
        False,
        6,
        claim=claim,
    )


@pytest.mark.unit
def test_r05_component_tolerance_is_half_a_unit_per_part():
    s, claim = _debt_world([("PartA", "10000000000"), ("PartB", "85000000000")])
    # two parts at -6: half a million each, one million in all
    assert pv.prove_cell(_debt_cell(claim, "95000000000"), s, "q").verdict == pv.PROVEN
    assert pv.prove_cell(_debt_cell(claim, "95001000000"), s, "q").verdict == pv.PROVEN
    # 1.2M off: the old flat 1.5M slack proved it
    p = pv.prove_cell(_debt_cell(claim, "95001200000"), s, "q")
    assert p.verdict == pv.DISAGREE
    assert p.reason_code == "shown_differs_from_printed_line"
    # four parts: two million of rounding room
    s4, c4 = _debt_world([(f"P{i}", "10000000000") for i in range(4)])
    assert pv.prove_cell(_debt_cell(c4, "40001900000"), s4, "q").verdict == pv.PROVEN
    assert pv.prove_cell(_debt_cell(c4, "40002100000"), s4, "q").verdict == pv.DISAGREE


@pytest.mark.unit
def test_r16_bank_operating_expenses_is_noninterestexpense():
    s = structure()
    s.pre[:] = [ln for ln in s.pre if ln.tag != "OperatingExpenses"]
    s.pre.append(
        PreLine(
            2,
            30,
            "IS",
            "NoninterestExpense",
            "us-gaap/2025",
            "Total noninterest expense",
            False,
        )
    )
    s.num[("NoninterestExpense", DDATE, 4)].append(
        NumValue(
            "NoninterestExpense",
            "us-gaap/2025",
            DDATE,
            4,
            "USD",
            Decimal("5000000000"),
            -6,
        )
    )
    cell = pv.Shown(
        3,
        "operating_expenses_resolved",
        "FY",
        FY_END.replace(month=1),
        FY_END,
        Decimal("5000000000"),
        ("NoninterestExpense",),
        ADSH,
        (1,),
        False,
        6,
    )
    p = pv.prove_cell(cell, s, "q")
    assert p.verdict == pv.PROVEN, (p.reason_code, p.reason_text)
    assert p.position_tag == "NoninterestExpense"
