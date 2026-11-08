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
