"""Page gate (Ritwik, PM final draw 2026-11-14): every PROVEN/REASON/DERIVED cell cites a page of its filing."""


def test_reason_with_note_statement_cites_the_filings_income_statement():
    """Live shape (PM amortization FY2022): the reason's docmap stmt is NOTE, that filing's IS is R3."""
    from scrooner_pipeline.mapper.top100_coverage import (
        LocatorIndex,
        statement_page_fallback,
    )

    A = "0001413329-23-000025"
    i = LocatorIndex()
    i.add(A, 3, 1, "IS", "Revenues", "x")
    i.add(A, 6, 1, "BS", "Assets", "x")
    for stmt in ("NOTE", "UN"):
        assert statement_page_fallback(A, stmt, False, i) == (
            "R3.htm",
            "evidence_acc_stmt_page",
        )
        assert statement_page_fallback(A, stmt, True, i) == (
            "R6.htm",
            "evidence_acc_stmt_page",
        )


def test_reason_whose_main_statement_is_not_a_report_of_the_filing_cites_its_income_statement():
    """META dividends_per_share (stmt EQ, no EQ report in the filing): the IS shows the absence."""
    from scrooner_pipeline.mapper.top100_coverage import (
        LocatorIndex,
        statement_page_fallback,
    )

    A = "0001326801-16-000043"
    i = LocatorIndex()
    i.add(A, 4, 1, "IS", "Revenues", "x")
    i.add(A, 2, 1, "BS", "Assets", "x")
    assert statement_page_fallback(A, "EQ", False, i) == (
        "R4.htm",
        "evidence_acc_stmt_page",
    )
    assert statement_page_fallback(A, "EQ", True, i) == (
        "R2.htm",
        "evidence_acc_stmt_page",
    )
    # META dividends_per_share has docmap stmt PAR: a duration cell, shown on the income statement
    assert statement_page_fallback(A, "PAR", False, i) == (
        "R4.htm",
        "evidence_acc_stmt_page",
    )


def test_proven_note_fact_page_comes_from_the_note_lookup_of_that_filing():
    from scrooner_pipeline.mapper.top100_coverage import LocatorIndex, proven_locator

    A = "0001413329-25-000013"
    i = LocatorIndex()
    i.add(
        A, 3, 5, "IS", "InterestIncomeExpenseNonoperatingNet", "Interest expense, net"
    )
    tag = "InterestExpenseNonoperating"
    assert proven_locator(A, "IS", None, tag, i, {(A, tag): 116}) == (
        A,
        "R116.htm",
        "note_report_from_pre",
    )
    # not in the lookup: the page stays blank (never the income statement)
    assert proven_locator(A, "IS", None, tag, i, {})[1] == ""


def test_committed_lookup_has_pm_interest_expense_note_page():
    from scrooner_pipeline.mapper.note_report_lookup import load_lookup

    assert (
        load_lookup().get(("0001413329-25-000013", "InterestExpenseNonoperating"))
        == 116
    )


def test_pageless_counts_per_company():
    from scrooner_pipeline.mapper.top100_coverage import pageless_counts

    rows = [
        {"company_id": 1, "class": "PROVEN", "r_page": "", "_parts_blank": 2},
        {"company_id": 1, "class": "PROVEN", "r_page": "R3.htm"},
        {"company_id": 1, "class": "REASON", "r_page": ""},
        {"company_id": 1, "class": "DERIVED", "r_page": ""},
        {"company_id": 1, "class": "UNCHECKED", "r_page": ""},
        {"company_id": 2, "class": "PROVEN", "r_page": "R4.htm"},
    ]
    p = pageless_counts(rows)
    assert p[1] == {
        "pageless_proven": 1,
        "pageless_reason": 1,
        "pageless_derived": 1,
        "parts_blank": 2,
    }
    assert p[2] == dict.fromkeys(p[1], 0)
