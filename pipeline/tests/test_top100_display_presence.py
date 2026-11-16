"""One presence test for every hidden year, and a never-reported row must have no printed year.

Fixtures are the actual BA and MO cells of the 2026-11-16 certification draws (BA 18 HIDDEN_YEAR: comprehensive_income
FY2015-19 via only_combined years, dividends_per_share FY2020-25 and share_buybacks FY2022-25 via absent_in_own;
MO other_income_expense_net hidden as never reported although FY2015 prints OtherNonoperatingIncomeExpense), with the
facts read from fsn for those companies."""

from datetime import date

from scrooner_pipeline.mapper import top100_coverage as t100


def _cell(company_id, ticker, dp, fy, **kw):
    r = {
        "company_id": company_id,
        "rank": 1,
        "ticker": ticker,
        "data_point": dp,
        "fiscal_year": fy,
        "period_end": f"{fy}-12-31",
        "class": "REASON",
        "reason_code": "line_presented_combined",
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
        "_presented": True,
    }
    r.update(kw)
    return r


def _year_facts(first, last):
    # the certifier's year-end tag (Assets) printed by a periodic filing for every BA year end
    return [(date(y, 12, 31), "Assets", 0) for y in range(first, last + 1)]


BA = 1
MO = 1413


def _run(rows, presence):
    t100.attach_presence(rows, presence)
    t100.apply_display(rows)


def test_ba_hidden_years_presented_by_a_periodic_filing_are_open_on_every_route():
    rows = (
        [  # only_combined years route
            _cell(BA, "BA", "comprehensive_income", fy, _only_combined="years")
            for fy in range(2015, 2020)
        ]
        + [  # absent_in_own route
            _cell(BA, "BA", "dividends_per_share", fy, _absent_own=True)
            for fy in range(2020, 2026)
        ]
        + [
            _cell(BA, "BA", "share_buybacks", fy, _absent_own=True)
            for fy in range(2022, 2026)
        ]
        + [  # a proven value in each row keeps the group from collapsing into a hidden row
            _cell(BA, "BA", dp, 2026, **{"class": "PROVEN"})
            for dp in ("comprehensive_income", "dividends_per_share", "share_buybacks")
        ]
    )
    _run(rows, {BA: _year_facts(2011, 2026)})
    hidden = [r for r in rows if r["display"] in ("HIDDEN_YEAR", "HIDDEN_ROW")]
    assert hidden == []
    assert sum(r["display"] == "OPEN" for r in rows) == 15


def test_a_year_no_periodic_filing_presents_stays_hidden():
    rows = [
        _cell(BA, "BA", "comprehensive_income", 2005, _only_combined="years"),
        _cell(BA, "BA", "comprehensive_income", 2015, _only_combined="years"),
        _cell(BA, "BA", "comprehensive_income", 2026, **{"class": "PROVEN"}),
    ]
    _run(rows, {BA: _year_facts(2011, 2026)})
    assert [r["display"] for r in rows] == ["HIDDEN_YEAR", "OPEN", "SHOWN_VALUE"]


def test_a_tenq_instant_comparative_presents_the_year():
    # the facts of a 10-Q are in the same list (company_filings covers 10-Q); a prior-year-end instant counts
    rows = [
        _cell(BA, "BA", "inventory", 2019, _absent_own=True),
        _cell(BA, "BA", "inventory", 2026, **{"class": "PROVEN"}),
    ]
    _run(rows, {BA: [(date(2019, 12, 31), "Assets", 0)]})
    assert rows[0]["display"] == "OPEN"


def test_mo_never_reported_row_with_a_printed_year_is_not_a_hidden_row():
    def mo_rows():
        return [
            _cell(MO, "MO", "other_income_expense_net", fy, _only_combined="row")
            for fy in range(2015, 2026)
        ]

    # no year prints the line: still a hidden row
    rows = mo_rows()
    _run(rows, {})
    assert {r["display"] for r in rows} == {"HIDDEN_ROW"}
    # FY2015 10-K prints OtherNonoperatingIncomeExpense (R4): the row is not hidden, every cell is judged per year
    rows = mo_rows()
    _run(rows, {MO: [(date(2015, 12, 31), "OtherNonoperatingIncomeExpense", 4)]})
    assert {r["display"] for r in rows} == {"OPEN"}


def test_presence_attaches_only_a_family_tag_to_the_row():
    rows = [
        _cell(MO, "MO", "other_income_expense_net", 2015),
        _cell(MO, "MO", "sbc", 2015),
    ]
    t100.attach_presence(
        rows, {MO: [(date(2015, 12, 31), "OtherNonoperatingIncomeExpense", 4)]}
    )
    assert [r["_family_hit"] for r in rows] == [True, False]
    assert [r["_year_presented_any"] for r in rows] == [False, False]
