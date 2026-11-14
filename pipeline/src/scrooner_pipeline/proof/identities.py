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
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg

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


def related_tags(row: CheckRow, dp: str, tags: tuple[str, ...]) -> bool:
    """Is a cell (data point `dp`, source `tags`) a member of this check (named members, or the calc parent / one of
    its children)?"""
    if row.check_id in CHECK_MEMBERS:
        return dp in CHECK_MEMBERS[row.check_id]
    if row.check_id.startswith("calc:"):
        parent = row.check_id.split(":")[1]
        return any(t == parent or t in row.children for t in tags)
    return False


def related(row: CheckRow, dp: str, p: Proof) -> bool:
    """Is the served cell a member of this check (named members, or the calc parent / one of its children)?"""
    return related_tags(row, dp, p.shown.tags)


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
                lift = lifting_row(rows, r, dp, p.shown.tags)
                if lift is not None:
                    # the filing's own independent tie passes: the failed group is an incomplete calc linkbase
                    p.checks.setdefault("quarantine_lifted", []).append(
                        {
                            "failed_check": r.check_id,
                            "lifted_by": lift.check_id,
                            "accession": acc,
                            "lhs": str(r.lhs),
                            "rhs": str(r.rhs),
                            "tie_lhs": str(lift.lhs),
                            "tie_rhs": str(lift.rhs),
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
        for rec, members, reason in _check_period(
            cells, grain, start, end, printed, cf_start, structures, checks
        ):
            if reason == REASON:
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
                        if reason == REASON
                        else f"the filing's own check {rec['check_id']} fails: {rec['lhs']} vs {rec['rhs']} "
                        f"(tolerance {rec['tolerance']})"
                    )
    return dict(counts)
