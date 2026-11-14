"""The structural resolver's standard inputs (data-team/tags/line_map/tools/standard_inputs.py + extract_notefacts.sql): single-member
own-period facts (equity column, RelatedParty Nonrelated/Related, Scenario), accretion facts and earlier-column (comparative, parenthetical
per-share) facts come from ONE extract, so the side files (_member-face-facts, _ap/_ar-related-split, _comparative-fill) are not needed at 1,000 companies.
The parity cases (COP AP 2023, LLY DPS 2016, ORCL comprehensive income) were run live 2026-11-14: 0 of 1,908 rows differ side files vs extract."""

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
    sql = si.build_sql(["1163165", "0001341439"], extra_tags=["CommonStockDividendsPerShareDeclared"])
    assert "/*" not in sql.split("set statement_timeout")[1]
    assert "cik::bigint in (1163165,1341439)" in sql
    assert "AccountsPayableCurrent" in sql and "CommonStockDividendsPerShareDeclared" in sql
    with pytest.raises(AssertionError):
        si.build_sql(["1; drop table x"])


def test_split_rows():
    nf, mf, cf = si.split_rows([("A", "t|4|1", None, None), ("B", None, "t|4|1|Scenario=X;", "t|4|2|2015-12-31")])
    assert nf == {"A": "t|4|1"} and mf == {"B": "t|4|1|Scenario=X;"} and cf == {"B": "t|4|2|2015-12-31"}


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
    assert si.comparative_fill([_row("A16", "2016-12-31", "not_presented", dp="goodwill"), _row("A18", "2018-12-31", "mapped", "Goodwill", dp="goodwill")],
                               {"A18": "Goodwill|0|7|2016-12-31"}, {"goodwill"}) != {}


def test_resolver_uses_the_extract_derived_splits_and_comparative_fill_without_side_files(monkeypatch):
    for k in ("COMPARATIVE_FILL", "AP_RELATED_SPLIT", "AR_RELATED_SPLIT", "PRINTED_ZERO"):
        monkeypatch.setenv(k, "/nonexistent")
    monkeypatch.setattr(RA, "EXT", {"ap": {"A1": dict(accession="A1", tag="AccountsPayableCurrent", nonrelated="5083", related="34")}, "ar": {},
                                    "cf": {("A2", "dividends_per_share"): dict(accession="A3", tag="T", value="2.05", window="FY-2")}})
    ap = dict(_row("A1", "2023-12-31", "mapped", "AccountsPayableCurrent", dp="accounts_payable"), value=D(5083))
    out = RA.apply_ap_related([ap], [])[0]
    assert out["status"] == "component_sum" and out["value"] == D(5117) and "ap_related_sum" in out["flags"]
    filled = RA.fill_printed_zero_and_comparative([_row("A2", "2016-12-31", "not_presented")], {})[0]
    assert filled["status"] == "mapped" and filled["value"] == D("2.05") and filled["accession"] == "A3" and filled["column"] == "comparative"
    assert "FY-2 column" in filled["nodes"] and "comparative_fill" in filled["flags"]
