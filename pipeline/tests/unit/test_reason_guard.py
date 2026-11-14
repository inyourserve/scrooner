"""False-reason guard (reason_guard.py): PM final draw 2026-11-14."""

from datetime import date
from decimal import Decimal as D

from scrooner_pipeline.mapper import reason_guard as rg

END = date(2016, 12, 31)
CI = "ComprehensiveIncomeNetOfTax"
CI_NCI = "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest"
AM = "AmortizationOfIntangibleAssets"


def f(value, qtrs=4, dim=False, seg="", dd=END):
    return rg.Fact(dd, qtrs, dim, seg, D(value))


def test_kind_of():
    assert rg.kind_of("not_presented") == rg.NOT_PRESENTED
    assert rg.kind_of("combined") == rg.COMBINED
    assert rg.kind_of("not_in_template", "line_presented_combined") == rg.COMBINED
    assert rg.kind_of("not_in_template", "other") is None
    assert rg.kind_of("mapped") is None


def test_combined_reason_refuted_by_parent_tag_not_by_the_tag_it_names():
    """PM FY2016: the reason's own node is the including-NCI tag; the parent tag is printed (R5)."""
    facts = {CI: [f("6810000000")], CI_NCI: [f("7043000000")]}
    text = f"{CI_NCI} [R5.htm:13] | why: only the figure including noncontrolling interest is printed"
    ev = rg.evidence_for(rg.COMBINED, END, False, {CI, CI_NCI}, text, facts)
    assert [e["tag"] for e in ev] == [CI] and ev[0]["value"] == D("6810000000")
    # only the named tag is stored: the reason stands
    assert rg.evidence_for(rg.COMBINED, END, False, {CI, CI_NCI}, text, {CI_NCI: facts[CI_NCI]}) == []


def test_member_rows_refute_not_presented_only():
    facts = {
        AM: [
            f("58000000", dim=True, seg="IncomeStatementLocation=CostOfSales;"),
            f("101000000", dim=True, seg="IncomeStatementLocation=MarketingAdministrationAndResearchCosts;"),
        ]
    }
    ev = rg.evidence_for(rg.NOT_PRESENTED, END, False, {AM}, "", facts)
    assert ev and ev[0]["member"] and ev[0]["value"] == D("159000000")
    assert rg.evidence_for(rg.COMBINED, END, False, {AM}, "", facts) == []


def test_other_column_or_wrong_grain_is_no_evidence():
    other = {AM: [f("5", dd=date(2015, 12, 31))]}
    assert rg.evidence_for(rg.NOT_PRESENTED, END, False, {AM}, "", other) == []
    quarter = {AM: [f("5", qtrs=1)]}
    assert rg.evidence_for(rg.NOT_PRESENTED, END, False, {AM}, "", quarter) == []
    inst = {AM: [f("5", qtrs=0)]}
    assert rg.evidence_for(rg.NOT_PRESENTED, END, True, {AM}, "", inst)
    assert rg.evidence_for(rg.NOT_PRESENTED, END, False, {AM}, "", inst) == []


def test_base_name_strips_resolved():
    assert rg.base_name("total_debt_resolved") == "total_debt"
