from decimal import Decimal

from scrooner_pipeline.mapper.conflict_resolution import MAX_SAFE_RATIO, _safe_fill_value


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
