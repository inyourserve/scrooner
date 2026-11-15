"""only_combined hides (resolver .37, Dhairya 2026-11-16): read from the resolver file, never recomputed."""

from scrooner_pipeline.mapper import top100_coverage as t100

HEADER = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"


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


def test_loader_reads_flags_of_the_newest_resolver_file(tmp_path):
    (tmp_path / "resolver-all110-2026-11-14.csv").write_text(
        HEADER + "1,T,a,2020-12-31,FY,combined,x,,OLD,,,only_combined;only_combined_row,r.36\n"
    )
    (tmp_path / "resolver-all110-2026-11-20.csv").write_text(
        HEADER
        + "1,T,a,2020-12-31,FY,combined,CostsAndExpenses=1 [R2.htm:14] | why: w | reported only combined: Total expenses,,ACC1,own,ok,roles;only_combined;only_combined_row,r.37\n"
        + "1,T,b,2021-12-31,FY,combined,y | reported only combined: Inv income,,ACC2,own,ok,only_combined;only_combined_years,r.37\n"
        + "1,T,c,2021-12-31,FY,combined,y,,ACC3,own,ok,roles,r.37\n"
        + "1,T,d,2021-12-31,Q1,combined,y | reported only combined: q,,ACC4,own,ok,only_combined;only_combined_row,r.37\n"
    )
    oc = t100.load_only_combined(tmp_path)
    assert oc == {
        ("T", "a", "2020-12-31"): ("row", "reported only combined: Total expenses", "ACC1"),
        ("T", "b", "2021-12-31"): ("years", "reported only combined: Inv income", "ACC2"),
    }
    assert t100.load_only_combined(tmp_path / "none") == {}


def test_only_combined_row_and_years_hide_with_evidence_and_accession():
    oc = {
        ("T", "a", "2020-12-31"): ("row", "reported only combined: L1", "A1"),
        ("T", "a", "2021-12-31"): ("row", "reported only combined: L1", "A2"),
        ("T", "b", "2020-12-31"): ("years", "reported only combined: L2", "A3"),
    }
    rows = [
        _cell("a", 2020, "REASON", "line_presented_combined"),
        _cell("a", 2021, "REASON", "line_presented_combined"),
        _cell("b", 2020, "REASON", "line_presented_combined"),
        _cell("b", 2021, "PROVEN", accession="Z", r_page="R2"),
        _cell("c", 2020, "REASON", "line_presented_combined"),
    ]
    t100.attach_only_combined(rows, oc)
    t100.apply_display(rows)
    d = {(r["data_point"], r["fiscal_year"]): r for r in rows}
    assert d[("a", 2020)]["display"] == d[("a", 2021)]["display"] == "HIDDEN_ROW"
    assert d[("a", 2021)]["evidence"] == "reported only combined: L1"
    assert d[("a", 2021)]["accession"] == "A2"
    assert d[("b", 2020)]["display"] == "HIDDEN_YEAR"
    assert d[("b", 2021)]["display"] == "SHOWN_VALUE"
    # not flagged: stays open work (split it)
    assert d[("c", 2020)]["display"] == "OPEN"
    hr, hy = t100.hidden_evidence(rows)
    assert hr[0]["evidence"] == "reported only combined: L1"
    assert hy[0]["basis"] == "reported_only_combined" and hy[0]["evidence_accession"] == "A3"


def test_a_row_hide_never_beats_a_shown_value_in_the_same_row():
    oc = {("T", "a", "2020-12-31"): ("row", "reported only combined: L", "A1")}
    rows = [
        _cell("a", 2020, "REASON", "line_presented_combined"),
        _cell("a", 2021, "PROVEN", accession="Z", r_page="R2"),
    ]
    t100.attach_only_combined(rows, oc)
    t100.apply_display(rows)
    assert rows[0]["display"] == "OPEN"
