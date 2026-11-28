"""Rule debt_composition (Stage 4 Prove, M1, 2026-11-29): total_debt_resolved without a company_tag_map claim had no
proof path (UNCHECKED "no company_tag_map claim ... nothing to prove it against", 28,745 FY+I cells across ranks
101-1000 in the 5k census of 2026-11-28). The cell is the composition mapper/concept_fallback.compute_total_debt wrote,
so it is proven as the sum of its own source tags read from the shown filing, and the perimeter post-pass then requires
the face short-term debt and the finance-lease liability (founder 2026-11-04)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine
from scrooner_pipeline.proof.perimeter import REASON, apply_perimeter
from scrooner_pipeline.proof.prove import (
    DEBT_COMPOSITION_TAGS,
    DISAGREE,
    PROVEN,
    UNCHECKED,
    Shown,
    prove_cell,
)

ADSH = "0001802768-25-000114"
END = date(2025, 9, 30)
M = 1_000_000


def struct(face: dict[str, int], notes: dict[str, int] | None = None, adsh: str = ADSH) -> FilingStructure:
    s = FilingStructure(adsh, "0001802768", "10-Q", date(2025, 11, 5), END)
    for i, tag in enumerate(face):
        s.pre.append(PreLine(2, i, "BS", tag, "us-gaap/2025", tag, False))
    for tag, v in {**face, **(notes or {})}.items():
        s.num[(tag, END, 0)].append(NumValue(tag, "us-gaap/2025", END, 0, "USD", Decimal(v * M), -3))
    return s


def shown(tags: tuple[str, ...], value: int, accession: str = ADSH, **kw) -> Shown:
    return Shown(
        2081,
        "total_debt_resolved",
        "I",
        END,
        END,
        Decimal(value * M),
        tags,
        accession,
        tuple(range(1, len(tags) + 1)),
        **kw,
    )


def run(sh: Shown, s: FilingStructure):
    p = prove_cell(sh, s, "2025q4")
    apply_perimeter([p], {s.adsh: s})
    return p


@pytest.mark.unit
def test_composition_of_current_and_noncurrent_ltd_is_proven_against_its_own_filing():
    face = {"LongTermDebtCurrent": 120, "LongTermDebtNoncurrent": 8826}
    p = run(shown(("LongTermDebtCurrent", "LongTermDebtNoncurrent"), 8946), struct(face))
    assert p.verdict == PROVEN, (p.reason_code, p.reason_text, p.checks)
    assert p.checks["debt_composition"]["status"] == "applied"
    assert p.checks["claim"]["source"] == "debt_composition"
    assert p.checks["component_parts"]["status"] == "pass"
    assert p.checks["perimeter"] == {"status": "pass"}
    assert p.row()["checks"]["rules"]["debt_composition"] == 1
    assert p.position_accession == ADSH


@pytest.mark.unit
def test_single_long_term_debt_tag_in_a_note_is_proven():
    # LongTermDebt (incl. current maturities) is disclosed in the debt note, not on the face: a note fact of the filing
    p = run(shown(("LongTermDebt",), 8946), struct({"Liabilities": 20000}, {"LongTermDebt": 8946}))
    assert p.verdict == PROVEN, (p.reason_code, p.reason_text, p.checks)
    assert p.checks["component_parts"]["note_facts"] == ["LongTermDebt"]


@pytest.mark.unit
def test_sum_that_is_not_the_shown_value_is_disagree():
    face = {"LongTermDebtCurrent": 120, "LongTermDebtNoncurrent": 8826}
    p = run(shown(("LongTermDebtCurrent", "LongTermDebtNoncurrent"), 9046), struct(face))
    assert p.verdict == DISAGREE


@pytest.mark.unit
def test_finance_lease_left_out_of_the_composition_is_perimeter_incomplete():
    face = {"LongTermDebtCurrent": 120, "LongTermDebtNoncurrent": 8826}
    s = struct(face, {"FinanceLeaseLiability": 75})
    p = run(shown(("LongTermDebtCurrent", "LongTermDebtNoncurrent"), 8946), s)
    assert (p.verdict, p.reason_code) == (DISAGREE, REASON)
    assert [m["tag"] for m in p.checks["perimeter"]["missing"]] == ["FinanceLeaseLiability"]


@pytest.mark.unit
def test_face_short_term_borrowings_left_out_is_perimeter_incomplete():
    face = {"ShortTermBorrowings": 300, "LongTermDebtNoncurrent": 8826}
    p = run(shown(("LongTermDebtNoncurrent",), 8826), struct(face))
    assert (p.verdict, p.reason_code) == (DISAGREE, REASON)


@pytest.mark.unit
def test_parts_come_from_the_shown_filing_only():
    # handed another filing's structure and the shown filing is not held: never judged across vintages
    face = {"LongTermDebtCurrent": 120, "LongTermDebtNoncurrent": 8826}
    p = run(
        shown(("LongTermDebtCurrent", "LongTermDebtNoncurrent"), 8946, accession="0001802768-26-000009"),
        struct(face),
    )
    assert p.verdict == UNCHECKED
    assert p.checks["component_parts"]["why"] == "parts_not_in_the_shown_filing"


@pytest.mark.unit
def test_a_tag_outside_the_composition_has_no_proof_path():
    face = {"LongTermDebtNoncurrent": 8826, "OperatingLeaseLiability": 50}
    p = run(shown(("LongTermDebtNoncurrent", "OperatingLeaseLiability"), 8876), struct(face))
    assert p.verdict == UNCHECKED
    assert "debt_composition" not in p.checks


@pytest.mark.unit
def test_a_company_claim_keeps_its_own_path():
    from scrooner_pipeline.proof.prove import Claim

    face = {"LongTermDebtCurrent": 120, "LongTermDebtNoncurrent": 8826}
    claim = Claim("component", "BS", parts=((1, "LongTermDebtCurrent"), (1, "LongTermDebtNoncurrent")))
    p = run(shown(("LongTermDebtCurrent", "LongTermDebtNoncurrent"), 8946, claim=claim), struct(face))
    assert p.verdict == PROVEN
    assert "debt_composition" not in p.checks
    assert p.checks["claim"]["source"] == "company_tag_map"


@pytest.mark.unit
def test_composition_tags_are_the_writer_tags():
    from scrooner_pipeline.mapper import concept_fallback as cf

    assert DEBT_COMPOSITION_TAGS == frozenset(cf.TOTAL_DEBT_TAGS) - set(cf.DEBT_CARRYING_CHECK)
