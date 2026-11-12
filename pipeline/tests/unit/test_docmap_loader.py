"""Docmap loader (mapper/docmap_loader.py): status vocabulary, eras, statement codes and the conflict rule (pure)."""

from __future__ import annotations

from datetime import date

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
