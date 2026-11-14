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
    on = {
        "IS": {
            "ProfitLoss",
            "NetIncomeLossAttributableToNoncontrollingInterest",
            "NetIncomeLoss",
        }
    }
    ok = _ties(
        on,
        [
            ("ProfitLoss", FY, "1000000000"),
            ("NetIncomeLossAttributableToNoncontrollingInterest", FY, "50000000"),
            ("NetIncomeLoss", FY, "950000000"),
        ],
    )
    assert ok["is_ni_total_minus_nci_eq_parent"]["ok"]
    bad = _ties(
        on,
        [
            ("ProfitLoss", FY, "1000000000"),
            ("NetIncomeLossAttributableToNoncontrollingInterest", FY, "50000000"),
            ("NetIncomeLoss", FY, "1000000000"),
        ],
    )
    assert not bad["is_ni_total_minus_nci_eq_parent"]["ok"]


@pytest.mark.unit
def test_cf_starts_from_the_is_net_income():
    on = {"IS": {"NetIncomeLoss", "ProfitLoss"}, "CF": {"ProfitLoss"}}
    rows = [("ProfitLoss", FY, "1000000000"), ("NetIncomeLoss", FY, "950000000")]
    c = _ties(on, rows)["cross_cf_ni_eq_is_ni"]
    assert c["ok"] and c["detail"] == {"cf_tag": "ProfitLoss", "is_tag": "ProfitLoss"}
    # the CF starts from ProfitLoss but the IS prints only the parent figure, 50M lower: a failure
    c2 = _ties({"IS": {"NetIncomeLoss"}, "CF": {"ProfitLoss"}}, rows)[
        "cross_cf_ni_eq_is_ni"
    ]
    assert not c2["ok"] and c2["lhs"] - c2["rhs"] == Decimal("50000000")


@pytest.mark.unit
def test_closing_cash_ties_to_bs_cash_plus_printed_restricted_cash():
    on = {
        "CF": {checks.CF_CASH_TOTAL},
        "BS": {"CashAndCashEquivalentsAtCarryingValue", "RestrictedCashCurrent"},
    }
    rows = [
        (checks.CF_CASH_TOTAL, BSD, "120000000"),
        ("CashAndCashEquivalentsAtCarryingValue", BSD, "100000000"),
        ("RestrictedCashCurrent", BSD, "20000000"),
    ]
    assert _ties(on, rows)["cross_cf_closing_cash_eq_bs_cash"]["ok"]
    rows[2] = ("RestrictedCashCurrent", BSD, "10000000")
    assert not _ties(on, rows)["cross_cf_closing_cash_eq_bs_cash"]["ok"]


@pytest.mark.unit
def test_closing_cash_not_decided_when_restricted_cash_sits_in_another_bs_line():
    on = {"CF": {checks.CF_CASH_TOTAL}, "BS": {"CashAndCashEquivalentsAtCarryingValue"}}
    rows = [
        (checks.CF_CASH_TOTAL, BSD, "120000000"),
        ("CashAndCashEquivalentsAtCarryingValue", BSD, "100000000"),
    ]
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
    c = {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}[
        "cf_parts_eq_change"
    ]
    assert c["ok"] and c["detail"]["fx_included"]


@pytest.mark.unit
def test_cash_change_identity_accepts_either_fx_layout_but_not_neither():
    def col(change):
        return {
            (t, "v"): checks.Print(
                t, "v", Decimal(v), 0, None
            )  # whole units: tolerance 0.5 per term
            for t, v in (
                ("NetCashProvidedByUsedInOperatingActivities", "1000"),
                ("NetCashProvidedByUsedInInvestingActivities", "-600"),
                ("NetCashProvidedByUsedInFinancingActivities", "-300"),
                ("EffectOfExchangeRateOnCashAndCashEquivalents", "-40"),
                ("CashAndCashEquivalentsPeriodIncreaseDecrease", change),
            )
        }

    def chk(change):
        return {
            x["check_id"]: x for x in checks.check_column("CF", col(change), {}, {})
        }["cf_parts_eq_change"]

    hd = chk("100")  # HD: the change line is printed before the FX line
    assert hd["ok"] and not hd["detail"]["fx_included"]
    assert chk("60")["ok"] and chk("60")["detail"]["fx_included"]  # MSFT layout
    assert not chk("80")["ok"]  # ties neither way: still a failure


@pytest.mark.unit
def test_cash_change_identity_uses_the_disposal_group_fx_tag():
    col = {
        (t, "v"): checks.Print(t, "v", Decimal(v), -6, None)
        for t, v in (
            ("NetCashProvidedByUsedInOperatingActivities", "100"),
            ("NetCashProvidedByUsedInInvestingActivities", "-60"),
            ("NetCashProvidedByUsedInFinancingActivities", "-30"),
            (
                "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
                "-4",
            ),
            (
                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
                "6",
            ),
        )
    }
    c = {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}[
        "cf_parts_eq_change"
    ]
    assert c["ok"] and c["detail"]["fx_included"]


@pytest.mark.unit
def test_cash_change_identity_tries_every_candidate_change_tag():
    def chk(second):
        col = {
            (t, "v"): checks.Print(t, "v", Decimal(v), 0, None)
            for t, v in (
                ("NetCashProvidedByUsedInOperatingActivities", "1000"),
                ("NetCashProvidedByUsedInInvestingActivities", "-600"),
                ("NetCashProvidedByUsedInFinancingActivities", "-300"),
                (
                    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
                    "55",
                ),
                ("CashAndCashEquivalentsPeriodIncreaseDecrease", second),
            )
        }
        return {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}[
            "cf_parts_eq_change"
        ]

    assert (
        chk("100")["ok"]
        and chk("100")["detail"]["change_tag"]
        == "CashAndCashEquivalentsPeriodIncreaseDecrease"
    )
    assert not chk("56")["ok"]


@pytest.mark.unit
def test_tolerance_treats_the_inf_decimals_sentinel_as_exact():
    # FSN dcml sentinel for decimals="INF": a tolerance of 5e-32769 overflows Postgres numeric
    assert checks.tol_of([32767, -6]) == Decimal(500000)
    assert checks.tol_of([None]) == Decimal("0.5")


def _cf(rows, version="us-gaap/2023", dcml=-6):
    return {
        (t, version): checks.Print(t, version, Decimal(v), dcml, None) for t, v in rows
    }


MSFT_FY2024 = (
    ("NetCashProvidedByUsedInOperatingActivities", "118548000000"),
    ("NetCashProvidedByUsedInFinancingActivities", "-37757000000"),
    ("NetCashProvidedByUsedInInvestingActivities", "-96970000000"),
    (
        "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
        "-210000000",
    ),
    (
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
        "-16389000000",
    ),
)


@pytest.mark.unit
def test_cash_change_fallback_finds_the_disposal_group_fx_variant():
    # MSFT 10-K 0000950170-24-087843 FY2024: the FX line uses the disposal-group element; without it the
    # check failed by exactly the FX effect (-210M) and v10 quarantined the filing
    c = checks.cf_change_check(_cf(MSFT_FY2024), {})
    assert (
        c["ok"]
        and c["detail"]["fx_included"]
        and c["detail"]["form"] == "fallback_totals"
    )
    broken = _cf(
        [
            r if not r[0].startswith("CashCash") else (r[0], "-16000000000")
            for r in MSFT_FY2024
        ]
    )
    assert not checks.cf_change_check(broken, {})["ok"]


@pytest.mark.unit
def test_cash_change_uses_the_filers_calc_tree_when_it_has_arcs():
    root = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect"
    groups = {
        (root, "us-gaap/2023", 21): [
            (t, "us-gaap/2023", Decimal(1)) for t, _ in MSFT_FY2024 if t != root
        ]
    }
    c = checks.cf_change_check(_cf(MSFT_FY2024), groups)
    assert c["ok"] and c["detail"]["form"] == "calc_tree"
    # a tree with a child missing from the column falls back to the operand families
    groups2 = {
        (root, "us-gaap/2023", 21): groups[(root, "us-gaap/2023", 21)]
        + [("CashAcquiredFromAcquisition", "us-gaap/2023", Decimal(1))]
    }
    assert (
        checks.cf_change_check(_cf(MSFT_FY2024), groups2)["detail"]["form"]
        == "fallback_totals"
    )


@pytest.mark.unit
def test_cash_change_fallback_adds_discontinued_flows_to_continuing_parts():
    rows = (
        ("NetCashProvidedByUsedInOperatingActivitiesContinuingOperations", "1000"),
        ("NetCashProvidedByUsedInInvestingActivitiesContinuingOperations", "-600"),
        ("NetCashProvidedByUsedInFinancingActivitiesContinuingOperations", "-300"),
        ("CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations", "50"),
        (
            "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
            "-10",
        ),
        (
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
            "140",
        ),
    )
    c = checks.cf_change_check(_cf(rows, dcml=0), {})
    assert c["ok"] and c["detail"]["discontinued"] == [
        "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations"
    ]


@pytest.mark.unit
def test_cash_change_passes_when_only_the_filers_calc_weights_are_wrong():
    # UNH 10-K 0000731766-22-000008: the linkbase weights CFO -1 under the change line; the printed
    # numbers tie, so the column passes and the linkbase defect is recorded, never a quarantine
    root = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect"
    kids = [t for t, _ in MSFT_FY2024 if t != root]
    groups = {
        (root, "us-gaap/2023", 1): [
            (t, "us-gaap/2023", Decimal(-1 if "Operating" in t else 1)) for t in kids
        ]
    }
    c = checks.cf_change_check(_cf(MSFT_FY2024), groups)
    assert (
        c["ok"]
        and c["detail"]["form"] == "fallback_totals"
        and "calc_tree_failed" in c["detail"]
    )
    # numbers that tie neither way still fail
    broken = _cf(
        [
            r if not r[0].startswith("CashCash") else (r[0], "-16000000000")
            for r in MSFT_FY2024
        ]
    )
    assert not checks.cf_change_check(broken, groups)["ok"]


@pytest.mark.unit
def test_tolerance_follows_the_filers_whole_million_rounding_not_a_wrong_decimals_attribute():
    # MCD: decimals -5 on figures that are whole millions; five operands each rounded to 1M can be 2.5M off
    col = {
        (t, "v"): checks.Print(t, "v", Decimal(v), -5, None)
        for t, v in (
            ("NetCashProvidedByUsedInOperatingActivities", "7000000000"),
            ("NetCashProvidedByUsedInInvestingActivities", "-2000000000"),
            ("NetCashProvidedByUsedInFinancingActivities", "-7000000000"),
            ("EffectOfExchangeRateOnCashAndCashEquivalents", "-126000000"),
            ("CashAndCashEquivalentsPeriodIncreaseDecrease", "-2127000000"),
        )
    }
    c = {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}[
        "cf_parts_eq_change"
    ]
    assert c["ok"]
    # a 4M gap is more than five 0.5M roundings: still fails
    col[("CashAndCashEquivalentsPeriodIncreaseDecrease", "v")] = checks.Print(
        "CashAndCashEquivalentsPeriodIncreaseDecrease",
        "v",
        Decimal("-2130000000"),
        -5,
        None,
    )
    assert not {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}[
        "cf_parts_eq_change"
    ]["ok"]
    assert checks.tol_of([checks.Print("a", "v", Decimal(1000), 0, None)]) == Decimal(
        "0.5"
    )


def test_a_column_with_several_copies_of_a_tag_reads_the_face_copy_not_the_last():
    # ADI FY2018 StockholdersEquity: RetainedEarnings iprx 0,1,2 = 5,982,697,000 (face), iprx 3 = 6,313,723,000
    # (includes an adjustment member); the calc check must foot the face copy
    d = date(2018, 11, 3)
    re_ = "RetainedEarningsAccumulatedDeficit"
    rows = [
        (re_, "us-gaap/2018", d, 0, 6313723000, -3, 3),
        (re_, "us-gaap/2018", d, 0, 5982697000, -3, 0),
        (re_, "us-gaap/2018", d, 0, 5982697000, -3, 1),
    ]
    stmt_of = {(re_, "us-gaap/2018"): "BS"}
    flat, by_col = checks.index_values(rows, stmt_of, {(re_, "us-gaap/2018"): 9})
    assert by_col[("BS", d, 0)][(re_, "us-gaap/2018")].value == Decimal(5982697000)
    assert flat[(re_, d, 0)].value == Decimal(5982697000)
