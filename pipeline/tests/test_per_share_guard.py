"""Filer-scale guard. STX FY2022 dividends_per_share was served as 2,770,000 (expected 2.77): the FY2024 10-K
0001137789-24-000068 stores per-share figures at the filer's monetary scale. Ritwik's certification draw 2026-11-17."""

import inspect
from decimal import Decimal as D

import pytest

from scrooner_pipeline.common.per_share_guard import (
    FILER_SCALE_REASON,
    filer_scale_error,
    is_per_share,
)
from scrooner_pipeline.mapper import company_tag_map, structural_direct
from scrooner_pipeline.mapper import top100_coverage as t100
from scrooner_pipeline.mapper.per_share_scale import scale_error_cell_indexes

STX = 1137789
OTHERS = [D("2.80"), D("2.64"), D("2.52")]  # the same 10-K's other columns of the tag


def _cell(dp, value, fy=2022, cls="PROVEN"):
    return {
        "company_id": STX,
        "rank": 90,
        "ticker": "STX",
        "data_point": dp,
        "fiscal_year": fy,
        "period_end": f"{fy}-07-01",
        "class": cls,
        "reason_code": "",
        "shown_value": value,
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
        "_presented": True,
    }


@pytest.mark.parametrize("dp", ["dividends_per_share", "basic_eps", "diluted_eps"])
def test_filer_scale_error_by_ratio(dp):
    assert filer_scale_error(dp, D("2770000"), OTHERS)  # 10^6
    assert filer_scale_error(dp + "_resolved", "2770", [D("2.64")])  # the concept name
    assert not filer_scale_error(dp, "999", [D("0.9")])  # below the floor
    assert filer_scale_error(dp, D("2770"), [D("2.64")])  # 10^3
    assert not filer_scale_error(dp, D("2.77"), OTHERS)
    assert not filer_scale_error(dp, D("2770000"), [])  # nothing to compare


def test_large_genuine_per_share_is_not_flagged():
    # BRK-A shape: every column is large, so no other column sits below the floor
    assert not filer_scale_error("diluted_eps", D("24000"), [D("18000"), D("21000")])
    # a real 40% rise is nowhere near 10^3
    assert not filer_scale_error("diluted_eps", D("1400"), [D("1000.5")])


def test_other_data_points_are_ignored():
    assert not is_per_share("revenue")
    assert not filer_scale_error("revenue", D("5000000000"), [D("5")])


def test_stx_shape_is_held_open_not_shown():
    rows = [
        _cell("dividends_per_share", "2770000"),
        _cell("dividends_per_share", "2.64", fy=2023),
        _cell("dividends_per_share", "2.80", fy=2024),
    ]
    t100.apply_display(rows)
    assert rows[0]["display"] == t100.OPEN
    assert rows[0]["class"] == "HELD"
    assert rows[0]["reason_code"] == FILER_SCALE_REASON
    assert rows[0]["hide_class"] == ""
    assert [r["display"] for r in rows[1:]] == [t100.SHOWN_VALUE] * 2


def test_serving_layer_calls_the_guard():
    assert "filer_scale_error(" in inspect.getsource(structural_direct.direct_cells)
    assert "scale_error_cell_indexes(" in inspect.getsource(company_tag_map)


class _Cur:
    def __init__(self, script):
        self.script = script
        self.sql = ""

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.sql = sql

    def fetchall(self):
        s = self.sql
        if (
            "from core.fact f join core.concept c on c.id = f.concept_id\n" in s
            and "f.id = any" in s
        ):
            return [(7, "0001137789-24-000068", "CommonStockDividendsPerShareDeclared")]
        if "fl.accession_number, c.tag, f.value" in s:
            return [
                ("0001137789-24-000068", "CommonStockDividendsPerShareDeclared", v)
                for v in ("2770000", "2.64", "2.80")
            ]
        return []


class _Conn:
    def cursor(self):
        return _Cur(None)


def test_cell_indexes_flag_the_stx_cell_from_the_other_columns():
    info = {1: ("dividends_per_share", "cash_flow")}
    cells = [
        {
            "canonical_concept_id": 1,
            "value": D("2770000"),
            "source_fact_ids": [7],
            "source_value_ids": [],
        },
        {
            "canonical_concept_id": 1,
            "value": D("2.64"),
            "source_fact_ids": [8],
            "source_value_ids": [],
        },
    ]
    assert scale_error_cell_indexes(_Conn(), STX, cells, info) == {0}
