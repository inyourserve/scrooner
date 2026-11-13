"""Claim-driven cell proofs (company_tag_map is the claim, the filing FSN/XBRL is the check): share counts,
per-share values, component sums and note-only lines. Pure."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
from scrooner_pipeline.proof.shown import claim_for

ADSH = "0000320193-25-000073"
FY_END = date(2025, 9, 27)
DDATE = date(2025, 9, 30)  # FSN rounds period ends to the month end


def world(tag, uom, value, dcml, stmt="IS", qtrs=4, with_pre=True):
    s = FilingStructure(ADSH, "0000320193", "10-K", date(2025, 10, 31), FY_END)
    if with_pre:
        s.pre.append(PreLine(2, 1, stmt, tag, "us-gaap/2025", tag, False))
    s.num[(tag, DDATE, qtrs)].append(
        NumValue(tag, "us-gaap/2025", DDATE, qtrs, uom, Decimal(value), dcml)
    )
    return s


def cell(name, value, claim, grain="FY"):
    start = date(2024, 9, 29) if grain != "I" else FY_END
    return pv.Shown(
        3,
        name,
        grain,
        start,
        FY_END,
        Decimal(value),
        ("x",),
        ADSH,
        (1,),
        False,
        6,  # the company's money scale: 1.5M of slack, which must never apply to shares or cents
        claim=claim,
    )


@pytest.mark.unit
def test_share_count_is_proven_in_shares_and_decimals_not_the_money_slack():
    tag = "WeightedAverageNumberOfDilutedSharesOutstanding"
    claim = pv.Claim("concept", "IS", tags=(tag,))
    s = world(tag, "shares", "15000000000", -3)
    ok = pv.prove_cell(
        cell("weighted_diluted_shares", "15000000000", claim), s, "2025q4"
    )
    assert ok.verdict == pv.PROVEN and ok.checks["unit_scale"]["class"] == "shares"
    # 5,000 shares off at decimals -3 (slack 1,500): the $ scale (1.5M) must not hide it
    bad = pv.prove_cell(
        cell("weighted_diluted_shares", "15000005000", claim), s, "2025q4"
    )
    assert bad.verdict == pv.DISAGREE
    assert bad.reason_code == "shown_differs_from_printed_line"
    # a USD value under the share tag is not a share count
    usd = world(tag, "USD", "15000000000", -3)
    p = pv.prove_cell(
        cell("weighted_diluted_shares", "15000000000", claim), usd, "2025q4"
    )
    assert p.verdict == pv.NOT_PRESENTED


@pytest.mark.unit
def test_per_share_value_uses_cents_not_the_money_slack():
    tag = "EarningsPerShareBasic"
    claim = pv.Claim("concept", "IS", tags=(tag,))
    s = world(tag, "USD/shares", "7.49", 2)
    ok = pv.prove_cell(cell("basic_eps_resolved", "7.49", claim), s, "2025q4")
    assert ok.verdict == pv.PROVEN and ok.checks["unit_scale"]["class"] == "per_share"
    bad = pv.prove_cell(cell("basic_eps_resolved", "7.52", claim), s, "2025q4")
    assert bad.verdict == pv.DISAGREE


@pytest.mark.unit
def test_component_sum_proves_the_sum_of_parts_each_matched_in_the_filing():
    claim = pv.Claim(
        "component",
        "BS",
        parts=((1, "LongTermDebtCurrent"), (1, "LongTermDebtNoncurrent")),
    )
    s = FilingStructure(ADSH, "0000320193", "10-K", date(2025, 10, 31), FY_END)
    for ln, (t, v) in enumerate(
        [
            ("LongTermDebtCurrent", "10000000000"),
            ("LongTermDebtNoncurrent", "85000000000"),
        ]
    ):
        s.pre.append(PreLine(4, ln, "BS", t, "us-gaap/2025", t, False))
        s.num[(t, DDATE, 0)].append(
            NumValue(t, "us-gaap/2025", DDATE, 0, "USD", Decimal(v), -6)
        )
    ok = pv.prove_cell(cell("total_debt_resolved", "95000000000", claim, "I"), s, "q")
    assert ok.verdict == pv.PROVEN
    assert [f["tag"] for f in ok.checks["component_parts"]["found"]] == [
        "LongTermDebtCurrent",
        "LongTermDebtNoncurrent",
    ]
    # the shown value is one leg only: the sum differs
    bad = pv.prove_cell(cell("total_debt_resolved", "85000000000", claim, "I"), s, "q")
    assert bad.verdict == pv.DISAGREE
    # a part the filing does not carry: never a guessed zero
    del s.num[("LongTermDebtCurrent", DDATE, 0)]
    gone = pv.prove_cell(cell("total_debt_resolved", "85000000000", claim, "I"), s, "q")
    assert gone.verdict == pv.UNCHECKED


@pytest.mark.unit
def test_note_only_line_is_proven_against_the_note_fact_with_no_face():
    tag = "InterestPaidNet"
    claim = pv.Claim("concept", "UN", tags=(tag,))
    s = world(tag, "USD", "3500000000", -6, with_pre=False)
    ok = pv.prove_cell(cell("cash_paid_for_interest", "3500000000", claim), s, "q")
    assert ok.verdict == pv.PROVEN
    assert ok.checks["statement_face"]["status"] == "n/a"
    bad = pv.prove_cell(cell("cash_paid_for_interest", "3900000000", claim), s, "q")
    assert bad.verdict == pv.DISAGREE
    # no claim and no hand expectation: nothing to prove it against
    none = pv.prove_cell(cell("cash_paid_for_interest", "1", None), s, "q")
    assert none.verdict == pv.UNCHECKED


@pytest.mark.unit
def test_the_claim_sign_applies_and_the_expected_map_is_the_fallback():
    s = world("NetIncomeLoss", "USD", "112010000000", -6)
    claim = pv.Claim("concept", "IS", tags=("NetIncomeLoss",), sign=-1)
    p = pv.prove_cell(cell("net_income_resolved", "-112010000000", claim), s, "q")
    assert p.verdict == pv.PROVEN
    assert p.checks["claim"]["source"] == "company_tag_map"
    # a claim naming a statement that does not print the line falls back to EXPECTED
    wrong = pv.Claim("concept", "CF", tags=("NetIncomeLoss",))
    fb = pv.prove_cell(cell("net_income_resolved", "112010000000", wrong), s, "q")
    assert fb.verdict == pv.PROVEN and fb.checks["claim"]["source"] == "expected_map"


@pytest.mark.unit
def test_claim_for_takes_the_row_whose_era_holds_the_period_and_the_components():
    d = date
    rows = [
        (1, "concept", "IS", "OldTag", "x", None, 1, d(2015, 3, 31), d(2018, 3, 31)),
        (2, "concept", "IS", "NewTag", "x", None, 1, d(2018, 6, 30), None),
        (3, "component", "BS", "A", None, "debt", 1, d(2015, 1, 1), None),
        (4, "component", "BS", "B", None, "debt", -1, d(2015, 1, 1), None),
    ]
    assert claim_for(rows, "x", d(2017, 12, 31)).tags == ("OldTag",)
    assert claim_for(rows, "x", d(2020, 12, 31)).tags == ("NewTag",)
    assert claim_for(rows, "x", d(2014, 12, 31)) is None
    c = claim_for(rows, "debt", d(2020, 12, 31))
    assert c.kind == "component" and c.parts == ((1, "A"), (-1, "B"))


@pytest.mark.unit
def test_without_filer_decimals_shares_and_cents_never_fall_back_to_the_money_scale():
    # FSN num without a dcml: money falls back to the company's scale (6 = 1.5M); a share count must
    # not (whole shares) and a per-share value must not (cents)
    tag = "WeightedAverageNumberOfDilutedSharesOutstanding"
    claim = pv.Claim("concept", "IS", tags=(tag,))
    s = world(tag, "shares", "15000000000", None)
    ok = pv.prove_cell(cell("weighted_diluted_shares", "15000000001", claim), s, "q")
    assert ok.verdict == pv.PROVEN  # one share off is inside 1.5 whole shares
    bad = pv.prove_cell(cell("weighted_diluted_shares", "15000005000", claim), s, "q")
    assert bad.verdict == pv.DISAGREE
    eps = "EarningsPerShareBasic"
    eclaim = pv.Claim("concept", "IS", tags=(eps,))
    es = world(eps, "USD/shares", "7.49", None)
    assert (
        pv.prove_cell(cell("basic_eps_resolved", "7.50", eclaim), es, "q").verdict
        == pv.PROVEN
    )
    assert (
        pv.prove_cell(cell("basic_eps_resolved", "7.60", eclaim), es, "q").verdict
        == pv.DISAGREE
    )
