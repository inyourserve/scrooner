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
BS_PRINTED = BS_HTML.replace(
    "<tr><td>Total current liabilities",
    "<tr><td>Total liabilities</td><td>63</td><td>50</td></tr><tr><td>Total current liabilities",
)
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
    assert p.multiplier == 1_000_000 and p.columns == [
        date(2020, 12, 31),
        date(2019, 12, 31),
    ]
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
        if r.label in (
            "Total equity",
            "Total liabilities and equity",
            "Redeemable noncontrolling interest",
        ):
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
    assert (
        fk.face_liabilities(fk.parse_rpage(BS_PRINTED), date(2020, 12, 31)).method
        == "printed_total"
    )
    assert (
        fk.face_liabilities(
            fk.parse_rpage(
                BS_HTML.replace("Total equity", "x").replace(
                    "Total stockholders' equity", "y"
                )
            ),
            date(2020, 12, 31),
        ).method
        == "unavailable"
    )


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
            return (
                SUMMARY.encode()
                if url.endswith("FilingSummary.xml")
                else BS_HTML.encode()
            )

    c = Fake()
    out = fk.fetch_statements(
        c, "https://www.sec.gov/Archives/edgar/data/1/2/", ("BS",)
    )
    assert out["BS"].rows and len(c.urls) == 2 and c.urls[1].endswith("R2.htm")


def test_seeded_sample_deterministic_and_covers_required():
    m = [
        {
            "cik": "1",
            "instant": f"20{15 + i:02d}-12-31",
            "shown": i != 4,
            "era": "a" if i < 6 else "b",
        }
        for i in range(10)
    ]
    s1, s2 = fk.seeded_sample(m, 7), fk.seeded_sample(m, 7)
    assert s1 == s2
    why = {r["instant"]: r["why"] for r in s1}
    assert why["2015-12-31"] == "first" and why["2024-12-31"] == "last"
    assert why["2021-12-31"] == "boundary" and why["2019-12-31"] == "withheld"


def test_verdict_skeleton_has_all_sections():
    t = fk.verdict_skeleton(
        "BS batch 9", "2026-10-26", "b", "abc", 5, {"ties": 3}, ["r.json"]
    )
    assert all(f"## {s}" in t for s in fk.VERDICT_SECTIONS) and "Seed 5" in t


def _page(rows, cols=("Dec. 31, 2020",), head="BALANCE SHEETS - USD ($) $ in Millions"):
    h = f"<tr><th>{head}</th>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>"
    body = "".join(
        f"<tr><td class='pl'>{lab}</td>"
        + "".join(f"<td class='nump'>{v}</td>" for v in vals)
        + "</tr>"
        for lab, *vals in rows
    )
    return fk.parse_rpage(h + body)


D = date(2020, 12, 31)


def test_report_selection_pairs_name_with_own_file_and_skips_misspelt_parenthetical():
    xml = (
        "<Report><HtmlFileName>R3.htm</HtmlFileName><ShortName>Balance Sheets (Paranthetical)</ShortName></Report>"
        "<Report><HtmlFileName>R2.htm</HtmlFileName><ShortName>Balance Sheets</ShortName></Report>"
        "<Report><HtmlFileName>R4.htm</HtmlFileName><ShortName>Statements of Operations and Comprehensive Income</ShortName></Report>"
    )
    got = fk.find_report_files(xml)
    assert got["BS"] == ("Balance Sheets", "R2.htm") and got["IS"][1] == "R4.htm"


def test_old_page_element_name_suffix_and_separate_footnote_cells():
    assert fk.parse_number("2,341,284us-gaap_Liabilities") == Decimal(2341284)
    html = (
        "<tr><th>BS (USD $)In Millions</th><th>Mar. 31, 2015</th><th>Dec. 31, 2014</th></tr>"
        "<tr><td>Total liabilities</td><td class='nump'>2,341,284us-gaap_Liabilities</td><td class='fn'>[1]</td>"
        "<td class='nump'>2,341,046us-gaap_Liabilities</td><td class='fn'>[1]</td></tr>"
        "<tr><td>X</td><td></td><td></td></tr>"
    )
    p = fk.parse_rpage(html)
    assert p.rows[0].values == [Decimal(2341284), Decimal(2341046)] and len(p.rows) == 1


def test_header_footnote_column_and_trailing_fn_cells():
    html = (
        "<tr><th>BS - USD ($)</th><th>Sep. 30, 2025</th><th>Dec. 31, 2024</th><th><sup>[1]</sup></th></tr>"
        "<tr><td>Total liabilities</td><td class='th'><sup></sup></td><td class='nump'>$ 5</td><td class='nump'>$ 4</td><td class='fn'></td></tr>"
    )
    p = fk.parse_rpage(html)
    assert len(p.columns) == 2 and p.rows[0].values == [Decimal(5), Decimal(4)]


@pytest.mark.parametrize(
    "le_label,eq_label",
    [
        (
            "Total liabilities, redeemable noncontrolling interests, and shareholders' equity",
            "Total shareholders' equity",
        ),
        (
            "TOTAL LIABILITIES, NONCONTROLLING INTERESTS IN THE OPERATING PARTNERSHIP AND SHAREHOLDERS' EQUITY",
            "Total shareholders' equity",
        ),
        ("Total liabilities, preferred units, and equity", "Total partners' equity"),
        ("TOTAL CAPITALIZATION AND LIABILITIES", "Total common stockholders' equity"),
        ("Liabilities and Shareholders' equity, Total", "Total shareholders' equity"),
        (
            "Total liabilities and equity",
            "Stockholders' Equity, Including Portion Attributable to Noncontrolling Interest",
        ),
        ("Total", "Total shareholders' equity"),
    ],
)
def test_label_variants(le_label, eq_label):
    p = _page(
        [
            ("Total assets", 100),
            ("Accounts payable", 10),
            (eq_label, 40),
            (le_label, 100),
        ]
    )
    r = fk.face_liabilities(p, D)
    assert r.method == "derived" and r.value == Decimal(60), r


def test_combined_filing_uses_first_registrant_block():
    p = _page(
        [
            ("Accounts payable", 5),
            ("Total equity", 40),
            ("Total liabilities and equity", 100),
            ("Accounts payable", 1),
            ("Total equity", 13),
            ("Total liabilities and equity", 30),
        ]
    )
    r = fk.face_liabilities(p, D)
    assert r.value == Decimal(60) and r.combined


def test_redeemable_preferred_inside_debt_is_not_mezzanine_but_real_mezzanine_is():
    awk = _page(
        [
            ("Total common stockholders' equity", 40),
            ("Long-term debt", 90),
            ("Redeemable preferred stock at redemption value", 8),
            ("Total long-term debt", 98),
            ("TOTAL CAPITALIZATION AND LIABILITIES", 200),
        ]
    )
    assert fk.face_liabilities(awk, D).value == Decimal(160)
    khc = _page(
        [
            ("Total current liabilities", 10),
            ("Redeemable preferred stock", 8),
            ("Common stock", 1),
            ("Total shareholders' equity", 40),
            ("Total liabilities and equity", 100),
        ]
    )
    assert fk.face_liabilities(khc, D).value == Decimal(52)
    wmt = _page(
        [
            ("Nonredeemable noncontrolling interest", 3),
            ("Total equity", 40),
            ("Total liabilities and equity", 100),
        ]
    )
    assert fk.face_liabilities(wmt, D).value == Decimal(60)


def test_equity_on_common_stock_line_only_when_it_foots():
    ok = _page(
        [
            ("Additional paid in capital", 7),
            ("Retained earnings", 5),
            ("Common stock - authorized", 12),
            ("Total liabilities and equity", 50),
        ]
    )
    assert fk.face_liabilities(ok, D).value == Decimal(38)
    bad = _page(
        [
            ("Additional paid in capital", 7),
            ("Retained earnings", 5),
            ("Common stock - authorized", 13),
            ("Total liabilities and equity", 50),
        ]
    )
    assert fk.face_liabilities(bad, D).method == "unavailable"


def test_position_rules_for_mezzanine():
    debt_first = _page(
        [
            ("Long-term debt", 90),
            ("Redeemable preferred stock", 8),
            ("Total long-term debt", 98),
            ("Total shareholders' equity", 40),
            ("Total liabilities and equity", 200),
        ]
    )
    assert fk.face_liabilities(debt_first, D).value == Decimal(
        160
    )  # redeemable inside debt: not mezzanine
    in_equity = _page(
        [
            ("Total current liabilities", 10),
            ("Common stock", 1),
            ("Redeemable preferred in equity section", 3),
            ("Total shareholders' equity", 40),
            ("Total liabilities and equity", 100),
        ]
    )
    assert fk.face_liabilities(in_equity, D).value == Decimal(
        60
    )  # after equity starts: not mezzanine
    one_row = _page(
        [
            ("Retained earnings", 12),
            ("Common stock - authorized", 12),
            ("Total liabilities and equity", 50),
        ]
    )
    assert (
        fk.face_liabilities(one_row, D).method == "unavailable"
    )  # a single row never 'foots'


def test_epd_convertible_preferred_units_between_liabilities_and_equity():
    p = _page(
        [
            ("Total current liabilities", 10),
            ("Redeemable preferred limited partner interests", None),
            (
                "Series A cumulative convertible preferred units (50,000 units outstanding)",
                49,
            ),
            ("Total equity", 26000),
            ("Total liabilities, preferred units, and equity", 63736),
        ]
    )
    assert fk.face_liabilities(p, D).value == Decimal(63736 - 26000 - 49)


def test_idacorp_bare_total_picks_first_total_after_equity():
    p = _page(
        [
            ("Total current assets", 5),
            ("Total", 6609),
            ("Total current liabilities", 2),
            ("Total equity", 2473),
            ("Total", 6609),
            ("Total current assets", 4),
            ("Total", 6453),
            ("Total equity", 2279),
            ("Total capitalization", 4116),
            ("Total", 6453),
        ]
    )
    r = fk.face_liabilities(p, D)
    assert r.value == Decimal(6609 - 2473) and r.combined


def test_ldos_le_printed_before_equity_section():
    p = _page(
        [
            ("Total assets", 9132),
            ("Total current liabilities", 2016),
            ("Total liabilities and stockholders' equity", 9132),
            ("Total equity", 3147),
            ("Total stockholder's equity", 3135),
        ]
    )
    assert fk.face_liabilities(p, D).value == Decimal(5985)
