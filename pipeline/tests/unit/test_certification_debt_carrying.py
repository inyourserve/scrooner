"""Gating certify check debt_not_carrying_lines (I8): stored total debt vs the balance-sheet carrying
lines. Real cases: AAPL 10-Q Q3 FY26 (stored 84,297 vs 84,344), GOOG FY2025 (49,085 vs 48,543), AMZN FY2025
(69,291 vs 68,851); CVX FY2016 is undecidable. The suite missed AAPL and GOOG before this rule."""

from datetime import date

import pytest
from certification_fixtures import D, add, clean_company, fact

from scrooner_pipeline.certification import composition
from scrooner_pipeline.certification.model import REVIEW, WRONG_VALUE


def company(stored, tags, end=date(2026, 6, 27)):
    d = clean_company()
    add(d, "total_debt_resolved", stored, end, None, "FY", tag="LongTermDebt")
    d.carrying_facts += [fact(t, v, None, end) for t, v in tags.items()]
    return d


def found(d, rule):
    return [f for f in composition.check(d) if f.evidence["rule"] == rule]


M = 1_000_000
AAPL = dict(
    CommercialPaper=1997 * M,
    LongTermDebt=82300 * M,
    LongTermDebtCurrent=11007 * M,
    LongTermDebtNoncurrent=71340 * M,
)
GOOG = dict(
    CommercialPaper=0,
    LongTermDebt=49085 * M,
    LongTermDebtCurrent=1996 * M,
    LongTermDebtNoncurrent=46547 * M,
)
AMZN = dict(
    LongTermDebt=68836 * M,
    ShortTermBorrowings=455 * M,
    LongTermDebtCurrent=2748 * M,
    LongTermDebtNoncurrent=65648 * M,
)
CVX = dict(CommercialPaper=10410 * M, ShortTermBorrowings=10840 * M, LongTermDebtCurrent=6253 * M,
           LongTermDebtNoncurrent=35193 * M, DebtCurrent=19840 * M)  # fmt: skip


@pytest.mark.parametrize(
    ("stored", "tags", "want"),
    [
        (84297 * M, AAPL, 84344 * M),
        (49085 * M, GOOG, 48543 * M),
        (69291 * M, AMZN, 68851 * M),
    ],
    ids=["AAPL", "GOOG", "AMZN"],
)
def test_the_pilot_errors_are_gating_wrong_values(stored, tags, want):
    f = found(company(stored, tags), "debt_not_carrying_lines")
    assert len(f) == 1 and f[0].severity == WRONG_VALUE
    assert f[0].expected_or_other_value == D(want)


@pytest.mark.parametrize(
    ("tags", "want"),
    [(AAPL, 84344 * M), (GOOG, 48543 * M), (AMZN, 68851 * M)],
    ids=["AAPL", "GOOG", "AMZN"],
)
def test_repaired_value_is_clean(tags, want):
    assert found(company(want, tags), "debt_not_carrying_lines") == []


def test_cvx_stored_value_is_a_review_not_a_wrong_value():
    f = found(
        company(43330 * M, CVX, end=date(2016, 12, 31)),
        "debt_carrying_lines_undecidable",
    )
    assert len(f) == 1 and f[0].severity == REVIEW
    assert (
        found(
            company(43330 * M, CVX, end=date(2016, 12, 31)), "debt_not_carrying_lines"
        )
        == []
    )


def test_no_carrying_lines_no_finding():
    assert (
        found(company(5 * M, dict(LongTermDebt=5 * M)), "debt_not_carrying_lines") == []
    )


def test_one_dollar_rounding_is_not_a_finding():
    assert found(company(84344 * M + 1, AAPL), "debt_not_carrying_lines") == []
