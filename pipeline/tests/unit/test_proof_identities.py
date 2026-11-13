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
    assert ps[1].checks["identity"]["name"] == "gross_profit"  # recorded, verdict untouched


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


def test_balance_sheet_pass_fail():
    assert apply_identities(bs(101, 61, 40)) == {}
    bad = bs(101, 61, 47)
    assert apply_identities(bad) == {"balance_sheet": 1}
    assert verdicts(bad) == [DISAGREE] * 3


def test_balance_sheet_nci_and_temporary_equity():
    key = ("MinorityInterest", None, INST[2])
    # parent-only equity: NCI printed -> A = L + SE + NCI
    assert apply_identities(bs(101, 56, 38), {key: Decimal(7 * M)}) == {}
    # without the printed NCI the same cells break
    assert apply_identities(bs(101, 56, 38)) == {"balance_sheet": 1}
    # equity already includes NCI: the NCI fact must not be added again
    incl = ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",)
    assert apply_identities(bs(101, 63, 38, tags=incl), {key: Decimal(7 * M)}) == {}
    # temporary equity printed
    temp = (
        "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
        None,
        INST[2],
    )
    assert apply_identities(bs(101, 56, 38), {temp: Decimal(7 * M)}) == {}


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


def test_cash_change_pass_fail_skip():
    printed = {CHG: Decimal(13 * M), FX: Decimal(3 * M)}
    assert apply_identities(cf(51, -31, -9), printed) == {}
    bad = cf(51, -31, -19)
    assert apply_identities(bad, printed) == {"cash_change": 1}
    assert verdicts(bad) == [DISAGREE] * 3
    # fx not printed: never assumed zero
    skip = cf(51, -31, -19)
    assert apply_identities(skip, {CHG: Decimal(13 * M)}) == {}
    assert verdicts(skip) == [PROVEN] * 3
    # change in cash not printed
    assert apply_identities(cf(51, -31, -19), {FX: Decimal(M)}) == {}


def test_cash_change_discontinued_flows_included():
    disc = (
        "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
        FY[1],
        FY[2],
    )
    printed = {CHG: Decimal(17 * M), FX: Decimal(3 * M), disc: Decimal(4 * M)}
    assert apply_identities(cf(51, -31, -9), printed) == {}


def test_net_income_cf_tie():
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

    st = FilingStructure("acc", "1", "10-K", None, None)
    st.pre.append(PreLine(6, 1, "CF", "NetIncomeLoss", "us-gaap/2017", "Net income", False))
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
    st.pre.append(PreLine(6, 1, "CF", "ProfitLoss", "us-gaap/2017", "Net income", False))
    st.num[("ProfitLoss", FY[2], 4)].append(
        NumValue("ProfitLoss", "us-gaap/2017", FY[2], 4, "USD", Decimal(25 * M), -6)
    )
    nci = ("NetIncomeLossAttributableToNoncontrollingInterest", FY[1], FY[2])
    ps = [mk("net_income_resolved", 21 * M)]
    assert apply_identities(ps, {nci: Decimal(4 * M)}, {"acc": st}) == {}
    # NCI income not printed and values differ: cannot tell parent from total, skip
    assert apply_identities([mk("net_income_resolved", 21 * M)], {}, {"acc": st}) == {}


def test_cash_change_not_judged_on_a_quarter():
    q = ("Q", date(2017, 4, 1), date(2017, 6, 30))
    chg = (CHG[0], q[1], q[2])
    fx = (FX[0], q[1], q[2])
    ps = [
        mk("cfo_resolved", 51 * M, q),
        mk("cash_flow_investing_resolved", -31 * M, q),
        mk("cash_flow_financing_resolved", -19 * M, q),
    ]
    assert apply_identities(ps, {chg: Decimal(13 * M), fx: Decimal(3 * M)}) == {}


def test_cf_start_value_is_annual_only():
    from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
    from scrooner_pipeline.proof.identities import cf_start_value

    st = FilingStructure("acc", "1", "10-K", None, None)
    st.pre.append(PreLine(6, 1, "CF", "NetIncomeLoss", "us-gaap/2017", "Net income", False))
    st.num[("NetIncomeLoss", FY[2], 4)].append(
        NumValue("NetIncomeLoss", "us-gaap/2017", FY[2], 4, "USD", Decimal(21 * M), -6)
    )
    assert cf_start_value({"acc": st}, mk("net_income_resolved", 21 * M)) is not None
    q = mk("net_income_resolved", 5 * M, ("Q", date(2017, 4, 1), date(2017, 6, 30)))
    assert cf_start_value({"acc": st}, q) is None


def test_cash_change_before_fx_under_the_including_tag_is_not_a_break():
    # HD: the printed 'change' equals the three flows alone, the fx line is separate
    printed = {CHG: Decimal(11 * M), FX: Decimal(3 * M)}
    assert apply_identities(cf(51, -31, -9), printed) == {}
