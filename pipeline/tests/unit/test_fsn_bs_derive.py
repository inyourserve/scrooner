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


def test_current_total_in_another_statement_blocks_the_unclassified_reason():
    """Planet Fitness 10-Q 0001193125-15-310710: the registrant shell's balance sheet (stmt BS) has no current items,
    but the operating predecessor's classified balance sheet in the same filing (stmt UN) prints AssetsCurrent."""
    shell = [{"tag": t, "label": t, "custom": False} for t in ("Assets", "CommitmentsAndContingencies", "CommonStockValue",
                                                               "StockholdersEquity", "LiabilitiesAndStockholdersEquity")]
    assert bd.unclassified(shell)
    assert bd.current_reason(shell, current_in_filing=True) is None
    assert bd.current_reason(shell, current_in_filing=False) == bd.REASON
    assert bd.current_reason(NEE_FACE, current_in_filing=False) is None


def test_derived_and_not_presented_rows_pass_the_cell_loader_contract():
    """The rows pilot.report_company adds go to the FSN write path (jobs/fsn.py writes them with json default=str,
    normalizer.cell_loader.parse_row reads them): a derived total and an unclassified reason must both be accepted."""
    import json
    from datetime import date, datetime

    from scrooner_pipeline.fsn_store import select as sel
    from scrooner_pipeline.normalizer import cell_loader

    filings = {7: sel.Filing(7, "0000753308-20-000150", datetime(2020, 7, 24), "10-Q", date(2020, 6, 30), 2020, "Q2", "1231")}
    (value, ids), rule, inputs = bd.derive_tl(NEE_FACE, NEE_ARCS, NEE_COL)
    derived = sel.Cell(bd.TL, date(2020, 6, 30), 0, "derived", value=value, filing_id=7, source_value_ids=ids, rule_id=rule,
                       derivation={"formula": "sum of the L&E calc children classed liability",
                                   "accession": "0000753308-20-000150", "inputs": inputs})
    reasoned = sel.Cell(bd.CA, date(2020, 6, 30), 0, "not_presented", filing_id=7, rule_id=bd.RULE_UNCLASSIFIED,
                        reason_code=bd.REASON, input_refs={"accession": "0000753308-20-000150", "face_lines": 9})
    for c in (derived, reasoned):
        row = json.loads(json.dumps(sel.to_row(c, 1, filings), default=str))
        parsed = cell_loader.parse_row(1, row, {bd.TL, bd.CA, bd.CL})
        assert not isinstance(parsed, str), parsed
        assert parsed.state == c.state
    assert sel.REASON_TEXT[bd.REASON]
