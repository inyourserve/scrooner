"""Cell-proof rulings from the Tag Expert audit (proof-ruling-audit-2026-11-13.csv)."""

from __future__ import annotations

from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import NumValue

from tests.unit.test_cell_proof import ADSH, DDATE, FY_END, structure


@pytest.mark.unit
def test_r12_dei_cover_count_is_never_proven_as_shares_outstanding():
    s = structure()
    s.num[("EntityCommonStockSharesOutstanding", DDATE, 0)].append(
        NumValue(
            "EntityCommonStockSharesOutstanding",
            "dei/2025",
            DDATE,
            0,
            "shares",
            Decimal("15000000000"),
            -3,
        )
    )
    cell = pv.Shown(
        3,
        "shares_outstanding_resolved",
        "I",
        FY_END,
        FY_END,
        Decimal("15000000000"),
        ("EntityCommonStockSharesOutstanding",),
        ADSH,
        (1,),
        False,
        6,
        claim=pv.Claim("concept", "CP", tags=("EntityCommonStockSharesOutstanding",)),
    )
    p = pv.prove_cell(cell, s, "2025q4")
    assert p.verdict == pv.DISAGREE
    assert p.reason_code == "dei_cover_count_is_not_shares_outstanding"


@pytest.mark.unit
def test_r15_combined_line_is_not_the_data_point_and_accretion_da_is_not_expected():
    from scrooner_pipeline.proof.shown import combined_for

    assert "DepreciationAmortizationAndAccretionNet" not in " ".join(
        pv.EXPECTED["depreciation_and_amortization_resolved"][1]
    )
    assert "PaymentsOfDividends" not in pv.EXPECTED["dividends_paid_resolved"][1]
    rows = [
        ("NetIncomeLoss", ("net_income_resolved", "x"), FY_END.replace(year=2015), None)
    ]
    assert combined_for(rows, "net_income_resolved", FY_END) == ("NetIncomeLoss",)
    assert combined_for(rows, "total_assets_resolved", FY_END) == ()
    cell = pv.Shown(
        3,
        "net_income_resolved",
        "FY",
        FY_END.replace(month=1),
        FY_END,
        Decimal("112010000000"),
        ("NetIncomeLoss",),
        ADSH,
        (1,),
        False,
        6,
        combined=("NetIncomeLoss",),
    )
    p = pv.prove_cell(cell, structure(), "2025q4")
    assert (
        p.verdict == pv.DISAGREE and p.reason_code == "combined_line_shown_as_concept"
    )
    # the same cell without the veto is PROVEN
    ok = pv.Shown(*[getattr(cell, f) for f in list(cell.__dataclass_fields__)[:11]])
    assert pv.prove_cell(ok, structure(), "2025q4").verdict == pv.PROVEN
