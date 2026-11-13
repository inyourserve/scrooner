"""R01 end to end: a map claim on a face statement (IS) whose tag the filing prints only as a note fact
is proven against the note fact; a claim whose tag IS a face line keeps the face reasons."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.shown import load_shown

from tests.unit.test_cell_proof_claims_db import _structure, _world

NOTE_ON_IS = dict(
    name="interest_expense_resolved",
    stmt="IS",
    rows=[("concept", "IS", "InterestExpense", 1)],
    facts=[("InterestExpense", "3500000000")],
    shown="3500000000",
    bad="3900000000",
    filing=[("InterestExpense", "USD", "3500000000", -6)],
    pre=[("IS", "OperatingIncomeLoss")],  # the IS prints no InterestExpense line
    kind="duration",
)


def _cell(conn, cik, case, shown_value):
    cid = _world(conn, cik, case, shown_value)
    cells = [
        c
        for c in load_shown(conn, cid, floor=date(2015, 1, 1))
        if c.data_point_name == case["name"]
    ]
    assert len(cells) == 1 and cells[0].claim.stmt == "IS"
    return cells[0]


@pytest.mark.integration
@pytest.mark.parametrize("variant", ["proven", "disagree"])
def test_is_claim_with_a_note_only_tag_is_proven_from_the_note_fact(
    isolated_database_url, variant
):
    shown_value = NOTE_ON_IS["shown"] if variant == "proven" else NOTE_ON_IS["bad"]
    with psycopg.connect(isolated_database_url) as conn:
        cell = _cell(conn, f"00000001{variant == 'proven':d}0", NOTE_ON_IS, shown_value)
    p = pv.prove_cell(cell, _structure(NOTE_ON_IS), "2025q1")
    if variant == "proven":
        assert p.verdict == pv.PROVEN, (p.reason_code, p.reason_text)
        assert p.reason_code != "value_in_note_not_on_statement_face"
        assert p.checks["statement_face"]["status"] == "n/a"
    else:
        assert p.verdict == pv.DISAGREE
        assert p.reason_code == "shown_differs_from_printed_line"


@pytest.mark.integration
def test_is_claim_on_a_printed_face_line_stays_on_the_face_path(isolated_database_url):
    """The tag IS a line of the IS: the note path must not take it over."""
    case = dict(NOTE_ON_IS, pre=[("IS", "InterestExpense")])
    with psycopg.connect(isolated_database_url) as conn:
        cell = _cell(conn, "0000000120", case, case["shown"])
    s = _structure(case)
    assert not pv._note_fact_claim(cell, s)
    p = pv.prove_cell(cell, s, "2025q1")
    assert p.verdict == pv.PROVEN
    assert p.checks["statement_face"]["status"] == "pass"
