from decimal import Decimal

import pytest

from scrooner_pipeline.sanity.tag_investigator import FIXABLE_CONCEPTS, _reconcile_by_mode, _score_and_decide


def _candidate(taxonomy="us-gaap", tag="Revenues", value=1000, is_authoritative=True, fact_id=1):
    return {"taxonomy": taxonomy, "tag": tag, "value": value, "is_authoritative": is_authoritative, "fact_id": fact_id}


@pytest.mark.unit
class TestScoreAndDecide:
    def test_auto_fixes_when_within_tolerance_and_concept_is_fixable(self):
        assert "revenue" in FIXABLE_CONCEPTS  # the actual, currently-wired case
        candidates = [_candidate(tag="Revenues", value=3_944_850_000)]
        outcome = _score_and_decide(candidates, Decimal(3_939_697_000), "revenue")
        assert outcome["outcome"] == "auto_fixed"
        assert outcome["candidate"]["tag"] == "Revenues"

    def test_needs_review_when_within_tolerance_but_concept_not_wired_up(self):
        """shares_outstanding has no *_sanity_resolved concept seeded yet
        -- a reconciling candidate is a real lead, but must NOT be
        silently applied without one existing to write into."""
        assert "shares_outstanding" not in FIXABLE_CONCEPTS
        candidates = [_candidate(tag="EntityCommonStockSharesOutstanding", value=1_200_000_000)]
        outcome = _score_and_decide(candidates, Decimal(1_202_110_951), "shares_outstanding")
        assert outcome["outcome"] == "needs_review"

    def test_no_match_found_when_best_candidate_still_far_off(self):
        """The Flowserve-shaped case's own failure mode, if the ONLY
        available tag were the spurious one: a $0 candidate against a
        real multi-billion external figure is nowhere near the tolerance,
        so this must not silently 'fix' anything."""
        candidates = [_candidate(tag="Revenues", value=0)]
        outcome = _score_and_decide(candidates, Decimal(4_440_492_343_296), "revenue")
        assert outcome["outcome"] == "no_match_found"

    def test_picks_the_closest_of_several_candidates(self):
        candidates = [
            _candidate(tag="Revenues", value=0, is_authoritative=True),
            _candidate(tag="RevenueFromContractWithCustomerExcludingAssessedTax", value=3_944_850_000, is_authoritative=False),
            _candidate(tag="SalesRevenueNet", value=2_000_000_000, is_authoritative=False),
        ]
        outcome = _score_and_decide(candidates, Decimal(3_939_697_000), "revenue")
        assert outcome["candidate"]["tag"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
        assert outcome["outcome"] == "auto_fixed"

    def test_boundary_exactly_at_tolerance_is_trusted(self):
        # 20% exactly (AUTO_FIX_TOLERANCE_PCT) -- <= means the boundary itself counts as trusted.
        candidates = [_candidate(tag="Revenues", value=1_200)]
        outcome = _score_and_decide(candidates, Decimal(1_000), "revenue")
        assert outcome["outcome"] == "auto_fixed"


@pytest.mark.unit
class TestReconcileByMode:
    """The real Flowserve shape: 3 filings report a real revenue tag for
    the same period, 2 agree exactly and 1 differs by a trivial rounding
    amount -- picking the majority value is the whole point of this
    function (never averaging, never "most recent," never guessing
    between equally-supported values)."""

    def test_majority_value_wins_over_a_lone_disagreement(self):
        rows = [(1, 3_939_697_000, 100), (1, 3_939_697_000, 101), (1, 3_944_850_000, 102)]
        result = _reconcile_by_mode(rows)
        assert result[1] == (3_939_697_000, 101)  # majority value, tie-broken to the higher of the 2 agreeing fact_ids

    def test_single_value_per_period_passes_through(self):
        rows = [(1, 5_000, 200), (2, 6_000, 201)]
        result = _reconcile_by_mode(rows)
        assert result == {1: (5_000, 200), 2: (6_000, 201)}

    def test_exact_tie_breaks_to_highest_fact_id(self):
        rows = [(1, 100, 10), (1, 200, 20)]
        result = _reconcile_by_mode(rows)
        assert result[1] == (200, 20)

    def test_independent_periods_reconciled_separately(self):
        rows = [(1, 100, 1), (1, 100, 2), (1, 999, 3), (2, 50, 4), (2, 999, 5)]
        result = _reconcile_by_mode(rows)
        assert result[1] == (100, 2)  # period 1's majority
        assert result[2][0] in (50, 999)  # period 2 has no majority (1 vs 1) -- tie-break still deterministic
        assert result[2] == (999, 5)  # tie-broken to the higher fact_id


class _FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self.rowcount = 0
        self._result = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=None):
        text = " ".join(sql.split())
        self.conn.sql.append(text)
        if "from analytics.canonical_concept where name" in text:
            self._result = [(len(self.conn.sql),)]
        elif "from analytics.company_tag_preference" in text:
            self._result = []
        else:
            self._result = [(0,)]

    def fetchone(self):
        return self._result[0]

    def fetchall(self):
        return self._result


class _FakeConn:
    def __init__(self):
        self.sql = []

    def cursor(self):
        return _FakeCursor(self)

    def commit(self):
        pass


@pytest.mark.unit
@pytest.mark.parametrize(("concept", "expect_drop"), [("revenue", True), ("total_debt", False)])
def test_stale_display_rows_are_dropped_except_without_a_refill_path(concept, expect_drop):
    from scrooner_pipeline.sanity import tag_investigator

    conn = _FakeConn()
    tag_investigator.resolve_company_tag_preferences(conn, concept, f"{concept}_resolved")

    drops = [s for s in conn.sql if "f.value <> cf.value" in s]
    assert bool(drops) is expect_drop
    if expect_drop:
        # The drop runs before the baseline copy that refills those rows.
        baseline = next(i for i, s in enumerate(conn.sql) if "on conflict (company_id, canonical_concept_id, period_id) do nothing" in s)
        assert conn.sql.index(drops[0]) < baseline
