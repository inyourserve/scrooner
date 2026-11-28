"""Rule absent_part_renamed (component_sum_authority v3, 2026-11-29): a part absent from a filing's column is no zero when
the column prints the line under another component tag of the same concept (IBM total_debt Dec-2019: the Q3-2020 10-Q
prints long-term debt as LongTermDebtNoncurrent). Pure; mutation-checked (fails with renamed_part_printed returning False)."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.proof import shown as sh

D = Decimal
END = date(2019, 12, 31)
OWN = {"ShortTermBorrowings", "LongTermDebtAndCapitalLeaseObligations"}
NAME = "total_debt_resolved"
ROWS = [
    (1, "component", "BS", "LongTermDebtAndCapitalLeaseObligations", None, NAME, 1, date(2019, 1, 1), date(2021, 12, 31), "x"),
    (2, "component", "BS", "ShortTermBorrowings", None, NAME, 1, date(2019, 1, 1), None, "x"),
    (3, "component", "BS", "LongTermDebtNoncurrent", None, NAME, 1, date(2022, 1, 1), None, "x"),
]


class _Face:
    def __init__(self, printed: set[tuple[str, str]]):
        self.printed = printed

    def prints_column(self, acc, tag, start, end, ptype):
        return (acc, tag) in self.printed


@pytest.mark.unit
def test_renamed_line_printed_vetoes_the_zero():
    face = _Face({("Q3", "ShortTermBorrowings"), ("Q3", "LongTermDebtNoncurrent")})
    assert sh.renamed_part_printed(face, ROWS, NAME, OWN, "Q3", END, END, "instant") is True


@pytest.mark.unit
def test_a_truly_absent_part_stays_zero_eligible():
    face = _Face({("K", "ShortTermBorrowings")})
    assert sh.renamed_part_printed(face, ROWS, NAME, OWN, "K", END, END, "instant") is False


@pytest.mark.unit
def test_complete_filing_wins_over_the_renamed_later_filing():
    copies = [
        ("K", D("1000"), "LongTermDebtAndCapitalLeaseObligations"),
        ("K", D("200"), "ShortTermBorrowings"),
        ("Q3", D("200"), "ShortTermBorrowings"),
    ]
    filed = {"K": date(2020, 2, 25), "Q3": date(2020, 10, 27)}
    parts = ((1, "ShortTermBorrowings"), (1, "LongTermDebtAndCapitalLeaseObligations"))
    face = _Face({("Q3", "ShortTermBorrowings"), ("Q3", "LongTermDebtNoncurrent")})

    def zero_ok(a, t):  # the shared rule says zero (calc parent ties); the rename veto must overrule it
        return not sh.renamed_part_printed(face, ROWS, NAME, OWN, a, END, END, "instant")

    # zero_ok True means "treat as zero" -> mirror the production lambda: zero only when NOT renamed
    def prod_zero_ok(a, t):
        return True and not sh.renamed_part_printed(face, ROWS, NAME, OWN, a, END, END, "instant")

    assert sh.component_sum_authority(copies, parts, filed, None, prod_zero_ok) == ("K", D("1200"))
    # without the veto the later 10-Q (ST 200, LTD "zero") wins with 200
    assert sh.component_sum_authority(copies, parts, filed, None, lambda a, t: True) == ("Q3", D("200"))
    assert zero_ok  # kept for readability
