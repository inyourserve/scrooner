from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import calculate


class MetricCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.conn.executed.append((" ".join(sql.split()), params))

    def executemany(self, sql, rows):
        self.conn.rows.extend(dict(row) for row in rows)


class MetricConnection:
    def __init__(self):
        self.executed = []
        self.rows = []
        self.commits = 0

    def cursor(self):
        return MetricCursor(self)

    def commit(self):
        self.commits += 1


@pytest.mark.unit
def test_calculation_matches_instant_facts_by_end_date_and_scopes_delete(monkeypatch):
    period_end = date(2025, 9, 27)
    facts = {
        "by_period_id": {
            # net_income/revenue scaled to real dollar magnitude (2026-
            # 09-27's REVENUE_DENOMINATOR_MATERIALITY_FLOOR fix nulls any
            # revenue-denominated ratio under $1M -- these values were
            # originally 20/100, a toy-scale immaterial base under the
            # new floor); ratio (0.2) kept identical.
            1: {10: (Decimal("2000000"), [101])},
            2: {10: (Decimal("10000000"), [102])},
            3: {10: (Decimal("30"), [103])},
            4: {10: (Decimal("5"), [104])},
            5: {10: (Decimal("25"), [105])},
        },
        "by_end_date": {
            # Debt (concept 6) deliberately absent: the invested-capital
            # role must be incomplete even though equity exists.
            7: {period_end: (Decimal("40"), [107])},
            8: {period_end: (Decimal("10"), [108])},
        },
        "periods": {10: (date(2024, 9, 29), period_end, "FY")},
    }
    monkeypatch.setattr(calculate, "_load_canonical_facts", lambda _conn, _company: facts)
    targets = [
        {
            "id": 11,
            "name": "net_margin",
            "inputs": [("net_income", 1, "numerator", False), ("revenue", 2, "denominator", False)],
        },
        {
            "id": 12,
            "name": "roic",
            "inputs": [
                ("operating_income", 3, "nopat_base", False),
                ("income_tax_expense", 4, "tax_rate_numerator", False),
                ("income_before_tax", 5, "tax_rate_denominator", False),
                ("total_debt", 6, "invested_capital_add", True),
                ("stockholders_equity", 7, "invested_capital_add", True),
                ("cash_and_equivalents", 8, "invested_capital_subtract", True),
            ],
        },
    ]
    conn = MetricConnection()

    stats = calculate.calculate_for_company(conn, 9, targets)
    by_metric = {row["metric_definition_id"]: row for row in conn.rows}

    assert stats == {"computed": 1, "null": 1}
    assert by_metric[11]["value"] == Decimal("0.2")
    assert by_metric[11]["source_fact_ids"] == [101, 102]
    assert by_metric[12]["value"] is None
    assert by_metric[12]["is_null_reason"] == "incomplete:invested_capital_add"
    delete_sql, params = conn.executed[0]
    assert "company_id = %s" in delete_sql
    assert "metric_definition_id = any(%s)" in delete_sql
    assert "period_label != 'TTM'" in delete_sql
    assert params == (9, [11, 12])


@pytest.mark.unit
def test_quick_ratio_computes_when_inventory_genuinely_absent(monkeypatch):
    """2026-10-05 fix (doc/planning/51 Finding 13): quick_ratio's
    "subtract" role (inventory) is verified-safe to treat as a genuine
    zero when absent -- most real companies (software, services) hold
    none. Unlike the ROIC case above, a missing optional component must
    NOT null the whole metric here."""
    period_end = date(2025, 9, 27)
    facts = {
        "by_period_id": {
            # current_assets present, inventory absent entirely,
            # current_liabilities present -- quick_ratio should still
            # compute as (current_assets - 0) / current_liabilities.
            1: {10: (Decimal("5000000"), [101])},
            3: {10: (Decimal("2000000"), [103])},
        },
        "by_end_date": {},
        "periods": {10: (date(2024, 9, 29), period_end, "FY")},
    }
    monkeypatch.setattr(calculate, "_load_canonical_facts", lambda _conn, _company: facts)
    targets = [
        {
            "id": 20,
            "name": "quick_ratio",
            "inputs": [
                ("current_assets", 1, "add", False),
                ("inventory", 2, "subtract", False),
                ("current_liabilities", 3, "denominator", False),
            ],
        },
    ]
    conn = MetricConnection()

    stats = calculate.calculate_for_company(conn, 9, targets)
    by_metric = {row["metric_definition_id"]: row for row in conn.rows}

    assert stats == {"computed": 1, "null": 0}
    assert by_metric[20]["value"] == Decimal("2.5")  # 5,000,000 / 2,000,000


@pytest.mark.unit
def test_gross_margin_still_nulls_when_cost_of_revenue_absent(monkeypatch):
    """Confirms the quick_ratio fix is scoped per-metric, not per-shape:
    gross_margin shares the identical "sum_diff_ratio" shape but its own
    "subtract" role (cost_of_revenue) is NOT in ZERO_WHEN_ABSENT_CONCEPTS
    -- a missing cost_of_revenue is almost always a real data gap, not a
    genuine zero, and must still null the whole metric."""
    period_end = date(2025, 9, 27)
    facts = {
        "by_period_id": {
            # revenue present, cost_of_revenue absent entirely.
            1: {10: (Decimal("5000000"), [101])},
        },
        "by_end_date": {},
        "periods": {10: (date(2024, 9, 29), period_end, "FY")},
    }
    monkeypatch.setattr(calculate, "_load_canonical_facts", lambda _conn, _company: facts)
    targets = [
        {
            "id": 21,
            "name": "gross_margin",
            "inputs": [
                ("revenue", 1, "add", False),
                ("cost_of_revenue", 2, "subtract", False),
                ("revenue", 1, "denominator", False),
            ],
        },
    ]
    conn = MetricConnection()

    stats = calculate.calculate_for_company(conn, 9, targets)
    by_metric = {row["metric_definition_id"]: row for row in conn.rows}

    assert stats == {"computed": 0, "null": 1}
    assert by_metric[21]["value"] is None
    assert by_metric[21]["is_null_reason"] == "incomplete:subtract"

