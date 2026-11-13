"""A quarter column the statement face does not print (Q4 3-month IS of a 10-K, Q2/Q3 3-month cash flow of a 10-Q) is
PROVEN as derived when it equals the printed year-to-date minus the printed earlier year-to-date and both inputs are
printed on a statement face. EPS is never derived; a share count is not additive."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

from tests.unit.test_cell_proof import ADSH, DDATE, FY_END, _q3_structure, structure

Q4_START = date(2025, 6, 29)


def _with_note_q4(tag: str, qtrs: int, value: str, dcml: int = -6):
    """The 10-K whose XBRL also carries the 3-month Q4 fact (quarterly-data note), not printed on the face."""
    s = structure()
    s.num[(tag, DDATE, qtrs)].append(
        NumValue(tag, "us-gaap/2025", DDATE, qtrs, "USD", Decimal(value), dcml)
    )
    return s


def _q4(name: str, tag: str, value: str, derived: bool = False) -> pv.Shown:
    return pv.Shown(
        3, name, "Q", Q4_START, FY_END, Decimal(value), (tag,), ADSH, (9,), derived, 6
    )


@pytest.mark.unit
def test_q4_note_column_is_proven_by_fy_minus_the_printed_nine_months():
    fy = _with_note_q4("NetIncomeLoss", 1, "28010000000")  # FY 112,010 - 9M 84,000 = 28,010
    p = pv.prove_cell(_q4("net_income_resolved", "NetIncomeLoss", "28010000000"), fy, "2025q4", _q3_structure())
    assert p.verdict == pv.PROVEN and p.reason_code is None
    assert p.position_value == Decimal("28010000000")
    assert p.checks["derivation"]["source"] == "face_inputs"
    assert p.checks["statement_face"]["rule"] == "quarter_column_by_subtraction"
    assert p.checks["components_sum"]["inputs"]["ytd"] == "112010000000"
    assert p.checks["components_sum"]["inputs"]["prior"] == "84000000000"


@pytest.mark.unit
def test_q4_note_column_stays_a_reason_without_the_prior_filing_or_when_it_does_not_subtract():
    fy = _with_note_q4("NetIncomeLoss", 1, "26000000000")
    # the reported 3-month value does not equal FY - 9M: not proven, and not silently DISAGREE either
    p = pv.prove_cell(_q4("net_income_resolved", "NetIncomeLoss", "26000000000"), fy, "2025q4", _q3_structure())
    assert p.verdict == pv.NOT_PRESENTED and p.reason_code == "value_in_note_not_on_statement_face"
    assert p.checks["derivation_attempt"]["status"] == pv.DISAGREE
    fy = _with_note_q4("NetIncomeLoss", 1, "28010000000")
    p = pv.prove_cell(_q4("net_income_resolved", "NetIncomeLoss", "28010000000"), fy, "2025q4", None)
    assert p.verdict == pv.NOT_PRESENTED and p.checks["derivation_attempt"]["status"] == pv.UNCHECKED


@pytest.mark.unit
def test_an_input_that_is_not_on_a_face_is_not_proof():
    fy = _with_note_q4("NetIncomeLoss", 1, "28010000000")
    q3 = _q3_structure()
    # the prior 9-month value exists in a filing whose face cannot print it (a 10-K statement prints annual columns
    # only): the subtraction would reproduce the value, but its input is a note fact
    q3.form = "10-K"
    p = pv.prove_cell(_q4("net_income_resolved", "NetIncomeLoss", "28010000000"), fy, "2025q4", q3)
    assert p.verdict == pv.NOT_PRESENTED


@pytest.mark.unit
def test_eps_and_share_counts_are_never_derived():
    for name in ("diluted_eps_resolved", "basic_eps_resolved", "weighted_diluted_shares"):
        assert pv.never_derived(name)
    assert not pv.never_derived("dividends_per_share_resolved")  # Q4 DPS by subtraction is allowed (founder 2026-11-04)
    s = _with_note_q4("EarningsPerShareDiluted", 1, "1.50", 2)
    q3 = FilingStructure("0000320193-25-000073", "0000320193", "10-Q", date(2025, 8, 1), date(2025, 6, 28))
    q3.pre.append(PreLine(2, 7, "IS", "EarningsPerShareDiluted", "us-gaap/2025", "Diluted", False))
    d = date(2025, 6, 30)
    q3.num[("EarningsPerShareDiluted", d, 3)].append(
        NumValue("EarningsPerShareDiluted", "us-gaap/2025", d, 3, "USD", Decimal("5.96"), 2)
    )  # 7.46 - 5.96 = 1.50 would reproduce the value: EPS must still not be proven by it
    p = pv.prove_cell(_q4("diluted_eps_resolved", "EarningsPerShareDiluted", "1.50"), s, "2025q4", q3)
    assert p.verdict == pv.NOT_PRESENTED and p.reason_code == "value_in_note_not_on_statement_face"
    assert "derivation_attempt" not in p.checks


@pytest.mark.unit
def test_q3_cash_flow_column_is_proven_from_nine_months_minus_six_months():
    q3 = FilingStructure("0000320193-25-000073", "0000320193", "10-Q", date(2025, 8, 1), date(2025, 6, 28))
    q3.pre.append(PreLine(6, 9, "CF", "NetCashProvidedByUsedInOperatingActivities", "us-gaap/2025", "Net cash from operations", False))
    d9, d6 = date(2025, 6, 30), date(2025, 3, 31)
    tag = "NetCashProvidedByUsedInOperatingActivities"
    q3.num[(tag, d9, 3)].append(NumValue(tag, "us-gaap/2025", d9, 3, "USD", Decimal("90000000000"), -6))
    q3.num[(tag, d9, 1)].append(NumValue(tag, "us-gaap/2025", d9, 1, "USD", Decimal("30000000000"), -6))  # note column
    q2 = FilingStructure("0000320193-25-000050", "0000320193", "10-Q", date(2025, 5, 1), date(2025, 3, 29))
    q2.pre.append(PreLine(6, 9, "CF", tag, "us-gaap/2025", "Net cash from operations", False))
    q2.num[(tag, d6, 2)].append(NumValue(tag, "us-gaap/2025", d6, 2, "USD", Decimal("60000000000"), -6))
    shown = pv.Shown(
        3, "cfo_resolved", "Q", date(2025, 3, 30), date(2025, 6, 28), Decimal("30000000000"), (tag,),
        "0000320193-25-000073", (9,), False, 6,
    )
    p = pv.prove_cell(shown, q3, "2025q3", q2)
    assert p.verdict == pv.PROVEN and p.checks["derivation"]["source"] == "face_inputs"
