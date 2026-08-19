from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import expanded_metrics

from test_price_metrics import PriceConnection, quarterly


OUTPUT_NAMES = (
    "net_debt_ebitda", "institutional_ownership_pct", "share_dilution_trend",
    "cash_conversion_cycle", "ev_ebitda", "ev_sales", "peg_ratio",
    "buyback_yield", "total_shareholder_yield",
)
DEPENDENCY_NAMES = (
    "ebitda", "market_cap", "trailing_pe", "eps_growth_yoy", "dividend_yield",
    "debtor_days", "inventory_days", "payables_days",
)
METRIC_IDS = {name: idx for idx, name in enumerate(OUTPUT_NAMES + DEPENDENCY_NAMES, 1)}
CONCEPT_IDS = {
    "total_debt": 101, "cash_and_equivalents": 102, "revenue": 103,
    "share_buybacks": 104, "shares_outstanding": 105,
}


@pytest.mark.unit
def test_all_expanded_composite_metrics_compute_with_expected_semantics(monkeypatch):
    instant = {
        101: (Decimal("40"), [1], None),
        102: (Decimal("10"), [2], None),
        105: (Decimal("100"), [3], None),
    }
    dependency_values = {
        METRIC_IDS["market_cap"]: Decimal("1000"),
        METRIC_IDS["trailing_pe"]: Decimal("20"),
        METRIC_IDS["eps_growth_yoy"]: Decimal("0.10"),
        METRIC_IDS["dividend_yield"]: Decimal("0.03"),
        METRIC_IDS["debtor_days"]: Decimal("45"),
        METRIC_IDS["inventory_days"]: Decimal("60"),
        METRIC_IDS["payables_days"]: Decimal("30"),
    }
    monkeypatch.setattr(expanded_metrics, "_latest_instant_fact", lambda _conn, _company, concept: instant.get(concept))
    monkeypatch.setattr(expanded_metrics, "_ebitda_ttm", lambda _conn, _company, _metric: Decimal("20"))
    monkeypatch.setattr(expanded_metrics, "_latest_metric_value", lambda _conn, _company, metric: dependency_values.get(metric))
    monkeypatch.setattr(expanded_metrics, "_institutional_ownership_shares", lambda _conn, _company: Decimal("60"))
    monkeypatch.setattr(expanded_metrics, "_shares_outstanding_now_and_1y_ago", lambda *_args: (Decimal("100"), Decimal("80")))
    monkeypatch.setattr(
        expanded_metrics,
        "_load_quarterly_facts",
        lambda _conn, _company, concept: quarterly("50", 10) if concept == 103 else quarterly("5", 20),
    )
    conn = PriceConnection()

    stats = expanded_metrics.calculate_expanded_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    rows = {name: next(r for r in conn.rows if r["metric_definition_id"] == METRIC_IDS[name]) for name in OUTPUT_NAMES}

    assert stats == {"computed": 9, "null": 0}
    assert rows["net_debt_ebitda"]["value"] == Decimal("1.5")
    assert rows["institutional_ownership_pct"]["value"] == Decimal("0.6")
    assert rows["share_dilution_trend"]["value"] == Decimal("0.25")
    assert rows["cash_conversion_cycle"]["value"] == Decimal("75")
    assert rows["ev_ebitda"]["value"] == Decimal("51.5")
    assert rows["ev_sales"]["value"] == Decimal("5.15")
    assert rows["peg_ratio"]["value"] == Decimal("2")
    assert rows["buyback_yield"]["value"] == Decimal("0.02")
    assert rows["total_shareholder_yield"]["value"] == Decimal("-0.20")


@pytest.mark.unit
def test_expanded_price_metrics_null_when_market_cap_is_missing(monkeypatch):
    monkeypatch.setattr(expanded_metrics, "_latest_instant_fact", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_load_shares_outstanding_fallback", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_ebitda_ttm", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_latest_metric_value", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_institutional_ownership_shares", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_shares_outstanding_now_and_1y_ago", lambda *_args: (None, None))
    conn = PriceConnection()

    stats = expanded_metrics.calculate_expanded_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    rows = {r["metric_definition_id"]: r for r in conn.rows}

    assert stats == {"computed": 0, "null": 9}
    assert rows[METRIC_IDS["cash_conversion_cycle"]]["is_null_reason"] == "missing:debtor_days"
    for name in ("ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield", "total_shareholder_yield"):
        assert rows[METRIC_IDS[name]]["is_null_reason"] == "missing:market_cap"
