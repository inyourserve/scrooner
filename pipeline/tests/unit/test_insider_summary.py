from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.ownership import insider_summary


def _tx(
    id_,
    owner_cik=None,
    owner_name="Some Insider",
    transaction_date=None,
    filing_date=None,
    code="P",
    shares=None,
    price=None,
    shares_owned_following=None,
):
    return {
        "id": id_,
        "reporting_owner_cik": owner_cik,
        "reporting_owner_name": owner_name,
        "transaction_date": transaction_date,
        "filing_date": filing_date,
        "transaction_code": code,
        "shares": shares,
        "price_per_share": price,
        "shares_owned_following": shares_owned_following,
    }


@pytest.mark.unit
class TestMonthsAgo:
    def test_clamps_to_shorter_target_month(self):
        # Aug 31 minus 6 months -> Feb (28 days in 2026, a non-leap year)
        assert insider_summary._months_ago(6, date(2026, 8, 31)) == date(2026, 2, 28)

    def test_plain_case(self):
        assert insider_summary._months_ago(3, date(2026, 8, 29)) == date(2026, 5, 29)

    def test_crosses_year_boundary(self):
        assert insider_summary._months_ago(12, date(2026, 8, 29)) == date(2025, 8, 29)


@pytest.mark.unit
class TestComputeOwnershipPct:
    def test_sums_each_owners_latest_transaction_only(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 1, 1), shares_owned_following=Decimal("90")),
            _tx(2, owner_cik="A1", transaction_date=date(2026, 3, 1), shares_owned_following=Decimal("100")),  # latest for A1
            _tx(3, owner_cik=None, owner_name="Bob", transaction_date=date(2026, 2, 1), shares_owned_following=Decimal("50")),
        ]
        result = insider_summary.compute_ownership_pct(rows, Decimal("1000"))
        assert result["shares_owned_by_insiders"] == Decimal("150")  # 100 (A1 latest) + 50 (Bob), not 90+100+50
        assert result["distinct_insiders_count"] == 2
        assert result["ownership_pct"] == Decimal("150") / Decimal("1000")
        assert result["is_null_reason"] is None

    def test_missing_shares_outstanding_is_null_with_reason(self):
        rows = [_tx(1, owner_cik="A1", transaction_date=date(2026, 1, 1), shares_owned_following=Decimal("10"))]
        result = insider_summary.compute_ownership_pct(rows, None)
        assert result["ownership_pct"] is None
        assert result["is_null_reason"] == "missing:shares_outstanding"
        assert result["shares_owned_by_insiders"] == Decimal("10")  # numerator still real, only pct withheld

    def test_zero_shares_outstanding_is_null_not_division_error(self):
        rows = [_tx(1, owner_cik="A1", transaction_date=date(2026, 1, 1), shares_owned_following=Decimal("10"))]
        result = insider_summary.compute_ownership_pct(rows, Decimal("0"))
        assert result["ownership_pct"] is None
        assert result["is_null_reason"] == "zero_denominator"

    def test_no_usable_shares_owned_following_is_null_with_reason(self):
        rows = [_tx(1, owner_cik="A1", transaction_date=date(2026, 1, 1), shares_owned_following=None)]
        result = insider_summary.compute_ownership_pct(rows, Decimal("1000"))
        assert result["is_null_reason"] == "missing:shares_owned_following"
        assert result["distinct_insiders_count"] == 0

    def test_falls_back_to_filing_date_and_id_when_transaction_date_missing(self):
        # transaction_date NULL for both -- must fall back to filing_date, then id, not crash.
        rows = [
            _tx(1, owner_cik="A1", transaction_date=None, filing_date=date(2026, 1, 1), shares_owned_following=Decimal("10")),
            _tx(2, owner_cik="A1", transaction_date=None, filing_date=date(2026, 2, 1), shares_owned_following=Decimal("20")),
        ]
        result = insider_summary.compute_ownership_pct(rows, Decimal("100"))
        assert result["shares_owned_by_insiders"] == Decimal("20")  # the later filing_date wins


@pytest.mark.unit
class TestComputeWindowSummary:
    AS_OF = date(2026, 8, 29)

    def test_separates_buys_and_sells_and_ignores_other_codes(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 8, 1), code="P", shares=Decimal("10"), price=Decimal("5")),
            _tx(2, owner_cik="A2", transaction_date=date(2026, 8, 5), code="S", shares=Decimal("4"), price=Decimal("6")),
            _tx(3, owner_cik="A3", transaction_date=date(2026, 8, 10), code="G", shares=Decimal("999")),  # gift, must not count
            _tx(4, owner_cik="A4", transaction_date=date(2026, 8, 10), code="A", shares=Decimal("999")),  # grant, must not count
        ]
        result = insider_summary.compute_window_summary(rows, 3, as_of=self.AS_OF)
        assert result["shares_bought"] == Decimal("10")
        assert result["shares_sold"] == Decimal("4")
        assert result["buy_dollar_volume"] == Decimal("50")
        assert result["sell_dollar_volume"] == Decimal("24")
        assert result["insiders_buying_count"] == 1
        assert result["insiders_selling_count"] == 1

    def test_excludes_transactions_outside_the_window(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 1, 1), code="P", shares=Decimal("100"), price=Decimal("5")),  # >3mo ago
            _tx(2, owner_cik="A2", transaction_date=date(2026, 8, 20), code="P", shares=Decimal("10"), price=Decimal("5")),  # in window
        ]
        result = insider_summary.compute_window_summary(rows, 3, as_of=self.AS_OF)
        assert result["shares_bought"] == Decimal("10")
        assert result["insiders_buying_count"] == 1

    def test_counts_distinct_insiders_not_transactions(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 8, 1), code="P", shares=Decimal("10"), price=Decimal("5")),
            _tx(2, owner_cik="A1", transaction_date=date(2026, 8, 15), code="P", shares=Decimal("20"), price=Decimal("5")),
        ]
        result = insider_summary.compute_window_summary(rows, 3, as_of=self.AS_OF)
        assert result["shares_bought"] == Decimal("30")  # both transactions summed
        assert result["insiders_buying_count"] == 1  # but only one distinct person

    def test_largest_purchase_and_sale_by_dollar_value_not_share_count(self):
        rows = [
            _tx(1, owner_cik="A1", owner_name="Small Buyer", transaction_date=date(2026, 8, 1), code="P",
                shares=Decimal("1000"), price=Decimal("1")),  # $1,000
            _tx(2, owner_cik="A2", owner_name="Big Buyer", transaction_date=date(2026, 8, 2), code="P",
                shares=Decimal("10"), price=Decimal("500")),  # $5,000 -- fewer shares, bigger value
            _tx(3, owner_cik="A3", owner_name="Seller", transaction_date=date(2026, 8, 3), code="S",
                shares=Decimal("5"), price=Decimal("100")),  # $500
        ]
        result = insider_summary.compute_window_summary(rows, 3, as_of=self.AS_OF)
        assert result["largest_purchase_owner_name"] == "Big Buyer"
        assert result["largest_purchase_value"] == Decimal("5000")
        assert result["largest_sale_owner_name"] == "Seller"
        assert result["largest_sale_value"] == Decimal("500")

    def test_no_transactions_in_window_gives_real_zeros_and_null_largest(self):
        result = insider_summary.compute_window_summary([], 3, as_of=self.AS_OF)
        assert result["shares_bought"] == Decimal("0")
        assert result["shares_sold"] == Decimal("0")
        assert result["buy_dollar_volume"] == Decimal("0")
        assert result["insiders_buying_count"] == 0
        assert result["largest_purchase_owner_name"] is None
        assert result["largest_purchase_value"] is None

    def test_transaction_missing_price_counts_toward_shares_but_not_dollar_volume_or_largest(self):
        rows = [
            _tx(1, owner_cik="A1", owner_name="No Price", transaction_date=date(2026, 8, 1), code="P",
                shares=Decimal("50"), price=None),
        ]
        result = insider_summary.compute_window_summary(rows, 3, as_of=self.AS_OF)
        assert result["shares_bought"] == Decimal("50")
        assert result["buy_dollar_volume"] == Decimal("0")
        assert result["largest_purchase_owner_name"] is None  # no priced transaction to be "largest"


@pytest.mark.unit
class TestComputeClusterSignal:
    AS_OF = date(2026, 8, 29)

    def test_no_buys_is_null_not_zero(self):
        rows = [_tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="S")]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] is None
        assert result["cluster_buy_window_start"] is None
        assert result["cluster_buy_window_end"] is None

    def test_single_buyer_gives_count_one_not_a_cluster(self):
        rows = [_tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="P")]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] == 1

    def test_three_distinct_insiders_within_7_days_is_a_real_cluster(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="P"),
            _tx(2, owner_cik="A2", transaction_date=date(2026, 6, 4), code="P"),
            _tx(3, owner_cik="A3", transaction_date=date(2026, 6, 7), code="P"),  # 6 days after A1 -- still in window
        ]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] == 3
        assert result["cluster_buy_window_start"] == date(2026, 6, 1)
        assert result["cluster_buy_window_end"] == date(2026, 6, 7)

    def test_buys_8_days_apart_are_not_one_cluster(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="P"),
            _tx(2, owner_cik="A2", transaction_date=date(2026, 6, 9), code="P"),  # 8 days later -- outside a 7-day window
        ]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] == 1

    def test_same_owner_buying_twice_in_window_counts_once(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="P"),
            _tx(2, owner_cik="A1", transaction_date=date(2026, 6, 3), code="P"),
            _tx(3, owner_cik="A2", transaction_date=date(2026, 6, 4), code="P"),
        ]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] == 2  # A1 (either transaction) + A2, not 3

    def test_sells_and_grants_never_count_toward_a_buy_cluster(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="P"),
            _tx(2, owner_cik="A2", transaction_date=date(2026, 6, 2), code="S"),
            _tx(3, owner_cik="A3", transaction_date=date(2026, 6, 3), code="A"),
        ]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] == 1

    def test_picks_the_earliest_window_on_a_tie(self):
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2026, 6, 1), code="P"),
            _tx(2, owner_cik="A2", transaction_date=date(2026, 6, 2), code="P"),
            _tx(3, owner_cik="A3", transaction_date=date(2026, 8, 1), code="P"),
            _tx(4, owner_cik="A4", transaction_date=date(2026, 8, 2), code="P"),
        ]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] == 2
        assert result["cluster_buy_window_start"] == date(2026, 6, 1)  # first 2-buyer window, not the August one

    def test_ignores_a_cluster_older_than_12_months_even_if_rows_contain_it(self):
        # Real bug found live 2026-08-29: core.insider_transaction is NOT
        # actually bounded to 12 months for every row despite
        # _load_transactions_for_company's docstring claiming it is (47%
        # of real rows have a filing_date older than 12 months). This
        # function must defend itself rather than trust that claim.
        rows = [
            _tx(1, owner_cik="A1", transaction_date=date(2008, 10, 8), code="P"),
            _tx(2, owner_cik="A2", transaction_date=date(2008, 10, 9), code="P"),
            _tx(3, owner_cik="A3", transaction_date=date(2008, 10, 10), code="P"),
        ]
        result = insider_summary.compute_cluster_signal(rows, as_of=self.AS_OF)
        assert result["cluster_buy_max_insiders"] is None  # a real 2008 cluster must not surface as current


@pytest.mark.unit
class TestUpdateInsiderSummaryForCompany:
    """Verifies the orchestration writes exactly 1 ownership row + 3
    window rows with correctly-shaped keys, via a fake connection
    (same PriceConnection-style pattern as test_price_metrics.py)."""

    class _FakeCursor:
        def __init__(self, conn):
            self.conn = conn

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql, params=()):
            self.conn.executed.append((" ".join(sql.split()), params))

        def executemany(self, sql, rows):
            self.conn.window_rows.extend(dict(row) for row in rows)

    class _FakeConnection:
        def __init__(self):
            self.executed = []
            self.window_rows = []

        def cursor(self):
            return TestUpdateInsiderSummaryForCompany._FakeCursor(self)

        def commit(self):
            pass

    def test_writes_one_ownership_row_and_three_window_rows(self, monkeypatch):
        from datetime import timedelta

        rows = [
            _tx(1, owner_cik="A1", transaction_date=date.today() - timedelta(days=5), code="P",
                shares=Decimal("10"), price=Decimal("5"), shares_owned_following=Decimal("100")),
        ]
        monkeypatch.setattr(insider_summary, "_load_transactions_for_company", lambda _conn, _cid: rows)
        monkeypatch.setattr(insider_summary, "_resolve_shares_outstanding", lambda _conn, _cid, _concept: (Decimal("1000"), [1]))

        conn = self._FakeConnection()
        stats = insider_summary.update_insider_summary_for_company(conn, 42, concept_id_arg := 7)

        assert stats["transactions_considered"] == 1
        assert stats["windows_written"] == 3
        assert len(conn.window_rows) == 3
        assert {r["window_months"] for r in conn.window_rows} == {3, 6, 12}
        assert all(r["company_id"] == 42 for r in conn.window_rows)
        # every window row includes real shares/$ volume for the 1 real transaction
        for r in conn.window_rows:
            assert r["shares_bought"] == Decimal("10")
            assert r["buy_dollar_volume"] == Decimal("50")
