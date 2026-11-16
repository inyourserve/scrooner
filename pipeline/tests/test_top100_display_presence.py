"""Line-level presence: a cell is never hidden when a periodic filing prints THIS data point's line at that period; a
period some filing presents without the line may still be hidden. A never-reported row needs no printed year.

Fixtures are BA and MO cells of the 2026-11-16 certification draws, with the facts read from fsn for those companies
(BA: ComprehensiveIncomeNetOfTax only FY2018-25, PaymentsOfDividendsCommonStock FY2011-20 and FY2025, no
PaymentsForRepurchaseOfCommonStock after FY2019; MO: OtherNonoperatingIncomeExpense FY2013-15 only)."""

from datetime import date

from scrooner_pipeline.mapper import top100_coverage as t100

BA = 1
MO = 1413


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


def _proven(cid, tk, dp, fy):
    return _cell(cid, tk, dp, fy, **{"class": "PROVEN"})


def _run(rows, presence):
    t100.attach_presence(rows, presence)
    t100.apply_display(rows)


def _facts(tag, years, q=4):
    return [(date(y, 12, 31), tag, q) for y in years]


def test_a_line_a_periodic_filing_presents_is_open_on_every_hidden_year_route():
    ci = [
        _cell(BA, "BA", "comprehensive_income", fy, _only_combined="years")
        for fy in (2018, 2019)
    ]
    divs = [_cell(BA, "BA", "dividends_paid", 2025, _absent_own=True)]
    keep = [
        _proven(BA, "BA", "comprehensive_income", 2026),
        _proven(BA, "BA", "dividends_paid", 2026),
    ]
    rows = ci + divs + keep
    pres = {
        BA: _facts("ComprehensiveIncomeNetOfTax", (2018, 2019))
        + _facts("PaymentsOfDividendsCommonStock", (2025,))
    }
    _run(rows, pres)
    assert [r["display"] for r in ci + divs] == ["OPEN", "OPEN", "OPEN"]


def test_a_period_presented_without_the_line_may_still_be_hidden():
    # BA FY2015-17 comprehensive income and FY2022-25 buybacks: every statement of those years is printed, the line is not
    ci = [
        _cell(BA, "BA", "comprehensive_income", fy, _only_combined="years")
        for fy in (2015, 2016, 2017)
    ]
    bb = [
        _cell(BA, "BA", "share_buybacks", fy, _absent_own=True)
        for fy in (2022, 2023, 2024, 2025)
    ]
    keep = [
        _proven(BA, "BA", "comprehensive_income", 2026),
        _proven(BA, "BA", "share_buybacks", 2026),
    ]
    rows = ci + bb + keep
    pres = {
        BA: _facts("Assets", range(2011, 2027), 0)
        + _facts("Revenues", range(2011, 2027))
        + _facts("ComprehensiveIncomeNetOfTax", (2018, 2019))
        + _facts("PaymentsForRepurchaseOfCommonStock", range(2013, 2020))
    }
    _run(rows, pres)
    assert {r["display"] for r in ci + bb} == {"HIDDEN_YEAR"}


def test_a_line_printed_in_a_tenq_instant_comparative_presents_the_year():
    rows = [
        _cell(BA, "BA", "shares_outstanding", 2019, _absent_own=True),
        _proven(BA, "BA", "shares_outstanding", 2026),
    ]
    _run(rows, {BA: _facts("CommonStockSharesOutstanding", (2019,), 0)})
    assert rows[0]["display"] == "OPEN"
    # the same tag at an annual duration is not the instant line of a balance-sheet point
    rows = [
        _cell(BA, "BA", "shares_outstanding", 2019, _absent_own=True),
        _proven(BA, "BA", "shares_outstanding", 2026),
    ]
    _run(rows, {BA: _facts("CommonStockSharesOutstanding", (2019,), 4)})
    assert rows[0]["display"] == "HIDDEN_YEAR"


def test_mo_never_reported_row_with_a_printed_year_is_not_a_hidden_row():
    def mo_rows():
        return [
            _cell(MO, "MO", "other_income_expense_net", fy, _only_combined="row")
            for fy in range(2015, 2026)
        ]

    rows = mo_rows()
    _run(rows, {})
    assert {r["display"] for r in rows} == {"HIDDEN_ROW"}
    # the FY2015 10-K prints OtherNonoperatingIncomeExpense (R4): the row is not hidden, cells are judged per year
    rows = mo_rows()
    _run(rows, {MO: _facts("OtherNonoperatingIncomeExpense", (2015,))})
    assert {r["display"] for r in rows} == {"OPEN"}


def test_family_hit_is_per_data_point_and_period():
    rows = [
        _cell(MO, "MO", "other_income_expense_net", 2015),
        _cell(MO, "MO", "other_income_expense_net", 2016),
        _cell(MO, "MO", "sbc", 2015),
    ]
    t100.attach_presence(rows, {MO: _facts("OtherNonoperatingIncomeExpense", (2015,))})
    assert [r["_family_hit"] for r in rows] == [True, False, False]
