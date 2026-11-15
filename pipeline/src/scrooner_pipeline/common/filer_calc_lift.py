"""One definition of when a filer's FAILED calc check is lifted (quarantine lifted), shared by the proof
(proof/identities.py: lifting_row, residual_line_tie) and the structural loader (mapper/structural_loader.py
quarantined / structural_direct): a lifted filing is both loaded and proven. Pure: no DB, no FilingStructure.

A failed calc group of a filing column says the filer's calc linkbase omits or mis-weights a child; the cell is lifted
ONLY from the same filing column, by one of these routes (recorded as `route` in the check detail):

  independent_tie              a passing printed-totals check of the column names the parent's data point, or an
                               alternative calc group of the same parent passes (LLY CFO 2019).
  cf_parts_eq_change           the failed group is the net-change-in-cash tree (CF_CHANGE_RE) and the same column's
                               cf_parts_eq_change passes (ISRG FY2019; fsn_store/checks.cf_change_check records
                               calc_tree_failed when the printed numbers tie but the tree does not).
  printed_residual_child_excluded / printed_residual_line_omitted
                               the group's residual (parent minus children sum) equals exactly one printed line
                               within the filer's rounding: a child the printed parent does not include (NEE FY2020
                               opex, gain on disposal) or a same-statement face line the group omits (NEE FY2020
                               operating income; NEE FY2024 L&SE + 401 redeemable NCI).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import date
from decimal import Decimal
from typing import Any

from scrooner_pipeline.fsn_store.checks import CF_CHANGE_RE

# data points that are members of a filing_check by name (the calc:<parent>:<group> checks are matched by tag)
CHECK_MEMBERS: dict[str, tuple[str, ...]] = {
    "bs_assets_eq_liabilities_equity": (
        "total_assets",
        "total_liabilities",
        "stockholders_equity",
    ),
    "cf_parts_eq_change": ("cfo", "cash_flow_investing", "cash_flow_financing"),
    "is_gross_profit": ("revenue", "cost_of_revenue", "gross_profit"),
    "is_ni_total_minus_nci_eq_parent": ("net_income",),
    "cross_cf_ni_eq_is_ni": ("net_income",),
}


class CheckRow:
    """One fsn.filing_check row of a filing column."""

    __slots__ = ("check_id", "children", "lhs", "ok", "rhs", "stmt", "tol")

    def __init__(
        self,
        stmt: str,
        check_id: str,
        ok: bool,
        lhs: Decimal | None,
        rhs: Decimal | None,
        tol: Decimal | None,
        children: tuple[str, ...] = (),
    ) -> None:
        self.stmt, self.check_id, self.ok = stmt, check_id, ok
        self.lhs, self.rhs, self.tol, self.children = lhs, rhs, tol, children


def related_tags(row: CheckRow, dp: str, tags: tuple[str, ...]) -> bool:
    """Is a cell (data point `dp`, source `tags`) a member of this check (named members, or the calc parent / one of
    its children)?"""
    if row.check_id in CHECK_MEMBERS:
        return dp in CHECK_MEMBERS[row.check_id]
    if row.check_id.startswith("calc:"):
        parent = row.check_id.split(":")[1]
        return any(t == parent or t in row.children for t in tags)
    return False


# calc parents that are served totals the named identities (CHECK_MEMBERS) tie by data point
PARENT_DP: dict[str, str] = {
    "NetCashProvidedByUsedInOperatingActivities": "cfo",
    "NetCashProvidedByUsedInInvestingActivities": "cash_flow_investing",
    "NetCashProvidedByUsedInFinancingActivities": "cash_flow_financing",
    "Assets": "total_assets",
    "Liabilities": "total_liabilities",
    "StockholdersEquity": "stockholders_equity",
    "GrossProfit": "gross_profit",
    "NetIncomeLoss": "net_income",
}


def lifting_row(
    rows: list[CheckRow], failed: CheckRow, dp: str, tags: tuple[str, ...]
) -> CheckRow | None:
    """The independent tie that lifts a failed calc group's quarantine, ONLY from the SAME filing column (`rows`).
    The group's parent total must be tied independently of the failed sum: a printed-totals identity of that column
    that PASSES and names the parent's data point (cf_parts_eq_change for the three cash-flow totals, the balance-sheet
    identity, gross profit), or an alternative calc group of the same parent that passes. The failed group then only
    says the filer's calc linkbase omits a child (LLY CFO 2019: the Elanco discontinued-operations line is no calc
    child). A cell that is the parent is lifted by that; a CHILD cell needs its own passing tie as well (net income
    IS = CF), because a failed sum cannot say which child is wrong. Returns the tie row or None. Pure."""
    if not failed.check_id.startswith("calc:"):
        return None
    parent = failed.check_id.split(":")[1]
    tie: CheckRow | None = None
    for r in rows:
        if r is failed or r.check_id == failed.check_id or not r.ok:
            continue
        if r.check_id.startswith("calc:"):
            if r.check_id.split(":")[1] == parent:
                tie = r
                break
        elif PARENT_DP.get(parent) in CHECK_MEMBERS.get(r.check_id, ()):
            tie = r
            break
        elif r.check_id == "cf_parts_eq_change" and CF_CHANGE_RE.match(parent):
            # the failed group is the filer's net-change-in-cash tree; the same column's printed cash-flow totals
            # tie to the printed change (cf_parts_eq_change passes, calc_tree_failed recorded): ISRG FY2019
            tie = r
            break
    if tie is None:
        return None
    if parent in tags:
        return tie
    own = next(
        (
            r
            for r in rows
            if r.ok
            and r.check_id != failed.check_id
            and not r.check_id.startswith("calc:")
            and related_tags(r, dp, tags)
        ),
        None,
    )
    return tie if own is not None else None


def residual_line_tie(
    failed: CheckRow,
    children: Sequence[tuple[str, bool]],
    value_of: Callable[[str], Decimal | None],
    face_tags: Iterable[str],
) -> dict[str, Any] | None:
    """The filing's PRINTED arithmetic ties although its calc group does not: the group's residual (parent minus the
    children sum) equals, within the filer's rounding, EXACTLY ONE printed line, either a child the printed parent
    does not include (NEE FY2020 operating expenses: the gain on disposal is a -1 child, 13,234 - 12,881 = 353) or a
    same-statement face line the calc group omits (NEE FY2020 operating income: 17,997 - 13,234 + 353 = 5,116;
    NEE FY2024 L&SE: 129,283 + 401 redeemable NCI + 60,460 = 190,144). Same filing, same column, undimensioned
    values only; the line must exceed twice the tolerance so rounding cannot explain it. None when no single line
    explains the residual. Pure."""
    if (
        not failed.check_id.startswith("calc:")
        or failed.lhs is None
        or failed.rhs is None
        or failed.tol is None
    ):
        return None
    parent = failed.check_id.split(":")[1]
    if len(children) < 2:
        return None
    residual = failed.lhs - failed.rhs
    tol = failed.tol
    child_tags = {c for c, _n in children}
    for ctag, neg in children:  # a printed child the printed parent does not include
        v = value_of(ctag)
        if v is None or abs(v) <= 2 * tol:
            continue
        w = Decimal(-1) if neg else Decimal(1)
        if abs(residual + w * v) <= tol:
            return {
                "rule": "printed_residual_child_excluded",
                "line": ctag,
                "value": str(v),
                "weight": str(w),
                "residual": str(residual),
            }
    seen: set[str] = set()
    for tag in face_tags:
        if tag in child_tags or tag == parent or tag in seen:
            continue
        seen.add(tag)
        v = value_of(tag)
        if v is None or abs(v) <= 2 * tol:
            continue
        for sign in (1, -1):
            if abs(residual - sign * v) <= tol:
                return {
                    "rule": "printed_residual_line_omitted",
                    "line": tag,
                    "value": str(v),
                    "sign": sign,
                    "residual": str(residual),
                }
    return None


def lift_route(
    rows: list[CheckRow],
    failed: CheckRow,
    dp: str,
    tags: tuple[str, ...],
    *,
    children: Sequence[tuple[str, bool]] = (),
    value_of: Callable[[str], Decimal | None] | None = None,
    face_tags: Iterable[str] = (),
) -> dict[str, Any] | None:
    """The route that lifts a failed calc check, with its detail, or None (the filing stays quarantined). `rows` are
    the check rows of the SAME filing column; children/value_of/face_tags describe that filing's group (the loader
    reads them from fsn.calc_arc / fsn.value / fsn.line, the proof from its FilingStructure)."""
    tie = lifting_row(rows, failed, dp, tags)
    if tie is not None:
        route = (
            "cf_parts_eq_change"
            if tie.check_id == "cf_parts_eq_change"
            else "independent_tie"
        )
        return {
            "route": route,
            "lifted_by": tie.check_id,
            "tie_lhs": str(tie.lhs),
            "tie_rhs": str(tie.rhs),
        }
    if value_of is not None:
        rt = residual_line_tie(failed, children, value_of, face_tags)
        if rt is not None:
            return {"route": rt["rule"], "lifted_by": rt["rule"], "printed_line": rt}
    return None
