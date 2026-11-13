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
    _row("us-gaap:CostOfRevenue", "Product", "400", "380"),       # member rows of one tag, no printed total (INTU 4,253)
    _row("us-gaap:CostOfRevenue", "Service", "3,853", "3,500"),
    _row("us-gaap:GeneralAndAdministrativeExpense", "General and administrative", "100", "90"),
    _row("us-gaap:SellingAndMarketingExpense", "Sales and marketing", "50", "40"),
    _row("us-gaap:OperatingIncomeLoss", "Operating income", "300", "250"),
    _row("us-gaap:InterestAndDebtExpense", "Interest and debt expense", "20", "18"),
    _row("us-gaap:NetIncomeLoss", "Net income", "200", "180"),
    _row("us-gaap:OperatingIncomeLoss", "Operating income", "120", "100"),   # co-registrant block: same tag and label,
    _row("us-gaap:NetIncomeLoss", "Net income", "90", "70"),                 # different values (AEE): never summed
])
BS = _page("CONSOLIDATED BALANCE SHEETS", [
    _row("us-gaap:Assets", "Total assets", "5,000", "4,800"),
    _row("us-gaap:LongTermDebt", "Debt", "1,500", "1,400"),
    _row("us-gaap:Assets", "Total assets", "5,000", "4,800"),          # co-registrant block repeats the parent
    _row("us-gaap:LongTermDebt", "Debt", "1,500", "1,400"),
    _row("us-gaap:LongTermDebtCurrent", "Current portion of debt", "100", "90"),          # components of the printed
    _row("us-gaap:LongTermDebtNoncurrent", "Long-term debt, less current portion", "1,400", "1,310"),  # total (PNC)
    _row("us-gaap:FinanceLeaseLiabilityNoncurrent", "Finance lease liabilities", "50", "45"),
    _row("us-gaap:OperatingLeaseLiabilityNoncurrent", "Operating lease liabilities", "70", "65"),
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
        "Revenues": dur(1000e6, 900e6), "CostOfRevenue": dur(4253e6, 3880e6),
        "LongTermDebtCurrent": [_fact(100e6, END), _fact(90e6, END1)],
        "LongTermDebtNoncurrent": [_fact(1400e6, END), _fact(1310e6, END1)], "GeneralAndAdministrativeExpense": dur(100e6, 90e6),
        "SellingAndMarketingExpense": dur(50e6, 40e6), "OperatingIncomeLoss": dur(300e6, 250e6),
        "InterestAndDebtExpense": dur(20e6, 18e6), "NetIncomeLoss": dur(200e6, 180e6),
        "Assets": inst(5000e6, 4800e6), "LongTermDebt": inst(1500e6, 1400e6),
        "FinanceLeaseLiabilityNoncurrent": inst(50e6, 45e6), "OperatingLeaseLiabilityNoncurrent": inst(70e6, 65e6),
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
    # debt counted once (not 3,000: PLD 70,074 vs 35,037) + face finance leases 50; operating leases 70 never
    assert rows["total_debt"]["fy0_printed"] == "1550000000"


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


def test_8_total_debt_includes_finance_leases_never_operating(tmp_path):
    rows = _read(tmp_path)
    assert "FinanceLeaseLiabilityNoncurrent" in rows["total_debt"]["tags"]
    assert "OperatingLease" not in rows["total_debt"]["tags"]


def test_9_capex_includes_turnarounds_in_investing(tmp_path):
    global CF
    saved = CF
    CF = _page("CONSOLIDATED STATEMENTS OF CASH FLOWS", [
        _row("us-gaap:NetCashProvidedByUsedInOperatingActivities", "Net cash provided by operating activities", "500", "450"),
        _row("us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", "Expenditures for property, plant and equipment", "(200)", "(180)"),
        _row("zz:PaymentsForDeferredTurnaroundCosts", "Expenditures for deferred turnaround costs", "(80)", "(60)"),
        _row("us-gaap:NetCashProvidedByUsedInInvestingActivities", "Net cash used in investing activities", "(280)", "(240)"),
    ])
    try:
        rows = _read(tmp_path)
    finally:
        CF = saved
    assert rows["capex"]["status"] == "component sum"
    assert rows["capex"]["fy0_printed"] == "-280000000"


def test_10_member_rows_of_one_tag_are_summed(tmp_path):
    rows = _read(tmp_path)
    r = rows["cost_of_revenue"]
    assert r["status"] == "component sum" and r["fy0_printed"] == "4253000000" and r["match"] == "Y"
    assert "[member: Product]" in r["tags"] and "[member: Service]" in r["tags"]


def test_11_reit_dividends_are_distributions_paid_not_declared(tmp_path):
    global CF
    saved = CF
    CF = _page("CONSOLIDATED STATEMENTS OF CASH FLOWS", [
        _row("us-gaap:DividendsCommonStockCash", "Dividends declared on common stock", "(130)", "(120)"),
        _row("us-gaap:PaymentsOfDividendsCommonStock", "Distributions paid to common stockholders", "(125)", "(118)"),
    ])
    try:
        rows = _read(tmp_path)
    finally:
        CF = saved
    assert rows["dividends_paid"]["tags"] == "us-gaap:PaymentsOfDividendsCommonStock"
    assert rows["dividends_paid"]["fy0_printed"] == "-125000000"


def test_12_coregistrant_blocks_with_other_values_are_not_members(tmp_path):
    rows = _read(tmp_path)
    assert rows["operating_income"]["status"] == "mapped" and rows["operating_income"]["fy0_printed"] == "300000000"
    assert rows["net_income"]["fy0_printed"] == "200000000"


# ---------------------------------------------------------------- fixes 17-21: direct unit fixtures (no page fetch)

def _r(tag, label, *vals):
    return {"tag": tag, "label": label, "vals": list(vals)}


def test_13_entity_blocks_dropped_member_blocks_kept_whole():
    rows = [_r("us-gaap:Revenues", "Total revenues", 100.0),
            _r("dei:LegalEntityAxis", "Sub A", None),
            _r("us-gaap:Revenues", "Total revenues", 60.0),
            _r("srt:ProductOrServiceAxis", "Product", None),
            _r("us-gaap:CostOfGoodsAndServicesSold", "Cost of goods sold", 40.0),
            _r("srt:ProductOrServiceAxis", "Other", None),
            _r("us-gaap:CostOfGoodsAndServicesSold", "Cost of goods sold", 5.0)]
    out = docmap.dedupe_coreg(rows)
    vals = [(r["tag"], r["vals"][0]) for r in out if not docmap.is_block_header(r)]
    assert ("us-gaap:Revenues", 60.0) not in vals  # the legal-entity block is a co-registrant block
    assert vals.count(("us-gaap:CostOfGoodsAndServicesSold", 40.0)) == 1 and ("us-gaap:CostOfGoodsAndServicesSold", 5.0) in vals


def test_14_total_with_member_cogs_is_component_sum_of_face_lines():
    page = {"rows": [_r("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax", "Total revenues", 5101.0),
                     _r("us-gaap:SellingGeneralAndAdministrativeExpense", "Selling, general and administrative", 2234.0),
                     _r("us-gaap:ResearchAndDevelopmentExpense", "Research and development", 371.0),
                     _r("us-gaap:OtherOperatingIncomeExpenseNet", "Other expense, net", 333.0),
                     _r("us-gaap:CostsAndExpenses", "Total expenses", 4988.0),
                     _r("us-gaap:OperatingIncomeLoss", "Operating income", 113.0),
                     _r("srt:ProductOrServiceAxis", "Product sales", None),
                     _r("us-gaap:CostOfGoodsAndServicesSold", "Cost of goods sold", 2045.0),
                     _r("srt:ProductOrServiceAxis", "Other revenues", None),
                     _r("us-gaap:CostOfGoodsAndServicesSold", "Cost of goods sold", 5.0)]}
    row, status, _ = docmap.opex_row(page)
    assert status == "component sum" and row["vals"][0] == 2938.0
    page["rows"][3]["vals"] = [350.0]  # no longer ties: the total still includes COGS -> combined, never opex
    row, status, _ = docmap.opex_row(page)
    assert status == "combined"


def test_15_proceeds_from_repurchase_of_equity_is_never_buybacks():
    assert docmap._excluded("share_buybacks", _r("us-gaap:ProceedsFromRepurchaseOfEquity", "Repurchases of common stock, net", -224.0))
    assert not docmap._excluded("share_buybacks", _r("us-gaap:PaymentsForRepurchaseOfCommonStock", "Repurchases of common stock", -224.0))


def test_16_affiliate_summarized_pages_are_rejected_notes():
    assert re.search(docmap.NOTE_REJECT, "Investments in Affiliated Companies (Summarized Financial Data-RRPF) (Details 6)", re.I)


def test_17_financial_group_from_the_group_file(monkeypatch):
    monkeypatch.setattr(docmap, "_GROUPS", {"CACC": "lender_nonbank", "AAPL": "corporate"})
    assert docmap.template_group("CACC") in docmap.FIN_GROUPS and docmap.template_group("AAPL") not in docmap.FIN_GROUPS


def test_18_face_row_beats_overlapping_member_blocks():
    # CVLT: 'Total revenues' on the face, then two axes (product and segment) each repeating it by member
    rows = [_r("us-gaap:Revenues", "Total revenues", 100.0),
            _r("srt:ProductOrServiceAxis", "Subscription", None), _r("us-gaap:Revenues", "Total revenues", 60.0),
            _r("srt:ProductOrServiceAxis", "Services", None), _r("us-gaap:Revenues", "Total revenues", 40.0),
            _r("us-gaap:StatementBusinessSegmentsAxis", "Americas", None), _r("us-gaap:Revenues", "Total revenues", 70.0),
            _r("us-gaap:StatementBusinessSegmentsAxis", "Intl", None), _r("us-gaap:Revenues", "Total revenues", 30.0)]
    page = {"rows": docmap.dedupe_coreg(rows)}
    got = docmap.member_sum(page, page["rows"][0])
    assert got["vals"][0] == 100.0 and "parts" not in got
    # members only (no face row of the tag): still summed as before (fix 13)
    page2 = {"rows": docmap.dedupe_coreg(rows[1:5])}
    first = next(x for x in page2["rows"] if x["tag"] == "us-gaap:Revenues")
    assert docmap.member_sum(page2, first)["vals"][0] == 100.0
