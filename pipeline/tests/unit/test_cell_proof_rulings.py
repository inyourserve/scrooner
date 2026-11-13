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
