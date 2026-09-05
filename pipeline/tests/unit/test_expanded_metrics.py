from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import expanded_metrics

from test_price_metrics import PriceConnection, quarterly


OUTPUT_NAMES = (
    "net_debt_ebitda", "institutional_ownership_pct", "share_dilution_trend",
    "cash_conversion_cycle", "ev_ebitda", "ev_sales", "peg_ratio",
    "buyback_yield", "total_shareholder_yield",
    # Added 2026-09-05 (financials display spec gap-fill).
    "ebitda_margin", "debt_to_ebitda", "fcf_per_share", "share_repurchases_pct_fcf", "dividends_pct_fcf",
)
DEPENDENCY_NAMES = (
    "ebitda", "market_cap", "trailing_pe", "eps_growth_yoy", "dividend_yield",
    "debtor_days", "inventory_days", "payables_days",
    "fcf",
)
METRIC_IDS = {name: idx for idx, name in enumerate(OUTPUT_NAMES + DEPENDENCY_NAMES, 1)}
CONCEPT_IDS = {
    # total_debt_resolved, not total_debt, since 2026-09-02 (doc 40) --
    # expanded_metrics.py now reads the fallback-merged concept.
    "total_debt_resolved": 101, "cash_and_equivalents": 102, "revenue": 103,
    "share_buybacks": 104, "shares_outstanding": 105, "dividends_paid": 106,
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
    monkeypatch.setattr(expanded_metrics, "_fcf_ttm", lambda _conn, _company, _metric: Decimal("50"))
    monkeypatch.setattr(expanded_metrics, "_latest_metric_value", lambda _conn, _company, metric: dependency_values.get(metric))
    monkeypatch.setattr(expanded_metrics, "_institutional_ownership_shares", lambda _conn, _company: Decimal("60"))
    monkeypatch.setattr(expanded_metrics, "_shares_outstanding_now_and_1y_ago", lambda *_args: (Decimal("100"), Decimal("80")))
    monkeypatch.setattr(
        expanded_metrics,
        "_load_quarterly_facts",
        lambda _conn, _company, concept: {103: quarterly("50", 10), 104: quarterly("5", 20), 106: quarterly("2", 30)}[concept],
    )
    conn = PriceConnection()

    stats = expanded_metrics.calculate_expanded_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    rows = {name: next(r for r in conn.rows if r["metric_definition_id"] == METRIC_IDS[name]) for name in OUTPUT_NAMES}

    assert stats == {"computed": 14, "null": 0}
    assert rows["net_debt_ebitda"]["value"] == Decimal("1.5")
    assert rows["institutional_ownership_pct"]["value"] == Decimal("0.6")
    assert rows["share_dilution_trend"]["value"] == Decimal("0.25")
    assert rows["cash_conversion_cycle"]["value"] == Decimal("75")
    assert rows["ev_ebitda"]["value"] == Decimal("51.5")
    assert rows["ev_sales"]["value"] == Decimal("5.15")
    assert rows["peg_ratio"]["value"] == Decimal("2")
    assert rows["buyback_yield"]["value"] == Decimal("0.02")
    # Changed 2026-09-05: total_shareholder_yield now sums dividends_ttm/
    # buybacks_ttm directly against market_cap (0.008 + 0.02) rather than
    # reading the separately-computed dividend_yield metric (was 0.03 in
    # this fixture) -- see expanded_metrics.py's own comment for why.
    assert rows["total_shareholder_yield"]["value"] == Decimal("-0.222")
    # Added 2026-09-05 (financials display spec gap-fill). revenue_ttm=200
    # (4x50), buybacks_ttm=20 (4x5), dividends_ttm=8 (4x2), ebitda_ttm=20
    # (mocked), fcf_ttm=50 (mocked), total_debt=40, shares_now=100.
    assert rows["ebitda_margin"]["value"] == Decimal("0.1")  # 20/200
    assert rows["debt_to_ebitda"]["value"] == Decimal("2")  # 40/20
    assert rows["fcf_per_share"]["value"] == Decimal("0.5")  # 50/100
    assert rows["share_repurchases_pct_fcf"]["value"] == Decimal("0.4")  # 20/50
    assert rows["dividends_pct_fcf"]["value"] == Decimal("0.16")  # 8/50


@pytest.mark.unit
def test_delete_scope_excludes_dependency_metric_ids(monkeypatch):
    """The real 2026-09-03 bug: metric_ids passed in includes both this
    module's real outputs AND the dependency metrics it only reads
    (market_cap, trailing_pe, dividend_yield, ebitda, fcf, debtor_days,
    inventory_days, payables_days) -- the delete must never touch the
    dependency IDs, since this module has no code path that recomputes
    them, and doing so silently and permanently wipes another module's
    already-correct data on every rerun."""
    monkeypatch.setattr(expanded_metrics, "_latest_instant_fact", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_load_shares_outstanding_fallback", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_ebitda_ttm", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_fcf_ttm", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_latest_metric_value", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_institutional_ownership_shares", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_shares_outstanding_now_and_1y_ago", lambda *_args: (None, None))
    monkeypatch.setattr(expanded_metrics, "_load_quarterly_facts", lambda *_args: {})
    conn = PriceConnection()

    expanded_metrics.calculate_expanded_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)

    delete_calls = [(sql, params) for sql, params in conn.executed if sql.strip().startswith("delete")]
    assert len(delete_calls) == 1
    _sql, params = delete_calls[0]
    deleted_ids = set(params[1])
    dependency_ids = {METRIC_IDS[name] for name in DEPENDENCY_NAMES}
    output_ids = {METRIC_IDS[name] for name in OUTPUT_NAMES}
    assert deleted_ids == output_ids
    assert deleted_ids.isdisjoint(dependency_ids)


@pytest.mark.unit
def test_expanded_price_metrics_null_when_market_cap_is_missing(monkeypatch):
    monkeypatch.setattr(expanded_metrics, "_latest_instant_fact", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_load_shares_outstanding_fallback", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_ebitda_ttm", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_fcf_ttm", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_latest_metric_value", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_institutional_ownership_shares", lambda *_args: None)
    monkeypatch.setattr(expanded_metrics, "_shares_outstanding_now_and_1y_ago", lambda *_args: (None, None))
    monkeypatch.setattr(expanded_metrics, "_load_quarterly_facts", lambda *_args: {})
    conn = PriceConnection()

    stats = expanded_metrics.calculate_expanded_metrics_for_company(conn, 1, METRIC_IDS, CONCEPT_IDS)
    rows = {r["metric_definition_id"]: r for r in conn.rows}

    assert stats == {"computed": 0, "null": 14}
    assert rows[METRIC_IDS["cash_conversion_cycle"]]["is_null_reason"] == "missing:debtor_days"
    for name in ("ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield", "total_shareholder_yield"):
        assert rows[METRIC_IDS[name]]["is_null_reason"] == "missing:market_cap"
    # Added 2026-09-05 -- all 5 new metrics are price-INDEPENDENT, so they
    # null for their own specific missing-input reasons, not market_cap.
    assert rows[METRIC_IDS["ebitda_margin"]]["is_null_reason"] == "missing:ebitda_ttm"
    assert rows[METRIC_IDS["debt_to_ebitda"]]["is_null_reason"] == "missing:total_debt"
    assert rows[METRIC_IDS["fcf_per_share"]]["is_null_reason"] == "missing:fcf_ttm"
    assert rows[METRIC_IDS["share_repurchases_pct_fcf"]]["is_null_reason"] == "missing:share_buybacks_ttm"
    assert rows[METRIC_IDS["dividends_pct_fcf"]]["is_null_reason"] == "missing:dividends_paid_ttm"
