"""The structural resolver's standard inputs (data-team/tags/line_map/tools/standard_inputs.py + extract_notefacts.sql): single-member
own-period facts (equity column, RelatedParty Nonrelated/Related, Scenario), accretion facts, earlier-column (comparative, parenthetical
per-share) facts, printed-dash lines and amortization by income-statement location come from ONE extract (+ its companion
extract_facelines.sql), so the side files (_member-face-facts, _ap/_ar-related-split, _comparative-fill, _printed-zero,
_amortization-location-total, total_debt_all) are gone. All-110 parity 2026-11-14: the resolver with those side files beside the extract
and from the extract alone differ in 0 values / decisions of 67,122 rows (2 provenance flags)."""

from __future__ import annotations

import re
import sys
from decimal import Decimal as D
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[3] / "data-team" / "tags" / "line_map" / "tools"
sys.path.insert(0, str(TOOLS))
import resolve_all as RA  # noqa: E402
import standard_inputs as si  # noqa: E402

pytestmark = pytest.mark.unit
SQL = (TOOLS / "extract_notefacts.sql").read_text()


def test_extract_sql_carries_the_three_member_axes_accretion_and_earlier_columns():
    assert "(EquityComponents|RelatedPartyTransactionsByRelatedParty|Scenario)=[^;=]+;$" in SQL   # exactly one member, those axes
    assert "like '%Accretion%'" in SQL
    assert "v.ddate<fl.period" in SQL and "interval '3 years 2 months'" in SQL            # FY-1 and FY-2 columns
    assert "v.ddate=fl.period" in SQL and "exists (select 1 from fsn.line" in SQL         # member facts: own column, on a statement line
    assert re.search(r"select fl\.accession a, own\.vals, mem\.mvals, cmp\.cvals", SQL)


def test_build_sql_fills_both_placeholders():
    sql = si.build_sql(["1163165", "0001341439"], extra_tags=["CommonStockDividendsPerShareDeclared", "OddExactTag"])
    assert "/*" not in sql.split("set statement_timeout")[1]
    assert "cik::bigint in (1163165,1341439)" in sql
    assert "|OddExactTag|" in sql and "CommonStockDividendsPerShare\\w*" in sql
    # an exact tag a family covers is not repeated (rules/extract_families.txt: the regex stays small enough for 1,000 companies)
    assert "|AccountsPayableCurrent|" not in sql and "Accounts\\w*Payable\\w*" in sql
    assert "CommonStockDividendsPerShareDeclared" not in sql


def test_families_cover_the_family_modules_and_total_debt_perimeter():
    fam = si.families()
    rx = re.compile("^(" + "|".join(fam) + ")$")
    for t in ("AccountsPayableRelatedPartiesCurrent", "CostOfGoodsAndServicesSold", "DepreciationDepletionAndAmortization", "PaymentsForRepurchaseOfCommonStock",
              "LongTermDebtNoncurrent", "FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsNoncurrent", "DueToOfficersOrStockholdersCurrent",
              "CommonStockDividendsPerShareDeclared", "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"):
        assert rx.match(t), t
    with pytest.raises(AssertionError):
        si.families(str(TOOLS / "extract_notefacts.sql"))   # a non-fragment line is refused
    with pytest.raises(AssertionError):
        si.build_sql(["1; drop table x"])


def test_split_rows():
    nf, mf, cf = si.split_rows([("A", "t|4|1", None, None), ("B", None, "t|4|1|Scenario=X;", "t|4|2|2015-12-31")])
    assert nf == {"A": "t|4|1"} and mf == {"B": "t|4|1|Scenario=X;"} and cf == {"B": "t|4|2|2015-12-31"}
    rows = [("A", "t|4|1", None, None, "P|CF|6|30|Repurchases"), ("B", "t|4|1", None, None, None)]
    assert si.split_rows(rows)[0] == {"A": "t|4|1", "B": "t|4|1"} and si.zero_lines(rows) == {"A": "P|CF|6|30|Repurchases"}


def test_printed_zero_needs_a_role_element_line_on_the_data_points_statement():
    roles = {"share_buybacks": ("CF", ["PaymentsForRepurchaseOfCommonStock", "PaymentsForRepurchaseOfEquity"]), "cost_of_revenue": ("IS", ["CostOfRevenue"])}
    z = {"A": "PaymentsForRepurchaseOfEquity|CF|6|31|Other~PaymentsForRepurchaseOfCommonStock|CF|6|30|Common stock repurchases~CostOfRevenue|CF|6|9|x"}
    rows = [_row("A", "2020-12-31", "not_presented", dp="share_buybacks"), _row("A", "2020-12-31", "not_presented", dp="cost_of_revenue"),
            _row("B", "2020-12-31", "not_presented", dp="share_buybacks"), _row("A", "2020-12-31", "mapped", dp="share_buybacks")]
    got = si.printed_zero(rows, z, roles)
    assert got == {("A", "share_buybacks"): dict(tag="PaymentsForRepurchaseOfCommonStock", stmt="CF", r_line="R6:30", label="Common stock repurchases")}
    # cost_of_revenue: the line sits on another statement; B: no zero line; a mapped row is never touched (first role element in roles order wins)


def test_amortization_location_total_undimensioned_total_or_total_member():
    A = "AmortizationOfIntangibleAssets"
    mf = {"CSCO": f"{A}|4|742|IncomeStatementLocation=CostOfSales;~{A}|4|275|IncomeStatementLocation=OperatingExpense;",
          "TOT": f"{A}|4|556|IncomeStatementLocation=CostOfSales;~{A}|4|259|IncomeStatementLocation=Amort;~{A}|4|815|IncomeStatementLocation=OperatingIncomeLoss;",
          "ONE": f"{A}|4|9|IncomeStatementLocation=CostOfSales;",
          "BAD": f"{A}|4|1|IncomeStatementLocation=CostOfSales;~{A}|4|2|IncomeStatementLocation=OperatingExpense;"}
    nf = {"CSCO": f"{A}|4|1017", "ONE": f"{A}|4|9", "BAD": f"{A}|4|5"}
    got = si.amortization_location_total(nf, mf)
    assert got["CSCO"]["value"] == D(1017) and got["CSCO"]["total_member"] is None
    assert got["TOT"]["value"] == D(815) and got["TOT"]["total_member"] == "OperatingIncomeLoss" and set(got["TOT"]["parts"]) == {"CostOfSales", "Amort"}
    assert "ONE" not in got and "BAD" not in got   # one member is not a split; members that do not sum to the total are not a location split


def test_debt_vals_carries_own_and_earlier_columns():
    f = [dict(cik="1", a="A", p="2016-12-31"), dict(cik="1", a="B", p="2017-12-31")]
    got = si.debt_vals(f, {"A": "LongTermDebt|0|5"}, {"A": "LongTermDebt|0|4|2015-12-31"})
    assert got[0] == dict(cik="1", a="A", p="2016-12-31", vals="LongTermDebt|0|2016-12-31|5~LongTermDebt|0|2015-12-31|4") and got[1]["vals"] == ""


def test_member_facts_single_member_only_and_not_beside_an_undimensioned_fact():
    mf = {"A": "ComprehensiveIncomeNetOfTax|4|9081000000|Scenario=OtherComprehensiveIncomeNetOfTax;"
               "~NetIncomeLoss|4|5|EquityComponents=RetainedEarnings;~NetIncomeLoss|4|7|EquityComponents=CommonStock;"
               "~DividendsPerShare|4|1|EquityComponents=CommonStock;"
               "~CommonStockSharesOutstanding|0|100|EquityComponents=CommonStock;"}
    nf = {"A": "DividendsPerShare|4|2~CommonStockSharesIssued|0|100"}
    got = {(m["tag"], m["member"], m["value"]) for m in si.member_facts(nf, mf)}
    assert got == {("ComprehensiveIncomeNetOfTax", "Scenario=OtherComprehensiveIncomeNetOfTax", "9081000000")}
    # two members of one tag (ambiguous), a tag that has an undimensioned fact, and shares equal to shares issued: all rejected


def test_related_splits_need_both_members_of_one_tag():
    mf = {"COP": "AccountsPayableCurrent|0|5083|RelatedPartyTransactionsByRelatedParty=NonrelatedParty;~AccountsPayableCurrent|0|34|RelatedPartyTransactionsByRelatedParty=RelatedParty;",
          "ONE": "AccountsPayableCurrent|0|9|RelatedPartyTransactionsByRelatedParty=NonrelatedParty;",
          "DUR": "AccountsPayableCurrent|4|5|RelatedPartyTransactionsByRelatedParty=NonrelatedParty;~AccountsPayableCurrent|4|1|RelatedPartyTransactionsByRelatedParty=RelatedParty;"}
    got = si.related_splits(mf, r"AccountsPayable\w*")
    assert got == {"COP": dict(accession="COP", tag="AccountsPayableCurrent", nonrelated="5083", related="34")}
    assert si.related_splits(mf, r"Receivables\w*") == {}


def _row(a, pe, status, tags="", dp="dividends_per_share", cik="1"):
    return dict(cik=cik, accession=a, period_end=pe, data_point=dp, status=status, tags=tags, value=None, nodes="", why="", flags="")


def test_comparative_fill_takes_the_later_filing_that_resolves_the_data_point_to_one_element():
    T = "CommonStockDividendsPerShareDeclared"
    rows = [_row("A16", "2016-12-31", "not_presented"), _row("A17", "2017-12-31", "not_presented"), _row("A18", "2018-12-31", "mapped", T)]
    cf = {"A18": f"{T}|4|2.12|2017-12-31~{T}|4|2.05|2016-12-31~{T}|4|2.33|2018-12-31"}
    got = si.comparative_fill(rows, cf, set())
    assert got[("A16", "dividends_per_share")] == dict(accession="A18", tag=T, value="2.05", window="FY-2")
    assert got[("A17", "dividends_per_share")]["value"] == "2.12" and got[("A17", "dividends_per_share")]["window"] == "FY-1"
    # not filled: the later filing resolves a combination / nothing / two values; a missing year is not FY-1; an instant uses qtrs 0
    assert si.comparative_fill([_row("A16", "2016-12-31", "not_presented"), _row("A18", "2018-12-31", "mapped", T)], {"A18": f"{T}|4|2.12|2017-12-31"}, set()) == {}
    assert si.comparative_fill([rows[0], _row("A18", "2018-12-31", "mapped", T + "+" + T)], {"A18": f"{T}+{T}|4|2.05|2016-12-31"}, set()) == {}
    assert si.comparative_fill([rows[0], _row("A18", "2018-12-31", "no_role")], cf, set()) == {}
    assert si.comparative_fill([rows[0], _row("A18", "2018-12-31", "mapped", T)], {"A18": f"{T}|4|1|2016-12-31~{T}|4|2|2016-12-31"}, set()) == {}
    assert si.comparative_fill([rows[0], _row("A18", "2018-12-31", "mapped", T)], {"A18": f"{T}|0|2.05|2016-12-31"}, set()) == {}
    g = lambda pe, st, tags="", nodes="": dict(_row("G" + pe[:4], pe, st, tags, dp="goodwill"), nodes=nodes)
    face = g("2017-12-31", "mapped", nodes="Goodwill=7 [R4.htm:11]")
    assert si.comparative_fill([g("2016-12-31", "not_presented"), face], {"G2017": "Goodwill|0|7|2016-12-31"}, {"goodwill"}) != {}   # element read from nodes
    # an instant fills from FY-1 only (the balance sheet prints two columns); a note-resolved later filing does not fill a face data point
    assert si.comparative_fill([g("2015-12-31", "not_presented"), g("2016-12-31", "not_presented"), face], {"G2017": "Goodwill|0|7|2015-12-31"}, {"goodwill"}) == {}
    note = g("2017-12-31", "mapped", nodes="Goodwill=7 [NOTE]")
    assert si.comparative_fill([g("2016-12-31", "not_presented"), note], {"G2017": "Goodwill|0|7|2016-12-31"}, {"goodwill"}) == {}


def test_resolver_uses_the_extract_derived_splits_and_comparative_fill_without_side_files(monkeypatch):
    monkeypatch.setattr(RA, "EXT", {"ap": {"A1": dict(accession="A1", tag="AccountsPayableCurrent", nonrelated="5083", related="34")}, "ar": {},
                                    "cf": {("A2", "dividends_per_share"): dict(accession="A3", tag="T", value="2.05", window="FY-2")}})
    ap = dict(_row("A1", "2023-12-31", "mapped", "AccountsPayableCurrent", dp="accounts_payable"), value=D(5083))
    out = RA.apply_ap_related([ap], [])[0]
    assert out["status"] == "component_sum" and out["value"] == D(5117) and "ap_related_sum" in out["flags"]
    filled = RA.fill_printed_zero_and_comparative([_row("A2", "2016-12-31", "not_presented")], {})[0]
    assert filled["status"] == "mapped" and filled["value"] == D("2.05") and filled["accession"] == "A3" and filled["column"] == "comparative"
    assert "FY-2 column" in filled["nodes"] and "comparative_fill" in filled["flags"]
    monkeypatch.setitem(RA.EXT, "pz", {("A4", "share_buybacks"): dict(accession="A4", data_point="share_buybacks", tag="PaymentsForRepurchaseOfCommonStock",
                                                                      r_line="R6:30", label="Common stock repurchases")})
    z = RA.fill_printed_zero_and_comparative([_row("A4", "2020-12-31", "not_presented", dp="share_buybacks")], {})[0]
    assert z["status"] == "mapped" and z["value"] == 0 and "printed_zero" in z["flags"] and "[R6:30]" in z["nodes"]


def test_merge_rows_appends_the_companion_facts():
    got = si.merge_rows([("A", "x|4|1", "m", "c|4|1|2015-12-31", "z"), ("B", None, "m", None, None)], [("A", "y|4|2", None), ("C", "w|0|3", "w|0|2|2015-12-31")])
    assert got == [("A", "x|4|1~y|4|2", "m", "c|4|1|2015-12-31", "z"), ("B", None, "m", None, None), ("C", "w|0|3", None, "w|0|2|2015-12-31")]
    face = (TOOLS / "extract_facelines.sql").read_text()
    assert "t.custom or not (t.tag ~ (select r from rx)" in face and "tag ~* (select r from rx)" in face   # statement lines + custom family names


def test_member_facts_reject_component_columns_and_rounded_issued_counts_with_treasury():
    S = "CommonStockSharesOutstanding"
    mf = {"ADP": "ComprehensiveIncomeNetOfTax|4|25|EquityComponents=AccumulatedOtherComprehensiveIncome;",
          "ACN": f"{S}|0|24545000|EquityComponents=TreasuryStock;",
          "TMO": f"{S}|0|441000000|EquityComponents=CommonStock;", "TJX": f"{S}|0|1199100000|EquityComponents=CommonStock;"}
    nf = {"TMO": "CommonStockSharesIssued|0|440668112~TreasuryStockValue|0|5", "TJX": "CommonStockSharesIssued|0|1199099768"}
    got = {m["accession"]: m["value"] for m in si.member_facts(nf, mf)}
    assert got == {"TJX": "1199100000"}   # TJX retires repurchased shares: no treasury, so the rounded count is outstanding
    assert si.member_facts(nf, {"TJX": mf["TJX"]}, si.class_share_filings([dict(a="TJX", cpv="4|3|CommonStockSharesOutstanding|x|ClassOfStock=CommonClassA;|5")])) == []


def test_location_total_on_the_class_axis_needs_location_names():
    A = "AmortizationOfIntangibleAssets"
    mf = {"CSCO": f"{A}|4|1017|FiniteLivedIntangibleAssetsByMajorClass=CostofSalesandOperatingExpenses;~{A}|4|275|FiniteLivedIntangibleAssetsByMajorClass=OperatingExpense;~{A}|4|742|FiniteLivedIntangibleAssetsByMajorClass=CostOfSales;",
          "WFC": f"{A}|4|388|FiniteLivedIntangibleAssetsByMajorClass=FiniteLivedIntangibleAssets;~{A}|4|274|FiniteLivedIntangibleAssetsByMajorClass=ServicingContracts;~{A}|4|114|FiniteLivedIntangibleAssetsByMajorClass=CustomerRelationships;",
          "PFX": f"{A}|4|947|StatementOfIncomeLocationBalance=us-gaap:CostOfGoodsAndServicesSold;~{A}|4|916|StatementOfIncomeLocationBalance=us-gaap:OperatingExpenses;~{A}|4|1863|StatementOfIncomeLocationBalance=us-gaap:OperatingIncomeLoss;"}
    got = si.amortization_location_total({"CSCO": f"{A}|4|275", "WFC": f"{A}|4|108", "PFX": f"{A}|4|916"}, mf)
    assert got["CSCO"]["value"] == D(1017) and got["PFX"]["value"] == D(1863) and "WFC" not in got


def test_ar_split_fills_a_member_only_row_and_ap_split_takes_ap_elements_only(monkeypatch):
    monkeypatch.setitem(RA.EXT, "ar", {"G": dict(accession="G", tag="ReceivablesNetCurrent", nonrelated="8174", related="4")})
    out = RA.apply_ar_related([_row("G", "2024-12-31", "not_presented", dp="accounts_receivable")], [])[0]
    assert out["status"] == "component_sum" and out["value"] == D(8178) and "ar_related_sum" in out["flags"]
    import re as _re
    src = (TOOLS / "resolve_all.py").read_text()
    pat = _re.search(r"EXT\['ap'\] = standard_inputs.related_splits\(memberfacts, r'([^']+)'\)", src).group(1)
    mf = {"GEV": "AccountsPayableAndOtherAccruedLiabilitiesCurrent|0|8578|RelatedPartyTransactionsByRelatedParty=NonrelatedParty;~AccountsPayableAndOtherAccruedLiabilitiesCurrent|0|24|RelatedPartyTransactionsByRelatedParty=RelatedParty;",
          "SNDK": "AccountsPayableCurrent|0|366|RelatedPartyTransactionsByRelatedParty=NonrelatedParty;~AccountsPayableCurrent|0|400|RelatedPartyTransactionsByRelatedParty=RelatedParty;"}
    assert set(si.related_splits(mf, pat)) == {"SNDK"}   # payable + accrued is the combined element, not AP


def test_note_facts_pick_is_order_independent_and_most_precise():
    from resolve import note_facts
    for raw in ("A|4|2400000000~A|4|2436000000", "A|4|2436000000~A|4|2400000000"):
        assert note_facts(raw)[("A", 4)] == D(2436000000)          # CVS: the table figure, not the rounded text figure
    assert note_facts("C|4|5300~C|4|5309~C|4|5309")[("C", 4)] == D(5309)
    assert note_facts("B|4|2.66~B|4|2.56")[("B", 4)] == note_facts("B|4|2.56~B|4|2.66")[("B", 4)] == D("2.66")


def test_total_debt_reads_the_year_end_column_and_adds_the_note_lease():
    import total_debt as TD
    lines = "~".join(["BS|4|10|Assets|0|0||Total assets|900", "BS|4|20|LongTermDebtNoncurrent|0|0||Long-term debt|100",
                      "BS|4|30|StockholdersEquity|0|0||Total equity|500"])
    f = dict(cik="9", a="X1", p="2015-12-31", fd="", lines=lines, calc="")
    vals = "~".join(["LongTermDebtNoncurrent|0|2015-12-31|100", "LongTermDebtNoncurrent|0|2014-12-31|90", "LongTermDebtNoncurrent|0|2015-01-31|7",
                     "FinanceLeaseLiability|0|2015-12-31|6", "FinanceLeaseLiabilityPaymentsDue|0|2015-12-31|8"])
    out = {r["column"]: r for r in TD.run([f], [dict(cik="9", a="X1", p="2015-12-31", vals=vals)], {})}
    assert out["comparative"]["period_end"] == "2014-12-31" and D(out["comparative"]["value"]) == D(90)   # not the 334-day-old 2015-01-31 instant
    assert D(out["own"]["value"]) == D(106) and "FinanceLeaseLiability" in out["own"]["tags"]           # the payment schedule is not a debt-and-lease total


def test_product_service_cor_needs_member_only_product_and_service_lines():
    C = "CostOfGoodsAndServicesSold"
    mf = {"TMUS": f"{C}|4|6622|ProductOrService=Service;~{C}|4|6622|ProductOrService=Service;~{C}|4|11899|ProductOrService=Product;~{C}|4|11899|ProductOrService=ProductEquipment;",
          "UND": f"{C}|4|1|ProductOrService=Product;~{C}|4|2|ProductOrService=Service;",
          "SEG": f"{C}|4|1|ProductOrService=Product;~{C}|4|2|ProductOrService=Service;~{C}|4|3|ProductOrService=Licenses;",
          "ONE": f"{C}|4|1|ProductOrService=Product;",
          "TWO": f"{C}|4|1|ProductOrService=Product;~{C}|4|5|ProductOrService=ProductEquipment;~{C}|4|2|ProductOrService=Service;"}
    got = si.product_service_cor({"UND": f"{C}|4|3"}, mf)
    assert got == {"TMUS": dict(tag=C, product="11899", service="6622")}   # an undimensioned total, another member, one side, or two product figures: no split


def test_gross_profit_facts_and_ci_face_lines_from_the_extract():
    assert si.gross_profit_facts({"A": "GrossProfit|4|11947000000.0000~Revenues|4|5", "B": "GrossProfit|0|3"}) == {"A": D(11947000000)}
    cl = {"BA": f"{si.CI_INCL}|4|22|Comprehensive income, net of tax~ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest|4|21|NCI",
          "X": f"{si.CI_INCL}|5|9|second~{si.CI_INCL}|4|30|first"}
    got = si.ci_face_lines(cl)
    assert got["BA"] == dict(report="4", line="22", label="Comprehensive income, net of tax") and got["X"]["label"] == "first"
    assert si.face_clines([("A", "v", "c", "cl"), ("B", "v", "c")]) == {"A": "cl"}
    face = (TOOLS / "extract_facelines.sql").read_text(); main = (TOOLS / "extract_notefacts.sql").read_text()
    assert "l.stmt='CI'" in face and "cl.clines" in face and "ProductOrService=[^;=]+;$" in main
