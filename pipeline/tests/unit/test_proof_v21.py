"""Proof v21: the shared filer-calc lift (ISRG, NEE), the non-interest band (STX), pre-filing cash (CRWD), note
component sums without a calc parent (ISRG D&A). Each test fails without its rule (mutation-checked)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.common.filer_calc_lift import (
    CheckRow,
    lift_route,
    residual_line_tie,
)
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue
from scrooner_pipeline.proof.prove import (
    DISAGREE,
    NOT_PRESENTED,
    PROVEN,
    Proof,
    Shown,
    first_balance_sheet_date,
    non_interest_band,
    prove_cell,
)

D = Decimal
CHANGE = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect"
CFO = "NetCashProvidedByUsedInOperatingActivities"


def _isrg_rows(parts_ok: bool) -> list[CheckRow]:
    return [
        CheckRow(
            "CF",
            f"calc:{CHANGE}:23",
            False,
            D("273200000"),
            D("-2923200000"),
            D("250000"),
            (CFO, "NetCashProvidedByUsedInInvestingActivities"),
        ),
        CheckRow(
            "CF",
            "cf_parts_eq_change",
            parts_ok,
            D("273200000"),
            D("273200000"),
            D("250000"),
        ),
    ]


def test_isrg_net_change_tree_lifted_by_cf_parts_eq_change():
    rows = _isrg_rows(True)
    got = lift_route(rows, rows[0], "cfo", (CFO,))
    assert got is not None and got["route"] == "cf_parts_eq_change"
    # the printed totals do not tie the change either: stays quarantined
    rows = _isrg_rows(False)
    assert lift_route(rows, rows[0], "cfo", (CFO,)) is None


def _nee_opex():
    failed = CheckRow(
        "IS",
        "calc:OperatingExpenses:12",
        False,
        D("13234000000"),
        D("12881000000"),
        D("3500000"),
    )
    children = [("Fuel", False), ("Gain", True)]
    vals = {"Fuel": D("13587000000"), "Gain": D("353000000")}
    return failed, children, vals


def test_nee_residual_equals_a_printed_child_the_parent_excludes():
    failed, children, vals = _nee_opex()
    got = lift_route(
        [failed],
        failed,
        "operating_expenses",
        ("OperatingExpenses",),
        children=children,
        value_of=vals.get,
        face_tags=[],
    )
    assert got is not None and got["route"] == "printed_residual_child_excluded"
    assert got["printed_line"]["line"] == "Gain"
    # the printed line does not equal the residual: stays quarantined
    vals["Gain"] = D("300000000")
    assert (
        lift_route(
            [failed],
            failed,
            "operating_expenses",
            ("OperatingExpenses",),
            children=children,
            value_of=vals.get,
            face_tags=[],
        )
        is None
    )


def test_nee_residual_equals_a_face_line_the_group_omits():
    failed = CheckRow(
        "BS",
        "calc:LiabilitiesAndStockholdersEquity:15",
        False,
        D("190144000000"),
        D("189743000000"),
        D("1500000"),
    )
    kids = [("Liabilities", False), ("EquityInclNCI", False)]
    vals = {"RedeemableNoncontrollingInterest": D("401000000"), "Other": D("999")}
    got = residual_line_tie(failed, kids, vals.get, ["Other", "RedeemableNoncontrollingInterest"])
    assert got is not None and got["rule"] == "printed_residual_line_omitted"
    assert got["line"] == "RedeemableNoncontrollingInterest"
    # a line smaller than twice the tolerance never explains a residual (rounding cannot be the evidence)
    tiny = CheckRow("BS", "calc:X:1", False, D("11"), D("10"), D("1"))
    assert residual_line_tie(tiny, kids, {"T": D("1")}.get, ["T"]) is None


def _structure(num: dict, calc: dict | None = None) -> FilingStructure:
    st = FilingStructure("A-1", "1", "10-K", date(2026, 8, 1), date(2026, 7, 3))
    for (tag, dd, q), (v, dcml) in num.items():
        st.num[(tag, dd, q)].append(NumValue(tag, "us-gaap/2025", dd, q, "USD", D(v), dcml))
    for parent, kids in (calc or {}).items():
        st.calc_children[parent] = kids
    return st


def test_stx_non_interest_band_excludes_the_interest_lines():
    dd = date(2026, 6, 30)
    st = _structure(
        {
            ("NonoperatingIncomeExpense", dd, 4): ("-404000000", -6),
            ("InvestmentIncomeInterest", dd, 4): ("30000000", -6),
            ("InterestExpenseNonoperating", dd, 4): ("284000000", -6),
            ("OtherNonoperatingIncomeExpense", dd, 4): ("1000000", -6),
            ("GainsLossesOnExtinguishmentOfDebt", dd, 4): ("-151000000", -6),
        },
        {
            "NonoperatingIncomeExpense": [
                ("InvestmentIncomeInterest", False),
                ("InterestExpenseNonoperating", True),
                ("OtherNonoperatingIncomeExpense", False),
                ("GainsLossesOnExtinguishmentOfDebt", False),
            ]
        },
    )
    band = non_interest_band(st, "NonoperatingIncomeExpense", dd, 4, "money")
    assert band is not None and band[0] == D("-150000000")
    # a child with no value in the column: never a guessed zero
    del st.num[("OtherNonoperatingIncomeExpense", dd, 4)]
    assert non_interest_band(st, "NonoperatingIncomeExpense", dd, 4, "money") is None


def test_crwd_pre_filing_cash_is_not_demanded():
    # the shown filing's balance sheet starts 2019-01-31; the cell's date is before it
    st = _structure({("Assets", date(2019, 1, 31), 0): ("1", -3), ("Assets", date(2019, 4, 30), 0): ("1", -3)})
    assert first_balance_sheet_date(st) == date(2019, 1, 31)
    assert first_balance_sheet_date(_structure({})) is None


def test_note_parts_need_no_single_calc_parent():
    from scrooner_pipeline.mapper.company_tag_map import MapRow, _check_components, Fact

    def row(tag, stmt):
        return MapRow("us-gaap", tag, stmt, "component", 1, 2, 1, date(2015, 1, 1), None)

    def fact(i):
        return Fact(D("1"), i, date(2019, 12, 31), False, 7, "A-1")

    arcs = {"A-1": {("Other", "X")}}
    note = [(row("Depreciation", "NOTE"), fact(1)), (row("AmortizationOfIntangibleAssets", "NOTE"), fact(2))]
    assert _check_components(note, arcs) is None
    face = [(row("Depreciation", "IS"), fact(1)), (row("AmortizationOfIntangibleAssets", "IS"), fact(2))]
    assert _check_components(face, arcs) == "components_without_single_calc_parent"
    # parts from two filings stay held
    other = Fact(D("1"), 3, date(2019, 12, 31), False, 8, "A-2")
    mixed = [note[0], (note[1][0], other)]
    assert _check_components(mixed, arcs) == "components_from_different_filings"
