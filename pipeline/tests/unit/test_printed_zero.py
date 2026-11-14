"""Printed zero (ruling 2026-11-14, Dhairya): a line printed with a dash or 0 is served as 0 with no fact id, citing the
resolver's R page; the proof treats it as an evidenced value. Pure parts; each assertion is mutation-checked."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl
from scrooner_pipeline.proof import prove as pv
from tests.unit.test_cell_proof import ADSH, FY_END, shown, structure


def _claim(**kw) -> sl.Claim:
    base = dict(
        ticker="TST",
        cik="0000000301",
        data_point="share_buybacks",
        decision="mapped",
        parts=((1, None, "PaymentsForRepurchaseOfCommonStock"),),
        stmts=("CF",),
        locs=((7, 32),),
        accession="0000064803-23-000009",
        period_end=date(2017, 12, 31),
        value="0",
        node_values=("0.0000",),
        flags="cf_family;printed_zero",
    )
    base.update(kw)
    return sl.Claim(**base)


def test_printed_zero_serves_only_a_flagged_mapped_zero_with_no_stored_fact():
    c = _claim()
    assert sd.printed_zero_ok(c, sd.NO_STORED_FACT)
    # another reason (two stored values, a mismatch) is never a printed zero
    assert not sd.printed_zero_ok(
        c, "two stored values for the part in that filing (units)"
    )
    # not flagged
    assert not sd.printed_zero_ok(_claim(flags="cf_family"), sd.NO_STORED_FACT)
    # a non-zero value or node is never served as a printed zero
    assert not sd.printed_zero_ok(
        _claim(value="5", node_values=("5",)), sd.NO_STORED_FACT
    )
    assert not sd.printed_zero_ok(_claim(node_values=("7",)), sd.NO_STORED_FACT)
    assert not sd.printed_zero_ok(
        _claim(value="5"), sd.NO_STORED_FACT
    )  # node 0, value not
    # only a mapped claim
    assert not sd.printed_zero_ok(_claim(decision="component_sum"), sd.NO_STORED_FACT)


def _zero_structure():
    s = structure()
    s.num.pop(
        ("NetIncomeLoss", date(2025, 9, 30), 4)
    )  # the IS prints the line, no value for the column
    return s


@pytest.mark.unit
def test_proof_accepts_a_printed_zero_only_as_zero_and_only_when_flagged():
    base = shown("net_income_resolved", "0")
    ok = pv.prove_cell(replace(base, printed_zero=True), _zero_structure(), "2025q4")
    assert ok.verdict == pv.PROVEN and ok.checks["printed_zero"]["status"] == "pass"
    # the same cell without the flag stays a NOT_PRESENTED reason
    plain = pv.prove_cell(base, _zero_structure(), "2025q4")
    assert plain.verdict == pv.NOT_PRESENTED
    # the flag never proves a non-zero value
    five = pv.prove_cell(
        replace(shown("net_income_resolved", "5"), printed_zero=True),
        _zero_structure(),
        "2025q4",
    )
    assert five.verdict != pv.PROVEN
    assert Decimal(0) == ok.position_value and ADSH and FY_END
