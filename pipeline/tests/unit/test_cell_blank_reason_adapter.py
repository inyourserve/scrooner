"""Guard-side adapter over lane 1's cell_store (migration 0100 field mapping)."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from scrooner_pipeline.common import cell_blank_reason as cb

RID = "revenue.total_disagreement@1"
D1, D2 = date(2025, 1, 1), date(2025, 12, 31)


def br(**kw):
    base = dict(company_id=1, data_point="revenue", period_grain="FY", period_start=D1, period_end=D2,
                basis="resolved", rule_id=RID, reason_code="revenue_total_undecidable")  # fmt: skip
    base.update(kw)
    return cb.BlankReason(**base)


def test_grain_and_basis_are_mapped_to_the_contract():
    r = br(period_grain="instant", period_start=D2, period_end=D2)
    assert (r.period_grain, r.basis) == ("I", "latest")
    assert br(period_grain="YTD").period_grain == "TP"
    assert br(period_grain="Q").period_grain == "Q"


@pytest.mark.parametrize(
    "code",
    ["guard_hidden", "not_in_template", "undefined_by_math", "definition_pending", ""],
)
def test_state_and_class_names_are_not_reason_codes(code):
    with pytest.raises(ValueError):
        br(reason_code=code)


def test_null_dates_and_bad_grain_are_rejected():
    with pytest.raises(ValueError):
        br(period_start=None)
    with pytest.raises(ValueError):
        br(period_grain="decade")


def test_store_row_is_a_guard_hidden_defect_with_owner_and_input_refs():
    row = br(detail={"before": "5"}).to_store_row()
    assert (row.state, row.defect_class, row.owner, row.reason_code) == (
        "defect", "guard_hidden", "data_engineer_l1", "revenue_total_undecidable")  # fmt: skip
    assert row.input_refs == {"before": "5"} and row.key.data_point_name == "revenue"


def test_not_in_template_is_a_state_not_a_defect():
    row = br(
        state="not_in_template",
        reason_code="yfinance_tier_off",
        rule_id="employee_count.no_yfinance_tier@1",
    ).to_store_row()
    assert (row.state, row.defect_class, row.owner) == ("not_in_template", None, None)


class _Cur:
    def __init__(self, c):
        self.c = c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append((sql, params))
        self.res = (
            [(True,)]
            if "to_regclass" in sql
            else [("11111111-1111-1111-1111-111111111111",)]
        )

    def executemany(self, sql, rows):
        self.c.many.append(rows)

    def fetchone(self):
        return self.res[0]


class _Conn:
    def __init__(self):
        self.sql, self.many = [], []

    def cursor(self):
        return _Cur(self)


def test_pg_store_starts_one_rule_run_and_replaces_only_its_scope():
    c = _Conn()
    store = cb.PgBlankReasonStore(c)
    assert store.replace(1, RID, "adhoc", [br()]) == 1
    store.replace(2, RID, "adhoc", [br(company_id=2)])
    starts = [s for s, _ in c.sql if s.startswith("insert into analytics.rule_run")]
    assert len(starts) == 1  # one manifest row per rule, reused
    (delete_sql, params) = next(
        (s, p)
        for s, p in c.sql
        if s.startswith("delete from analytics.cell_blank_reason")
    )
    assert "run_id = %s::uuid and company_id = %s and rule_id = %s" in delete_sql
    assert params == ("11111111-1111-1111-1111-111111111111", 1, RID)


def test_pg_store_uses_a_caller_uuid_and_rejects_foreign_rows():
    c = _Conn()
    store = cb.PgBlankReasonStore(c)
    run = "22222222-2222-2222-2222-222222222222"
    store.replace(1, RID, run, [br()])
    assert not [s for s, _ in c.sql if s.startswith("insert into analytics.rule_run")]
    with pytest.raises(ValueError):
        store.replace(1, RID, run, [br(rule_id="scale.unit_plausibility@1")])
    with pytest.raises(ValueError):
        store.replace(1, RID, run, [br(company_id=9)])


def test_pg_store_refuses_without_the_table():
    c = MagicMock()
    c.cursor.return_value.__enter__.return_value.fetchone.return_value = (False,)
    with pytest.raises(RuntimeError):
        cb.PgBlankReasonStore(c).replace(1, RID, "x", [br()])
