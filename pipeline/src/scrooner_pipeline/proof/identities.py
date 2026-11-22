"""Identities over the SERVED values, a post-pass of the cell proof: the filing's own arithmetic decides.

Founder direction 2026-11-13 (data-team/tags/STRUCTURAL-MAPPING.md): no operand lists. A served member is a node
(tag, column) of ONE filing, the statement filing it is served from (common/authority statement_filing), and that
filing's own calc linkbase arithmetic was already evaluated per column into fsn.filing_check (fsn_store/checks.py:
calc:<parent>:<group>, bs_assets_eq_liabilities_equity, cf_parts_eq_change, is_gross_profit, cross ties).

  node_mismatch          a served member whose value differs from its node in the statement filing (printed,
                         non-dimensional, same column, within the filer's dcml): identity_break (a vintage mix:
                         JPM 2015-Q1 assets from a later 10-Q's summary table).
  filer_arithmetic_fails the statement filing's own check for that column FAILS and the cell is one of its
                         members (the parent or a calc child): the filing is quarantined for those cells, DISAGREE
                         reason filer_arithmetic_fails, checks.identity carries the check id. Never served as PROVEN.
  hand_fallback          only where the filing has no filing_check row for the relation (no calc arcs, ~1%): the
                         minimal gross_profit / operating_income / assets = printed L&SE ties, source hand_fallback.
                         Net income IS to CF start stays (a cross-statement tie served-vs-CF line).

Tolerance is the filer's rounding (0.5 x unit per operand, fsn dcml; fsn_store/checks.tol_of). SKIPPED, never
derived, when a member is not served, not presented, combined, derived-not-printed (mapper/derived_cells.py) or
a derived Q4 / 6M / 9M span (not a filed column). Break marks each member that would be PROVEN as DISAGREE with
checks.identity = {name, source, members, lhs, rhs, diff, tolerance, ...}.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import psycopg

from scrooner_pipeline.common.filer_calc_lift import (  # noqa: F401  (re-exported: tests and shown.py)
    CHECK_MEMBERS,
    PARENT_DP,
    CheckRow,
    lift_route,
    lifting_row,
    related_tags,
    residual_line_tie,
)
from scrooner_pipeline.mapper.dqc_checks import tolerance
from scrooner_pipeline.proof.fsn import FilingStructure, fsn_ddate
from scrooner_pipeline.proof.prove import DISAGREE, NOT_PRESENTED, PROVEN, Proof

REASON = "identity_break"
QUARANTINE_REASON = "filer_arithmetic_fails"

PeriodKey = tuple[str, date, date]  # (grain, start, end)
PrintedKey = tuple[str, date | None, date]  # (tag, start for durations, end)

# operand tags kept ONLY for mapper/derived_cells.py (total liabilities = L&SE - the equity side); no identity uses them
NCI_EQUITY_TAGS: tuple[str, ...] = (
    "MinorityInterest",
    "NonredeemableNoncontrollingInterest",
    "StockholdersEquityAttributableToNoncontrollingInterestContinuingOperations",
)
EQUITY_INCL_NCI_TAG = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
)
# mezzanine / temporary-equity operands (triage 2026-11-13, data-team/tags/red-cells/identity-breaks-2026-11-13.csv):
# ALL present are summed. The including-NCI total already holds the redeemable-NCI and parent lines, so those parts
# are dropped when it is printed (never counted twice).
TEMP_EQUITY_TOTAL_TAG = (
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests"
)
TEMP_EQUITY_PART_TAGS: tuple[str, ...] = (
    "TemporaryEquityCarryingAmountAttributableToParent",
    "RedeemableNoncontrollingInterestEquityCarryingAmount",
    "RedeemableNoncontrollingInterestEquityOtherFairValue",
    "RedeemableNoncontrollingInterestEquityFairValue",
    "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
)
TEMP_EQUITY_OTHER_TAGS: tuple[str, ...] = (
    "TemporaryEquityPreferredStockDividendObligation",
    "TemporaryEquityValueExcludingAdditionalPaidInCapital",
    "ConvertibleDebtEquity",
    "DebtInstrumentConvertibleCarryingAmountOfTheEquityComponent",
)
TEMP_EQUITY_TAGS: tuple[str, ...] = (
    TEMP_EQUITY_TOTAL_TAG,
    *TEMP_EQUITY_PART_TAGS,
    *TEMP_EQUITY_OTHER_TAGS,
)
LSE_TAGS = ("LiabilitiesAndStockholdersEquity", "LiabilitiesAndEquity")

NI_START_TAGS = frozenset(
    {"NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"}
)
NCI_INCOME_TAGS = (
    "NetIncomeLossAttributableToNoncontrollingInterest",
    "NetIncomeLossAttributableToRedeemableNoncontrollingInterest",
)
PRINTED_TAGS: tuple[str, ...] = NCI_INCOME_TAGS

# served members tied to their node in the statement filing
NODE_MEMBERS = frozenset(
    {
        "revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_expenses",
        "operating_income",
        "total_assets",
        "total_liabilities",
        "stockholders_equity",
        "cfo",
        "cash_flow_investing",
        "cash_flow_financing",
        "net_income",
    }
)
# hand fallback applies when the filing's column has none of these check rows
FALLBACK_COVER: dict[str, tuple[str, ...]] = {
    "gross_profit": ("is_gross_profit", "calc:GrossProfit:"),
    "operating_income": ("calc:OperatingIncomeLoss:",),
    "balance_sheet": ("bs_assets_eq_liabilities_equity",),
}


# (accession, ddate, qtrs) -> the filing's check rows for that column
FilingChecks = dict[tuple[str, date, int], list[CheckRow]]


def base_name(name: str) -> str:
    for suffix in ("_sanity_resolved", "_resolved"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def load_filing_checks(conn: psycopg.Connection, company_id: int) -> FilingChecks:
    """Every fsn.filing_check row of the company's filings, one query (batch per company, never per cell)."""
    out: FilingChecks = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.accession, fc.ddate, fc.qtrs, fc.stmt, fc.check_id, fc.ok, fc.lhs, fc.rhs, fc.tol,
                   fc.detail->'children'
            from fsn.filing_check fc join fsn.filing f on f.id = fc.filing_id
            where f.company_id = %s
            """,
            (company_id,),
        )
        for acc, dd, q, stmt, cid, ok, lhs, rhs, tol, kids in cur.fetchall():
            tags = tuple(k[0] for k in (kids or []) if k)
            out[(acc, dd, int(q))].append(
                CheckRow(
                    stmt,
                    cid,
                    bool(ok),
                    None if lhs is None else Decimal(lhs),
                    None if rhs is None else Decimal(rhs),
                    None if tol is None else Decimal(tol),
                    tags,
                )
            )
    return dict(out)


def load_printed(
    conn: psycopg.Connection, company_id: int, floor: date
) -> dict[PrintedKey, Decimal]:
    """Printed (non-derived, authoritative) NCI income values (the net_income_cf tie). A key with two distinct
    values is ambiguous and dropped (never guess an operand)."""
    out: dict[PrintedKey, set[Decimal]] = defaultdict(set)
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.tag, p.period_type, p.start_date, p.end_date, f.value
            from core.fact f
            join core.concept c on c.id = f.concept_id
            join core.period p on p.id = f.period_id
            where f.company_id = %s and f.is_authoritative and not f.is_derived
              and c.taxonomy = 'us-gaap' and c.tag = any(%s) and p.end_date >= %s
            """,
            (company_id, list(PRINTED_TAGS), floor),
        )
        for tag, ptype, start, end, value in cur.fetchall():
            out[(tag, start if ptype == "duration" else None, end)].add(Decimal(value))
    return {k: next(iter(v)) for k, v in out.items() if len(v) == 1}


def not_printed(p: Proof) -> bool:
    """A cell that is no printed line: derived (a Q4 or a sum from a derived fact), or served with no source fact
    at all (mapper/derived_cells.py: gross profit = revenue - cost of revenue, total liabilities = L&SE - equity,
    family company_tag_map:derived_not_printed). An identity over it would only restate its own derivation."""
    s = p.shown
    return s.is_derived or (not s.source_fact_ids and not s.tags)


def cf_start_value(
    structures: dict[str, FilingStructure], proof: Proof
) -> tuple[str, Decimal] | None:
    """(tag, value) of the first cash-flow line of the filing the net_income cell came from, at the cell's
    annual column; None when the structure or the line is not there."""
    s = proof.shown
    st = structures.get(s.accession or "")
    if st is None or s.period_grain != "FY":
        return None
    lines = st.lines_on("CF")
    if not lines or lines[0].tag not in NI_START_TAGS:
        return None
    v = st.value(lines[0].tag, fsn_ddate(s.period_end), 4)
    if v is None:
        return None
    return lines[0].tag, v.value


def _qtrs(grain: str) -> int:
    return {"I": 0, "FY": 4}.get(grain, 1)


def _unit(nv: Any) -> Decimal:
    """The filer's rounding unit (fsn dcml); an exact print (dcml beyond 20, 'INF') has none."""
    d = nv.dcml
    if d is None:
        return Decimal(1)
    if abs(int(d)) > 20:
        return Decimal(0)
    return Decimal(10) ** (-int(d))


def node_mismatch(
    st: FilingStructure, dp: str, p: Proof, ddate: date, qtrs: int
) -> dict[str, Any] | None:
    """A served single-tag member whose value is not its node (tag, column) in the statement filing.
    The node is the cell's CLAIMED tag (the proof's claim, set from the mapping), not a tag of the source
    records: a resolver-served cell has source records of only some of its parts (MSFT/TXN opex = R&D + SG&A +
    restructuring listed as one part's tag; AMD cost of revenue claimed on CostOfGoodsAndServicesSold, source
    tag AmortizationOfAcquisitionRelatedIntangibles). A component-sum claim is no single node."""
    claim = p.checks.get("claim") or {}
    if claim.get("kind") == "component":
        return None
    tags = tuple(claim.get("tags") or ()) or p.shown.tags
    if len(tags) != 1:
        return None
    tag = tags[0]
    nv = st.value(tag, ddate, qtrs)
    if nv is None:
        return None
    tol = Decimal("0.5") * _unit(nv)
    diff = p.shown.value - nv.value
    if abs(diff) <= tol:
        return None
    return {
        "name": "node_mismatch",
        "source": "filing_check",
        "members": {dp: str(p.shown.value)},
        "tag": tag,
        "accession": st.adsh,
        "lhs": str(p.shown.value),
        "rhs": str(nv.value),
        "diff": str(diff),
        "tolerance": str(tol),
    }


def related(row: CheckRow, dp: str, p: Proof) -> bool:
    """Is the served cell a member of this check (named members, or the calc parent / one of its children)?"""
    return related_tags(row, dp, p.shown.tags)


def failing_unlifted(
    rows: list[CheckRow], dp: str, tags: tuple[str, ...]
) -> list[CheckRow]:
    """The failed checks of a filing column the cell belongs to that no independent tie lifts."""
    return [
        r
        for r in rows
        if not r.ok
        and related_tags(r, dp, tags)
        and lifting_row(rows, r, dp, tags) is None
    ]


def _covered(rows: list[CheckRow], identity: str) -> bool:
    return any(r.check_id.startswith(c) for r in rows for c in FALLBACK_COVER[identity])


def _usable(p: Proof | None) -> bool:
    """A member that may enter an identity: served, line presented, not a combined line."""
    return (
        p is not None
        and p.verdict != NOT_PRESENTED
        and not p.shown.combined
        and not (p.reason_code and "combined" in p.reason_code)
    )


def _lift_route_in(
    st: FilingStructure | None,
    rows: list[CheckRow],
    failed: CheckRow,
    dp: str,
    tags: tuple[str, ...],
    ddate: date,
    qtrs: int,
) -> dict[str, Any] | None:
    """common/filer_calc_lift.lift_route over this filing's structure (the loader calls the same function)."""
    if st is None:
        return lift_route(rows, failed, dp, tags)
    children: Sequence[tuple[str, bool]] = ()
    if failed.check_id.startswith("calc:"):
        _c, parent, grp = (failed.check_id.split(":") + ["", ""])[:3]
        children = st.calc_groups.get(parent, {}).get(grp) or ()

    def value_of(tag: str) -> Decimal | None:
        nv = st.value(tag, ddate, qtrs)
        return None if nv is None else nv.value

    return lift_route(
        rows,
        failed,
        dp,
        tags,
        children=children,
        value_of=value_of,
        face_tags=[ln.tag for ln in st.lines_on(failed.stmt)],
    )


def _evaluate(
    name: str,
    members: dict[str, Proof],
    lhs: Decimal,
    rhs: Decimal,
    extra: list[Decimal] | None = None,
    detail: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """The hand-fallback record when lhs and rhs differ beyond the operands' rounding slack, else None."""
    tol = tolerance([p.shown.value for p in members.values()] + list(extra or []))
    if abs(lhs - rhs) <= tol:
        return None
    rec: dict[str, Any] = {
        "name": name,
        "source": "hand_fallback",
        "members": {dp: str(p.shown.value) for dp, p in members.items()},
        "lhs": str(lhs),
        "rhs": str(rhs),
        "diff": str(lhs - rhs),
        "tolerance": str(tol),
    }
    if detail:
        rec["operands"] = detail
    return rec


def _check_period(
    cells: dict[str, Proof],
    grain: str,
    start: date,
    end: date,
    printed: dict[PrintedKey, Decimal],
    cf_start: tuple[str, Decimal] | None,
    structures: dict[str, FilingStructure] | None,
    checks: FilingChecks | None,
) -> list[tuple[dict[str, Any], dict[str, Proof], str]]:
    """Every failed check of one company period: (record, member proofs, reason code)."""
    out: list[tuple[dict[str, Any], dict[str, Proof], str]] = []
    if grain == "Q" and (end - start).days > 100:
        return out  # a 6M/9M span is no filed column (C3)
    ddate, qtrs = fsn_ddate(end), _qtrs(grain)

    def get(*dps: str) -> dict[str, Proof] | None:
        got = {d: cells.get(d) for d in dps}
        if all(_usable(p) for p in got.values()):
            members: dict[str, Proof] = got  # type: ignore[assignment]
            # a derived Q4 is no filed column (C3); a derived-not-printed member would only restate its derivation
            if any(
                (grain == "Q" and p.shown.is_derived)
                or (d in ("gross_profit", "total_liabilities") and not_printed(p))
                for d, p in members.items()
            ):
                return None
            return members
        return None

    def v(m: dict[str, Proof], dp: str) -> Decimal:
        return m[dp].shown.value

    def add(rec: dict[str, Any] | None, m: dict[str, Proof]) -> None:
        if rec is not None:
            out.append((rec, m, REASON))

    # 1. each served member equals its node in the statement filing; 2. that filing's own check passes
    rows_of: dict[str, list[CheckRow]] = {}
    for dp, p in cells.items():
        if dp not in NODE_MEMBERS or not _usable(p) or not_printed(p):
            continue
        if grain == "Q" and p.shown.is_derived:
            continue
        acc = p.shown.accession or ""
        st = (structures or {}).get(acc)
        if st is not None:
            add(node_mismatch(st, dp, p, ddate, qtrs), {dp: p})
        rows = (checks or {}).get((acc, ddate, qtrs), [])
        rows_of[dp] = rows
        for r in rows:
            if not r.ok and related(r, dp, p):
                route = _lift_route_in(st, rows, r, dp, p.shown.tags, ddate, qtrs)
                if route is not None:
                    # the filing's own printed arithmetic ties (route recorded): the failed group is an incomplete
                    # or mis-weighted calc linkbase, not a wrong value
                    p.checks.setdefault("quarantine_lifted", []).append(
                        {
                            "failed_check": r.check_id,
                            "accession": acc,
                            "lhs": str(r.lhs),
                            "rhs": str(r.rhs),
                            **route,
                        }
                    )
                    continue
                rec = {
                    "name": r.check_id,
                    "source": "filing_check",
                    "check_id": r.check_id,
                    "stmt": r.stmt,
                    "accession": acc,
                    "members": {dp: str(p.shown.value)},
                    "lhs": str(r.lhs),
                    "rhs": str(r.rhs),
                    "diff": str((r.lhs or 0) - (r.rhs or 0)),
                    "tolerance": str(r.tol),
                }
                out.append((rec, {dp: p}, QUARANTINE_REASON))

    def uncovered(identity: str, dp: str) -> bool:
        """No filing_check row for the relation in the member's filing column: the hand fallback judges it."""
        return not _covered(rows_of.get(dp, []), identity)

    if grain in ("FY", "Q"):
        m = get("revenue", "cost_of_revenue", "gross_profit")
        if m and uncovered("gross_profit", "gross_profit"):
            add(
                _evaluate(
                    "gross_profit",
                    m,
                    v(m, "revenue") - v(m, "cost_of_revenue"),
                    v(m, "gross_profit"),
                ),
                m,
            )
        m = get("gross_profit", "operating_expenses", "operating_income")
        if m:
            if uncovered("operating_income", "operating_income"):
                add(
                    _evaluate(
                        "operating_income",
                        m,
                        v(m, "gross_profit") - v(m, "operating_expenses"),
                        v(m, "operating_income"),
                    ),
                    m,
                )
        elif cells.get("gross_profit") is None:
            m = get(
                "revenue", "cost_of_revenue", "operating_expenses", "operating_income"
            )
            if m and uncovered("operating_income", "operating_income"):
                add(
                    _evaluate(
                        "operating_income",
                        m,
                        v(m, "revenue")
                        - v(m, "cost_of_revenue")
                        - v(m, "operating_expenses"),
                        v(m, "operating_income"),
                    ),
                    m,
                )
    if grain == "I":
        m = get("total_assets", "total_liabilities", "stockholders_equity")
        if m and uncovered("balance_sheet", "total_assets"):
            # fallback: assets = the filing's printed L&SE (the face total); never derived from the parts
            st = (structures or {}).get(m["total_assets"].shown.accession or "")
            lse = next(
                (
                    lv
                    for t in LSE_TAGS
                    if st is not None and (lv := st.value(t, ddate, 0)) is not None
                ),
                None,
            )
            if lse is not None:
                add(
                    _evaluate(
                        "balance_sheet",
                        {"total_assets": m["total_assets"]},
                        v(m, "total_assets"),
                        lse.value,
                        [lse.value],
                        {"LiabilitiesAndStockholdersEquity": str(lse.value)},
                    ),
                    m,
                )
    if grain == "FY":
        m = get("net_income")
        if m and cf_start is not None:
            tag, start_v = cf_start
            ni = v(m, "net_income")
            extra: list[Decimal] = []
            detail = {tag: str(start_v)}
            rhs = start_v
            nci_inc: Decimal | None = Decimal(0)
            if tag == "ProfitLoss":
                nci_inc = next(
                    (
                        x
                        for t in NCI_INCOME_TAGS
                        if (x := printed.get((t, start, end))) is not None
                    ),
                    None,
                )
                if nci_inc is None and ni == start_v:
                    nci_inc = Decimal(0)
            if (
                nci_inc is not None
            ):  # NCI income not printed: parent vs total cannot be told apart
                rhs = start_v - nci_inc
                if tag == "ProfitLoss":
                    extra.append(nci_inc)
                    detail["nci_income"] = str(nci_inc)
                add(
                    _evaluate("net_income_cf", m, ni, rhs, [start_v, *extra], detail),
                    m,
                )
    return out


SPLIT_REASON = "split_parts_do_not_sum_to_combined_line"


def _check_splits(
    cells: dict[str, Proof],
    grain: str,
    end: date,
    structures: dict[str, FilingStructure] | None,
) -> list[tuple[dict[str, Any], dict[str, Proof], str]]:
    """Founder decision 2026-11-16 (CERTIFICATION-METHOD): a combined face line split into data points from the notes
    must be the SUM of its parts. For each combined row spanning a served cell (Shown.combined_splits), when every
    spanned concept is served, PROVEN, printed and read from ONE filing, and that filing prints the combined line in
    the column, the parts' SIGNED sum (split_part_weight below) must equal the printed line within the filer's rounding.
    Judged only when parts and line are all non-negative. A part that is missing, unproven or from another filing
    leaves the split unjudged here (that is coverage, not a wrong value)."""

    def split_part_weight(
        st: FilingStructure,
        line_tag: str,
        concept: str,
        member: Proof,
        members: dict[str, Proof | None],
    ) -> Decimal:
        """The sign a split part enters its combined face line with. (1) The filing's own calc weight when the part's one
        printed tag is a calc child of the line. (2) Otherwise (the part is a NOTE fact, MRK 'Other (income) expense, net'
        = other 831 + interest income 343 - interest expense 772 = 402 FY2018) the concept's polarity
        (common/polarity.py): when the split mixes fixed-positive concepts (expenses) with signed ones, the line is a
        signed net line and every expense part enters it negatively. A split of only expenses (or only signed concepts)
        adds plainly (D&A = depreciation + amortization)."""
        from scrooner_pipeline.common.polarity import (
            is_fixed_positive,
        )

        tags = member.shown.tags
        if len(tags) == 1:
            for child, negative in st.calc_children.get(line_tag) or []:
                if child == tags[0]:
                    return Decimal(-1) if negative else Decimal(1)
        fixed = {c: is_fixed_positive(c) for c, m in members.items() if m is not None}
        if len(set(fixed.values())) > 1 and fixed[concept]:
            return Decimal(-1)
        return Decimal(1)

    out: list[tuple[dict[str, Any], dict[str, Proof], str]] = []
    if not structures:
        return out
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for p in list(cells.values()):
        for tag, comps in p.shown.combined_splits:
            if (tag, comps) in seen:
                continue
            seen.add((tag, comps))
            members = {c: cells.get(base_name(c)) for c in comps}
            if not all(
                m is not None and _usable(m) and m.verdict == PROVEN
                for m in members.values()
            ):
                continue
            accs = {m.shown.accession for m in members.values() if m is not None}
            acc = next(iter(accs)) if len(accs) == 1 else None
            st = structures.get(acc or "")
            if st is None:
                continue
            ddate, qtrs = fsn_ddate(end), _qtrs(grain)
            line = st.value(tag, ddate, qtrs)
            if line is None:
                continue
            vals = [m.shown.value for m in members.values() if m is not None]
            if line.value < 0 or any(v < 0 for v in vals):
                continue
            weights = {
                c: split_part_weight(st, tag, c, m, members)
                for c, m in members.items()
                if m is not None
            }
            total = sum(
                (weights[c] * m.shown.value for c, m in members.items() if m),
                Decimal(0),
            )
            tol = tolerance([*vals, line.value])
            for m in members.values():
                assert m is not None
                m.checks["split_parts"] = {
                    "status": "pass" if abs(total - line.value) <= tol else "fail",
                    "combined_tag": tag,
                    "combined_line": str(line.value),
                    "parts_sum": str(total),
                    "weights": {c: str(w) for c, w in weights.items()},
                    "accession": acc,
                }
            if abs(total - line.value) <= tol:
                continue
            rec = {
                "name": f"split:{tag}",
                "source": "split_check",
                "members": {c: str(m.shown.value) for c, m in members.items() if m},
                "lhs": str(total),
                "rhs": str(line.value),
                "diff": str(total - line.value),
                "tolerance": str(tol),
            }
            out.append(
                (rec, {c: m for c, m in members.items() if m is not None}, SPLIT_REASON)
            )
    return out


def apply_identities(
    proofs: list[Proof],
    printed: dict[PrintedKey, Decimal] | None = None,
    structures: dict[str, FilingStructure] | None = None,
    checks: FilingChecks | None = None,
) -> dict[str, int]:
    """Post-pass over a company's proofs (in place). Returns {check name: failures}; a quarantined column counts
    under its check id. `checks` None = filing_check not loaded: every identity is judged by the hand fallback."""
    printed = printed or {}
    by_period: dict[PeriodKey, dict[str, Proof]] = defaultdict(dict)
    for p in proofs:
        s = p.shown
        key = (s.period_grain, s.period_start, s.period_end)
        b = base_name(s.data_point_name)
        cur = by_period[key].get(b)
        if cur is None or (
            s.data_point_name.endswith("_resolved")
            and not cur.shown.data_point_name.endswith("_resolved")
        ):
            by_period[key][b] = p
    counts: dict[str, int] = defaultdict(int)
    seen_columns: set[tuple[str, str, date, int]] = set()
    for (grain, start, end), cells in by_period.items():
        ni = cells.get("net_income")
        cf_start = cf_start_value(structures, ni) if structures and ni else None
        for rec, members, reason in [
            *_check_period(
                cells, grain, start, end, printed, cf_start, structures, checks
            ),
            *_check_splits(cells, grain, end, structures),
        ]:
            if reason in (REASON, SPLIT_REASON):
                counts[rec["name"]] += 1
            else:  # one filing column's failed check counts once, however many cells it holds
                col = (rec["accession"], rec["check_id"], end, _qtrs(grain))
                if col not in seen_columns:
                    seen_columns.add(col)
                    counts[rec["name"]] += 1
            for p in members.values():
                p.checks.setdefault("identity", rec)
                if p.verdict == PROVEN:
                    p.verdict, p.reason_code = DISAGREE, reason
                    p.reason_text = (
                        f"identity {rec['name']} breaks: {rec['lhs']} vs {rec['rhs']} "
                        f"(diff {rec['diff']}, tolerance {rec['tolerance']})"
                        if reason in (REASON, SPLIT_REASON)
                        else f"the filing's own check {rec['check_id']} fails: {rec['lhs']} vs {rec['rhs']} "
                        f"(tolerance {rec['tolerance']})"
                    )
    return dict(counts)


# ================================================================ identity web over the shown export (2026-11-22)
# The same identities, judged over the SHOWN cells of a coverage export (top100-coverage.csv, or the resolver files
# read as cells) for every company x fiscal year, with the operands no export row carries (NCI, temporary equity,
# change in cash, FX, the CF start line, NCI income, income available to common, discrete quarters) read from the
# company's own filings in fsn.* (WEB_FACT_SQL, read-only). Each member cell carries its support: the automated
# draw checker's census outcome against the cited filing (AUTO_MATCH / AUTO_MISMATCH / NEEDS_READ) and the cell
# proof verdict. A BREAK names the members most likely wrong: AUTO_MISMATCH first, then members with neither a
# filing match nor a proof, then proof-only members; a member the filing's own fact matches is never the suspect.
# A break whose every member matches its filing fact is FILING_BREAK (the filing or the identity's operand set, not
# a shown value): reported, never opened. An EXACT identity that passes corroborates its one member the checker
# could not settle when every other member is AUTO_MATCH (draw_check.corroborate).

WEB_VERSION = "identity_web@1"
WEB_PASS, WEB_BREAK, WEB_FILING_BREAK = "PASS", "BREAK", "FILING_BREAK"
# identity names (the self-check reason and the report column)
ID_BS = "balance_sheet"
ID_CURRENT = "current_le_total"
ID_CF = "cash_flow"
ID_NI_CF = "net_income_cf"
ID_GP = "gross_profit"
ID_BAND = "operating_to_pretax_band"
ID_QUARTERS = "quarters_sum_to_year"
ID_EPS = "shares_x_eps"
WEB_IDENTITIES = (
    ID_BS,
    ID_CURRENT,
    ID_CF,
    ID_NI_CF,
    ID_GP,
    ID_BAND,
    ID_QUARTERS,
    ID_EPS,
)
# exact arithmetic of the filing (no slack beyond rounding): only these corroborate a cell
WEB_EXACT = frozenset({ID_BS, ID_CF, ID_NI_CF, ID_GP})

# support ranks: lower = more suspect
SUPPORT_RANK = {"AUTO_MISMATCH": 0, "none": 1, "proof": 2, "AUTO_MATCH": 9}

NCI_BS_TAGS = ("MinorityInterest", "NonredeemableNoncontrollingInterest")
CASH_CHANGE_INCL_FX = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecrease",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperationsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashPeriodIncreaseDecrease",
)
CASH_CHANGE_EXCL_FX = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
    "CashPeriodIncreaseDecreaseExcludingExchangeRateEffect",
)
FX_TAGS = (
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "EffectOfExchangeRateOnCashAndCashEquivalents",
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
    "EffectOfExchangeRateOnCash",
)
DISC_CF_TAGS = (
    "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
    "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
    "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
)
DISC_CF_TOTAL = "NetCashProvidedByUsedInDiscontinuedOperations"
# cash balances in the order the filing's own CF reconciles them (restricted cash per the filing: ASU 2016-18 total
# first, then cash and equivalents)
CASH_BALANCE_TAGS = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "CashAndCashEquivalentsAtCarryingValue",
    "Cash",
)
AVAIL_COMMON = {
    "basic": ("NetIncomeLossAvailableToCommonStockholdersBasic",),
    "diluted": (
        "NetIncomeLossAvailableToCommonStockholdersDiluted",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
    ),
}
QUARTER_DPS = (
    "revenue",
    "cost_of_revenue",
    "gross_profit",
    "operating_income",
    "income_before_tax",
    "net_income",
    "income_tax_expense",
)
QUARTER_SLACK = Decimal(
    "0.005"
)  # 10-Q quarters + a 10-K Q4: different vintages (recasts), 0.5% of the year
EPS_FALLBACK_SLACK = Decimal(
    "0.03"
)  # net income for income available to common: preferred / participating slack
WEB_TAGS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *NCI_BS_TAGS,
            EQUITY_INCL_NCI_TAG,
            "StockholdersEquity",
            *TEMP_EQUITY_TAGS,
            *LSE_TAGS,
            *CASH_CHANGE_INCL_FX,
            *CASH_CHANGE_EXCL_FX,
            *FX_TAGS,
            *DISC_CF_TAGS,
            DISC_CF_TOTAL,
            *CASH_BALANCE_TAGS,
            *sorted(NI_START_TAGS),
            *NCI_INCOME_TAGS,
            *AVAIL_COMMON["diluted"],
        )
    )
)
WEB_FLOOR = "2013-01-01"
WEB_FORMS = ("10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A", "20-F", "40-F")
# one read of the company's own filings: every undimensioned operand fact (and the shown flows' own tags, for the
# quarters), any duration; the CF statement's first lines
WEB_FACT_SQL = """
select f.accession, f.form, t.tag, v.ddate::text, v.qtrs, v.value, v.dcml, coalesce(v.uom, '')
from fsn.filing f
join fsn.value v on v.filing_id = f.id and coalesce(v.coreg, '') = '' and v.value is not null and v.qtrs in (0, 1, 3, 4)
join fsn.dim d on d.id = v.dim_id and d.segments = ''
join fsn.tag t on t.id = v.tag_id
where f.cik = lpad(ltrim(%(cik)s, '0'), 10, '0') and f.form = any(%(forms)s) and t.tag = any(%(tags)s)
  and v.ddate >= %(floor)s::date
"""
WEB_CF_LINE_SQL = """
select f.accession, t.tag, l.report, l.line
from fsn.filing f join fsn.line l on l.filing_id = f.id join fsn.tag t on t.id = l.tag_id
where f.cik = lpad(ltrim(%(cik)s, '0'), 10, '0') and f.form = any(%(forms)s) and l.stmt = 'CF' and l.line <= 8
"""


class WebFacts:
    """The operand facts of one company (WEB_FACT_SQL rows), indexed by (accession, tag, qtrs); the form of each
    accession; the first line of each filing's cash-flow statement."""

    def __init__(
        self,
        rows: Sequence[tuple[Any, ...]],
        cf_lines: Sequence[tuple[Any, ...]] = (),
    ):
        self.by: dict[tuple[str, str, int], list[tuple[date, Decimal, int]]] = (
            defaultdict(list)
        )
        self.form: dict[str, str] = {}
        self.own_end: dict[str, date] = {}
        for acc, form, tag, dd, q, val, dcml, uom in rows:
            toks = [
                t
                for t in str(uom or "").replace("/", " ").split()
                if len(t) == 3 and t.isupper()
            ]
            if any(t != "USD" for t in toks):
                continue  # a fact in another currency is never a USD operand
            d = date.fromisoformat(str(dd)[:10])
            self.by[(acc, tag, int(q))].append(
                (d, Decimal(str(val)), 32767 if dcml is None else int(dcml))
            )
            self.form[acc] = form
            if int(q) in (0, 1, 4) and d > self.own_end.get(acc, date.min):
                self.own_end[acc] = d
        # the net-income line the cash-flow statement starts from: the first NI_START_TAGS line of the filing's
        # main (lowest-numbered) CF report; a beginning cash balance printed above it (AAPL) is skipped
        main: dict[str, int] = {}
        for acc, _tag, rep, _line in cf_lines:
            main[acc] = min(main.get(acc, int(rep)), int(rep))
        first: dict[str, tuple[int, str]] = {}
        for acc, tag, rep, line in cf_lines:
            if int(rep) != main[acc] or str(tag) not in NI_START_TAGS:
                continue
            if acc not in first or int(line) < first[acc][0]:
                first[acc] = (int(line), str(tag))
        self.cf_first = {a: k[1] for a, k in first.items()}

    def get(self, acc: str, tag: str, end: date, qtrs: int) -> Decimal | None:
        cand = [
            (abs((d - end).days), -dc, v)
            for d, v, dc in self.by.get((acc, tag, qtrs), ())
            if abs((d - end).days) <= 7
        ]
        return min(cand)[2] if cand else None

    def first(
        self, acc: str, tags: Sequence[str], end: date, qtrs: int
    ) -> tuple[str, Decimal] | None:
        for t in tags:
            v = self.get(acc, t, end, qtrs)
            if v is not None:
                return t, v
        return None

    def quarters(
        self, tag: str, start: date, end: date
    ) -> dict[str, list[tuple[date, Decimal]]]:
        """Discrete-quarter facts (qtrs 1) of a tag ending inside (start, end], per accession."""
        out: dict[str, list[tuple[date, Decimal]]] = defaultdict(list)
        for (acc, t, q), vals in self.by.items():
            if t != tag or q != 1:
                continue
            for d, v, _dc in vals:
                if start < d <= end + timedelta(days=7):
                    out[acc].append((d, v))
        return out


@dataclass(frozen=True)
class WebMember:
    data_point: str
    value: Decimal
    support: str  # AUTO_MATCH | AUTO_MISMATCH | proof | none


@dataclass(frozen=True)
class WebResult:
    identity: str
    fiscal_year: str
    status: str  # PASS | BREAK | FILING_BREAK
    members: tuple[WebMember, ...]
    lhs: Decimal
    rhs: Decimal
    tolerance: Decimal
    suspects: tuple[str, ...]
    detail: str

    @property
    def exact(self) -> bool:
        return self.identity in WEB_EXACT and "slack" not in self.detail

    def opens(self, dp: str) -> bool:
        """Does the break open this suspect? Always for an exact identity; for a banded one (pretax band, shares x
        EPS, quarters) only when the suspect has no proof or its filing fact differs: a proven cell that breaks only a
        band (CAT interest partly above operating income, DELL two-class EPS) goes to a read, not open."""
        sup = next((m.support for m in self.members if m.data_point == dp), "none")
        return self.status == WEB_BREAK and (self.exact or sup != "proof")

    def reason(self, dp: str) -> str:
        mem = ", ".join(f"{m.data_point}={m.value} [{m.support}]" for m in self.members)
        return (
            f"identity {self.identity} breaks FY{self.fiscal_year}: {self.lhs} vs {self.rhs} "
            f"(diff {self.lhs - self.rhs}, tolerance {self.tolerance}); {dp} is the member no filing fact or proof "
            f"supports; members {mem}; {self.detail}"
        )


def support_of(auto: str | None, proof: str | None) -> str:
    """A member's support: the draw checker's census outcome decides when it settled the cell; else the proof."""
    if auto in ("AUTO_MATCH", "AUTO_MISMATCH"):
        return auto
    return "proof" if (proof or "").upper() == "PROVEN" else "none"


def _suspects(
    members: Sequence[WebMember], among: Sequence[str] | None = None
) -> tuple[str, ...]:
    pool = [m for m in members if among is None or m.data_point in among]
    pool = [m for m in pool if m.support != "AUTO_MATCH"] or (
        [m for m in members if m.support != "AUTO_MATCH"] if among is not None else []
    )
    if not pool:
        return ()
    best = min(SUPPORT_RANK[m.support] for m in pool)
    return tuple(m.data_point for m in pool if SUPPORT_RANK[m.support] == best)


def _result(
    identity: str,
    fy: str,
    members: Sequence[WebMember],
    lhs: Decimal,
    rhs: Decimal,
    tol: Decimal,
    ok: bool,
    detail: str,
    among: Sequence[str] | None = None,
) -> WebResult:
    if ok:
        return WebResult(
            identity, fy, WEB_PASS, tuple(members), lhs, rhs, tol, (), detail
        )
    sus = _suspects(members, among)
    return WebResult(
        identity,
        fy,
        WEB_BREAK if sus else WEB_FILING_BREAK,
        tuple(members),
        lhs,
        rhs,
        tol,
        sus,
        detail,
    )


def _close(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= tol


def web_period(
    fy: str,
    cells: dict[str, Any],
    support: dict[str, str],
    wf: WebFacts,
) -> list[WebResult]:
    """Every identity of one company fiscal year. cells: data point -> shown cell (attributes value, accession,
    period_end, tag, parts); support: data point -> support_of(...)."""
    out: list[WebResult] = []

    def mem(*dps: str) -> list[WebMember] | None:
        if not all(
            cells.get(d) is not None and cells[d].value is not None for d in dps
        ):
            return None
        return [WebMember(d, cells[d].value, support.get(d, "none")) for d in dps]

    def end_of(dp: str) -> date | None:
        c = cells.get(dp)
        pe = (c.period_end if c is not None else "") or ""
        return date.fromisoformat(pe[:10]) if pe else None

    def acc_of(*dps: str) -> str:
        return next(
            (
                cells[d].accession
                for d in dps
                if cells.get(d) is not None and cells[d].accession
            ),
            "",
        )

    # 1. assets = liabilities + equity + NCI + temporary equity (the operands from the liabilities' filing)
    m = mem("total_assets", "total_liabilities", "stockholders_equity")
    if m and (end := end_of("total_assets")):
        a, li, e = (x.value for x in m)
        acc = acc_of("total_liabilities", "total_assets")
        nci = wf.first(acc, NCI_BS_TAGS, end, 0)
        incl = wf.get(acc, EQUITY_INCL_NCI_TAG, end, 0)
        se = wf.get(acc, "StockholdersEquity", end, 0)
        nci_v = (
            nci[1]
            if nci
            else (incl - se if incl is not None and se is not None else None)
        )
        temp = wf.get(acc, TEMP_EQUITY_TOTAL_TAG, end, 0)
        if temp is None:
            parts = [
                v
                for t in TEMP_EQUITY_PART_TAGS
                if (v := wf.get(acc, t, end, 0)) is not None
            ]
            temp = sum(parts, Decimal(0)) if parts else None
        others = [
            v
            for t in TEMP_EQUITY_OTHER_TAGS
            if (v := wf.get(acc, t, end, 0)) is not None
        ]
        adds = [x for x in (nci_v, temp) if x is not None]
        opts = {Decimal(0)}
        for x in [*adds, *others]:
            opts |= {o + x for o in opts}
        if incl is not None:
            opts.add(
                incl - e
            )  # the shown equity is the parent's, the filing's total equity holds NCI
        r = a - li - e
        tol = tolerance([a, li, e, *adds, *others])
        ok = any(_close(r, o, tol) for o in opts)
        lse = wf.first(acc, LSE_TAGS, end, 0)
        among: list[str] | None = None
        if not ok and lse is not None:
            # the filing's own L&SE localises the break: assets off the face total, or the other side
            among = (
                ["total_assets"]
                if not _close(a, lse[1], tolerance([a, lse[1]]))
                else ["total_liabilities", "stockholders_equity"]
            )
        bs_best = min(opts, key=lambda o: abs(r - o))
        out.append(
            _result(
                ID_BS,
                fy,
                m,
                a,
                li + e + bs_best,
                tol,
                ok,
                f"filing {acc}: NCI {nci_v}, temporary equity {temp}, other mezzanine {others or '-'}"
                + (f", {lse[0]} {lse[1]}" if lse else ""),
                among,
            )
        )
    # 2. current assets <= total assets; current liabilities <= total liabilities
    for cur, tot in (
        ("current_assets", "total_assets"),
        ("current_liabilities", "total_liabilities"),
    ):
        m = mem(cur, tot)
        if m:
            c, t = m[0].value, m[1].value
            tol = tolerance([c, t])
            out.append(
                _result(ID_CURRENT, fy, m, c, t, tol, c <= t + tol, f"{cur} <= {tot}")
            )
    # 3. CFO + CFI + CFF (+ FX, + discontinued) = change in cash, the filing's own change line or balances
    m = mem("cfo", "cash_flow_investing", "cash_flow_financing")
    if m and (end := end_of("cfo")):
        s = sum((x.value for x in m), Decimal(0))
        acc = acc_of("cfo")
        fx = wf.first(acc, FX_TAGS, end, 4)
        disc = [v for t in DISC_CF_TAGS if (v := wf.get(acc, t, end, 4)) is not None]
        dtot = wf.get(acc, DISC_CF_TOTAL, end, 4)
        disc_opts = (
            {Decimal(0)}
            | ({sum(disc, Decimal(0))} if disc else set())
            | ({dtot} if dtot is not None else set())
        )
        chg_incl = wf.first(acc, CASH_CHANGE_INCL_FX, end, 4)
        chg_excl = wf.first(acc, CASH_CHANGE_EXCL_FX, end, 4)
        targets: list[tuple[str, Decimal, bool]] = []  # (source, change, includes FX)
        if chg_incl:
            targets.append((chg_incl[0], chg_incl[1], True))
        if chg_excl:
            targets.append((chg_excl[0], chg_excl[1], False))
        if not targets:
            prior = end - timedelta(days=365)
            for bt in CASH_BALANCE_TAGS:
                e1, e0 = wf.get(acc, bt, end, 0), wf.get(acc, bt, prior, 0)
                if e1 is not None and e0 is not None:
                    targets.append((f"{bt} {e1} - {e0}", e1 - e0, True))
                    break
        if targets:
            fx_v = fx[1] if fx else Decimal(0)
            extra = [fx_v, *disc] + ([dtot] if dtot is not None else [])
            tol = tolerance([*(x.value for x in m), *(t[1] for t in targets), *extra])
            cf_best: tuple[Decimal, Decimal, str] | None = None
            for src, chg, with_fx in targets:
                for dv in disc_opts:
                    for f in {fx_v, Decimal(0)} if with_fx else {Decimal(0)}:
                        lhs = s + f + dv
                        if cf_best is None or abs(lhs - chg) < abs(
                            cf_best[0] - cf_best[1]
                        ):
                            cf_best = (lhs, chg, f"{src}; FX {f}; discontinued {dv}")
            assert cf_best is not None
            lhs, chg, why = cf_best
            out.append(
                _result(
                    ID_CF,
                    fy,
                    m,
                    lhs,
                    chg,
                    tol,
                    _close(lhs, chg, tol),
                    f"filing {acc}: {why}",
                )
            )
    # 4. net income on the IS = the CF starting line (ProfitLoss less the printed NCI income)
    m = mem("net_income")
    if m and (ni_end := end_of("net_income")):
        acc = acc_of("net_income", "cfo")
        cf_tag = wf.cf_first.get(acc) or ""
        start_v = wf.get(acc, cf_tag, ni_end, 4) if cf_tag in NI_START_TAGS else None
        if cf_tag and start_v is not None:
            ni = m[0].value
            rhs: Decimal | None = start_v
            note = f"CF start {cf_tag} {start_v}"
            if cf_tag == "ProfitLoss":
                nci_inc = wf.first(acc, NCI_INCOME_TAGS, ni_end, 4)
                if nci_inc is not None:
                    rhs, note = (
                        start_v - nci_inc[1],
                        note + f" - {nci_inc[0]} {nci_inc[1]}",
                    )
                elif ni != start_v:
                    rhs = None  # NCI income not printed: parent vs total cannot be told apart
            if rhs is not None:
                tol = tolerance([ni, start_v])
                out.append(
                    _result(
                        ID_NI_CF,
                        fy,
                        m,
                        ni,
                        rhs,
                        tol,
                        _close(ni, rhs, tol),
                        f"filing {acc}: {note}",
                    )
                )
    # 5. gross profit = revenue - cost of revenue, all three shown
    m = mem("revenue", "cost_of_revenue", "gross_profit")
    if m:
        rv, cr, gp = (x.value for x in m)
        tol = tolerance([rv, cr, gp])
        out.append(
            _result(
                ID_GP,
                fy,
                m,
                rv - abs(cr),
                gp,
                tol,
                _close(rv - abs(cr), gp, tol),
                "revenue - cost of revenue",
            )
        )
    # 6. pretax - operating income = the band: other income (expense), net less the interest lines in the band
    m = mem("operating_income", "income_before_tax", "other_income_expense_net")
    if m:
        oi, pt, oie = (x.value for x in m)
        ie_m, ii_m = mem("interest_expense"), mem("interest_income")
        ie = abs(ie_m[0].value) if ie_m else None
        ii = ii_m[0].value if ii_m else None
        opts = {Decimal(0)}
        if ie is not None:
            opts.add(-ie)
        if ii is not None:
            opts |= {o + ii for o in list(opts)}
        r = pt - oi - oie
        tol = tolerance([oi, pt, oie] + [x for x in (ie, ii) if x is not None])
        band_best = min(opts, key=lambda o: abs(r - o))
        mm = m + (ie_m or []) + (ii_m or [])
        out.append(
            _result(
                ID_BAND,
                fy,
                mm,
                pt - oi,
                oie + band_best,
                tol,
                any(_close(r, o, tol) for o in opts),
                f"pretax - operating income = other income (expense), net {oie} + interest effect {band_best}",
            )
        )
    # 7. quarters sum to the year: the 10-K's own quarterly table (one vintage), else the 10-Qs' quarters + the
    # 10-K's Q4, at 0.5% slack
    for dp in QUARTER_DPS:
        m = mem(dp)
        qc = cells.get(dp)
        if not m or qc is None or qc.parts or not (qend := end_of(dp)):
            continue
        qtag = (qc.tag or "").split(":")[-1].strip()
        if not qtag:
            continue
        qacc = qc.accession
        qstart = qend - timedelta(days=371)
        qs = wf.quarters(qtag, qstart, qend)
        own = sorted({d: v for d, v in qs.get(qacc, [])}.items())
        q4 = next((v for d, v in own if abs((d - qend).days) <= 7), None)
        if q4 is None:
            continue
        fyv = m[0].value
        signs = (Decimal(1), Decimal(-1)) if is_fixed_positive_dp(dp) else (Decimal(1),)
        if len(own) == 4:
            vals = [v for _, v in own]
            total, slack, src = (
                sum(vals, Decimal(0)),
                Decimal(0),
                f"10-K {qacc} quarterly table",
            )
        else:
            picked: dict[date, Decimal] = {}
            for qa, lst in qs.items():
                if qa == qacc or wf.form.get(qa, "").split("/")[0] != "10-Q":
                    continue
                for d, v in lst:
                    if (
                        wf.own_end.get(qa) is not None
                        and abs((wf.own_end[qa] - d).days) <= 7
                    ):
                        picked.setdefault(
                            d, v
                        )  # the 10-Q whose own period is the quarter (original vintage)
            q13 = [v for d, v in sorted(picked.items()) if (qend - d).days > 45]
            if len(q13) != 3:
                continue
            vals = [*q13, q4]
            total, slack, src = (
                sum(vals, Decimal(0)),
                QUARTER_SLACK * abs(fyv),
                "10-Q quarters + 10-K Q4",
            )
        tol = tolerance([fyv, *vals]) + slack
        ok = any(_close(fyv, sg * total, tol) for sg in signs)
        out.append(
            _result(
                ID_QUARTERS,
                fy,
                m,
                fyv,
                total,
                tol,
                ok,
                f"{dp} {qtag}: {src} {' + '.join(str(v) for v in vals)}"
                + (" (slack 0.5%)" if slack else ""),
            )
        )
    # 8. weighted shares x EPS = income available to common (net income at 3% slack where the filing has none)
    for kind, eps_dp, sh_dp in (
        ("basic", "basic_eps", "weighted_basic_shares"),
        ("diluted", "diluted_eps", "weighted_diluted_shares"),
    ):
        m = mem(eps_dp, sh_dp)
        if not m or not (end := end_of(eps_dp)):
            continue
        eps, sh = m[0].value, m[1].value
        if sh <= 0:
            continue
        acc = acc_of(eps_dp)
        avail = wf.first(acc, AVAIL_COMMON[kind], end, 4)
        if avail is not None:
            num, slack, src = avail[1], Decimal(0), f"{avail[0]} {avail[1]} ({acc})"
        else:
            ni_m = mem("net_income")
            if not ni_m:
                continue
            m = m + ni_m
            num, slack, src = (
                ni_m[0].value,
                EPS_FALLBACK_SLACK * abs(ni_m[0].value),
                "net income (slack 3%)",
            )
        tol = Decimal("0.005") * sh + tolerance([num]) + slack
        out.append(
            _result(
                ID_EPS,
                fy,
                m,
                eps * sh,
                num,
                tol,
                _close(eps * sh, num, tol),
                f"{kind}: {eps_dp} x {sh_dp} vs {src}",
            )
        )
    return out


def is_fixed_positive_dp(dp: str) -> bool:
    from scrooner_pipeline.common.polarity import is_fixed_positive

    return is_fixed_positive(dp)


WEB_MEMBER_DPS = frozenset(
    {
        "total_assets", "total_liabilities", "stockholders_equity", "current_assets", "current_liabilities",
        "cfo", "cash_flow_investing", "cash_flow_financing", "net_income", "revenue", "cost_of_revenue",
        "gross_profit", "operating_income", "income_before_tax", "other_income_expense_net", "interest_expense",
        "interest_income", "income_tax_expense", "basic_eps", "diluted_eps", "weighted_basic_shares",
        "weighted_diluted_shares",
    }
)  # fmt: skip


def web_tags(cells: Iterable[Any]) -> list[str]:
    """WEB_TAGS plus the shown quarter-checked flows' own tags (one read per company)."""
    own = {
        (c.tag or "").split(":")[-1].strip()
        for c in cells
        if c.data_point in QUARTER_DPS and c.tag
    }
    return sorted(set(WEB_TAGS) | {t for t in own if t})


def identity_web(
    cells: Iterable[Any],
    wf: WebFacts,
    auto: dict[tuple[str, str], str] | None = None,
    proof: dict[tuple[str, str], str] | None = None,
) -> list[WebResult]:
    """Every identity over every fiscal year of one company's SHOWN cells. auto: (dp, fy) -> draw checker census
    outcome; proof: (dp, fy) -> proof verdict (the export's proof_verdict)."""
    auto, proof = auto or {}, proof or {}
    by_fy: dict[str, dict[str, Any]] = defaultdict(dict)
    for c in cells:
        if c.data_point in WEB_MEMBER_DPS and c.value is not None:
            by_fy[str(c.fiscal_year)][c.data_point] = c
    out: list[WebResult] = []
    for fy in sorted(by_fy):
        sup = {
            dp: support_of(auto.get((dp, fy)), proof.get((dp, fy))) for dp in by_fy[fy]
        }
        out += web_period(fy, by_fy[fy], sup, wf)
    return out


def web_corroborated(results: Iterable[WebResult]) -> dict[tuple[str, str], str]:
    """(dp, fy) -> evidence for cells an EXACT identity corroborates: the identity holds, the cell is its one member
    the draw checker did not settle, and every other member is AUTO_MATCH against the filing (the rest of the
    identity's operands are the filing's own facts)."""
    out: dict[tuple[str, str], str] = {}
    for r in results:
        if r.status != WEB_PASS or not r.exact:
            continue
        open_ = [m for m in r.members if m.support != "AUTO_MATCH"]
        if len(open_) != 1 or open_[0].support == "AUTO_MISMATCH":
            continue
        out.setdefault(
            (open_[0].data_point, r.fiscal_year),
            f"{WEB_VERSION} {r.identity} holds ({r.lhs} vs {r.rhs}, tolerance {r.tolerance}) with every other "
            f"member AUTO_MATCH; {r.detail}",
        )
    return out
