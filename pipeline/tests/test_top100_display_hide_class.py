"""A hide needs a doc 02 hide class (certify_display.check_hide_reasons). Pipeline-state reasons default to OPEN.

Fixtures are the MO (company 1413) sbc cells of data-team/strategy/certification/MO-coverage-2026-11-15.csv: FY2015-19
era_unmapped and FY2020-24 reason_own_filing_unverified were hidden; FY2025 is structural_not_presented."""

import pytest

from scrooner_pipeline.mapper import top100_coverage as t100

MO = 1413


def _cell(dp, fy, cls, code, **kw):
    r = {
        "company_id": MO,
        "rank": 97,
        "ticker": "MO",
        "data_point": dp,
        "fiscal_year": fy,
        "period_end": f"{fy}-12-31",
        "class": cls,
        "reason_code": code,
        "accession": "",
        "r_page": "",
        "evidence": "",
        "_parts_blank": 0,
        "_presented": True,
    }
    r.update(kw)
    return r


def _mo_sbc_pipeline_state():
    return [
        _cell("sbc", fy, "BLANK", "era_unmapped", _absent_own=True)
        for fy in range(2015, 2020)
    ] + [
        _cell("sbc", fy, "UNCHECKED", "reason_own_filing_unverified", _absent_own=True)
        for fy in range(2020, 2025)
    ]


def test_mo_sbc_pipeline_states_are_open_not_hidden():
    rows = _mo_sbc_pipeline_state()
    t100.apply_display(rows)
    assert [r["display"] for r in rows] == [t100.OPEN] * 10
    assert all(r["hide_class"] == "" for r in rows)


def test_a_structural_not_presented_row_still_hides_with_its_class():
    rows = [
        _cell("sbc", fy, "REASON", "structural_not_presented") for fy in (2024, 2025)
    ]
    t100.apply_display(rows)
    assert [r["display"] for r in rows] == [t100.HIDDEN_ROW] * 2
    assert {r["hide_class"] for r in rows} == {"structural_not_presented"}


def test_row_collapse_cannot_hide_a_row_with_a_pipeline_state_cell():
    rows = _mo_sbc_pipeline_state() + [
        _cell("sbc", 2025, "REASON", "structural_not_presented")
    ]
    t100.apply_display(rows)
    assert {r["display"] for r in rows} == {t100.OPEN}
    assert {r["hide_class"] for r in rows} == {""}


@pytest.mark.parametrize(
    "code",
    [
        "era_unmapped",
        "reason_own_filing_unverified",
        "no_role",
        "proof_unchecked",
        "no_proof_row",
        "predictor_candidate",
        "open_period",
        "held_x",
        "some_future_code",
    ],
)
def test_unknown_and_pipeline_state_reasons_never_hide(code):
    rows = [_cell("sbc", 2020, "REASON", code, _presented=False)]
    t100.apply_display(rows)
    assert rows[0]["display"] == t100.OPEN


def test_unverified_data_point_absent_own_stays_open_but_allowlisted_hides():
    off = _cell("sbc", 2020, "BLANK", "era_unmapped", _absent_own=True)
    on = _cell("operating_income", 2020, "BLANK", "era_unmapped", _absent_own=True)
    keep = [_cell(dp, 2021, "PROVEN", None) for dp in ("sbc", "operating_income")]
    t100.apply_display([off, on, *keep])
    assert off["display"] == t100.OPEN
    assert (on["display"], on["hide_class"]) == (t100.HIDDEN_YEAR, "verified_absent")


def test_other_hide_classes_and_exports_carry_hide_class():
    pre = _cell("sbc", 2012, "BLANK", "era_unmapped", _before_first_filing=True)
    pre["_presented"] = False
    nop = _cell("sbc", 2013, "REASON", "no_10k_presents_period", _presented=False)
    comb = _cell("other_income", 2016, "REASON", "x", _only_combined="years")
    keep = _cell("other_income", 2017, "PROVEN", None)
    keep2 = _cell("sbc", 2020, "PROVEN", None)
    rows = [pre, nop, comb, keep, keep2]
    t100.apply_display(rows)
    assert pre["hide_class"] == nop["hide_class"] == "pre_filing"
    assert comb["hide_class"] == "line_presented_combined"
    _, hy = t100.hidden_evidence(rows)
    assert {r["hide_class"] for r in hy} == {"pre_filing", "line_presented_combined"}
    assert "hide_class" in t100.CSV_COLUMNS
    assert "hide_class" in t100.HIDDEN_YEAR_COLUMNS
    assert "hide_class" in t100.HIDDEN_ROW_COLUMNS
