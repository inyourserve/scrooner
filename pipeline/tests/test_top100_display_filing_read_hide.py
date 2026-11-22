"""Filing-read hides (Dhairya 2026-11-21, resolver .86): coverage reads the resolver flag `filing_read_hide;<class>`
written by data-team/tags/line_map/tools/filing_reads.py, so each of the reader's hides is a hidden cell with the
reader's class, quote, locator and accession, never a plain not_presented. Mutation checks: drop the apply_display
branch, or the loader's class lookup, and these fail."""

from scrooner_pipeline.mapper import cell_display_state as cds
from scrooner_pipeline.mapper import top100_coverage as t100

HEADER = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,quote,locator,quote_period,resolver_version\n"


def _cell(dp, fy, cls, code="", **kw):
    r = {
        "company_id": 1,
        "rank": 1,
        "ticker": "T",
        "data_point": dp,
        "fiscal_year": fy,
        "period_end": f"{fy}-12-31",
        "class": cls,
        "reason_code": code,
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
    }
    r.update(kw)
    return r


def _resolver(tmp_path):
    d = tmp_path / "resolver"
    d.mkdir()
    (d / "T.csv").write_text(
        HEADER
        + '1,T,sbc,2019-12-31,FY,not_presented,,,0000000001-20-000001,own,,filing_read_hide;only_after_tax_disclosed,"R97: after tax 297",R97.htm of 0000000001-20-000001,,r.86\n'
        + '1,T,oie,2019-12-31,FY,not_presented,,,0000000001-20-000001,own,,roles;filing_read_hide;never_reported,"no line",R4.htm of 0000000001-20-000001,,r.86\n'
        + '1,T,inv,2019-12-31,FY,combined,,,0000000001-20-000001,own,,filing_read_hide;line_presented_combined,"Inventories and other",R2.htm,,r.86\n'
        + "1,T,x,2019-12-31,FY,not_presented,,,A,own,,filing_read_hide;made_up_class,q,L,,r.86\n"
        + "1,T,y,2019-12-31,FY,not_presented,,,A,own,,roles,,,,r.86\n"
    )
    return tmp_path


def test_loader_maps_reader_classes_and_skips_unknown_ones(tmp_path):
    h = t100.load_filing_read_hides(_resolver(tmp_path))
    assert set(h) == {
        ("T", "sbc", "2019-12-31"),
        ("T", "oie", "2019-12-31"),
        ("T", "inv", "2019-12-31"),
    }
    assert h[("T", "sbc", "2019-12-31")][:2] == (
        "only_after_tax_disclosed",
        "only_after_tax_disclosed",
    )
    assert h[("T", "oie", "2019-12-31")][:2] == (
        "never_reported",
        "structural_not_presented",
    )
    assert h[("T", "inv", "2019-12-31")][1] == "line_presented_combined"
    assert (
        h[("T", "sbc", "2019-12-31")][2]
        == "filing read, only_after_tax_disclosed: R97: after tax 297"
    )
    assert h[("T", "sbc", "2019-12-31")][3:] == (
        "0000000001-20-000001",
        "R97.htm of 0000000001-20-000001",
    )
    assert t100.load_filing_read_hides(tmp_path / "none") == {}


def test_reader_hide_is_a_hidden_year_with_the_reader_class_and_evidence(tmp_path):
    h = t100.load_filing_read_hides(_resolver(tmp_path))
    rows = [
        _cell("sbc", 2019, "REASON", "company_tag_map:not_presented"),
        _cell("sbc", 2020, "PROVEN", accession="Z", r_page="R5"),
        _cell("inv", 2019, "REASON", "company_tag_map:not_presented"),
        _cell("inv", 2020, "BLANK"),
        _cell("y", 2019, "BLANK"),
        _cell("y", 2020, "PROVEN"),
    ]
    t100.attach_filing_read_hides(rows, h)
    t100.apply_display(rows)
    d = {(r["data_point"], r["fiscal_year"]): r for r in rows}
    s = d[("sbc", 2019)]
    assert (s["display"], s["hide_class"]) == (
        "HIDDEN_YEAR",
        "only_after_tax_disclosed",
    )
    assert s["accession"] == "0000000001-20-000001" and s["r_page"].startswith(
        "R97.htm"
    )
    assert s["evidence"].startswith("filing read, only_after_tax_disclosed")
    assert (d[("inv", 2019)]["display"], d[("inv", 2019)]["hide_class"]) == (
        "HIDDEN_YEAR",
        "line_presented_combined",
    )
    assert d[("inv", 2020)]["display"] == "OPEN"
    assert d[("y", 2019)]["display"] == "OPEN"  # no reader flag: unchanged
    _, hy = t100.hidden_evidence(rows)
    assert {r["basis"] for r in hy} == {
        "filing_read:only_after_tax_disclosed",
        "filing_read:line_presented_combined",
    }
    # the display-state writer accepts every class the reader path assigns
    assert cds.state_rows(rows, [], "run", "r.86")


def test_every_year_hidden_by_reads_collapses_to_a_hidden_row_and_a_printed_line_reopens(
    tmp_path,
):
    h = t100.load_filing_read_hides(_resolver(tmp_path))
    rows = [_cell("oie", 2019, "REASON", "company_tag_map:not_presented")]
    t100.attach_filing_read_hides(rows, h)
    t100.apply_display(rows)
    assert (rows[0]["display"], rows[0]["hide_class"]) == (
        "HIDDEN_ROW",
        "structural_not_presented",
    )
    # line-level presence still wins: a filing that prints the data point's line keeps the cell open
    rows = [_cell("oie", 2019, "REASON", "company_tag_map:not_presented")]
    t100.attach_filing_read_hides(rows, h)
    rows[0]["_family_hit"] = True
    t100.apply_display(rows)
    assert (rows[0]["display"], rows[0]["hide_class"]) == ("OPEN", "")


def test_a_proven_or_derived_value_is_never_hidden_by_a_read(tmp_path):
    h = t100.load_filing_read_hides(_resolver(tmp_path))
    rows = [_cell("sbc", 2019, "DERIVED", accession="Q")]
    t100.attach_filing_read_hides(rows, h)
    t100.apply_display(rows)
    assert rows[0]["display"] == "SHOWN_VALUE" and rows[0]["accession"] == "Q"


def test_a_row_class_read_for_one_year_is_a_year_class_or_open_never_a_row_class_on_a_year(
    tmp_path,
):
    """WMT other_income_expense_net FY2015 (approver 2026-11-22): the reader's structural_not_presented (a row class)
    hid ONE year of a row shown in every other year. A year hide needs a year class: verified_absent, allowlisted data
    points only; otherwise the year is open. Mutation: hide with the reader's class as before and this fails."""
    d = tmp_path / "resolver"
    d.mkdir()
    (d / "T.csv").write_text(
        HEADER
        + '1,T,other_income_expense_net,2019-12-31,FY,not_presented,,,0000000001-20-000001,own,,filing_read_hide;structural_not_presented,"band",R2.htm,,r.89\n'
        + '1,T,operating_income,2019-12-31,FY,not_presented,,,0000000001-20-000001,own,,filing_read_hide;structural_not_presented,"no line",R2.htm,,r.89\n'
    )
    h = t100.load_filing_read_hides(tmp_path)
    rows = [
        _cell("other_income_expense_net", 2019, "REASON", "filing_read_hide"),
        _cell("other_income_expense_net", 2020, "PROVEN", accession="Z", r_page="R5"),
        _cell("operating_income", 2019, "REASON", "filing_read_hide"),
        _cell("operating_income", 2020, "PROVEN", accession="Z", r_page="R5"),
    ]
    t100.attach_filing_read_hides(rows, h)
    t100.apply_display(rows)
    by = {(r["data_point"], r["fiscal_year"]): r for r in rows}
    oie = by[("other_income_expense_net", 2019)]
    assert (oie["display"], oie["hide_class"]) == ("OPEN", "")
    assert "row class" in oie["reason"]
    # an allowlisted data point hides the year with the YEAR class
    oi = by[("operating_income", 2019)]
    assert (oi["display"], oi["hide_class"]) == ("HIDDEN_YEAR", "verified_absent")
    # every year read as never reported (no shown year): one structural row, as before
    rows = [_cell("other_income_expense_net", 2019, "REASON", "filing_read_hide")]
    t100.attach_filing_read_hides(rows, h)
    t100.apply_display(rows)
    assert (rows[0]["display"], rows[0]["hide_class"]) == (
        "HIDDEN_ROW",
        "structural_not_presented",
    )
