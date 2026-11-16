"""absent_in_own_filing + comparative_fill (DHR/UBER share_buybacks, resolver .63).

FY2020-21 are absent in their own 10-Ks; FY2022-23 are filled as comparatives from the FY2024 10-K, which does not carry
FY2020-21. The later-filing guard must use the filling filing's period (2024), not the filled period (2022), or the
absent years stay OPEN."""

from datetime import date

from scrooner_pipeline.mapper import top100_coverage as t100

HDR = "cik,ticker,data_point,period_end,grain,decision,nodes,value,accession,column,calc_check,flags,resolver_version\n"
LINE = "1,DHR,share_buybacks,{},FY,{},,,{},{},,{},v\n"


def _cell(end):
    return {
        "company_id": 1,
        "rank": 1,
        "ticker": "DHR",
        "data_point": "share_buybacks",
        "fiscal_year": int(end[:4]),
        "period_end": end,
        "class": "UNCHECKED",
        "reason_code": "proof_unchecked",
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
    }


def _csv(tmp_path, comparative_accession):
    (tmp_path / "resolver-all110-2026-11-14.csv").write_text(
        HDR
        + LINE.format("2020-12-31", "not_presented", "A20", "own", "absent_in_own_filing")
        + LINE.format("2021-12-31", "not_presented", "A21", "own", "absent_in_own_filing")
        + LINE.format("2022-12-31", "mapped", comparative_accession, "comparative", "comparative_fill")
        + LINE.format("2023-12-31", "mapped", comparative_accession, "comparative", "comparative_fill")
        + LINE.format("2024-12-31", "mapped", "A24", "own", "cf_family")
    )


def _run(tmp_path):
    proven = {**_cell("2024-12-31"), "class": "PROVEN", "reason_code": ""}  # keeps the row, so years hide as years
    rows = [_cell("2020-12-31"), _cell("2021-12-31"), proven]
    t100.attach_absent_in_own(rows, t100.load_absent_in_own(tmp_path))
    t100.apply_display(rows)
    return rows[:2]


def test_comparative_fill_from_a_later_filing_keeps_the_absent_years_hidden(tmp_path):
    _csv(tmp_path, "A24")
    cells, printed = t100.load_absent_in_own(tmp_path)[("DHR", "share_buybacks")]
    assert set(cells) == {"2020-12-31", "2021-12-31"}
    assert sorted(printed) == [date(2024, 12, 31)] * 3  # own 2024 + two comparatives resolved to the FY2024 filing
    rows = _run(tmp_path)
    assert [r["display"] for r in rows] == ["HIDDEN_YEAR", "HIDDEN_YEAR"]
    assert rows[0]["hide_class"] == "verified_absent"


def test_comparative_from_an_unknown_filing_stays_strict(tmp_path):
    _csv(tmp_path, "UNKNOWN")  # filing period not derivable: the filled period (2022) is used, the guard keeps 2020-21 open
    assert [r["display"] for r in _run(tmp_path)] == ["OPEN", "OPEN"]
