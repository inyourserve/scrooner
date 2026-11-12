"""The document-first reader (pipeline/scripts/reads/docmap.py) reads printed R-page values the way the page prints
them: parentheses are negatives, the title's scale multiplies money and share counts but never per-share amounts, and
a printed value that disagrees with companyfacts for the same accession and period is a mismatch the filing decides."""

import gzip
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "reads" / "docmap.py"


def _mod():
    spec = importlib.util.spec_from_file_location("docmap_script", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(m)
    return m


def test_printed_numbers_and_scales():
    m = _mod()
    assert m.parse_num("(1,234)") == Decimal(-1234)
    assert m.parse_num("$ 3.73") == Decimal("3.73")
    assert m.parse_num("—") is None
    assert m.scales(
        "CONSOLIDATED STATEMENTS OF OPERATIONS - USD ($) shares in Millions, $ in Millions"
    ) == (10**6, 10**6)
    assert m.scales("BALANCE SHEETS - USD ($) $ in Thousands") == (10**3, 1)
    assert m.scales(
        "STATEMENTS OF INCOME - USD ($) In Millions, except Per Share data"
    ) == (10**6, 10**6)
    assert m.scales(
        "STATEMENTS OF INCOME - USD ($) In Thousands, except Share data"
    ) == (10**3, 1)


def _row(elem, label, a, b):
    return (
        f"<tr><td class='pl'><a onclick=\"top.Show.showAR( this, 'defref_{elem}', window );\">{label}</a></td>"
        f"<td class='nump'>{a}</td><td class='nump'>{b}</td></tr>"
    )


def test_a_company_read_against_companyfacts(tmp_path):
    m = _mod()
    acc = "0000000001-26-000001"
    d = tmp_path / "0000000001" / acc
    d.mkdir(parents=True)
    (d / "FilingSummary.xml").write_text(
        "<FilingSummary><MyReports><Report><HtmlFileName>R2.htm</HtmlFileName>"
        "<LongName>0000002 - Statement - CONSOLIDATED STATEMENTS OF OPERATIONS</LongName><ShortName>x</ShortName>"
        "<MenuCategory>Statements</MenuCategory></Report></MyReports></FilingSummary>"
    )
    (d / "R2.htm").write_text(
        "<table class='report'><tr><th class='tl' rowspan='2'>STATEMENTS OF OPERATIONS - USD ($) $ in Millions</th>"
        "<th class='th' colspan='2'>12 Months Ended</th></tr><tr><th>Dec. 31, 2025</th><th>Dec. 31, 2024</th></tr>"
        + _row("us-gaap_Revenues", "Total revenues", "$ 1,000", "$ 900")
        + _row("us-gaap_InterestExpense", "Interest expense", "(20)", "(25)")
        + _row("us-gaap_NetIncomeLoss", "Net income", "$ 300", "$ 250")
        + _row("us-gaap_EarningsPerShareBasic", "Basic", "$ 3.00", "$ 2.50")
        + "</table>"
    )

    def f(val, end):
        return {
            "start": f"{end[:4]}-01-01",
            "end": end,
            "val": val,
            "accn": acc,
            "form": "10-K",
            "filed": "2026-02-01",
        }

    facts = {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [f(1000000000, "2025-12-31"), f(900000000, "2024-12-31")]
                    }
                },
                "InterestExpense": {
                    "units": {
                        "USD": [f(20000000, "2025-12-31"), f(25000000, "2024-12-31")]
                    }
                },
                "NetIncomeLoss": {
                    "units": {
                        "USD": [f(301000000, "2025-12-31"), f(250000000, "2024-12-31")]
                    }
                },
                "EarningsPerShareBasic": {
                    "units": {
                        "USD/shares": [f(3.0, "2025-12-31"), f(2.5, "2024-12-31")]
                    }
                },
            }
        }
    }
    (tmp_path / "0000000001" / "companyfacts.json.gz").write_bytes(
        gzip.compress(json.dumps(facts).encode())
    )
    res = m.read_company(tmp_path, "0000000001", "TST", acc, "2026-02-01")
    rows = {r["data_point"]: r for r in res["rows"]}
    assert (rows["revenue"]["fy0_printed"], rows["revenue"]["match"]) == (
        "1000000000",
        "Y",
    )
    assert rows["interest_expense"]["fy0_printed"] == "-20000000"
    assert rows["interest_expense"]["match"].startswith("Y (sign differs")
    assert (rows["basic_eps"]["fy0_printed"], rows["basic_eps"]["match"]) == ("3", "Y")
    assert rows["net_income"]["match"].startswith("FY0 N")
    assert "the filing value stands" in rows["net_income"]["note"]
    assert rows["gross_profit"]["status"] == "not_presented"


def _filing(tmp_path, pages):
    acc = "0000000002-26-000001"
    d = tmp_path / "0000000002" / acc
    d.mkdir(parents=True)
    reps = "".join(
        f"<Report><HtmlFileName>{fn}</HtmlFileName><LongName>000000{i} - {cat} - {name}</LongName><ShortName>x</ShortName>"
        f"<MenuCategory>{cat}</MenuCategory></Report>"
        for i, (fn, cat, name, _) in enumerate(pages)
    )
    (d / "FilingSummary.xml").write_text(
        f"<FilingSummary><MyReports>{reps}</MyReports></FilingSummary>"
    )
    for fn, _, _, body in pages:
        (d / fn).write_text(body)
    return acc


BS_HEAD = "<table class='report'><tr><th class='tl'>{t} - USD ($) {s}</th><th>Dec. 31, 2025</th><th>Dec. 31, 2024</th></tr>"


def test_shares_are_the_balance_sheet_class_sum_never_the_cover(tmp_path):
    """Dhairya 2026-11-12: shares_outstanding = CommonStockSharesOutstanding (class sum) at the BS date; dei never"""
    m = _mod()
    cover = (
        "<table class='report'><tr><th class='tl'>Cover</th><th>Feb. 1, 2026</th></tr>"
        + _row("dei_EntityCommonStockSharesOutstanding", "Shares", "999", "").replace(
            "<td class='nump'></td>", ""
        )
        + "</table>"
    )
    bs = (
        BS_HEAD.format(t="BALANCE SHEETS", s="$ in Millions")
        + _row("us-gaap_Assets", "Total assets", "5,000", "4,000")
        + _row("us-gaap_ReceivablesNetCurrent", "Receivables, net", "70", "60")
        + _row("abc_OtherReceivables", "Other receivables", "5", "4")
        + "</table>"
    )
    par = (
        BS_HEAD.format(t="BALANCE SHEETS (Parenthetical)", s="shares in Millions")
        + "<tr><td class='pl'>Class A [Member]</td><td></td><td></td></tr>"
        + _row(
            "us-gaap_CommonStockSharesOutstanding",
            "Common stock, shares outstanding",
            "100",
            "90",
        )
        + "<tr><td class='pl'>Class B [Member]</td><td></td><td></td></tr>"
        + _row(
            "us-gaap_CommonStockSharesOutstanding",
            "Common stock, shares outstanding",
            "20",
            "20",
        )
        + "</table>"
    )
    acc = _filing(
        tmp_path,
        [
            ("R1.htm", "Cover", "Cover", cover),
            ("R2.htm", "Statements", "BALANCE SHEETS", bs),
            ("R3.htm", "Statements", "BALANCE SHEETS (Parenthetical)", par),
        ],
    )
    res = m.read_company(tmp_path, "0000000002", "TS2", acc, "2026-02-01")
    rows = {r["data_point"]: r for r in res["rows"]}
    so = rows["shares_outstanding"]
    assert (so["tags"], so["fy0_printed"], so["fy1_printed"]) == (
        "us-gaap:CommonStockSharesOutstanding",
        "120000000",
        "110000000",
    )
    assert "class sum of 2" in so["note"]
    ar = rows["accounts_receivable"]
    assert ar["status"] == "not_presented" and "2 receivables lines" in ar["note"]
    assert {r["status"] for r in res["rows"]} <= {
        "mapped",
        "combined",
        "component sum",
        "component_in_note",
        "not_presented",
        "OUT",
    }


IS_HEAD = (
    "<table class='report'><tr><th class='tl' rowspan='2'>STATEMENTS OF OPERATIONS - USD ($) $ in Millions</th>"
    "<th class='th' colspan='2'>12 Months Ended</th></tr><tr><th>Dec. 31, 2025</th><th>Dec. 31, 2024</th></tr>"
)


def _opex(tmp_path, body):
    m = _mod()
    page = IS_HEAD + body + "</table>"
    acc = _filing(
        tmp_path, [("R2.htm", "Statements", "STATEMENTS OF OPERATIONS", page)]
    )
    rows = {
        r["data_point"]: r
        for r in m.read_company(tmp_path, "0000000002", "TS3", acc, "2026-02-01")[
            "rows"
        ]
    }
    return rows["operating_expenses"]


def test_opex_is_every_line_between_gross_profit_and_operating_income(tmp_path):
    """Dhairya 2026-11-12: opex never includes cost of revenue; component sum tied exactly to GP - OI"""
    r = _opex(
        tmp_path,
        _row("us-gaap_Revenues", "Revenue", "1,000", "900")
        + _row("us-gaap_CostOfRevenue", "Cost of revenue", "600", "500")
        + _row("us-gaap_GrossProfit", "Gross profit", "400", "400")
        + _row("us-gaap_SellingGeneralAndAdministrativeExpense", "SG&A", "150", "140")
        + _row("abc_RestructuringCustom", "Restructuring", "50", "10")
        + _row("us-gaap_OperatingIncomeLoss", "Operating income", "200", "250"),
    )
    assert (r["status"], r["fy0_printed"], r["fy1_printed"]) == (
        "component sum",
        "200000000",
        "150000000",
    )
    assert (
        r["tags"]
        == "us-gaap:SellingGeneralAndAdministrativeExpense+abc:RestructuringCustom"
    )


def test_costs_and_expenses_with_cost_of_revenue_is_combined_never_opex(tmp_path):
    r = _opex(
        tmp_path,
        _row("us-gaap_Revenues", "Revenue", "1,000", "900")
        + _row("us-gaap_CostOfRevenue", "Cost of revenue", "600", "500")
        + _row("us-gaap_SellingGeneralAndAdministrativeExpense", "SG&A", "200", "150")
        + _row("us-gaap_CostsAndExpenses", "Total costs and expenses", "800", "650")
        + _row("us-gaap_OperatingIncomeLoss", "Operating income", "200", "250"),
    )
    assert r["status"] == "combined" and r["tags"] == "us-gaap:CostsAndExpenses"


def test_eras_reach_fy2015_and_each_needs_an_opened_10k(tmp_path):
    """Dhairya 2026-11-12: every data point's eras must cover FY2015 to the latest year, each era seen on a face"""
    m = _mod()

    def fact(fy, val):
        return {
            "start": f"{fy}-01-01",
            "end": f"{fy}-12-31",
            "val": val,
            "accn": f"A-{fy}",
            "fy": fy,
            "form": "10-K",
            "filed": f"{fy + 1}-02-01",
        }

    facts = {
        "facts": {
            "us-gaap": {
                "SalesRevenueNet": {"units": {"USD": [fact(2015, 10), fact(2016, 11)]}},
                "Revenues": {"units": {"USD": [fact(2017, 12)]}},
            }
        }
    }
    p = tmp_path / "cf.json.gz"
    p.write_bytes(gzip.compress(json.dumps(facts).encode()))
    f = m.Facts(p)
    rows = [
        {
            "data_point": dp.name,
            "tags": "us-gaap:Revenues" if dp.name == "revenue" else "",
            "status": "mapped",
            "r_page": "R2.htm",
            "fy0_printed": "12",
            "match": "Y",
        }
        for dp in m.DPS
    ]
    plan = m.plan_eras(f, {"accession": "A-2017", "rows": rows})
    assert plan["reaches_2015"] and plan["latest_fy"] == 2017
    rev = [(r["sig"], r["from"], r["to"]) for r in plan["eras"]["revenue"]]
    assert rev == [("SalesRevenueNet", 2015, 2016), ("Revenues", 2017, 2017)]
    assert sorted(plan["need"]) == [2015, 2017]  # FY2016 is inside the FY2015 era
    m.era_evidence(plan, {2017: {"accession": "A-2017", "rows": rows}})
    assert not plan["verdict"]["covered"] and "revenue" in plan["verdict"]["uncovered"]
    m.era_evidence(
        plan,
        {
            2015: {"accession": "A-2015", "rows": rows},
            2017: {"accession": "A-2017", "rows": rows},
        },
    )
    assert plan["verdict"]["covered"]
