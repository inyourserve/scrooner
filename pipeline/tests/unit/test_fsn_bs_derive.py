"""fsn_store.bs_derive: total liabilities from the filing's own calc tree / L&E identity (same accession, never
invented), and the not-presented reason for an unclassified balance sheet. Numbers are the filings' own:
NEE 10-Q 0000753308-20-000150 (2020-06-30, capitalization-format balance sheet, no total-liabilities line)."""

from decimal import Decimal as D

from scrooner_pipeline.fsn_store import bs_derive as bd

NEE_FACE = [{"tag": t, "label": lab, "custom": False} for t, lab in (
    ("Assets", "TOTAL ASSETS"),
    ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "Total equity"),
    ("LongTermDebtNoncurrent", "Long-term debt"),
    ("CapitalizationLongtermDebtAndEquity", "Total capitalization"),
    ("LiabilitiesCurrent", "Total current liabilities"),
    ("LiabilitiesNoncurrent", "Total other liabilities and deferred credits"),
    ("CommitmentsAndContingencies", "COMMITMENTS AND CONTINGENCIES"),
    ("RedeemableNoncontrollingInterestEquityCarryingAmount", "REDEEMABLE NONCONTROLLING INTERESTS"),
    ("LiabilitiesAndStockholdersEquity", "TOTAL CAPITALIZATION AND LIABILITIES"))]
NEE_ARCS = {
    "LiabilitiesAndStockholdersEquity": [("CapitalizationLongtermDebtAndEquity", 1), ("LiabilitiesCurrent", 1), ("LiabilitiesNoncurrent", 1),
                                         ("CommitmentsAndContingencies", 1), ("RedeemableNoncontrollingInterestEquityCarryingAmount", 1)],
    "CapitalizationLongtermDebtAndEquity": [("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", 1), ("LongTermDebtNoncurrent", 1)],
}
NEE_COL = {t: (D(v), i) for i, (t, v) in enumerate((
    ("Assets", "121961000000"), ("LiabilitiesAndStockholdersEquity", "121961000000"),
    ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "41574000000"),
    ("LongTermDebtNoncurrent", "42667000000"), ("CapitalizationLongtermDebtAndEquity", "84241000000"),
    ("LiabilitiesCurrent", "12365000000"), ("LiabilitiesNoncurrent", "25064000000"),
    ("RedeemableNoncontrollingInterestEquityCarryingAmount", "291000000")))}


def test_calc_route_expands_the_capitalization_subtotal():
    (value, ids), rule, inputs = bd.derive_tl(NEE_FACE, NEE_ARCS, NEE_COL)
    assert rule == bd.RULE_CALC
    assert value == D("80096000000")  # 12,365 + 25,064 + 42,667; with equity 41,574 + temporary 291 = L&E 121,961
    assert [c for c, _w, _v in inputs["mezz"]] == ["RedeemableNoncontrollingInterestEquityCarryingAmount"]
    assert len(ids) == 1 + 5


def test_calc_route_refuses_when_children_do_not_tie_or_a_child_is_blank():
    off = dict(NEE_COL, LiabilitiesCurrent=(D("12000000000"), 9))
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, off)[1] == "calc_children_do_not_tie_le"
    # a blank child counts as zero only when the valued children still tie to L&E: here they do not
    blank = {k: v for k, v in NEE_COL.items() if k != "LiabilitiesNoncurrent"}
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, blank)[1] == "calc_children_do_not_tie_le"


def test_blank_child_is_zero_only_when_the_tie_proves_it():
    arcs = dict(NEE_ARCS)
    arcs["LiabilitiesAndStockholdersEquity"] = arcs["LiabilitiesAndStockholdersEquity"] + [("OperatingLeaseLiabilityNoncurrent", 1)]
    (value, _ids), _rule, inputs = bd.derive_tl(NEE_FACE, arcs, NEE_COL)  # the lease line is printed blank
    assert value == D("80096000000")
    assert sorted(inputs["blank_children"]) == ["CommitmentsAndContingencies", "OperatingLeaseLiabilityNoncurrent"]
    valued_commitments = dict(NEE_COL, CommitmentsAndContingencies=(D("5"), 99))
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, valued_commitments)[1] == "calc_child_noise_valued:CommitmentsAndContingencies"
    zero_commitments = dict(NEE_COL, CommitmentsAndContingencies=(D("0"), 99))
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, zero_commitments)[0][0] == D("80096000000")


def test_printed_total_liabilities_is_never_derived():
    face = NEE_FACE + [{"tag": "Liabilities", "label": "Total liabilities", "custom": False}]
    assert bd.derive_tl(face, NEE_ARCS, NEE_COL)[0] is None


def test_identity_route_only_without_calc_arcs_and_with_printed_terms():
    (value, _ids), rule, _inputs = bd.derive_tl(NEE_FACE, {}, NEE_COL)
    assert rule == bd.RULE_IDENTITY and value == D("121961000000") - D("41574000000") - D("291000000")
    no_equity = {k: v for k, v in NEE_COL.items() if not k.startswith("StockholdersEquity")}
    assert bd.derive_tl(NEE_FACE, {}, no_equity)[0] is None


def test_unclassified_balance_sheet():
    bank = [{"tag": t, "label": lab, "custom": False} for t, lab in (
        ("CashAndDueFromBanks", "Cash and due from banks"), ("LoansAndLeasesReceivableNetReportedAmount", "Loans, net"),
        ("Assets", "Total assets"), ("Deposits", "Deposits"), ("Liabilities", "Total liabilities"))]
    assert bd.unclassified(bank)
    assert not bd.unclassified(NEE_FACE)  # prints Total current liabilities
    custom_current = bank + [{"tag": "TotalCurrentAssetsX", "label": "Total current assets", "custom": True}]
    assert not bd.unclassified(custom_current)
