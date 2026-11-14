"""Docmap loader (mapper/docmap_loader.py): status vocabulary, eras, statement codes and the conflict rule (pure)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from scrooner_pipeline.mapper import docmap_loader as dl

HEADER = "ticker,data_point,status,tags,stmt,r_page,label,era_from_note,evidence_class,note\n"
MD = "Latest 10-K opened: 0000000001-26-000001 (period 2025-12-31)"


def _parse(*lines: str):
    return dl.parse_docmap(
        HEADER + "\n".join(lines) + "\n", MD, "T-docmap-2026-11-12.csv"
    )


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
    assert (
        rows[0].accession == "0000000002-26-000009"
        and rows[1].accession == "0000000001-26-000001"
    )
    assert rows[1].parts == (
        (1, "us-gaap", "InterestCostsIncurred"),
        (-1, "us-gaap", "InterestCostsCapitalizedAdjustment"),
    )


def test_era_starts_where_the_read_evidence_starts():
    fy0 = date(2025, 12, 31)
    parts = ((1, "us-gaap", "Revenues"),)
    assert dl.era_from_of("same_tag@2020-12-31", parts, fy0) == date(2020, 1, 1)
    assert dl.era_from_of(
        "ERA-CHECK: chosen tag ['2022-12-31', '2025-12-31'] ; others", parts, fy0
    ) == date(2022, 1, 1)
    assert dl.era_from_of("tag covers last 5 FY in companyfacts", parts, fy0) == date(
        2021, 1, 1
    )
    assert dl.era_from_of(
        "api FY coverage | FY-4 10-K same-label tag: SAME_TAG_IN_OLD(accn):us-gaap:Revenues",
        parts,
        fy0,
    ) == date(2021, 1, 1)
    assert dl.era_from_of("sum of components: not era-scanned", parts, fy0) == date(
        2024, 1, 1
    )  # fy1 only


def test_statement_codes_and_served_concepts():
    assert (
        dl.stmt_code(
            "Consolidated Statements of Cas",
            "capex_resolved",
            "cash_flow",
            value_row=True,
        )
        == "CF"
    )
    assert (
        dl.stmt_code("PAR", "dividends_per_share_resolved", "cash_flow", value_row=True)
        == "UN"
    )
    assert (
        dl.stmt_code("", "gross_profit_resolved", "income_statement", value_row=False)
        == "IS"
    )
    names = {
        "revenue",
        "revenue_sanity_resolved",
        "capex",
        "capex_resolved",
        "goodwill",
    }
    assert [dl.served_concept(n, names) for n in ("revenue", "capex", "goodwill")] == [
        "revenue_sanity_resolved",
        "capex_resolved",
        "goodwill",
    ]


def _doc(tags: str, r_page: str = "R3.htm", status: str = "mapped") -> dl.DocmapRow:
    return dl.DocmapRow(
        "T",
        "revenue_sanity_resolved",
        status,
        dl.parse_parts(tags),
        "IS",
        r_page,
        "Revenue",
        date(2021, 1, 1),
        "0000000001-26-000001",
        "",
        "T-docmap.csv",
    )


LIB = {
    "id": 7,
    "decision": "concept",
    "taxonomy": "us-gaap",
    "tag": "Revenues",
    "sign": 1,
    "canonical_concept_id": 1,
    "parent_concept_id": None,
    "components": None,
    "era_from": date(2015, 1, 1),
    "era_to": None,
}


def test_docmap_wins_a_disagreement_only_when_it_cites_a_filing_page():
    ids = {"revenue_sanity_resolved": 1}
    cited = dl.plan_company(
        [LIB],
        [_doc("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")],
        ids,
    )
    assert cited.cut == [(7, date(2020, 12, 31))] and len(cited.insert) == 1
    assert [(c["winner"], c["data_point"]) for c in cited.conflicts] == [
        ("docmap", "revenue_sanity_resolved")
    ]

    uncited = dl.plan_company(
        [LIB],
        [
            _doc(
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax", r_page=""
            )
        ],
        ids,
    )
    assert uncited.cut == [] and uncited.delete == [] and uncited.insert == []
    assert [c["winner"] for c in uncited.conflicts] == ["library"]

    inside = dl.plan_company(
        [{**LIB, "era_from": date(2022, 1, 1)}], [_doc("us-gaap:Other")], ids
    )
    assert (
        inside.delete == [7] and inside.cut == []
    )  # the library row starts inside the docmap era


def test_agreement_writes_nothing_and_lists_nothing():
    plan = dl.plan_company(
        [LIB], [_doc("us-gaap:Revenues")], {"revenue_sanity_resolved": 1}
    )
    assert (plan.agree, plan.insert, plan.conflicts, plan.cut) == (1, [], [], [])


def test_a_library_combined_line_is_never_cut():
    combined = {
        **LIB,
        "decision": "combined",
        "taxonomy": "us-gaap",
        "tag": "X",
        "canonical_concept_id": None,
        "components": ["revenue_sanity_resolved", "other"],
    }
    plan = dl.plan_company(
        [combined], [_doc("us-gaap:Revenues")], {"revenue_sanity_resolved": 1}
    )
    assert (
        plan.insert == []
        and plan.cut == []
        and [c["winner"] for c in plan.conflicts] == ["library"]
    )


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

    rows = [
        (1, date(2019, 1, 1), None),
        (1, date(2015, 1, 1), date(2018, 12, 31)),
        (2, date(2019, 1, 1), None),
        (None, date(2024, 1, 1), None),
    ]
    assert plan.era_shortfall(rows, [date(2018, 12, 31), date(2025, 12, 31)]) == {
        2: date(2018, 12, 31)
    }
    assert (
        plan.era_shortfall(rows, [date(2014, 12, 31), date(2019, 12, 31)]) == {}
    )  # 2014 is outside the window
    gap = [
        (3, date(2015, 1, 1), date(2018, 12, 31)),
        (3, date(2021, 1, 1), None),
    ]  # merged map with a hole
    assert plan.era_shortfall(
        gap, [date(2016, 12, 31), date(2019, 12, 31), date(2022, 12, 31)]
    ) == {3: date(2019, 12, 31)}
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
    assert (
        dl.stmt_code("NOTE", "cash_paid_for_interest", "cash_flow", value_row=True)
        == "UN"
    )


def test_docmap_era_from_2021_leaves_earlier_library_eras_and_period_reasons_intact():
    ids = {"revenue_sanity_resolved": 1}
    early = {**LIB, "id": 1, "era_from": date(2015, 1, 1), "era_to": date(2020, 12, 31)}
    open_row = {
        **LIB,
        "id": 2,
        "tag": "SalesRevenueNet",
        "era_from": date(2015, 1, 1),
        "era_to": None,
    }
    reason = {
        **LIB,
        "id": 3,
        "decision": "not_presented",
        "taxonomy": None,
        "tag": None,
        "era_from": date(2023, 12, 31),
        "era_to": date(2023, 12, 31),
    }
    plan = dl.plan_company(
        [early, open_row, reason],
        [_doc("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")],
        ids,
    )
    assert (
        plan.cut == [(2, date(2020, 12, 31))] and plan.delete == []
    )  # 2015-2020 kept; the period reason kept
    assert len(plan.insert) == 1


def test_a_docmap_reason_never_cuts_a_library_value():
    reason_doc = dl.DocmapRow(
        "T",
        "revenue_sanity_resolved",
        "not_presented",
        (),
        "IS",
        "R3.htm",
        "",
        date(2021, 1, 1),
        "0000000001-26-000001",
        "no line",
        "T-docmap.csv",
    )
    plan = dl.plan_company([LIB], [reason_doc], {"revenue_sanity_resolved": 1})
    assert plan.cut == [] and plan.delete == [] and len(plan.insert) == 1
    assert [c["winner"] for c in plan.conflicts] == ["coexist"]


def test_a_combined_line_replaces_the_library_period_reasons_inside_its_era():
    reason = {
        **LIB,
        "id": 3,
        "decision": "not_in_template",
        "taxonomy": None,
        "tag": None,
        "era_from": date(2024, 12, 31),
        "era_to": date(2024, 12, 31),
    }
    combined = dl.DocmapRow(
        "T",
        "revenue_sanity_resolved",
        "combined",
        dl.parse_parts("us-gaap:X"),
        "IS",
        "R3.htm",
        "Revenue and other",
        date(2024, 1, 1),
        "0000000001-26-000001",
        "",
        "T-docmap.csv",
    )
    plan = dl.plan_company([reason], [combined], {"revenue_sanity_resolved": 1})
    assert (
        plan.delete == [3] and len(plan.insert) == 1
    )  # no overlapping reason rows left behind


def test_member_qualified_tags_are_rejected_row_by_row():
    rows, rejects = _parse(
        "T,cost_of_revenue,component sum,us-gaap:CostOfGoodsAndServicesSold[ProductOrService=Product]+us-gaap:CostOfGoodsAndServicesSold[ProductOrService=Service],IS,R4+R4,x,,FILING-CHECKED,",
        "T,amortization_of_intangibles,component sum,us-gaap:AmortizationOfIntangibleAssets[StatementOfIncomeLocationBalance=us-gaap:OperatingExpenses],IS,R4,x,,FILING-CHECKED,",
        "T,revenue,mapped,us-gaap:Revenues,IS,R4.htm,Revenues,,FILING-CHECKED,",
    )
    assert [r.data_point for r in rows] == ["revenue"]
    assert [(r["data_point"], r["why"]) for r in rejects] == [
        ("cost_of_revenue", "member_not_supported"),
        ("amortization_of_intangibles", "member_not_supported"),
    ]


def test_agreeing_library_row_does_not_lose_the_docmaps_earlier_era():
    ids = {"revenue_sanity_resolved": 1}
    lib = {**LIB, "era_from": date(2025, 6, 30), "era_to": date(2026, 6, 30)}
    plan = dl.plan_company(
        [lib], [_doc("us-gaap:Revenues")], ids
    )  # docmap era from 2021-01-01
    assert plan.agree == 1 and plan.conflicts == []
    assert plan.cut == [
        (7, None)
    ]  # and the library row's closed tail is opened (see the test at the end)
    assert [(d.era_from, d.era_to) for d in plan.insert] == [
        (date(2021, 1, 1), date(2025, 6, 29))
    ]
    (row,) = dl.table_rows(
        plan.insert[0], 5, "0000000001", {"revenue_sanity_resolved": "income_statement"}
    )
    assert (row["era_from"], row["era_to"]) == (date(2021, 1, 1), date(2025, 6, 29))
    # a docmap era that starts with or after the library row adds nothing
    same = dl.plan_company(
        [{**lib, "era_from": date(2021, 1, 1)}], [_doc("us-gaap:Revenues")], ids
    )
    assert same.insert == []


def test_closed_era_with_an_extension_stays_inside_the_end():
    d = dl.replace(
        _doc("us-gaap:Revenues"),
        era_from=date(2018, 1, 1),
        base_era=date(2021, 1, 1),
        ext_note="n",
        era_to=date(2019, 12, 31),
    )
    rows = dl.table_rows(
        d, 5, "0000000001", {"revenue_sanity_resolved": "income_statement"}
    )
    assert [(r["era_from"], r["era_to"], r["rule_id"][-12:]) for r in rows] == [
        (date(2018, 1, 1), date(2019, 12, 31), "era_extend@1")
    ]


def test_every_decided_status_yields_a_row_covering_its_era():
    cs = {"revenue_sanity_resolved": "income_statement"}
    expect = {
        "not_presented": ("not_presented", "docmap_not_presented"),
        "combined": ("not_in_template", "line_presented_combined"),
        "OUT": ("not_in_template", "docmap_out"),
        "mapped": ("concept", None),
        "component_in_note": ("concept", None),
        "component sum": ("component", None),
    }
    for status, (decision, reason_class) in expect.items():
        tags = "us-gaap:Revenues" + (
            "+us-gaap:SalesRevenueNet" if status == "component sum" else ""
        )
        rows = dl.table_rows(_doc(tags, status=status), 5, "0000000001", cs)
        assert rows and {r["decision"] for r in rows} == {decision}, status
        assert all(
            r["era_from"] == date(2021, 1, 1) and r["era_to"] is None for r in rows
        ), status
        assert {r.get("reason_class") for r in rows} == {reason_class}, status


def test_agreeing_library_row_cut_at_the_read_fy_is_opened_to_the_docmaps_open_era():
    # MSFT cash_paid_*: the library row (read_verified) ended at FY2026 (2026-06-30); the docmap reads the same tag
    # through the present. The 2026-09-30 10-Q period stayed uncovered, the tagmap-plan concept gate skipped the
    # concept and FY2015-FY2024 never served.
    ids = {"revenue_sanity_resolved": 1}
    cut = {**LIB, "era_from": date(2025, 6, 30), "era_to": date(2026, 6, 30)}
    plan = dl.plan_company([cut], [_doc("us-gaap:Revenues")], ids)
    assert plan.agree == 1 and plan.cut == [(7, None)]
    # an open library row, or a docmap era that itself ends, is left alone
    assert dl.plan_company([LIB], [_doc("us-gaap:Revenues")], ids).cut == []
    closed = dl.replace(_doc("us-gaap:Revenues"), era_to=date(2025, 6, 30))
    assert dl.plan_company([cut], [closed], ids).cut == []


NOTE_CMP = (
    "era from the FY2017 10-K's comparative year to FY2026: same tag(s) in 10 10-Ks; prior era read in 10-K "
    "0001193125-16-662209 (FY2016): mapped us-gaap:AllocatedShareBasedCompensationExpense R7.htm 'SBC'; "
    "value_source sec_api | accn 0000000001-26-000001 period 2025-07-01..2026-06-30"
)


def _sbc_doc() -> dl.DocmapRow:
    (row,), _ = _parse(
        f'T,sbc,mapped,us-gaap:ShareBasedCompensation,CF,R6.htm,SBC,same_tag@2016-06-30,FILING-CHECKED,"{NOTE_CMP}"'
    )
    return row


def test_comparative_start_keeps_the_prior_tag_through_its_first_year():
    """MSFT sbc: the FY2017 10-K's comparative year (FY2016) is not the year's own filing: the FY2016 10-K and its
    10-Qs print the prior tag, the quarters and Q4 exist only under it. The prior era runs to the FY2016 end."""
    d = _sbc_doc()
    assert d.comparative_start and d.prior_tags == (
        "AllocatedShareBasedCompensationExpense",
    )
    assert d.era_from == date(2015, 7, 1)
    ids = {"sbc": 72}
    alloc = {
        **LIB,
        "id": 9,
        "tag": "AllocatedShareBasedCompensationExpense",
        "canonical_concept_id": 72,
        "era_from": date(2015, 3, 31),
        "era_to": date(2017, 3, 31),
    }
    first = dl.plan_company(
        [alloc], [d], ids
    )  # first load: the library row overlaps the docmap era
    assert first.cut == [(9, date(2016, 6, 30))]
    assert [x.era_from for x in first.insert] == [date(2016, 7, 1)]
    # a reload sees the row this loader cut at the comparative year before: it is opened to the first year's end
    again = dl.plan_company([{**alloc, "era_to": date(2015, 6, 30)}], [d], ids)
    assert again.cut == [(9, date(2016, 6, 30))]
    assert [x.era_from for x in again.insert] == [date(2016, 7, 1)]
    # a library row of another tag than the read's prior tag is never extended
    other = dl.plan_company(
        [{**alloc, "tag": "Other", "era_to": date(2015, 6, 30)}], [d], ids
    )
    assert other.cut == []


def test_comparative_start_without_a_named_prior_tag_changes_nothing():
    (row,), _ = _parse(
        "T,sbc,mapped,us-gaap:ShareBasedCompensation,CF,R6.htm,SBC,same_tag@2016-06-30,FILING-CHECKED,"
        '"era from the FY2017 10-K\'s comparative year to FY2026; value_source sec_api | accn 0000000001-26-000001 period 2025-07-01..2026-06-30"'
    )
    assert not row.comparative_start and row.era_from == date(2015, 7, 1)


def test_instant_component_sum_allowed_for_total_debt_and_multi_class_shares_only():
    from scrooner_pipeline.mapper.company_tag_map_seed import instant_sum_refused

    assert not instant_sum_refused("total_debt", "balance_sheet")
    assert not instant_sum_refused("shares_outstanding_resolved", "balance_sheet")
    assert instant_sum_refused("inventory", "balance_sheet")
    assert not instant_sum_refused("operating_expenses", "income_statement")


def test_era_shortfall_unread_tail_after_reader_fix_is_unchecked_not_short():
    from scrooner_pipeline.mapper import company_tag_map_plan as plan

    fix = plan.FIX_RULE_ID
    full = [
        (1, date(2015, 7, 1), date(2025, 6, 30), fix),
        (1, date(2025, 7, 1), date(2026, 6, 30), fix),  # last reader-fixed FY
        (
            2,
            date(2015, 7, 1),
            date(2026, 6, 30),
            "company_tag_map.docmap@1",
        ),  # not a fix: its shortfall stays
        (
            3,
            date(2015, 7, 1),
            date(2025, 6, 30),
            fix,
        ),  # a fix ends, then a hole inside the read years
        (3, date(2026, 1, 1), date(2026, 6, 30), fix),
    ]
    rows = [r[:3] for r in full]
    ends = [date(2016, 6, 30), date(2025, 12, 31), date(2026, 9, 30)]
    tail = plan.unread_tail_concepts(full)
    assert tail == {1, 3}  # 2 ends at a library row, not a reader fix
    assert plan.era_shortfall(rows, ends) == {
        1: date(2026, 9, 30),
        2: date(2026, 9, 30),
        3: date(2025, 12, 31),
    }
    got = plan.era_shortfall(rows, ends, tail)
    assert (
        1 not in got
    )  # 2026-09-30 is past the last read FY: UNCHECKED unread_period, not a shortfall
    assert got[2] == date(
        2026, 9, 30
    )  # a library row that ends early is still a real shortfall
    assert got[3] == date(2025, 12, 31)  # a hole inside the read years still counts
    open_end = [(1, date(2015, 7, 1), None, fix)]
    assert plan.unread_tail_concepts(open_end) == set()


def test_total_debt_component_sum_keeps_each_part_statement_face_and_note():
    # 'BS+BS+NOTE': face debt lines on BS, the note finance-lease total on UN (audit R06); one stmt = all parts
    tags = "us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiability"

    def mk(stmt):
        return dl.DocmapRow(
            "T",
            "total_debt",
            "component sum",
            dl.parse_parts(tags),
            stmt,
            "R4.htm+R4.htm+R92.htm",
            "",
            date(2021, 1, 1),
            "0000000001-26-000001",
            "",
            "T-docmap.csv",
        )

    cs = {"total_debt": "balance_sheet"}
    rows = dl.table_rows(mk("BS+BS+NOTE"), 5, "0000000001", cs)
    assert [r["stmt"] for r in rows] == ["BS", "BS", "UN"]
    assert {r["stmt"] for r in dl.table_rows(mk("BS"), 5, "0000000001", cs)} == {"BS"}


def test_fix_files_include_versioned_names_and_a_later_version_wins(tmp_path):
    from scrooner_pipeline.mapper.docmap_loader import FIX_FILE_RE, fix_files

    for name in (
        "JNJ-fixes-2026-11-13.csv",
        "JNJ-fixes-v2-2026-11-13.csv",
        "notes.csv",
    ):
        (tmp_path / name).write_text("data_point\n")
    assert [p.name for p in fix_files(tmp_path)] == [
        "JNJ-fixes-2026-11-13.csv",
        "JNJ-fixes-v2-2026-11-13.csv",
    ]
    m = FIX_FILE_RE.match("JNJ-fixes-v2-2026-11-13.csv")
    assert m and m.group(1) == "JNJ" and m.group(2) == "2026-11-13"


def _fix(era_from: date, era_to: date) -> dl.DocmapRow:
    return replace(_doc("us-gaap:OperatingExpenses"), era_from=era_from, era_to=era_to)


def test_fix_eras_close_a_small_gap_between_52_and_53_week_years():
    """JNJ: FY2019 ends 2019-12-29, FY2020 (53 weeks) starts nominally 2020-01-04: no gap days may be left, or a guard
    row on 2019-12-30..31 (month-end rounding) would hold FY2019."""
    fy19 = _fix(date(2018, 12, 31), date(2019, 12, 29))
    fy20 = _fix(date(2020, 1, 4), date(2021, 1, 2))
    out = dl.assign_fix_eras([fy20, fy19])
    assert [(d.era_from, d.era_to) for d in out] == [
        (date(2018, 12, 31), date(2019, 12, 29)),
        (date(2019, 12, 30), date(2021, 1, 2)),
    ]
    far = _fix(date(2020, 3, 1), date(2021, 1, 2))
    assert dl.assign_fix_eras([fy19, far])[1].era_from == date(2020, 3, 1)
    over = _fix(date(2019, 12, 29), date(2021, 1, 2))
    assert dl.assign_fix_eras([fy19, over])[1].era_from == date(2019, 12, 30)


def test_absent_extension_rows_carry_each_years_own_evidence():
    d = dl.replace(
        _doc("", status="not_presented"),
        era_from=date(2018, 1, 1),
        base_era=date(2021, 1, 1),
        ext_note="n",
        ext_slices=(
            (date(2020, 1, 1), date(2020, 12, 31), "A-2020", (("IS", 4),)),
            (date(2019, 1, 1), date(2019, 12, 31), "A-2019", (("IS", 5),)),
            (date(2018, 1, 1), date(2018, 12, 31), "A-2018", (("IS", 6),)),
        ),
    )
    rows = dl.table_rows(
        d, 5, "0000000001", {"revenue_sanity_resolved": "income_statement"}
    )
    ext = [r for r in rows if r["rule_id"].endswith("era_extend@1")]
    assert [
        (r["era_from"].year, r["evidence_adsh"], r["evidence_report"]) for r in ext
    ] == [
        (2020, "A-2020", 4),
        (2019, "A-2019", 5),
        (2018, "A-2018", 6),
    ]
    main = [r for r in rows if not r["rule_id"].endswith("era_extend@1")]
    assert [r["evidence_adsh"] for r in main] == ["0000000001-26-000001"]
