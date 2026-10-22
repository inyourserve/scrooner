"""D-4: the yfinance tier of employee_count_resolved is switched off behind
rule employee_count.no_yfinance_tier@1 (default OFF = old behaviour byte-identical)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.common.cell_blank_reason import InMemoryBlankReasonStore
from scrooner_pipeline.common.rule_before_image import (
    read_before_image,
    write_before_image,
)
from scrooner_pipeline.mapper import concept_fallback as cf

RULE = cf.RULE_EMPLOYEE_NO_YFINANCE


class _Cur:
    def __init__(self, conn):
        self.c = conn
        self.res = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=()):
        sql = " ".join(sql.split())
        c = self.c
        c.sql.append(sql)
        if sql.startswith("select id, cik from core.company"):
            self.res = [(c.company_id, "0000000001")]
        elif sql.startswith("select id from analytics.canonical_concept"):
            self.res = [(10 if params[0] == "employee_count" else 11,)]
        elif sql.startswith("select period_id, value, source_fact_ids"):
            self.res = [(5, Decimal(c.xbrl), [9])] if c.xbrl else []
        elif "from core.employee_headcount_disclosure" in sql:
            self.res = [(date(2026, 2, 1), c.prose)] if c.prose else []
        elif sql.startswith("select y_employee_count"):
            self.res = [(c.yf,)] if c.yf else []
        elif sql.startswith("select id from core.period"):
            self.res = [(77,)]
        else:
            self.res = []

    def executemany(self, sql, rows):
        self.c.inserts.extend(rows)

    def fetchall(self):
        return self.res

    def fetchone(self):
        return self.res[0] if self.res else None


class _Conn:
    def __init__(self, *, xbrl=0, prose=0, yf=0):
        self.company_id, self.xbrl, self.prose, self.yf = 1, xbrl, prose, yf
        self.sql: list[str] = []
        self.inserts: list[dict] = []

    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def rollback(self):
        pass

    def wrote(self):
        return any(s.startswith(("delete", "insert")) for s in self.sql) or bool(
            self.inserts
        )


def test_flag_off_keeps_yfinance_tier_unchanged():
    conn = _Conn(yf=1200)
    stats = cf.resolve_employee_count_fallback(conn, {"0000000001"}, environ={})
    assert stats["from_yfinance"] == 1 and stats["yfinance_skipped"] == 0
    assert [r["value"] for r in conn.inserts] == [Decimal(1200)]


def test_flag_on_skips_yfinance_and_records_reason():
    conn = _Conn(yf=1200)
    store = InMemoryBlankReasonStore()
    stats = cf.resolve_employee_count_fallback(
        conn,
        {"0000000001"},
        reason_store=store,
        run_id="r1",
        environ={"SCROONER_RULES_ENABLED": RULE},
    )
    assert (
        stats["from_yfinance"] == 0
        and stats["yfinance_skipped"] == 1
        and stats["still_null"] == 1
    )
    assert conn.inserts == []
    assert any(
        s.startswith("delete from analytics.canonical_fact") for s in conn.sql
    )  # old yfinance row removed
    (r,) = store.all()
    assert (r.reason_code, r.rule_id, r.data_point, r.state) == (
        "yfinance_tier_off",
        RULE,
        "employee_count_resolved",
        "not_in_template",
    )


def test_flag_on_keeps_xbrl_and_prose_tiers():
    for kw, expect in (
        ({"xbrl": 500, "yf": 1}, Decimal(500)),
        ({"prose": 700, "yf": 1}, Decimal(700)),
    ):
        conn = _Conn(**kw)
        cf.resolve_employee_count_fallback(
            conn, {"0000000001"}, environ={"SCROONER_RULES_ENABLED": RULE}
        )
        assert [r["value"] for r in conn.inserts] == [expect]


def test_dry_run_writes_nothing_and_returns_before_image(tmp_path):
    conn = _Conn(yf=1200)
    stats = cf.resolve_employee_count_fallback(
        conn, {"0000000001"}, dry_run=True, environ={}
    )
    assert not conn.wrote()
    (pc,) = stats["planned"]
    assert (pc.before, pc.after, pc.reason) == (Decimal(1200), None, "not_in_template")
    p = tmp_path / "bi.jsonl"
    assert write_before_image(p, stats["planned"]) == 1
    assert read_before_image(p) == stats["planned"]


def test_dry_run_does_not_flag_companies_with_a_real_source():
    conn = _Conn(prose=700, yf=1)
    assert (
        cf.resolve_employee_count_fallback(conn, {"0000000001"}, dry_run=True)[
            "planned"
        ]
        == []
    )


def test_no_core_period_created_when_tier_off():
    conn = _Conn(yf=1200)
    cf.resolve_employee_count_fallback(
        conn, {"0000000001"}, environ={"SCROONER_RULES_ENABLED": RULE}
    )
    assert not any("core.period" in s and s.startswith("insert") for s in conn.sql)
