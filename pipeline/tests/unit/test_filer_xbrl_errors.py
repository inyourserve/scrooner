"""Filer XBRL errors (data-team/tags/line_map/rules/filer_xbrl_errors.csv): loader, filing check, serving."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.common import filer_xbrl_errors as fxe
from scrooner_pipeline.fsn_store import checks
from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import structural_loader as sl

ACC = "0000101829-20-000013"
D19, D18 = date(2019, 12, 31), date(2018, 12, 31)
VER = "us-gaap/2019"
RNCI = (
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"
)
EQ = "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
LSE = "LiabilitiesAndStockholdersEquity"
EM = "IncomeLossFromEquityMethodInvestments"


def _row(**kw):
    r = {
        "accession": ACC,
        "tag": "Liabilities",
        "qtrs": "0",
        "xbrl_value": "",
        "printed_value": "95390000000",
        "evidence": "RTX FY2019 balance sheet",
    }
    r.update(kw)
    return r


def _by_tag_qtrs(rows):
    return [c for cs in fxe.parse(rows).values() for c in cs]


@pytest.mark.unit
def test_committed_csv_parses_and_has_every_row():
    got = fxe.load()
    assert len(got) == 14
    # MCD FY2023-25 weighted shares tagged in millions at scale 0 (wave 3A 2026-11-17)
    mcd = got[
        ("0000063908-24-000072", "WeightedAverageNumberOfSharesOutstandingBasic", 4)
    ][0]
    assert mcd.xbrl_value == Decimal("727.9") and mcd.printed_value == Decimal(
        "727900000"
    )
    # STX R9 holds the FY2022 DPS beside the FY2024 one: two rows under one key, told apart by the stored value
    assert {
        r.printed_value
        for r in got[
            ("0001137789-24-000068", "CommonStockDividendsPerShareDeclared", 4)
        ]
    } == {Decimal("2.80"), Decimal("2.77")}
    stx = got[("0001137789-24-000068", "CommonStockDividendsPerShareDeclared", 4)][
        0
    ]  # STX FY2024 DPS stored 10^6 too large (Ritwik draw 2026-11-16)
    assert stx.xbrl_value == Decimal("2800000") and stx.printed_value == Decimal("2.80")
    c = got[("0001562762-20-000064", EM, 4)][0]
    assert c.xbrl_value == Decimal("-6000000") and c.printed_value == Decimal("6000000")
    s = got[(ACC, "Liabilities", 0)][0]
    assert s.supplies and s.printed_value == Decimal("95390000000")


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad",
    [
        {"accession": "0000101829-20-00013"},
        {"qtrs": "7"},
        {"qtrs": "x"},
        {"printed_value": ""},
        {"printed_value": "abc"},
        {"xbrl_value": "95390000000"},
        {"evidence": ""},
        {"tag": ""},
    ],
)
def test_parse_rejects_malformed_rows(bad):
    with pytest.raises(ValueError):
        fxe.parse([_row(**bad)])


@pytest.mark.unit
def test_parse_rejects_duplicate_key():
    with pytest.raises(ValueError):
        fxe.parse([_row(), _row()])


@pytest.mark.unit
def test_stored_problems():
    fix = fxe.parse([_row(xbrl_value="-6", printed_value="6")])[
        (ACC, "Liabilities", 0)
    ][0]
    assert fxe.stored_problems(fix, [Decimal("-6")]) is None
    assert fxe.stored_problems(fix, [Decimal("5")]) is not None
    sup = fxe.parse([_row()])[(ACC, "Liabilities", 0)][0]
    assert fxe.stored_problems(sup, [Decimal("93492000000")]) is None
    assert fxe.stored_problems(sup, [Decimal("95390000000")]) is not None


def _p(tag, v):
    return checks.Print(tag, VER, Decimal(v), -6, None)


def _bs_data():
    """RTX-shaped balance sheet: Liabilities and RNCI untagged in 2019, tagged in 2018."""
    stmt_of = {(t, VER): "BS" for t in ("Liabilities", RNCI, EQ, LSE)}
    c19 = {(EQ, VER): _p(EQ, "44231000000"), (LSE, VER): _p(LSE, "139716000000")}
    c18 = {
        ("Liabilities", VER): _p("Liabilities", "93492000000"),
        (RNCI, VER): _p(RNCI, "109000000"),
        (EQ, VER): _p(EQ, "40000000000"),
        (LSE, VER): _p(LSE, "133601000000"),
    }
    data = {
        "stmt_of": stmt_of,
        "columns": {("BS", D19, 0): c19, ("BS", D18, 0): c18},
        "alts": {},
        "members": {},
        "groups": {
            (LSE, VER, 1): [("Liabilities", VER, 1), (RNCI, VER, 1), (EQ, VER, 1)]
        },
        "on": {"BS": set(stmt_of and {k[0] for k in stmt_of})},
        "values": {},
    }
    for (_s, d, q), col in data["columns"].items():
        for (tag, _v), pr in col.items():
            data["values"][(tag, d, q)] = pr
    return data


def _col19(data):
    return checks.check_column(
        "BS", data["columns"][("BS", D19, 0)], data["groups"], data["stmt_of"]
    )


@pytest.mark.unit
def test_supplied_facts_make_the_column_foot():
    data = _bs_data()
    assert _col19(data) == []  # a missing child silently skips the group
    used = checks.apply_corrections(
        data,
        _by_tag_qtrs(
            [_row(), _row(tag=RNCI, printed_value="95000000", evidence="RNCI 95")]
        ),
    )
    assert len(used[("BS", D19, 0)]) == 2
    got = _col19(data)
    assert got and all(c["ok"] for c in got)
    assert data["columns"][("BS", D18, 0)][("Liabilities", VER)].value == Decimal(
        "93492000000"
    )  # the 2018 column is untouched


@pytest.mark.unit
def test_wrong_supplied_value_is_caught_by_the_check():
    data = _bs_data()
    checks.apply_corrections(
        data,
        _by_tag_qtrs(
            [
                _row(printed_value="95000000000"),
                _row(tag=RNCI, printed_value="95000000"),
            ]
        ),
    )
    got = _col19(data)
    assert got and not all(c["ok"] for c in got)


@pytest.mark.unit
def test_sign_correction_replaces_only_the_matching_value():
    pr = checks.Print(EM, VER, Decimal(-6000000), -6, 3)
    other = checks.Print(EM, VER, Decimal(-48000000), -6, 3)
    data = {
        "stmt_of": {(EM, VER): "IS"},
        "columns": {
            ("IS", D19, 4): {(EM, VER): pr},
            ("IS", D18, 4): {(EM, VER): other},
        },
        "alts": {},
        "values": {},
    }
    used = checks.apply_corrections(
        data,
        _by_tag_qtrs(
            [_row(tag=EM, qtrs="4", xbrl_value="-6000000", printed_value="6000000")]
        ),
    )
    assert data["columns"][("IS", D19, 4)][(EM, VER)].value == Decimal(6000000)
    assert data["columns"][("IS", D18, 4)][(EM, VER)].value == Decimal(-48000000)
    assert list(used) == [("IS", D19, 4), ("", D19, 4)]


@pytest.mark.unit
def test_fix_fit_for_serving():
    none = "no stored fact for the part in that filing and column"
    sup = fxe.parse([_row()])[(ACC, "Liabilities", 0)][0]
    assert sd._fix_fit(sup, none) is None
    assert sd._fix_fit(sup, (Decimal("95390000000"), "fsn_xbrl", {1})) is None
    assert sd._fix_fit(sup, (Decimal("1"), "fsn_xbrl", {1})) is not None
    assert sd._fix_fit(sup, "two fsn values for the part in that filing") is not None
    cor = fxe.parse([_row(xbrl_value="-6", printed_value="6")])[
        (ACC, "Liabilities", 0)
    ][0]
    assert sd._fix_fit(cor, (Decimal("-6"), "sec_api", {1})) is None
    assert sd._fix_fit(cor, (Decimal("9"), "sec_api", {1})) is not None
    assert sd._fix_fit(cor, none) is not None


@pytest.mark.unit
def test_loader_sign_solve_uses_the_printed_value():
    c = sl.Claim(
        ticker="T",
        cik="0000732717",
        data_point="other_income_expense_net",
        decision="component_sum",
        parts=((1, None, EM),),
        stmts=("",),
        locs=((None, None),),
        accession="0001562762-20-000064",
        period_end=D19,
        grain="FY",
    )
    assert sl.fixed_option(c, EM, {Decimal(-6000000)}) == {Decimal(6000000)}
    assert sl.fixed_option(c, "Other", {Decimal(1)}) == {Decimal(1)}
    c2 = sl.Claim(**{**c.__dict__, "accession": "0000000000-20-000001"})
    assert sl.fixed_option(c2, EM, {Decimal(-6000000)}) == {Decimal(-6000000)}


STX_ACC = "0001137789-24-000068"
STX_TAG = "CommonStockDividendsPerShareDeclared"


def _stx(xv, pv):
    return _row(
        accession=STX_ACC, tag=STX_TAG, qtrs="4", xbrl_value=xv, printed_value=pv
    )


@pytest.mark.unit
def test_several_rows_share_a_key_when_xbrl_value_differs(tmp_path):
    got = fxe.parse([_stx("2770000", "2.77"), _stx("2800000", "2.80")])
    assert len(got[(STX_ACC, STX_TAG, 4)]) == 2
    with pytest.raises(ValueError):  # same stored value twice is still a duplicate
        fxe.parse([_stx("2770000", "2.77"), _stx("2770000", "2.78")])
    with pytest.raises(ValueError):  # a supply cannot share a key
        fxe.parse([_stx("2770000", "2.77"), _stx("", "2.80")])
    path = tmp_path / "f.csv"
    path.write_text(
        ",".join(fxe.COLUMNS)
        + f"\n{STX_ACC},{STX_TAG},4,2770000,2.77,FY2022 DPS\n{STX_ACC},{STX_TAG},4,2800000,2.80,FY2024 DPS\n"
    )
    assert fxe.corrected_value(
        STX_ACC, STX_TAG, 4, Decimal("2770000"), path
    ) == Decimal("2.77")
    assert fxe.corrected_value(
        STX_ACC, STX_TAG, 4, Decimal("2800000"), path
    ) == Decimal("2.80")
    assert fxe.corrected_value(STX_ACC, STX_TAG, 4, Decimal("2.5"), path) == Decimal(
        "2.5"
    )
    rows = fxe.parse([_stx("2770000", "2.77"), _stx("2800000", "2.80")])[
        (STX_ACC, STX_TAG, 4)
    ]
    assert fxe.pick(rows, Decimal("2800000")).printed_value == Decimal("2.80")
    assert fxe.pick(rows, Decimal("9")) is None
