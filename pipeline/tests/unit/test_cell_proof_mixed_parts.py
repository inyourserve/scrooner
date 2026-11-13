"""R06: a component claim may mix statements (face debt lines + a note finance-lease total)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import NumValue, PreLine
from scrooner_pipeline.proof.shown import claim_for

from tests.unit.test_cell_proof import ADSH, DDATE, FY_END, structure

ERA = date(2015, 1, 1)


def _rows(lease_stmt):
    # (id, decision, stmt, tag, concept, parent, sign, era_from, era_to)
    return [
        (
            1,
            "component",
            "BS",
            "LongTermDebtNoncurrent",
            None,
            "total_debt_resolved",
            1,
            ERA,
            None,
        ),
        (
            2,
            "component",
            lease_stmt,
            "FinanceLeaseLiability",
            None,
            "total_debt_resolved",
            1,
            ERA,
            None,
        ),
    ]


@pytest.mark.unit
def test_claim_for_keeps_the_note_part_of_a_mixed_statement_claim():
    claim = claim_for(_rows("UN"), "total_debt_resolved", FY_END)
    assert claim is not None
    assert [t for _s, t in claim.parts] == [
        "LongTermDebtNoncurrent",
        "FinanceLeaseLiability",
    ]
    assert claim.part_stmts == ("BS", "UN")


def _world():
    s = structure()
    s.pre.append(
        PreLine(
            4,
            20,
            "BS",
            "LongTermDebtNoncurrent",
            "us-gaap/2025",
            "Long-term debt",
            False,
        )
    )
    for tag, v in (
        ("LongTermDebtNoncurrent", "60000000000"),
        ("FinanceLeaseLiability", "4000000000"),
    ):
        s.num[(tag, DDATE, 0)].append(
            NumValue(tag, "us-gaap/2025", DDATE, 0, "USD", Decimal(v), -6)
        )
    return s


def _cell(claim, value):
    return pv.Shown(
        3,
        "total_debt_resolved",
        "I",
        FY_END,
        FY_END,
        Decimal(value),
        ("x",),
        ADSH,
        (1,),
        False,
        6,
        claim=claim,
    )


@pytest.mark.unit
@pytest.mark.parametrize("lease_stmt", ["UN", "BS"])
def test_mixed_claim_sums_face_and_note_parts(lease_stmt):
    # the map may store the note part on UN or (as the maps do) on the face statement code
    claim = claim_for(_rows(lease_stmt), "total_debt_resolved", FY_END)
    s = _world()
    ok = pv.prove_cell(_cell(claim, "64000000000"), s, "q")
    assert ok.verdict == pv.PROVEN, (ok.reason_code, ok.reason_text)
    assert ok.checks["component_parts"]["note_facts"] == ["FinanceLeaseLiability"]
    # the partial total (the dropped-lease-part claim) no longer proves
    assert pv.prove_cell(_cell(claim, "60000000000"), s, "q").verdict == pv.DISAGREE
