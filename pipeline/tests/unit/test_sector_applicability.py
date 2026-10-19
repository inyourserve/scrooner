"""Bank applicability (common/sector_applicability.py): which values are
suppressed for a bank, with which reason, and that a non-bank is untouched."""

import pytest

from scrooner_pipeline.common.sector_applicability import (
    BANK_NII_PENDING,
    BANK_REVENUE_PENDING,
    BANK_SUPPRESSED_METRICS,
    BANK_SUPPRESSED_STATEMENT_LINES,
    NOT_APPLICABLE_TO_BANKS,
    apply_to_resolved,
    bank_predicate_sql,
    load_bank_company_ids,
    metric_suppression_reason,
    statement_line_suppression_reason,
)
from scrooner_pipeline.screener import query as screener_query
from scrooner_pipeline.screener.resolve import _suppress_for_banks


class FakeCursor:
    """Records executed SQL and answers by substring."""

    def __init__(self, answers: dict[str, list[tuple]]):
        self.answers = answers
        self.executed: list[tuple[str, object]] = []
        self._rows: list[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        text = str(sql)
        self.executed.append((text, params))
        self._rows = []
        for needle, rows in self.answers.items():
            if needle in text:
                self._rows = rows
                break

    def fetchall(self):
        return self._rows


class FakeConn:
    def __init__(self, answers):
        self.cur = FakeCursor(answers)

    def cursor(self):
        return self.cur


DECIDED_NOT_APPLICABLE = [
    "gross_margin", "operating_margin", "roic", "interest_coverage_ratio",
    "ev_ebitda", "net_debt_ebitda", "ebitda", "fcf", "fcf_yield", "fcf_margin",
    "net_cash", "net_cash_per_share", "debt_to_equity", "zero_debt", "ev_sales",
    "current_ratio", "quick_ratio", "working_capital", "inventory_days",
    "payables_days", "debtor_days", "cash_conversion_cycle", "piotroski_f_score",
]
DECIDED_REVENUE = [
    "price_to_sales", "net_margin", "pretax_margin", "revenue_growth_yoy",
    "revenue_growth_3y_cagr", "revenue_growth_5y_cagr", "revenue_growth_10y_cagr",
]
KEPT = [
    "roe", "roa", "diluted_eps", "eps_growth_yoy", "book_value_per_share",
    "price_to_book", "trailing_pe", "market_cap", "dividend_yield", "payout_ratio",
    "dps_growth_yoy", "buyback_yield", "total_shareholder_yield",
]


@pytest.mark.unit
def test_every_decided_metric_is_suppressed_with_the_decided_reason():
    for name in DECIDED_NOT_APPLICABLE:
        assert BANK_SUPPRESSED_METRICS[name] == NOT_APPLICABLE_TO_BANKS, name
    for name in DECIDED_REVENUE:
        assert BANK_SUPPRESSED_METRICS[name] == BANK_REVENUE_PENDING, name
    assert BANK_SUPPRESSED_METRICS["net_interest_income"] == BANK_NII_PENDING
    assert BANK_NII_PENDING == "bank net interest income mapping pending"
    assert BANK_REVENUE_PENDING == "bank revenue definition pending"
    assert NOT_APPLICABLE_TO_BANKS == "not applicable to banks"


@pytest.mark.unit
def test_kept_metrics_are_never_suppressed():
    for name in KEPT:
        assert name not in BANK_SUPPRESSED_METRICS, name
        assert metric_suppression_reason(name, True) is None


@pytest.mark.unit
def test_a_non_bank_is_never_suppressed_for_any_metric_or_line():
    for name in BANK_SUPPRESSED_METRICS:
        assert metric_suppression_reason(name, False) is None
    for label in BANK_SUPPRESSED_STATEMENT_LINES:
        assert statement_line_suppression_reason(label, False) is None


@pytest.mark.unit
def test_a_bank_gets_the_reason_for_each_suppressed_metric_and_line():
    assert metric_suppression_reason("fcf_yield", True) == "not applicable to banks"
    assert metric_suppression_reason("price_to_sales", True) == "bank revenue definition pending"
    assert statement_line_suppression_reason("Revenue", True) == "bank revenue definition pending"
    assert statement_line_suppression_reason("Operating Income", True) == "not applicable to banks"
    assert statement_line_suppression_reason("EBITDA", True) == "not applicable to banks"
    assert statement_line_suppression_reason("Net Income", True) is None


@pytest.mark.unit
def test_population_requires_sic_range_and_filed_tag_evidence_not_sic_alone():
    sql = bank_predicate_sql("c")
    assert "'6020'" in sql and "'6036'" in sql
    assert "NoninterestExpense" in sql and "'Deposits'" in sql
    # two independent evidence tests, so SIC alone can never satisfy it
    assert sql.count("exists (") == 2


@pytest.mark.unit
def test_apply_to_resolved_suppresses_bank_only_and_keeps_other_metrics():
    resolved = {
        (1, 10): {"value": 0.18, "period_label": "TTM", "period_end": "2026-06-30",
                  "is_null_reason": None, "formula_version": 1},   # bank fcf_yield
        (1, 11): {"value": 0.11, "period_label": "TTM", "period_end": "2026-06-30",
                  "is_null_reason": None, "formula_version": 1},   # bank roe (kept)
        (2, 10): {"value": 0.05, "period_label": "TTM", "period_end": "2026-06-30",
                  "is_null_reason": None, "formula_version": 1},   # industrial fcf_yield
    }
    changed = apply_to_resolved(resolved, {1}, {10: "not applicable to banks"})
    assert changed == 1
    assert resolved[(1, 10)]["value"] is None
    assert resolved[(1, 10)]["is_null_reason"] == "not applicable to banks"
    assert resolved[(1, 11)]["value"] == 0.11            # ROE kept
    assert resolved[(2, 10)]["value"] == 0.05            # industrial unaffected
    assert resolved[(2, 10)]["is_null_reason"] is None
    # idempotent
    assert apply_to_resolved(resolved, {1}, {10: "not applicable to banks"}) == 0


@pytest.mark.unit
def test_apply_to_resolved_does_not_invent_rows():
    resolved: dict = {}
    assert apply_to_resolved(resolved, {1}, {10: "x"}) == 0
    assert resolved == {}


@pytest.mark.unit
def test_load_bank_company_ids_scopes_to_given_ids_and_handles_empty():
    cur = FakeCursor({"core.company": [(7,), (9,)]})
    assert load_bank_company_ids(cur, [7, 8, 9]) == {7, 9}
    sql, params = cur.executed[0]
    assert "c.id = any(%s::bigint[])" in sql and params == ([7, 8, 9],)
    cur2 = FakeCursor({})
    assert load_bank_company_ids(cur2, []) == set()
    assert cur2.executed == []
    cur3 = FakeCursor({"core.company": [(1,)]})
    assert load_bank_company_ids(cur3) == {1}
    assert cur3.executed[0][1] is None


@pytest.mark.unit
def test_screener_resolve_nulls_a_bank_value_with_reason_and_leaves_an_industrial():
    result = {
        (1, 10): {"value": 0.18, "period_label": "TTM", "period_end": None,
                  "is_null_reason": None, "formula_version": 1},
        (2, 10): {"value": 0.05, "period_label": "TTM", "period_end": None,
                  "is_null_reason": None, "formula_version": 1},
    }
    conn = FakeConn({
        "analytics.metric_definition": [(10, "fcf_yield"), (11, "roe")],
        "core.company": [(1,)],
    })
    assert _suppress_for_banks(conn, result, [10, 11]) == 1
    assert result[(1, 10)]["value"] is None
    assert result[(1, 10)]["is_null_reason"] == "not applicable to banks"
    assert result[(2, 10)]["value"] == 0.05


@pytest.mark.unit
def test_screener_resolve_skips_the_bank_lookup_when_no_suppressed_metric_requested():
    conn = FakeConn({"analytics.metric_definition": [(11, "roe")]})
    assert _suppress_for_banks(conn, {}, [11]) == 0
    assert len(conn.cur.executed) == 1  # no bank query issued


@pytest.mark.unit
def test_screener_exclusion_names_the_reason_for_a_bank_only():
    excluded = {
        1: {"cik": "0000000001", "company_name": "Bank", "missing_metrics": ["fcf_yield", "roe"]},
        2: {"cik": "0000000002", "company_name": "Industrial", "missing_metrics": ["fcf_yield"]},
        3: {"cik": "0000000003", "company_name": "SIC bank, no bank evidence",
            "missing_metrics": ["fcf_yield"]},
    }
    conn = FakeConn({"core.company": [(1,)]})
    screener_query._annotate_bank_suppression(
        conn, excluded, {1: "6022", 2: "3571", 3: "6022"}
    )
    assert excluded[1]["suppressed_reasons"] == {"fcf_yield": "not applicable to banks"}
    assert "suppressed_reasons" not in excluded[2]
    assert "suppressed_reasons" not in excluded[3]       # SIC alone is not enough
    # the lookup was limited to SIC-range candidates
    assert conn.cur.executed[0][1] == ([1, 3],)


@pytest.mark.unit
def test_screener_exclusion_issues_no_query_when_no_bank_candidate():
    excluded = {2: {"cik": "2", "company_name": "Industrial", "missing_metrics": ["fcf_yield"]},
                1: {"cik": "1", "company_name": "Bank", "missing_metrics": ["roe"]}}
    conn = FakeConn({})
    screener_query._annotate_bank_suppression(conn, excluded, {1: "6022", 2: "3571"})
    assert conn.cur.executed == []
    assert "suppressed_reasons" not in excluded[1]   # roe is kept for banks


@pytest.mark.unit
def test_run_query_explains_a_bank_exclusion_and_leaves_an_industrial_match(monkeypatch):
    """Snapshot rows as the nightly rebuild now writes them: the bank's
    fcf_yield is null (suppressed), the industrial's is a real value."""
    from decimal import Decimal

    from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery

    identity = {"cik": "", "company_name": "", "sic_code": "6022", "sic_description": "",
                "sector": "", "status": "active", "ticker": ""}
    rows = [
        (1, {**identity, "cik": "0000000001", "company_name": "Bank"}, {}),
        (2, {**identity, "cik": "0000000002", "company_name": "Industrial", "sic_code": "3571"},
         {"fcf_yield": {"value": Decimal("0.10"), "period_label": "TTM",
                        "period_end": None, "formula_version": 1}}),
    ]
    monkeypatch.setattr(screener_query, "_select_snapshot_rows", lambda *a, **k: rows)
    conn = FakeConn({"core.company": [(1,)]})
    result = screener_query.run_query(
        conn,
        ScreenQuery(metric_predicates=[MetricPredicate(
            metric_name="fcf_yield", operator=">", value=Decimal("0.05"))]),
        dataset_version=1,
        catalog={"fcf_yield": 10},
    )
    assert [m["company_name"] for m in result["matched"]] == ["Industrial"]
    (excluded,) = result["excluded_missing_data"]
    assert excluded["company_name"] == "Bank"
    assert excluded["missing_metrics"] == ["fcf_yield"]
    assert excluded["suppressed_reasons"] == {"fcf_yield": "not applicable to banks"}


@pytest.mark.unit
def test_is_bank_sic_boundaries():
    from scrooner_pipeline.common.sector_applicability import is_bank_sic

    assert is_bank_sic("6020") and is_bank_sic("6022") and is_bank_sic("6036")
    assert not is_bank_sic("6019") and not is_bank_sic("6037")
    assert not is_bank_sic("6199") and not is_bank_sic("3571")
    assert not is_bank_sic(None) and not is_bank_sic("60250")
