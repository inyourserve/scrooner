"""Total debt from the balance-sheet carrying lines (r8). Filing-checked targets:
AAPL Q3 FY26 84,344 (10-Q 0000320193-26-000020 R38 / data-team/35), GOOG FY2025 48,543 (0001652044-26-000018 R67),
AMZN FY2025 68,851 and Q2 2026 132,549 (0001018724-26-000004 R69), CVX FY2016 (0000093410-17-000013 R5: 46,033,
undecidable from tags), DPZ FY2024 4,975,338K (0000950170-25-025223 R2), PFE FY2020 39,836 (0000078003-21-000038 R4).
Values in $M."""

from __future__ import annotations

from decimal import Decimal

import pytest

from scrooner_pipeline.common import debt_carrying as dc
from scrooner_pipeline.mapper import concept_fallback as cf

M = Decimal(1_000_000)


def V(**tags):
    return {t: Decimal(str(v)) * M for t, v in tags.items()}


def F(**tags):
    return {t: (Decimal(str(v)) * M, i) for i, (t, v) in enumerate(tags.items(), 1)}


AAPL = dict(
    CommercialPaper=1997,
    LongTermDebt=82300,
    LongTermDebtCurrent=11007,
    LongTermDebtNoncurrent=71340,
)
GOOG = dict(
    CommercialPaper=0,
    LongTermDebt=49085,
    LongTermDebtCurrent=1996,
    LongTermDebtNoncurrent=46547,
    DebtInstrumentCarryingAmount=49085,
)
AMZN_FY25 = dict(
    LongTermDebt=68836,
    ShortTermBorrowings=455,
    LongTermDebtCurrent=2748,
    LongTermDebtNoncurrent=65648,
)
AMZN_Q2 = dict(
    LongTermDebt=132995,
    ShortTermBorrowings=325,
    LongTermDebtCurrent=3330,
    LongTermDebtNoncurrent=128894,
)
CVX = dict(CommercialPaper=10410, LongTermDebt=32490, OtherShortTermBorrowings=0, ShortTermBorrowings=10840,
           LongTermDebtCurrent=6253, LongTermDebtNoncurrent=35193, DebtCurrent=19840, ShortTermBankLoansAndNotesPayable=50)  # fmt: skip
DPZ = dict(LongTermDebt="14.7", LongTermDebtCurrent="0.1", LongTermDebtAndCapitalLeaseObligations="3825.659",
           LongTermDebtAndCapitalLeaseObligationsCurrent="1149.679", DebtAndCapitalLeaseObligations="4975.338")  # fmt: skip
PFE = dict(CommercialPaper=556, LongTermDebt=4000, OtherShortTermBorrowings=145, LongTermDebtCurrent=2002,
           LongTermDebtNoncurrent=37133, DebtCurrent=2703)  # fmt: skip
GUARDS = cf.ALL_DEBT_GUARDS


@pytest.mark.parametrize(
    ("name", "tags", "want"),
    [
        ("AAPL Q3 FY26", AAPL, "84344"),
        ("GOOG FY2025", GOOG, "48543"),
        ("AMZN FY2025", AMZN_FY25, "68851"),
        ("AMZN Q2 2026", AMZN_Q2, "132549"),
    ],
)
def test_filing_checked_targets_come_out_of_the_carrying_lines(name, tags, want):
    c = dc.carrying_lines(V(**tags))
    assert isinstance(c, dc.Carrying) and c.value == Decimal(want) * M, name
    d = cf.evaluate_total_debt(F(**tags), GUARDS)
    assert d.value == Decimal(want) * M and cf.GUARD_CARRYING in d.guards_fired


def test_the_old_path_gave_the_wrong_numbers_the_pilot_found():
    assert (
        cf.evaluate_total_debt(F(**AAPL), cf.GUARDS_BEFORE_CARRYING).value
        == Decimal(84297) * M
    )
    assert (
        cf.evaluate_total_debt(F(**AMZN_Q2), cf.GUARDS_BEFORE_CARRYING).value
        == Decimal(133320) * M
    )


def test_pfe_and_dpz_targets():
    assert cf.evaluate_total_debt(F(**PFE), GUARDS).value == Decimal(39836) * M
    assert cf.evaluate_total_debt(F(**DPZ), GUARDS).value == Decimal(
        "4975338000"
    )  # lease family pair


def test_cvx_2016_is_held_because_the_tags_cannot_show_the_printed_46033():
    c = dc.carrying_lines(V(**CVX))
    assert c == dc.Hold("current_block_unexplained")
    d = cf.evaluate_total_debt(F(**CVX), GUARDS)
    assert d.value is None and d.reason == cf.REASON_UNDECIDABLE_FALLBACK


def test_aapl_fy2015_has_no_authoritative_noncurrent_line_so_the_carrying_path_does_not_apply():
    tags = dict(
        CommercialPaper=8499,
        LongTermDebtCurrent=2500,
        DebtInstrumentCarryingAmount=55701,
    )
    assert dc.carrying_lines(V(**tags)) is None
    d = cf.evaluate_total_debt(F(**tags), GUARDS)
    assert (
        d.value is None and d.reason == cf.REASON_PARTIAL_COMPONENT
    )  # r7 keeps blanking the partial total


def test_dedupe_when_short_term_equals_current_ltd():
    c = dc.carrying_lines(
        V(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, ShortTermBorrowings=10)
    )
    assert c.value == Decimal(110) * M


def test_lease_inclusive_noncurrent_pairs_only_with_the_lease_current_line():
    assert (
        dc.carrying_lines(
            V(LongTermDebtAndCapitalLeaseObligations=100, LongTermDebtCurrent=10)
        )
        is None
    )


def test_disagreement_with_long_term_debt_over_10_percent_disables_the_mechanism():
    assert (
        dc.carrying_lines(
            V(LongTermDebt=1000, LongTermDebtNoncurrent=100, LongTermDebtCurrent=10)
        )
        is None
    )
    assert (
        dc.carrying_lines(
            V(LongTermDebt=1000, LongTermDebtNoncurrent=900, LongTermDebtCurrent=95)
        ).value
        == Decimal(995) * M
    )


def test_no_current_line_is_not_applicable():
    assert dc.carrying_lines(V(LongTermDebtNoncurrent=100, LongTermDebt=105)) is None


def test_flag_off_keeps_the_legacy_path_byte_identical():
    for tags in (AAPL, GOOG, AMZN_FY25, AMZN_Q2, CVX, PFE, DPZ):
        f = F(**tags)
        assert (
            cf.evaluate_total_debt(f, frozenset()).value
            == (cf._compose_total_debt(f) or (None,))[0]
        )
    assert cf.debt_guards_active({}) == frozenset()
    assert cf.GUARD_CARRYING in cf.debt_guards_active(
        {"SCROONER_RULES_ENABLED": cf.RULE_DEBT}
    )


def test_dpz_comes_from_the_lease_family_pair_directly():
    tags = {
        k: v for k, v in DPZ.items() if k != "LongTermDebt"
    }  # r1 containment removes it first
    c = dc.carrying_lines(V(**tags))
    assert c.value == Decimal("4975338000") and c.tags == (
        "LongTermDebtAndCapitalLeaseObligations",
        "LongTermDebtAndCapitalLeaseObligationsCurrent",
    )


def test_wmt_company_stated_total_within_10_percent_is_overridden_by_the_balance_sheet_lines():
    # WMT 2024-01-31: stated total 39,579 = noncurrent 36,132 + current 3,447; the balance sheet also
    # prints short-term borrowings 878, so the carrying total is 40,457 (2.2% above the stated figure).
    wmt = V(
        LongTermDebt=39579, ShortTermBorrowings=878, LongTermDebtCurrent=3447,
        LongTermDebtNoncurrent=36132, DebtLongtermAndShorttermCombinedAmount=39579,
    )  # fmt: skip
    assert dc.carrying_lines(wmt).value == Decimal(40457) * M


def test_company_stated_total_far_from_the_carrying_lines_disables_the_mechanism():
    odd = V(
        LongTermDebtNoncurrent=100,
        LongTermDebtCurrent=10,
        DebtLongtermAndShorttermCombinedAmount=200,
    )
    assert dc.carrying_lines(odd) is None


def test_debt_current_above_the_listed_parts_is_the_printed_line_not_a_contradiction():
    # TSLA-shaped: DebtCurrent holds unlisted components (non-recourse, leases), so it exceeds the listed parts
    c = dc.carrying_lines(
        V(LongTermDebtNoncurrent=100, LongTermDebtCurrent=10, DebtCurrent=40)
    )
    assert c.value == Decimal(140) * M and c.path == "carrying_noncurrent+debt_current"


def test_debt_current_below_overlapping_parts_with_no_matching_subset_is_held():
    assert dc.carrying_lines(
        V(
            LongTermDebtNoncurrent=100,
            ShortTermBorrowings=60,
            LongTermDebtCurrent=30,
            DebtCurrent=70,
        )
    ) == dc.Hold("current_block_unexplained")
