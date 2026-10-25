from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.verification import filing_kit as fk

BS_HTML = """<table><tr><th>CONSOLIDATED BALANCE SHEETS - USD ($) $ in Millions</th><th>Dec. 31, 2020</th><th>Dec. 31, 2019</th></tr>
<tr><td>Total current liabilities</td><td>$ 10</td><td>$ 8</td></tr>
<tr><td>Redeemable noncontrolling interest</td><td>5</td><td>4</td></tr>
<tr><td>Total stockholders' equity</td><td>30</td><td>25</td></tr>
<tr><td>Noncontrolling interests</td><td>2</td><td>1</td></tr>
<tr><td>Total equity</td><td>32</td><td>26</td></tr>
<tr><td>Total liabilities and equity</td><td>100</td><td>(80)</td></tr></table>"""
BS_PRINTED = BS_HTML.replace("<tr><td>Total current liabilities", "<tr><td>Total liabilities</td><td>63</td><td>50</td></tr><tr><td>Total current liabilities")
IS_HTML = """<tr><th>INCOME - USD ($) $ in Thousands</th><th colspan="2">12 Months Ended</th></tr>
<tr><th></th><th>Dec. 31, 2020</th><th>Dec. 31, 2019</th></tr>
<tr><td>Other</td><td></td><td>7</td><td>8</td></tr>
<tr><td>Revenue</td><td>1,000</td><td>(2)</td></tr>"""
SUMMARY = """<Report><ShortName>CONSOLIDATED STATEMENTS OF INCOME</ShortName><HtmlFileName>R4.htm</HtmlFileName></Report>
<Report><ShortName>CONSOLIDATED BALANCE SHEETS (Parenthetical)</ShortName><HtmlFileName>R3.htm</HtmlFileName></Report>
<Report><ShortName>CONSOLIDATED BALANCE SHEETS</ShortName><HtmlFileName>R2.htm</HtmlFileName></Report>
<Report><ShortName>CONSOLIDATED STATEMENTS OF CASH FLOWS</ShortName><HtmlFileName>R7.htm</HtmlFileName></Report>"""


def test_parse_balance_sheet():
    p = fk.parse_rpage(BS_HTML)
    assert p.multiplier == 1_000_000 and p.columns == [date(2020, 12, 31), date(2019, 12, 31)]
    assert p.find("^total liabilities and")[0].values == [Decimal(100), Decimal(-80)]


def test_parse_income_two_header_rows_and_leading_blank_column():
    p = fk.parse_rpage(IS_HTML)
    assert p.multiplier == 1000 and len(p.columns) == 2
    assert p.rows[0].values == [Decimal(7), Decimal(8)]  # aligned from the right
    assert p.rows[1].values == [Decimal(1000), Decimal(-2)]


def test_derived_liabilities_exact_with_mezzanine():
    p = fk.parse_rpage(BS_HTML)
    r = fk.face_liabilities(p, date(2020, 12, 31))
    assert (r.method, r.value) == ("derived", Decimal(63))  # 100 - 32 - 5


def test_mutation_guard_derivation_is_sensitive():
    p = fk.parse_rpage(BS_HTML)
    base = fk.face_liabilities(p, date(2020, 12, 31)).value
    for r in p.rows:  # perturb each input line: the answer must move
        if r.label in ("Total equity", "Total liabilities and equity", "Redeemable noncontrolling interest"):
            old = r.values[0]
            r.values[0] = old + 1
            assert fk.face_liabilities(p, date(2020, 12, 31)).value != base, r.label
            r.values[0] = old
    # NCI row and stockholders' equity row must NOT leak into the answer
    for r in p.rows:
        if r.label in ("Noncontrolling interests", "Total stockholders' equity"):
            r.values[0] += 7
    assert fk.face_liabilities(p, date(2020, 12, 31)).value == base


def test_printed_total_wins_and_unavailable():
    assert fk.face_liabilities(fk.parse_rpage(BS_PRINTED), date(2020, 12, 31)).method == "printed_total"
    assert fk.face_liabilities(fk.parse_rpage(BS_HTML.replace("Total equity", "x").replace("Total stockholders' equity", "y")),
                               date(2020, 12, 31)).method == "unavailable"


def test_cell_matches_tolerance():
    assert fk.cell_matches(Decimal(63_000_000), Decimal(63), 1_000_000)
    assert not fk.cell_matches(Decimal(64_000_000), Decimal(63), 1_000_000)


def test_report_files_and_fetch_mocked():
    assert fk.find_report_files(SUMMARY)["BS"][1] == "R2.htm"
    assert fk.find_report_files(SUMMARY)["IS"][1] == "R4.htm"

    class Fake:
        urls: list[str] = []

        def get(self, url):
            self.urls.append(url)
            return SUMMARY.encode() if url.endswith("FilingSummary.xml") else BS_HTML.encode()

    c = Fake()
    out = fk.fetch_statements(c, "https://www.sec.gov/Archives/edgar/data/1/2/", ("BS",))
    assert out["BS"].rows and len(c.urls) == 2 and c.urls[1].endswith("R2.htm")


def test_seeded_sample_deterministic_and_covers_required():
    m = [{"cik": "1", "instant": f"20{15+i:02d}-12-31", "shown": i != 4, "era": "a" if i < 6 else "b"} for i in range(10)]
    s1, s2 = fk.seeded_sample(m, 7), fk.seeded_sample(m, 7)
    assert s1 == s2
    why = {r["instant"]: r["why"] for r in s1}
    assert why["2015-12-31"] == "first" and why["2024-12-31"] == "last"
    assert why["2021-12-31"] == "boundary" and why["2019-12-31"] == "withheld"


def test_verdict_skeleton_has_all_sections():
    t = fk.verdict_skeleton("BS batch 9", "2026-10-26", "b", "abc", 5, {"ties": 3}, ["r.json"])
    assert all(f"## {s}" in t for s in fk.VERDICT_SECTIONS) and "Seed 5" in t
