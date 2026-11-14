"""Accounting identities over the served values (proof/identities.py): pass, fail, skip, tolerance, MSFT FY2017."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof.identities import REASON, apply_identities
from scrooner_pipeline.proof.prove import (
    DISAGREE,
    NOT_PRESENTED,
    PROVEN,
    UNCHECKED,
    Proof,
    Shown,
)

M = 1_000_000
FY = ("FY", date(2016, 7, 1), date(2017, 6, 30))
INST = ("I", date(2017, 6, 30), date(2017, 6, 30))


def mk(
    name,
    value,
    period=FY,
    verdict=PROVEN,
    tags=(),
    combined=(),
    reason=None,
) -> Proof:
    s = Shown(
        1,
        name,
        period[0],
        period[1],
        period[2],
        Decimal(value),
        tuple(tags),
        "acc",
        (1,),
        combined=tuple(combined),
    )
    return Proof(shown=s, verdict=verdict, reason_code=reason)


def verdicts(ps):
    return [p.verdict for p in ps]


def is_(rev, cor, gp, opex=None, oi=None, **kw):
    ps = [
        mk("revenue_sanity_resolved", rev * M, **kw),
        mk("cost_of_revenue_resolved", cor * M, **kw),
        mk("gross_profit_resolved", gp * M, **kw),
    ]
    if opex is not None:
        ps += [
            mk("operating_expenses_resolved", opex * M),
            mk("operating_income_resolved", oi * M),
        ]
    return ps


def test_gross_profit_pass():
    ps = is_(89_950, 34_261, 55_689)
    assert apply_identities(ps) == {}
    assert verdicts(ps) == [PROVEN] * 3


def test_msft_fy2017_shape_breaks():
    ps = is_(89_950, 34_261, 62_310)
    assert apply_identities(ps) == {"gross_profit": 1}
    assert verdicts(ps) == [DISAGREE] * 3
    assert {p.reason_code for p in ps} == {REASON}
    rec = ps[0].checks["identity"]
    assert rec["name"] == "gross_profit"
    assert rec["members"] == {
        "revenue": str(89_950 * M),
        "cost_of_revenue": str(34_261 * M),
        "gross_profit": str(62_310 * M),
    }
    assert Decimal(rec["diff"]) == -(62_310 - 55_689) * M
    assert set(rec) >= {"lhs", "rhs", "diff", "tolerance"}


def test_only_proven_members_flip():
    ps = is_(89_950, 34_261, 62_310)
    ps[1].verdict = UNCHECKED
    apply_identities(ps)
    assert verdicts(ps) == [DISAGREE, UNCHECKED, DISAGREE]
    assert (
        ps[1].checks["identity"]["name"] == "gross_profit"
    )  # recorded, verdict untouched


def test_tolerance_edge():
    # 1 (unit 1) values: slack is 0.5 per member, 1.5 over three members
    def run(gp):
        ps = [
            mk("revenue_sanity_resolved", 1001),
            mk("cost_of_revenue_resolved", 401),
            mk("gross_profit_resolved", gp),
        ]
        apply_identities(ps)
        return ps[0].verdict

    assert run(600) == PROVEN  # exact
    assert run(601) == PROVEN  # diff 1 <= 1.5
    assert run(602) == DISAGREE  # diff 2 > 1.5


def test_skip_when_member_absent():
    ps = [mk("revenue_sanity_resolved", 100 * M), mk("gross_profit_resolved", 1 * M)]
    assert apply_identities(ps) == {}
    assert verdicts(ps) == [PROVEN, PROVEN]


def test_skip_not_presented_and_combined():
    ps = is_(100, 40, 1)
    ps[1].verdict = NOT_PRESENTED
    assert apply_identities(ps) == {}
    ps = is_(100, 40, 1)
    ps[1].shown = ps[1].shown.__class__(
        **{**ps[1].shown.__dict__, "combined": ("CostOfRevenue",)}
    )
    assert apply_identities(ps) == {}
    assert ps[0].verdict == PROVEN


def test_operating_income_with_gross_profit():
    ok = is_(102, 41, 61, 21, 40)
    assert apply_identities(ok) == {}
    bad = is_(102, 41, 61, 21, 45)
    assert apply_identities(bad) == {"operating_income": 1}
    assert bad[0].verdict == PROVEN  # revenue is not an operating_income member here
    assert bad[3].verdict == DISAGREE and bad[4].verdict == DISAGREE


def test_operating_income_without_gross_profit():
    def ps(oi):
        return [
            mk("revenue_sanity_resolved", 101 * M),
            mk("cost_of_revenue_resolved", 41 * M),
            mk("operating_expenses_resolved", 21 * M),
            mk("operating_income_resolved", oi * M),
        ]

    assert apply_identities(ps(39)) == {}
    bad = ps(49)
    assert apply_identities(bad) == {"operating_income": 1}
    assert verdicts(bad) == [DISAGREE] * 4


def bs(a, liab, eq, tags=()):
    return [
        mk("total_assets_resolved", a * M, INST),
        mk("total_liabilities_resolved", liab * M, INST),
        mk("stockholders_equity_resolved", eq * M, INST, tags=tags),
    ]


def cf(cfo, cfi, cff):
    return [
        mk("cfo_resolved", cfo * M),
        mk("cash_flow_investing_resolved", cfi * M),
        mk("cash_flow_financing_resolved", cff * M),
    ]


CHG = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    FY[1],
    FY[2],
)
FX = (
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    FY[1],
    FY[2],
)


def test_net_income_cf_tie():
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

    st = FilingStructure("acc", "1", "10-K", None, None)
    st.pre.append(
        PreLine(6, 1, "CF", "NetIncomeLoss", "us-gaap/2017", "Net income", False)
    )
    st.num[("NetIncomeLoss", FY[2], 4)].append(
        NumValue("NetIncomeLoss", "us-gaap/2017", FY[2], 4, "USD", Decimal(21 * M), -6)
    )
    ok = [mk("net_income_resolved", 21 * M)]
    assert apply_identities(ok, {}, {"acc": st}) == {}
    bad = [mk("net_income_resolved", 29 * M)]
    assert apply_identities(bad, {}, {"acc": st}) == {"net_income_cf": 1}
    assert bad[0].verdict == DISAGREE
    # a quarter is never judged against the annual cash-flow column
    q = [mk("net_income_resolved", 5 * M, ("Q", date(2017, 4, 1), date(2017, 6, 30)))]
    assert apply_identities(q, {}, {"acc": st}) == {}
    # no structure: skipped
    assert apply_identities([mk("net_income_resolved", 29 * M)], {}, {}) == {}


def test_net_income_cf_profitloss_nets_nci_income():
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

    st = FilingStructure("acc", "1", "10-K", None, None)
    st.pre.append(
        PreLine(6, 1, "CF", "ProfitLoss", "us-gaap/2017", "Net income", False)
    )
    st.num[("ProfitLoss", FY[2], 4)].append(
        NumValue("ProfitLoss", "us-gaap/2017", FY[2], 4, "USD", Decimal(25 * M), -6)
    )
    nci = ("NetIncomeLossAttributableToNoncontrollingInterest", FY[1], FY[2])
    ps = [mk("net_income_resolved", 21 * M)]
    assert apply_identities(ps, {nci: Decimal(4 * M)}, {"acc": st}) == {}
    # NCI income not printed and values differ: cannot tell parent from total, skip
    assert apply_identities([mk("net_income_resolved", 21 * M)], {}, {"acc": st}) == {}


def test_cf_start_value_is_annual_only():
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
    from scrooner_pipeline.proof.identities import cf_start_value

    st = FilingStructure("acc", "1", "10-K", None, None)
    st.pre.append(
        PreLine(6, 1, "CF", "NetIncomeLoss", "us-gaap/2017", "Net income", False)
    )
    st.num[("NetIncomeLoss", FY[2], 4)].append(
        NumValue("NetIncomeLoss", "us-gaap/2017", FY[2], 4, "USD", Decimal(21 * M), -6)
    )
    assert cf_start_value({"acc": st}, mk("net_income_resolved", 21 * M)) is not None
    q = mk("net_income_resolved", 5 * M, ("Q", date(2017, 4, 1), date(2017, 6, 30)))
    assert cf_start_value({"acc": st}, q) is None


# ---- identity triage rulings 2026-11-13 (B1-B5, C1-C3) ------------------------------------------------------------


def _pk(tag, period=INST):
    return (tag, None if period[0] == "I" else period[1], period[2])


def face(lines, vals):
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

    st = FilingStructure("acc", "1", "10-K", None, None)
    for i, tag in enumerate(lines):
        st.pre.append(PreLine(2, i, "BS", tag, "us-gaap/2017", tag, False))
    for tag, v in vals.items():
        st.num[(tag, INST[2], 0)].append(
            NumValue(tag, "us-gaap/2017", INST[2], 0, "USD", Decimal(v * M), -6)
        )
    return st


def _no_source(p):
    p.shown = p.shown.__class__(
        **{**p.shown.__dict__, "source_fact_ids": (), "tags": ()}
    )


def test_c1_c2_derived_not_printed_members_are_skipped():
    ps = is_(100, 40, 1)
    _no_source(ps[2])
    assert apply_identities(ps) == {}
    assert verdicts(ps) == [PROVEN] * 3
    b = bs(101, 5, 38)
    _no_source(b[1])
    assert apply_identities(b) == {}


def test_c3_derived_quarters_and_spans_are_skipped():
    q = ("Q", date(2017, 4, 1), date(2017, 6, 30))
    assert apply_identities(is_(100, 40, 1, period=q)) == {
        "gross_profit": 1
    }  # a filed quarter still breaks
    ps = is_(100, 40, 1, period=q)
    ps[0].shown = ps[0].shown.__class__(**{**ps[0].shown.__dict__, "is_derived": True})
    assert apply_identities(ps) == {}
    span = ("Q", date(2017, 1, 1), date(2017, 9, 30))
    assert apply_identities(is_(100, 40, 1, period=span)) == {}


# --- the filing's own arithmetic (fsn.filing_check) and the node tie ---------------------------------------------
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue
from scrooner_pipeline.proof.identities import (
    QUARANTINE_REASON,
    CheckRow,
)

KIDS = ("Revenues", "CostOfRevenue")


def tagged_is(rev, cor, gp):
    ps = is_(rev, cor, gp)
    for p, t in zip(ps, ("Revenues", "CostOfRevenue", "GrossProfit"), strict=True):
        p.shown = p.shown.__class__(**{**p.shown.__dict__, "tags": (t,)})
    return ps


def gp_check(ok, lhs=55, rhs=55):
    return {
        ("acc", FY[2], 4): [
            CheckRow(
                "IS",
                "calc:GrossProfit:r1",
                ok,
                Decimal(lhs * M),
                Decimal(rhs * M),
                Decimal(M // 2),
                KIDS,
            )
        ]
    }


def test_filing_check_pass_covers_the_relation_so_no_hand_rule_runs():
    # the hand rule alone would break (100 - 40 != 1); the filing's own passing check covers the relation
    ps = tagged_is(100, 40, 1)
    assert apply_identities(ps, checks=gp_check(True)) == {}
    assert verdicts(ps) == [PROVEN] * 3
    ps = tagged_is(100, 40, 1)  # no filing_check row: the fallback judges it
    assert apply_identities(ps, checks={}) == {"gross_profit": 1}
    assert ps[0].checks["identity"]["source"] == "hand_fallback"


def test_filing_check_fail_quarantines_the_filings_cells():
    ps = tagged_is(100, 40, 60)
    assert apply_identities(ps, checks=gp_check(False, 60, 61)) == {
        "calc:GrossProfit:r1": 1
    }
    assert verdicts(ps) == [DISAGREE] * 3
    assert {p.reason_code for p in ps} == {QUARANTINE_REASON}
    rec = ps[2].checks["identity"]
    assert rec["source"] == "filing_check" and rec["check_id"] == "calc:GrossProfit:r1"


def test_nested_total_only_members_of_the_failing_check_flip():
    # OperatingIncomeLoss = GrossProfit - OperatingExpenses fails; the GrossProfit check (a child total of it) passes
    ps = tagged_is(100, 40, 60)
    ps += [
        mk("operating_expenses_resolved", 20 * M, tags=("OperatingExpenses",)),
        mk("operating_income_resolved", 41 * M, tags=("OperatingIncomeLoss",)),
    ]
    checks = gp_check(True, 60, 60)
    checks[("acc", FY[2], 4)].append(
        CheckRow(
            "IS",
            "calc:OperatingIncomeLoss:r1",
            False,
            Decimal(41 * M),
            Decimal(40 * M),
            Decimal(M),
            ("GrossProfit", "OperatingExpenses"),
        )
    )
    apply_identities(ps, checks=checks)
    assert [p.verdict for p in ps[:2]] == [PROVEN, PROVEN]  # only in the passing check
    assert [p.verdict for p in ps[2:]] == [DISAGREE] * 3  # GP (child), opex, OI


def node_filing(value, dcml):
    st = FilingStructure("acc", "1", "10-K", None, None)
    st.num[("Revenues", FY[2], 4)].append(
        NumValue("Revenues", "us-gaap/2017", FY[2], 4, "USD", Decimal(value), dcml)
    )
    return {"acc": st}


def test_node_tie_within_the_filers_dcml_rounding():
    def run(served, dcml):
        ps = [mk("revenue_resolved", served, tags=("Revenues",))]
        return apply_identities(ps, structures=node_filing(100 * M, dcml)), ps

    c, ps = run(100 * M + 400_000, -6)  # inside half a million
    assert c == {} and verdicts(ps) == [PROVEN]
    c, ps = run(100 * M + 600_000, -6)  # outside: a served value that is not its node
    assert c == {"node_mismatch": 1} and verdicts(ps) == [DISAGREE]
    assert ps[0].reason_code == REASON
    c, ps = run(
        100 * M + 1, 0
    )  # a filer printing to the unit gets no slack beyond half a unit
    assert c == {"node_mismatch": 1}


def test_component_sum_cell_is_no_single_node():
    # opex = parts; the shown tags carry one part only, whose node is far below the sum
    def run(kind):
        ps = [mk("revenue_resolved", 100 * M, tags=("Revenues",))]
        ps[0].checks["claim"] = {"kind": kind}
        st = node_filing(10 * M, -6)
        return apply_identities(ps, structures=st), ps

    c, ps = run("concept")
    assert c == {"node_mismatch": 1} and verdicts(ps) == [DISAGREE]
    c, ps = run("component")
    assert c == {} and verdicts(ps) == [PROVEN]


def test_node_is_the_claimed_tag_not_a_source_record_tag():
    # AMD cost of revenue: claimed on the node (100), the source records name another tag (a part)
    def run(claim_tags):
        ps = [mk("revenue_resolved", 100 * M, tags=("SomePartTag",))]
        ps[0].checks["claim"] = {"kind": "concept", "tags": claim_tags}
        st = node_filing(100 * M, -6)
        st["acc"].num[("SomePartTag", FY[2], 4)].append(
            NumValue("SomePartTag", "us-gaap/2017", FY[2], 4, "USD", Decimal(10 * M), -6)
        )
        return apply_identities(ps, structures=st), ps

    c, ps = run(["Revenues"])
    assert c == {} and verdicts(ps) == [PROVEN]
    c, ps = run(["Revenues", "Other"])  # two claimed tags: no single node
    assert c == {} and verdicts(ps) == [PROVEN]
