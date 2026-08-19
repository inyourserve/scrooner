from decimal import Decimal

import pytest

from scrooner_pipeline.mapper.ttm import _growth_value, _trailing_quarters, _ttm_sum


@pytest.mark.unit
@pytest.mark.parametrize("year,quarter,expected", [
    (2025, "Q4", [(2025, "Q1"), (2025, "Q2"), (2025, "Q3"), (2025, "Q4")]),
    (2025, "Q1", [(2024, "Q2"), (2024, "Q3"), (2024, "Q4"), (2025, "Q1")]),
])
def test_trailing_quarter_window_is_fiscal_not_calendar(year, quarter, expected):
    assert _trailing_quarters(year, quarter) == expected


@pytest.mark.unit
def test_ttm_requires_all_four_quarters_and_preserves_lineage():
    complete = {
        (2025, "Q1"): (Decimal("1"), [1], None, None),
        (2025, "Q2"): (Decimal("2"), [2], None, None),
        (2025, "Q3"): (Decimal("3"), [3], None, None),
        (2025, "Q4"): (Decimal("4"), [4], None, None),
    }
    assert _ttm_sum(complete, 2025, "Q4") == (Decimal("10"), [1, 2, 3, 4])

    incomplete = dict(complete)
    incomplete.pop((2025, "Q2"))
    assert _ttm_sum(incomplete, 2025, "Q4") == (None, [])


@pytest.mark.unit
def test_growth_yoy_cagr_and_invalid_bases():
    assert _growth_value(Decimal("120"), Decimal("100"), 1) == (Decimal("0.2"), None)
    cagr, reason = _growth_value(Decimal("1331"), Decimal("1000"), 3)
    assert cagr.quantize(Decimal("0.0000001")) == Decimal("0.1000000")
    assert reason is None
    assert _growth_value(Decimal("10"), Decimal("0"), 1) == (None, "zero_base_value")
    assert _growth_value(Decimal("10"), Decimal("-10"), 3) == (None, "negative_ratio_undefined_cagr")

