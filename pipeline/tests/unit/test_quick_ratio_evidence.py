"""quick_ratio: a missing inventory is zero only where the filing-line evidence says the line is not presented.
Fixtures (Data Triage 2026-10-24, FILING-CHECKED): NKE 0000320187-26-000193 R4, BA 0001628280-26-050038 R5, GAP
0001628280-26-059345 R2, AZO 0001104659-26-073525 R2, XOM 0000034088-26-000093 R5."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from scrooner_pipeline.common import rule_flags
from scrooner_pipeline.mapper import calculate as calc
from scrooner_pipeline.mapper import quick_ratio_evidence as qe

END = date(2026, 6, 30)
CA, INV, CL = 1, 2, 3
# name: (current assets, current liabilities, filed inventory, stored value before the fix, correct quick ratio)
K = Decimal(
    1000
)  # the filings print thousands/millions; the engine's materiality floor needs dollar-scale values
FIXTURES = {  # name: (current assets, current liabilities, filed inventory, stored before the fix, correct quick ratio)
    "NKE": (Decimal(23672) * K, Decimal(11409) * K, Decimal(7846) * K, Decimal("2.075"), Decimal("1.387")),
    "BA": (Decimal(124616) * K, Decimal(109527) * K, Decimal(88388) * K, Decimal("1.138"), Decimal("0.331")),
    "GAP": (Decimal(5869) * K, Decimal(3221) * K, Decimal(2297) * K, Decimal("1.822"), Decimal("1.109")),
    "AZO": (Decimal(8937000) * K, Decimal(10040000) * K, Decimal(7559056) * K, Decimal("0.890"), Decimal("0.137")),
    "XOM": (Decimal(100740) * K, Decimal(88760) * K, Decimal(25563) * K, Decimal("1.135"), Decimal("0.847")),
}  # fmt: skip
# what the evidence says about each company's inventory line / unmapped inventory-like tags
CONTEXT = {
    "NKE": qe.Context(True), "GAP": qe.Context(True), "AZO": qe.Context(True),
    "BA": qe.Context(False, frozenset({END})),  # unmapped inventory-like tag filed at the date
    "XOM": qe.Context(True, frozenset({END})),  # inventories in two sub-lines with no total
}  # fmt: skip


def test_inventory_like_tags_exclude_flows_reserves_and_noncurrent_lines():
    for tag in ("InventoryNet", "InventoryFinishedGoodsNetOfReserves", "InventoryCrudeOilProductsAndMerchandise", "RetailRelatedInventoryMerchandise"):  # fmt: skip
        assert qe.is_inventory_like(tag), tag
    for tag in ("IncreaseDecreaseInInventories", "InventoryValuationReserves", "InventoryWriteDown", "InventoryNoncurrent", "InventoryLIFOReserve", "Revenues"):  # fmt: skip
        assert not qe.is_inventory_like(tag), tag


def test_missing_inventory_reason_matrix():
    assert (
        qe.inventory_missing_reason(qe.Context(False), END) is None
    )  # the statement shows no inventory line
    assert qe.inventory_missing_reason(qe.Context(True), END) == qe.REASON_PRESENTED
    assert qe.inventory_missing_reason(qe.Context(None), END) == qe.REASON_UNKNOWN
    # an unmapped inventory-like tag wins over "not presented", and is date-specific
    assert (
        qe.inventory_missing_reason(qe.Context(False, frozenset({END})), END)
        == qe.REASON_UNMAPPED
    )
    assert (
        qe.inventory_missing_reason(
            qe.Context(False, frozenset({date(2025, 6, 30)})), END
        )
        is None
    )
    assert (
        qe.inventory_missing_reason(qe.Context(True, frozenset({END})), END)
        == qe.REASON_UNMAPPED
    )


def _target():
    return [
        {
            "id": 7,
            "name": "quick_ratio",
            "inputs": [
                ("current_assets", CA, "add", True),
                ("inventory", INV, "subtract", True),
                ("current_liabilities", CL, "denominator", True),
            ],
        }
    ]


def _run(monkeypatch, name, *, with_inventory, rule_on, ctx=None):
    ca, cl, inv, _stored, _correct = FIXTURES[name]
    by_end = {CA: {END: (ca, [1])}, CL: {END: (cl, [3])}}
    by_period = {CA: {10: (ca, [1])}, CL: {10: (cl, [3])}}
    if with_inventory:
        by_end[INV] = {END: (inv, [2])}
        by_period[INV] = {10: (inv, [2])}
    monkeypatch.setattr(
        calc, "_load_canonical_facts",
        lambda conn, cid: {"by_period_id": by_period, "by_end_date": by_end, "periods": {10: (END, END, "Q2")}},
    )  # fmt: skip
    env = {rule_flags.ENV_ENABLED: qe.RULE_ID} if rule_on else {}
    monkeypatch.setattr(
        calc, "rule_enabled", lambda rid: rule_flags.rule_enabled(rid, env)
    )
    monkeypatch.setattr(
        qe, "load_context", lambda conn, cid, like_ids=None: ctx or CONTEXT[name]
    )
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    calc.calculate_for_company(conn, 1, _target())
    rows = cur.executemany.call_args.args[1]
    assert len(rows) == 1
    return rows[0]


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_flag_off_keeps_the_legacy_value_that_equals_the_current_ratio(
    monkeypatch, name
):
    ca, cl, _inv, stored, _correct = FIXTURES[name]
    row = _run(monkeypatch, name, with_inventory=False, rule_on=False)
    assert row["value"] == ca / cl and abs(row["value"] - stored) < Decimal("0.001")
    assert row["is_null_reason"] is None


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_flag_on_nulls_the_cell_with_a_visible_reason(monkeypatch, name):
    row = _run(monkeypatch, name, with_inventory=False, rule_on=True)
    assert row["value"] is None
    assert row["is_null_reason"] == (
        qe.REASON_UNMAPPED if name in ("BA", "XOM") else qe.REASON_PRESENTED
    )


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_with_the_inventory_extracted_the_correct_quick_ratio_is_computed(
    monkeypatch, name
):
    ca, cl, inv, _stored, correct = FIXTURES[name]
    row = _run(monkeypatch, name, with_inventory=True, rule_on=True)
    assert row["is_null_reason"] is None and abs(row["value"] - (ca - inv) / cl) == 0
    assert abs(row["value"] - correct) < Decimal("0.002")


def test_a_company_whose_statements_show_no_inventory_line_still_gets_the_current_ratio_as_quick_ratio(
    monkeypatch,
):
    row = _run(
        monkeypatch, "NKE", with_inventory=False, rule_on=True, ctx=qe.Context(False)
    )
    ca, cl, *_ = FIXTURES["NKE"]
    assert row["value"] == ca / cl and row["is_null_reason"] is None


def test_unknown_evidence_is_a_null_not_a_guess(monkeypatch):
    row = _run(
        monkeypatch, "NKE", with_inventory=False, rule_on=True, ctx=qe.Context(None)
    )
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_UNKNOWN


def test_rule_is_registered_default_off_with_a_dry_run():
    assert rule_flags.RULES[qe.RULE_ID].dry_run is True
    assert rule_flags.rule_mode(qe.RULE_ID, {}) == rule_flags.OFF


# ---------------------------------------------------------------- the loaders and the dry-run planner
class _Cur:
    def __init__(self, tables):
        self.t, self.rows = tables, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        s = " ".join(sql.split()).lower()
        for key, rows in self.t.items():
            if key in s:
                self.rows = rows
                return
        raise AssertionError(s)

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class _Conn:
    def __init__(self, tables):
        self.t = tables

    def cursor(self):
        return _Cur(self.t)


def test_load_context_reads_the_evidence_row_and_the_unmapped_dates():
    conn = _Conn({
        "from analytics.company_filing_line_evidence": [(True,)],
        "from core.fact f join core.period": [(END,), (date(2025, 12, 31),)],
    })  # fmt: skip
    ctx = qe.load_context(conn, 5, like_ids=[99])
    assert ctx == qe.Context(True, frozenset({END, date(2025, 12, 31)}))
    assert qe.load_context(_Conn({"from analytics.company_filing_line_evidence": []}), 5, like_ids=[]) == qe.Context(None)  # fmt: skip


def test_inventory_concept_loader_drops_mapped_and_non_balance_sheet_tags():
    conn = _Conn({
        "from analytics.concept_mapping": [(1,)],
        "from core.concept": [(1, "InventoryNet"), (2, "InventoryCrudeOilProductsAndMerchandise"), (3, "InventoryWriteDown")],
    })  # fmt: skip
    like, mapped = qe.load_inventory_concept_ids(conn)
    assert like == [2] and mapped == {1}


def test_planner_lists_only_value_cells_without_inventory_that_the_evidence_nulls():
    tables = {
        "select id from analytics.metric_definition where metric_name = 'quick_ratio'": [(7,)],
        "select id from analytics.metric_definition where metric_name = 'current_ratio'": [(8,)],
        "select id from analytics.canonical_concept": [(50,)],
        "select id, cik from core.company": [(1, "0000320187"), (2, "0000012927")],
        "from analytics.concept_mapping": [],
        "from core.concept": [],
        "metric_definition_id = %s and value is not null and period_label": [],
    }  # fmt: skip
    # the two metric_value reads share one SQL shape; script them by call order instead
    calls = iter([
        [(1, END, "Q2", Decimal("2.075")), (2, END, "Q2", Decimal("1.138")), (1, date(2025, 6, 30), "Q2", Decimal("2.0"))],
        [(1, END, Decimal("2.075")), (2, END, Decimal("1.138")), (1, date(2025, 6, 30), Decimal("2.5"))],
    ])  # fmt: skip

    class Conn(_Conn):
        def cursor(self):
            cur = _Cur(self.t)
            orig = cur.execute

            def execute(sql, params=None):
                s = " ".join(sql.split()).lower()
                if "from analytics.metric_value" in s:
                    cur.rows = next(calls)
                    return
                orig(sql, params)

            cur.execute = execute
            return cur

    tables["from analytics.canonical_fact cf"] = [
        (2, END)
    ]  # company 2 has an inventory fact at END
    tables["from analytics.company_filing_line_evidence"] = [(True,)]
    tables["from core.fact f join core.period"] = []
    got = qe.plan_quick_ratio(Conn(tables), [1, 2])
    assert [
        (p.company_id, p.period_end, p.reason, p.new, p.equals_current_ratio)
        for p in got
    ] == [
        (1, "2026-06-30", qe.REASON_PRESENTED, None, True),
        (
            1,
            "2025-06-30",
            qe.REASON_PRESENTED,
            None,
            False,
        ),  # no current-ratio row for that date: not asserted
    ]


def test_planner_leaves_cells_alone_where_the_statements_show_no_inventory_line():
    tables = {
        "select id from analytics.metric_definition where metric_name = 'quick_ratio'": [(7,)],
        "select id from analytics.metric_definition where metric_name = 'current_ratio'": [(8,)],
        "select id from analytics.canonical_concept": [(50,)],
        "select id, cik from core.company": [(1, "0000000001")],
        "from analytics.concept_mapping": [],
        "from core.concept": [],
        "from analytics.canonical_fact cf": [],
        "from analytics.company_filing_line_evidence": [(False,)],
        "from core.fact f join core.period": [],
    }  # fmt: skip
    rows = iter([[(1, END, "Q2", Decimal("2.075"))], [(1, END, Decimal("2.075"))]])

    class Conn(_Conn):
        def cursor(self):
            cur = _Cur(self.t)
            orig = cur.execute

            def execute(sql, params=None):
                if "from analytics.metric_value" in " ".join(sql.split()).lower():
                    cur.rows = next(rows)
                    return
                orig(sql, params)

            cur.execute = execute
            return cur

    assert qe.plan_quick_ratio(Conn(tables), [1]) == []


def test_unmapped_dates_are_read_from_instant_facts_only():
    seen = []

    class Conn(_Conn):
        def cursor(self):
            cur = _Cur(self.t)
            orig = cur.execute

            def execute(sql, params=None):
                seen.append(" ".join(sql.split()).lower())
                orig(sql, params)

            cur.execute = execute
            return cur

    qe.load_context(Conn({"from analytics.company_filing_line_evidence": [(None,)], "from core.fact f join core.period": []}), 1, like_ids=[9])  # fmt: skip
    assert any("p.period_type = 'instant'" in q for q in seen)
