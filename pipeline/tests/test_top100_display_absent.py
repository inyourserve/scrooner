"""absent_in_own_filing: the resolver's not_presented-in-own-10-K cell is a hidden year with the resolver accession."""

from datetime import date

from scrooner_pipeline.mapper import top100_coverage as t100

DP = "operating_income"  # a VERIFIED_ABSENT_HIDE data point


def _cell(end, cls="UNCHECKED", **kw):
    r = {
        "company_id": 1,
        "rank": 1,
        "ticker": "QCOM",
        "data_point": DP,
        "fiscal_year": int(end[:4]),
        "period_end": end,
        "class": cls,
        "reason_code": "",
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
    }
    r.update(kw)
    return r


def _absent(cells, printed=()):
    return {("QCOM", DP): (cells, list(printed))}


def _run(rows, ab):
    t100.attach_absent_in_own(rows, ab)
    t100.apply_display(rows)


def test_absent_in_own_filing_hides_the_year_with_the_resolver_accession():
    rows = [_cell("2016-09-30"), _cell("2015-09-27"), _cell("2018-09-30", "PROVEN")]
    _run(rows, _absent({"2016-09-30": "A16"}))
    assert rows[0]["display"] == "HIDDEN_YEAR"
    assert rows[0]["_oc_accession"] == "A16" and rows[0]["accession"] == "A16"
    assert rows[1]["display"] == "OPEN"  # a year the resolver does not flag stays open


def test_absent_in_own_filing_later_filing_guard_keeps_a_printed_year_open():
    rows = [_cell("2016-09-30"), _cell("2017-09-30", "PROVEN")]
    _run(rows, _absent({"2016-09-30": "A16"}, [date(2017, 9, 30)]))
    assert rows[0]["display"] == "OPEN"  # a later annual report prints the line
    rows = [_cell("2016-09-30"), _cell("2017-09-30", "PROVEN")]
    _run(rows, _absent({"2016-09-30": "A16"}, [date(2020, 9, 30)]))
    assert rows[0]["display"] == "HIDDEN_YEAR"  # too late to carry the year


def test_absent_in_own_filing_matches_a_52_53_week_end_uniquely():
    rows = [_cell("2016-09-25"), _cell("2017-10-01"), _cell("2018-09-30", "PROVEN")]
    _run(rows, _absent({"2016-09-30": "A16", "2017-09-30": "A17", "2017-10-05": "A18"}))
    assert rows[0]["display"] == "HIDDEN_YEAR" and rows[0]["accession"] == "A16"
    assert rows[1]["display"] == "OPEN"  # two resolver periods match: ambiguous


def test_absent_in_own_filing_never_touches_a_value():
    rows = [_cell("2016-09-30", "PROVEN")]
    _run(rows, _absent({"2016-09-30": "A16"}))
    assert rows[0]["display"] == "SHOWN_VALUE"


def test_loader_reads_not_presented_own_and_skips_pre_filing(tmp_path):
    hdr = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"
    line = f"1,QCOM,{DP},{{}},FY,{{}},,,{{}},{{}},,{{}},v\n"
    (tmp_path / "resolver-all110-2026-11-14.csv").write_text(
        hdr
        + line.format(
            "2016-09-30", "not_presented", "A16", "own", "roles;never_reported"
        )
        + line.format("2014-09-30", "not_presented", "A14", "own", "before_first_10k")
        + line.format(
            "2015-09-30", "not_presented", "A15", "comparative", "line_not_printed"
        )
        + line.format("2017-09-30", "mapped", "A17", "own", "roles")
    )
    cells, printed = t100.load_absent_in_own(tmp_path)[("QCOM", DP)]
    assert cells == {"2016-09-30": "A16"} and printed == [date(2017, 9, 30)]


def test_an_unlisted_data_point_is_never_hidden_by_this_rule(tmp_path):
    hdr = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"
    row = "1,QCOM,{},2016-09-30,FY,not_presented,,,A16,own,,roles,v\n"
    dps = [
        "inventory",
        "cash_paid_for_interest",
        "operating_income",
        "shares_outstanding",
        "share_buybacks",
    ]
    (tmp_path / "resolver-all110-2026-11-14.csv").write_text(
        hdr + "".join(row.format(d) for d in dps)
    )
    got = t100.load_absent_in_own(tmp_path)
    assert {dp for _, dp in got} == {
        "operating_income",
        "shares_outstanding",
        "share_buybacks",
    }
    assert "no face-statement line" in t100.ABSENT_EVIDENCE


def test_not_in_template_pairs_are_out_of_the_grid(tmp_path):
    hdr = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"
    row = "1,{},{},2016-09-30,FY,{},,,A1,own,,roles,v\n"
    (tmp_path / "resolver-all110-2026-11-14.csv").write_text(
        hdr
        + row.format("AAPL", "deposits", "not_in_template")
        + row.format("JPM", "deposits", "mapped")
        + row.format("AAPL", "revenue", "mapped")
        + row.format("MIX", "x", "not_in_template")
        + row.format("MIX", "x", "mapped")
    )
    out = t100.load_not_in_template(tmp_path)
    assert out == {("AAPL", "deposits")}
    rows = [
        _cell("2016-09-30", "PROVEN", ticker="AAPL", data_point="deposits"),
        _cell("2016-09-30", "PROVEN", ticker="JPM", data_point="deposits"),
        _cell("2016-09-30", "UNCHECKED", ticker="AAPL", data_point="revenue"),
    ]
    kept, dropped = t100.split_out_of_template(rows, out)
    assert [r["ticker"] + r["data_point"] for r in kept] == [
        "JPMdeposits",
        "AAPLrevenue",
    ]
    assert len(dropped) == 1
