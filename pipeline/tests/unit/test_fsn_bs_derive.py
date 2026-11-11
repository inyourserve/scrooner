"""fsn_store.bs_derive: total liabilities from the filing's own calc tree / L&E identity (same accession, never
invented), and the not-presented reason for an unclassified balance sheet. Numbers are the filings' own:
NEE 10-Q 0000753308-20-000150 (2020-06-30, capitalization-format balance sheet, no total-liabilities line)."""

from decimal import Decimal as D

from scrooner_pipeline.fsn_store import bs_derive as bd

NEE_FACE = [
    {"tag": t, "label": lab, "custom": False}
    for t, lab in (
        ("Assets", "TOTAL ASSETS"),
        (
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "Total equity",
        ),
        ("LongTermDebtNoncurrent", "Long-term debt"),
        ("CapitalizationLongtermDebtAndEquity", "Total capitalization"),
        ("LiabilitiesCurrent", "Total current liabilities"),
        ("LiabilitiesNoncurrent", "Total other liabilities and deferred credits"),
        ("CommitmentsAndContingencies", "COMMITMENTS AND CONTINGENCIES"),
        (
            "RedeemableNoncontrollingInterestEquityCarryingAmount",
            "REDEEMABLE NONCONTROLLING INTERESTS",
        ),
        ("LiabilitiesAndStockholdersEquity", "TOTAL CAPITALIZATION AND LIABILITIES"),
    )
]
NEE_ARCS = {
    "LiabilitiesAndStockholdersEquity": [
        ("CapitalizationLongtermDebtAndEquity", 1),
        ("LiabilitiesCurrent", 1),
        ("LiabilitiesNoncurrent", 1),
        ("CommitmentsAndContingencies", 1),
        ("RedeemableNoncontrollingInterestEquityCarryingAmount", 1),
    ],
    "CapitalizationLongtermDebtAndEquity": [
        ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", 1),
        ("LongTermDebtNoncurrent", 1),
    ],
}
NEE_COL = {
    t: (D(v), i)
    for i, (t, v) in enumerate(
        (
            ("Assets", "121961000000"),
            ("LiabilitiesAndStockholdersEquity", "121961000000"),
            (
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                "41574000000",
            ),
            ("LongTermDebtNoncurrent", "42667000000"),
            ("CapitalizationLongtermDebtAndEquity", "84241000000"),
            ("LiabilitiesCurrent", "12365000000"),
            ("LiabilitiesNoncurrent", "25064000000"),
            ("RedeemableNoncontrollingInterestEquityCarryingAmount", "291000000"),
        )
    )
}


def test_calc_route_expands_the_capitalization_subtotal():
    (value, ids), rule, inputs = bd.derive_tl(NEE_FACE, NEE_ARCS, NEE_COL)
    assert rule == bd.RULE_CALC
    assert value == D(
        "80096000000"
    )  # 12,365 + 25,064 + 42,667; with equity 41,574 + temporary 291 = L&E 121,961
    assert [c for c, _w, _v in inputs["mezz"]] == [
        "RedeemableNoncontrollingInterestEquityCarryingAmount"
    ]
    assert len(ids) == 1 + 5


def test_calc_route_refuses_when_children_do_not_tie_or_a_child_is_blank():
    off = dict(NEE_COL, LiabilitiesCurrent=(D("12000000000"), 9))
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, off)[1] == "calc_children_do_not_tie_le"
    # a blank child counts as zero only when the valued children still tie to L&E: here they do not
    blank = {k: v for k, v in NEE_COL.items() if k != "LiabilitiesNoncurrent"}
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, blank)[1] == "calc_children_do_not_tie_le"


def test_blank_child_is_zero_only_when_the_tie_proves_it():
    arcs = dict(NEE_ARCS)
    arcs["LiabilitiesAndStockholdersEquity"] = arcs[
        "LiabilitiesAndStockholdersEquity"
    ] + [("OperatingLeaseLiabilityNoncurrent", 1)]
    (value, _ids), _rule, inputs = bd.derive_tl(
        NEE_FACE, arcs, NEE_COL
    )  # the lease line is printed blank
    assert value == D("80096000000")
    assert sorted(inputs["blank_children"]) == [
        "CommitmentsAndContingencies",
        "OperatingLeaseLiabilityNoncurrent",
    ]
    valued_commitments = dict(NEE_COL, CommitmentsAndContingencies=(D("5"), 99))
    assert (
        bd.derive_tl(NEE_FACE, NEE_ARCS, valued_commitments)[1]
        == "calc_child_noise_valued:CommitmentsAndContingencies"
    )
    zero_commitments = dict(NEE_COL, CommitmentsAndContingencies=(D("0"), 99))
    assert bd.derive_tl(NEE_FACE, NEE_ARCS, zero_commitments)[0][0] == D("80096000000")


def test_printed_total_liabilities_is_never_derived():
    face = NEE_FACE + [
        {"tag": "Liabilities", "label": "Total liabilities", "custom": False}
    ]
    assert bd.derive_tl(face, NEE_ARCS, NEE_COL)[0] is None


def test_identity_route_only_without_calc_arcs_and_with_printed_terms():
    (value, _ids), rule, _inputs = bd.derive_tl(NEE_FACE, {}, NEE_COL)
    assert rule == bd.RULE_IDENTITY and value == D("121961000000") - D(
        "41574000000"
    ) - D("291000000")
    no_equity = {
        k: v for k, v in NEE_COL.items() if not k.startswith("StockholdersEquity")
    }
    assert bd.derive_tl(NEE_FACE, {}, no_equity)[0] is None


def test_unclassified_balance_sheet():
    bank = [
        {"tag": t, "label": lab, "custom": False}
        for t, lab in (
            ("CashAndDueFromBanks", "Cash and due from banks"),
            ("LoansAndLeasesReceivableNetReportedAmount", "Loans, net"),
            ("Assets", "Total assets"),
            ("Deposits", "Deposits"),
            ("Liabilities", "Total liabilities"),
        )
    ]
    assert bd.unclassified(bank)
    assert not bd.unclassified(NEE_FACE)  # prints Total current liabilities
    custom_current = bank + [
        {"tag": "TotalCurrentAssetsX", "label": "Total current assets", "custom": True}
    ]
    assert not bd.unclassified(custom_current)


def test_current_total_in_another_statement_blocks_the_unclassified_reason():
    """Planet Fitness 10-Q 0001193125-15-310710: the registrant shell's balance sheet (stmt BS) has no current items,
    but the operating predecessor's classified balance sheet in the same filing (stmt UN) prints AssetsCurrent."""
    shell = [
        {"tag": t, "label": t, "custom": False}
        for t in (
            "Assets",
            "CommitmentsAndContingencies",
            "CommonStockValue",
            "StockholdersEquity",
            "LiabilitiesAndStockholdersEquity",
        )
    ]
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

    filings = {
        7: sel.Filing(
            7,
            "0000753308-20-000150",
            datetime(2020, 7, 24),
            "10-Q",
            date(2020, 6, 30),
            2020,
            "Q2",
            "1231",
        )
    }
    (value, ids), rule, inputs = bd.derive_tl(NEE_FACE, NEE_ARCS, NEE_COL)
    derived = sel.Cell(
        bd.TL,
        date(2020, 6, 30),
        0,
        "derived",
        value=value,
        filing_id=7,
        source_value_ids=ids,
        rule_id=rule,
        derivation={
            "formula": "sum of the L&E calc children classed liability",
            "accession": "0000753308-20-000150",
            "inputs": inputs,
        },
    )
    reasoned = sel.Cell(
        bd.CA,
        date(2020, 6, 30),
        0,
        "not_presented",
        filing_id=7,
        rule_id=bd.RULE_UNCLASSIFIED,
        reason_code=bd.REASON,
        input_refs={"accession": "0000753308-20-000150", "face_lines": 9},
    )
    for c in (derived, reasoned):
        row = json.loads(json.dumps(sel.to_row(c, 1, filings), default=str))
        parsed = cell_loader.parse_row(1, row, {bd.TL, bd.CA, bd.CL})
        assert not isinstance(parsed, str), parsed
        assert parsed.state == c.state
    assert sel.REASON_TEXT[bd.REASON]


KMB_FACE = [
    {"tag": t, "label": lab, "custom": t.startswith("Redeemable")}
    for t, lab in (
        ("Assets", "TOTAL ASSETS"),
        ("LiabilitiesCurrent", "Total Current Liabilities"),
        ("LongTermDebtAndCapitalLeaseObligations", "Long-Term Debt"),
        (
            "PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent",
            "Noncurrent Employee Benefits",
        ),
        ("DeferredIncomeTaxLiabilitiesNet", "Deferred Income Taxes"),
        ("OtherLiabilitiesNoncurrent", "Other Liabilities"),
        (
            "RedeemableCommonAndPreferredSecuritiesOfSubsidiaries",
            "Redeemable Preferred Securities of Subsidiaries",
        ),
        ("PreferredStockSharesIssued", "Preferred Stock, Shares Issued"),
        ("StockholdersEquity", "Equity, Attributable to Parent, Total"),
        ("MinorityInterest", "Noncontrolling Interests"),
        (
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "Total Stockholders' Equity",
        ),
        (
            "LiabilitiesAndStockholdersEquity",
            "TOTAL LIABILITIES AND STOCKHOLDERS' EQUITY",
        ),
    )
]
KMB_COL = {
    t: (D(v), i)
    for i, (t, v) in enumerate(
        (
            ("Assets", "17092000000"),
            ("LiabilitiesAndStockholdersEquity", "17092000000"),
            ("LiabilitiesCurrent", "6878000000"),
            ("LongTermDebtAndCapitalLeaseObligations", "7161000000"),
            (
                "PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent",
                "652000000",
            ),
            ("DeferredIncomeTaxLiabilitiesNet", "395000000"),
            ("OtherLiabilitiesNoncurrent", "796000000"),
            ("RedeemableCommonAndPreferredSecuritiesOfSubsidiaries", "26000000"),
            (
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                "1184000000",
            ),
        )
    )
}


def test_redeemable_line_between_liabilities_and_equity_is_temporary_equity():
    """Kimberly-Clark 10-Q 0000055785-24-000054, 2024-03-31 (Verifier VERIFY-BS-DERIVE-2026-11-08): "Redeemable
    Preferred Securities of Subsidiaries" ($26M) sits after Other Liabilities and before equity. It is mezzanine, not
    a liability: total liabilities 15,882, not 15,908, in both routes."""
    arcs = {
        "LiabilitiesAndStockholdersEquity": [
            (t, 1)
            for t in (
                "LiabilitiesCurrent",
                "DeferredIncomeTaxLiabilitiesNet",
                "PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent",
                "OtherLiabilitiesNoncurrent",
                "LongTermDebtAndCapitalLeaseObligations",
                "RedeemableCommonAndPreferredSecuritiesOfSubsidiaries",
                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            )
        ]
    }
    (value, _ids), rule, inputs = bd.derive_tl(KMB_FACE, arcs, KMB_COL)
    assert rule == bd.RULE_CALC and value == D("15882000000")
    assert [c for c, _w, _v in inputs["mezz"]] == [
        "RedeemableCommonAndPreferredSecuritiesOfSubsidiaries"
    ]
    (value, _ids), rule, _inputs = bd.derive_tl(KMB_FACE, {}, KMB_COL)
    assert rule == bd.RULE_IDENTITY and value == D("15882000000")
    # the same line printed AMONG the liabilities (another liability after it) stays a liability
    among = KMB_FACE[:5] + [KMB_FACE[6], KMB_FACE[5]] + KMB_FACE[7:]
    assert bd.derive_tl(among, arcs, KMB_COL)[0][0] == D("15908000000")
    # "mandatorily redeemable" (ASC 480) is a liability wherever it is printed
    mand = [
        dict(f, label="Mandatorily redeemable preferred stock")
        if f["tag"].startswith("Redeemable")
        else f
        for f in KMB_FACE
    ]
    assert bd.derive_tl(mand, arcs, KMB_COL)[0][0] == D("15908000000")


def test_an_unconfirmed_total_is_not_presented_never_a_sum_of_face_lines():
    """Ruling (Dhairya 2026-11-11): a sum of printed face lines only where the calc tree or the section confirms
    completeness, otherwise not_presented. NEE's children with Other liabilities altered no longer tie to L&E: the
    column gets a not_presented cell carrying the reason, and it passes the cell-loader contract; a printed total
    gets no cell from here (select serves it); a confirmed derivation stays derived."""
    import json
    from datetime import date, datetime

    from scrooner_pipeline.fsn_store import select as sel
    from scrooner_pipeline.normalizer import cell_loader

    off = dict(NEE_COL, LiabilitiesCurrent=(D("12000000000"), 9))
    res, rule, inputs = bd.derive_tl(NEE_FACE, NEE_ARCS, off)
    cell = bd.tl_cell(date(2020, 6, 30), 7, "0000753308-20-000150", res, rule, inputs)
    assert (cell.state, cell.reason_code, cell.value) == (
        "not_presented",
        bd.REASON_TL,
        None,
    )
    assert cell.input_refs == {
        "accession": "0000753308-20-000150",
        "not_derived": "calc_children_do_not_tie_le",
    }
    filings = {
        7: sel.Filing(
            7,
            "0000753308-20-000150",
            datetime(2020, 7, 24),
            "10-Q",
            date(2020, 6, 30),
            2020,
            "Q2",
            "1231",
        )
    }
    row = json.loads(json.dumps(sel.to_row(cell, 1, filings), default=str))
    assert row["reason_text"] and not isinstance(
        cell_loader.parse_row(1, row, {bd.TL}), str
    )
    printed = NEE_FACE + [
        {"tag": "Liabilities", "label": "Total liabilities", "custom": False}
    ]
    res, rule, inputs = bd.derive_tl(printed, NEE_ARCS, NEE_COL)
    assert bd.tl_cell(date(2020, 6, 30), 7, "x", res, rule, inputs) is None
    res, rule, inputs = bd.derive_tl(NEE_FACE, NEE_ARCS, NEE_COL)
    ok = bd.tl_cell(date(2020, 6, 30), 7, "x", res, rule, inputs)
    assert ok.state == "derived" and ok.value == D("80096000000")
