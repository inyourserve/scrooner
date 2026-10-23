"""Total debt from the balance-sheet CARRYING lines (pure; no settings, no database).

Why (ledger 2026-10-21, mind: ledger-build-total-debt-from-the-balance-sheet): ``LongTermDebt`` is face
value at AMZN and GOOG and a $0.1B-rounded narrative at AAPL's 10-Q, so a total built from it is
0.1-1.1% off the balance sheet. The balance sheet prints carrying lines: noncurrent debt, current
debt, short-term borrowings. Their tags are ``LongTermDebtNoncurrent``, ``LongTermDebtCurrent`` (or
``DebtCurrent``), ``ShortTermBorrowings`` / ``CommercialPaper``.

    total = noncurrent + current block [+ short-term borrowings]

Filing-checked targets (balance-sheet R-files): AAPL 10-Q Q3 FY26 84,344 = CP 1,997 + term debt
current 11,007 + noncurrent 71,340 (the old path gave 84,297 from the rounded LongTermDebt 82,300);
GOOG FY2025 48,543 = 46,547 + 1,996 (old 49,085 face); AMZN FY2025 68,851 and Q2 2026 132,549 = 128,894 +
3,330 + 325 (old 133,320); PFE FY2020 39,836; DPZ FY2024 4,975,338K (lease family pair).

Safety, so the mechanism cannot invent a total:
* the current block must match: a filed ``DebtCurrent`` must be explained by a subset sum of the
  current-debt parts filed beside it, else HOLD (CVX FY2016: DebtCurrent 19,840 vs short-term debt
  10,840 + current maturities 6,253 + ...; the printed total is 46,033 but tags cannot say that the
  10,840 already contains the current maturities, so it is held, not guessed);
* lease family: a lease-inclusive noncurrent pairs only with the lease-inclusive current line;
* agreement: when ``LongTermDebt`` is filed beside noncurrent and current lines it must lie within
  10% of their sum, and the company's own ``DebtLongtermAndShorttermCombinedAmount`` within 10% of the total (face vs carrying is a few percent); otherwise the mechanism does not apply and
  the legacy path and the guards decide;
* no noncurrent line, or no current line: not applicable (None).
Authoritative facts only: the caller passes them.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations

PAIRS = (
    ("LongTermDebtNoncurrent", "LongTermDebtCurrent"),
    (
        "LongTermDebtAndCapitalLeaseObligations",
        "LongTermDebtAndCapitalLeaseObligationsCurrent",
    ),
)
SHORT_TERM = ("ShortTermBorrowings", "CommercialPaper")
CURRENT_PART_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "OtherShortTermBorrowings",
    "ShortTermBankLoansAndNotesPayable",
    "LinesOfCreditCurrent",
    "NotesPayableCurrent",
    "ConvertibleNotesPayableCurrent",
    "LongTermDebtCurrent",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
)
CARRYING_TAGS = tuple(
    dict.fromkeys(
        [t for p in PAIRS for t in p]
        + list(SHORT_TERM)
        + list(CURRENT_PART_TAGS)
        + ["DebtCurrent", "LongTermDebt", "DebtLongtermAndShorttermCombinedAmount"]
    )
)
EXPLAIN_TOLERANCE = Decimal("0.02")
AGREEMENT_TOLERANCE = Decimal("0.10")


@dataclass(frozen=True)
class Carrying:
    value: Decimal
    tags: tuple[str, ...]
    path: str


@dataclass(frozen=True)
class Hold:
    reason: str  # "current_block_unexplained"


def current_parts_explain(vals: Mapping[str, Decimal], debt_current: Decimal) -> bool:
    """False only when DebtCurrent is CONTRADICTED by the current-debt parts filed beside it: no subset of
    them sums to it (within 2%) AND it is smaller than all of them together, i.e. the parts overlap and the
    tags cannot say which are inside which (CVX FY2016: 19,840 against parts that sum to 27,553 with
    short-term debt 10,840 already containing the 6,253 current maturities). A DebtCurrent at or above the
    sum of the listed parts may hold unlisted components (TSLA non-recourse and lease lines): it is the
    printed line and is accepted. Zero, and 'no part filed', are accepted too."""
    if debt_current == 0:
        return True
    parts = [vals[t] for t in CURRENT_PART_TAGS if t in vals and vals[t] > 0]
    if not parts:
        return True
    tol = debt_current * EXPLAIN_TOLERANCE
    if debt_current >= sum(parts) - tol:
        return True
    return any(
        abs(sum(c) - debt_current) <= tol
        for n in range(1, len(parts) + 1)
        for c in combinations(parts, n)
    )


def carrying_lines(vals: Mapping[str, Decimal]) -> Carrying | Hold | None:
    pair = next(((n, c) for n, c in PAIRS if n in vals), None)
    if pair is None:
        return None
    noncurrent, current = pair
    n_val = vals[noncurrent]
    if "DebtCurrent" in vals:
        if not current_parts_explain(vals, vals["DebtCurrent"]):
            return Hold("current_block_unexplained")
        return Carrying(
            n_val + vals["DebtCurrent"],
            (noncurrent, "DebtCurrent"),
            "carrying_noncurrent+debt_current",
        )
    if current not in vals:
        return None
    c_val = vals[current]
    lt = vals.get("LongTermDebt")
    if lt is not None and lt > 0:
        base = n_val + c_val
        if abs(lt - base) > AGREEMENT_TOLERANCE * lt:
            return None
    short_tag = next((t for t in SHORT_TERM if t in vals), None)
    tags = [noncurrent, current]
    total = n_val + c_val
    if short_tag is not None and vals[short_tag] != c_val:
        total += vals[short_tag]
        tags.append(short_tag)
    all_in = vals.get("DebtLongtermAndShorttermCombinedAmount")
    if (
        all_in is not None
        and all_in > 0
        and abs(all_in - total) > AGREEMENT_TOLERANCE * all_in
    ):
        return None  # the company's own stated total disagrees by more than face vs carrying: not proven
    return Carrying(total, tuple(tags), "carrying_noncurrent+current+short_term")
