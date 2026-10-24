"""Balance-sheet identity fallback, corrected: liabilities = assets - total equity (incl NCI) - temporary equity.
Cells: WMT 2026-07-31 (0000104169-26-000154 R4), AT&T 2026-06-30 (0000732717-26-000297 R5),
VLO 2020-12-31 (0001035002-21-000051 R2), values in $M."""

from __future__ import annotations

import json
from decimal import Decimal

import pytest
from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import balance_identity as bi
from scrooner_pipeline.mapper import concept_fallback as cf

M = Decimal(1_000_000)


def D(**kw):
    return {k: Decimal(str(v)) * M for k, v in kw.items()}


def amt(target, assets, other, tag, **adj):
    return bi.identity_amount(
        target, Decimal(assets) * M, Decimal(other) * M, tag,
        {getattr(bi, k): Decimal(str(v)) * M for k, v in adj.items()},
    )  # fmt: skip


def test_wmt_parent_equity_with_nci_total_and_redeemable_nci_gives_the_filing_liabilities():
    # filing: 293,914 - 104,506 (total equity) - 293 (redeemable NCI) = 189,115; legacy stored 202,237
    a = amt("total_liabilities_resolved", 293914, 97945, "StockholdersEquity",
            NCI=6561, NCI_INCLUSIVE_EQUITY=104506, TEMP_REDEEMABLE_NCI=293)  # fmt: skip
    assert a.value == Decimal(189115) * M
    assert a.basis == "filed_nci_inclusive_total+temp_one_line"


def test_att_equity_input_is_already_nci_inclusive_so_nci_is_not_counted_twice():
    # no parent-equity line on the face: the NCI-inclusive total is the input. legacy 319,920 added 17,995
    a = amt("total_liabilities_resolved", 500000, 198075, bi.NCI_INCLUSIVE_EQUITY,
            NCI=15990, TEMP_PARENT=2005)  # fmt: skip
    assert a.value == Decimal(299920) * M
    assert a.basis == "equity_nci_inclusive+temp_one_line"
    assert a.equity_tag == bi.NCI_INCLUSIVE_EQUITY


def test_vlo_2020_total_equity_including_nci_is_subtracted():
    # stored 33,814 = 51,774 - 18,801 + 841; the face gives total equity 19,642 -> 32,132
    a = amt("total_liabilities_resolved", 51774, 18801, "StockholdersEquity", NCI=841)
    assert a.value == Decimal(32132) * M and a.basis == "parent_equity+nci"


def test_parent_equity_without_any_nci_fact_is_not_adjusted():
    a = amt("total_liabilities_resolved", 1000, 400, "StockholdersEquity")
    assert a.value == Decimal(600) * M and a.basis == "parent_equity_no_nci_filed"


def test_temporary_equity_is_subtracted_and_a_deficit_spac_balance_sheet_stays_correct():
    # permanent equity -20 (deficit), redeemable common in temporary equity 95: liabilities 100 + 20 - 95 = 25
    a = amt(
        "total_liabilities_resolved", 100, -20, "StockholdersEquity", TEMP_PARENT=95
    )
    assert a.value == Decimal(25) * M


def test_temp_equity_including_nci_replaces_the_two_parts_instead_of_adding_to_them():
    a = amt("total_liabilities_resolved", 1000, 400, "StockholdersEquity",
            TEMP_INCL=70, TEMP_PARENT=50, TEMP_REDEEMABLE_NCI=10)  # fmt: skip
    assert a.value == Decimal(530) * M
    b = amt("total_liabilities_resolved", 1000, 400, "StockholdersEquity", TEMP_PARENT=50, TEMP_REDEEMABLE_NCI=10)  # fmt: skip
    assert b.value == Decimal(540) * M and "temp_parent+redeemable_nci" in b.basis


def test_the_equity_direction_subtracts_nci_and_temporary_equity():
    a = amt("stockholders_equity_resolved", 1000, 600, None, NCI=30, TEMP_PARENT=20)
    assert a.value == Decimal(350) * M


# ------------------------------------------------------------------ planner with a scripted cursor
class Cur:
    def __init__(self, tables):
        self.t, self.rows, self.rowcount = tables, [], 0
        self.sql = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.sql.append((sql, params))
        s = " ".join(sql.split()).lower()
        for key, rows in self.t.items():
            if key in s:
                self.rows = rows
                self.rowcount = 1
                return
        raise AssertionError(s)

    def fetchall(self):
        return self.rows


class Conn:
    def __init__(self, tables):
        self.cur = Cur(tables)
        self.commits = 0

    def cursor(self):
        return self.cur

    def commit(self):
        self.commits += 1


from datetime import date

A, L, E = 1, 2, 3
WMT_TABLES = {
    "from analytics.canonical_concept": [("total_assets_resolved", A), ("total_liabilities_resolved", L), ("stockholders_equity_resolved", E)],
    "from core.concept where tag": [(10, "MinorityInterest"), (11, bi.NCI_INCLUSIVE_EQUITY), (12, bi.TEMP_REDEEMABLE_NCI), (13, "StockholdersEquity")],
    "from core.company": [(1134, "0000104169")],
    "from analytics.canonical_fact cf join core.period": [
        (1134, 77, A, Decimal(293914) * M, [100], date(2026, 7, 31)),
        (1134, 77, E, Decimal(97945) * M, [200], date(2026, 7, 31)),
        (1134, 77, L, Decimal(202237) * M, [100, 200, 301], date(2026, 7, 31)),
        (1134, 78, A, Decimal(1000) * M, [101], date(2026, 4, 30)),
        (1134, 78, E, Decimal(400) * M, [201], date(2026, 4, 30)),
        (1134, 79, A, Decimal(1000) * M, [102], date(2026, 1, 31)),
        (1134, 79, E, Decimal(400) * M, [202], date(2026, 1, 31)),
        (1134, 79, L, Decimal(555) * M, [999], date(2026, 1, 31)),  # a real Liabilities tag value: untouched
        (1134, 80, A, Decimal(1000) * M, [103], date(2025, 10, 31)),
        (1134, 80, E, Decimal(400) * M, [203], date(2025, 10, 31)),
        (1134, 80, L, Decimal(777) * M, [103, 998], date(2025, 10, 31)),  # carries the assets ids but not the equity ids
        (1134, 82, A, Decimal(1000) * M, [105], date(2025, 4, 30)),
        (1134, 82, E, Decimal(400) * M, [205], date(2025, 4, 30)),
        (1134, 82, L, Decimal(777) * M, [205, 997], date(2025, 4, 30)),  # carries the equity ids but not the assets ids
        (1134, 83, A, Decimal(1000) * M, [106], date(2025, 1, 31)),
        (1134, 83, E, Decimal(400) * M, [206, 207], date(2025, 1, 31)),
        (1134, 81, A, Decimal(1000) * M, [104], date(2025, 7, 31)),
        (1134, 81, E, Decimal(400) * M, [204], date(2025, 7, 31)),
        (1134, 81, L, Decimal(600) * M, [104, 204], date(2025, 7, 31)),  # derived and already correct: no change
    ],
    "from core.fact f where": [
        (1134, 77, 10, Decimal(6561) * M, 301), (1134, 77, 11, Decimal(104506) * M, 302), (1134, 77, 12, Decimal(293) * M, 303),
    ],
    "from core.fact f join core.concept": [(200, "StockholdersEquity"), (201, "StockholdersEquity"), (202, "StockholdersEquity"), (206, bi.NCI_INCLUSIVE_EQUITY), (207, "StockholdersEquity")],
}  # fmt: skip


def conn_sql(conn):
    return conn.cur.sql


def test_planner_replaces_a_row_this_fallback_wrote_fills_an_empty_cell_and_leaves_a_tag_value():
    plan_conn = Conn(WMT_TABLES)
    plan = bi.plan_identity(plan_conn, [1134])
    by = {p.period_end: p for p in plan}
    assert not any(k in by for k in ("2025-10-31", "2025-07-31", "2025-04-30"))
    assert by["2025-01-31"].basis == "equity_nci_inclusive"
    assert by["2025-01-31"].equity_tag == bi.NCI_INCLUSIVE_EQUITY
    assert set(by) == {
        "2025-01-31",
        "2026-07-31",
        "2026-04-30",
    }  # 2026-01-31 holds a real Liabilities tag value
    r = by["2026-07-31"]
    assert (r.kind, r.before, r.after) == (
        "replace",
        str(Decimal(202237) * M),
        str(Decimal(189115) * M),
    )
    assert r.equity_tag == "StockholdersEquity"
    assert r.legacy_adjustment == str(
        Decimal(6561 + 293) * M
    )  # what the legacy SQL added (not the inclusive total)
    # only authoritative adjustment facts are read
    assert any(
        "is_authoritative" in " ".join(q.split()).lower()
        for q, _ in conn_sql(plan_conn)
    )
    f = by["2026-04-30"]
    assert (f.kind, f.before, f.after) == ("fill", None, str(Decimal(600) * M))


def test_apply_updates_only_replacements_inserts_fills_and_writes_the_before_image(
    tmp_path,
):
    plan = bi.plan_identity(Conn(WMT_TABLES), [1134])
    conn = Conn(
        {
            **WMT_TABLES,
            "update analytics.canonical_fact": [],
            "insert into analytics.canonical_fact": [],
        }
    )
    n = bi.apply_identity(conn, plan, tmp_path / "img.jsonl")
    sqls = [" ".join(s.split()).lower() for s, _ in conn.cur.sql]
    assert n == 3 and conn.commits == 1
    assert (
        sum(s.startswith("update") for s in sqls) == 1
        and sum(s.startswith("insert") for s in sqls) == 2
    )
    assert not any("delete" in s for s in sqls)
    rows = [json.loads(x) for x in (tmp_path / "img.jsonl").read_text().splitlines()]
    assert {r["kind"] for r in rows} == {"replace", "fill"}


# ------------------------------------------------------------------ flag wiring
def test_rule_is_registered_default_off_and_has_a_dry_run():
    assert rule_flags.RULES[bi.RULE_ID].dry_run is True
    assert rule_flags.rule_mode(bi.RULE_ID, {}) == rule_flags.OFF


def test_flag_off_keeps_the_legacy_path_and_never_plans(monkeypatch):
    monkeypatch.delenv(rule_flags.ENV_ENABLED, raising=False)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)
    called = []
    monkeypatch.setattr(bi, "plan_identity", lambda *a, **k: called.append(1) or [])
    monkeypatch.setattr(
        cf, "resolve_balance_sheet_identity_fallback", lambda *a, **k: 5
    )
    assert cf.resolve_all_balance_sheet_identity_fallbacks(object()) == {
        "total_liabilities_resolved": 5, "stockholders_equity_resolved": 5}  # fmt: skip
    assert called == []


def test_flag_on_replaces_the_legacy_path(monkeypatch):
    monkeypatch.setenv(rule_flags.ENV_ENABLED, bi.RULE_ID)
    monkeypatch.delenv(rule_flags.ENV_DRYRUN, raising=False)
    monkeypatch.setattr(bi, "plan_identity", lambda *a, **k: ["p"])
    monkeypatch.setattr(bi, "apply_identity", lambda conn, plan, path: 9)
    monkeypatch.setattr(
        cf,
        "resolve_balance_sheet_identity_fallback",
        lambda *a, **k: pytest.fail("legacy ran"),
    )
    conn = Conn(
        {"from analytics.canonical_fact cf join analytics.canonical_concept": [(1,)]}
    )
    assert cf.resolve_all_balance_sheet_identity_fallbacks(conn) == {
        "balance_identity_rows": 9
    }
