"""ttm / expanded_metrics / price_metrics input loaders behind serve.shown_cell_path@1 (one-display-path plan step 5, M3).
Flag off: the SQL and result are exactly today's (analytics.canonical_fact, no shown filter). Flag on: the same loader
reads analytics.shown_cell restricted to cell_state = 'value'; an unproven cell is absent from the view, so the loader
returns nothing and the metric is null with its existing reason. The view (draft 0135) is faked as the rows it returns."""

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper import expanded_metrics, price_metrics, shown_source, ttm
from scrooner_pipeline.common import rule_flags

RULE = shown_source.SHOWN_CELL_PATH_RULE
D = Decimal


class FakeConn:
    def __init__(self, rows):
        self.rows, self.sql = rows, []

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.sql.append(sql)

    def fetchall(self):
        return list(self.rows)

    def fetchone(self):
        return self.rows[0] if self.rows else None


@pytest.fixture(autouse=True)
def _flag_off(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)


def _on(monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, RULE)


def _uses_facts(conn):
    return "analytics.canonical_fact cf" in conn.sql[0]


def _uses_shown(conn):
    return (
        "analytics.shown_cell cf" in conn.sql[0]
        and "cf.cell_state = 'value'" in conn.sql[0]
    )


TTM_ROW = (2024, "FY", D("100"), [1], date(2024, 1, 1), date(2024, 12, 31), 5, False)


@pytest.mark.unit
def test_ttm_flag_off_is_canonical_fact_and_unchanged():
    conn = FakeConn([TTM_ROW])
    out = ttm._load_company_facts(conn, 1, 9)
    assert _uses_facts(conn) and "shown_cell" not in conn.sql[0]
    assert out[(2024, "FY")] == (D("100"), [1], date(2024, 1, 1), date(2024, 12, 31))


@pytest.mark.unit
def test_ttm_flag_on_reads_the_shown_view_and_unproven_is_absent(monkeypatch):
    _on(monkeypatch)
    conn = FakeConn([])  # the view omits an unproven cell
    out = ttm._load_company_facts(conn, 1, 9)
    assert _uses_shown(conn) and not _uses_facts(conn)
    assert dict(out) == {} and out.durations == []
    assert ttm._ttm_sum(out, 2024, "Q4") == (
        None,
        [],
    )  # null; callers write their incomplete:* reason
