from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.sanity.timeseries_check import SEVERITY_OK, SEVERITY_OUTLIER, SEVERITY_SIGN_VIOLATION, check_yoy


def _check(current, prior, min_ratio=0.1, max_ratio=10.0, floor=1_000_000, never_negative=False):
    return check_yoy(
        1, 1, 1, date(2026, 3, 31), 2026, "Q1",
        Decimal(current), Decimal(prior) if prior is not None else None,
        min_ratio, max_ratio, floor, never_negative,
    )


@pytest.mark.unit
class TestCheckYoy:
    def test_ok_within_normal_growth(self):
        row = _check(current=110_000_000, prior=100_000_000)
        assert row["severity"] == SEVERITY_OK

    def test_outlier_when_ratio_exceeds_bound(self):
        # 100x growth on a material base -- way outside a 10x max_ratio.
        row = _check(current=10_000_000_000, prior=100_000_000)
        assert row["severity"] == SEVERITY_OUTLIER

    def test_outlier_when_collapsed_below_min_ratio(self):
        row = _check(current=1_000_000, prior=100_000_000, min_ratio=0.1)
        assert row["severity"] == SEVERITY_OUTLIER

    def test_sign_violation_for_never_negative_concept(self):
        # revenue/total_assets/cash should never be negative, regardless
        # of any history -- flagged even with no prior period at all.
        row = _check(current=-5_000_000, prior=None, never_negative=True)
        assert row["severity"] == SEVERITY_SIGN_VIOLATION

    def test_ok_when_no_prior_period_to_compare(self):
        row = _check(current=100_000_000, prior=None)
        assert row["severity"] == SEVERITY_OK
        assert row["yoy_ratio"] is None

    def test_ok_when_prior_base_below_materiality_floor(self):
        # A tiny prior base makes any ratio meaningless -- not flaggable.
        row = _check(current=50_000_000, prior=500, floor=1_000_000)
        assert row["severity"] == SEVERITY_OK

    def test_sign_flip_within_normal_bound_is_ok(self):
        # A real, legitimate turnaround (loss to modest profit) for a
        # concept that can be negative -- not an outlier on its own.
        row = _check(current=5_000_000, prior=-2_000_000, never_negative=False, max_ratio=10.0)
        assert row["severity"] == SEVERITY_OK

    def test_extreme_sign_flip_is_flagged(self):
        # A tiny loss flipping into an enormous profit -- needs a much
        # higher bar than ordinary same-sign growth, but this clears it.
        row = _check(current=500_000_000, prior=-1_000_000, never_negative=False, max_ratio=10.0)
        assert row["severity"] == SEVERITY_OUTLIER

    def test_never_negative_concept_flagged_even_with_normal_looking_history(self):
        row = _check(current=-1_000_000, prior=100_000_000, never_negative=True)
        assert row["severity"] == SEVERITY_SIGN_VIOLATION
