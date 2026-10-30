"""Income-statement reader: one fixture per Verifier case (BAH, SM, WDAY, STE, LNG, VRSN, AKTX).
Fixtures copy the real R-page structure (two-row header with rowspan, 'N Months Ended'
colspans, spacer th cells, empty text cells), with the real values."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.verification import filing_kit as fk


def _page(title, spans, dates, rows, spacer=False):
    """spans: [(text, colspan)], dates: ['Mar. 31, 2026', ...], rows: [(label, [cells])]."""
    tl = f'<th class="tl" colspan="{2 if spacer else 1}" rowspan="2"><div><strong>{title}</strong></div></th>'
    h1 = (
        "<tr>"
        + tl
        + "".join(f'<th class="th" colspan="{c}">{t}</th>' for t, c in spans)
        + "</tr>"
    )
    h2 = (
        "<tr>" + "".join(f'<th class="th"><div>{d}</div></th>' for d in dates) + "</tr>"
    )
    sp = '<td class="th"><sup></sup></td>' if spacer else ""
    body = ""
    for label, cells in rows:
        tds = "".join(
            f'<td class="nump">{c}<span></span></td>'
            if c is not None
            else '<td class="text">&#160;<span></span></td>'
            for c in cells
        )
        body += f'<tr class="ro"><td class="pl"><a>{label}</a></td>{sp}{tds}</tr>'
    return fk.parse_rpage(h1 + h2 + body)


def _summary(*reports):
    return "".join(
        f"<Report instance='x'><HtmlFileName>{f}</HtmlFileName><ShortName>{n}</ShortName>"
        f"<MenuCategory>{c}</MenuCategory></Report>"
        for n, f, c in reports
    )


# ---- BAH FY2025: the second header row has no title cell, its first date must stay
def test_bah_fy2025_first_column_not_dropped():
    p = _page(
        "CONSOLIDATED STATEMENTS OF OPERATIONS - USD ($) $ in Millions",
        [("12 Months Ended", 3)],
        ["Mar. 31, 2026", "Mar. 31, 2025", "Mar. 31, 2024"],
        [
            ("Revenue", ["$ 11,217", "$ 11,980", "$ 10,662"]),
            ("Net income", ["851", "935", "606"]),
        ],
    )
    assert p.columns == [
        date(2026, 3, 31),
        date(2025, 3, 31),
        date(2024, 3, 31),
    ] and p.months == [12, 12, 12]
    ni = fk.net_income_lines(p)[0][1]
    assert ni.values[p.column(date(2025, 3, 31))] == Decimal(935)
    # printed precision: millions with 0 decimals = unit 1,000,000, whatever the digits say
    assert p.printed_unit(ni, 1) == Decimal(1_000_000)


# ---- SM Q3 2025 10-Q: 3 and 9 months share end dates
SM = lambda: _page(
    "CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (UNAUDITED) - USD ($) $ in Thousands",
    [("3 Months Ended", 2), ("9 Months Ended", 2)],
    ["Sep. 30, 2025", "Sep. 30, 2024", "Sep. 30, 2025", "Sep. 30, 2024"],
    [
        ("Operating expenses:", [None] * 4),
        ("Net income", ["155,088", "240,523", "539,022", "582,015"]),
    ],
)


def test_sm_duplicate_end_dates_need_months():
    p = SM()
    assert p.months == [3, 3, 9, 9]
    with pytest.raises(fk.AmbiguousColumn):
        p.column(date(2024, 9, 30))
    ni = fk.net_income_lines(p)[0][1]
    assert ni.values[p.column(date(2024, 9, 30), months=9)] == Decimal(582015)
    assert ni.values[p.column(date(2024, 9, 30), months=3)] == Decimal(240523)


# ---- WDAY Q3 FY2023 10-Q (9M prior-year net income 102,626) and FY page selection
def test_wday_nine_month_prior_year_and_parenthetical_skipped():
    p = _page(
        "Condensed Consolidated Statements of Operations - USD ($) $ in Thousands",
        [("3 Months Ended", 2), ("9 Months Ended", 2)],
        ["Oct. 31, 2022", "Oct. 31, 2021", "Oct. 31, 2022", "Oct. 31, 2021"],
        [("Net income (loss)", ["(74,721)", "43,412", "(241,052)", "102,626"])],
    )
    ni = fk.net_income_lines(p)[0][1]
    assert ni.values[p.column(date(2021, 10, 31), months=9)] == Decimal(102626)
    xml = _summary(
        (
            "Consolidated Statements of Operations (Parenthetical)",
            "R6.htm",
            "Statements",
        ),
        ("Consolidated Statements of Operations", "R5.htm", "Statements"),
    )
    assert fk.select_income_statement(xml) == (
        "Consolidated Statements of Operations",
        "R5.htm",
        False,
    )


# ---- STE FY2025: NCI and attributable lines stay labelled; Gross Profit is not net income
def test_ste_nci_and_attributable_kept_apart():
    p = _page(
        "CONSOLIDATED STATEMENTS OF OPERATIONS - USD ($) $ in Thousands",
        [("12 Months Ended", 3)],
        ["Mar. 31, 2025", "Mar. 31, 2024", "Mar. 31, 2023"],
        [
            ("Gross Profit", ["2,402,764", "2,218,160", "1,980,726"]),
            ("Net income", ["616,074", "380,079", "105,813"]),
            (
                "Less: Net income (loss) attributable to noncontrolling interests",
                ["1,433", "1,840", "(1,217)"],
            ),
            (
                "Net income attributable to shareholders",
                ["614,641", "378,239", "107,030"],
            ),
            ("Basic earnings per share", [None] * 3),
            ("Net income attributable to shareholders", ["2.5", "1.6", "0.4"]),
        ],
    )
    got = {k: r.values[0] for k, r in fk.net_income_lines(p)}
    assert got == {
        "consolidated": Decimal(616074),
        "nci": Decimal(1433),
        "attributable": Decimal(614641),
    }


# ---- LNG 10-Q: title cell colspan 2 + spacer th cells in data rows
def test_lng_spacer_cells_do_not_shift_columns():
    p = _page(
        "Consolidated Statements of Operations - USD ($) $ in Millions",
        [("3 Months Ended", 2), ("9 Months Ended", 2)],
        ["Sep. 30, 2022", "Sep. 30, 2021", "Sep. 30, 2022", "Sep. 30, 2021"],
        [
            ("Revenues", [None] * 4),
            ("Net loss", ["(2,644)", "(916)", "(2,512)", "(476)"]),
            (
                "Net loss attributable to common stockholders",
                ["(2,385)", "(1,084)", "(2,509)", "(1,020)"],
            ),
        ],
        spacer=True,
    )
    att = next(r for k, r in fk.net_income_lines(p) if k == "attributable")
    assert att.values[p.column(date(2021, 9, 30), months=9)] == Decimal(-1020)
    assert att.values[p.column(date(2022, 9, 30), months=3)] == Decimal(-2385)


# ---- VRSN: only a comprehensive-income page; EPS rows also say 'Net Income'; one decimal
def test_vrsn_comprehensive_only_page_and_eps_rows_ignored():
    xml = _summary(
        ("Condensed Consolidated Balance Sheets", "R2.htm", "Statements"),
        (
            "Condensed Consolidated Statements Of Comprehensive Income",
            "R4.htm",
            "Statements",
        ),
        ("Calculation Of Net Income Per Share", "R11.htm", "Notes"),
    )
    _n, f, combined = fk.select_income_statement(xml)
    assert f == "R4.htm" and combined
    p = _page(
        "Condensed Consolidated Statements Of Comprehensive Income - USD ($) $ in Millions",
        [("3 Months Ended", 2), ("9 Months Ended", 2)],
        ["Sep. 30, 2023", "Sep. 30, 2022", "Sep. 30, 2023", "Sep. 30, 2022"],
        [
            ("Net Income", ["188.5", "169.5", "552.9", "494.3"]),
            ("Earnings per share:", [None] * 4),
            ("Net Income", ["1.83", "1.58", "5.32", "4.55"]),
        ],
    )
    lines = fk.net_income_lines(p)
    assert len(lines) == 1
    row = lines[0][1]
    c = p.column(date(2023, 9, 30), months=9)
    assert row.values[c] == Decimal("552.9") and p.printed_unit(row, c) == Decimal(
        100_000
    )


# ---- AKTX: combined operations + comprehensive loss, thousands, 'Net loss' repeats in the OCI block
def test_aktx_combined_page_first_block_only():
    p = _page(
        "Consolidated Statements of Operations and Comprehensive Loss - USD ($) $ in Thousands",
        [("12 Months Ended", 2)],
        ["Dec. 31, 2025", "Dec. 31, 2024"],
        [
            ("Net loss", ["$ (17,298)", "$ (19,791)"]),
            ("Other comprehensive loss:", [None, None]),
            ("Net loss", ["(17,298)", "(19,791)"]),
        ],
    )
    lines = fk.net_income_lines(p)
    assert len(lines) == 1 and lines[0][1].values == [Decimal(-17298), Decimal(-19791)]
    assert p.printed_unit(lines[0][1], 0) == Decimal(
        1000
    )  # thousands, not 5,000,000-style trailing-zero rounding


def test_note_pages_and_per_share_parenthetical_never_selected():
    xml = _summary(
        ("Cover", "R1.htm", "Cover"),
        (
            "CONDENSED CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME (LOSS) (UNAUDITED)",
            "R7.htm",
            "Statements",
        ),
        (
            "CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (UNAUDITED) (in thousands, except per share data)",
            "R6.htm",
            "Statements",
        ),
        ("Income Taxes", "R12.htm", "Notes"),
        ("Net Income Per Share", "R13.htm", "Notes"),
        ("Loss per Share", "R14.htm", "Notes"),
    )
    assert fk.select_income_statement(xml)[1] == "R6.htm"
    only_notes = _summary(
        ("Income Taxes", "R12.htm", "Notes"),
        ("Net Income Per Share", "R13.htm", "Notes"),
    )
    assert fk.select_income_statement(only_notes) is None
    # no menu categories: a note title must still not win, a 'Statements of ...' title does
    nocat = _summary(
        ("Income Taxes", "R9.htm", ""),
        ("CONSOLIDATED STATEMENTS OF INCOME", "R4.htm", ""),
    )
    assert fk.select_income_statement(nocat)[1] == "R4.htm"
    assert fk.find_report_files(xml)["IS"][1] == "R6.htm"


# ---- ABNB: money printed in whole dollars; the only unit phrase is 'shares in Millions'
@pytest.mark.parametrize(
    "hdr,want",
    [
        ("CONSOLIDATED STATEMENTS OF OPERATIONS - USD ($) shares in Millions", 1),
        ("Statements - USD ($) $ in Thousands, shares in Millions", 1_000),
        ("Statements - USD ($) shares in Thousands, $ in Thousands", 1_000),
        ("Statements - USD ($) $ in Millions, shares in Thousands", 1_000_000),
        ("Statements (USD $)In Millions, except Per Share data", 1_000_000),
        ("Statements - USD ($) units in Thousands", 1),
        ("Statements - USD ($)", 1),
    ],
)
def test_money_multiplier_from_money_phrase_only(hdr, want):
    assert fk.money_multiplier(hdr) == want


def test_abnb_whole_dollar_page_with_shares_in_millions():
    p = _page(
        "CONSOLIDATED STATEMENTS OF OPERATIONS - USD ($)<br> shares in Millions",
        [("12 Months Ended", 2)],
        ["Dec. 31, 2024", "Dec. 31, 2023"],
        [("Net income", ["$ 2,648,000,000", "$ 4,792,000,000"])],
    )
    assert p.multiplier == 1
    row = fk.net_income_lines(p)[0][1]
    assert row.values[0] == Decimal(2_648_000_000) and p.printed_unit(
        row, 0
    ) == Decimal(1)


# ---- Ambac: 'Including Portion Attributable to Noncontrolling Interest' is the TOTAL; combined page
def _ambac(scale_hdr, spans, dates, ni):
    return _page(
        f"Consolidated Statements of Total Comprehensive Income - USD ($) {scale_hdr}",
        spans,
        dates,
        [
            ("Total revenues and other income", [74] * len(dates)),
            (
                "Net Income (Loss) Attributable to Nonredeemable Noncontrolling Interest",
                [0] * len(dates),
            ),
            (
                "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest",
                ni[0],
            ),
            ("Net income attributable to common stockholders", ni[1]),
            ("Net income (loss) from discontinued operations", ["(497)"] * len(dates)),
            ("Other comprehensive income (loss), after tax", [None] * len(dates)),
            (
                "Net Income (Loss), Including Portion Attributable to Noncontrolling Interest",
                ni[0],
            ),
            (
                "Total comprehensive income (loss) attributable to common stockholders",
                ["13"] * len(dates),
            ),
        ],
    )


def test_ambac_including_nci_is_consolidated_and_combined_page_read():
    xml = _summary(
        (
            "Consolidated Statements of Total Comprehensive Income",
            "R4.htm",
            "Statements",
        )
    )
    assert fk.select_income_statement(xml) == (
        "Consolidated Statements of Total Comprehensive Income",
        "R4.htm",
        True,
    )
    p = _ambac(
        "$ in Millions",
        [("3 Months Ended", 2), ("9 Months Ended", 2)],
        ["Sep. 30, 2023", "Sep. 30, 2022", "Sep. 30, 2023", "Sep. 30, 2022"],
        (["66", "340", "21", "348"], ["66", "340", "19", "347"]),
    )
    assert [k for k, _ in fk.net_income_lines(p)] == [
        "nci",
        "consolidated",
        "attributable",
    ]  # discontinued + OCI block skipped
    att = next(r for k, r in fk.net_income_lines(p) if k == "attributable")
    assert (
        att.values[p.column(date(2022, 9, 30), months=9)] == Decimal(347)
        and p.multiplier == 1_000_000
    )


def test_ambac_fy_in_thousands():
    p = _ambac(
        "$ in Thousands",
        [("12 Months Ended", 3)],
        ["Dec. 31, 2024", "Dec. 31, 2023", "Dec. 31, 2022"],
        (["(58,921)", "(23,232)", "(35,244)"], ["(556,449)", "3,632", "522,380"]),
    )
    att = next(r for k, r in fk.net_income_lines(p) if k == "attributable")
    assert att.values[p.column(date(2022, 12, 31))] == Decimal(
        522380
    ) and p.printed_unit(att, 2) == Decimal(1000)


# ---- LNG Q3 2025 10-Q (0000003570-25-000107 R2, real page): the prior-year date
# cells carry colspan=2 (a footnote column), so each "N Months Ended" header spans 3
# grid columns over 2 dates. Durations must follow the date cells' grid positions.
def test_lng_2025_duration_header_spans_footnote_columns():
    from pathlib import Path

    html = (
        Path(__file__).parent / "fixtures" / "lng_10q_0000003570-25-000107_R2.html"
    ).read_text()
    p = fk.parse_rpage(html)
    assert p.multiplier == 1_000_000
    assert p.months == [3, 3, 9, 9]
    att = next(
        r
        for k, r in fk.net_income_lines(p)
        if r.label == "Net income attributable to Cheniere"
    )
    assert att.values[p.column(date(2025, 9, 30), months=9)] == Decimal(3028)
    assert att.values[p.column(date(2025, 9, 30), months=3)] == Decimal(1049)
    assert att.values[p.column(date(2024, 9, 30), months=9)] == Decimal(2275)
