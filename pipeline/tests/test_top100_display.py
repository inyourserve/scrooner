"""Display layer of the top-100 coverage report (founder 2026-11-16): shown value / hidden row / hidden year / open."""

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


def test_display_rows_years_values_and_open():
    rows = [
        _cell("a", 2020, "PROVEN"),
        _cell("a", 2021, "DERIVED"),
        # never reported in any year -> hidden row
        _cell("b", 2020, "REASON", "structural_not_presented"),
        _cell("b", 2021, "REASON", "docmap_not_presented"),
        # not presented in one year, a value in another -> gap inside a row: OPEN
        _cell("c", 2020, "REASON", "structural_not_presented"),
        _cell("c", 2021, "PROVEN"),
        # a combined year keeps the whole row visible
        _cell("d", 2020, "REASON", "line_presented_combined"),
        _cell("d", 2021, "REASON", "structural_not_presented"),
        # pre-filing year (no periodic report presents it) is hidden, the rest of the row stays
        _cell("e", 2019, "BLANK", "x", _before_first_filing=True, _presented=False),
        _cell("e", 2020, "PROVEN"),
        # a later 10-K comparative presents the period: never hidden
        _cell("f", 2019, "REASON", "no_public_filing_for_period", _presented=True),
        _cell("f", 2020, "PROVEN"),
        _cell("g", 2020, "UNCHECKED", "no_proof_row"),
        _cell("g", 2021, "HELD", "held_x"),
        _cell("g", 2022, "DISAGREE", "x"),
        _cell("g", 2023, "BLANK", "no_value_no_reason"),
    ]
    t100.apply_display(rows)
    d = {(r["data_point"], r["fiscal_year"]): r["display"] for r in rows}
    assert d[("a", 2020)] == d[("a", 2021)] == "SHOWN_VALUE"
    assert d[("b", 2020)] == d[("b", 2021)] == "HIDDEN_ROW"
    assert d[("c", 2020)] == "OPEN" and d[("c", 2021)] == "SHOWN_VALUE"
    assert d[("d", 2020)] == d[("d", 2021)] == "OPEN"
    assert d[("e", 2019)] == "HIDDEN_YEAR"
    assert d[("f", 2019)] == "OPEN"
    assert [d[("g", y)] for y in (2020, 2021, 2022, 2023)] == ["OPEN"] * 4
    work = {(r["data_point"], r["fiscal_year"]): t100.work_type(r) for r in rows}
    assert work[("d", 2020)] == "combined_split" and work[("c", 2020)] == "gap_fill"
    assert [work[("g", y)] for y in (2020, 2021, 2022, 2023)] == [
        "proof",
        "held",
        "proof",
        "blank",
    ]


def test_registration_statement_switch_defaults_to_no(monkeypatch):
    # ruling Dhairya 2026-11-16: Form 10 / S-1 / F-1 do not present a year; default False
    assert t100.REGISTRATION_STATEMENT_PRESENTS_YEAR is False
    r = [_cell("e", 2019, "BLANK", "x", _before_first_filing=True, _presented=False)]
    monkeypatch.setattr(t100, "REGISTRATION_STATEMENT_PRESENTS_YEAR", True)
    t100.apply_display(r)
    assert r[0]["display"] == "OPEN"


def test_hidden_evidence_and_open_queue():
    rows = [
        _cell("a", 2020, "PROVEN"),
        _cell(
            "b",
            2020,
            "REASON",
            "structural_not_presented",
            _latest_10k="a",
            _first_10k="z",
        ),
        _cell("c", 2020, "REASON", "no_10k_presents_period"),
        _cell("c", 2021, "PROVEN"),
        _cell("d", 2020, "UNCHECKED", "no_proof_row"),
    ]
    t100.apply_display(rows)
    hr, hy = t100.hidden_evidence(rows)
    assert len(hr) == 1 and hr[0]["both_10ks_cited"] == "no"
    assert len(hy) == 1 and hy[0]["basis"] == "evidenced_no_period_reason"
    assert [r["work"] for r in t100.open_rows(rows)] == ["proof"]


def test_summary_certified_needs_no_open_and_locators():
    class Co:
        rank, ticker, company_id = 1, "T", 1

    ok = [
        _cell("a", 2020, "PROVEN"),
        _cell("b", 2020, "REASON", "docmap_not_presented"),
    ]
    bad = [_cell("a", 2020, "PROVEN", r_page="")]
    for rows, want in ((ok, "yes"), (bad, "no")):
        t100.apply_display(rows)
        s = t100.summarize(rows, [Co()], {}, "x")[0]
        assert s["display_certified"] == want
    s = t100.summarize(ok, [Co()], {}, "x")[0]
    assert (s["shown_cells"], s["shown_values"], s["hidden_rows"]) == (1, 1, 1)
    assert s["pct_shown_values"] == "100.0"
