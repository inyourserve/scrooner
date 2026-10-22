"""NA-9 structural revenue pick on the FILING-CHECKED rows of data-team/37 section 2
(values in $M; row order is the income-statement presentation order)."""

from __future__ import annotations

from decimal import Decimal as D

from scrooner_pipeline.mapper import revenue_structure_total as s

RCFC = "RevenueFromContractWithCustomerExcludingAssessedTax"


def row(order, tag, kind, value, tax="us-gaap", tol="0", members=()):
    return s.IsRow(
        order,
        tax,
        tag,
        kind,
        None if value is None else D(str(value)),
        D(tol),
        tuple(D(str(m)) for m in members),
    )


def exp(order):
    return row(order, "CostOfRevenue", "expense_line", 1)


def pick(rows, arcs=(), **kw):
    return s.select_structural_total(rows, list(arcs), **kw)


def test_ge_fy2018_total_revenues_not_sales_component():
    # 0000040545-19-000014 R2: Sales 113,543 + GE Capital revenues 8,072 = Total revenues 121,615
    rows = [
        row(1, RCFC, "revenue_line", 113543),
        row(2, "ge:GECapitalServices", "revenue_line", 8072, tax="ge"),
        row(3, "Revenues", "revenue_line", 121615),
        exp(4),
    ]
    r = pick(rows)
    assert isinstance(r, s.StructuralPick) and (r.tag, r.value) == (
        "Revenues",
        D(121615),
    )
    assert r.proof == "P1+presentation_siblings" and not r.single_line


def test_oge_fy2018_presentation_siblings_without_calc_children():
    # 0001021635-19-000015 R2: 2,211.7 + 58.6 = 2,270.3
    rows = [
        row(1, RCFC, "revenue_line", "2211.7", tol="0.05"),
        row(2, "oge:AltRev", "revenue_line", "58.6", tax="oge", tol="0.05"),
        row(3, "Revenues", "revenue_line", "2270.3", tol="0.05"),
        exp(4),
    ]
    assert pick(rows).tag == "Revenues"


def test_sna_fy2025_face_dimension_members_prove_the_total():
    # 0000091440-26-000045 R3: members 4,743.2 + 412.9 = 5,156.1, label "Net sales"
    rows = [
        row(
            1,
            "Revenues",
            "revenue_line",
            "5156.1",
            members=("4743.2", "412.9"),
            tol="0.1",
        ),
        exp(2),
    ]
    r = pick(rows)
    assert (r.tag, r.proof) == ("Revenues", "P1+face_members")


def test_single_line_statements_ema_ntap_flagged_single_line():
    # EMR 0000032604-24-000041 R3 net sales 13,804; NTAP 0001193125-26-259683 R4 6,925: only revenue row,
    # calc child of a profit subtotal. The note facts (Revenues 1,660 / 6,237) are not statement rows.
    for tag, value in (("EMR", 13804), ("NTAP", 6925)):
        rows = [row(1, RCFC, "revenue_line", value), exp(2)]
        r = pick(rows, [s.CalcArc("OperatingIncomeLoss", RCFC, 1)])
        assert (r.tag, r.value, r.single_line) == (RCFC, D(value), True), tag


def test_ma_face_total_is_revenues_net_revenue():
    # 0001141391-22-000023 R3: single face row "Net revenue" 18,884 (Revenues); 29,845 gross is a note value
    rows = [row(1, "Revenues", "revenue_line", 18884), exp(2)]
    r = pick(rows, [s.CalcArc("OperatingIncomeLoss", "Revenues", 1)])
    assert (r.tag, r.value) == ("Revenues", D(18884))


def test_single_row_without_subtotal_arc_or_identity_is_blank_not_guessed():
    rows = [row(1, "Revenues", "revenue_line", 100), exp(2)]
    assert pick(rows) == s.Blank("revenue_total_undecidable.identity_failed")


def test_identity_failure_is_blank():
    rows = [
        row(1, RCFC, "revenue_line", 100),
        row(2, "Revenues", "revenue_line", 250),
        exp(3),
    ]
    assert pick(rows) == s.Blank("revenue_total_undecidable.identity_failed")


def test_custom_tag_total_is_not_selected():
    rows = [row(1, "x:Total", "revenue_line", 100, tax="x"), exp(2)]
    assert pick(rows) == s.Blank(
        "revenue_total_undecidable.total_line_not_tagged_standard"
    )


def test_two_independent_totals_are_blank_never_largest():
    # SYNTHETIC shape: two section rows each proven by their own calc children, neither a component
    # of the other
    arcs = [s.CalcArc(RCFC, "a", 1), s.CalcArc("Revenues", "b", 1)]
    rows = [
        row(1, "a", "revenue_line", 100),
        row(2, RCFC, "revenue_line", 100),
        row(3, "b", "revenue_line", 60),
        row(4, "Revenues", "revenue_line", 60),
        exp(5),
    ]
    assert pick(rows, arcs) == s.Blank("revenue_total_undecidable.two_totals")


def test_bank_template_and_empty_statement():
    assert pick(
        [row(1, "Revenues", "revenue_line", 1), exp(2)], is_bank=True
    ).reason.endswith("bank_template")
    assert pick([exp(1)]).reason.endswith("no_statement_located")


def test_zero_component_with_a_total_that_does_not_equal_the_sum_is_blank():
    # SYNTHETIC. The real OGE FY2017 column (0001021635-19-000015 R2: RCFC 0.0 beside the other
    # revenue rows, expected Revenues 2,261.1 selected) is Verifier case 30 and needs the real rows.
    rows = [
        row(1, RCFC, "revenue_line", "0.0"),
        row(2, "Revenues", "revenue_line", "2261.1"),
        exp(3),
    ]
    assert pick(rows) == s.Blank("revenue_total_undecidable.identity_failed")
