"""Cash-flow gap classes of the cohort dry run 41515845455 (data-team/strategy/team/CF-GAPS-2026-11-02.md).

1. checks: the total FX effect under its other standard names ties the cash-flow identity (Nucor FY2024, real values).
2. select: a quarter whose year-to-date input is held gets that input's reason, never silence and never a value.
3. select.absent_line_cell: evidenced blanks for a key whose filings print no line of the concept.
4. cf_detector.decide: run 7's lane rules map one common line whatever its tag, withdraw definitional holds, and
   leave the seed alone on structural gates (Verifier fixtures pipeline/tests/fixtures/fsn_company_cf).
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from scrooner_pipeline.fsn_store import cf_detector as cd
from scrooner_pipeline.fsn_store import checks
from scrooner_pipeline.fsn_store import select as sel

ROOT = Path(__file__).resolve().parents[3]
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_company_cf"
M = Decimal(1_000_000)


# ---------------------------------------------------------------- 1. FX tags
@pytest.mark.unit
@pytest.mark.parametrize(
    "fx_tag",
    [
        "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
        "EffectOfExchangeRateOnCashAndCashEquivalentsContinuingOperations",
        "EffectOfExchangeRateOnCash",
    ],
)
def test_nucor_fy2024_ties_with_its_fx_line(fx_tag):
    # Nucor 10-K 0001193125-26-071575, FY2024 column: 3,979 - 3,734 - 3,058 = -2,813; FX -16; change -2,829
    col = {
        (t, "us-gaap/2025"): checks.Print(t, "us-gaap/2025", Decimal(v) * M, -6, None)
        for t, v in (
            ("NetCashProvidedByUsedInOperatingActivities", "3979"),
            ("NetCashProvidedByUsedInInvestingActivities", "-3734"),
            ("NetCashProvidedByUsedInFinancingActivities", "-3058"),
            (fx_tag, "-16"),
            ("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect", "-2829"),
        )
    }
    c = {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}["cf_parts_eq_change"]
    assert c["ok"] and c["detail"]["fx_included"]


@pytest.mark.unit
def test_a_discontinued_fx_component_is_never_the_total():
    assert "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsDisposalGroupIncludingDiscontinuedOperations" not in checks.CF_FX
    assert "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations" not in checks.CF_FX


# ---------------------------------------------------------------- 2. held YTD input
def _filings():
    return {
        i: sel.Filing(i, f"a{i}", datetime(2025, 3 * i + 1, 1), "10-Q", date(2025, 3 * i, 28), 2025, f"Q{i}", "1231")
        for i in (1, 2, 3)
    }


def _p(vid, fid, d, q, v, ok=True):
    return sel.Print(vid, fid, "PaymentsOfDividends", d, q, "USD", Decimal(v), 0, "CF", True, ok)


@pytest.mark.unit
def test_a_quarter_whose_ytd_input_is_held_gets_that_reason_not_silence():
    q1, h1, n9 = date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30)
    prints = [_p(1, 1, q1, 1, 10), _p(2, 2, h1, 2, 20), _p(3, 3, n9, 3, 31, ok=False)]  # the 9M column fails a check
    cells = {(c.ddate, c.qtrs): c for c in sel.select_concept("dividends_paid_resolved", prints, _filings())}
    q3 = cells[(n9, 1)]
    assert q3.state == "defect" and q3.value is None
    assert q3.reason_code == "latest_copy_fails_identity" and q3.input_refs["ytd_qtrs"] == 3
    # Q2 is decided by the unchanged rules (here: no same-basis witness in the toy filings), not by the held 9M
    assert cells[(h1, 1)].reason_code == "no_basis_witness"


@pytest.mark.unit
def test_a_held_ytd_never_hides_a_printed_quarter():
    n9 = date(2025, 9, 30)
    prints = [_p(1, 3, n9, 1, 11), _p(2, 3, n9, 3, 31, ok=False)]
    cells = {(c.ddate, c.qtrs): c for c in sel.select_concept("dividends_paid_resolved", prints, _filings())}
    assert cells[(n9, 1)].state == "value" and cells[(n9, 1)].value == Decimal(11)


# ---------------------------------------------------------------- 3. absent line
def _data(mapped=()):
    f = {
        1: sel.Filing(1, "0000000001-25-000001", datetime(2025, 2, 1), "10-K", date(2024, 12, 31), 2024, "FY"),
        2: sel.Filing(2, "0000000001-25-000002", datetime(2025, 5, 1), "10-Q", date(2025, 3, 31), 2025, "Q1"),
    }
    cols = {(1, "CF", date(2024, 12, 31), 4), (1, "CF", date(2023, 12, 31), 4), (2, "CF", date(2025, 3, 31), 1)}
    return {"filings": f, "face_cols": cols, "mapped_filings": {"dividends_paid_resolved": set(mapped)}}


@pytest.mark.unit
@pytest.mark.parametrize(
    "classes, state, reason",
    [
        ([], "not_presented", "line_not_presented_in_filing"),
        (["perimeter_nci", "perimeter_preferred"], "not_presented", "only_excluded_lines_presented"),
        (["combined"], "not_presented", "line_presented_combined_with_others"),
        (["perimeter_partnership_distribution"], "defect", "perimeter_partnership_distribution"),
        (["net"], "defect", "perimeter_line_unresolved"),
    ],
)
def test_absent_line_reasons(classes, state, reason):
    c = sel.absent_line_cell("dividends_paid_resolved", "FY", date(2024, 12, 31), _data(), {1: classes})
    assert c is not None and (c.state, c.reason_code, c.value) == (state, reason, None)
    assert c.rule_id == sel.RULE_ABSENT and c.input_refs["accessions"] == ["0000000001-25-000001"]
    row = sel.to_row(c, 1, _data()["filings"])
    assert row["reason_text"]


@pytest.mark.unit
def test_no_absent_claim_when_a_common_line_exists_or_a_line_maps_or_no_column():
    d = date(2024, 12, 31)
    assert sel.absent_line_cell("dividends_paid_resolved", "FY", d, _data(), {1: ["common"]}) is None
    assert sel.absent_line_cell("dividends_paid_resolved", "FY", d, _data(mapped=[1]), {}) is None
    assert sel.absent_line_cell("dividends_paid_resolved", "FY", date(2022, 12, 31), _data(), {}) is None
    q = sel.absent_line_cell("dividends_paid_resolved", "Q", date(2025, 3, 31), _data(), {})
    assert q is not None and q.qtrs == 1 and q.reason_code == "line_not_presented_in_filing"


# ---------------------------------------------------------------- 4. detector on the Verifier fixtures
def _decide(cik, acc, drop_cal=False):
    sys.path.insert(0, str(ROOT / "pipeline" / "scripts" / "slot_records"))
    from fsn_company_cf import read_cf_inputs  # noqa: PLC0415

    _f, face, vals, arcs, _d = read_cf_inputs(FX / cik)
    return cd.decide(acc, {acc: face[acc]}, {acc: vals[acc]}, {} if drop_cal else arcs.get(acc, {}))


@pytest.mark.unit
def test_detector_maps_the_one_common_line_and_excludes_the_subsidiary():
    d = _decide("0000032604", "0000032604-24-000041")[cd.BUYBACKS]  # EMR FY2024 (VERIFY-BUYBACKS-R2)
    assert d["status"] == "mapped" and d["tag"] == "PaymentsForRepurchaseOfCommonStock"
    assert "perimeter_subsidiary_repurchase" in d["lines"].values()


@pytest.mark.unit
def test_detector_maps_an_unseeded_tag_and_dividend_equivalents():
    nws = _decide("0001564708", "0001193125-15-288946")[cd.BUYBACKS]  # News Corp: PaymentsForRepurchaseOfEquity
    assert nws["status"] == "mapped" and nws["tag"] == "PaymentsForRepurchaseOfEquity"
    aapl = _decide("0000320193", "0000320193-24-000123")[cd.DIVIDENDS]  # "dividends and dividend equivalents"
    assert aapl["status"] == "mapped" and aapl["tag"] == "PaymentsOfDividends"


@pytest.mark.unit
def test_detector_holds_definitional_cases():
    rost = _decide("0000745732", "0000745732-20-000016")[cd.BUYBACKS]  # two repurchase lines (VERIFY-BUYBACKS-RUN3)
    assert rost["status"] == "held" and "multiple_common_lines_not_summed_in_store" in rost["reasons"]
    ldos = _decide("0001336920", "0001336920-21-000010")[cd.BUYBACKS]  # "Repurchases of stock and other"
    assert ldos["status"] == "held" and "buyback_combined_with_other_items" in ldos["reasons"]


@pytest.mark.unit
def test_structural_gates_leave_the_seed_decision_alone():
    # GPN FY2022 without its calc linkbase: the lane says hold_no_statement_cal; the store checks columns itself
    d = _decide("0001123360", "0001123360-23-000009", drop_cal=True)[cd.BUYBACKS]
    assert d["status"] == "seed_only" and "hold_no_statement_cal" in d["reasons"]


# ---------------------------------------------------------------- 5. the write route accepts every new row
@pytest.mark.unit
@pytest.mark.parametrize(
    "classes",
    [[], ["perimeter_nci"], ["combined"], ["perimeter_partnership_distribution"], ["net"]],
)
def test_the_cell_loader_accepts_every_new_absent_line_row(classes):
    """pilot-prod loads these rows through cell_loader.parse_row: a reason the frozen contract rejects (defect class,
    owner, rule id) would drop the row at load time instead of reaching analytics.cell_blank_reason."""
    from scrooner_pipeline.normalizer import cell_loader

    c = sel.absent_line_cell("dividends_paid_resolved", "FY", date(2024, 12, 31), _data(), {1: classes})
    row = sel.to_row(c, 1, _data()["filings"])
    got = cell_loader.parse_row(1, row, {"dividends_paid_resolved"})
    assert not isinstance(got, str), got


@pytest.mark.unit
def test_the_cell_loader_accepts_a_held_ytd_quarter_row():
    from scrooner_pipeline.normalizer import cell_loader

    n9 = date(2025, 9, 30)
    prints = [_p(1, 1, date(2025, 3, 31), 1, 10), _p(2, 3, n9, 3, 31, ok=False)]
    q3 = {(c.ddate, c.qtrs): c for c in sel.select_concept("dividends_paid_resolved", prints, _filings())}[(n9, 1)]
    got = cell_loader.parse_row(1, sel.to_row(q3, 1, _filings()), {"dividends_paid_resolved"})
    assert not isinstance(got, str), got


@pytest.mark.unit
def test_an_unnamed_share_purchase_line_blocks_the_absent_claim():
    """"Purchase of CP Common Shares" under a custom tag misses the lane's repurchase test: it may be the buyback,
    so no `line_not_presented_in_filing` is claimed (the key stays a gap); ESPP proceeds never block a claim."""
    from scrooner_pipeline.fsn_store import pilot

    assert pilot.SHARE_PURCHASE_RX.search("Purchase of CP Common Shares")
    assert not pilot.SHARE_PURCHASE_RX.search("Purchases of property, plant and equipment")
    d = date(2024, 12, 31)
    assert sel.absent_line_cell("share_buybacks_resolved", "FY", d, _data(), {1: ["unclassified_share_line"]}) is None


# ---------------------------------------------------------------- 6. Verifier 2026-11-08 (VERIFY-CF-GAPS-2026-11-08)
def _cf_col(rows, version="us-gaap/2020"):
    return {(t, version): checks.Print(t, version, Decimal(v) * M, -5, None) for t, v in rows}


CHANGE_INCL = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect"


@pytest.mark.unit
def test_a_separately_printed_discontinued_total_ties_the_column():
    # Somnigroup 0001206264-21-000208, 6M 2020: 170.4 - 87.2 + 1.4 = 84.6; - 1.0 discontinued - 1.7 FX = 81.9
    col = _cf_col(
        [
            ("NetCashProvidedByUsedInOperatingActivities", "170.4"),
            ("NetCashProvidedByUsedInInvestingActivities", "-87.2"),
            ("NetCashProvidedByUsedInFinancingActivities", "1.4"),
            ("NetCashProvidedByUsedInDiscontinuedOperations", "-1.0"),
            ("EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "-1.7"),
            (CHANGE_INCL, "81.9"),
        ]
    )
    c = {x["check_id"]: x for x in checks.check_column("CF", col, {}, {})}["cf_parts_eq_change"]
    assert c["ok"] and c["detail"]["discontinued_included"] and c["detail"]["fx_included"]


@pytest.mark.unit
def test_two_statements_one_parent_pass_when_one_calc_group_ties():
    # a co-registrant's own cash-flow statement brings a second calc group for the same parent (Cheniere FY2018)
    v = "us-gaap/2020"
    col = _cf_col([("P", "10"), ("A", "6"), ("B", "4"), ("C", "99")])
    stmt_of = {(t, v): "CF" for t in "PABC"}
    groups = {("P", v, 1): [("A", v, 1), ("B", v, 1)], ("P", v, 2): [("A", v, 1), ("C", v, 1)]}
    got = [x for x in checks.check_column("CF", col, groups, stmt_of) if x["check_id"].startswith("calc:")]
    assert len(got) == 1 and got[0]["ok"] and len(got[0]["detail"]["groups"]) == 2
    groups1 = {("P", v, 2): [("A", v, 1), ("C", v, 1)]}  # one group that does not tie still fails
    assert not [x for x in checks.check_column("CF", col, groups1, stmt_of) if x["check_id"].startswith("calc:")][0]["ok"]


@pytest.mark.unit
def test_a_merged_tree_with_profitloss_and_netincomeloss_ties_with_either():
    # Brixmor 0001581068-15-000050: one group lists both (parent + operating partnership trees merged)
    v = "us-gaap/2014"
    col = _cf_col([("NetCashProvidedByUsedInOperatingActivities", "86.576"), ("NetIncomeLoss", "41.740"),
                   ("ProfitLoss", "41.740"), ("DepreciationDepletionAndAmortization", "44.836")], v)
    stmt_of = {k: "CF" for k in col}
    groups = {("NetCashProvidedByUsedInOperatingActivities", v, 2): [
        ("NetIncomeLoss", v, 1), ("ProfitLoss", v, 1), ("DepreciationDepletionAndAmortization", v, 1)]}
    got = [x for x in checks.check_column("CF", col, groups, stmt_of) if x["check_id"].startswith("calc:")]
    assert got[0]["ok"]


def _lane():
    return cd._lane()


def _face(*rows, report=4):
    """(report, line, tag, label, custom, negating) rows of a primary cash-flow statement, in printed order."""
    return [(report, i + 1, t, lab, False, False) for i, (t, lab) in enumerate(rows)]


OP, INV, FIN = (
    ("NetCashProvidedByUsedInOperatingActivities", "Net cash provided by operating activities"),
    ("NetCashProvidedByUsedInInvestingActivities", "Net cash used for investing activities"),
    ("NetCashProvidedByUsedInFinancingActivities", "Net cash used for financing activities"),
)


@pytest.mark.unit
def test_section_headers_are_never_lines_kraft_heinz():
    from scrooner_pipeline.fsn_store import pilot

    rows = _face(OP, INV, ("NetCashProvidedByUsedInFinancingActivitiesAbstract", "Cash Flows from Financing Activities:"),
                 ("PaymentsForRepurchaseOfCommonStockAbstract", "Repurchases of common stock:"),
                 ("RepaymentsOfLongTermDebt", "Repayments of long-term debt"), FIN)
    got = pilot.classify_filing(rows, _lane())
    assert got["share_buybacks_resolved"] == []
    c = sel.absent_line_cell("share_buybacks_resolved", "FY", date(2024, 12, 31), _data(), {1: got["share_buybacks_resolved"]})
    assert c.reason_code == "line_not_presented_in_filing"


@pytest.mark.unit
def test_rows_of_another_page_are_never_lines_erie():
    from scrooner_pipeline.fsn_store import pilot

    face = _face(OP, INV, ("RepaymentsOfLongTermDebt", "Repayments of debt"), FIN)
    other = _face(
        ("RelatedPartyTransactionAmountsOfTransaction", "Purchase of treasury shares from related party"),
        ("PaymentsRelatedToTaxWithholdingForShareBasedCompensation", "Shares withheld for taxes (related party)"),
        report=9,
    )
    rows = face[:2] + other + face[2:]  # rows arrive unordered from the store: the other page sits inside the section
    assert pilot.classify_filing(rows, _lane())["share_buybacks_resolved"] == []


@pytest.mark.unit
def test_operating_inflows_and_non_cash_items_are_never_dividend_lines():
    from scrooner_pipeline.fsn_store import pilot

    lane = _lane()
    rows = _face(("ProceedsFromEquityMethodInvestmentDividendsOrDistributions", "Dividends received from unconsolidated affiliates"),
                 OP, INV, ("RepaymentsOfLongTermDebt", "Repayments of debt"), FIN,
                 ("DividendsPayableCurrentAndNoncurrent", "Dividends and distributions declared but not paid"))
    assert pilot.classify_filing(rows, lane)["dividends_paid_resolved"] == []  # Somnigroup FY2018, BXP supplemental
    assert lane.dividend_class("DividendsPayable", "Dividends and distributions declared but not paid") == "excluded_noncash"


@pytest.mark.unit
def test_dividends_and_distributions_is_a_combined_line_bxp():
    from scrooner_pipeline.fsn_store import pilot

    lane = _lane()
    assert lane.dividend_class("PaymentsOfDividends", "Dividends and distributions") == "combined"
    rows = _face(OP, INV, ("PaymentsOfDividends", "Dividends and distributions"), FIN)
    classes = pilot.classify_filing(rows, lane)["dividends_paid_resolved"]
    c = sel.absent_line_cell("dividends_paid_resolved", "FY", date(2024, 12, 31), _data(), {1: classes})
    assert c.reason_code == "line_presented_combined_with_others"


@pytest.mark.unit
def test_no_claim_when_the_financing_section_cannot_be_located():
    from scrooner_pipeline.fsn_store import pilot

    got = pilot.classify_filing(_face(OP, ("RepaymentsOfLongTermDebt", "Repayments of debt")), _lane())
    assert got["share_buybacks_resolved"] == ["no_financing_section"]
    assert sel.absent_line_cell("share_buybacks_resolved", "FY", date(2024, 12, 31), _data(), {1: got["share_buybacks_resolved"]}) is None


@pytest.mark.unit
def test_a_period_excluded_by_one_filing_is_never_filled_by_a_relabelled_copy():
    # Brixmor: FY2015 10-K "Repurchase of common shares in conjunction with equity award plans" (excluded); the FY2017
    # 10-K reprints FY2015 under the same tag as "Repurchase of common shares"
    f = _data()["filings"]
    ex = {("PaymentsForRepurchaseOfCommonStock", date(2024, 12, 31), 4): [1]}
    got = {(c.ddate, c.qtrs): c for c in sel.excluded_period_cells("share_buybacks_resolved", [], ex, f)}
    assert set(got) == {(date(2024, 12, 31), 4), (date(2024, 12, 31), 1)}
    assert all(c.state == "not_presented" and c.reason_code == "only_excluded_lines_presented" for c in got.values())
    kept = sel.Cell("share_buybacks_resolved", date(2024, 12, 31), 4, "defect", reason_code="latest_copy_fails_identity")
    assert {(c.ddate, c.qtrs) for c in sel.excluded_period_cells("share_buybacks_resolved", [kept], ex, f)} == {(date(2024, 12, 31), 1)}


@pytest.fixture
def db(isolated_database_url):
    import psycopg

    c = psycopg.connect(isolated_database_url)
    if c.execute("select count(*) from information_schema.tables where table_schema = 'fsn' and table_name = 'value'").fetchone()[0] != 1:
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


@pytest.mark.integration
def test_the_identity_reads_the_primary_registrant_only(db):
    """Brixmor 10-Q 0001581068-15-000050 prints the operating partnership's block as a co-registrant (FSN coreg):
    its numbers must never replace the parent's in the column (the identity ties on the parent's own block)."""
    cid = db.execute("insert into core.company (cik, company_name) values ('0009999999', 'COREG TEST') returning id").fetchone()[0]
    fid = db.execute(
        "insert into fsn.filing (accession, company_id, cik, form, period, fsn_set) values "
        "('0009999999-15-000050', %s, '0009999999', '10-Q', '2014-03-31', '2015q2') returning id", (cid,)).fetchone()[0]
    parent = {"NetCashProvidedByUsedInOperatingActivities": ("86576", "86623"),
              "NetCashProvidedByUsedInInvestingActivities": ("-39774", "-39771"),
              "NetCashProvidedByUsedInFinancingActivities": ("-105021", "-104629"),
              "CashAndCashEquivalentsPeriodIncreaseDecrease": ("-58219", "-57777")}
    for i, (tag, (pv, opv)) in enumerate(parent.items()):
        tid = db.execute("insert into fsn.tag (tag, version) values (%s, 'us-gaap/2014') returning id", (tag,)).fetchone()[0]
        db.execute("insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s, 8, %s, 'CF', %s)", (fid, i + 1, tid))
        for coreg, v in (("", pv), ("BrixmorOperatingPartnershipLP", opv)):
            db.execute("insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, coreg, value, dcml) "
                       "values (%s, %s, %s, '2014-03-31', 1, 'USD', 0, %s, %s, -3)", (fid, cid, tid, coreg, Decimal(v) * 1000))
    data = checks.load_filing(db, fid)
    col = data["columns"][("CF", date(2014, 3, 31), 1)]
    assert col[("NetCashProvidedByUsedInOperatingActivities", "us-gaap/2014")].value == Decimal(86576000)
    c = {x["check_id"]: x for x in checks.check_column("CF", col, data["groups"], data["stmt_of"])}["cf_parts_eq_change"]
    assert c["ok"]
    db.rollback()


@pytest.mark.unit
def test_the_evidence_is_the_filing_whose_own_period_it_is():
    d = _data()
    d["filings"][3] = sel.Filing(3, "0000000001-26-000003", datetime(2026, 5, 1), "10-Q", date(2026, 3, 31), 2026, "Q1")
    d["face_cols"] = {(2, "CF", date(2025, 3, 31), 1), (3, "CF", date(2025, 3, 31), 1)}  # the 2026 10-Q re-prints it
    c = sel.absent_line_cell("dividends_paid_resolved", "Q", date(2025, 3, 31), d, {})
    assert c.filing_id == 2 and c.input_refs["accessions"] == ["0000000001-25-000002", "0000000001-26-000003"]


@pytest.mark.unit
def test_a_latest_printed_zero_is_served_although_an_earlier_filing_excluded_the_period():
    """Dhairya's ruling 2026-11-08: Brixmor's FY2017 10-K prints "Repurchase of common shares 0" for FY2015 under
    PaymentsForRepurchaseOfCommonStock; the FY2015 10-K excluded its equity-award line. The 0 is served."""
    fy = date(2024, 12, 31)
    f = _filings()
    prints = [sel.Print(1, 3, "PaymentsForRepurchaseOfCommonStock", fy, 4, "USD", Decimal(0), 0, "CF", True, True)]
    cells = sel.select_concept("share_buybacks_resolved", prints, f)
    ex = {("PaymentsForRepurchaseOfCommonStock", fy, 4): [1]}
    got = {(c.ddate, c.qtrs): c for c in cells + sel.excluded_period_cells("share_buybacks_resolved", cells, ex, f)}
    assert got[(fy, 4)].state == "value" and got[(fy, 4)].value == 0


@pytest.mark.unit
def test_a_two_block_page_reads_the_primary_registrants_block_only():
    """Dominion / Virginia Power, Ares: the parent's block comes first; a line in the co-registrant's financing
    section is not the parent's line."""
    from scrooner_pipeline.fsn_store import pilot

    rows = _face(OP, INV, ("PaymentsOfDividendsCommonStock", "Common dividend payments"), FIN,
                 OP, INV, ("PaymentsForRepurchaseOfCommonStock", "Repurchase of common stock"), FIN)
    got = pilot.classify_filing(rows, _lane())
    assert got["share_buybacks_resolved"] == [] and got["dividends_paid_resolved"] == ["common"]
