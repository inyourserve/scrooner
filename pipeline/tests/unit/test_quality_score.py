from decimal import Decimal

import pytest

from scrooner_pipeline.mapper.quality_score import _derive_missing_gross_profit


@pytest.mark.unit
def test_derives_gross_profit_from_revenue_minus_cost_of_revenue_when_missing():
    fy_facts = {
        "revenue": {2024: Decimal("1000"), 2025: Decimal("1200")},
        "cost_of_revenue": {2024: Decimal("600"), 2025: Decimal("700")},
        "gross_profit": {},
    }
    _derive_missing_gross_profit(fy_facts)
    assert fy_facts["gross_profit"] == {2024: Decimal("400"), 2025: Decimal("500")}


@pytest.mark.unit
def test_never_overrides_a_real_reported_gross_profit_value():
    fy_facts = {
        "revenue": {2024: Decimal("1000")},
        "cost_of_revenue": {2024: Decimal("600")},
        "gross_profit": {2024: Decimal("999")},  # the real reported tag, deliberately different from 1000-600
    }
    _derive_missing_gross_profit(fy_facts)
    assert fy_facts["gross_profit"] == {2024: Decimal("999")}


@pytest.mark.unit
def test_no_derivation_when_cost_of_revenue_missing_for_that_year():
    fy_facts = {
        "revenue": {2024: Decimal("1000")},
        "cost_of_revenue": {},
        "gross_profit": {},
    }
    _derive_missing_gross_profit(fy_facts)
    assert fy_facts["gross_profit"] == {}


@pytest.mark.unit
def test_handles_missing_cost_of_revenue_key_entirely():
    # A company with zero core.fact rows for cost_of_revenue ever --
    # _load_fy_facts still returns an empty dict for it (never a
    # missing key), but this test guards the derivation function
    # itself against a caller that didn't pre-populate the key.
    fy_facts = {"revenue": {2024: Decimal("1000")}, "gross_profit": {}}
    _derive_missing_gross_profit(fy_facts)
    assert fy_facts["gross_profit"] == {}


@pytest.mark.unit
def test_partial_years_only_derives_where_both_inputs_exist():
    fy_facts = {
        "revenue": {2023: Decimal("900"), 2024: Decimal("1000")},
        "cost_of_revenue": {2024: Decimal("600")},  # 2023 missing
        "gross_profit": {},
    }
    _derive_missing_gross_profit(fy_facts)
    assert fy_facts["gross_profit"] == {2024: Decimal("400")}
