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


def ctx(face, lines=None, like=None, end=END, *, materials=None, nonauth=False):
    """face: does THIS period's own balance sheet show an inventory line at its date (True / False); "hide" = the
    statement was read but does not show the date (or predates machine-readable statements); None = no readable
    statement here (the value stays, flagged). ``materials``: a MaterialsSuppliesAndOther fact value."""
    pf = {end: qe.PeriodFace(face, False)} if face in (True, False) else {}
    hide = frozenset({end}) if face == "hide" else frozenset()
    return qe.Context(
        None, {end: lines or {}}, {end: like or {}}, {end: materials} if materials else {}, pf, hide,
        frozenset({end}) if nonauth else frozenset(),
    )  # fmt: skip


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
# ---------------------------------------------------------------- tags
def test_inventory_like_tags_exclude_flows_reserves_noncurrent_lines_and_materials_and_supplies_other():
    for tag in (
        "InventoryNet", "InventoryFinishedGoodsNetOfReserves", "InventoryCrudeOilProductsAndMerchandise",
        "RetailRelatedInventoryMerchandise", "OtherInventorySupplies", "InventoryRawMaterialsAndSupplies",
        "InventorySuppliesNetOfReserves", "PublicUtilitiesInventory", "EnergyRelatedInventory",
    ):  # fmt: skip
        assert qe.is_inventory_like(tag), tag
    for tag in (
        "IncreaseDecreaseInInventories", "InventoryValuationReserves", "InventoryWriteDown", "InventoryNoncurrent",
        "InventoryLIFOReserve", "Revenues", "InventoryLineFill",
        "MaterialsSuppliesAndOther",  # element text: not included in inventory
    ):  # fmt: skip
        assert not qe.is_inventory_like(tag), tag


def test_reason_codes_come_from_one_mapping_table_and_the_precedence_is_the_record_s():
    assert qe.PRECEDENCE == (
        "unclassified",
        "materials",
        "not_authoritative",
        "unavailable",
        "presented",
        "review",
    )
    assert qe.HIDE_REASONS == {
        "unclassified": "incomplete:balance_sheet_unclassified",
        "materials": "incomplete:materials_supplies_line_present",
        "not_authoritative": "incomplete:inventory_fact_not_authoritative",
        "unavailable": "incomplete:inventory_statement_unavailable",
        "presented": "incomplete:inventory_presented_not_extracted",
        "review": "incomplete:inventory_value_under_review",
    }
    assert (qe.REASON_MATERIALS, qe.REASON_REVIEW) == (
        qe.HIDE_REASONS["materials"],
        qe.HIDE_REASONS["review"],
    )


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


# ---------------------------------------------------------------- the decision
NOFOOT = M(AssetsCurrent=1000, CashAndCashEquivalentsAtCarryingValue=100)
FOOT = M(AssetsCurrent=1000, CashAndCashEquivalentsAtCarryingValue=1000)
MEMBER = M(InventoryFinishedGoodsNetOfReserves=600)


def cause(c, *, present=False, ca=None):
    return qe.hide_cause(c, END, ca, present)


def test_decision_when_the_inventory_value_is_missing():
    assert (
        cause(ctx(True, FOOT, MEMBER)) is None
    )  # the period's own lines foot: no room for an inventory line
    # nothing foots: THIS period's own statement decides, at the cell's own date column
    assert (
        cause(ctx(True, NOFOOT)) == "presented"
    )  # an inventory line, and no rule step yields a value
    assert (
        cause(ctx(True, NOFOOT, MEMBER)) == "review"
    )  # authoritative member sub-lines yield a value: not yet published
    assert (
        cause(ctx(False, NOFOOT, MEMBER)) is None
    )  # the statement shows no inventory line (0001522540 2023-06-30)
    assert (
        cause(ctx("hide", NOFOOT)) == "unavailable"
    )  # readable but not that date; pre-2010
    assert (
        cause(ctx(None, NOFOOT)) is None
    )  # no readable statement in the data set (after 2009): the value stays
    assert cause(ctx(None, NOFOOT, MEMBER)) == "review"
    assert (
        cause(ctx("hide", NOFOOT, MEMBER)) == "review"
    )  # a member value the rule can read decides before "unavailable"
    # a member figure larger than current assets is not a current line
    assert cause(ctx(None, NOFOOT, M(InventoryFinishedGoodsNetOfReserves=5000))) is None
    # the passed current-assets total overrides a missing AssetsCurrent line
    assert (
        cause(ctx(True, M(CashAndCashEquivalentsAtCarryingValue=1000)), ca=D(1000) * K)
        is None
    )
    # another date's statement says nothing about this one
    assert cause(ctx(True, NOFOOT, end=date(2025, 1, 1))) is None
    assert qe.face_unavailable(ctx("hide", NOFOOT), END) and not qe.face_unavailable(
        ctx(True, NOFOOT), END
    )


def test_non_authoritative_inventory_net_hides_with_its_own_reason_and_is_never_read():
    # 147 cells at 85 companies: only non-authoritative InventoryNet copies. Not mapped, not shown.
    assert cause(ctx(True, NOFOOT, MEMBER, nonauth=True)) == "not_authoritative"
    assert cause(ctx(None, NOFOOT, nonauth=True)) == "not_authoritative"
    assert (
        cause(ctx(True, FOOT, nonauth=True)) is None
    )  # footing without inventory still stands


def test_materials_and_supplies_takes_precedence_over_every_other_reason():
    # CP 2017-03-31 (0000016875-17-000029): inventory-like facts exist, but the face presents "Materials and supplies"
    lines = M(AssetsCurrent=1110, CashAndCashEquivalentsAtCarryingValue=201, AccountsReceivableNetCurrent=631, OtherAssetsCurrent=77)  # fmt: skip
    c = qe.Context(False, {END: lines}, {END: M(OtherInventorySupplies=201)}, {END: D(201) * K}, {END: qe.PeriodFace(True, True)}, frozenset(), frozenset({END}))  # fmt: skip
    assert cause(c) == "materials"  # not 'not_authoritative', 'presented' or 'review'
    assert qe.inventory_missing_reason(c, END) == qe.REASON_MATERIALS
    # also where an inventory value exists (the cell would otherwise stay)
    assert cause(c, present=True) == "materials"
    # CP's real shape without a statement: the MaterialsSuppliesAndOther fact itself
    c2 = qe.Context(
        False, {END: lines}, {}, {END: D(201) * K}, {}, {}, frozenset(), frozenset()
    )
    assert cause(c2) == "materials"
    # not when the total foots without that fact (it is inside another line or a note), nor larger than current assets
    foot = M(AssetsCurrent=1110, CashAndCashEquivalentsAtCarryingValue=1110)
    assert (
        cause(
            qe.Context(
                False,
                {END: foot},
                {},
                {END: D(201) * K},
                {},
                {},
                frozenset(),
                frozenset(),
            )
        )
        is None
    )
    assert (
        cause(
            qe.Context(
                False,
                {END: lines},
                {},
                {END: D(5000) * K},
                {},
                {},
                frozenset(),
                frozenset(),
            )
        )
        is None
    )


def test_materials_switch_turns_the_rule_off_in_one_place(monkeypatch):
    c = qe.Context(
        False, {END: NOFOOT}, {}, {END: D(10) * K}, {END: qe.PeriodFace(False, True)}
    )
    assert cause(c, present=True) == "materials"
    monkeypatch.setattr(qe, "MATERIALS_AND_SUPPLIES_ARE_INVENTORY", False)
    assert cause(c, present=True) is None


def test_inventory_named_supplies_elements_are_inside_inventory_and_hide_nothing():
    # NI 2023-12-31 "Materials and supplies, at average cost" 172.1 on InventoryRawMaterialsAndSupplies; XOM, PEG
    c = ctx(True, NOFOOT, M(InventoryRawMaterialsAndSupplies=40))
    assert cause(c, present=True) is None
    assert (
        cause(c) == "review"
    )  # as a member sub-line when the inventory total is missing


def test_the_materials_line_hides_a_cell_that_stays_UPS_does_not():
    # UPS 2023-12-31: no inventory or materials line on the face -> nothing hidden
    assert (
        cause(
            qe.Context(
                False, {END: NOFOOT}, {}, {}, {END: qe.PeriodFace(False, False)}
            ),
            present=True,
        )
        is None
    )
    # FDX 'Spare parts, supplies, and fuel' / ConEd: the face presents a supplies line, the cell has an inventory value
    assert (
        cause(
            qe.Context(False, {END: NOFOOT}, {}, {}, {END: qe.PeriodFace(False, True)}),
            present=True,
        )
        == "materials"
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
        lambda conn, cid, like_ids=None, face=None, mapped_ids=None: (
            context or fixture_ctx(name)
        ),
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
def test_flag_on_hides_the_fixture_cells_with_the_review_reason(monkeypatch, name):
    # the face shows an inventory line and authoritative member sub-lines yield a value that is not yet published
    row = _run(monkeypatch, name, with_inventory=False, rule_on=True)
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_REVIEW


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_with_the_inventory_extracted_the_correct_quick_ratio_is_computed(
    monkeypatch, name
):
    ca, cl, inv, _stored, correct = FIXTURES[name]
    row = _run(monkeypatch, name, with_inventory=True, rule_on=True)
    assert row["is_null_reason"] is None and abs(row["value"] - (ca - inv) / cl) == 0
    assert abs(row["value"] - correct) < Decimal("0.002")


def test_cp_2017_03_31_gets_the_materials_reason_in_calculate_not_unmapped(monkeypatch):
    ca, cl, *_ = FIXTURES["NKE"]
    lines = {"AssetsCurrent": ca, "CashAndCashEquivalentsAtCarryingValue": ca / 4}
    c = qe.Context(False, {END: lines}, {END: {"OtherInventorySupplies": ca / 5}}, {END: ca / 5}, {END: qe.PeriodFace(True, True)}, frozenset(), frozenset({END}))  # fmt: skip
    row = _run(monkeypatch, "NKE", with_inventory=False, rule_on=True, context=c)
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_MATERIALS


def test_calculate_hides_a_quick_ratio_that_has_an_inventory_value_but_a_materials_line(
    monkeypatch,
):
    ca, cl, inv, _stored, correct = FIXTURES["XOM"]
    lines = {"AssetsCurrent": ca, "CashAndCashEquivalentsAtCarryingValue": ca / 4}
    c = qe.Context(
        True, {END: lines}, {}, {END: D(3200) * K}, {END: qe.PeriodFace(True, True)}
    )
    row = _run(monkeypatch, "XOM", with_inventory=True, rule_on=True, context=c)
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_MATERIALS
    off = _run(monkeypatch, "XOM", with_inventory=True, rule_on=False, context=c)
    assert abs(off["value"] - correct) < Decimal("0.002")  # flag off: untouched


def test_a_period_whose_own_current_assets_foot_without_inventory_keeps_the_current_ratio(
    monkeypatch,
):
    ca, cl, *_ = FIXTURES["NKE"]
    row = _run(monkeypatch, "NKE", with_inventory=False, rule_on=True, context=ctx(True, {"AssetsCurrent": ca, "CashAndCashEquivalentsAtCarryingValue": ca}))  # fmt: skip
    assert row["value"] == ca / cl and row["is_null_reason"] is None


def test_the_periods_own_current_assets_total_is_passed_even_when_the_lines_lack_it(
    monkeypatch,
):
    ca, cl, *_ = FIXTURES["NKE"]
    c = qe.Context(
        True,
        {END: {"CashAndCashEquivalentsAtCarryingValue": ca}},
        {},
        {},
        {END: qe.PeriodFace(True, False)},
    )
    row = _run(monkeypatch, "NKE", with_inventory=False, rule_on=True, context=c)
    assert row["value"] == ca / cl and row["is_null_reason"] is None


def test_an_unavailable_statement_hides_the_cell_with_its_reason(monkeypatch):
    ca, *_ = FIXTURES["NKE"]
    row = _run(
        monkeypatch,
        "NKE",
        with_inventory=False,
        rule_on=True,
        context=ctx("hide", {"AssetsCurrent": ca}),
    )
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_UNAVAILABLE


def test_a_statement_that_shows_inventory_with_no_member_value_is_presented_not_extracted(
    monkeypatch,
):
    ca, *_ = FIXTURES["NKE"]
    row = _run(
        monkeypatch,
        "NKE",
        with_inventory=False,
        rule_on=True,
        context=ctx(True, {"AssetsCurrent": ca}),
    )
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_PRESENTED


def test_rule_is_registered_default_off_with_a_dry_run():
    assert rule_flags.RULES[qe.RULE_ID].dry_run is True
    assert rule_flags.rule_mode(qe.RULE_ID, {}) == rule_flags.OFF


# ---------------------------------------------------------------- the loaders (a scripted cursor)
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


def tables(
    *, evidence=True, cik="0000000005", periodic=(), fallback=(), facts=(), nonauth=()
):
    return {  # most specific key first: the first key found in the SQL wins
        "select cik from core.company": [(cik,)],
        "bool_or(f.is_authoritative)": list(nonauth),
        "k.tag = 'assetscurrent'": list(fallback),
        "from core.filing where": list(periodic),
        "from analytics.company_filing_line_evidence": [(evidence,)],
        "from core.fact f join core.period": list(facts),
    }


from scrooner_pipeline.mapper.quick_ratio_face import AccessionFace  # noqa: E402

D0 = date(2025, 6, 30)
ACC = "0000000001-26-000001"


def AF(dates, inventory=(), materials=(), wip=(), classified=True):
    return AccessionFace(
        frozenset(dates), frozenset(inventory), frozenset(materials), frozenset(wip),
        classified,
    )  # fmt: skip


def load(conn_tables, face, **kw):
    return qe.load_context(
        _Conn(conn_tables), 5, like_ids=[99], mapped_ids={1}, face=face, **kw
    )


def test_load_context_splits_footing_lines_members_and_materials_per_date():
    t = tables(periodic=[(END, ACC)], facts=[
        (END, "AssetsCurrent", D(100), ACC, True), (END, "InventoryFinishedGoodsNetOfReserves", D(30), ACC, True),
        (END, "MaterialsSuppliesAndOther", D(7), ACC, True), (date(2025, 12, 31), "AssetsCurrent", D(90), ACC, True),
    ])  # fmt: skip
    c = load(t, {})
    assert c.lines_by_date == {
        END: {"AssetsCurrent": D(100)},
        date(2025, 12, 31): {"AssetsCurrent": D(90)},
    }
    assert c.inventory_like == {END: {"InventoryFinishedGoodsNetOfReserves": D(30)}}
    assert c.materials_supplies == {END: D(7)}


def test_member_facts_must_be_authoritative_and_from_the_periods_own_filing():
    t = tables(periodic=[(END, ACC)], facts=[
        (END, "InventoryFinishedGoodsNetOfReserves", D(30), "0000000002-26-000009", True),  # another filing (a recast)
        (END, "OtherInventorySupplies", D(5), ACC, False),  # a non-authoritative copy
        (END, "InventoryRawMaterialsAndSupplies", D(8), ACC, True),
    ])  # fmt: skip
    assert load(t, {}).inventory_like == {
        END: {"InventoryRawMaterialsAndSupplies": D(8)}
    }


def test_footing_lines_prefer_the_own_filing_and_the_authoritative_copy():
    t = tables(periodic=[(END, ACC)], facts=[
        (END, "AssetsCurrent", D(1), "0000000002-26-000009", True), (END, "AssetsCurrent", D(2), ACC, False),
        (END, "AssetsCurrent", D(3), ACC, True),
    ])  # fmt: skip
    assert load(t, {}).lines_by_date[END]["AssetsCurrent"] == D(3)


def test_inventory_net_that_exists_only_as_non_authoritative_copies_is_flagged():
    t = tables(periodic=[(END, ACC)], nonauth=[(END, False), (D0, True)])
    assert load(t, {}).nonauthoritative_dates == {END}


def test_load_context_reads_the_period_s_own_statement_at_the_cell_s_own_date():
    t = tables(
        periodic=[
            (END, ACC),
            (date(2025, 12, 31), "0000000001-26-000002"),
            (D0, "0000000001-25-000003"),
        ]
    )
    face = {
        ACC: AF(
            {END, D0}, {D0}, {END}
        ),  # inventory only in the comparative column; materials at END
        "0000000001-26-000099": AF(
            {date(2025, 12, 31)}, {date(2025, 12, 31)}
        ),  # some other accession
        "0000000001-25-000003": AF(
            {date(2024, 6, 30)}, {date(2024, 6, 30)}
        ),  # shows only OTHER dates than its own
    }
    c = load(t, face)
    assert c.face_by_date == {
        END: qe.PeriodFace(inventory_line=False, materials_line=True)
    }
    assert (
        c.accession_by_date[date(2025, 12, 31)] == "0000000001-26-000002"
        and D0 in c.face_hide_dates
    )
    q = next(s for s in _Conn(t).cur.sql if False) if False else None


def test_the_period_filing_is_the_original_periodic_filing_of_the_date():
    conn = _Conn(tables(periodic=[(END, ACC)]))
    qe.load_context(conn, 5, like_ids=[], mapped_ids=set(), face={})
    q = next(s for s in conn.cur.sql if "from core.filing where" in s)
    assert (
        "order by period_of_report, is_amendment, filing_date" in q
        and "'10-k'" in q
        and "'10-q'" in q
    )


def test_a_date_without_a_periodic_filing_of_its_own_uses_the_filing_of_its_current_assets_fact():
    # CIK 0001058811 2024-04-30: no 10-K/10-Q has that period_of_report; the transition-period filing carries it
    t = tables(
        periodic=[(END, ACC)],
        fallback=[
            (date(2024, 4, 30), "0001213900-24-109054"),
            (END, "ignored-primary-wins"),
        ],
    )
    c = load(
        t, {"0001213900-24-109054": AF({date(2024, 4, 30)}), ACC: AF({END}, {END})}
    )
    assert c.accession_by_date == {END: ACC, date(2024, 4, 30): "0001213900-24-109054"}
    assert c.face_by_date == {
        END: qe.PeriodFace(True, False),
        date(2024, 4, 30): qe.PeriodFace(False, False),
    }


def test_fsds_rounded_year_end_dates_match_the_cell_s_date():
    # 52/53-week filers: the data set shows 2020-09-30 for the balance sheet of 2020-09-27 (0001792044)
    assert qe._column(date(2020, 9, 27), frozenset({date(2020, 9, 30)})) == date(
        2020, 9, 30
    )
    assert qe._column(date(2020, 9, 27), frozenset({date(2019, 9, 30)})) is None
    assert qe._column(
        date(2020, 9, 30), frozenset({date(2020, 9, 30), date(2020, 9, 27)})
    ) == date(2020, 9, 30)
    c = load(
        tables(periodic=[(date(2020, 9, 27), ACC)]),
        {ACC: AF({date(2020, 9, 30)}, {date(2020, 9, 30)})},
    )
    assert (
        c.face_by_date == {date(2020, 9, 27): qe.PeriodFace(True, False)}
        and not c.face_hide_dates
    )


def test_a_filing_missing_from_the_data_set_is_kept_after_2009_and_hidden_before():
    # 0001162896 / 0001314102 are readable statements the data set lacks: kept. EOG 2008/2009: no machine-readable pages: hidden
    c = load(
        tables(
            periodic=[
                (date(2019, 3, 31), "0001493152-19-007263"),
                (date(2008, 12, 31), "0000821189-09-000047"),
            ]
        ),
        {},
    )
    assert c.face_hide_dates == {date(2008, 12, 31)} and not c.face_by_date
    assert (
        qe._accession_year("0000821189-09-000047") == 2009
        and qe._accession_year("0001193125-16-708358") == 2016
    )


def test_omc_work_in_process_is_excluded_in_all_years_after_the_note_was_read():
    # OMC 2015-2016: 10-K FY2016 0000029989-17-000004 Note 2 (client billable costs); 2017-2019 the contract-asset guard
    assert (
        "0000029989" in qe.CONTRACT_ASSET_NOTE_READ
        and "0000029989-17-000004" in qe.CONTRACT_ASSET_NOTE_READ["0000029989"]
    )
    face = {ACC: AF({END}, {END}, (), wip={END})}
    omc = load(tables(cik="0000029989", periodic=[(END, ACC)]), face)
    assert omc.face_by_date == {
        END: qe.PeriodFace(False, False)
    }  # no inventory line: the stored value stays
    other = load(tables(cik="0000000007", periodic=[(END, ACC)]), face)
    assert other.face_by_date == {
        END: qe.PeriodFace(True, False)
    }  # without a read note a WIP caption never excludes it
    mixed = load(
        tables(cik="0000029989", periodic=[(END, ACC)]),
        {ACC: AF({END}, {END}, (), wip=())},
    )  # real inventory beside WIP
    assert mixed.face_by_date == {END: qe.PeriodFace(True, False)}


def test_inventory_concept_loader_drops_mapped_and_non_balance_sheet_tags():
    conn = _Conn({
        "from analytics.concept_mapping": [(1,)],
        "from core.concept": [(1, "InventoryNet"), (2, "InventoryCrudeOilProductsAndMerchandise"), (3, "InventoryWriteDown"), (4, "OtherInventorySupplies"), (5, "MaterialsSuppliesAndOther")],
    })  # fmt: skip
    like, mapped = qe.load_inventory_concept_ids(conn)
    assert like == [2, 4] and mapped == {1}


# ---------------------------------------------------------------- the dry-run planner
def _planner_conn(
    context_rows, have_inventory=((2, END),), stored=None, current=None, periodic=None
):
    t = {
        "select id from analytics.metric_definition where metric_name = 'quick_ratio'": [(7,)],
        "select id from analytics.metric_definition where metric_name = 'current_ratio'": [(8,)],
        "select id from analytics.canonical_concept": [(50,)],
        "select id, cik from core.company": [(1, "0000320187"), (2, "0000012927")],
        "from analytics.concept_mapping": [],
        "from core.concept": [],
        "from analytics.canonical_fact cf": list(have_inventory),
    }  # fmt: skip
    t |= tables(
        periodic=periodic
        or [(END, "0000000001-26-000001"), (D0, "0000000001-25-000003")],
        facts=context_rows,
    )
    t["select cik from core.company"] = [("0000000005",)]
    t = {
        "select id, cik from core.company": [(1, "0000320187"), (2, "0000012927")],
        **t,
    }
    calls = iter([
        stored or [(1, END, "Q2", D("2.075")), (2, END, "Q2", D("1.138")), (1, D0, "Q2", D("2.0"))],
        current or [(1, END, D("2.075")), (2, END, D("1.138")), (1, D0, D("2.5"))],
    ])  # fmt: skip

    class Conn(_Conn):
        def cursor(self):
            cur = _Cur(self.t)
            orig = cur.execute

            def execute(sql, params=None):
                if "from analytics.metric_value" in " ".join(sql.split()).lower():
                    cur.rows = next(calls)
                    return
                if (
                    "select id, cik from core.company" in " ".join(sql.split()).lower()
                    or "where id = any" in sql
                ):
                    cur.rows = [(1, "0000320187"), (2, "0000012927")]
                    return
                orig(sql, params)

            cur.execute = execute
            return cur

    return Conn(t)


def test_planner_hides_a_value_that_equals_the_current_ratio_and_flags_one_that_does_not():
    # 18 of 20 drawn presented-not-extracted cells store exactly the face quick ratio: inventory WAS subtracted, only our
    # canonical fact is missing now. Hide only stored == current ratio; flag_keep the rest.
    face = {
        "0000000001-26-000001": AF({END}, {END}),
        "0000000001-25-000003": AF({D0}, {D0}),
    }
    got = qe.plan_quick_ratio(_planner_conn([]), [1, 2], face=face)
    by = {(p.company_id, p.period_end): (p.reason, p.outcome) for p in got}
    assert by == {
        (1, "2026-06-30"): (qe.REASON_PRESENTED, "hide"),  # 2.075 == current 2.075
        (1, "2025-06-30"): (qe.REASON_PRESENTED, "flag_keep"),  # 2.0 != current 2.5
    }


def test_planner_leaves_cells_alone_where_the_period_foots_or_its_own_date_shows_no_line():
    shows_none = {"0000000001-26-000001": AF({END}), "0000000001-25-000003": AF({D0})}
    assert qe.plan_quick_ratio(_planner_conn([]), [1, 2], face=shows_none) == []
    comparative_only = {
        "0000000001-26-000001": AF({END, D0}, {D0}),
        "0000000001-25-000003": AF({D0}),
    }  # a value only in the comparative column
    assert qe.plan_quick_ratio(_planner_conn([]), [1, 2], face=comparative_only) == []
    foot = [(END, "AssetsCurrent", D(100)), (END, "CashAndCashEquivalentsAtCarryingValue", D(100)),
            (D0, "AssetsCurrent", D(100)), (D0, "CashAndCashEquivalentsAtCarryingValue", D(100))]  # fmt: skip
    assert (
        qe.plan_quick_ratio(
            _planner_conn(foot), [1, 2], face={"0000000001-26-000001": AF({END}, {END})}
        )
        == []
    )
    assert (
        qe.plan_quick_ratio(
            _planner_conn([]), [1, 2], face={"0000000001-26-000001": AF({END, D0})}
        )
        == []
    )  # kept, flagged


def test_planner_hides_cells_whose_statement_does_not_show_the_date():
    # 0001907982 2020-12-31: a 10-K/A that shows newer columns only. The other date's filing is simply not in the data
    # set (after 2009): its value stays, flagged.
    got = qe.plan_quick_ratio(
        _planner_conn([]), [1, 2], face={"0000000001-26-000001": AF({date(2022, 12, 31)}, {date(2022, 12, 31)})}
    )  # fmt: skip
    assert {(p.period_end, p.reason) for p in got} == {
        ("2026-06-30", qe.REASON_UNAVAILABLE)
    }


def test_planner_lists_cells_with_an_inventory_value_and_a_materials_line():
    face = {
        "0000000001-26-000001": AF({END}, {END}, {END}),
        "0000000001-25-000003": AF({D0}, {D0}),
    }
    got = qe.plan_quick_ratio(_planner_conn([]), [1, 2], face=face)
    assert [(p.company_id, p.reason, p.outcome) for p in got if p.company_id == 2] == [(2, qe.REASON_PRESENTED if False else qe.REASON_MATERIALS, "hide")]  # fmt: skip


def test_materials_by_face_hides_cells_that_stay():
    # FDX 'Spare parts, supplies, and fuel', ConEd 'Fuel oil, gas in storage, materials and supplies'
    t = {
        "select id from analytics.metric_definition": [(7,)],
        "select id, cik from core.company": [(1, "0000000001")],
        "from analytics.metric_value": [(1, END, "Q2", D("1.4754")), (1, D0, "Q2", D("1.0"))],
        "from core.filing where": [(1, END, "acc-m"), (1, D0, "acc-n")],
    }  # fmt: skip
    face = {"acc-m": AF({END}, {END}, {END}), "acc-n": AF({D0}, {D0})}
    got = qe.plan_materials_by_face(_Conn(t), [1], face)
    assert [(p.period_end, p.reason, p.outcome) for p in got] == [
        ("2026-06-30", qe.REASON_MATERIALS, "hide")
    ]


# ---- a stored-right value whose inventory fact is demoted must not become the current ratio at the next recompute
TXN_2018 = (
    D(8097) * D(1000000),
    D(2474) * D(1000000),
    D(2217) * D(1000000),
)  # CA, CL, inventories (0000097476-19-000007)


def _recompute(monkeypatch, ca, cl, inv, context, rule_on):
    by_end = {
        CA: {END: (ca, [1])},
        CL: {END: (cl, [3])},
    }  # the inventory fact is missing from canonical data now
    by_period = {CA: {10: (ca, [1])}, CL: {10: (cl, [3])}}
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
        lambda conn, cid, like_ids=None, face=None, mapped_ids=None: context,
    )
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    calc.calculate_for_company(conn, 1, _target())
    return cur.executemany.call_args.args[1][0]


@pytest.mark.parametrize(
    ("label", "nonauth", "member", "reason"),
    [
        ("TXN 2018: the InventoryNet copy was demoted to non-authoritative", True, {}, qe.REASON_NOT_AUTHORITATIVE),
        ("NKE-type: no inventory fact, authoritative member sub-lines", False, {"InventoryFinishedGoodsNetOfReserves": D(2217)}, qe.REASON_REVIEW),
        ("NKE-type: no inventory fact, no member value", False, {}, qe.REASON_PRESENTED),
    ],
)  # fmt: skip
def test_a_right_stored_value_whose_inventory_fact_is_gone_is_hidden_not_turned_into_the_current_ratio(
    monkeypatch, label, nonauth, member, reason
):
    ca, cl, inv = TXN_2018
    lines = {"AssetsCurrent": ca, "CashAndCashEquivalentsAtCarryingValue": ca / 4}
    context = qe.Context(
        False, {END: lines}, {END: {k: v * D(1000000) for k, v in member.items()}}, {}, {END: qe.PeriodFace(True, False)},
        frozenset(), frozenset({END}) if nonauth else frozenset(),
    )  # fmt: skip
    current_ratio = ca / cl
    right = (ca - inv) / cl
    assert abs(right - D("2.3767")) < D(
        "0.0001"
    )  # the value that was stored and is right
    off = _recompute(monkeypatch, ca, cl, inv, context, rule_on=False)
    assert off["value"] == current_ratio  # the live code today: the wrong number
    on = _recompute(monkeypatch, ca, cl, inv, context, rule_on=True)
    assert (
        on["value"] is None
        and on["value"] != current_ratio
        and on["is_null_reason"] == reason
    ), label


def test_when_the_face_shows_no_inventory_line_the_zero_stands_on_recompute(
    monkeypatch,
):
    ca, cl, inv = TXN_2018
    context = qe.Context(
        False, {END: {"AssetsCurrent": ca}}, {}, {}, {END: qe.PeriodFace(False, False)}
    )
    row = _recompute(monkeypatch, ca, cl, inv, context, rule_on=True)
    assert row["value"] == ca / cl and row["is_null_reason"] is None


# ---------------------------------------------------------------- Verifier 2 V5 (VERIFY-QUICK-RATIO-5-2026-10-26)
RAVE_Q2, RAVE_Q3 = date(2023, 12, 24), date(2024, 3, 24)


def test_fsds_rounds_to_the_nearest_month_end_even_seven_days_away():
    # RAVE (0000718332) 10-Qs 0001140361-24-005023 / -023848: the data set shows 2023-12-31 and 2024-03-31 for the
    # balance sheets of 2023-12-24 and 2024-03-24 (7 days); a fixed 6-day window called the statement unavailable
    assert qe._column(RAVE_Q2, frozenset({date(2023, 12, 31)})) == date(2023, 12, 31)
    assert qe._column(RAVE_Q3, frozenset({date(2024, 3, 31)})) == date(2024, 3, 31)
    assert qe._column(date(2021, 9, 2), frozenset({date(2021, 8, 31)})) == date(
        2021, 8, 31
    )  # MU
    # the rounding is to ONE month end; never to the next nearest column in the set
    assert qe._column(date(2024, 3, 10), frozenset({date(2024, 3, 31)})) is None
    assert qe._column(RAVE_Q2, frozenset({date(2023, 9, 30)})) is None


def test_rave_readable_statement_with_no_inventory_line_keeps_the_value():
    acc2, acc3 = "0001140361-24-005023", "0001140361-24-023848"
    face = {
        acc2: AF({date(2023, 9, 30), date(2023, 12, 31)}),
        acc3: AF({date(2023, 9, 30), date(2024, 3, 31)}),
    }
    c = load(tables(periodic=[(RAVE_Q2, acc2), (RAVE_Q3, acc3)]), face)
    assert not c.face_hide_dates
    assert c.face_by_date == {
        RAVE_Q2: qe.PeriodFace(False, False),
        RAVE_Q3: qe.PeriodFace(False, False),
    }
    for d in (RAVE_Q2, RAVE_Q3):
        assert qe.inventory_missing_reason(c, d, NOFOOT["AssetsCurrent"]) is None


def test_eog_2015_q1_statement_is_readable_so_the_reason_is_presented_not_unavailable():
    # EOG 10-Q 0000821189-15-000023: the face shows 2015-03-31 with "Inventories" (current assets 4,793,368 thousand)
    acc, d = "0000821189-15-000023", date(2015, 3, 31)
    c = load(
        tables(periodic=[(d, acc)]),
        {acc: AF({date(2014, 12, 31), d}, {date(2014, 12, 31), d})},
    )
    assert c.face_by_date == {d: qe.PeriodFace(True, False)} and not c.face_hide_dates
    assert (
        qe.inventory_missing_reason(c, d, NOFOOT["AssetsCurrent"])
        == qe.REASON_PRESENTED
    )


def test_an_unclassified_balance_sheet_hides_the_quick_ratio_with_or_without_inventory():
    # FTAI 10-K FY2023 0001590364-24-000003: Total assets / Total liabilities only, no current subtotals; stored 1.9511
    acc, d = "0001590364-24-000003", date(2023, 12, 31)
    c = load(tables(periodic=[(d, acc)]), {acc: AF({d}, {d}, classified=False)})
    assert c.face_by_date == {d: qe.PeriodFace(True, False, True)}
    assert (
        qe.inventory_missing_reason(c, d, NOFOOT["AssetsCurrent"])
        == qe.REASON_UNCLASSIFIED
    )
    assert (
        qe.materials_supplies_reason(c, d, NOFOOT["AssetsCurrent"])
        == qe.REASON_UNCLASSIFIED
    )
    # it outranks every other cause (materials on the face, a foot that would keep the zero)
    both = qe.Context(None, {d: NOFOOT}, {}, {}, {d: qe.PeriodFace(True, True, True)})
    assert qe.hide_cause(both, d, None, inventory_present=False) == "unclassified"
    foots = M(AssetsCurrent=100, CashAndCashEquivalentsAtCarryingValue=100)
    assert qe.hide_cause(qe.Context(None, {d: foots}, {}, {}, {d: qe.PeriodFace(False, False, True)}),
                         d, None, inventory_present=False) == "unclassified"  # fmt: skip


def test_calculate_hides_a_computed_quick_ratio_on_an_unclassified_balance_sheet(
    monkeypatch,
):
    ca, *_ = FIXTURES["NKE"]
    c = qe.Context(
        None,
        {END: {"AssetsCurrent": ca}},
        {},
        {},
        {END: qe.PeriodFace(True, False, True)},
    )
    row = _run(monkeypatch, "NKE", with_inventory=True, rule_on=True, context=c)
    assert row["value"] is None and row["is_null_reason"] == qe.REASON_UNCLASSIFIED
    off = _run(monkeypatch, "NKE", with_inventory=True, rule_on=False, context=c)
    assert off["value"] is not None  # flag off: nothing changes


def test_planner_hides_an_unclassified_cell_even_when_it_differs_from_the_current_ratio():
    face = {
        "0000000001-26-000001": AF({END}, {END}, classified=False),  # 2.075 == current
        "0000000001-25-000003": AF(
            {D0}, {D0}, classified=False
        ),  # 2.0 != current 2.5: hidden, not flag_keep
    }
    got = qe.plan_quick_ratio(_planner_conn([]), [1, 2], face=face)
    by = {(p.company_id, p.period_end): (p.reason, p.outcome) for p in got}
    assert by == {
        (1, "2026-06-30"): (qe.REASON_UNCLASSIFIED, "hide"),
        (1, "2025-06-30"): (qe.REASON_UNCLASSIFIED, "hide"),
        (2, "2026-06-30"): (
            qe.REASON_UNCLASSIFIED,
            "hide",
        ),  # an inventory value exists: hidden all the same
    }
