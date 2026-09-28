from decimal import Decimal

from datetime import date

from scrooner_pipeline.mapper.conflict_resolution import MAX_SAFE_RATIO, MAX_SPLIT_RATIO, MIN_SPLIT_RATIO, _restatement_fill_value, _safe_fill_value, _split_safe_fill_value


def test_small_disagreement_picks_highest_fact_id():
    values = [Decimal("100"), Decimal("106")]
    fact_ids = [10, 20]
    assert _safe_fill_value(values, fact_ids) == (Decimal("106"), 20)


def test_small_disagreement_regardless_of_insertion_order():
    values = [Decimal("106"), Decimal("100")]
    fact_ids = [20, 10]
    # highest fact_id (20) wins even though it's first in the list
    assert _safe_fill_value(values, fact_ids) == (Decimal("106"), 20)


def test_disagreement_exactly_at_threshold_is_safe():
    base = Decimal("100")
    values = [base, base * MAX_SAFE_RATIO]
    fact_ids = [1, 2]
    assert _safe_fill_value(values, fact_ids) is not None


def test_disagreement_over_threshold_is_unsafe():
    values = [Decimal("100"), Decimal("117")]
    fact_ids = [1, 2]
    assert _safe_fill_value(values, fact_ids) is None


def test_zero_value_is_never_auto_filled():
    values = [Decimal("0"), Decimal("5")]
    fact_ids = [1, 2]
    assert _safe_fill_value(values, fact_ids) is None


def test_negative_value_is_never_auto_filled():
    values = [Decimal("-100"), Decimal("-95")]
    fact_ids = [1, 2]
    assert _safe_fill_value(values, fact_ids) is None


def test_three_way_conflict_uses_overall_highest_fact_id_not_pairwise():
    # Real shape this must handle: 3 filings, two of which happen to agree
    # closely but aren't the most recent -- the most-recently-filed value
    # wins regardless of which other value it's being compared against.
    values = [Decimal("100"), Decimal("101"), Decimal("108")]
    fact_ids = [5, 7, 30]
    assert _safe_fill_value(values, fact_ids) == (Decimal("108"), 30)


class TestSplitSafeFillValue:
    def test_real_kla_10_for_1_split_prefers_the_restated_value(self):
        # KLA Corp's real FY2025 diluted EPS: $30.37 (original 10-K,
        # pre-split) and $3.04 (the same period's comparative column in
        # the FOLLOWING year's 10-K, filed after a real 10-for-1 split) --
        # the most-recently-filed value is the split-adjusted one.
        values = [Decimal("30.37"), Decimal("3.04")]
        fact_ids = [100, 200]
        assert _split_safe_fill_value(values, fact_ids) == (Decimal("3.04"), 200)

    def test_ordinary_small_disagreement_is_out_of_range_not_a_split(self):
        # A ~6% cross-filing revision is MAX_SAFE_RATIO's own job (the
        # stricter, ordinary-revision path) -- this function must not also
        # claim it, or every routine small disagreement would get treated
        # as a stock split.
        values = [Decimal("100"), Decimal("106")]
        assert _split_safe_fill_value(values, [1, 2]) is None

    def test_ratio_just_above_max_safe_ratio_is_still_not_split_range(self):
        base = Decimal("100")
        values = [base, base * MAX_SAFE_RATIO * Decimal("1.01")]
        assert _split_safe_fill_value(values, [1, 2]) is None
        assert MIN_SPLIT_RATIO > MAX_SAFE_RATIO  # the two ranges must not overlap

    def test_ratio_at_the_edges_of_the_split_band(self):
        base = Decimal("100")
        assert _split_safe_fill_value([base, base * MIN_SPLIT_RATIO], [1, 2]) is not None
        assert _split_safe_fill_value([base, base * MAX_SPLIT_RATIO], [1, 2]) is not None
        assert _split_safe_fill_value([base, base * (MAX_SPLIT_RATIO * Decimal("1.5"))], [1, 2]) is None

    def test_zero_value_is_never_auto_filled(self):
        # A ratio against zero is meaningless, not evidence of anything.
        assert _split_safe_fill_value([Decimal("0"), Decimal("5")], [1, 2]) is None

    def test_negative_values_use_absolute_ratio_since_eps_can_be_a_loss(self):
        # Unlike _safe_fill_value (dollar totals, negative is always
        # suspicious), a per-share loss is a normal, real value -- a split
        # scales a negative EPS by the same factor as a positive one.
        values = [Decimal("-3.0"), Decimal("-0.3")]
        assert _split_safe_fill_value(values, [1, 2]) == (Decimal("-0.3"), 2)



class TestRestatementFillValue:
    """Symbotic Q2 FY2025 net income: -3,925K in the original 10-Q
    (2025-05-07), -1,804K restated in the next year's 10-Q (2026-05-06)."""

    def test_latest_filing_wins_for_a_restatement(self):
        values = [Decimal("-3925000"), Decimal("-1804000")]
        dates = [date(2025, 5, 7), date(2026, 5, 6)]
        assert _restatement_fill_value(values, [10, 20], dates) == (Decimal("-1804000"), 20)

    def test_latest_is_by_filing_date_not_fact_id(self):
        values = [Decimal("-1804000"), Decimal("-3925000")]
        dates = [date(2026, 5, 6), date(2025, 5, 7)]
        assert _restatement_fill_value(values, [10, 20], dates) == (Decimal("-1804000"), 10)

    def test_disagreeing_facts_on_the_latest_date_refuse(self):
        values = [Decimal("100"), Decimal("200"), Decimal("300")]
        dates = [date(2025, 1, 1), date(2026, 1, 1), date(2026, 1, 1)]
        assert _restatement_fill_value(values, [1, 2, 3], dates) is None

    def test_same_day_versions_are_not_a_restatement(self):
        values = [Decimal("100"), Decimal("200")]
        dates = [date(2026, 1, 1), date(2026, 1, 1)]
        assert _restatement_fill_value(values, [1, 2], dates) is None

    def test_scale_error_spread_refuses(self):
        values = [Decimal("1000"), Decimal("1000000")]
        dates = [date(2025, 1, 1), date(2026, 1, 1)]
        assert _restatement_fill_value(values, [1, 2], dates) is None

    def test_zero_refuses(self):
        values = [Decimal("0"), Decimal("500")]
        dates = [date(2025, 1, 1), date(2026, 1, 1)]
        assert _restatement_fill_value(values, [1, 2], dates) is None

    def test_sign_flip_within_bounds_uses_latest(self):
        values = [Decimal("-400"), Decimal("300")]
        dates = [date(2025, 1, 1), date(2026, 1, 1)]
        assert _restatement_fill_value(values, [1, 2], dates) == (Decimal("300"), 2)
