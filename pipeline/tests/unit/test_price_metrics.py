from datetime import date, timedelta
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import price_metrics


class PriceCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.conn.executed.append((" ".join(sql.split()), params))

    def executemany(self, sql, rows):
        rows = [dict(row) for row in rows]
        self.conn.rows.extend(rows)
        self.conn.executemany_calls.append((" ".join(sql.split()), rows))


class PriceConnection:
    def __init__(self):
        self.executed = []
        self.rows = []
        self.executemany_calls = []

    def cursor(self):
        return PriceCursor(self)

    def commit(self):
        pass


METRIC_NAMES = ("market_cap", "trailing_pe", "price_to_sales", "price_to_book", "dividend_yield", "fcf_yield")
METRIC_IDS = {name: idx for idx, name in enumerate(METRIC_NAMES, 1)}
CONCEPT_IDS = {
    "diluted_eps": 10, "revenue": 11, "dividends_per_share": 12,
    "cfo": 13, "capex": 14, "shares_outstanding": 15, "stockholders_equity": 16,
}


def quarterly(value, first_fact_id):
    return {
        (2025, quarter): (Decimal(value), [first_fact_id + offset])
        for offset, quarter in enumerate(("Q1", "Q2", "Q3", "Q4"))
    }


def install_price_inputs(monkeypatch, price):
    by_concept = {
        10: quarterly("2", 100),
        11: quarterly("25", 110),
        12: quarterly("0.25", 120),
        13: quarterly("10", 130),
        14: quarterly("2", 140),
    }
    monkeypatch.setattr(price_metrics, "_load_latest_price", lambda _conn, _company: (price, date.today()))
    monkeypatch.setattr(price_metrics, "_load_quarterly_facts", lambda _conn, _company, concept: by_concept[concept])
    monkeypatch.setattr(
        price_metrics,
        "_latest_instant_fact",
        lambda _conn, _company, concept: (
            (Decimal("100"), [150], date(2025, 9, 27))
            if concept == 15
            else (Decimal("200"), [160], date(2025, 9, 27))
        ),
    )


@pytest.mark.unit
def test_all_six_price_metrics_compute_with_decimal_lineage(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    rows = {name: next(r for r in conn.rows if r["metric_definition_id"] == METRIC_IDS[name]) for name in METRIC_NAMES}

    assert stats == {"computed": 6, "null": 0}
    assert rows["market_cap"]["value"] == Decimal("1000")
    assert rows["trailing_pe"]["value"] == Decimal("1.25")
    assert rows["price_to_sales"]["value"] == Decimal("10")
    assert rows["price_to_book"]["value"] == Decimal("5")
    assert rows["dividend_yield"]["value"] == Decimal("0.1")
    assert rows["fcf_yield"]["value"] == Decimal("0.032")
    assert rows["fcf_yield"]["source_fact_ids"] == [150, 130, 131, 132, 133, 140, 141, 142, 143]
    delete_sql, _params = conn.executed[0]
    assert "period_label = 'TTM'" in delete_sql


@pytest.mark.unit
def test_non_positive_price_fails_closed_instead_of_dividing(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("0"))
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)

    assert stats == {"computed": 0, "null": 6}
    assert {row["is_null_reason"] for row in conn.rows} == {"invalid:non_positive_price"}


@pytest.mark.unit
def test_missing_price_null_rows_still_satisfy_required_period_dates(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    monkeypatch.setattr(price_metrics, "_load_latest_price", lambda _conn, _company: None)
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)

    assert stats == {"computed": 0, "null": 6}
    assert {row["is_null_reason"] for row in conn.rows} == {"missing:real_price"}
    assert all(isinstance(row["period_start"], date) for row in conn.rows)
    assert all(row["period_start"] == row["period_end"] for row in conn.rows)


@pytest.mark.unit
def test_stale_price_fails_closed_instead_of_valuing_at_an_old_bar(monkeypatch):
    install_price_inputs(monkeypatch, Decimal("10"))
    old_bar = date.today() - timedelta(days=price_metrics.MAX_PRICE_AGE_DAYS + 1)
    monkeypatch.setattr(price_metrics, "_load_latest_price", lambda _conn, _company: (Decimal("10"), old_bar))
    conn = PriceConnection()

    stats = price_metrics.calculate_price_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)

    assert stats == {"computed": 0, "null": 6}
    assert {row["is_null_reason"] for row in conn.rows} == {"stale:real_price"}
    assert all(row["period_end"] == old_bar for row in conn.rows)
