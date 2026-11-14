"""Rule 1 in the proof: a component part the filing omits on its face counts as 0 only when shown.zero_parts names it
(evidence absent_on_face_parent_ties, common/authority.absent_part_is_zero); otherwise the cell stays UNCHECKED."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.proof import prove
from scrooner_pipeline.proof.fsn import NumValue
from scrooner_pipeline.proof.prove import PROVEN, UNCHECKED, Claim, Proof, Shown
from scrooner_pipeline.proof.shown import component_sum_authority

END = date(2024, 12, 31)


class _Struct:
    adsh = "A-10"
    pre: list = []

    def lines_on(self, stmt):
        return []


def _shown(zero_parts):
    return Shown(
        company_id=1,
        data_point_name="total_debt_resolved",
        period_grain="I",
        period_start=END,
        period_end=END,
        value=Decimal("100"),
        tags=("DebtCurrent",),
        accession="A-10",
        source_fact_ids=(1,),
        claim=Claim(
            "component",
            "BS",
            parts=((1, "DebtCurrent"), (1, "LongTermDebtNoncurrent")),
            part_stmts=("BS", "BS"),
        ),
        zero_parts=zero_parts,
    )


def _run(monkeypatch, zero_parts):
    def fv(structure, tag, ddate, qtrs, cls):
        if tag == "DebtCurrent":
            return NumValue(tag, "v", ddate, qtrs, "USD", Decimal("100"), -6)
        return None

    monkeypatch.setattr(prove, "find_value", fv)
    monkeypatch.setattr(prove, "structure_face", lambda s, st: {"DebtCurrent"})
    s = _shown(zero_parts)
    return prove.prove_component(s, _Struct(), Proof(shown=s, verdict=UNCHECKED))


def test_zero_part_with_evidence_is_proven(monkeypatch):
    p = _run(monkeypatch, ("LongTermDebtNoncurrent",))
    assert p.verdict == PROVEN
    assert p.checks["component_parts"]["absent_zero"] == ["LongTermDebtNoncurrent"]


def test_missing_part_without_evidence_stays_unchecked(monkeypatch):
    assert _run(monkeypatch, ()).verdict == UNCHECKED


def test_sum_authority_counts_the_evidenced_zero_part():
    copies = [
        ("f18", Decimal(100), "DC"),
        ("f17", Decimal(90), "DC"),
        ("f17", Decimal(5), "LT"),
    ]
    filed = {"f17": date(2017, 1, 1), "f18": date(2018, 1, 1)}
    parts = ((1, "DC"), (1, "LT"))
    assert component_sum_authority(copies, parts, filed) == ("f17", Decimal(95))
    got = component_sum_authority(
        copies, parts, filed, zero_ok=lambda a, t: a == "f18" and t == "LT"
    )
    assert got == ("f18", Decimal(100))
