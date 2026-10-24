"""AC-1 interim: the ten total-debt consumers are hidden with 'definition pending accountant review'."""

from __future__ import annotations

from datetime import date
from decimal import Decimal as D

import pytest

from scrooner_pipeline.common import cell_blank_reason as cb
from scrooner_pipeline.mapper import debt_metrics_pending as g

ON = {"SCROONER_RULES_ENABLED": g.RULE_ID}


class _Cur:
    def __init__(self, c):
        self.c, self.res = c, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append((sql, params))
        if sql.startswith("select id, cik from core.company"):
            self.res = [(1, "0000320193"), (2, "0000000002")]
        elif "from analytics.metric_value mv" in sql:
            fy = (date(2025, 1, 1), date(2025, 12, 31))
            self.res = [
                (11, 1, "debt_to_equity", "FY", *fy, D("1.5")),
                (12, 1, "roic", "TTM", date(2025, 7, 1), date(2025, 12, 31), D("0.2")),
                (13, 1, "net_cash", "Q2", date(2025, 4, 1), date(2025, 6, 30), D("5")),
                (
                    14,
                    1,
                    "zero_debt",
                    "FY",
                    date(2025, 12, 31),
                    date(2025, 12, 31),
                    D("0"),
                ),
            ]
        else:
            self.res = []

    def fetchall(self):
        return self.res


class _Conn:
    def __init__(self):
        self.sql = []

    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def writes(self):
        return [s for s, _ in self.sql if s.startswith(("update", "delete", "insert"))]


def test_the_ten_metrics_are_exactly_the_cards_list():
    assert set(g.METRICS) == {
        "debt_to_equity", "net_cash", "net_cash_per_share", "net_debt_ebitda", "debt_to_ebitda",
        "ev_ebitda", "ev_sales", "roic", "piotroski_f_score", "zero_debt",
    }  # fmt: skip


def test_flag_off_is_a_noop():
    c = _Conn()
    assert (
        g.apply_debt_metrics_pending(c, environ={})["skipped"] == "rule_off"
        and c.sql == []
    )


def test_dry_run_writes_nothing_and_counts_by_metric():
    c = _Conn()
    out = g.apply_debt_metrics_pending(c, dry_run=True, environ={})
    assert (
        c.writes() == []
        and out["cells_hidden"] == 4
        and out["roic"] == 1
        and out["companies_hidden"] == 1
    )
    assert all(p.after is None and p.reason == g.REASON_CODE for p in out["planned"])


def test_live_updates_only_the_listed_row_ids_and_stores_definition_pending_reasons():
    c, store = _Conn(), cb.InMemoryBlankReasonStore()
    g.apply_debt_metrics_pending(c, environ=ON, reason_store=store, run_id="r1")
    ((sql, params),) = [(s, p) for s, p in c.sql if s.startswith("update")]
    assert (
        "set value = null, is_null_reason = %s" in sql and "where id = any(%s)" in sql
    )
    assert params == (g.REASON_TEXT, [11, 12, 13, 14])
    rows = {r.data_point: r for r in store.all()}
    assert {r.defect_class for r in rows.values()} == {"definition_pending"}
    assert {r.owner for r in rows.values()} == {"accountant"} and {
        r.reason_code for r in rows.values()
    } == {g.REASON_CODE}
    assert (
        rows["debt_to_equity"].period_grain == "FY"
        and rows["roic"].period_grain == "TTM"
    )
    assert (
        rows["net_cash"].period_grain == "Q" and rows["zero_debt"].period_grain == "I"
    )
    assert rows["roic"].to_store_row().defect_class == "definition_pending"


def test_live_without_a_reason_store_refuses():
    with pytest.raises(RuntimeError):
        g.apply_debt_metrics_pending(_Conn(), environ=ON)


def test_reason_code_cannot_be_the_class_name():
    with pytest.raises(ValueError):
        cb.BlankReason(1, "roic", "FY", date(2025, 1, 1), date(2025, 12, 31), "latest", g.RULE_ID, "definition_pending",
                       owner="accountant", defect_class="definition_pending")  # fmt: skip
