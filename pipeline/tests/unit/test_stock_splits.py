from decimal import Decimal

import pytest

from scrooner_pipeline.corporate_actions.stock_splits import _classify


@pytest.mark.unit
class TestClassify:
    def test_real_forward_split_ratios_pass_unscaled(self):
        for value in ("2", "3", "4", "5", "10", "20", "50"):
            assert _classify(Decimal(value)) == (Decimal(value), 1)

    def test_real_reverse_split_ratios_pass_unscaled(self):
        assert _classify(Decimal("0.1")) == (Decimal("0.1"), 1)
        assert _classify(Decimal("0.25")) == (Decimal("0.25"), 1)

    def test_kla_real_case_needs_1000x_scale_correction(self):
        # KLA Corp's own real FY2025 10-K: StockholdersEquityNoteStockSplit
        # ConversionRatio1 = 10000, a real 10-for-1 split, confirmed
        # independently from its own conflicting comparative EPS values.
        assert _classify(Decimal("10000")) == (Decimal("10"), 1000)

    def test_zero_and_one_are_non_events_not_splits(self):
        assert _classify(Decimal("0")) is None
        assert _classify(Decimal("1")) is None

    def test_negative_value_rejected(self):
        assert _classify(Decimal("-75")) is None

    def test_wildly_implausible_value_rejected_even_after_every_scale(self):
        # A real value found live in the population (109,673,709) -- not
        # a stock split under any scale correction, almost certainly a
        # different real XBRL use of the same tag name (a convertible-
        # security conversion ratio).
        assert _classify(Decimal("109673709")) is None

    def test_unscaled_value_preferred_over_a_scaled_reading_when_both_would_be_plausible(self):
        # 150 is already plausible unscaled (<=200) -- must not also be
        # accepted as 150/1000=0.15 under a different scale; the first
        # matching scale in try-order (1, then 1000, then 10000) wins.
        assert _classify(Decimal("150")) == (Decimal("150"), 1)
