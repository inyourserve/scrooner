"""Year presence for the display layer: comparative-only years of the first report, 20-F / 40-F as periodic filings."""

from datetime import date

from scrooner_pipeline.mapper import top100_coverage as t100


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
        "accession": "a",
        "r_page": "R2",
        "_parts_blank": 0,
    }
    r.update(kw)
    return r


def test_comparative_only_year_of_the_first_report_is_hidden_with_evidence():
    # first annual report FY2023 (F1) prints FY2022 only as a comparative column; a later one is F2
    filings = [(date(2023, 12, 31), "F1"), (date(2024, 12, 31), "F2")]
    yp = t100.year_presence(filings, date(2024, 2, 20), date(2022, 12, 31), False)
    assert yp["comparative_only"] and yp["presented"] and not yp["before_first"]
    assert yp["first_presenting"] == "F1"
    # from the first report's own fiscal year onward the flag is off: a gap there stays open
    own = t100.year_presence(filings, date(2024, 2, 20), date(2023, 12, 31), False)
    assert not own["comparative_only"]
    cell = _cell(
        "x",
        2022,
        "REASON",
        "structural_not_presented",
        _comparative_only=True,
        _presented=True,
        _first_presenting="F1",
    )
    own_cell = _cell("x", 2023, "REASON", "structural_not_presented", _presented=True)
    keep = _cell("x", 2024, "PROVEN")
    t100.apply_display([cell, own_cell, keep])
    assert cell["display"] == "HIDDEN_YEAR" and own_cell["display"] == "OPEN"
    ev = t100.hidden_evidence([cell])[1][0]
    assert ev["basis"] == "first_report_comparative_only"
    assert ev["earliest_10k_presenting"] == "F1"


def test_20f_and_40f_are_periodic_filings_for_first_filing_and_presents():
    for f in ("20-F", "20-F/A", "40-F", "40-F/A"):
        assert f in t100.ANNUAL_FORMS and f in t100.PERIODIC_FORMS
    # a 20-F company: first report FY2016 (A1) presents FY2015 as a comparative: presented, not pre-filing
    one = [(date(2016, 12, 31), "A1")]
    yp = t100.year_presence(one, date(2017, 3, 1), date(2015, 12, 31), False)
    assert yp["presented"] and not yp["before_first"] and yp["comparative_only"]
    pre = t100.year_presence(one, date(2017, 3, 1), date(2013, 12, 31), False)
    assert pre["before_first"] and not pre["presented"]


def test_proof_pre_filing_period_is_a_hidden_year_unless_a_periodic_report_presents_it():
    # CRWD cash 2018-01-31: the proof says no balance sheet of the shown filing presents the date
    cell = _cell("cash_and_equivalents", 2018, "REASON", "pre_filing_period", _presented=False)
    shown = _cell("cash_and_equivalents", 2020, "PROVEN")
    t100.apply_display([cell, shown])
    assert cell["display"] == "HIDDEN_YEAR"
    # a periodic report that does present the year keeps it open work (never a silent hide)
    seen = _cell("cash_and_equivalents", 2018, "REASON", "pre_filing_period", _presented=True)
    t100.apply_display([seen, _cell("cash_and_equivalents", 2020, "PROVEN")])
    assert seen["display"] == "OPEN"
