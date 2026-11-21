"""A component sum is judged in ONE filing: the parts come from the filing the shown value comes from. GOOG FY2017
SG&A is shown from the FY2019 10-K (S&M 12,893 + G&A 6,840 = 19,733, G&A restated); the own-year FY2017 10-K prints
G&A 6,872, so its parts tie to the old 19,765. Reading those parts against the latest print is a cross-vintage
mismatch. Handed the own-year structure, the proof fetches the parts from the shown filing's own structure (same
accession) and proves there; it is UNCHECKED (parts_not_in_the_shown_filing) only when that filing is not held or
prints none of the parts, never DISAGREE."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof import prove
from scrooner_pipeline.proof.fsn import NumValue
from scrooner_pipeline.proof.prove import (
    DISAGREE,
    PROVEN,
    UNCHECKED,
    Claim,
    Proof,
    Shown,
)

END = date(2017, 12, 31)
OWN, LATEST = "0001652044-18-000007", "0001652044-20-000008"
PRINTS = {
    OWN: {
        "SellingAndMarketingExpense": Decimal(12893),
        "GeneralAndAdministrativeExpense": Decimal(6872),
    },
    LATEST: {
        "SellingAndMarketingExpense": Decimal(12893),
        "GeneralAndAdministrativeExpense": Decimal(6840),
    },
}


class _Struct:
    def __init__(self, adsh, store=None):
        self.adsh = adsh
        self.pre: list = []
        self.store = store  # accession -> _Struct, the runner's loader; None = no other filing held

    def lines_on(self, stmt):
        return []

    def filing(self, adsh):
        if adsh == self.adsh:
            return self
        return None if self.store is None else self.store.get(adsh)


def _shown(value, accession):
    return Shown(
        company_id=9,
        data_point_name="sga_expense",
        period_grain="FY",
        period_start=date(2017, 1, 1),
        period_end=END,
        value=value,
        tags=("GeneralAndAdministrativeExpense", "SellingAndMarketingExpense"),
        accession=accession,
        source_fact_ids=(1, 2),
        presentation_scale=0,
        claim=Claim(
            "component",
            "IS",
            parts=(
                (1, "SellingAndMarketingExpense"),
                (1, "GeneralAndAdministrativeExpense"),
            ),
            part_stmts=("IS", "IS"),
        ),
    )


def _run(monkeypatch, shown, structure_adsh, store=None):
    def fv(structure, tag, ddate, qtrs, cls):
        v = PRINTS.get(structure.adsh, {}).get(tag)
        return None if v is None else NumValue(tag, "v", ddate, qtrs, "USD", v, 0)

    monkeypatch.setattr(prove, "find_value", fv)
    monkeypatch.setattr(
        prove,
        "structure_face",
        lambda s, st: {"SellingAndMarketingExpense", "GeneralAndAdministrativeExpense"},
    )
    return prove.prove_component(
        shown, _Struct(structure_adsh, store), Proof(shown=shown, verdict=UNCHECKED)
    )


def test_shown_filing_not_held_is_unchecked_never_a_mismatch(monkeypatch):
    p = _run(monkeypatch, _shown(Decimal(19733), LATEST), OWN)
    assert p.verdict == UNCHECKED and p.verdict != DISAGREE
    assert p.checks["component_parts"]["why"] == "parts_not_in_the_shown_filing"
    assert p.checks["component_parts"]["shown_filing_held"] is False


def test_handed_own_year_parts_fetches_the_shown_filing_and_proves(monkeypatch):
    # the runner hands the own-year 10-K; the parts are read from the FY2019 10-K the value comes from
    p = _run(
        monkeypatch,
        _shown(Decimal(19733), LATEST),
        OWN,
        store={LATEST: _Struct(LATEST)},
    )
    assert p.verdict == PROVEN
    assert p.position_accession == LATEST
    assert p.checks["component_parts"]["read_from"] == LATEST
    assert p.checks["component_parts"]["handed"] == OWN
    assert {f["value"] for f in p.checks["component_parts"]["found"]} == {
        "12893",
        "6840",
    }


def test_shown_filing_that_prints_no_parts_is_unchecked(monkeypatch):
    other = "0001652044-21-000010"  # held, but prints neither part at this column
    p = _run(
        monkeypatch,
        _shown(Decimal(19733), other),
        OWN,
        store={other: _Struct(other)},
    )
    assert p.verdict == UNCHECKED
    assert p.checks["component_parts"]["why"] == "parts_not_in_the_shown_filing"
    assert p.checks["component_parts"]["shown_filing_held"] is True


def test_wrong_value_against_the_shown_filing_is_not_proven(monkeypatch):
    # the own-year sum 19,765 under the FY2019 10-K's accession: the shown filing's parts give 19,733
    p = _run(
        monkeypatch,
        _shown(Decimal(19765), LATEST),
        OWN,
        store={LATEST: _Struct(LATEST)},
    )
    assert p.verdict != PROVEN
    assert p.position_accession == LATEST


def test_parts_of_the_shown_filing_prove_the_latest_print(monkeypatch):
    assert _run(monkeypatch, _shown(Decimal(19733), LATEST), LATEST).verdict == PROVEN


def test_own_year_print_proves_against_its_own_parts(monkeypatch):
    assert _run(monkeypatch, _shown(Decimal(19765), OWN), OWN).verdict == PROVEN
