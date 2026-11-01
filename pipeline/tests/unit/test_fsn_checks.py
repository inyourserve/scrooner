"""fsn_store.checks ties (design §5): NI attributable and the cross-statement ties of one filing."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.fsn_store import checks

FY, BSD = (date(2025, 12, 31), 4), (date(2025, 12, 31), 0)


def _vals(rows):
    return {
        (t, d, q): checks.Print(t, "us-gaap/2025", Decimal(v), -6, None)
        for t, (d, q), v in rows
    }


def _ties(on, rows):
    return {c["check_id"]: c for _s, _d, _q, c in checks.check_ties(on, _vals(rows))}


@pytest.mark.unit
def test_ni_total_minus_nci_equals_parent():
    on = {"IS": {"ProfitLoss", "NetIncomeLossAttributableToNoncontrollingInterest", "NetIncomeLoss"}}
    ok = _ties(on, [("ProfitLoss", FY, "1000000000"), ("NetIncomeLossAttributableToNoncontrollingInterest", FY, "50000000"), ("NetIncomeLoss", FY, "950000000")])
    assert ok["is_ni_total_minus_nci_eq_parent"]["ok"]
    bad = _ties(on, [("ProfitLoss", FY, "1000000000"), ("NetIncomeLossAttributableToNoncontrollingInterest", FY, "50000000"), ("NetIncomeLoss", FY, "1000000000")])
    assert not bad["is_ni_total_minus_nci_eq_parent"]["ok"]


@pytest.mark.unit
def test_cf_starts_from_the_is_net_income():
    on = {"IS": {"NetIncomeLoss", "ProfitLoss"}, "CF": {"ProfitLoss"}}
    rows = [("ProfitLoss", FY, "1000000000"), ("NetIncomeLoss", FY, "950000000")]
    c = _ties(on, rows)["cross_cf_ni_eq_is_ni"]
    assert c["ok"] and c["detail"] == {"cf_tag": "ProfitLoss", "is_tag": "ProfitLoss"}
    # the CF starts from ProfitLoss but the IS prints only the parent figure, 50M lower: a failure
    c2 = _ties({"IS": {"NetIncomeLoss"}, "CF": {"ProfitLoss"}}, rows)["cross_cf_ni_eq_is_ni"]
    assert not c2["ok"] and c2["lhs"] - c2["rhs"] == Decimal("50000000")


@pytest.mark.unit
def test_closing_cash_ties_to_bs_cash_plus_printed_restricted_cash():
    on = {"CF": {checks.CF_CASH_TOTAL}, "BS": {"CashAndCashEquivalentsAtCarryingValue", "RestrictedCashCurrent"}}
    rows = [(checks.CF_CASH_TOTAL, BSD, "120000000"), ("CashAndCashEquivalentsAtCarryingValue", BSD, "100000000"), ("RestrictedCashCurrent", BSD, "20000000")]
    assert _ties(on, rows)["cross_cf_closing_cash_eq_bs_cash"]["ok"]
    rows[2] = ("RestrictedCashCurrent", BSD, "10000000")
    assert not _ties(on, rows)["cross_cf_closing_cash_eq_bs_cash"]["ok"]


@pytest.mark.unit
def test_closing_cash_not_decided_when_restricted_cash_sits_in_another_bs_line():
    on = {"CF": {checks.CF_CASH_TOTAL}, "BS": {"CashAndCashEquivalentsAtCarryingValue"}}
    rows = [(checks.CF_CASH_TOTAL, BSD, "120000000"), ("CashAndCashEquivalentsAtCarryingValue", BSD, "100000000")]
    assert "cross_cf_closing_cash_eq_bs_cash" not in _ties(on, rows)


@pytest.mark.unit
def test_cash_change_identity_adds_fx_for_the_pre_2018_change_tag():
    def pr(tag, v):
        return checks.Print(tag, "us-gaap/2016", Decimal(v), -6, None)

    col = {
        (t, "us-gaap/2016"): pr(t, v)
        for t, v in (
            ("NetCashProvidedByUsedInOperatingActivities", "100"),
            ("NetCashProvidedByUsedInInvestingActivities", "-60"),
            ("NetCashProvidedByUsedInFinancingActivities", "-30"),
            ("EffectOfExchangeRateOnCashAndCashEquivalents", "-4"),
            ("CashAndCashEquivalentsPeriodIncreaseDecrease", "6"),
        )
    }
    c = {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}["cf_parts_eq_change"]
    assert c["ok"] and c["detail"]["fx_included"]


@pytest.mark.unit
def test_cash_change_identity_accepts_either_fx_layout_but_not_neither():
    def col(change):
        return {
            (t, "v"): checks.Print(t, "v", Decimal(v), -6, None)
            for t, v in (
                ("NetCashProvidedByUsedInOperatingActivities", "100"),
                ("NetCashProvidedByUsedInInvestingActivities", "-60"),
                ("NetCashProvidedByUsedInFinancingActivities", "-30"),
                ("EffectOfExchangeRateOnCashAndCashEquivalents", "-4"),
                ("CashAndCashEquivalentsPeriodIncreaseDecrease", change),
            )
        }

    def chk(change):
        return {x["check_id"]: x for x in checks.check_column("CF", col(change), {}, {})}["cf_parts_eq_change"]

    hd = chk("10")  # HD: the change line is printed before the FX line
    assert hd["ok"] and not hd["detail"]["fx_included"]
    assert chk("6")["ok"] and chk("6")["detail"]["fx_included"]  # MSFT layout
    assert not chk("8")["ok"]  # ties neither way: still a failure
