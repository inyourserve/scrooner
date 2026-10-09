from decimal import Decimal as D

from scrooner_pipeline.mapper.dedup_majority_resolver import _group_by_tolerance, _split_reconcile


def test_near_identical_values_group_as_one():
    # Apple total_assets FY2015 real shape: all 5 raw rows within 0.5% of
    # each other -- the actual bug this module fixed live.
    vals = [D("290345000000"), D("290479000000"), D("290479000000"), D("290479000000"), D("290479000000")]
    groups = _group_by_tolerance(vals)
    assert len(groups) == 1
    assert sum(groups.values()) == 5


def test_genuinely_different_values_stay_separate():
    # Abbott Labs FY2012 real shape: 3 raw rows, 3 different values, no majority.
    vals = [D("1360000000"), D("1890000000"), D("8080000000")]
    groups = _group_by_tolerance(vals)
    assert len(groups) == 3
    assert max(groups.values()) == 1


def test_stock_split_shaped_divergence_not_grouped():
    # Nike EPS real shape: a ~2x divergence from a stock split -- must NOT
    # be tolerance-grouped as "the same value," since they're genuinely
    # different numbers on different share bases.
    vals = [D("2.79"), D("1.39")]
    groups = _group_by_tolerance(vals)
    assert len(groups) == 2


def test_two_of_three_majority():
    vals = [D("5.34"), D("5.33"), D("5.33")]
    groups = _group_by_tolerance(vals)
    best_value, best_count = max(groups.items(), key=lambda kv: kv[1])
    assert best_count == 3  # 5.34 is within 0.5% tolerance of 5.33, groups together


def test_split_reconcile_matches_known_ratio():
    # Nike's real FY2015 Q3 basic_eps shape: 2.79 (pre-split) vs 1.39
    # (post-split comparative column), Nike's own real 2015-11-19 split
    # ratio is 2. Must return the SMALLER (current-basis) value.
    assert _split_reconcile([D("2.79"), D("1.39")], [D("2")]) == D("1.39")
    assert _split_reconcile([D("0.92"), D("0.46")], [D("2")]) == D("0.46")


def test_split_reconcile_rejects_genuine_disagreement():
    # Abbott Labs FY2012 operating_income shape: 3 genuinely different
    # values, no split explains any of them -- must stay None.
    assert _split_reconcile([D("1360000000"), D("1890000000"), D("8080000000")], []) is None


def test_split_reconcile_zero_value_never_reconciles():
    # Real crash found live 2026-10-03: a genuine $0 EPS value alongside a
    # nonzero one must not divide by zero, and can never be split-explained.
    assert _split_reconcile([D("0.01"), D("0")], [D("2")]) is None
    assert _split_reconcile([D("0"), D("0")], [D("2")]) is None


def test_split_reconcile_rejects_mixed_sign():
    # A split never flips sign -- a positive vs. negative EPS pair (even
    # matching magnitude) is genuine disagreement, not a split artifact.
    assert _split_reconcile([D("0.02"), D("-0.01")], [D("2")]) is None


def test_split_reconcile_preserves_negative_sign():
    # A real loss-per-share pre/post split: -2.00 (pre-split) vs -1.00
    # (post-split) -- must return the smaller-MAGNITUDE value with its
    # sign intact, not drop the sign or pick the more-negative one.
    assert _split_reconcile([D("-2.00"), D("-1.00")], [D("2")]) == D("-1.00")


def test_split_reconcile_grows_direction_picks_larger_value():
    # shares_outstanding: a 2-for-1 split DOUBLES share count. The larger
    # value (post-split, current) must be returned, not the smaller one.
    assert _split_reconcile([D("1000000"), D("2000000")], [D("2")], "grows") == D("2000000")


def test_split_reconcile_tries_compounded_ratios():
    from scrooner_pipeline.mapper.dedup_majority_resolver import _candidate_ratios

    assert _candidate_ratios([D("2"), D("3")]) == [D("2"), D("3"), D("6")]
    # A period predating two splits (2-for-1 then 3-for-1): raw value is
    # 6x the current-basis value.
    assert _split_reconcile([D("6.0"), D("1.0")], [D("2"), D("3")]) == D("1.0")
