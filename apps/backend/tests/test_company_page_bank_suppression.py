"""Bank applicability on the company page (2026-10-19): a bank's suppressed
metrics, statement rows, FY history and peer cells come back null with a
stated reason; a non-bank's page is unchanged."""

import copy

import pytest

import company_page
from company_page import (
    get_company_page_data,
    suppress_bank_metrics,
    suppress_bank_statement,
)

METRICS = [
    {
        "metric_name": "fcf_yield",
        "value": "0.406",
        "period_label": "TTM",
        "period_end": "2026-06-30",
        "is_null_reason": None,
    },
    {
        "metric_name": "roe",
        "value": "0.11",
        "period_label": "TTM",
        "period_end": "2026-06-30",
        "is_null_reason": None,
    },
    {
        "metric_name": "net_interest_income",
        "value": "-28575000",
        "period_label": "Q2",
        "period_end": "2026-06-30",
        "is_null_reason": None,
    },
    {
        "metric_name": "gross_margin",
        "value": None,
        "period_label": "FY",
        "period_end": "2025-12-31",
        "is_null_reason": "incomplete:gross_profit_resolved",
    },
]


@pytest.mark.unit
def test_bank_metrics_are_nulled_with_the_stated_reason():
    out = {
        m["metric_name"]: m for m in suppress_bank_metrics(copy.deepcopy(METRICS), True)
    }
    assert out["fcf_yield"]["value"] is None
    assert out["fcf_yield"]["is_null_reason"] == "not applicable to banks"
    assert out["net_interest_income"]["value"] is None
    assert (
        out["net_interest_income"]["is_null_reason"]
        == "bank net interest income mapping pending"
    )
    # the wrong reason text a bank used to get is replaced
    assert out["gross_margin"]["is_null_reason"] == "not applicable to banks"
    # ROE is kept, value and all
    assert out["roe"]["value"] == "0.11" and out["roe"]["is_null_reason"] is None
    # a suppressed metric with no stored row still shows the reason
    assert out["piotroski_f_score"]["value"] is None
    assert out["piotroski_f_score"]["is_null_reason"] == "not applicable to banks"
    assert out["price_to_sales"]["is_null_reason"] == "bank revenue definition pending"


@pytest.mark.unit
def test_non_bank_metrics_are_returned_unchanged():
    original = copy.deepcopy(METRICS)
    assert suppress_bank_metrics(copy.deepcopy(METRICS), False) == original


@pytest.mark.unit
def test_bank_statement_rows_are_nulled_with_reason_and_others_untouched():
    statement = {
        "periods": [
            {"fiscal_year": 2025, "fiscal_period": "FY", "period_end": "2025-12-31"}
        ],
        "lines": [
            {"label": "Revenue", "values": ["138566000000"]},
            {"label": "Operating Income", "values": ["72814000"]},
            {"label": "Net Income", "values": ["1"]},
        ],
    }
    out = suppress_bank_statement(statement, True)
    revenue, operating, net_income = out["lines"]
    assert revenue == {
        "label": "Revenue",
        "values": [None],
        "suppressed_reason": "bank revenue definition pending",
    }
    assert operating["values"] == [None]
    assert operating["suppressed_reason"] == "not applicable to banks"
    assert net_income == {"label": "Net Income", "values": ["1"]}
    # input not mutated; non-bank identical
    assert statement["lines"][0]["values"] == ["138566000000"]
    assert suppress_bank_statement(statement, False) is statement


class _Cursor:
    def __init__(self, row):
        self.row = row

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.sql = sql

    def fetchone(self):
        return self.row


class _Conn:
    def __init__(self, row):
        self.cursor_obj = _Cursor(row)

    def cursor(self):
        return self.cursor_obj


def _row(is_bank: bool):
    statements = [
        {
            "statement": "income_statement",
            "display_order": 1,
            "display_label": "Revenue",
            "fiscal_year": 2025,
            "fiscal_period": "FY",
            "period_end": "2025-12-31",
            "value": "100",
        },
        {
            "statement": "income_statement",
            "display_order": 9,
            "display_label": "Net Income",
            "fiscal_year": 2025,
            "fiscal_period": "FY",
            "period_end": "2025-12-31",
            "value": "10",
        },
    ]
    history = [
        {"metric_name": "roic", "value": "0.2", "period_end": "2025-12-31"},
        {"metric_name": "roe", "value": "0.1", "period_end": "2025-12-31"},
    ]
    return (
        {"id": 1, "ticker": "TST", "is_bank": is_bank},
        copy.deepcopy(METRICS),
        statements,
        [],
        [],
        [],
        [],
        None,
        None,
        [],
        None,
        history,
        [],
        None,
        [],
        None,
        None,
        [],
        [],
    )


@pytest.mark.unit
def test_company_page_bank_vs_industrial_end_to_end():
    bank = get_company_page_data(_Conn(_row(True)), "tst")
    assert bank["metrics"]["fcf_yield"]["value"] is None
    assert bank["metrics"]["fcf_yield"]["is_null_reason"] == "not applicable to banks"
    assert bank["metrics"]["roe"]["value"] == "0.11"
    revenue = next(
        l for l in bank["incomeStatement"]["lines"] if l["label"] == "Revenue"
    )
    assert revenue["values"] == [None] and revenue["suppressed_reason"]
    assert "roic" not in bank["metricHistory"] and "roe" in bank["metricHistory"]

    industrial = get_company_page_data(_Conn(_row(False)), "tst")
    assert industrial["metrics"]["fcf_yield"]["value"] == "0.406"
    assert industrial["metrics"]["fcf_yield"]["is_null_reason"] is None
    revenue = next(
        l for l in industrial["incomeStatement"]["lines"] if l["label"] == "Revenue"
    )
    assert revenue == {"label": "Revenue", "values": ["100"]}
    assert industrial["metricHistory"]["roic"] == ["0.2"]


@pytest.mark.unit
def test_query_carries_the_bank_flag_and_filters_bank_peer_cells_in_sql():
    sql = company_page._QUERY
    assert sql.count("as is_bank") == 2  # selected company and peers
    assert "'is_bank', company.is_bank" in sql
    # a bank peer's suppressed peer-table metrics are excluded; ROE is not
    assert (
        "not (p.is_bank and md.metric_name in ('roic', 'revenue_growth_3y_cagr', 'net_margin'))"
        in sql
    )
