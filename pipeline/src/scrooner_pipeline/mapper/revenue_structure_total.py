"""Structural revenue-total pick (NA-9, RF-48 ``revenue.structure_total@1``): pure decision logic.

NOT WIRED. The inputs (income-statement presentation rows, calculation arcs, face dimension
members, per accession and context) do not exist in our tables yet: ``core.fact`` keeps no context,
dimension or presentation order, and companyfacts strips them (data-team/37 section 7). This module
is the source-selection rule of data-team/37 sections 4-5 written as a pure function so the
Verifier's 30-case plan (section 8) can be run on structure evidence as soon as the loader
(FSDS ``pre.txt``/``num.txt`` plus the filing's calculation linkbase) exists. Until then the
disagreement guard (``revenue_total_guard``) hides the periods this would convert into values.

Rule. Candidates are the undimensioned revenue-line rows of the income statement for one filing
and one context. The selected row must satisfy ALL of:
  P1  position: the last revenue-section row before the first expense row;
  P2  calc: a calculation child (+1) of a profit subtotal, or the parent of the other revenue rows,
      and not contradicted as a child of another revenue row;
  P3  identity: its value equals, within rounding, the sum of its weighted calc children, or of the
      revenue-line presentation siblings above it (no calc children: OGE), or of its own face
      dimension members (SNA, GM). A single revenue row with nothing to sum passes on P1+P2 and is
      flagged ``single_line`` (weaker).
and the tag must be standard us-gaap. Tie-breaks, in order: the calc parent of the other
candidates; the candidate whose identity holds; two passing candidates = ``two_totals`` (never
"largest": wrong in 5 of 19 doc-37 companies); none = ``identity_failed``. Banks are out of this
anchor (their own template).

Evidence for the rule: FILING-CHECKED in data-team/37 section 2 (19 of 19 decidable cases; the
fixtures in tests/unit/test_revenue_structure_total.py are those rows).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

RULE_ID = "revenue.structure_total@1"

PROFIT_SUBTOTALS = frozenset(
    {
        "GrossProfit",
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        "CostsAndExpenses",
    }
)


@dataclass(frozen=True)
class IsRow:
    order: int
    taxonomy: str
    tag: str
    kind: str  # "revenue_line" | "expense_line" | "other"
    value: Decimal | None  # undimensioned value in the context
    tol: Decimal = Decimal(0)  # absolute rounding interval of the value
    members: tuple[Decimal, ...] = ()  # face dimension members of the same tag, if any


@dataclass(frozen=True)
class CalcArc:
    parent: str
    child: str
    weight: int


@dataclass(frozen=True)
class StructuralPick:
    tag: str
    value: Decimal
    single_line: bool
    proof: str


@dataclass(frozen=True)
class Blank:
    reason: str  # revenue_total_undecidable.<sub>


def _near(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= max(tol, Decimal("0.5"))


def _identity(
    cand: IsRow,
    rows: Sequence[IsRow],
    arcs: Sequence[CalcArc],
    notes_by_tag: dict[str, IsRow],
) -> str | None:
    """Name of the identity that holds (for the proof), else None. cand.value is not None."""
    assert cand.value is not None
    kids = [a for a in arcs if a.parent == cand.tag and a.child in notes_by_tag]
    if kids:
        total = sum(
            (a.weight * (notes_by_tag[a.child].value or Decimal(0)) for a in kids),
            Decimal(0),
        )
        tol = cand.tol + sum((notes_by_tag[a.child].tol for a in kids), Decimal(0))
        if _near(total, cand.value, tol):
            return "calc_children"
    above = [
        r
        for r in rows
        if r.kind == "revenue_line" and r.order < cand.order and r.value is not None
    ]
    if above:
        total = sum((r.value for r in above if r.value is not None), Decimal(0))
        tol = cand.tol + sum((r.tol for r in above), Decimal(0))
        if _near(total, cand.value, tol):
            return "presentation_siblings"
    if cand.members:
        if _near(sum(cand.members, Decimal(0)), cand.value, cand.tol):
            return "face_members"
    return None


def select_structural_total(
    rows: Sequence[IsRow], arcs: Sequence[CalcArc], *, is_bank: bool = False
) -> StructuralPick | Blank:
    if is_bank:
        return Blank("revenue_total_undecidable.bank_template")
    revenue_rows = [r for r in rows if r.kind == "revenue_line" and r.value is not None]
    if not revenue_rows:
        return Blank("revenue_total_undecidable.no_statement_located")
    first_expense = min(
        (r.order for r in rows if r.kind == "expense_line"), default=None
    )
    section = [
        r for r in revenue_rows if first_expense is None or r.order < first_expense
    ]
    if not section:
        return Blank("revenue_total_undecidable.no_statement_located")
    p1 = max(
        section, key=lambda r: r.order
    )  # P1: last revenue row before the first expense row
    notes_by_tag = {r.tag: r for r in revenue_rows}
    children_of_other_revenue = {
        a.child for a in arcs if a.parent in notes_by_tag and a.parent != p1.tag
    }
    if p1.tag in children_of_other_revenue and len(section) > 1:
        return Blank(
            "revenue_total_undecidable.identity_failed"
        )  # P2 contradicted: a child of another row
    if p1.taxonomy != "us-gaap":
        return Blank("revenue_total_undecidable.total_line_not_tagged_standard")
    if len(section) == 1:
        child_of_subtotal = any(
            a.child == p1.tag and a.parent in PROFIT_SUBTOTALS and a.weight == 1
            for a in arcs
        )
        ident = _identity(p1, rows, arcs, notes_by_tag)
        if ident is not None:
            return StructuralPick(p1.tag, p1.value, False, f"P1+{ident}")  # type: ignore[arg-type]
        if child_of_subtotal:
            return StructuralPick(p1.tag, p1.value, True, "P1+P2 single_line")  # type: ignore[arg-type]
        return Blank("revenue_total_undecidable.identity_failed")
    ident = _identity(p1, rows, arcs, notes_by_tag)
    if ident is None:
        return Blank("revenue_total_undecidable.identity_failed")
    # a second total: another section row proven by its own calc children / face members that is
    # not a component of the selected row
    others = [
        r
        for r in section
        if r is not p1
        and _identity(r, rows, arcs, notes_by_tag) in ("calc_children", "face_members")
        and not any(a.parent == p1.tag and a.child == r.tag for a in arcs)
    ]
    if others:
        return Blank("revenue_total_undecidable.two_totals")
    return StructuralPick(p1.tag, p1.value, False, f"P1+{ident}")  # type: ignore[arg-type]
