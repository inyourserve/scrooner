from decimal import Decimal

from datetime import date

from scrooner_pipeline.mapper.conflict_resolution import MAX_SAFE_RATIO, MAX_SPLIT_RATIO, MIN_SPLIT_RATIO, _restatement_fill_value, _safe_fill_value, _split_safe_fill_value
from scrooner_pipeline.mapper import conflict_resolution
from scrooner_pipeline.mapper.conflict_resolution import STALE_FILL_GUARD_CLASS, StaleFillCandidate, classify_stale_fill


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


def _cand(stored, primary, stored_tags, primary_tags, stored_date, primary_date,
          primary_forms=("10-K",), derived=False, concept="revenue"):
    return StaleFillCandidate(
        concept=concept, row_id=1, company_id=1, period_id=1,
        stored=Decimal(stored), primary=Decimal(primary),
        stored_tags=frozenset("us-gaap:" + t for t in stored_tags),
        primary_tags=frozenset("us-gaap:" + t for t in primary_tags),
        primary_any_derived=derived, primary_forms=frozenset(primary_forms),
        stored_filing_date=stored_date, primary_filing_date=primary_date,
    )


class TestStaleFillGuards:
    """Fixtures are rows from data-team/28-VERIFIER-STALE-FILL-PROPOSALS-
    2026-10-18.md (values, tags, forms and filing dates from the Verifier's
    metadata; verdicts FILING-CHECKED there). Row numbers are that file's."""

    # --- (a) same source tag ---
    def test_ande_asc606_subset_tag_is_not_a_refresh(self):
        # row 74: stored Revenues 11,257,548K is the face total; the primary
        # RevenueFromContract... 1,403,382K is the ASC 606-scope subset.
        c = _cand("11257548000", "1403382000", ["Revenues"],
                  ["RevenueFromContractWithCustomerExcludingAssessedTax"],
                  date(2026, 2, 18), date(2026, 2, 18))
        assert classify_stale_fill(c) == ("skip", "different_tag")

    def test_xpl_continuing_ops_subtotal_is_not_a_refresh(self):
        # row 53: total investing (996)K vs continuing-ops subtotal 592K.
        c = _cand("-996000", "592000", ["NetCashProvidedByUsedInInvestingActivities"],
                  ["NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"],
                  date(2015, 11, 12), date(2015, 11, 12), ("10-Q",))
        assert classify_stale_fill(c) == ("skip", "different_tag")

    def test_qwtr_opposite_signed_alternative_tag_is_not_a_refresh(self):
        # row 20: NetIncomeLoss (295,072) vs ...AvailableToCommonStockholdersBasic +295,072.
        c = _cand("-295072", "295072", ["NetIncomeLoss"],
                  ["NetIncomeLossAvailableToCommonStockholdersBasic"],
                  date(2023, 7, 20), date(2023, 7, 20), ("10-Q",))
        assert classify_stale_fill(c) == ("skip", "different_tag")

    def test_viav_arithmetic_stored_row_is_a_different_tag_set(self):
        # row 8 (bucket C): stored = revenue - opex - cost over 3 tags. That
        # class needs its own reviewed path, not this function.
        c = _cand("7700000", "-6400000", ["SalesRevenueNet", "OperatingExpenses", "CostOfRevenue"],
                  ["OperatingIncomeLoss"], date(2013, 8, 23), date(2013, 8, 23),
                  concept="operating_income")
        assert classify_stale_fill(c) == ("skip", "different_tag")

    def test_tags_compare_taxonomy_too(self):
        c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1), date(2021, 1, 1))
        c = StaleFillCandidate(**{**c.__dict__, "primary_tags": frozenset({"abc:Revenues"})})
        assert classify_stale_fill(c) == ("skip", "different_tag")

    def test_missing_source_facts_are_skipped(self):
        c = _cand("100", "200", [], ["Revenues"], date(2020, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("skip", "stored_source_facts_missing")
        c = _cand("100", "200", ["Revenues"], [], date(2020, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("skip", "primary_source_facts_missing")

    # --- (b) primary must be filed, not derived ---
    def test_agnt_derived_negative_dps_is_not_a_refresh(self):
        # row 64: same tag, stored 0.05 (correct per R6), primary -0.090 derived.
        c = _cand("0.05", "-0.090", ["CommonStockDividendsPerShareCashPaid"],
                  ["CommonStockDividendsPerShareCashPaid"],
                  date(2024, 2, 22), date(2026, 2, 24), derived=True,
                  concept="dividends_per_share")
        assert classify_stale_fill(c) == ("skip", "primary_derived")

    def test_lea_derived_dps_is_not_a_refresh(self):
        # row 66: stored 0.75 correct; primary -1.50 derived, same tag.
        c = _cand("0.75", "-1.50", ["CommonStockDividendsPerShareDeclared"],
                  ["CommonStockDividendsPerShareDeclared"],
                  date(2020, 2, 4), date(2021, 2, 10), derived=True)
        assert classify_stale_fill(c) == ("skip", "primary_derived")

    def test_unknown_derivation_flag_is_treated_as_derived(self):
        c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), derived=None)
        assert classify_stale_fill(c) == ("skip", "primary_derived")

    # --- (c) periodic forms only ---
    def test_aemd_def14a_rounded_figure_is_not_a_refresh(self):
        # row 77: 10-K net loss (13,388,089) vs DEF 14A pay-vs-performance (13,400,000).
        c = _cand("-13388089", "-13400000", ["NetIncomeLoss"], ["NetIncomeLoss"],
                  date(2025, 6, 26), date(2026, 9, 1), ("DEF 14A",), concept="net_income")
        assert classify_stale_fill(c) == ("skip", "primary_non_periodic_form")

    def test_bkd_8k_recast_is_not_a_refresh(self):
        # row 76: 10-K 2,280,535K vs 8-K recast 2,278,920K, same tag.
        c = _cand("2280535000", "2278920000", ["Revenues"], ["Revenues"],
                  date(2013, 2, 20), date(2013, 12, 11), ("8-K",))
        assert classify_stale_fill(c) == ("skip", "primary_non_periodic_form")

    def test_mixed_periodic_and_8k_primary_sources_are_rejected(self):
        c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K", "8-K"))
        assert classify_stale_fill(c) == ("skip", "primary_non_periodic_form")

    def test_every_allowed_periodic_form_passes(self):
        for form in ("10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-KT/A"):
            c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                      date(2021, 1, 1), (form,))
            assert classify_stale_fill(c)[0] == "propose", form
        for form in ("20-F", "40-F", "6-K", "S-1"):
            c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                      date(2021, 1, 1), (form,))
            assert classify_stale_fill(c) == ("skip", "primary_non_periodic_form"), form

    # --- dates (kept from the first version, tightened) ---
    def test_older_authoritative_never_overwrites_a_newer_restated_fill(self):
        c = _cand("4734", "6981", ["Revenues"], ["Revenues"], date(2021, 1, 1), date(2020, 1, 1))
        assert classify_stale_fill(c) == ("skip", "authoritative_older_than_stored")

    def test_same_filing_date_goes_to_review(self):
        c = _cand("100", "120", ["Revenues"], ["Revenues"], date(2021, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("needs_review", "same_filing_date")

    def test_unknown_dates_go_to_review(self):
        c = _cand("100", "120", ["Revenues"], ["Revenues"], None, date(2021, 1, 1))
        assert classify_stale_fill(c) == ("needs_review", "filing_date_unknown")

    # --- (d) sign flips and zeros go to review ---
    def test_lgnd_sign_flip_goes_to_review_even_though_same_tag_later(self):
        # row 17: IncomeTaxExpenseBenefit (35)K -> 66K, 10-K/A -> later 10-K/A.
        c = _cand("-35000", "66000", ["IncomeTaxExpenseBenefit"], ["IncomeTaxExpenseBenefit"],
                  date(2014, 12, 1), date(2014, 12, 12), ("10-K/A",))
        assert classify_stale_fill(c) == ("needs_review", "sign_flip")

    def test_lgnd_zero_goes_to_review(self):
        # row 59: PaymentsForRepurchaseOfCommonStock 55K -> 0.
        c = _cand("55000", "0", ["PaymentsForRepurchaseOfCommonStock"],
                  ["PaymentsForRepurchaseOfCommonStock"],
                  date(2014, 12, 1), date(2014, 12, 12), ("10-K/A",))
        assert classify_stale_fill(c) == ("needs_review", "zero_value")

    def test_stored_zero_goes_to_review(self):
        c = _cand("0", "500", ["InterestExpense"], ["InterestExpense"],
                  date(2021, 4, 15), date(2023, 10, 17), ("10-K/A",))
        assert classify_stale_fill(c) == ("needs_review", "zero_value")

    # --- (e) rounding vs near-equal ---
    def test_ttwo_rounded_copy_is_skipped(self):
        # ledger 2026-10-17: 3,372,772K vs 3,372.8M (0.0008%).
        c = _cand("3372772000", "3372800000", ["Revenues"], ["Revenues"],
                  date(2020, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("skip", "rounding_equivalent")

    def test_aemd_shape_on_a_periodic_form_goes_to_review_not_replace(self):
        # 0.09%, and 13,400,000 IS 13,388,089 rounded to 100K: still not
        # silently "rounding" (above 0.01%) and never auto-replaced.
        c = _cand("-13388089", "-13400000", ["NetIncomeLoss"], ["NetIncomeLoss"],
                  date(2025, 6, 26), date(2026, 9, 1), ("10-K",))
        assert classify_stale_fill(c) == ("needs_review", "rounded_copy_beyond_tolerance")

    def test_jef_small_real_represent_goes_to_review(self):
        # row 80: 2,187,495K vs 2,186,582K (0.04%), not a rounding pattern.
        c = _cand("2187495000", "2186582000", ["Revenues"], ["Revenues"],
                  date(2013, 2, 25), date(2014, 2, 28))
        assert classify_stale_fill(c) == ("needs_review", "near_equal_not_rounding")

    def test_tiny_difference_without_rounding_pattern_is_not_rounding(self):
        # Under 0.01% but both values at the same precision: not explainable
        # as rounding, so it must not be skipped as rounding_equivalent.
        c = _cand("1234567", "1234568", ["Revenues"], ["Revenues"],
                  date(2020, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("needs_review", "near_equal_not_rounding")

    def test_just_over_near_equal_band_is_proposed(self):
        c = _cand("100000", "101011", ["Revenues"], ["Revenues"],
                  date(2020, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)

    # --- the one class the Verifier found clean (bucket G) ---
    def test_gamg_10qa_restatement_is_proposed(self):
        # row 27: 10-Q 64,180 -> 10-Q/A 187,933 (restated cash).
        c = _cand("64180", "187933", ["CashAndCashEquivalentsAtCarryingValue"],
                  ["CashAndCashEquivalentsAtCarryingValue"],
                  date(2026, 8, 19), date(2026, 10, 1), ("10-Q/A",))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)

    def test_senea_10qa_restatement_is_proposed(self):
        # row 86: SalesRevenueNet 656,495K -> restated 627,397K (4.4%).
        c = _cand("656495000", "627397000", ["SalesRevenueNet"], ["SalesRevenueNet"],
                  date(2017, 10, 26), date(2018, 9, 7), ("10-Q/A",))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)

    def test_equal_values_are_left_alone(self):
        c = _cand("100", "100", ["Revenues"], ["Revenues"], date(2020, 1, 1), date(2021, 1, 1))
        assert classify_stale_fill(c) == ("skip", "equal")


def test_nightly_never_runs_the_stale_refresh():
    import inspect
    import re

    body = inspect.getsource(conflict_resolution.resolve_all_conflict_fills)
    assert not re.search(r"(?<!# )refresh_stale_fills\(", body)
    assert "refresh_stale_fills(conn" not in body


def test_stale_refresh_defaults_to_dry_run():
    import inspect

    sig = inspect.signature(conflict_resolution.refresh_stale_fills)
    assert sig.parameters["dry_run"].default is True


class _FakeCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.conn.executed.append(sql)
        self._sql = sql

    def executemany(self, sql, rows):
        self.conn.written.extend(rows)

    def fetchone(self):
        return (7,)

    def fetchall(self):
        d1, d2 = date(2026, 8, 19), date(2026, 10, 1)
        tag = ["us-gaap:CashAndCashEquivalentsAtCarryingValue"]
        return [
            # GAMG-shaped clean refresh -> proposal
            (1, 10, 100, Decimal("64180"), Decimal("187933"), [5],
             tag, d1, ["a1"], ["10-Q"], tag, False, ["10-Q/A"], ["a2"], d2),
            # sign flip -> needs_review
            (2, 10, 101, Decimal("-35000"), Decimal("66000"), [6],
             tag, d1, ["a1"], ["10-Q"], tag, False, ["10-Q/A"], ["a2"], d2),
            # different tag -> skip
            (3, 10, 102, Decimal("-996000"), Decimal("592000"), [7],
             tag, d1, ["a1"], ["10-Q"], ["us-gaap:Other"], False, ["10-Q"], ["a1"], d1),
        ]


class _FakeConn:
    def __init__(self):
        self.executed, self.written, self.commits = [], [], 0

    def cursor(self):
        return _FakeCursor(self)

    def commit(self):
        self.commits += 1


def test_dry_run_returns_proposals_and_review_and_writes_nothing():
    conn = _FakeConn()
    out = conflict_resolution.refresh_stale_fills(conn, "cash_and_equivalents", "cash_and_equivalents_resolved")
    assert conn.written == [] and conn.commits == 0
    assert [p["id"] for p in out["proposals"]] == [1]
    p = out["proposals"][0]
    assert p["old"] == Decimal("64180") and p["new"] == Decimal("187933")
    assert p["stored_tags"] == p["primary_tags"] and p["primary_forms"] == ["10-Q/A"]
    assert p["primary_accessions"] == ["a2"] and p["guard"] == STALE_FILL_GUARD_CLASS
    assert [r["id"] for r in out["needs_review"]] == [2]
    assert out["needs_review"][0]["guard"] == "sign_flip"
    assert out["skipped"] == {"different_tag": 1}


def test_explicit_apply_writes_only_proposals():
    conn = _FakeConn()
    conflict_resolution.refresh_stale_fills(
        conn, "cash_and_equivalents", "cash_and_equivalents_resolved", dry_run=False
    )
    assert [r["id"] for r in conn.written] == [1]
    assert conn.commits == 1
