"""FSN dropped facts (data-team/tags/line_map/rules/fsn_dropped_facts.csv): loader, member read, filing check, serving."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import fsn_dropped_facts as fdf
from scrooner_pipeline.common import member_facts as mf
from scrooner_pipeline.fsn_store import checks
from scrooner_pipeline.mapper import structural_loader as sl
from tests.unit.test_structural_direct import ACC1, END, W, _csv, _row  # noqa: F401

PM = "0001413329-23-000025"
AM = "AmortizationOfIntangibleAssets"
LOC = "IncomeStatementLocation=CostOfSales;"
D = date(2022, 12, 31)


def _r(**kw):
    r = {
        "accession": PM,
        "tag": AM,
        "qtrs": "4",
        "segment": LOC,
        "value": "58000000",
        "evidence": "PM FY2022 10-K R60.htm line 3",
    }
    r.update(kw)
    return r


@pytest.mark.unit
def test_committed_csv_parses_and_holds_the_pm_members():
    got = fdf.load()
    assert got[(PM, AM, 4, LOC)].value == Decimal(58000000)
    assert got[
        (PM, AM, 4, "IncomeStatementLocation=MarketingAdministrationAndResearchCosts;")
    ].value == Decimal(101000000)


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad",
    [
        {"accession": "bad"},
        {"qtrs": "9"},
        {"value": "x"},
        {"value": ""},
        {"evidence": ""},
        {"tag": ""},
    ],
)
def test_parse_rejects_malformed_rows(bad):
    with pytest.raises(ValueError):
        fdf.parse([_r(**bad)])


@pytest.mark.unit
def test_parse_rejects_duplicates_and_normalises_segments():
    with pytest.raises(ValueError):
        fdf.parse([_r(), _r(segment="IncomeStatementLocation=CostOfSales")])
    assert fdf.norm_segment("A=B,C=D") == "A=B;C=D;"
    assert fdf.norm_segment("") == ""


@pytest.mark.unit
def test_stored_problems():
    f = fdf.parse([_r()])[(PM, AM, 4, LOC)]
    assert fdf.stored_problems(f, []) is None
    assert fdf.stored_problems(f, [Decimal(58000000)]) is None  # the store caught up
    assert fdf.stored_problems(f, [Decimal(1)]) is not None


@pytest.mark.unit
def test_member_read_resolves_a_dropped_row_with_the_evidence_and_no_value_id():
    f = fdf.parse([_r()])[(PM, AM, 4, LOC)]
    rows = [mf.MemberRow(D, 4, "USD", LOC, f.value, 0, f)]
    spec = mf.split_member_part(f"{AM}[{LOC.rstrip(';')}]")
    hit = mf.resolve_member_part(rows, spec, D, Decimal(58000000))
    assert not isinstance(hit, str)
    assert hit.value == Decimal(58000000) and hit.ids == () and hit.dropped == (f,)
    # the store caught up: a stored fact of the same value wins, the CSV row is no longer the source
    both = [*rows, mf.MemberRow(D, 4, "USD", LOC, f.value, 77)]
    hit = mf.resolve_member_part(both, spec, D, None)
    assert hit.ids == (77,) and hit.dropped == ()
    # a stored fact with a different value makes the part ambiguous, never a silent pick
    clash = [*rows, mf.MemberRow(D, 4, "USD", LOC, Decimal(1), 78)]
    assert isinstance(mf.resolve_member_part(clash, spec, D, None), str)


def _data():
    ver = "us-gaap/2022"
    p = checks.Print("Assets", ver, Decimal(10), -6, None)
    return {
        "stmt_of": {("Assets", ver): "BS", (AM, ver): "CF"},
        "columns": {("BS", D, 0): {("Assets", ver): p}, ("CF", D, 4): {}},
        "alts": {},
        "members": {},
        "values": {("Assets", D, 0): p},
    }


@pytest.mark.unit
def test_apply_dropped_supplies_values_and_member_rows_to_the_check():
    data = _data()
    facts = fdf.parse(
        [
            _r(
                segment="", tag="Assets", qtrs="0", value="10"
            ),  # already tagged: nothing to supply
            _r(segment="", tag=AM, qtrs="4", value="159"),
        ]
    )
    used = checks.apply_dropped(data, list(facts.values()))
    assert data["columns"][("CF", D, 4)][(AM, "us-gaap/2022")].value == Decimal(159)
    assert ("CF", D, 4) in used and ("BS", D, 0) not in used
    data = _data()
    f = fdf.parse([_r()])
    used = checks.apply_dropped(data, list(f.values()))
    assert data["members"][("CF", D, 4)][("dropped", LOC)][
        (AM, "us-gaap/2022")
    ] == Decimal(58000000)
    assert used[("CF", D, 4)][0].evidence.startswith("PM FY2022")


@pytest.mark.unit
def test_loader_sign_solve_reads_an_undimensioned_dropped_fact(monkeypatch, tmp_path):
    p = tmp_path / "d.csv"
    p.write_text(
        f'accession,tag,qtrs,segment,value,evidence\n{PM},Foo,4,,7,"R9 line 2"\n'
    )
    monkeypatch.setattr(fdf, "CSV_PATH", p)
    fdf._load.cache_clear()
    c = sl.Claim(
        ticker="PM",
        cik="0001413329",
        data_point="x",
        decision="component_sum",
        parts=((1, None, "Foo"),),
        stmts=("",),
        locs=((None, None),),
        accession=PM,
        period_end=D,
        grain="FY",
    )
    assert sl.fixed_option(c, "Foo", set()) == {Decimal(7)}
    assert sl.fixed_option(c, "Foo", {Decimal(5)}) == {Decimal(5)}  # a stored fact wins
    fdf._load.cache_clear()


NODES = (
    "AmortizationOfIntangibleAssets[IncomeStatementLocation=CostOfSales]=58 [NOTE]; "
    "AmortizationOfIntangibleAssets[IncomeStatementLocation=MarketingAdministrationAndResearchCosts]=101 [NOTE] | why: location sum"
)


@pytest.mark.integration
def test_dropped_members_serve_as_fsn_dropped_fact(
    isolated_database_url, tmp_path, monkeypatch
):
    """The PM FY2022 shape: two member facts the FSN ingest dropped; the cell serves their sum, value_source
    fsn_dropped_fact, no value ids, the note carries the CSV evidence."""
    with psycopg.connect(isolated_database_url) as conn:
        w = W(conn)
        w.filing(ACC1, date(2019, 2, 1), END)
        w.fsn_fact(
            ACC1, "Anchor", "1", custom=False
        )  # creates the fsn.filing row (period END)
        _csv(
            tmp_path,
            _row(ACC1, "159", tags=NODES, decision="component_sum"),
            monkeypatch=monkeypatch,
        )
        cells, st = w.cells()
        assert cells == []  # no stored member facts and no CSV rows: rejected
        p = tmp_path / "fsn_dropped_facts.csv"
        p.write_text(
            "accession,tag,qtrs,segment,value,evidence\n"
            f'{ACC1},AmortizationOfIntangibleAssets,4,IncomeStatementLocation=CostOfSales;,58,"R60.htm line 3"\n'
            f'{ACC1},AmortizationOfIntangibleAssets,4,IncomeStatementLocation=MarketingAdministrationAndResearchCosts;,101,"R60.htm line 4"\n'
        )
        monkeypatch.setattr(fdf, "CSV_PATH", p)
        fdf._load.cache_clear()
        (c,), st = w.cells()
        assert (c["value"], c["value_source"]) == (Decimal(159), "fsn_dropped_fact")
        assert c["source_value_ids"] == [] and c["source_fact_ids"] == []
        assert (
            "R60.htm line 3" in c["serve_note"] and "R60.htm line 4" in c["serve_note"]
        )
        fdf._load.cache_clear()
