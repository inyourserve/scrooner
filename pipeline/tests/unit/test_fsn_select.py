"""G1 fixtures for fsn_select (FSN-STORE-DESIGN-2026-11-01 §7 step 3): real FSN rows extracted
from the fsn-notes bucket into tests/fixtures/fsn_select/ (Teleflex, KO, AMZN, GE)."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from scrooner_pipeline.fsn_store import select as sel

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "fsn_select"
M = Decimal(1_000_000)


def _case(name: str, concept_tags: dict[str, str], *, drop=lambda v: False):
    """Fixture -> select_concept inputs, the way load_company assembles them from the store.
    concept_tags: tag -> concept for the lines the test maps (status 'mapped')."""
    d = json.loads((FIXTURES / f"{name}.json").read_text())
    ids = {f["accession"]: i for i, f in enumerate(d["filings"], start=1)}
    filings = {
        ids[f["accession"]]: sel.Filing(
            ids[f["accession"]],
            f["accession"],
            datetime.fromisoformat(f["accepted"]),
            f["form"],
            date.fromisoformat(f["period"]),
            f["fy"],
            f["fp"],
        )
        for f in d["filings"]
    }
    tag_ids = {t: i for i, t in enumerate(sorted({v["tag"] for v in d["values"]}), start=1)}
    lines = [ln for ln in d["lines"] if not ln["inpth"]]
    mapped = [
        (ids[ln["accession"]], ln["stmt"], tag_ids[ln["tag"]], ln["tag"], concept_tags[ln["tag"]])
        for ln in lines
        if ln["tag"] in concept_tags and ln["tag"] in tag_ids
    ]
    anchors = {t for ts in sel.ANCHOR_TAGS.values() for t in ts}
    on_line: dict[tuple[int, str], set[str]] = {}  # a tag can sit on two statements (NI on IS and CF)
    for ln in lines:
        on_line.setdefault((ids[ln["accession"]], ln["tag"]), set()).add(ln["stmt"])
    vals = [v for v in d["values"] if v["iprx"] == 0 and not drop(v)]
    anchor_prints = {
        (ids[v["accession"]], stmt, date.fromisoformat(v["ddate"]), v["qtrs"])
        for v in vals
        if v["tag"] in anchors and v["dimh"] == "0x00000000" and v["coreg"] == ""
        for stmt in on_line.get((ids[v["accession"]], v["tag"]), ())
    }
    values = [
        (
            n,
            ids[v["accession"]],
            tag_ids[v["tag"]],
            date.fromisoformat(v["ddate"]),
            v["qtrs"],
            v["uom"],
            v["value"],
            v["dcml"],
            0 if v["dimh"] == "0x00000000" else 1,
            v["coreg"],
        )
        for n, v in enumerate(vals, start=1)
        if v["tag"] in concept_tags
    ]
    data = sel.build(filings, mapped, sel.face_columns(filings, anchor_prints), values, set())
    return data, filings, ids


def _cells(data, concept, **kw):
    return {
        (c.ddate, c.qtrs): c
        for c in sel.select_concept(
            concept, data["prints"][concept], data["filings"], members=data["members"], **kw
        )
    }


REV = {"RevenueFromContractWithCustomerExcludingAssessedTax": "revenue_sanity_resolved"}


@pytest.mark.unit
def test_teleflex_q4_2025_is_the_note_quarter_never_fy_minus_a_pre_recast_9m():
    data, filings, ids = _case("teleflex", REV)
    cells = _cells(data, "revenue_sanity_resolved", residual_guard=True)
    q4 = cells[(date(2025, 12, 31), 1)]
    assert (q4.state, q4.value, q4.rule_id) == ("value", Decimal("568984000"), sel.RULE_NOTE_Q)
    assert filings[q4.filing_id].accession == "0000096943-26-000019"
    # FY2024 served from the latest (recast) print, its Q4 from the same 10-K's note
    assert cells[(date(2024, 12, 31), 4)].value == Decimal("1699546000")
    assert cells[(date(2024, 12, 31), 1)].value == Decimal("442010000")
    assert all(c.value is None or c.value >= 0 for c in cells.values())


@pytest.mark.unit
def test_teleflex_without_the_note_the_recast_10k_blocks_fy_minus_9m():
    # mutation of the input: drop the 10-K's quarterly note. FY − 9M = −401.9M must not appear.
    data, filings, ids = _case(
        "teleflex",
        REV,
        drop=lambda v: v["accession"] == "0000096943-26-000019" and v["qtrs"] == 1,
    )
    q4 = _cells(data, "revenue_sanity_resolved", residual_guard=True)[(date(2025, 12, 31), 1)]
    assert (q4.state, q4.reason_code, q4.value) == ("defect", "mixed_vintage_inputs", None)


@pytest.mark.unit
def test_mixed_vintage_keys_are_blocked_or_equal_to_a_same_basis_difference():
    # property over every derived quarter of the fixtures: its two inputs are SAME_BASIS
    for name, tags in (("teleflex", REV), ("ge", {"Revenues": "revenue_sanity_resolved"})):
        data, filings, _ = _case(name, tags)
        concept = "revenue_sanity_resolved"
        s = sel._Series([p for p in data["prints"][concept] if p.uom == "USD"], filings)
        for c in _cells(data, concept).values():
            if c.state == "derived":
                b, a = c.source_value_ids
                pa = next(p for p in data["prints"][concept] if p.value_id == a)
                pb = next(p for p in data["prints"][concept] if p.value_id == b)
                assert s.same_basis(pa.filing_id, pb.filing_id) is None
                assert c.value == pb.value - pa.value


@pytest.mark.unit
def test_ko_q1_2015_binds_by_fiscal_label_not_the_rounded_fsn_date():
    data, filings, _ = _case("ko", {"SalesRevenueGoodsNet": "revenue_sanity_resolved"})
    cells = _cells(data, "revenue_sanity_resolved")
    q1 = cells[(date(2015, 3, 31), 1)]
    row = sel.to_row(q1, 7, filings)
    assert row["value"] == "10711000000"
    assert (row["fiscal_year"], row["fiscal_period"], row["fsn_end"]) == (2015, "Q1", "2015-03-31")
    assert (row["period_start"], row["period_end"]) == (None, None)  # the loader binds to 2015-04-03
    # the comparative column binds one year back through the same filing's label
    assert sel.fiscal_label(date(2014, 3, 31), 1, filings.values()) == (2014, "Q1")
    assert row["source_value_ids"] == q1.source_value_ids and len(q1.source_value_ids) == 1


@pytest.mark.unit
def test_amzn_combined_lease_line_is_never_served_as_debt():
    # LeaseLiabilityNoncurrent (77,297M = operating 67,220 + finance 10,077) is a combined line:
    # line_map status 'combined', so it is not among the mapped lines select reads
    data, _, _ = _case("amzn", {"LongTermDebtNoncurrent": "total_debt_resolved"})
    cells = _cells(data, "total_debt_resolved")
    assert cells[(date(2023, 12, 31), 0)].value == Decimal("58314") * M
    assert all(c.value != Decimal("77297") * M for c in cells.values())


@pytest.mark.unit
def test_ge_gecc_double_context_never_becomes_a_consolidated_quarter():
    data, filings, _ = _case("ge", {"Revenues": "revenue_sanity_resolved"})
    cells = _cells(data, "revenue_sanity_resolved", residual_guard=True)
    gecc = {Decimal(x) * M for x in ("2885", "2771", "2600", "2649")}
    assert all(c.value not in gecc for c in cells.values())
    # the 10-K's undimensioned quarterly rows are GECC member duplicates: not used as note quarters
    q4 = cells[(date(2016, 12, 31), 1)]
    assert q4.rule_id != sel.RULE_NOTE_Q
    assert q4.state == "derived" or q4.reason_code in ("mixed_vintage_inputs", "no_basis_witness")
    assert cells[(date(2016, 12, 31), 4)].value == Decimal("123693") * M


@pytest.mark.unit
def test_same_basis_needs_a_witness_and_no_break_between():
    f = {
        i: sel.Filing(i, f"a{i}", datetime(2025, i, 1), "10-Q", date(2025, 3 * i, 28), 2025, f"Q{i}")
        for i in (1, 2, 3)
    }

    def p(vid, fid, d, q, v):
        return sel.Print(vid, fid, "T", d, q, "USD", Decimal(v), 0, "IS", True)

    d1, d0 = date(2025, 3, 31), date(2024, 3, 31)
    prints = [p(1, 1, d1, 1, 10), p(2, 2, d1, 1, 10), p(3, 3, d1, 1, 12), p(4, 1, d0, 1, 5)]
    s = sel._Series(prints, f)
    assert s.breaks == {3} and s.witness == {2, 3}
    assert s.same_basis(1, 1) is None
    assert s.same_basis(1, 2) is None
    assert s.same_basis(1, 3) == "mixed_vintage_inputs"
    assert s.same_basis(2, 1) is None  # order-free
    s2 = sel._Series([p(1, 1, d1, 1, 10), p(2, 2, d0, 1, 5)], f)
    assert s2.same_basis(1, 2) == "no_basis_witness"


@pytest.mark.unit
def test_ge_member_duplicate_alone_rejects_a_note_quarter():
    # with one note quarter removed the four-quarter sum cannot run: only the member guard
    # keeps GECC's undimensioned Q4 (2,649M = the SubsidiariesGecc member value) out
    data, _, _ = _case(
        "ge",
        {"Revenues": "revenue_sanity_resolved"},
        drop=lambda v: v["accession"] == "0000040545-17-000010"
        and v["qtrs"] == 1
        and v["ddate"] == "2016-03-31"
        and v["dimh"] == "0x00000000",
    )
    q4 = _cells(data, "revenue_sanity_resolved")[(date(2016, 12, 31), 1)]
    assert q4.rule_id != sel.RULE_NOTE_Q and q4.value != Decimal("2649") * M


@pytest.mark.unit
def test_fiscal_label_follows_the_year_end_not_fsn_sub_fy():
    # WMT: FSN sub.fy calls the year ending 2015-01-31 fiscal 2014; core.period calls it 2015
    def f(i, period, fy, fp, fye):
        return sel.Filing(i, f"a{i}", datetime(2015, 3, i), "10-K", period, fy, fp, fye)

    wmt = [f(1, date(2015, 1, 31), 2014, "FY", "0131")]
    assert sel.fiscal_label(date(2015, 1, 31), 4, wmt) == (2015, "FY")
    assert sel.fiscal_label(date(2015, 1, 31), 1, wmt) == (2015, "Q4")
    assert sel.fiscal_label(date(2014, 10, 31), 1, wmt) == (2015, "Q3")
    assert sel.fiscal_label(date(2014, 4, 30), 1, wmt) == (2015, "Q1")
    assert sel.fiscal_label(date(2014, 7, 31), 0, wmt) == (2015, "Q2")
    # HD ends near Feb 1 (fye 0201 rounds to January), JNJ near Jan 3 (rounds to December)
    hd = [f(1, date(2015, 1, 31), 2014, "FY", "0201")]
    assert sel.fiscal_label(date(2015, 1, 31), 4, hd) == (2015, "FY")
    jnj = [f(1, date(2015, 12, 31), 2015, "FY", "0103")]
    assert sel.fiscal_label(date(2015, 12, 31), 4, jnj) == (2015, "FY")
    assert sel.fiscal_label(date(2015, 6, 30), 1, jnj) == (2015, "Q2")


@pytest.mark.unit
def test_eps_prints_filed_as_usd_are_selected_and_never_derived():
    # FSN files EarningsPerShareBasic with uom "USD"; filtering by "USD/shares" dropped every print
    f = {1: sel.Filing(1, "a1", datetime(2025, 5, 1), "10-Q", date(2025, 3, 31), 2025, "Q1")}
    p = sel.Print(1, 1, "EarningsPerShareBasic", date(2025, 3, 31), 1, "USD", Decimal("1.23"), 2, "IS", True)
    cells = sel.select_concept("basic_eps_resolved", [p], f, unit=sel.FSN_UOM["USD/shares"], derive=False)
    assert [(c.state, c.value) for c in cells] == [("value", Decimal("1.23"))]
    assert sel.to_row(cells[0], 1, f, unit="USD/shares")["unit"] == "USD/shares"


@pytest.mark.unit
def test_period_rules_split_basis_and_unfiled_instant():
    split = [{"kind": "basis_split", "date": "2025-08-06", "reason_code": "predecessor_successor_split", "note": "PSKY"}]
    cells = [
        sel.Cell("revenue_sanity_resolved", date(2025, 12, 31), 4, "value", Decimal(10)),  # FY2025 spans it
        sel.Cell("revenue_sanity_resolved", date(2025, 9, 30), 1, "derived", Decimal(3)),  # Q3 2025 spans it
        sel.Cell("revenue_sanity_resolved", date(2025, 6, 30), 1, "value", Decimal(2)),  # before: kept
        sel.Cell("revenue_sanity_resolved", date(2025, 12, 31), 1, "value", Decimal(4)),  # Q4 after: kept
    ]
    out = {(c.ddate, c.qtrs): c for c in sel.apply_period_rules("revenue_sanity_resolved", cells, split, instant=False)}
    assert out[(date(2025, 12, 31), 4)].reason_code == "predecessor_successor_split"
    assert out[(date(2025, 9, 30), 1)].reason_code == "predecessor_successor_split"
    assert out[(date(2025, 6, 30), 1)].state == "value" and out[(date(2025, 12, 31), 1)].state == "value"
    unfiled = [{"kind": "unfiled_instant", "date": "2021-09-30", "reason_code": "balance_sheet_not_filed", "note": "AHR"}]
    got = sel.apply_period_rules("total_assets_resolved", [], unfiled, instant=True)
    assert [(c.ddate, c.qtrs, c.reason_code) for c in got] == [(date(2021, 9, 30), 0, "balance_sheet_not_filed")]
    row = sel.to_row(got[0], 3885, {})
    assert row["defect_class"] == "filer_error" and row["reason_text"]


@pytest.mark.unit
def test_eps_q4_is_a_reasoned_blank_never_a_derived_value():
    f = {
        1: sel.Filing(1, "a1", datetime(2025, 10, 30), "10-Q", date(2025, 9, 30), 2025, "Q3"),
        2: sel.Filing(2, "a2", datetime(2026, 2, 1), "10-K", date(2025, 12, 31), 2025, "FY"),
    }
    ps = [
        sel.Print(1, 1, "EarningsPerShareBasic", date(2025, 9, 30), 3, "USD", Decimal("4.10"), 2, "IS", True),
        sel.Print(2, 2, "EarningsPerShareBasic", date(2025, 12, 31), 4, "USD", Decimal("5.60"), 2, "IS", True),
    ]
    q4 = {(c.ddate, c.qtrs): c for c in sel.select_concept("basic_eps_resolved", ps, f, derive=False)}[(date(2025, 12, 31), 1)]
    assert (q4.state, q4.value, q4.reason_code) == ("not_presented", None, "not_filed_separately")
    row = sel.to_row(q4, 1, f, unit="USD/shares")
    assert row["state"] == "not_presented" and row["reason_text"] and "defect_class" not in row


@pytest.mark.unit
def test_note_values_fill_only_missing_keys_with_guards():
    f = {
        1: sel.Filing(1, "a1", datetime(2024, 2, 1), "10-K", date(2023, 12, 31), 2023, "FY"),
        2: sel.Filing(2, "a2", datetime(2025, 2, 1), "10-K", date(2024, 12, 31), 2024, "FY"),
    }

    def n(vid, fid, tag, d, q, v):
        return sel.NoteFact(vid, fid, tag, d, q, Decimal(v), -6)

    d23, d24 = date(2023, 12, 31), date(2024, 12, 31)
    facts = [
        n(1, 1, "InterestExpense", d23, 4, "1968000000"),          # FY2023 printed in its 10-K
        n(2, 2, "InterestExpense", d23, 4, "1968000000"),          # reprinted later: latest wins
        n(3, 2, "InterestExpenseNonoperating", d24, 4, "2935000000"),  # only the lower-priority tag
        n(4, 2, "InterestExpense", date(2024, 6, 30), 1, "0"),     # capitalised (TOL): a printed zero is served
        n(5, 2, "InterestExpense", date(2024, 9, 30), 1, "107000000"),
        n(6, 2, "InterestExpenseOperating", date(2024, 9, 30), 1, "55000000"),  # two perimeters (IP)
        n(7, 2, "InterestExpense", date(2024, 3, 31), 1, "500000000"),  # face cell exists: skipped
    ]
    cells = {(c.ddate, c.qtrs): c for c in sel.select_note_values(
        "interest_expense_resolved", facts, f, taken={(date(2024, 3, 31), 1)})}
    assert cells[(d23, 4)].value == Decimal("1968000000") and cells[(d23, 4)].source_value_ids == [2]
    assert cells[(d23, 4)].rule_id == sel.RULE_NOTE_VALUE and cells[(d23, 4)].input_refs["source"] == "note"
    assert cells[(d24, 4)].tag == "InterestExpenseNonoperating"
    assert (cells[(date(2024, 6, 30), 1)].state, cells[(date(2024, 6, 30), 1)].value) == ("value", Decimal(0))  # printed zero
    assert cells[(date(2024, 9, 30), 1)].reason_code == "note_values_disagree"
    assert (date(2024, 3, 31), 1) not in cells
    assert sel.to_row(cells[(date(2024, 9, 30), 1)], 1, f)["defect_class"] == "composition"


@pytest.mark.unit
def test_sole_debt_interest_counts_only_when_it_is_the_filings_only_interest_line():
    f = {
        1: sel.Filing(1, "a1", datetime(2025, 2, 1), "10-K", date(2024, 12, 31), 2024, "FY"),
        2: sel.Filing(2, "a2", datetime(2025, 3, 1), "10-K", date(2024, 9, 30), 2024, "FY"),
        3: sel.Filing(3, "a3", datetime(2025, 4, 1), "10-K", date(2023, 12, 31), 2023, "FY"),
    }

    def n(vid, fid, tag, d, v, label=None):
        return sel.NoteFact(vid, fid, tag, d, 4, Decimal(v), -6, label)

    d1, d2, d3 = date(2024, 12, 31), date(2024, 9, 30), date(2023, 12, 31)
    facts = [
        n(1, 1, "InterestExpenseDebt", d1, "378000000"),                 # PGR/CVX pattern: only line
        n(2, 2, "InterestExpenseDebt", d2, "111000000"),                 # beside another interest tag:
        n(3, 2, "InterestExpenseOther", d2, "9000000"),                  #   a component, never taken
        n(4, 3, "InterestExpenseDebt", d3, "50000000", "Debt issuance costs"),  # face label not interest
    ]
    cells = {c.ddate: c for c in sel.select_note_values(
        "interest_expense_resolved", facts, f, taken=set(), sole_debt=True)}
    assert cells[d1].value == Decimal("378000000") and cells[d1].input_refs["sole_debt"]
    assert cells[d1].input_refs["label_unverified"] is True
    assert d2 not in cells
    assert cells[d3].reason_code == "sole_debt_label_not_interest"
    # without the PENDING rule Debt is never a gross figure
    assert sel.select_note_values("interest_expense_resolved", facts, f, taken=set()) == []


@pytest.mark.unit
def test_note_path_never_takes_operating_income_and_holds_negative_interest():
    f = {1: sel.Filing(1, "0001744489-25-000155", datetime(2025, 11, 13), "10-K", date(2025, 9, 30), 2025, "FY")}
    d = date(2025, 9, 30)
    # MOG-A pattern: a non-dimensional OperatingIncomeLoss equal to the sum of segment members, off the face
    oi = [sel.NoteFact(1, 1, "OperatingIncomeLoss", d, 4, Decimal("538000000"), -6)]
    assert sel.select_note_values("operating_income_resolved", oi, f, taken=set()) == []
    neg = [sel.NoteFact(2, 1, "InterestExpense", d, 4, Decimal("-1812000000"), -6)]
    held = sel.select_note_values("interest_expense_resolved", neg, f, taken=set())
    assert [c.reason_code for c in held] == ["sign_inconsistent"]
    # DIS FY2025 cleared at +1,812M, only while the stored value is the pinned one
    pin = {("0001744489-25-000155", d, 4): (Decimal("-1812000000"), Decimal("1812000000"))}
    ok = sel.select_note_values("interest_expense_resolved", neg, f, taken=set(), cleared=pin)
    assert [(c.state, c.value) for c in ok] == [("value", Decimal("1812000000"))]
    moved = [sel.NoteFact(2, 1, "InterestExpense", d, 4, Decimal("-1900000000"), -6)]
    assert sel.select_note_values("interest_expense_resolved", moved, f, taken=set(), cleared=pin)[0].reason_code == "sign_inconsistent"
    debt = [sel.NoteFact(3, 1, "InterestExpenseDebt", d, 4, Decimal("378000000"), -6)]
    c = sel.select_note_values("interest_expense_resolved", debt, f, taken=set(), sole_debt=True, label_verified=True)[0]
    assert c.input_refs["label_unverified"] is False
