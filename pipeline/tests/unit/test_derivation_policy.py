"""common/derivation_policy.py: Item 302(a) cutoff (NA-1 state split) and the
NA-3 FY dividends-per-share sum test (rulings 2026-10-22)."""

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.common import derivation_policy as dp


@pytest.mark.unit
@pytest.mark.parametrize(
    ("fy_end", "required"),
    [
        (date(2020, 12, 31), True),  # 10-K had to file Q4 quarterly data
        (date(2021, 8, 8), True),
        (date(2021, 8, 9), False),  # compliance date of Release 33-10890
        (date(2025, 9, 27), False),  # AAPL FY25
        (None, False),
    ],
)
def test_item_302a_cutoff(fy_end, required):
    assert dp.q4_per_share_filed_separately_required(fy_end) is required
    expected = (
        dp.PER_SHARE_NOT_CAPTURED_REASON
        if required
        else dp.PER_SHARE_NOT_DERIVED_REASON
    )
    assert dp.q4_per_share_reason(fy_end) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("case", "fy", "quarters", "is_total"),
    [
        # V FY2025: quarterly 0.59 tagged on the 12-month context (0001403161-25-000089 R8).
        # The old "at least each quarter" test passes it; the sum test does not.
        ("V_rate_on_fy_context", "0.59", ["0.59", "0.59", "0.59"], False),
        # LEA FY2025: 0.77 on the FY context (0000842162-26-000011).
        ("LEA_rate_on_fy_context", "0.77", ["0.77", "0.77", "0.77"], False),
        ("real_annual_total", "2.36", ["0.59", "0.59", "0.59"], True),
        ("rounding_tolerated", "1.769", ["0.59", "0.59", "0.59"], True),
        ("no_filed_quarters", "0.59", [], True),
    ],
    ids=lambda v: v if isinstance(v, str) and v[:1].isalpha() else "",
)
def test_fy_dps_sum_guard(case, fy, quarters, is_total):
    assert (
        dp.fy_dps_is_annual_total(Decimal(fy), [Decimal(q) for q in quarters])
        is is_total
    )
    # The old per-quarter test would wrongly accept the V/LEA rows.
    if not is_total:
        assert all(Decimal(fy) >= Decimal(q) for q in quarters)


@pytest.mark.unit
def test_periodic_form_helper():
    assert dp.is_periodic_form("10-K") and dp.is_periodic_form(" 10-q/a ")
    assert not dp.is_periodic_form("DEF 14A") and not dp.is_periodic_form("8-K")
    assert not dp.is_periodic_form(None)
