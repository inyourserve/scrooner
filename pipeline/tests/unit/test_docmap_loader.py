"""Docmap loader (mapper/docmap_loader.py): status vocabulary, eras, statement codes and the conflict rule (pure)."""

from __future__ import annotations

from datetime import date

import pytest

from scrooner_pipeline.mapper import docmap_loader as dl

HEADER = "ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note\n"
MD = "Latest 10-K opened: 0000000001-26-000001 (period 2025-12-31)"


def _parse(*lines: str):
    return dl.parse_docmap(HEADER + "\n".join(lines) + "\n", MD, "T-docmap-2026-11-12.csv")


def test_unknown_status_is_rejected_and_listed():
    rows, rejects = _parse(
        "T,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Revenue,,FILING-CHECKED,",
        "T,dividends_per_share,not_located,,,,,,ASSUMED,no fact",
        "T,goodwill,maybe,us-gaap:Goodwill,BS,R2.htm,Goodwill,,FILING-CHECKED,",
        "T,total_debt,component_sum,us-gaap:DebtCurrent;us-gaap:LongTermDebtNoncurrent,BS,R2;R2,Debt,,FILING-CHECKED,",
    )
    assert [r.data_point for r in rows] == ["revenue", "total_debt"]
    assert rows[1].status == "component sum"  # spelling alias, not a new status
    assert [(r["data_point"], r["why"]) for r in rejects] == [
        ("dividends_per_share", "unknown status 'not_located'"),
        ("goodwill", "unknown status 'maybe'"),
    ]


def test_accession_from_the_row_else_the_read_header_and_parts_signs():
    rows, _ = _parse(
        "T,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Revenue,,FILING-CHECKED, | accn 0000000002-26-000009 period 2025-01-01..2025-12-31",
        "T,cash_paid_for_interest,component sum,us-gaap:InterestCostsIncurred;-us-gaap:InterestCostsCapitalizedAdjustment,CF,R8;R8,x,,FILING-CHECKED,",
    )
    assert rows[0].accession == "0000000002-26-000009" and rows[1].accession == "0000000001-26-000001"
    assert rows[1].parts == ((1, "us-gaap", "InterestCostsIncurred"), (-1, "us-gaap", "InterestCostsCapitalizedAdjustment"))


def test_era_starts_where_the_read_evidence_starts():
    fy0 = date(2025, 12, 31)
    parts = ((1, "us-gaap", "Revenues"),)
    assert dl.era_from_of("same_tag@2020-12-31", parts, fy0) == date(2020, 1, 1)
    assert dl.era_from_of("ERA-CHECK: chosen tag ['2022-12-31', '2025-12-31'] ; others", parts, fy0) == date(2022, 1, 1)
    assert dl.era_from_of("tag covers last 5 FY in companyfacts", parts, fy0) == date(2021, 1, 1)
    assert dl.era_from_of("api FY coverage | FY-4 10-K same-label tag: SAME_TAG_IN_OLD(accn):us-gaap:Revenues", parts, fy0) == date(2021, 1, 1)
    assert dl.era_from_of("sum of components: not era-scanned", parts, fy0) == date(2024, 1, 1)  # fy1 only


def test_statement_codes_and_served_concepts():
    assert dl.stmt_code("Consolidated Statements of Cas", "capex_resolved", "cash_flow", value_row=True) == "CF"
    assert dl.stmt_code("PAR", "dividends_per_share_resolved", "cash_flow", value_row=True) == "UN"
    assert dl.stmt_code("", "gross_profit_resolved", "income_statement", value_row=False) == "IS"
    names = {"revenue", "revenue_sanity_resolved", "capex", "capex_resolved", "goodwill"}
    assert [dl.served_concept(n, names) for n in ("revenue", "capex", "goodwill")] == [
        "revenue_sanity_resolved", "capex_resolved", "goodwill"]


def _doc(tags: str, r_page: str = "R3.htm", status: str = "mapped") -> dl.DocmapRow:
    return dl.DocmapRow("T", "revenue_sanity_resolved", status, dl.parse_parts(tags), "IS", r_page, "Revenue",
                        date(2021, 1, 1), "0000000001-26-000001", "", "T-docmap.csv")


LIB = {"id": 7, "decision": "concept", "taxonomy": "us-gaap", "tag": "Revenues", "sign": 1, "canonical_concept_id": 1,
       "parent_concept_id": None, "components": None, "era_from": date(2015, 1, 1), "era_to": None}


def test_docmap_wins_a_disagreement_only_when_it_cites_a_filing_page():
    ids = {"revenue_sanity_resolved": 1}
    cited = dl.plan_company([LIB], [_doc("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")], ids)
    assert cited.cut == [(7, date(2020, 12, 31))] and len(cited.insert) == 1
    assert [(c["winner"], c["data_point"]) for c in cited.conflicts] == [("docmap", "revenue_sanity_resolved")]

    uncited = dl.plan_company([LIB], [_doc("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax", r_page="")], ids)
    assert uncited.cut == [] and uncited.delete == [] and uncited.insert == []
    assert [c["winner"] for c in uncited.conflicts] == ["library"]

    inside = dl.plan_company([{**LIB, "era_from": date(2022, 1, 1)}], [_doc("us-gaap:Other")], ids)
    assert inside.delete == [7] and inside.cut == []  # the library row starts inside the docmap era


def test_agreement_writes_nothing_and_lists_nothing():
    plan = dl.plan_company([LIB], [_doc("us-gaap:Revenues")], {"revenue_sanity_resolved": 1})
    assert (plan.agree, plan.insert, plan.conflicts, plan.cut) == (1, [], [], [])


def test_a_library_combined_line_is_never_cut():
    combined = {**LIB, "decision": "combined", "taxonomy": "us-gaap", "tag": "X", "canonical_concept_id": None,
                "components": ["revenue_sanity_resolved", "other"]}
    plan = dl.plan_company([combined], [_doc("us-gaap:Revenues")], {"revenue_sanity_resolved": 1})
    assert plan.insert == [] and plan.cut == [] and [c["winner"] for c in plan.conflicts] == ["library"]


def test_repeated_part_tag_is_rejected_and_fy_ended_header_dates_the_read():
    md = "- Latest 10-K 0000008670-26-000030 (CIK 0000008670, filed 2026-08-05, FY ended 2026-06-30)."
    rows, rejects = dl.parse_docmap(
        HEADER
        + "T,cost_of_revenue,component sum,us-gaap:CostOfGoodsAndServicesSold+us-gaap:CostOfGoodsAndServicesSold,IS,R3+R3,x,,FILING-CHECKED,\n"
        + "T,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Revenues,,FILING-CHECKED,accn 0000008670-26-000030\n",
        md,
        "T-docmap-2026-11-12.csv",
    )
    assert [r["why"][:22] for r in rejects] == ["a part tag repeats (di"]
    assert rows[0].era_from == date(2024, 7, 1)  # fy1 of the FY ended 2026-06-30


def test_era_shortfall_needs_a_window_period_before_the_era():
    from scrooner_pipeline.mapper import company_tag_map_plan as plan

    rows = [(1, date(2019, 1, 1), None), (1, date(2015, 1, 1), date(2018, 12, 31)), (2, date(2019, 1, 1), None),
            (None, date(2024, 1, 1), None)]
    assert plan.era_shortfall(rows, [date(2018, 12, 31), date(2025, 12, 31)]) == {2: date(2018, 12, 31)}
    assert plan.era_shortfall(rows, [date(2014, 12, 31), date(2019, 12, 31)]) == {}  # 2014 is outside the window
    gap = [(3, date(2015, 1, 1), date(2018, 12, 31)), (3, date(2021, 1, 1), None)]  # merged map with a hole
    assert plan.era_shortfall(gap, [date(2016, 12, 31), date(2019, 12, 31), date(2022, 12, 31)]) == {3: date(2019, 12, 31)}
    ok = {"era_short": {}, "fy01_before": 4, "fy01_after": 4, "values_lost": 0}
    assert plan.coverage_gate_ok(ok)
    assert not plan.coverage_gate_ok({**ok, "fy01_after": 3})
    assert not plan.coverage_gate_ok({**ok, "values_lost": 1})
    assert not plan.coverage_gate_ok({**ok, "era_short": {"x": "2019-01-01"}})


def test_machine_picks_and_unchecked_rows_are_rejected_as_unverified():
    rows, rejects = _parse(
        "T,revenue,mapped,us-gaap:Revenues,IS,R3.htm,Revenues,,FILING-CHECKED,auto: first candidate tag on face",
        "T,goodwill,mapped,us-gaap:Goodwill,BS,R2.htm,Goodwill,,FILING-CHECKED,AUTO: R3.htm read; no face row matched",
        "T,inventory,mapped,us-gaap:InventoryNet,BS,R2.htm,Inventory,,FILING-CHECKED,tag picked; not hand-verified",
        "T,capex,mapped,us-gaap:PaymentsToAcquirePropertyPlantAndEquipment,CF,R6.htm,Capex,,ASSUMED,",
        "T,sbc,mapped,us-gaap:ShareBasedCompensation,CF,R6.htm,SBC,,FILING-CHECKED,auto-reader: manual override",
        "T,cash_paid_for_interest,mapped,us-gaap:InterestPaidNet,NOTE,R60.htm,Interest paid,,FILING-CHECKED,",
    )
    assert [r.data_point for r in rows] == ["sbc", "cash_paid_for_interest"]
    assert [(r["data_point"], r["why"]) for r in rejects] == [
        (dp, "unverified") for dp in ("revenue", "goodwill", "inventory", "capex")
    ]
    assert dl.stmt_code("NOTE", "cash_paid_for_interest", "cash_flow", value_row=True) == "UN"


def test_docmap_era_from_2021_leaves_earlier_library_eras_and_period_reasons_intact():
    ids = {"revenue_sanity_resolved": 1}
    early = {**LIB, "id": 1, "era_from": date(2015, 1, 1), "era_to": date(2020, 12, 31)}
    open_row = {**LIB, "id": 2, "tag": "SalesRevenueNet", "era_from": date(2015, 1, 1), "era_to": None}
    reason = {**LIB, "id": 3, "decision": "not_presented", "taxonomy": None, "tag": None,
              "era_from": date(2023, 12, 31), "era_to": date(2023, 12, 31)}
    plan = dl.plan_company([early, open_row, reason], [_doc("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")], ids)
    assert plan.cut == [(2, date(2020, 12, 31))] and plan.delete == []  # 2015-2020 kept; the period reason kept
    assert len(plan.insert) == 1


def test_a_docmap_reason_never_cuts_a_library_value():
    reason_doc = dl.DocmapRow("T", "revenue_sanity_resolved", "not_presented", (), "IS", "R3.htm", "", date(2021, 1, 1),
                              "0000000001-26-000001", "no line", "T-docmap.csv")
    plan = dl.plan_company([LIB], [reason_doc], {"revenue_sanity_resolved": 1})
    assert plan.cut == [] and plan.delete == [] and len(plan.insert) == 1
    assert [c["winner"] for c in plan.conflicts] == ["coexist"]


def test_a_combined_line_replaces_the_library_period_reasons_inside_its_era():
    reason = {**LIB, "id": 3, "decision": "not_in_template", "taxonomy": None, "tag": None,
              "era_from": date(2024, 12, 31), "era_to": date(2024, 12, 31)}
    combined = dl.DocmapRow("T", "revenue_sanity_resolved", "combined", dl.parse_parts("us-gaap:X"), "IS", "R3.htm",
                            "Revenue and other", date(2024, 1, 1), "0000000001-26-000001", "", "T-docmap.csv")
    plan = dl.plan_company([reason], [combined], {"revenue_sanity_resolved": 1})
    assert plan.delete == [3] and len(plan.insert) == 1  # no overlapping reason rows left behind


def test_member_qualified_parts_parse_into_tag_and_segments():
    rows, rejects = _parse(
        "T,cost_of_revenue,component sum,us-gaap:CostOfGoodsAndServicesSold[ProductOrService=Product]+us-gaap:CostOfGoodsAndServicesSold[ProductOrService=Service],IS,R4+R4,x,,FILING-CHECKED,",
        "T,amortization_of_intangibles,component sum,us-gaap:AmortizationOfIntangibleAssets[StatementOfIncomeLocationBalance=us-gaap:OperatingExpenses],IS,R4,x,,FILING-CHECKED,",
        "T,revenue,mapped,us-gaap:Revenues,IS,R4.htm,Revenues,,FILING-CHECKED,",
    )
    assert rejects == []
    assert [(r.data_point, r.parts, r.dims) for r in rows] == [
        (
            "cost_of_revenue",
            ((1, "us-gaap", "CostOfGoodsAndServicesSold"), (1, "us-gaap", "CostOfGoodsAndServicesSold")),
            ("ProductOrService=Product;", "ProductOrService=Service;"),
        ),
        (
            "amortization_of_intangibles",
            ((1, "us-gaap", "AmortizationOfIntangibleAssets"),),
            ("StatementOfIncomeLocationBalance=OperatingExpenses;",),
        ),
        ("revenue", ((1, "us-gaap", "Revenues"),), ()),
    ]


def test_dims_are_normalized_to_the_fsn_segments_format():
    assert dl.normalize_dims("ClassOfStock=us-gaap:CommonClassAMember") == "ClassOfStock=CommonClassA;"
    assert (
        dl.normalize_dims("us-gaap:ProductOrServiceAxis=Gaming,BusinessSegments=amzn:GamingMember")
        == "BusinessSegments=Gaming;ProductOrService=Gaming;"
    )  # axes sorted, no Axis / Member suffix, no namespace prefix
    for bad in ("Product", "A=B,A=C", "A=B C"):
        with pytest.raises(ValueError, match="member_syntax"):
            dl.normalize_dims(bad)


def test_malformed_member_syntax_and_repeats_are_rejected_alone():
    rows, rejects = _parse(
        "T,cost_of_revenue,component sum,us-gaap:CostOfGoodsAndServicesSold[ProductOrService]+us-gaap:Other,IS,R4+R4,x,,FILING-CHECKED,",
        "T,sga_expense,component sum,us-gaap:Selling[A=B]+us-gaap:Selling[A=B],IS,R4+R4,x,,FILING-CHECKED,",
        "T,revenue,mapped,us-gaap:Revenues,IS,R4.htm,Revenues,,FILING-CHECKED,",
    )
    assert [r.data_point for r in rows] == ["revenue"]
    assert [(r["data_point"], r["why"][:14]) for r in rejects] == [
        ("cost_of_revenue", "member_syntax:"),
        ("sga_expense", "a part tag rep"),
    ]


def test_the_table_check_is_mirrored_so_a_refusable_row_is_refused_alone():
    from scrooner_pipeline.mapper.company_tag_map_seed import dims_refusal

    assert dims_refusal("component", "ProductOrService=Product;") is None
    assert dims_refusal("concept", "ClassOfStock=CommonClassA;") is None
    assert dims_refusal("concept", "ProductOrService=Product;")  # a slice is never the data point
    assert dims_refusal("concept", "ClassOfStock=A;ProductOrService=P;")  # two axes
    assert dims_refusal("component", "ProductOrService Product")  # not segments format
    assert dims_refusal("concept", "") is None


def test_a_dims_row_competes_by_dims_in_the_library_signature():
    d = dl.DocmapRow("T", "revenue", "component sum", ((1, "us-gaap", "X"),), "IS", "R3", "", date(2020, 1, 1),
                     "0000000001-26-000001", "", "T.csv", None, ("ProductOrService=Product;",))
    plain = dl.DocmapRow("T", "revenue", "component sum", ((1, "us-gaap", "X"),), "IS", "R3", "", date(2020, 1, 1),
                         "0000000001-26-000001", "", "T.csv")
    assert dl._signature_doc(d) != dl._signature_doc(plain)
    lib = [{"decision": "component", "taxonomy": "us-gaap", "tag": "X", "sign": 1, "dims": "ProductOrService=Product;"}]
    assert dl._signature_lib(lib) == dl._signature_doc(d)
