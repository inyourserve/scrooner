"""A 52/53-week year end (HD 2018-01-28) is inside the era row ending on it AND, by month-end rounding, inside the
stub era row 2018-01-29..2018-01-31 that lists the same tags. The same fact must count once in a component sum
(HD total_debt FY2017 served 54,056 = 2 x 27,028; five more FY ends the same)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, build_cells

DA_ID = 31
INFO = {DA_ID: ("depreciation_and_amortization", "cash_flow")}
END = date(2018, 1, 28)


def _fact(v, i):
    return Fact(Decimal(v), i, END, False, 10, "A-10")


def _world(stub: bool):
    def row(tag, parent, lo, hi):
        return MapRow("us-gaap", tag, "CF", "component", None, DA_ID, 1, lo, hi, parent)

    rows = []
    for tag, parent in (("Dep", "P1"), ("Amort", "P2")):
        rows.append(row(tag, parent, date(2017, 1, 29), END))
        if stub:
            rows.append(row(tag, parent, date(2018, 1, 29), date(2018, 1, 31)))
    facts = {
        ("us-gaap", "Dep"): {7: _fact("700", 1)},
        ("us-gaap", "Amort"): {7: _fact("66", 2)},
    }
    arcs = {"A-10": {("P1", "Dep"), ("P2", "Amort")}}
    return build_cells(rows, facts, INFO, arcs, {})


def test_a_tag_listed_by_two_adjacent_era_rows_counts_once():
    cells, _ = _world(stub=True)
    assert [c["value"] for c in cells] == [Decimal("766")]


def test_one_era_row_per_tag_is_unchanged():
    cells, _ = _world(stub=False)
    assert [c["value"] for c in cells] == [Decimal("766")]
