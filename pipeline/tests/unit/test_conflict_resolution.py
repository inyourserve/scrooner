from decimal import Decimal

from datetime import date

from scrooner_pipeline.mapper.conflict_resolution import MAX_SAFE_RATIO, MAX_SPLIT_RATIO, MIN_SPLIT_RATIO, _restatement_fill_value, _safe_fill_value, _split_safe_fill_value
from scrooner_pipeline.mapper import conflict_resolution
from scrooner_pipeline.mapper.conflict_resolution import STALE_FILL_GUARD_CLASS, StaleFillCandidate, classify_stale_fill
from scrooner_pipeline.mapper.conflict_resolution import (
    STALE_FILL_INSTANT_CONCEPTS,
    STALE_FILL_PER_SHARE_CONCEPTS,
    _is_re_presentation_tag,
    _is_restricted_cash_tag,
    _share_ratio,
    stale_fill_signals,
)


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
          primary_forms=("10-K",), derived=False, concept="revenue", **extra):
    """A candidate whose 2026-10-19 evidence is loaded and clean unless
    `extra` overrides it: USD (USD/shares for per-share) on both sides, a
    90-day quarter (or an instant for balance-sheet concepts) inside the
    primary filing's window, no other-period copy, no sibling facts, and an
    unchanged share count."""
    instant = concept in STALE_FILL_INSTANT_CONCEPTS
    unit = "usd/shares" if concept in STALE_FILL_PER_SHARE_CONCEPTS else "usd"
    end = date(2020, 3, 31)
    fields = dict(
        concept=concept, row_id=1, company_id=1, period_id=1,
        stored=Decimal(stored), primary=Decimal(primary),
        stored_tags=frozenset("us-gaap:" + t for t in stored_tags),
        primary_tags=frozenset("us-gaap:" + t for t in primary_tags),
        primary_any_derived=derived, primary_forms=frozenset(primary_forms),
        stored_filing_date=stored_date, primary_filing_date=primary_date,
        stored_units=frozenset({unit}), primary_units=frozenset({unit}),
        period_type="instant" if instant else "duration",
        period_start=end if instant else date(2020, 1, 1), period_end=end,
        stored_filing_ids=(1,),
        primary_filings=tuple((2, f, end) for f in sorted(primary_forms)),
        value_at_other_period=False, primary_sibling_tags=frozenset(),
        share_basis_checked=True, share_ratio=Decimal("1"), split_on_record=False,
    )
    fields.update(extra)
    return StaleFillCandidate(**fields)


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
        # Amendments are the proposal class; original forms pass the form
        # guard but stop at the 2026-10-19 re-presentation policy (7).
        for form in ("10-K/A", "10-Q/A", "10-KT/A"):
            c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                      date(2021, 1, 1), (form,))
            assert classify_stale_fill(c)[0] == "propose", form
        for form in ("10-K", "10-Q", "10-KT"):
            c = _cand("100", "200", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                      date(2021, 1, 1), (form,))
            assert classify_stale_fill(c) == ("needs_review", "original_form_basis_unconfirmed"), form
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
                  date(2020, 1, 1), date(2021, 1, 1), ("10-K/A",))
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
    """Answers each query of refresh_stale_fills by its SQL shape."""

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
        sql = self._sql
        if "from analytics.canonical_fact r" in sql:
            return self.conn.candidate_rows()
        if "from core.concept where tag ilike any" in sql:
            return [(900, "us-gaap:RestrictedCash")]
        if "join core.fact f0" in sql:
            return [(5,)]  # row 5's primary value also sits at another period
        if "f.value <> 0" in sql:
            return [(4, 900)]  # row 4: restricted cash at the same instant
        raise AssertionError("unexpected query: " + sql[:80])


class _FakeConn:
    def __init__(self):
        self.executed, self.written, self.commits = [], [], 0

    def cursor(self):
        return _FakeCursor(self)

    def commit(self):
        self.commits += 1

    @staticmethod
    def candidate_rows():
        d1, d2 = date(2026, 8, 19), date(2026, 10, 1)
        q_end = date(2026, 6, 30)
        tag = ["us-gaap:CashAndCashEquivalentsAtCarryingValue"]

        def row(rid, stored, primary, p_tags=tag, p_forms=("10-Q/A",), p_date=d2,
                p_units=("usd",)):
            return (rid, 10, 100 + rid, Decimal(stored), Decimal(primary), [rid * 10],
                    tag, d1, ["a1"], ["10-Q"],
                    p_tags, False, list(p_forms), ["a2"], p_date,
                    ["usd"], list(p_units), [1],
                    [2], list(p_forms), [q_end],
                    "instant", q_end, q_end)

        return [
            row(1, "64180", "187933"),                       # GAMG-shaped -> proposal
            row(2, "-35000", "66000"),                        # sign flip -> review
            row(3, "-996000", "592000", p_tags=["us-gaap:Other"],
                p_forms=("10-Q",), p_date=d1),                # different tag -> skip
            row(4, "26996932", "19878673"),                   # FDCT-shaped -> review
            row(5, "100000", "120000"),                       # label error -> review
            row(6, "4754597", "1959399", p_units=("twd",)),  # IVDA-shaped -> skip
        ]


def test_dry_run_returns_proposals_and_review_and_writes_nothing():
    conn = _FakeConn()
    out = conflict_resolution.refresh_stale_fills(conn, "cash_and_equivalents", "cash_and_equivalents_resolved")
    assert conn.written == [] and conn.commits == 0
    assert [p["id"] for p in out["proposals"]] == [1]
    p = out["proposals"][0]
    assert p["old"] == Decimal("64180") and p["new"] == Decimal("187933")
    assert p["stored_tags"] == p["primary_tags"] and p["primary_forms"] == ["10-Q/A"]
    assert p["primary_accessions"] == ["a2"] and p["guard"] == STALE_FILL_GUARD_CLASS
    assert p["signals"] == []
    assert {r["id"]: r["guard"] for r in out["needs_review"]} == {
        2: "sign_flip", 4: "restricted_cash_same_date", 5: "value_at_other_period"}
    assert out["skipped"] == {"different_tag": 1, "non_usd_unit": 1}
    assert "skipped_rows" not in out


def test_dry_run_can_return_skipped_rows():
    conn = _FakeConn()
    out = conflict_resolution.refresh_stale_fills(
        conn, "cash_and_equivalents", "cash_and_equivalents_resolved", include_skipped=True)
    assert sorted((r["id"], r["guard"]) for r in out["skipped_rows"]) == [
        (3, "different_tag"), (6, "non_usd_unit")]
    assert conn.written == []


def test_explicit_apply_writes_only_proposals():
    conn = _FakeConn()
    conflict_resolution.refresh_stale_fills(
        conn, "cash_and_equivalents", "cash_and_equivalents_resolved", dry_run=False
    )
    assert [r["id"] for r in conn.written] == [1]
    assert conn.commits == 1


def _p(stored, primary, tag, concept, start, end, stored_date, primary_date,
       primary_form, period_of_report, **extra):
    """A candidate built from one data-team/29 row: values, tag, forms,
    filing dates and the primary filing's period_of_report (core.filing,
    read 2026-10-19). Instant concepts pass start == end."""
    instant = concept in STALE_FILL_INSTANT_CONCEPTS
    fields = dict(
        period_type="instant" if instant else "duration",
        period_start=start, period_end=end,
        primary_filings=((2, primary_form, period_of_report),),
    )
    fields.update(extra)
    return _cand(stored, primary, [tag], [tag], stored_date, primary_date,
                 (primary_form,), concept=concept, **fields)


class TestVerifier29Guards:
    """The 19 wrong proposals of data-team/29-VERIFIER-GUARDED-STALE-FILL-
    2026-10-18.md (FILING-CHECKED there) plus correct amendment rows that
    must stay proposals. Sibling tags and share counts are the real core.fact
    rows of the cited accessions unless a test says it is a shape."""

    # --- (1) period-label error in the later filing ---
    def test_swk_shifted_quarter_value_at_other_period(self):
        # SWK FY2019 10-K 0000093556-20-000006 R134: "Sep. 30, 2017" carries
        # Q3 2018's 3,494.8M. Stored 3,359.4M is right.
        c = _p("3359400000", "3494800000", "Revenues", "revenue",
               date(2017, 7, 2), date(2017, 9, 30), date(2019, 2, 26), date(2020, 2, 21),
               "10-K", date(2019, 12, 28), value_at_other_period=True)
        assert classify_stale_fill(c) == ("needs_review", "value_at_other_period")
        # and the period is outside the FY2019 10-K's own window on its own
        c2 = _p("3359400000", "3494800000", "Revenues", "revenue",
                date(2017, 7, 2), date(2017, 9, 30), date(2019, 2, 26), date(2020, 2, 21),
                "10-K/A", date(2019, 12, 28))
        assert classify_stale_fill(c2) == ("needs_review", "outside_comparative_window")

    def test_swk_2018_quarters_inside_window_caught_by_value_match(self):
        for start, end, old, new in [
            (date(2017, 12, 31), date(2018, 3, 31), "3209300000", "3333600000"),
            (date(2018, 4, 1), date(2018, 6, 30), "3643600000", "3761300000"),
            (date(2018, 7, 1), date(2018, 9, 29), "3494800000", "3633100000"),
        ]:
            c = _p(old, new, "Revenues", "revenue", start, end, date(2019, 4, 26),
                   date(2020, 2, 21), "10-K", date(2019, 12, 28), value_at_other_period=True)
            assert classify_stale_fill(c) == ("needs_review", "value_at_other_period")
            assert "outside_comparative_window" not in stale_fill_signals(c)

    def test_cb_shifted_contexts(self):
        # CB FY2015 10-K 0000896159-16-000027 R120.
        for start, end, old, new in [
            (date(2013, 1, 1), date(2013, 3, 31), "4310000000", "4419000000"),
            (date(2014, 7, 1), date(2014, 9, 30), "5200000000", "4871000000"),
            (date(2014, 4, 1), date(2014, 6, 30), "4815000000", "5048000000"),
            (date(2013, 4, 1), date(2013, 6, 30), "4705000000", "4815000000"),
        ]:
            c = _p(old, new, "Revenues", "revenue", start, end, date(2015, 2, 27),
                   date(2016, 2, 26), "10-K", date(2015, 12, 31), value_at_other_period=True)
            assert classify_stale_fill(c) == ("needs_review", "value_at_other_period")
        # the 2013 quarters are also two-plus years before the 2015 period end
        c = _p("4310000000", "4419000000", "Revenues", "revenue", date(2013, 1, 1),
               date(2013, 3, 31), date(2015, 2, 27), date(2016, 2, 26), "10-K/A", date(2015, 12, 31))
        assert classify_stale_fill(c) == ("needs_review", "outside_comparative_window")

    def test_ford_rdi_mhh_value_match_and_outside_window(self):
        rows = [
            # Ford FY2017 10-K 0000037996-18-000015 R107: "Jun. 30, 2015" = Q2 2016.
            ("37263000000", "39485000000", "Revenues", date(2015, 4, 1), date(2015, 6, 30),
             date(2017, 2, 9), date(2018, 2, 8), date(2017, 12, 31)),
            # RDI FY2014 10-K 0001562762-15-000083: FY2012 254,430K under 2011.
            ("244979000", "254430000", "Revenues", date(2011, 1, 1), date(2011, 12, 31),
             date(2014, 3, 7), date(2015, 3, 17), date(2014, 12, 31)),
            # MHH FY2023 10-K 0001193125-24-068609 R41/R42: FY2021 under 2020.
            ("194101000", "222012000", "RevenueFromContractWithCustomerExcludingAssessedTax",
             date(2020, 1, 1), date(2020, 12, 31), date(2023, 3, 27), date(2024, 3, 15),
             date(2023, 12, 31)),
        ]
        for old, new, tag, start, end, sd, pd, por in rows:
            c = _p(old, new, tag, "revenue", start, end, sd, pd, "10-K", por,
                   value_at_other_period=True)
            assert classify_stale_fill(c) == ("needs_review", "value_at_other_period")
            c = _p(old, new, tag, "revenue", start, end, sd, pd, "10-K/A", por)
            assert classify_stale_fill(c) == ("needs_review", "outside_comparative_window"), tag

    def test_window_edges(self):
        base = dict(stored="100", primary="120", tag="Revenues", concept="revenue",
                    stored_date=date(2020, 1, 1), primary_date=date(2021, 1, 1))
        # three fiscal years in a 10-K: FY-2 ends exactly two years back -> inside
        c = _p(start=date(2017, 1, 1), end=date(2017, 12, 31), primary_form="10-K/A",
               period_of_report=date(2019, 12, 31), **base)
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)
        # a 10-Q reaches one year back for flows, not two
        c = _p(start=date(2018, 1, 1), end=date(2018, 3, 31), primary_form="10-Q/A",
               period_of_report=date(2019, 3, 31), **base)
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)
        c = _p(start=date(2017, 1, 1), end=date(2017, 3, 31), primary_form="10-Q/A",
               period_of_report=date(2019, 3, 31), **base)
        assert classify_stale_fill(c) == ("needs_review", "outside_comparative_window")
        # a period after the document period end is outside too
        c = _p(start=date(2020, 1, 1), end=date(2020, 3, 31), primary_form="10-Q/A",
               period_of_report=date(2019, 12, 31), **base)
        assert classify_stale_fill(c) == ("needs_review", "outside_comparative_window")
        # a 10-K equity statement opens three years back: instant inside
        c = _p("100", "120", "StockholdersEquity", "stockholders_equity",
               date(2016, 12, 31), date(2016, 12, 31), date(2020, 1, 1), date(2021, 1, 1),
               "10-K/A", date(2019, 12, 31))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)
        # unknown document period end is never treated as inside
        c = _p(start=date(2020, 1, 1), end=date(2020, 3, 31), primary_form="10-Q/A",
               period_of_report=None, **base)
        assert classify_stale_fill(c) == ("needs_review", "comparative_window_unknown")

    # --- (2) continuing-ops subtotal under the total cash-flow tag ---
    def test_mgnc_continuing_ops_cfo(self):
        # MGNC 10-K 0001683168-26-007689 R6: 59,584 is continuing-ops CFO;
        # discontinued (1,974) sits beside it. Stored total (61,558) is right.
        c = _p("-61558", "-59584", "NetCashProvidedByUsedInOperatingActivities", "cfo",
               date(2024, 5, 1), date(2025, 4, 30), date(2025, 7, 23), date(2026, 10, 7),
               "10-K", date(2026, 4, 30),
               primary_sibling_tags=frozenset({
                   "us-gaap:CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
                   "us-gaap:CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
                   "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations",
                   "us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax"}))
        assert classify_stale_fill(c) == ("needs_review", "continuing_ops_subtotal")

    LRDC_SIBLINGS = frozenset({
        "us-gaap:CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
        "us-gaap:CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
        "us-gaap:CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
        "us-gaap:NetCashProvidedByUsedInDiscontinuedOperations",
        "us-gaap:DisposalGroupIncludingDiscontinuedOperationOperatingIncomeLoss",
        "us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax",
        "us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffectContinuingOperations",
    })

    def test_lrdc_amendment_continuing_ops_cash_flows(self):
        # LRDC 10-K/A 0001199835-26-000359 R6: continuing CFO/CFI/CFF under
        # the total tags. An amendment, so only guard (2) can stop it.
        for concept, tag, old, new in [
            ("cfo", "NetCashProvidedByUsedInOperatingActivities", "-1649834", "-1413370"),
            ("cash_flow_investing", "NetCashProvidedByUsedInInvestingActivities", "-3174164", "-794521"),
            ("cash_flow_financing", "NetCashProvidedByUsedInFinancingActivities", "3111176", "2379676"),
        ]:
            c = _p(old, new, tag, concept, date(2024, 6, 1), date(2025, 5, 31),
                   date(2025, 9, 15), date(2026, 9, 30), "10-K/A", date(2026, 5, 31),
                   primary_sibling_tags=self.LRDC_SIBLINGS)
            assert classify_stale_fill(c) == ("needs_review", "continuing_ops_subtotal"), concept
            clean = _p(old, new, tag, concept, date(2024, 6, 1), date(2025, 5, 31),
                       date(2025, 9, 15), date(2026, 9, 30), "10-K/A", date(2026, 5, 31))
            assert classify_stale_fill(clean) == ("propose", STALE_FILL_GUARD_CLASS)

    def test_lrdc_operating_income_amendment_stays_a_proposal(self):
        # Verifier row 60 (B, inside the 38 unflagged amendment rows): the
        # disc-ops siblings only gate cash-flow totals, and (7) only gates
        # original forms.
        c = _p("-3322430", "-2587374", "OperatingIncomeLoss", "operating_income",
               date(2024, 6, 1), date(2025, 5, 31), date(2025, 9, 15), date(2026, 9, 30),
               "10-K/A", date(2026, 5, 31), primary_sibling_tags=self.LRDC_SIBLINGS)
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)

    # --- (3) cash vs cash plus restricted cash ---
    def test_fdct_restricted_cash_same_instant(self):
        # FDCT 10-Q/A 0001493152-26-027765: plain-cash tag = 19,878,673 total;
        # RestrictedCash 17,453,282 at the same instant; face cash 2,425,391.
        c = _p("26996932", "19878673", "CashAndCashEquivalentsAtCarryingValue",
               "cash_and_equivalents", date(2025, 3, 31), date(2025, 3, 31),
               date(2025, 8, 11), date(2026, 6, 8), "10-Q/A", date(2025, 3, 31),
               primary_sibling_tags=frozenset({
                   "us-gaap:RestrictedCash", "us-gaap:RestrictedCashAndCashEquivalents",
                   "us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations"}))
        assert classify_stale_fill(c) == ("needs_review", "restricted_cash_same_date")

    def test_combined_cash_tag_alone_is_enough(self):
        c = _p("100", "120", "CashAndCashEquivalentsAtCarryingValue", "cash_and_equivalents",
               date(2025, 3, 31), date(2025, 3, 31), date(2025, 8, 11), date(2026, 6, 8),
               "10-Q/A", date(2025, 3, 31),
               primary_sibling_tags=frozenset({"us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"}))
        assert classify_stale_fill(c) == ("needs_review", "restricted_cash_same_date")

    def test_restricted_cash_does_not_gate_other_concepts(self):
        c = _p("100", "120", "Assets", "total_assets", date(2025, 3, 31), date(2025, 3, 31),
               date(2025, 8, 11), date(2026, 6, 8), "10-Q/A", date(2025, 3, 31),
               primary_sibling_tags=frozenset({"us-gaap:RestrictedCash"}))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)

    def test_tag_families(self):
        assert _is_restricted_cash_tag("us-gaap:RestrictedCashCurrent")
        assert _is_restricted_cash_tag("us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents")
        assert not _is_restricted_cash_tag("us-gaap:CashAndCashEquivalentsAtCarryingValue")
        assert _is_re_presentation_tag("us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax")
        assert _is_re_presentation_tag("us-gaap:DisposalGroupIncludingDiscontinuedOperationOperatingIncomeLoss")
        assert _is_re_presentation_tag("us-gaap:StockholdersEquityNoteSpinoffTransaction")
        # the standard combined cash total is not evidence of discontinued ops
        assert not _is_re_presentation_tag(
            "us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations")
        assert not _is_re_presentation_tag(
            "us-gaap:EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations")

    # --- (4) unit ---
    def test_ivda_twd_component_is_skipped(self):
        # IVDA 10-K/A 0001641172-25-015284: 1,959,399 is cash held in TWD,
        # unit twd (core.fact 45910028); USD face total 4,738,504.
        c = _p("4754597", "1959399", "CashAndCashEquivalentsAtCarryingValue",
               "cash_and_equivalents", date(2023, 12, 31), date(2023, 12, 31),
               date(2024, 11, 14), date(2025, 6, 16), "10-K/A", date(2024, 12, 31),
               primary_units=frozenset({"twd"}))
        assert classify_stale_fill(c) == ("skip", "non_usd_unit")

    def test_unit_must_match_stored_and_concept(self):
        common = ("100", "120")
        c = _cand(*common, ["Revenues"], ["Revenues"], date(2020, 1, 1), date(2021, 1, 1),
                  ("10-K/A",), stored_units=frozenset({"eur"}))
        assert classify_stale_fill(c) == ("skip", "non_usd_unit")
        c = _cand(*common, ["Revenues"], ["Revenues"], date(2020, 1, 1), date(2021, 1, 1),
                  ("10-K/A",), primary_units=frozenset({"usd", "twd"}))
        assert classify_stale_fill(c) == ("skip", "non_usd_unit")
        c = _cand(*common, ["Revenues"], ["Revenues"], date(2020, 1, 1), date(2021, 1, 1),
                  ("10-K/A",), primary_units=frozenset(), stored_units=frozenset())
        assert classify_stale_fill(c) == ("skip", "non_usd_unit")
        c = _cand("-0.29", "-0.19", ["EarningsPerShareBasic"], ["EarningsPerShareBasic"],
                  date(2020, 1, 1), date(2021, 1, 1), ("10-Q/A",), concept="basic_eps",
                  primary_units=frozenset({"usd"}), stored_units=frozenset({"usd"}))
        assert classify_stale_fill(c) == ("skip", "non_usd_unit")

    # --- (5) not a real period ---
    def test_eonr_one_day_interest_context_is_skipped(self):
        # EONR InterestExpenseDebt on 2025-09-09..2025-09-09 (debt note).
        c = _p("37591", "137728", "InterestExpenseDebt", "interest_expense",
               date(2025, 9, 9), date(2025, 9, 9), date(2025, 11, 17), date(2026, 10, 13),
               "10-K/A", date(2025, 12, 31))
        assert classify_stale_fill(c) == ("skip", "short_duration")

    def test_wyy_annual_value_from_a_10q_is_skipped(self):
        # WYY 10-Q 0001654954-22-006878 tags Q1 2021's 20,650,843 with FY2020.
        c = _p("180343015", "20650843", "Revenues", "revenue", date(2020, 1, 1),
               date(2020, 12, 31), date(2022, 3, 28), date(2022, 5, 16), "10-Q",
               date(2022, 3, 31), value_at_other_period=True)
        assert classify_stale_fill(c) == ("skip", "annual_from_10q")

    def test_real_calendar_lengths_pass(self):
        # Apple: 98-day Q1 FY2023, 371-day FY2023, 280-day 9M YTD in a 10-Q.
        for start, end, form, por in [
            (date(2022, 9, 25), date(2022, 12, 31), "10-Q/A", date(2022, 12, 31)),
            (date(2022, 9, 25), date(2023, 9, 30), "10-K/A", date(2023, 9, 30)),
            (date(2022, 9, 25), date(2023, 7, 1), "10-Q/A", date(2023, 7, 1)),
        ]:
            c = _p("100", "120", "Revenues", "revenue", start, end, date(2023, 1, 1),
                   date(2024, 1, 1), form, por)
            assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS), (start, end)
        c = _p("100", "120", "Revenues", "revenue", date(2020, 1, 1), date(2020, 3, 20),
               date(2023, 1, 1), date(2024, 1, 1), "10-Q/A", date(2020, 3, 31))
        assert classify_stale_fill(c) == ("skip", "short_duration")  # 79 days

    def test_period_type_must_fit_the_concept(self):
        c = _cand("100", "120", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K/A",), period_type="instant",
                  period_start=date(2020, 3, 31))
        assert classify_stale_fill(c) == ("skip", "period_type_mismatch")
        c = _cand("100", "120", ["Assets"], ["Assets"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K/A",), concept="total_assets",
                  period_type="duration", period_start=date(2020, 1, 1))
        assert classify_stale_fill(c) == ("skip", "period_type_mismatch")

    # --- (6) share-basis change on per-share concepts ---
    def test_gure_ncra_svmb_share_rebasing(self):
        # Weighted shares from the filings (data-team/29 section 4):
        # GURE 10,726,924 -> 1,091,562; NCRA 14,306,487 -> 481,121;
        # SVMB 209,845,205 -> 1,055,138. All amendments, so only (6) stops them.
        rows = [
            ("basic_eps", "EarningsPerShareBasic", "-3.46", "-33.98", date(2024, 1, 1),
             date(2024, 6, 30), date(2024, 10, 11), date(2026, 9, 30), "10-Q/A",
             date(2025, 6, 30), 10726924, 1091562),
            ("diluted_eps", "EarningsPerShareDiluted", "-0.2069", "-6.1524", date(2025, 1, 1),
             date(2025, 12, 31), date(2026, 4, 21), date(2026, 8, 28), "10-K/A",
             date(2025, 12, 31), 14306487, 481121),
            ("basic_eps", "EarningsPerShareBasic", "-0.03", "-6.42", date(2022, 3, 1),
             date(2023, 2, 28), date(2024, 8, 15), date(2025, 5, 6), "10-K/A",
             date(2024, 2, 29), 209845205, 1055138),
        ]
        for concept, tag, old, new, start, end, sd, pd, form, por, s_sh, p_sh in rows:
            ratio = Decimal(max(s_sh, p_sh)) / Decimal(min(s_sh, p_sh))
            c = _p(old, new, tag, concept, start, end, sd, pd, form, por, share_ratio=ratio)
            assert classify_stale_fill(c) == ("needs_review", "split_basis_change"), tag

    def test_buru_split_without_comparable_shares_uses_the_value_move(self):
        # BURU 10-Q/A 0001193125-26-396895: 1-for-40 split applied
        # retroactively; -0.92 -> -36.81 (shape: share facts not comparable).
        c = _p("-0.92", "-36.81", "EarningsPerShareDiluted", "diluted_eps",
               date(2025, 4, 1), date(2025, 6, 30), date(2026, 8, 14), date(2026, 9, 22),
               "10-Q/A", date(2026, 6, 30), share_ratio=None)
        assert classify_stale_fill(c) == ("needs_review", "split_basis_change")
        # a split on record does not make it a per-cell refresh either
        c = StaleFillCandidate(**{**c.__dict__, "split_on_record": True})
        assert classify_stale_fill(c) == ("needs_review", "split_basis_change")

    def test_rolr_restatement_with_unchanged_shares_stays_a_proposal(self):
        # ROLR 10-Q/A 0001753926-26-001959: -0.29 -> -0.19 restated (PR). The
        # value moves 1.53x, so only an unchanged share count keeps it in.
        c = _p("-0.29", "-0.19", "EarningsPerShareBasic", "basic_eps", date(2026, 1, 1),
               date(2026, 3, 31), date(2026, 5, 12), date(2026, 10, 16), "10-Q/A",
               date(2026, 3, 31), share_ratio=Decimal("1.0"))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)
        c = StaleFillCandidate(**{**c.__dict__, "share_ratio": None})
        assert classify_stale_fill(c) == ("needs_review", "split_basis_change")

    def test_share_ratio_threshold_and_unchecked(self):
        mk = lambda **kw: _p("-1", "-1.2", "EarningsPerShareBasic", "basic_eps",
                             date(2026, 1, 1), date(2026, 3, 31), date(2026, 5, 12),
                             date(2026, 10, 16), "10-Q/A", date(2026, 3, 31), **kw)
        assert classify_stale_fill(mk(share_ratio=Decimal("1.49")))[0] == "propose"
        assert classify_stale_fill(mk(share_ratio=Decimal("1.5"))) == ("needs_review", "split_basis_change")
        assert classify_stale_fill(mk(share_basis_checked=False)) == ("needs_review", "share_basis_not_checked")

    def test_share_ratio_compares_same_tag_across_the_two_filings(self):
        w = "us-gaap:WeightedAverageNumberOfSharesOutstandingBasic"
        rows = [(1, w, "same", Decimal("10726924")), (2, w, "same", Decimal("1091562")),
                (2, "us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding", "same", Decimal("1091562"))]
        assert _share_ratio(rows, {1}, {2}) == Decimal("10726924") / Decimal("1091562")
        assert _share_ratio(rows, {1}, {3}) is None
        assert _share_ratio([(1, w, "same", Decimal("0")), (2, w, "same", Decimal("5"))], {1}, {2}) is None

    # --- (7) re-presentation policy ---
    def test_msge_original_10k_re_presentation_goes_to_review(self):
        # Verifier row 0 (B): MSGE FY2024 revenue re-presented in the next
        # 10-K, reason not established. Original form -> not a proposal.
        c = _p("885989000", "959265000", "RevenueFromContractWithCustomerExcludingAssessedTax",
               "revenue", date(2023, 7, 1), date(2024, 6, 30), date(2025, 8, 13),
               date(2026, 8, 12), "10-K", date(2026, 6, 30))
        assert classify_stale_fill(c) == ("needs_review", "original_form_basis_unconfirmed")

    def test_discontinued_ops_in_original_form_is_a_re_presentation_candidate(self):
        # PPG FY2022 revenue 17,652M -> 15,614M re-presented for discontinued
        # ops (Verifier row 14; sibling tag is a shape, not read here).
        c = _p("17652000000", "15614000000", "Revenues", "revenue", date(2022, 1, 1),
               date(2022, 12, 31), date(2024, 2, 15), date(2025, 2, 20), "10-K",
               date(2024, 12, 31),
               primary_sibling_tags=frozenset({"us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax"}))
        assert classify_stale_fill(c) == ("needs_review", "re_presentation_candidate")
        # the combined cash total alone is not a discontinued-ops signal
        c = StaleFillCandidate(**{**c.__dict__, "primary_sibling_tags": frozenset({
            "us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations"})})
        assert classify_stale_fill(c) == ("needs_review", "original_form_basis_unconfirmed")

    def test_mixed_original_and_amendment_primary_is_not_an_amendment(self):
        c = _cand("100", "120", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K", "10-K/A"))
        assert classify_stale_fill(c) == ("needs_review", "original_form_basis_unconfirmed")

    def test_policy_switch_admits_unflagged_originals_only(self, monkeypatch):
        monkeypatch.setattr(conflict_resolution, "STALE_FILL_PROPOSE_ORIGINAL_FORMS", True)
        c = _p("885989000", "959265000", "RevenueFromContractWithCustomerExcludingAssessedTax",
               "revenue", date(2023, 7, 1), date(2024, 6, 30), date(2025, 8, 13),
               date(2026, 8, 12), "10-K", date(2026, 6, 30))
        assert classify_stale_fill(c) == ("propose", STALE_FILL_GUARD_CLASS)
        c = StaleFillCandidate(**{**c.__dict__, "primary_sibling_tags": frozenset(
            {"us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax"})})
        assert classify_stale_fill(c) == ("needs_review", "re_presentation_candidate")

    # --- correct amendment rows stay proposals; missing evidence never proposes ---
    def test_correct_amendment_rows_stay_proposals(self):
        rows = [  # Verifier PR rows (FILING-CHECKED restatements)
            # ROLR 10-Q/A 0001753926-26-001959
            ("-2996000", "-1993000", "OperatingIncomeLoss", "operating_income", date(2026, 1, 1),
             date(2026, 3, 31), date(2026, 5, 12), date(2026, 10, 16), "10-Q/A", date(2026, 3, 31)),
            # EONR 10-K/A 0001213900-26-108617
            ("86938586", "90478586", "Assets", "total_assets", date(2025, 12, 31),
             date(2025, 12, 31), date(2026, 9, 28), date(2026, 10, 13), "10-K/A", date(2025, 12, 31)),
            # TULP 10-K/A 0001654954-21-009347 (quarter inside its window)
            ("5842000", "5727000", "Revenues", "revenue", date(2019, 4, 1), date(2019, 6, 30),
             date(2020, 8, 11), date(2021, 8, 23), "10-K/A", date(2020, 12, 31)),
        ]
        for row in rows:
            assert classify_stale_fill(_p(*row)) == ("propose", STALE_FILL_GUARD_CLASS), row

    def test_unloaded_evidence_is_never_a_proposal(self):
        c = _cand("100", "120", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K/A",), value_at_other_period=None)
        assert classify_stale_fill(c) == ("needs_review", "other_period_check_not_loaded")
        c = _cand("100", "120", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K/A",), primary_sibling_tags=None)
        assert classify_stale_fill(c) == ("needs_review", "sibling_check_not_loaded")
        c = _cand("100", "120", ["Revenues"], ["Revenues"], date(2020, 1, 1),
                  date(2021, 1, 1), ("10-K/A",), primary_filings=())
        assert classify_stale_fill(c) == ("needs_review", "comparative_window_unknown")
