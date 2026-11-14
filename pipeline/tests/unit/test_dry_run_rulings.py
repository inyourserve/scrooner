"""Rulings 2026-11-14 from the first dry run outside the 110 (ranks 117-137): FCX inventory under an 'Inventories:' header, the MAR matrix
cost line, CEG's legal-entity face, and the per-accession instance evidence for total_debt (data-team/tags/line_map/tools)."""

from __future__ import annotations

import sys
from decimal import Decimal as D
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[3] / "data-team" / "tags" / "line_map" / "tools"
sys.path.insert(0, str(TOOLS))
import instance_evidence as IE  # noqa: E402
import resolve_all as RA  # noqa: E402
import resolve_bs as B  # noqa: E402
import standard_inputs as si  # noqa: E402

pytestmark = pytest.mark.unit


def _l(ln, tag, lb, val=None, custom=False, prole="terseLabel"):
    return dict(st="BS", rep=2, ln=ln, tag=tag, lb=lb, val=None if val is None else D(val), custom=custom, prole=prole)


FCX = [_l(9, "InventoryNetAbstract", "Inventories:"), _l(10, "InventoryRawMaterialsAndSuppliesNetOfReserves", "Total materials and supplies, net", 1594),
       _l(11, "InventoryMillandStockpilesonLeachPadsCurrent", "Mill and leach stockpiles", 1014, custom=True), _l(12, "Product", "Product", 1285, custom=True),
       _l(13, "OtherAssetsCurrent", "Other current assets", 341), _l(14, "AssetsCurrent", "Total current assets", 9303, prole="totalLabel")]


def test_inventory_header_sum_replaces_a_component_or_note_pick():
    r = B.inventory_header_sum(FCX, dict(status="mapped", value=D(19), nodes="MaterialsSuppliesAndOther=19 [NOTE]", rule="note"))
    assert r["value"] == D(3893) and r["flags"] == "header_sum" and "OtherAssetsCurrent" not in r["nodes"]
    total = FCX[:4] + [_l(13, "InventoryNet", "Total inventories", 3893, prole="totalLabel")] + FCX[4:]
    assert B.inventory_header_sum(total, None) is None                                   # a printed inventory total: the normal pick
    assert B.inventory_header_sum(FCX[:2] + FCX[4:], None) is None                        # one line under the header is not a sum
    # CEG: 'Renewable energy credits' after the inventory lines is not inventory (FSN marks the new standard element custom)
    ceg = [_l(9, "InventoryNetAbstract", "Inventories, net"), _l(10, "EnergyRelatedInventoryNaturalGasInStorage", "Natural gas, oil, and emission allowances", 243),
           _l(11, "InventoryRawMaterialsAndSuppliesNetOfReserves", "Materials and supplies", 1357), _l(12, "RenewableEnergyCreditsCurrent", "Renewable energy credits", 797, custom=True),
           _l(13, "OtherAssetsCurrent", "Other", 5)]
    assert B.inventory_header_sum(ceg, None)["value"] == D(1600)
    # a reported InventoryNet bounds the group to the run that sums to it; nothing ties: no header sum
    assert B.inventory_header_sum(FCX, None, {"InventoryNet": D(2608)})["value"] == D(2608)
    assert B.inventory_header_sum(FCX, None, {"InventoryNet": D(7)}) is None


def test_matrix_cost_line_needs_a_cost_of_revenue_label_and_the_tie():
    C = "CostOfRevenue"
    mf = {"MAR": f"{C}|4|15141|ProductOrService=Reimbursements;~{C}|4|1074|ProductOrService=OwnedLeasedandOther;"}
    x = si.cost_member_sums({}, mf)["MAR"]
    assert x["total"] == "16215" and list(x["members"]) == ["OwnedLeasedandOther", "Reimbursements"]
    def filing(label, ce):
        ls = ["IS|2|14|Revenues|0|0|totalLabel|Total revenue|20773", f"IS|2|16|{C}|0|0|terseLabel|{label}|",
              "IS|2|17|DepreciationAmortizationAndOther|1|0|terseLabel|Depreciation, amortization, and other|193",
              "IS|2|18|GeneralAndAdministrativeExpense|0|0|terseLabel|General, administrative, and other|891",
              f"IS|2|20|CostsAndExpenses|0|0|totalLabel|Costs and expenses|{ce}"]
        return dict(cik="1", a="MAR", p="2022-12-31", fd="", lines="~".join(ls), calc="")
    row = lambda: [dict(ticker="MAR", accession="MAR", period_end="2022-12-31", data_point="cost_of_revenue", status="not_presented", value=None, flags="")]
    RA.EXT["cor_mx"] = {"MAR": x}
    assert RA.apply_cost_and_opex(row(), [filing("Cost of revenues", 17299)])[0]["value"] == D(16215)
    assert RA.apply_cost_and_opex(row(), [filing("Cost of revenues", 18000)])[0]["status"] == "not_presented"   # no tie
    assert RA.apply_cost_and_opex(row(), [filing("Costs and expenses", 17299)])[0]["status"] == "not_presented"  # DE: rows, not columns
    RA.EXT["cor_mx"] = {}


def test_legal_entity_face_filer_member_fills_and_coregistrant_is_a_reason():
    le = si.legal_entity_faces({"A": "Assets|0|5|Gen|Gen~Revenues|4|7|Gen|Gen", "B": "Assets|0|5|Parent|", "C": "Assets|0|5|X|X~Assets|0|6|Y|Y"})
    assert le["A"]["coregistrant"] == "Gen" and le["B"]["coregistrant"] == "" and le["C"] is None
    f = dict(a="B", lines="BS|2|3|Assets|0|0|totalLabel|Total assets|~BS|2|4|Cash|0|0|terseLabel|Cash|")
    assert si.fill_face_values(f, le["B"]["facts"])["lines"] == "BS|2|3|Assets|0|0|totalLabel|Total assets|5~BS|2|4|Cash|0|0|terseLabel|Cash|"
    assert si.no_face_value([f, dict(a="Z", lines="IS|2|1|Revenues|0|0|x|Rev|9")]) == ["B"]


INSTANCE = """<xbrli:context id="c1"><xbrli:entity/><xbrli:period><xbrli:instant>2016-06-30</xbrli:instant></xbrli:period></xbrli:context>
<xbrli:context id="c2"><xbrli:entity><xbrli:segment><xbrldi:explicitMember dimension="us-gaap:BalanceSheetLocationAxis">us-gaap:OtherLiabilitiesCurrentMember</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2016-06-30</xbrli:instant></xbrli:period></xbrli:context>
<xbrli:context id="c3"><xbrli:entity><xbrli:segment><xbrldi:explicitMember dimension="us-gaap:StatementBusinessSegmentsAxis">x:SegMember</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2016-06-30</xbrli:instant></xbrli:period></xbrli:context>
<us-gaap:CapitalLeaseObligationsCurrent contextRef="c2" decimals="-6">25000000</us-gaap:CapitalLeaseObligationsCurrent>
<us-gaap:CapitalLeaseObligations contextRef="c1" decimals="-6">786000000</us-gaap:CapitalLeaseObligations>
<us-gaap:CapitalLeaseObligations contextRef="c3" decimals="-6">5</us-gaap:CapitalLeaseObligations>
<us-gaap:FinanceLeaseLiabilityCurrentStatementOfFinancialPositionExtensibleList contextRef="c1">http://fasb.org/us-gaap/2019#OtherLiabilitiesCurrent</us-gaap:FinanceLeaseLiabilityCurrentStatementOfFinancialPositionExtensibleList>"""


def test_instance_evidence_reads_location_list_and_lease_facts():
    fl, facts = IE.read_instance(INSTANCE, "2016-06-30")
    assert fl == ["OtherLiabilitiesCurrent"]
    assert sorted(facts) == [["CapitalLeaseObligations", "2016-06-30", "", "786000000"],
                             ["CapitalLeaseObligationsCurrent", "2016-06-30", "us-gaap:OtherLiabilitiesCurrentMember", "25000000"]]   # a segment fact is dropped
    assert IE.loc_of(["OtherLiabilitiesCurrent"], []) == "out" and IE.loc_of(["LongTermDebtNoncurrent"], []) == "in"
    assert IE.loc_of([], ["us-gaap_LongTermDebtAndCapitalLeaseObligations"]) == "in" and IE.loc_of([], []) == "none"
    with pytest.raises(AssertionError):
        IE._get("https://example.com/x")   # sec.gov only
