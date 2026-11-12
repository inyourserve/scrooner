"""Fixtures for docmap.py: one synthetic 10-K served from a fake cache, one assertion per fix.

Run: python3 -m pytest -q data-team/companies/reads/tools/test_docmap.py
No network: every URL the tool would fetch is pre-written into the cache directory.
"""

import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("docmap", os.path.join(HERE, "docmap.py"))
docmap = importlib.util.module_from_spec(spec)
sys.modules["docmap"] = docmap
spec.loader.exec_module(docmap)

CIK = "0000999999"
ACCN = "0000999999-26-000001"
BASE = f"https://www.sec.gov/Archives/edgar/data/{int(CIK)}/{ACCN.replace('-', '')}/"
END, START, END1 = "2025-12-31", "2025-01-01", "2024-12-31"


def _row(tag, label, v0, v1=None):
    href = f"defref_{tag.replace(':', '_')}"
    cells = "".join(f'<td class="nump">{x}</td>' for x in (v0, v1) if x is not None)
    return f"<tr><td class=\"pl\"><a onclick=\"top.Show.showAR( this, '{href}', window );\">{label}</a></td>{cells}</tr>"


def _page(title, rows, months=True):
    head = (f'<tr><th class="tl" colspan="1" rowspan="2">{title} - USD ($) $ in Millions</th>'
            + ('<th class="th" colspan="2">12 Months Ended</th></tr>' if months else "</tr>")
            + '<tr><th class="th">Dec. 31, 2025</th><th class="th">Dec. 31, 2024</th></tr>')
    return "<table>" + head + "".join(rows) + "</table>"


IS = _page("CONSOLIDATED STATEMENTS OF INCOME", [
    _row("us-gaap:Revenues", "Total revenues", "1,000", "900"),
    _row("us-gaap:GeneralAndAdministrativeExpense", "General and administrative", "100", "90"),
    _row("us-gaap:SellingAndMarketingExpense", "Sales and marketing", "50", "40"),
    _row("us-gaap:OperatingIncomeLoss", "Operating income", "300", "250"),
    _row("us-gaap:InterestAndDebtExpense", "Interest and debt expense", "20", "18"),
    _row("us-gaap:NetIncomeLoss", "Net income", "200", "180"),
])
BS = _page("CONSOLIDATED BALANCE SHEETS", [
    _row("us-gaap:Assets", "Total assets", "5,000", "4,800"),
    _row("us-gaap:LongTermDebt", "Debt", "1,500", "1,400"),
    _row("us-gaap:Assets", "Total assets", "5,000", "4,800"),          # co-registrant block repeats the parent
    _row("us-gaap:LongTermDebt", "Debt", "1,500", "1,400"),
], months=False)
CF = _page("CONSOLIDATED STATEMENTS OF CASH FLOWS", [
    _row("us-gaap:Depreciation", "Depreciation", "60", "55"),
    _row("us-gaap:AdjustmentForAmortization", "Amortization", "40", "35"),
    _row("us-gaap:PaymentsToDevelopRealEstateAssets", "Development of real estate", "(300)", "(250)"),
    _row("zz:PaymentsForPropertyImprovements", "Property improvements", "(30)", "(25)"),
    _row("us-gaap:CapitalExpendituresIncurredButNotYetPaid", "Invoices accrued for construction and tenant improvements", "45", "40"),
    _row("us-gaap:PaymentsOfDividends", "Dividends paid on common and preferred stock", "(120)", "(110)"),
])
FS = ("<FilingSummary><MyReports>"
      "<Report><ShortName>Cover</ShortName><MenuCategory>Cover</MenuCategory><HtmlFileName>R1.htm</HtmlFileName></Report>"
      "<Report><ShortName>CONSOLIDATED STATEMENTS OF INCOME</ShortName><MenuCategory>Statements</MenuCategory><HtmlFileName>R2.htm</HtmlFileName></Report>"
      "<Report><ShortName>CONSOLIDATED BALANCE SHEETS</ShortName><MenuCategory>Statements</MenuCategory><HtmlFileName>R3.htm</HtmlFileName></Report>"
      "<Report><ShortName>CONSOLIDATED STATEMENTS OF CASH FLOWS</ShortName><MenuCategory>Statements</MenuCategory><HtmlFileName>R4.htm</HtmlFileName></Report>"
      "</MyReports></FilingSummary>")


def _fact(v, end, start=None):
    f = {"val": v, "accn": ACCN, "end": end, "form": "10-K", "fp": "FY", "fy": 2025, "filed": "2026-02-20"}
    if start:
        f["start"] = start
    return f


def _cf():
    dur = lambda a, b: [_fact(a, END, START), _fact(b, END1, "2024-01-01")]
    inst = lambda a, b: [_fact(a, END), _fact(b, END1)]
    g = {
        "Revenues": dur(1000e6, 900e6), "GeneralAndAdministrativeExpense": dur(100e6, 90e6),
        "SellingAndMarketingExpense": dur(50e6, 40e6), "OperatingIncomeLoss": dur(300e6, 250e6),
        "InterestAndDebtExpense": dur(20e6, 18e6), "NetIncomeLoss": dur(200e6, 180e6),
        "Assets": inst(5000e6, 4800e6), "LongTermDebt": inst(1500e6, 1400e6),
        "Depreciation": dur(60e6, 55e6), "AdjustmentForAmortization": dur(40e6, 35e6),
        "PaymentsToDevelopRealEstateAssets": dur(300e6, 250e6), "PaymentsOfDividends": dur(120e6, 110e6),
    }
    return {"facts": {"us-gaap": {k: {"units": {"USD": v}} for k, v in g.items()}}}


METALINKS = {"instance": {"x.htm": {
    "report": {"R1": {"role": "r/cover", "groupType": "document", "shortName": "Cover"},
               "R50": {"role": "r/vie", "groupType": "details", "shortName": "Variable Interest Entities (Details)"}},
    "tag": {"us-gaap_Liabilities": {"presentation": ["r/vie"], "lang": {"en-us": {"role": {"label": "Liabilities"}}}}},
}}}


def _write(cache, url, body):
    path = os.path.join(cache, re.sub(r"\W", "_", url)[-150:])
    with open(path, "w", encoding="utf8") as fh:
        fh.write(body)


def _offline_get(url, cache):
    """Never touch the network in tests: a page that is not in the fixture cache is empty."""
    path = os.path.join(cache, re.sub(r"\W", "_", url)[-150:])
    return open(path, encoding="utf8").read() if os.path.exists(path) else ""


docmap.get = _offline_get


def _read(tmp_path):
    cache = str(tmp_path)
    _write(cache, f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json", json.dumps(_cf()))
    _write(cache, f"https://data.sec.gov/submissions/CIK{CIK}.json", json.dumps({"sic": "6798"}))
    _write(cache, BASE + "FilingSummary.xml", FS)
    for n, body in (("R1", "<table></table>"), ("R2", IS), ("R3", BS), ("R4", CF)):
        _write(cache, BASE + f"{n}.htm", body)
    _write(cache, BASE + "MetaLinks.json", json.dumps(METALINKS))
    out, quirks, meta = docmap.read_company({"cik": CIK, "ticker": "TST", "name": "Test"}, cache)
    return {r["data_point"]: r for r in out}


def test_1_coregistrant_debt_counted_once(tmp_path):
    rows = _read(tmp_path)
    assert rows["total_debt"]["fy0_printed"] == "1500000000"   # not 3,000 (PLD 70,074 vs 35,037)


def test_2_note_hit_never_from_a_vie_note(tmp_path):
    rows = _read(tmp_path)
    assert rows["total_liabilities"]["status"] == "not_presented"
    assert "R50" not in rows["total_liabilities"].get("r_page", "")


def test_3_da_includes_adjustment_for_amortization(tmp_path):
    rows = _read(tmp_path)
    assert rows["depreciation_and_amortization"]["status"] == "component sum"
    assert "AdjustmentForAmortization" in rows["depreciation_and_amortization"]["tags"]
    assert rows["depreciation_and_amortization"]["fy0_printed"] == "100000000"


def test_4_interest_and_debt_expense_label(tmp_path):
    rows = _read(tmp_path)
    assert rows["interest_expense"]["tags"] == "us-gaap:InterestAndDebtExpense"
    assert rows["interest_expense"]["status"] == "mapped"


def test_5_reit_capex_component_sum(tmp_path):
    # the accrued (non-cash) supplemental line is never part of capex (HR)
    rows = _read(tmp_path)
    assert rows["capex"]["status"] == "component sum"
    assert rows["capex"]["fy0_printed"] == "-330000000"


def test_6_common_and_preferred_dividends_combined(tmp_path):
    rows = _read(tmp_path)
    assert rows["dividends_paid"]["status"] == "combined"


def test_7_sga_is_never_ga_alone(tmp_path):
    rows = _read(tmp_path)
    assert rows["sga_expense"]["status"] == "component sum"
    assert rows["sga_expense"]["fy0_printed"] == "150000000"
