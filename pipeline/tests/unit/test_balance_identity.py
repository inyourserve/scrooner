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


# ------------------------------------------------------------------ V2 fixes (Verifier, 2026-10-24)
def test_including_nci_temporary_equity_element_is_spelled_as_filed_and_is_loaded():
    # core.concept 32640 ends in ...Interests; the singular spelling matched nothing (AMRX)
    assert bi.TEMP_INCL.endswith("AttributableToNoncontrollingInterests")
    assert bi.TEMP_INCL in bi.LOAD_TAGS and bi.TEMP_INCL in bi.ADJUSTMENT_TAGS


def test_amrx_including_nci_temporary_equity_is_subtracted():
    # AMRX 2023-12-31 (0001723128-24-000014 R5): liabilities 3,411.265, redeemable NCI 41.293 outside
    a = amt("total_liabilities_resolved", 5000, "1547.442", "StockholdersEquity", TEMP_INCL=41.293)  # fmt: skip
    assert a.value == Decimal("3411.265") * M


def test_mck_redeemable_nci_on_the_common_carrying_amount_element_is_subtracted():
    # MCK 2015-06-30 (0000927653-15-000006 R4): 34,673 + 8,142 + 2,741 = 45,556; RNCI 1,430 outside
    adj = {bi.TEMP_REDEEMABLE_PARTS[0]: Decimal(1430) * M}
    a = bi.identity_amount("total_liabilities_resolved", Decimal(60000) * M, Decimal(13014) * M, "StockholdersEquity", adj)  # fmt: skip
    assert isinstance(a, bi.Amount) and a.value == Decimal(45556) * M


def test_etp_redeemable_nci_on_the_other_carrying_amount_element_is_subtracted():
    # ETP 2015-09-30 (0001276187-15-000094 R2): mezzanine = preferred units 33 + redeemable NCI 15
    adj = {
        bi.TEMP_PARENT: Decimal(33) * M,
        bi.TEMP_REDEEMABLE_PARTS[2]: Decimal(15) * M,
    }
    a = bi.identity_amount("total_liabilities_resolved", Decimal(52000) * M, Decimal(4880) * M, "StockholdersEquity", adj)  # fmt: skip
    assert isinstance(a, bi.Amount) and a.value == Decimal(52000 - 4880 - 48) * M


def test_redeemable_nci_total_element_wins_over_its_components():
    adj = {bi.TEMP_REDEEMABLE_NCI: Decimal(100) * M, bi.TEMP_REDEEMABLE_PARTS[0]: Decimal(60) * M, bi.TEMP_REDEEMABLE_PARTS[1]: Decimal(40) * M}  # fmt: skip
    a = bi.identity_amount("total_liabilities_resolved", Decimal(1000) * M, Decimal(400) * M, "StockholdersEquity", adj)  # fmt: skip
    assert isinstance(a, bi.Amount) and a.value == Decimal(500) * M


def test_ipg_redeemable_nci_only_on_a_fair_value_element_is_held_not_guessed():
    # IPG 2024-06-30: the face RNCI 460.8 is tagged FairValue; placement cannot be proven from the tag alone
    adj = {bi.TEMP_MEASURE_ONLY[0]: Decimal("460.8") * M}
    a = bi.identity_amount("total_liabilities_resolved", Decimal(25000) * M, Decimal(1000) * M, "StockholdersEquity", adj)  # fmt: skip
    assert a == bi.Held("redeemable_nci_measurement_only")


def test_a_fair_value_element_beside_a_carrying_amount_is_a_note_and_ignored():
    adj = {
        bi.TEMP_REDEEMABLE_NCI: Decimal(100) * M,
        bi.TEMP_MEASURE_ONLY[0]: Decimal(130) * M,
    }
    a = bi.identity_amount("total_liabilities_resolved", Decimal(1000) * M, Decimal(400) * M, "StockholdersEquity", adj)  # fmt: skip
    assert isinstance(a, bi.Amount) and a.value == Decimal(500) * M


def test_generic_temporary_equity_alone_is_read_but_beside_a_redeemable_nci_it_is_held():
    alone = bi.identity_amount("total_liabilities_resolved", Decimal(1000) * M, Decimal(400) * M, "StockholdersEquity", {bi.TEMP_GENERIC: Decimal(50) * M})  # fmt: skip
    assert isinstance(alone, bi.Amount) and alone.value == Decimal(550) * M
    both = bi.identity_amount("total_liabilities_resolved", Decimal(1000) * M, Decimal(400) * M, "StockholdersEquity", {bi.TEMP_GENERIC: Decimal(50) * M, bi.TEMP_REDEEMABLE_NCI: Decimal(10) * M})  # fmt: skip
    assert both == bi.Held("temporary_equity_generic_overlaps_redeemable_nci")


def test_equity_direction_is_held_when_no_nci_fact_is_read():
    # BX 2019-06-30 / KKR 2015-06-30: assets - liabilities is total partners' capital incl NCI, not the parent
    a = bi.identity_amount(
        "stockholders_equity_resolved", Decimal(1000) * M, Decimal(600) * M, None, {}
    )
    assert a == bi.Held("nci_not_read")
    p = bi.identity_amount("stockholders_equity_resolved", Decimal(1000) * M, Decimal(600) * M, None, {bi.NCI_UNREAD[0]: Decimal(300) * M})  # fmt: skip
    assert p == bi.Held("nci_on_unmapped_partnership_elements")


def test_liabilities_from_parent_equity_are_held_when_nci_sits_on_partnership_elements():
    adj = {bi.NCI_UNREAD[1]: Decimal(300) * M}
    a = bi.identity_amount("total_liabilities_resolved", Decimal(1000) * M, Decimal(400) * M, "PartnersCapital", adj)  # fmt: skip
    assert a == bi.Held("nci_on_unmapped_partnership_elements")
    # a read NCI total makes the unmapped element irrelevant
    adj[bi.NCI] = Decimal(300) * M
    b = bi.identity_amount("total_liabilities_resolved", Decimal(1000) * M, Decimal(400) * M, "PartnersCapital", adj)  # fmt: skip
    assert isinstance(b, bi.Amount) and b.value == Decimal(300) * M


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


A, L, E = 1, 2, 3
T = {  # concept ids
    "MinorityInterest": 10, bi.NCI_INCLUSIVE_EQUITY: 11, bi.TEMP_REDEEMABLE_NCI: 12, "StockholdersEquity": 13,
    "Assets": 14, bi.LSE: 15, bi.NCI_UNREAD[0]: 16,
}  # fmt: skip
F1, F2 = 900, 901  # filings


def canon(pid, concept, value, src, end):
    return (1134, pid, concept, Decimal(value) * M, src, end)


def fact(pid, filing, tag, value, fid):
    return (1134, pid, filing, T[tag], Decimal(value) * M, fid)


def tables(canonical, facts, info):
    return {
        "from analytics.canonical_concept": [("total_assets_resolved", A), ("total_liabilities_resolved", L), ("stockholders_equity_resolved", E)],
        "from core.concept where tag": [(i, t) for t, i in T.items()],
        "from core.company": [(1134, "0000104169")],
        "from analytics.canonical_fact cf join core.period": canonical,
        "from core.fact f where": facts,
        "from core.fact f join core.concept": info,
    }  # fmt: skip


from datetime import date

D1, D2, D3, D4, D5, D6, D7, D8 = (date(2026, 7, 31), date(2026, 4, 30), date(2026, 1, 31), date(2025, 10, 31),
                                  date(2025, 7, 31), date(2025, 4, 30), date(2025, 1, 31), date(2024, 10, 31))  # fmt: skip
CANON = [
    # 77: the WMT cell, one filing: legacy-derived liabilities 202,237 (= 100 + 200 + adjustment facts)
    canon(77, A, 293914, [100], D1), canon(77, E, 97945, [200], D1), canon(77, L, 202237, [100, 200, 301], D1),
    # 78: empty liabilities cell
    canon(78, A, 1000, [101], D2), canon(78, E, 400, [201], D2),
    # 79: a real Liabilities tag value (no assets ids in the source): untouched
    canon(79, A, 1000, [102], D3), canon(79, E, 400, [202], D3), canon(79, L, 555, [999], D3),
    # 80: carries the assets ids but not the equity ids; 82: the equity ids but not the assets ids
    canon(80, A, 1000, [103], D4), canon(80, E, 400, [203], D4), canon(80, L, 777, [103, 998], D4),
    canon(82, A, 1000, [105], D6), canon(82, E, 400, [205], D6), canon(82, L, 777, [205, 997], D6),
    # 81: derived and already correct
    canon(81, A, 1000, [104], D5), canon(81, E, 400, [204], D5), canon(81, L, 600, [104, 204], D5),
    # 83: equity input is the NCI-inclusive tag next to a parent-equity tag
    canon(83, A, 1000, [106], D7), canon(83, E, 400, [206, 207], D7),
    # 84: IRM: original-10-K assets (filing 900) with restated equity (filing 901)
    canon(89, A, 1000, [113, 114], date(2023, 7, 31)), canon(89, E, 400, [213], date(2023, 7, 31)), canon(89, L, 800, [113, 114, 213], date(2023, 7, 31)),
    canon(88, A, 1000, [112], date(2023, 10, 31)), canon(88, E, 400, [212], date(2023, 10, 31)), canon(88, L, 800, [112, 212], date(2023, 10, 31)),
    canon(84, A, 1000, [108], D8), canon(84, E, 400, [208], D8), canon(84, L, 800, [108, 208], D8),
    # 85: L&SE (1000.2) differs from assets (1000) in the same filing (BRKR)
    canon(85, A, 1000, [109], date(2024, 7, 31)), canon(85, E, 400, [209], date(2024, 7, 31)),
    # 86: adjustment fact of ANOTHER filing for the same instant must not be used
    canon(86, A, 1000, [110], date(2024, 4, 30)), canon(86, E, 400, [210], date(2024, 4, 30)),
    # 87: equity direction without an NCI fact (BX/KKR)
    canon(87, A, 1000, [111], date(2024, 1, 31)), canon(87, L, 600, [211], date(2024, 1, 31)),
]  # fmt: skip
FACTS = [
    fact(77, F1, "MinorityInterest", 6561, 301), fact(77, F1, bi.NCI_INCLUSIVE_EQUITY, 104506, 302), fact(77, F1, bi.TEMP_REDEEMABLE_NCI, 293, 303),
    fact(85, F1, bi.LSE, "1000.2", 304),
    fact(84, F1, "StockholdersEquity", 450, 307),
    fact(86, F2, bi.TEMP_REDEEMABLE_NCI, 100, 305),
    fact(87, F1, bi.NCI_UNREAD[0], 300, 306),
]  # fmt: skip
INFO = [(i, "Assets", F1) for i in (113, 112, 100, 101, 102, 103, 104, 105, 106, 108, 109, 110, 111)] + [
    (200, "StockholdersEquity", F1), (201, "StockholdersEquity", F1), (202, "StockholdersEquity", F1),
    (203, "StockholdersEquity", F1), (204, "StockholdersEquity", F1), (205, "StockholdersEquity", F1),
    (206, bi.NCI_INCLUSIVE_EQUITY, F1), (207, "StockholdersEquity", F1), (208, "StockholdersEquity", F2),
    (209, "StockholdersEquity", F1), (210, "StockholdersEquity", F1), (211, "Liabilities", F1), (212, "StockholdersEquity", F2), (114, "Assets", F2), (213, "StockholdersEquity", F1),
]  # fmt: skip
TABLES = tables(CANON, FACTS, INFO)


def planned():
    conn = Conn(TABLES)
    plan = bi.plan_identity(conn, [1134])
    return conn, {(p.period_end, p.concept[:5]): p for p in plan}


def test_planner_replaces_a_row_this_fallback_wrote_fills_an_empty_cell_and_leaves_a_tag_value():
    conn, by = planned()
    r = by[("2026-07-31", "total")]
    assert (r.kind, r.before, r.after) == (
        "replace",
        str(Decimal(202237) * M),
        str(Decimal(189115) * M),
    )
    assert r.equity_tag == "StockholdersEquity" and r.filing_id == F1
    assert r.legacy_adjustment == str(Decimal(6561 + 293) * M)
    assert {100, 200, 301, 302, 303} <= set(
        r.source_fact_ids
    )  # lineage: base, equity and the adjustment facts
    f = by[("2026-04-30", "total")]
    assert (f.kind, f.before, f.after) == ("fill", None, str(Decimal(600) * M))
    # untouched: a real tag value, rows missing one side's source ids, and a derived row that is already right
    for d in ("2026-01-31", "2025-10-31", "2025-04-30", "2025-07-31"):
        assert (d, "total") not in by
    # only the adjustment elements of the SAME filing are read, one value per filing
    assert any("f.filing_id" in " ".join(q.split()) for q, _ in conn.cur.sql)


def test_the_nci_inclusive_tag_among_the_equity_sources_is_recorded_as_the_input():
    _, by = planned()
    p = by[("2025-01-31", "total")]
    assert p.equity_tag == bi.NCI_INCLUSIVE_EQUITY and p.basis.startswith(
        "equity_nci_inclusive"
    )


def test_mixed_vintage_is_solved_inside_the_assets_filing_from_its_own_equity():
    # IRM 2018-12-31: original 10-K assets with the restated 10-K equity -> the old 10-K's own equity is used
    _, by = planned()
    p = by[("2024-10-31", "total")]
    assert (p.kind, p.after, p.filing_id) == ("replace", str(Decimal(550) * M), F1)
    assert (
        p.equity_tag == "StockholdersEquity"
        and 307 in p.source_fact_ids
        and 208 not in p.source_fact_ids
    )


def test_assets_that_themselves_span_two_filings_give_no_value():
    _, by = planned()
    assert by[("2023-07-31", "total")].basis == "mixed_vintage"


def test_mixed_vintage_without_the_equity_in_the_assets_filing_gives_no_value():
    _, by = planned()
    p = by[("2023-10-31", "total")]
    assert (p.kind, p.after, p.basis) == ("hold", None, "mixed_vintage") and p.before == str(Decimal(800) * M)  # fmt: skip


def test_base_is_liabilities_and_equity_when_filed_in_the_same_filing():
    _, by = planned()
    p = by[("2024-07-31", "total")]
    assert p.after == str(Decimal("600.2") * M) and p.basis.endswith(
        "base_lse"
    )  # BRKR: 1,000.2 - 400
    assert by[("2026-04-30", "total")].basis.endswith("base_assets")


def test_an_adjustment_filed_in_another_filing_is_not_used():
    _, by = planned()
    p = by[("2024-04-30", "total")]
    assert p.after == str(
        Decimal(600) * M
    )  # the 100 redeemable NCI belongs to filing 901, the cell to filing 900


def test_equity_direction_without_an_nci_fact_is_a_hold_in_the_plan():
    _, by = planned()
    p = by[("2024-01-31", "stock")]
    assert (p.kind, p.after, p.basis) == (
        "hold",
        None,
        "nci_on_unmapped_partnership_elements",
    )


def test_apply_writes_replacements_and_fills_only_and_never_a_hold(tmp_path):
    plan = bi.plan_identity(Conn(TABLES), [1134])
    conn = Conn(
        {
            **TABLES,
            "update analytics.canonical_fact": [],
            "insert into analytics.canonical_fact": [],
        }
    )
    n = bi.apply_identity(conn, plan, tmp_path / "img.jsonl")
    sqls = [" ".join(s.split()).lower() for s, _ in conn.cur.sql]
    kinds = [p.kind for p in plan]
    assert n == kinds.count("replace") + kinds.count("fill") and "hold" in kinds
    assert sum(s.startswith("update") for s in sqls) == kinds.count("replace")
    assert sum(s.startswith("insert") for s in sqls) == kinds.count("fill")
    assert conn.commits == 1 and not any("delete" in s for s in sqls)
    rows = [json.loads(x) for x in (tmp_path / "img.jsonl").read_text().splitlines()]
    assert {r["kind"] for r in rows} == {"replace", "fill", "hold"}


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
