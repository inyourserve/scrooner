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


def D_(**kw):
    return {getattr(bi, k): Decimal(str(v)) * M for k, v in kw.items()}


def liab(base, other, tag, adj, nci_family=False, temp_family=False):
    return bi.identity_amount(
        "total_liabilities_resolved", Decimal(str(base)) * M, Decimal(str(other)) * M, tag, adj, nci_family, temp_family
    )  # fmt: skip


def test_strict_mode_reads_only_whole_line_elements_and_holds_components():
    # NI 2023-12-31 (0001111711-24-000011 R6): 1,360 on the Other component is not on the balance sheet
    comp = liab(
        30000,
        8000,
        "StockholdersEquity",
        {bi.TEMP_REDEEMABLE_PARTS[2]: Decimal(1360) * M},
    )
    assert comp == bi.Held("redeemable_nci_component_not_proven_on_face")
    # IPG: FairValue elements alone
    assert liab(25000, 1000, "StockholdersEquity", {bi.TEMP_MEASURE_ONLY[0]: Decimal(460) * M}) == bi.Held("redeemable_nci_measurement_only")  # fmt: skip
    assert liab(1000, 400, "StockholdersEquity", {bi.TEMP_GENERIC: Decimal(50) * M}) == bi.Held("temporary_equity_generic_not_proven_on_face")  # fmt: skip
    # whole-line elements are read: the redeemable NCI total, the parent line, the including-NCI element
    assert liab(1000, 400, "StockholdersEquity", {bi.TEMP_REDEEMABLE_NCI: Decimal(100) * M}).value == Decimal(500) * M  # fmt: skip
    assert liab(1000, 400, "StockholdersEquity", {bi.TEMP_PARENT: Decimal(100) * M}).value == Decimal(500) * M  # fmt: skip


def test_a_carrying_total_beside_measurement_elements_ignores_the_note_figures():
    adj = {
        bi.TEMP_REDEEMABLE_NCI: Decimal(100) * M,
        bi.TEMP_MEASURE_ONLY[0]: Decimal(130) * M,
    }
    assert liab(1000, 400, "StockholdersEquity", adj).value == Decimal(500) * M


def test_nci_inclusive_total_must_equal_parent_equity_plus_minority_interest():
    # FE 2018-03-31 (0001031296-18-000031 R5): an 86M NCI-inclusive fact that is not the face total
    parent, incl = 10000, 10086
    held = liab(
        40000,
        parent,
        "StockholdersEquity",
        {bi.NCI_INCLUSIVE_EQUITY: Decimal(incl) * M},
    )
    assert held == bi.Held("nci_inclusive_total_without_minority_interest")
    bad = liab(40000, parent, "StockholdersEquity", {bi.NCI_INCLUSIVE_EQUITY: Decimal(incl) * M, bi.NCI: Decimal(500) * M})  # fmt: skip
    assert bad == bi.Held("nci_inclusive_total_disagrees_with_minority_interest")
    ok = liab(40000, parent, "StockholdersEquity", {bi.NCI_INCLUSIVE_EQUITY: Decimal(incl) * M, bi.NCI: Decimal(86) * M})  # fmt: skip
    assert ok.value == Decimal(40000 - incl) * M
    same = liab(
        40000,
        parent,
        "StockholdersEquity",
        {bi.NCI_INCLUSIVE_EQUITY: Decimal(parent) * M},
    )  # no NCI at all
    assert same.value == Decimal(30000) * M


def test_temporary_equity_family_without_a_read_element_holds_but_a_read_element_is_enough():
    adj = {bi.TEMP_PARENT: Decimal(100) * M}
    assert liab(1000, 400, "StockholdersEquity", {}, temp_family=True) == bi.Held("temporary_equity_present_not_read")  # fmt: skip
    assert liab(1000, 400, "StockholdersEquity", adj, temp_family=True).value == Decimal(500) * M  # fmt: skip
    assert liab(1000, 400, "StockholdersEquity", {}).value == Decimal(600) * M


def test_parent_equity_alone_needs_a_filing_without_any_nci_element():
    assert liab(1000, 400, "StockholdersEquity", {}).value == Decimal(600) * M
    assert liab(1000, 400, "StockholdersEquity", {}, nci_family=True) == bi.Held(
        "nci_unconfirmed"
    )


def test_equity_direction_accepts_no_nci_only_when_the_filing_has_none():
    eq = lambda adj, fam: bi.identity_amount(
        "stockholders_equity_resolved",
        Decimal(1000) * M,
        Decimal(600) * M,
        None,
        adj,
        fam,
    )  # noqa: E731
    assert eq({}, False).value == Decimal(400) * M  # AJG: no NCI anywhere in the filing
    assert eq({}, True) == bi.Held("nci_not_read")  # NCI exists but is not read
    assert eq({bi.NCI_UNREAD[0]: Decimal(300) * M}, True) == bi.Held(
        "nci_on_unmapped_partnership_elements"
    )
    assert (
        eq({bi.NCI: Decimal(30) * M, bi.TEMP_PARENT: Decimal(20) * M}, True).value
        == Decimal(350) * M
    )


def test_liabilities_from_parent_equity_are_held_when_nci_sits_on_partnership_elements():
    adj = {bi.NCI_UNREAD[1]: Decimal(300) * M}
    assert liab(1000, 400, "PartnersCapital", adj, True) == bi.Held(
        "nci_on_unmapped_partnership_elements"
    )
    adj[bi.NCI] = Decimal(300) * M
    assert liab(1000, 400, "PartnersCapital", adj, True).value == Decimal(300) * M


# --- with the filing's own face subtotals (LiabilitiesCurrent + LiabilitiesNoncurrent) the identity is a cross-check
def ref(base, other, tag, adj):
    return bi.reference_reading("total_liabilities_resolved", Decimal(str(base)) * M, Decimal(str(other)) * M, tag, adj)  # fmt: skip


def test_reference_reading_ignores_an_nci_inclusive_fact_that_is_not_the_total():
    # FE 2018-03-31 (0001031296-18-000031 R5): parent equity 7,375, a stray 86 'NCI-inclusive' fact; face 31,420
    assert (
        ref(
            38795,
            7375,
            "StockholdersEquity",
            {bi.NCI_INCLUSIVE_EQUITY: Decimal(86) * M},
        )
        == Decimal(31420) * M
    )


def test_reference_reading_uses_the_nci_inclusive_total_when_it_agrees_and_leaves_out_unproven_mezzanine():
    # NI 2023-12-31 (0001111711-24-000011 R6): 31,077.2 - 10,136.3 = 20,940.9; the 1,360 component is not subtracted
    adj = {bi.NCI_INCLUSIVE_EQUITY: Decimal("10136.3") * M, bi.NCI: Decimal("1866.7") * M, bi.TEMP_REDEEMABLE_PARTS[2]: Decimal(1360) * M}  # fmt: skip
    assert ref("31077.2", "8269.6", "StockholdersEquity", adj) == Decimal("20940.9") * M
    # parent + MinorityInterest when no inclusive total is filed; whole-line mezzanine is subtracted
    assert ref(1000, 400, "StockholdersEquity", {bi.NCI: Decimal(50) * M, bi.TEMP_PARENT: Decimal(30) * M}) == Decimal(520) * M  # fmt: skip
    # the equity input already is the total
    assert (
        ref(1000, 400, bi.NCI_INCLUSIVE_EQUITY, {bi.NCI: Decimal(50) * M})
        == Decimal(600) * M
    )
    # an inclusive total that disagrees with parent + MinorityInterest is ignored
    assert ref(1000, 400, "StockholdersEquity", {bi.NCI_INCLUSIVE_EQUITY: Decimal(900) * M, bi.NCI: Decimal(50) * M}) == Decimal(550) * M  # fmt: skip
    assert (
        bi.reference_reading(
            "stockholders_equity_resolved", Decimal(1), Decimal(1), None, {}
        )
        is None
    )


def sub(cur, noncur):
    return {
        bi.LIABILITIES_CURRENT: Decimal(str(cur)) * M,
        bi.LIABILITIES_NONCURRENT: Decimal(str(noncur)) * M,
    }


def test_ni_component_that_the_subtotals_do_not_confirm_is_dropped():
    # face liabilities 20,940.9; the 1,360 Other carrying amount would give 19,580.9
    adj = {bi.TEMP_REDEEMABLE_PARTS[2]: Decimal(1360) * M, **sub("7940.9", 13000)}
    a = liab(30000, "9059.1", "StockholdersEquity", adj)
    assert (
        a.value == Decimal("20940.9") * M
        and "confirmed_by_face_subtotals" in a.basis
        and "temp_zero" in a.basis
    )


def test_mck_component_that_the_subtotals_confirm_is_subtracted():
    # MCK 2015-06-30: face liabilities 45,556 with a 1,430 redeemable NCI outside
    adj = {bi.TEMP_REDEEMABLE_PARTS[0]: Decimal(1430) * M, **sub(30000, 15556)}
    a = liab(60000, 13014, "StockholdersEquity", adj)
    assert a.value == Decimal(45556) * M and "temp_zero" not in a.basis


def test_ipg_fair_value_element_is_read_when_the_subtotals_confirm_it():
    adj = {bi.TEMP_MEASURE_ONLY[0]: Decimal("460.8") * M, **sub(10000, "12667.5")}
    a = liab(25000, "1871.7", "StockholdersEquity", adj)
    assert a.value == Decimal("22667.5") * M


def test_awk_measurement_figure_that_is_not_on_the_face_is_ignored_when_the_subtotals_say_so():
    adj = {bi.TEMP_MEASURE_ONLY[0]: Decimal(8) * M, **sub(6000, 12000)}
    a = liab(25000, 7000, "StockholdersEquity", adj)
    assert a.value == Decimal(18000) * M


def test_trgp_unseen_mezzanine_makes_the_identity_disagree_with_the_subtotals_so_the_cell_is_held():
    # TRGP 2021-09-30: face liabilities 9,823.1; a 749.7 class-member mezzanine fact is not stored
    a = liab(12000, "1427.2", "StockholdersEquity", sub(3000, "6823.1"))
    assert a == bi.Held("identity_not_confirmed_by_face_subtotals")


def test_fe_nci_inclusive_fact_that_is_not_the_total_loses_to_the_subtotals():
    # FE 2018-03-31: face 31,420; the 86 'NCI-inclusive' fact would give 38,709-type totals
    adj = {bi.NCI_INCLUSIVE_EQUITY: Decimal(8000) * M, **sub(10000, 21420)}
    a = liab(40000, 8580, "StockholdersEquity", adj)
    assert a.value == Decimal(31420) * M and a.basis.startswith("parent_equity_no_nci")


def test_subtotals_cannot_make_up_a_missing_pair():
    assert bi.face_subtotals({bi.LIABILITIES_CURRENT: Decimal(1)}) is None


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
    "Assets": 14, bi.LSE: 15, bi.NCI_UNREAD[0]: 16, bi.LIABILITIES_CURRENT: 17, bi.LIABILITIES_NONCURRENT: 18,
    bi.TEMP_REDEEMABLE_PARTS[2]: 19,
}  # fmt: skip
F1, F2, F3, F4, F5 = (
    900,
    901,
    902,
    903,
    904,
)  # filings; F4 carries NCI elements the planner does not read; F3 none


def canon(pid, concept, value, src, end):
    return (1134, pid, concept, Decimal(str(value)) * M, src, end)


def fact(pid, filing, tag, value, fid):
    return (1134, pid, filing, T[tag], Decimal(str(value)) * M, fid)


def tables(canonical, facts, info):
    return {
        "from analytics.canonical_concept": [("total_assets_resolved", A), ("total_liabilities_resolved", L), ("stockholders_equity_resolved", E)],
        "from core.concept where tag": [(i, t) for t, i in T.items()],
        "from core.company": [(1134, "0000104169")],
        "from analytics.canonical_fact cf join core.period": canonical,
        "ilike 'temporaryequity": [(1134, F5)],
        "select distinct f.company_id, f.filing_id": [(1134, F4)],
        "from core.fact f where": facts,
        "from core.fact f join core.concept": info,
    }  # fmt: skip


from datetime import date  # noqa: E402


def d(n):
    return date(2020, 1, 1 + n)


CANON = [
    # 77: the WMT cell, one filing: legacy-derived liabilities 202,237 (= 100 + 200 + adjustment facts)
    canon(77, A, 293914, [100], d(0)), canon(77, E, 97945, [200], d(0)), canon(77, L, 202237, [100, 200, 301], d(0)),
    canon(78, A, 1000, [101], d(1)), canon(78, E, 400, [201], d(1)),  # empty liabilities cell
    # 79: a real Liabilities tag value (no assets ids in the source): untouched
    canon(79, A, 1000, [102], d(2)), canon(79, E, 400, [202], d(2)), canon(79, L, 555, [999], d(2)),
    # 80: carries the assets ids but not the equity ids; 82: the equity ids but not the assets ids
    canon(80, A, 1000, [103], d(3)), canon(80, E, 400, [203], d(3)), canon(80, L, 777, [103, 998], d(3)),
    canon(82, A, 1000, [105], d(5)), canon(82, E, 400, [205], d(5)), canon(82, L, 777, [205, 997], d(5)),
    canon(81, A, 1000, [104], d(4)), canon(81, E, 400, [204], d(4)), canon(81, L, 600, [104, 204], d(4)),  # already right
    canon(83, A, 1000, [106], d(6)), canon(83, E, 400, [206, 207], d(6)),  # NCI-inclusive tag among the equity sources
    # 84: IRM: original-10-K assets (filing F1) with restated equity (F2); no filing carries both values
    canon(84, A, 1000, [108], d(7)), canon(84, E, 400, [208], d(7)), canon(84, L, 800, [108, 208], d(7)),
    # 90: OXY: identical copies in two filings; F1 carries BOTH values, so the terms are not mixed
    canon(90, A, 1000, [115], d(8)), canon(90, E, 400, [215], d(8)), canon(90, L, 777, [115, 215], d(8)),
    canon(85, A, 1000, [109], d(9)), canon(85, E, 400, [209], d(9)),  # L&SE 1000.2 in the same filing (BRKR)
    canon(86, A, 1000, [110], d(10)), canon(86, E, 400, [210], d(10)),  # adjustment of ANOTHER filing
    canon(87, A, 1000, [111], d(11)), canon(87, L, 600, [211], d(11)),  # equity direction, partnership NCI unread
    canon(91, A, 1000, [116], d(12)), canon(91, L, 600, [216], d(12)),  # AJG: a filing with no NCI element
    canon(93, A, 1000, [118], d(14)), canon(93, E, 400, [218], d(14)), canon(93, L, 777, [118, 218], d(14)),  # NCI elements exist in F4
    canon(94, A, 1000, [119], d(15)), canon(94, L, 600, [219], d(15)),  # equity direction in F4
    canon(95, A, 1000, [120], d(16)), canon(95, E, 400, [220], d(16)), canon(95, L, 777, [120, 220], d(16)),
    canon(96, A, 1000, [121], d(17)), canon(96, E, 400, [221], d(17)), canon(96, L, 777, [121, 221], d(17)),
    canon(97, A, 1000, [122], d(18)), canon(97, E, 400, [222], d(18)), canon(97, L, 777, [122, 222], d(18)),  # TRGP-like
    canon(92, A, 30000, [117], d(13)), canon(92, E, "9059.1", [217], d(13)),  # NI: face subtotals reject the component
]  # fmt: skip
FACTS = [
    fact(77, F1, "MinorityInterest", 6561, 301), fact(77, F1, bi.NCI_INCLUSIVE_EQUITY, 104506, 302), fact(77, F1, bi.TEMP_REDEEMABLE_NCI, 293, 303),
    fact(85, F1, bi.LSE, "1000.2", 304),
    fact(86, F2, bi.TEMP_REDEEMABLE_NCI, 100, 305),
    fact(87, F1, bi.NCI_UNREAD[0], 300, 306),
    fact(90, F1, "Assets", 1000, 308), fact(90, F1, "StockholdersEquity", 400, 309),
    fact(95, F1, "Assets", 900, 313), fact(95, F1, "StockholdersEquity", 400, 314),  # same equity value, other assets value
    fact(96, F1, "Assets", 1000, 315), fact(96, F1, "StockholdersEquity", 350, 316),  # same assets value, other equity value
    fact(92, F3, bi.TEMP_REDEEMABLE_PARTS[2], 1360, 310), fact(92, F3, bi.LIABILITIES_CURRENT, "7940.9", 311), fact(92, F3, bi.LIABILITIES_NONCURRENT, 13000, 312),
]  # fmt: skip
INFO = [(i, "Assets", F1) for i in (100, 101, 102, 103, 104, 105, 106, 108, 109, 110, 111)] + [
    (200, "StockholdersEquity", F1), (201, "StockholdersEquity", F1), (202, "StockholdersEquity", F1),
    (203, "StockholdersEquity", F1), (204, "StockholdersEquity", F1), (205, "StockholdersEquity", F1),
    (206, bi.NCI_INCLUSIVE_EQUITY, F1), (207, "StockholdersEquity", F1), (208, "StockholdersEquity", F2),
    (209, "StockholdersEquity", F1), (210, "StockholdersEquity", F1), (211, "Liabilities", F1), (216, "Liabilities", F3),
    (118, "Assets", F4), (218, "StockholdersEquity", F4), (119, "Assets", F4), (219, "Liabilities", F4), (122, "Assets", F5), (222, "StockholdersEquity", F5), (120, "Assets", F1), (220, "StockholdersEquity", F2), (121, "Assets", F1), (221, "StockholdersEquity", F2), (115, "Assets", F2), (116, "Assets", F3), (215, "StockholdersEquity", F1), (117, "Assets", F3), (217, "StockholdersEquity", F3),
]  # fmt: skip
TABLES = tables(CANON, FACTS, INFO)


def planned():
    conn = Conn(TABLES)
    plan = bi.plan_identity(conn, [1134])
    return conn, {(p.period_end, p.concept[:5]): p for p in plan}


def day(n):
    return str(d(n))


def test_planner_replaces_a_row_this_fallback_wrote_fills_an_empty_cell_and_leaves_a_tag_value():
    conn, by = planned()
    r = by[(day(0), "total")]
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
    f = by[(day(1), "total")]
    assert (f.kind, f.before, f.after) == ("fill", None, str(Decimal(600) * M))
    # untouched: a real tag value, rows missing one side's source ids, and a derived row that is already right
    for n in (2, 3, 5, 4):
        assert (day(n), "total") not in by
    assert any("f.filing_id" in " ".join(q.split()) for q, _ in conn.cur.sql)


def test_the_nci_inclusive_tag_among_the_equity_sources_is_recorded_as_the_input():
    _, by = planned()
    p = by[(day(6), "total")]
    assert p.equity_tag == bi.NCI_INCLUSIVE_EQUITY and p.basis.startswith(
        "equity_nci_inclusive"
    )


def test_terms_that_no_single_filing_carries_together_give_no_value():
    # IRM 2018-12-31: original 10-K assets with the restated 10-K equity
    _, by = planned()
    p = by[(day(7), "total")]
    assert (p.kind, p.after, p.basis) == ("hold", None, "mixed_vintage") and p.before == str(Decimal(800) * M)  # fmt: skip


def test_no_filing_carries_both_values_when_either_value_differs():
    _, by = planned()
    assert by[(day(16), "total")].basis == "mixed_vintage"
    assert by[(day(17), "total")].basis == "mixed_vintage"


def test_identical_values_in_two_filings_are_not_mixed_when_one_filing_carries_both():
    # OXY 2018-12-31: values are compared, not accessions
    _, by = planned()
    p = by[(day(8), "total")]
    assert (p.kind, p.after, p.filing_id) == ("replace", str(Decimal(600) * M), F1)
    assert 309 in p.source_fact_ids and 215 not in p.source_fact_ids


def test_base_is_liabilities_and_equity_when_filed_in_the_same_filing():
    _, by = planned()
    p = by[(day(9), "total")]
    assert p.after == str(Decimal("600.2") * M) and p.basis.endswith(
        "base_lse"
    )  # BRKR: 1,000.2 - 400
    assert by[(day(1), "total")].basis.endswith("base_assets")


def test_an_adjustment_filed_in_another_filing_is_not_used():
    _, by = planned()
    assert by[(day(10), "total")].after == str(
        Decimal(600) * M
    )  # the 100 redeemable NCI belongs to filing F2


def test_equity_direction_follows_the_filing_s_nci_elements():
    _, by = planned()
    assert (by[(day(11), "stock")].kind, by[(day(11), "stock")].basis) == (
        "hold",
        "nci_on_unmapped_partnership_elements",
    )
    aj = by[(day(12), "stock")]  # AJG: no NCI element anywhere in filing F3
    assert (aj.kind, aj.after, aj.basis.startswith("no_nci_in_filing")) == (
        "fill",
        str(Decimal(400) * M),
        True,
    )


def test_a_filing_with_nci_elements_the_planner_cannot_read_holds_a_parent_only_cell():
    _, by = planned()
    assert by[(day(14), "total")].basis == "nci_unconfirmed"
    # the independent reading of a held cell travels with it (parent equity only: 1,000 - 400)
    assert by[(day(14), "total")].reference == str(Decimal(600) * M)
    assert (
        by[(day(15), "stock")].reference is None
    )  # the equity direction has no reference
    assert by[(day(15), "stock")].basis == "nci_not_read"


def test_a_filing_with_temporary_equity_elements_but_none_read_for_the_instant_is_held():
    # TRGP 2021-09-30: a 749.7M Series A preferred filed only with a class-of-stock member; no fact is stored
    _, by = planned()
    assert by[(day(18), "total")].basis == "temporary_equity_present_not_read"


def test_planner_holds_carry_the_reference_reading():
    _, by = planned()
    # the NI-type cell is not a hold here; a mixed-vintage hold has no reading at all
    assert by[(day(7), "total")].reference is None


def test_planner_uses_the_face_subtotals_to_drop_an_unproven_component():
    _, by = planned()
    p = by[(day(13), "total")]
    assert p.after == str(Decimal("20940.9") * M) and "confirmed_by_face_subtotals" in p.basis and p.filing_id == F3  # fmt: skip


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
