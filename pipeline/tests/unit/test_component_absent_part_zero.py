"""Rule 1 (Dhairya 2026-11-14): a component part absent from the period's filing counts as 0 only when that filing's face
omits the line in the column AND the filing's own calc parent ties without it (evidence absent_on_face_parent_ties).
No parent to tie: the part stays unknown (component_missing_for_period)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.common.authority import FaceIndex, absent_part_is_zero
from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, build_cells

DEBT = 50
INFO = {DEBT: ("total_debt", "balance_sheet")}
END = date(2024, 12, 31)
ACC = "A-10"
PERIODS = {7: (END, END, "instant")}


def _rows(parent="Liabilities"):
    return [
        MapRow(
            "us-gaap",
            t,
            "BS",
            "component",
            None,
            DEBT,
            1,
            date(2015, 1, 1),
            None,
            parent,
        )
        for t in ("DebtCurrent", "LongTermDebtNoncurrent")
    ]


def _face(prints_noncurrent: bool):
    prints = {(ACC, "DebtCurrent"): [("BS", END, 0)]}
    if prints_noncurrent:
        prints[(ACC, "LongTermDebtNoncurrent")] = [("BS", END, 0)]
    return FaceIndex(filings={ACC: ("10-K", END, (END, 0.0))}, prints=prints)


FACTS = {("us-gaap", "DebtCurrent"): {7: Fact(Decimal("100"), 1, END, False, 10, ACC)}}
TIES = {(ACC, "Liabilities"): [(END, 0, True)]}


def _build(face, ties, parent="Liabilities"):
    return build_cells(
        _rows(parent),
        FACTS,
        INFO,
        {ACC: {("Liabilities", "DebtCurrent")}},
        {},
        PERIODS,
        face=face,
        ties=ties,
    )


def test_absent_part_is_zero_when_face_omits_it_and_parent_ties():
    cells, stats = _build(_face(False), TIES)
    assert [c["value"] for c in cells] == [Decimal("100")]
    assert "absent_on_face_parent_ties" in cells[0]["serve_note"]
    assert "LongTermDebtNoncurrent" in cells[0]["serve_note"]


def test_part_stays_unknown_without_a_tie_or_a_parent():
    for ties, parent in (
        ({}, "Liabilities"),
        (TIES, None),
        ({(ACC, "Liabilities"): [(END, 0, False)]}, "Liabilities"),
    ):
        cells, stats = _build(_face(False), ties, parent)
        assert cells == []
        assert stats["held"][0]["reason"] == "component_missing_for_period"


def test_evidence_function_requires_face_omission_and_a_tie():
    f = _face(False)
    assert absent_part_is_zero(
        f, TIES, ACC, "LongTermDebtNoncurrent", {"Liabilities"}, END, END, "instant"
    )
    # the face prints the line: not absent
    assert (
        absent_part_is_zero(
            _face(True),
            TIES,
            ACC,
            "LongTermDebtNoncurrent",
            {"Liabilities"},
            END,
            END,
            "instant",
        )
        is None
    )
    # filing not judged (not in the FSN store)
    assert (
        absent_part_is_zero(
            f,
            TIES,
            "B-1",
            "LongTermDebtNoncurrent",
            {"Liabilities"},
            END,
            END,
            "instant",
        )
        is None
    )
