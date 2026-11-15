"""only_combined matching on 52/53-week ends, and the proof's pre_filing_period reason as a hidden year."""

from scrooner_pipeline.mapper import top100_coverage as t100


def _cell(dp, end, cls, code="", **kw):
    r = {
        "company_id": 1,
        "rank": 1,
        "ticker": "ADI",
        "data_point": dp,
        "fiscal_year": int(end[:4]),
        "period_end": end,
        "class": cls,
        "reason_code": code,
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
    }
    r.update(kw)
    return r


def test_only_combined_matches_a_52_53_week_end_to_the_month_end_key():
    oc = {
        ("ADI", "cf_ap", "2016-10-31"): ("row", "reported only combined: L", "A1"),
        ("ADI", "x", "2016-10-31"): ("row", "reported only combined: X", "A2"),
        ("ADI", "x", "2016-11-05"): ("row", "reported only combined: X", "A3"),
    }
    rows = [
        _cell("cf_ap", "2016-10-29", "REASON", "line_presented_combined"),
        # two resolver periods within tolerance of the cell: ambiguous, no hide
        _cell("x", "2016-11-01", "REASON", "line_presented_combined"),
        # another data point or ticker never matches
        _cell("other", "2016-10-29", "REASON", "line_presented_combined"),
        _cell("cf_ap", "2016-10-29", "REASON", "line_presented_combined", ticker="ZZZ"),
        # a different year does not match
        _cell("cf_ap", "2015-10-31", "REASON", "line_presented_combined"),
    ]
    t100.attach_only_combined(rows, oc)
    t100.apply_display(rows)
    assert rows[0]["display"] == "HIDDEN_ROW" and rows[0]["accession"] == "A1"
    assert [r["display"] for r in rows[1:]] == ["OPEN"] * 4


def test_proof_pre_filing_period_is_a_hidden_year():
    rows = [
        _cell(
            "a",
            "2015-12-31",
            "REASON",
            "pre_filing_period",
            _presented=False,
            _comparative_only=False,
        ),
        _cell("a", "2016-12-31", "PROVEN", accession="Z", r_page="R2"),
    ]
    t100.apply_display(rows)
    assert rows[0]["display"] == "HIDDEN_YEAR"
