"""Rule 4 (Dhairya 2026-11-14): a face PP&E line that includes finance-lease ROU IS ppe_net (mapped, never combined)."""

from __future__ import annotations

from scrooner_pipeline.mapper import docmap_loader as dl

ROU = "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"
HEADER = "ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note\n"
MD = "Latest 10-K opened: 0000000001-26-000001 (period 2025-12-31)"
FIX_HEADER = "data_point,fiscal_year,period_end,decision,tags,stmt,accession,r_page,printed_value,note\n"


def test_docmap_combined_rou_line_on_ppe_net_is_mapped():
    rows, rejects = dl.parse_docmap(
        HEADER
        + f"T,ppe_net,combined,us-gaap:{ROU},BS,R5.htm,PP&E net,,FILING-CHECKED,\n"
        + f"T,goodwill,combined,us-gaap:{ROU},BS,R5.htm,x,,FILING-CHECKED,\n",
        MD,
        "T-docmap-2026-11-12.csv",
    )
    got = {r.data_point: r.status for r in rows}
    assert not rejects
    assert got == {"ppe_net": "mapped", "goodwill": "combined"}


def test_fix_row_combined_rou_line_is_mapped_and_other_combined_stays():
    csv_text = (
        FIX_HEADER
        + f"ppe_net,2023,2023-12-30,combined,us-gaap:{ROU},BS,0000050863-24-000010,R5.htm,96647000000,why\n"
        + "ppe_net,2024,2024-12-28,combined,us-gaap:Foo+us-gaap:Bar,BS,0000050863-25-000009,R5.htm,1,why\n"
        + "cash_and_equivalents,2023,2023-12-30,combined,us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents,BS,0000050863-24-000010,R4.htm,1,why\n"
    )
    rows, _ = dl.parse_fixes(csv_text, "T-fixes-2026-11-14.csv")
    st = {(r.data_point, r.era_to.year): r.status for r in rows}
    assert st[("ppe_net", 2023)] == "mapped"
    assert st[("cash_and_equivalents", 2023)] == "combined"
    mapped = next(
        r for r in rows if r.data_point == "ppe_net" and r.era_to.year == 2023
    )
    assert "ppe_net ruling" in mapped.fix_note
