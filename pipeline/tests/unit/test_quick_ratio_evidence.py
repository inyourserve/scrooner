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
D = Decimal


def M(**kw):  # footing lines in thousands -> dollars
    return {k: D(str(v)) * K for k, v in kw.items()}


def ctx(line_present, lines=None, like=None, end=END):
    return qe.Context(line_present, {end: lines or {}}, {end: like or {}})


def fixture_ctx(name):
    ca, cl, inv, *_ = FIXTURES[name]
    # the period's own current assets do NOT foot without the inventory: the inventory-like current line is the residual
    lines = {
        "AssetsCurrent": ca,
        "CashAndCashEquivalentsAtCarryingValue": ca / 4,
        "AccountsReceivableNetCurrent": ca / 10,
    }
    like = (
        {"InventoryFinishedGoodsNetOfReserves": inv}
        if name != "AZO"
        else {"InventoryFinishedGoodsNetOfReserves": inv}
    )
    return ctx(True, lines, like)


# ---------------------------------------------------------------- tags
def test_inventory_like_tags_exclude_flows_reserves_and_noncurrent_lines():
    for tag in (
        "InventoryNet", "InventoryFinishedGoodsNetOfReserves", "InventoryCrudeOilProductsAndMerchandise",
        "RetailRelatedInventoryMerchandise", "OtherInventorySupplies", "MaterialsSuppliesAndOther",
    ):  # fmt: skip
        assert qe.is_inventory_like(tag), tag
    for tag in (
        "IncreaseDecreaseInInventories", "InventoryValuationReserves", "InventoryWriteDown", "InventoryNoncurrent",
        "InventoryLIFOReserve", "Revenues", "InventoryLineFill",
    ):  # fmt: skip
        assert not qe.is_inventory_like(tag), tag


def test_materials_and_supplies_is_a_named_switch(monkeypatch):
    assert qe.is_inventory_like("MaterialsSuppliesAndOther")
    monkeypatch.setattr(qe, "MATERIALS_AND_SUPPLIES_ARE_INVENTORY", False)
    assert not qe.is_inventory_like(
        "MaterialsSuppliesAndOther"
    ) and qe.is_inventory_like("InventoryNet")


# ---------------------------------------------------------------- footing of the period's own balance sheet
def test_insm_cash_plus_prepaid_foots_so_there_is_no_inventory_line():
    # INSM 2016-12-31 (0001047469-17-000856): cash 162,591 + prepaid 5,816 = CA 168,407
    lines = M(
        AssetsCurrent=168407,
        CashAndCashEquivalentsAtCarryingValue=162591,
        PrepaidExpenseAndOtherAssetsCurrent=5816,
    )
    assert qe.foots_without_inventory(lines["AssetsCurrent"], lines)
    assert (
        qe.inventory_missing_reason(ctx(True, lines), END) is None
    )  # the later-years evidence 'presented' is irrelevant


def test_val_inventory_figure_that_is_a_note_inside_other_current_assets_does_not_block_the_zero():
    # VAL 2018-09-30 (0000314808-18-000140): cash 196 + STI 434 + receivables 348.5 + other 404 = CA 1,382.5; InventoryGross 270.7 is a note
    lines = M(AssetsCurrent=1382500, CashAndCashEquivalentsAtCarryingValue=196000, ShortTermInvestments=434000,
              ReceivablesNetCurrent=348500, OtherAssetsCurrent=404000, PrepaidExpenseCurrent=19500)  # fmt: skip
    assert (
        qe.inventory_missing_reason(ctx(False, lines, M(InventoryGross=270700)), END)
        is None
    )
    assert (
        qe.inventory_missing_reason(ctx(True, lines, M(InventoryGross=270700)), END)
        is None
    )


def test_wes_noncurrent_line_fill_does_not_block_the_zero():
    # WES 2018-06-30: receivables 166,983 + cash 55,317 + other 27,057 = CA 249,357
    lines = M(AssetsCurrent=249357, AccountsAndOtherReceivablesNetCurrent=166983, CashAndCashEquivalentsAtCarryingValue=55317, OtherAssetsCurrent=27057)  # fmt: skip
    assert (
        qe.inventory_missing_reason(
            ctx(False, lines, M(EnergyRelatedInventoryNaturalGasLiquids=9421)), END
        )
        is None
    )


def test_the_combined_cash_and_investments_line_is_not_added_to_the_investments_again():
    # CYTK 2025-09-30: cash 225.5 + AFS securities 737 + prepaid 13 + receivables 1.8 = CA 977.3; the 1,300 combined note is not a line
    lines = M(AssetsCurrent=977349, CashAndCashEquivalentsAtCarryingValue=225467, AvailableForSaleSecuritiesDebtSecuritiesCurrent=737000,
              PrepaidExpenseAndOtherAssetsCurrent=13006, AccountsReceivableNetCurrent=1808, CashCashEquivalentsAndShortTermInvestments=1300000)  # fmt: skip
    assert qe.foots_without_inventory(lines["AssetsCurrent"], lines)
    only_combined = M(
        AssetsCurrent=1400,
        CashCashEquivalentsAndShortTermInvestments=1300,
        AccountsReceivableNetCurrent=100,
    )
    assert qe.foots_without_inventory(
        only_combined["AssetsCurrent"],
        {**only_combined, "ShortTermInvestments": D(500) * K},
    )  # STI not double counted


def test_extra_current_lines_and_the_other_options_can_complete_the_footing():
    # receivables 600 + contract asset 100 = CA 700: only the extras option reaches it; "prepaid + other" alternatives too
    lines = M(
        AssetsCurrent=700,
        AccountsReceivableNetCurrent=600,
        ContractWithCustomerAssetNetCurrent=100,
    )
    assert qe.foots_without_inventory(lines["AssetsCurrent"], lines)
    only_other = M(
        AssetsCurrent=500, OtherAssetsCurrent=450, PrepaidExpenseCurrent=50
    )  # other + prepaid
    assert qe.foots_without_inventory(only_other["AssetsCurrent"], only_other)
    inside_other = M(
        AssetsCurrent=450, OtherAssetsCurrent=450, PrepaidExpenseCurrent=50
    )  # prepaid is inside other
    assert qe.foots_without_inventory(inside_other["AssetsCurrent"], inside_other)
    assert not qe.foots_without_inventory(
        D(1000) * K, M(AccountsReceivableNetCurrent=600)
    )  # a plain gap
    # the rounding allowance is capped: small round totals do not absorb a real residual
    assert not qe.foots_without_inventory(
        D(1000000), {"CashAndCashEquivalentsAtCarryingValue": D(900000)}
    )


def test_a_residual_that_the_lines_do_not_explain_does_not_foot():
    lines = M(AssetsCurrent=23673, CashAndCashEquivalentsAtCarryingValue=6903, AccountsReceivableNetCurrent=5242,
              PrepaidExpenseAndOtherAssetsCurrent=2217, DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent=1465)  # fmt: skip
    assert not qe.foots_without_inventory(
        lines["AssetsCurrent"], lines
    )  # NKE: 7,846 is missing (the inventory)
    assert not qe.foots_without_inventory(D(0), {})


def test_missing_inventory_reason_matrix():
    foot = M(AssetsCurrent=1000, CashAndCashEquivalentsAtCarryingValue=1000)
    nofoot = M(AssetsCurrent=1000, CashAndCashEquivalentsAtCarryingValue=100)
    inv = M(InventoryFinishedGoodsNetOfReserves=600)
    assert (
        qe.inventory_missing_reason(ctx(None, foot), END) is None
    )  # footing beats missing evidence
    assert (
        qe.inventory_missing_reason(ctx(False, nofoot), END) is None
    )  # latest statements show no line, nothing explains the residual
    assert qe.inventory_missing_reason(ctx(True, nofoot), END) == qe.REASON_PRESENTED
    assert qe.inventory_missing_reason(ctx(None, nofoot), END) == qe.REASON_UNKNOWN
    assert (
        qe.inventory_missing_reason(ctx(False, nofoot, inv), END) == qe.REASON_UNMAPPED
    )
    assert (
        qe.inventory_missing_reason(ctx(True, nofoot, inv), END) == qe.REASON_UNMAPPED
    )
    # an inventory-like figure larger than current assets is not a current line
    assert (
        qe.inventory_missing_reason(
            ctx(False, nofoot, M(InventoryFinishedGoodsNetOfReserves=5000)), END
        )
        is None
    )
    # the passed current-assets total (the period's own) overrides a missing AssetsCurrent line
    assert (
        qe.inventory_missing_reason(
            ctx(True, M(CashAndCashEquivalentsAtCarryingValue=1000)), END, D(1000) * K
        )
        is None
    )
    # dates are independent
    assert (
        qe.inventory_missing_reason(ctx(True, nofoot, inv, end=date(2025, 1, 1)), END)
        == qe.REASON_PRESENTED
    )


def test_cp_materials_and_supplies_is_an_inventory_line_under_the_default_switch(
    monkeypatch,
):
    # CP 2017-03-31 (0000016875-17-000029): cash 201 + receivables 631 + other 77 = 909 of CA 1,110; materials and supplies 201
    lines = M(AssetsCurrent=1110, CashAndCashEquivalentsAtCarryingValue=201, AccountsReceivableNetCurrent=631, OtherAssetsCurrent=77)  # fmt: skip
    like = {"MaterialsSuppliesAndOther": D(201) * K}
    assert (
        qe.inventory_missing_reason(ctx(False, lines, like), END) == qe.REASON_UNMAPPED
    )
    # the rule keeps the switch in one place: the loader filters inventory-like tags with it
    monkeypatch.setattr(qe, "MATERIALS_AND_SUPPLIES_ARE_INVENTORY", False)
    assert not qe.is_inventory_like("MaterialsSuppliesAndOther")


def test_a_current_materials_and_supplies_line_hides_the_figure_with_a_reason(
    monkeypatch,
):
    # founder ruling 2026-10-25: the formula is locked; wherever a current MaterialsSuppliesAndOther line exists the
    # figure is hidden. CP 2017-03-31: CA 1,110 does not foot without the 201 line.
    lines = M(AssetsCurrent=1110, CashAndCashEquivalentsAtCarryingValue=201, AccountsReceivableNetCurrent=631, OtherAssetsCurrent=77)  # fmt: skip
    c = qe.Context(
        False,
        {END: lines},
        {END: {"MaterialsSuppliesAndOther": D(201) * K}},
        {END: D(201) * K},
    )
    assert qe.materials_supplies_reason(c, END) == qe.REASON_MATERIALS
    # not when the current-assets total foots without it (the figure is inside another line or a note)
    foot = M(AssetsCurrent=1110, CashAndCashEquivalentsAtCarryingValue=1110)
    assert (
        qe.materials_supplies_reason(
            qe.Context(False, {END: foot}, {}, {END: D(201) * K}), END
        )
        is None
    )
    # not when it is larger than current assets (not a current line), nor when there is none
    assert (
        qe.materials_supplies_reason(
            qe.Context(False, {END: lines}, {}, {END: D(5000) * K}), END
        )
        is None
    )
    assert qe.materials_supplies_reason(qe.Context(False, {END: lines}), END) is None
    # the named switch turns the rule off in one place
    monkeypatch.setattr(qe, "MATERIALS_AND_SUPPLIES_ARE_INVENTORY", False)
    assert qe.materials_supplies_reason(c, END) is None


def test_calculate_hides_a_quick_ratio_that_has_an_inventory_value_but_a_materials_line(
    monkeypatch,
):
    ca, cl, inv, _stored, correct = FIXTURES["XOM"]
    lines = {"AssetsCurrent": ca, "CashAndCashEquivalentsAtCarryingValue": ca / 4}
    c = qe.Context(
        True, {END: lines}, {}, {END: D(3200) * K}
    )  # XOM: materials and supplies 3,200 on the face
    row = _run(monkeypatch, "XOM", with_inventory=True, rule_on=True, context=c)
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_MATERIALS
    off = _run(monkeypatch, "XOM", with_inventory=True, rule_on=False, context=c)
    assert abs(off["value"] - correct) < Decimal("0.002")  # flag off: untouched


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


def _run(monkeypatch, name, *, with_inventory, rule_on, context=None):
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
        qe,
        "load_context",
        lambda conn, cid, like_ids=None: context or fixture_ctx(name),
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
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_UNMAPPED


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_with_the_inventory_extracted_the_correct_quick_ratio_is_computed(
    monkeypatch, name
):
    ca, cl, inv, _stored, correct = FIXTURES[name]
    row = _run(monkeypatch, name, with_inventory=True, rule_on=True)
    assert row["is_null_reason"] is None and abs(row["value"] - (ca - inv) / cl) == 0
    assert abs(row["value"] - correct) < Decimal("0.002")


def test_a_period_whose_own_current_assets_foot_without_inventory_keeps_the_current_ratio(
    monkeypatch,
):
    ca, cl, *_ = FIXTURES["NKE"]
    lines = {"AssetsCurrent": ca, "CashAndCashEquivalentsAtCarryingValue": ca}
    row = _run(
        monkeypatch, "NKE", with_inventory=False, rule_on=True, context=ctx(True, lines)
    )
    assert row["value"] == ca / cl and row["is_null_reason"] is None


def test_the_periods_own_current_assets_total_is_passed_even_when_the_lines_lack_it(
    monkeypatch,
):
    ca, cl, *_ = FIXTURES["NKE"]
    c = qe.Context(
        True, {END: {"CashAndCashEquivalentsAtCarryingValue": ca}}, {}
    )  # no AssetsCurrent line stored
    row = _run(monkeypatch, "NKE", with_inventory=False, rule_on=True, context=c)
    assert row["value"] == ca / cl and row["is_null_reason"] is None


def test_unknown_evidence_is_a_null_not_a_guess(monkeypatch):
    row = _run(
        monkeypatch,
        "NKE",
        with_inventory=False,
        rule_on=True,
        context=ctx(None, {"AssetsCurrent": FIXTURES["NKE"][0]}),
    )
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_UNKNOWN


def test_rule_is_registered_default_off_with_a_dry_run():
    assert rule_flags.RULES[qe.RULE_ID].dry_run is True
    assert rule_flags.rule_mode(qe.RULE_ID, {}) == rule_flags.OFF


# ---------------------------------------------------------------- the loaders and the dry-run planner
class _Cur:
    def __init__(self, tables):
        self.t, self.rows, self.sql = tables, [], []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        s = " ".join(sql.split()).lower()
        self.sql.append(s)
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
        self.cur = _Cur(tables)

    def cursor(self):
        return self.cur


def test_load_context_splits_footing_lines_from_inventory_like_facts_per_date():
    conn = _Conn({
        "from analytics.company_filing_line_evidence": [(True,)],
        "from core.fact f join core.period": [
            (END, "AssetsCurrent", D(100)), (END, "InventoryFinishedGoodsNetOfReserves", D(30)),
            (date(2025, 12, 31), "AssetsCurrent", D(90)),
        ],
    })  # fmt: skip
    c = qe.load_context(conn, 5, like_ids=[99])
    assert c.line_present is True
    assert c.lines_by_date == {
        END: {"AssetsCurrent": D(100)},
        date(2025, 12, 31): {"AssetsCurrent": D(90)},
    }
    assert (
        c.inventory_like == {END: {"InventoryFinishedGoodsNetOfReserves": D(30)}}
        and c.materials_supplies == {}
    )
    assert any("p.period_type = 'instant'" in q for q in conn.cur.sql)
    assert qe.load_context(_Conn({"from analytics.company_filing_line_evidence": [], "from core.fact f join core.period": []}), 5, like_ids=[]).line_present is None  # fmt: skip


def test_load_context_collects_materials_and_supplies_per_date():
    conn = _Conn({
        "from analytics.company_filing_line_evidence": [(False,)],
        "from core.fact f join core.period": [(END, "MaterialsSuppliesAndOther", D(201)), (END, "InventoryRawMaterialsAndSupplies", D(5))],
    })  # fmt: skip
    c = qe.load_context(conn, 5, like_ids=[1])
    assert c.materials_supplies == {END: D(201)} and set(c.inventory_like[END]) == {"MaterialsSuppliesAndOther"} | {"InventoryRawMaterialsAndSupplies"}  # fmt: skip


def test_planner_also_lists_cells_with_an_inventory_value_and_a_materials_line():
    # the XOM-type cell: inventory is mapped (so it is in `have`), the stored value is not the current ratio
    tables_conn = _planner_conn(
        [
            (END, "MaterialsSuppliesAndOther", D(3200)),
            (END, "AssetsCurrent", D(1000000)),
        ],
        None,
    )
    got = qe.plan_quick_ratio(tables_conn, [2])
    assert [(p.company_id, p.reason) for p in got if p.company_id == 2] == [
        (2, qe.REASON_MATERIALS)
    ]


def test_inventory_concept_loader_drops_mapped_and_non_balance_sheet_tags():
    conn = _Conn({
        "from analytics.concept_mapping": [(1,)],
        "from core.concept": [(1, "InventoryNet"), (2, "InventoryCrudeOilProductsAndMerchandise"), (3, "InventoryWriteDown"), (4, "OtherInventorySupplies")],
    })  # fmt: skip
    like, mapped = qe.load_inventory_concept_ids(conn)
    assert like == [2, 4] and mapped == {1}


def _planner_conn(context_rows, evidence):
    tables = {
        "select id from analytics.metric_definition where metric_name = 'quick_ratio'": [(7,)],
        "select id from analytics.metric_definition where metric_name = 'current_ratio'": [(8,)],
        "select id from analytics.canonical_concept": [(50,)],
        "select id, cik from core.company": [(1, "0000320187"), (2, "0000012927")],
        "from analytics.concept_mapping": [],
        "from core.concept": [],
        "from analytics.canonical_fact cf": [(2, END)],  # company 2 has an inventory fact at END
        "from analytics.company_filing_line_evidence": [(evidence,)],
        "from core.fact f join core.period": context_rows,
    }  # fmt: skip
    calls = iter([
        [(1, END, "Q2", D("2.075")), (2, END, "Q2", D("1.138")), (1, date(2025, 6, 30), "Q2", D("2.0"))],
        [(1, END, D("2.075")), (2, END, D("1.138")), (1, date(2025, 6, 30), D("2.5"))],
    ])  # fmt: skip

    class Conn(_Conn):
        def cursor(self):
            cur = _Cur(self.t)
            orig = cur.execute

            def execute(sql, params=None):
                if "from analytics.metric_value" in " ".join(sql.split()).lower():
                    cur.rows = next(calls)
                    return
                orig(sql, params)

            cur.execute = execute
            return cur

    return Conn(tables)


def test_planner_lists_only_value_cells_without_inventory_that_the_rule_nulls():
    got = qe.plan_quick_ratio(_planner_conn([], True), [1, 2])
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
        ),  # the current ratio of that date differs: not asserted equal
    ]


def test_planner_leaves_cells_alone_where_the_period_foots_or_no_line_is_shown():
    assert qe.plan_quick_ratio(_planner_conn([], False), [1, 2]) == []
    foot = [(END, "AssetsCurrent", D(100)), (END, "CashAndCashEquivalentsAtCarryingValue", D(100)),
            (date(2025, 6, 30), "AssetsCurrent", D(100)), (date(2025, 6, 30), "CashAndCashEquivalentsAtCarryingValue", D(100))]  # fmt: skip
    assert qe.plan_quick_ratio(_planner_conn(foot, True), [1, 2]) == []
