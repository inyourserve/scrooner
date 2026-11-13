"""Independent accounting identities over the SERVED values, a post-pass of the cell proof.

The cell proof judges one cell at a time against the filing the mapper picked. An identity judges the cells
TOGETHER, over what production serves, so a wrong filing choice or a wrong member shows up even when each cell
agrees with its own filing (MSFT FY2017: revenue 89,950 - cost of revenue 34,261 = 55,689, served gross profit
62,310). Identities:

  gross_profit     revenue - cost_of_revenue = gross_profit
  operating_income gross_profit - operating_expenses = operating_income; revenue - cost_of_revenue -
                   operating_expenses = operating_income when gross profit is not served
  balance_sheet    total_assets = total_liabilities + stockholders_equity (+ the printed non-controlling
                   interest when the served equity excludes it, + printed temporary equity); the DQC4-05 tag set
  cash_change      cfo + cfi + cff (+ printed discontinued flows, + the printed exchange-rate effect) = the printed
                   change in cash (annual only: the printed change line exists for years)
  net_income_cf    served net_income = the first line of the filing's cash-flow statement (annual), net of the
                   printed non-controlling income when that line is ProfitLoss

Tolerance is the members' rounding slack, half a unit per member (mapper/dqc_checks.tolerance: trailing zeros).
An identity is SKIPPED, never derived, when a member is not served, the filing does not present it
(NOT_PRESENTED), the company's map calls its line combined, or a printed operand (fx, change in cash, NCI) is
absent. A failed identity marks each member cell that would otherwise be PROVEN as DISAGREE, reason
identity_break, with checks.identity = {name, members, lhs, rhs, diff, tolerance}.
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

PeriodKey = tuple[str, date, date]  # (grain, start, end)
PrintedKey = tuple[str, date | None, date]  # (tag, start for durations, end)

NCI_EQUITY_TAG = "MinorityInterest"
EQUITY_INCL_NCI_TAG = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
)
TEMP_EQUITY_GROUPS: tuple[tuple[str, ...], ...] = (
    (
        "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
    ),
    (
        "TemporaryEquityCarryingAmountAttributableToParent",
        "RedeemableNoncontrollingInterestEquityCarryingAmount",
    ),
)
DISCONTINUED_CF_TAGS = (
    "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
    "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
    "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
)
FX_TAGS = (
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "EffectOfExchangeRateOnCashAndCashEquivalents",
    "EffectOfExchangeRateOnCash",
)
# the printed change in cash, with the exchange-rate effect
CHANGE_TAGS: tuple[str, ...] = (
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
    "CashAndCashEquivalentsPeriodIncreaseDecrease",
    "CashPeriodIncreaseDecrease",
)
NI_START_TAGS = frozenset(
    {"NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"}
)
NCI_INCOME_TAGS = (
    "NetIncomeLossAttributableToNoncontrollingInterest",
    "NetIncomeLossAttributableToRedeemableNoncontrollingInterest",
)

PRINTED_TAGS: tuple[str, ...] = tuple(
    dict.fromkeys(
        [
            NCI_EQUITY_TAG,
            *[t for g in TEMP_EQUITY_GROUPS for t in g],
            *DISCONTINUED_CF_TAGS,
            *FX_TAGS,
            *CHANGE_TAGS,
            *NCI_INCOME_TAGS,
        ]
    )
)

IDENTITY_NAMES = (
    "gross_profit",
    "operating_income",
    "balance_sheet",
    "cash_change",
    "net_income_cf",
)


def base_name(name: str) -> str:
    for suffix in ("_sanity_resolved", "_resolved"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def load_printed(
    conn: psycopg.Connection, company_id: int, floor: date
) -> dict[PrintedKey, Decimal]:
    """Printed (non-derived, authoritative) values of the operand tags that are not served as cells: NCI,
    temporary equity, discontinued cash flows, exchange-rate effect, change in cash, NCI income. A key with two
    distinct values is ambiguous and dropped (never guess an operand)."""
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


def _printed(
    printed: dict[PrintedKey, Decimal], tag: str, grain: str, start: date, end: date
) -> Decimal | None:
    return printed.get((tag, None if grain == "I" else start, end))


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
    """The identity record when lhs and rhs differ beyond the operands' rounding slack, else None."""
    tol = tolerance([p.shown.value for p in members.values()] + list(extra or []))
    if abs(lhs - rhs) <= tol:
        return None
    rec: dict[str, Any] = {
        "name": name,
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
) -> list[tuple[dict[str, Any], dict[str, Proof]]]:
    """Every failed identity of one company period: (record, member proofs)."""
    out: list[tuple[dict[str, Any], dict[str, Proof]]] = []

    def get(*dps: str) -> dict[str, Proof] | None:
        got = {d: cells.get(d) for d in dps}
        if all(_usable(p) for p in got.values()):
            return got  # type: ignore[return-value]
        return None

    def v(m: dict[str, Proof], dp: str) -> Decimal:
        return m[dp].shown.value

    def add(rec: dict[str, Any] | None, m: dict[str, Proof]) -> None:
        if rec is not None:
            out.append((rec, m))

    if grain in ("FY", "Q"):
        m = get("revenue", "cost_of_revenue", "gross_profit")
        if m:
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
            if m:
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
        if m:
            extra: list[Decimal] = []
            detail: dict[str, str] = {}
            if EQUITY_INCL_NCI_TAG not in m["stockholders_equity"].shown.tags:
                nci = _printed(printed, NCI_EQUITY_TAG, grain, start, end)
                if nci is not None:
                    extra.append(nci)
                    detail[NCI_EQUITY_TAG] = str(nci)
            for group in TEMP_EQUITY_GROUPS:
                got = [
                    (t, x)
                    for t in group
                    if (x := _printed(printed, t, grain, start, end)) is not None
                ]
                if got:
                    for t, x in got:
                        extra.append(x)
                        detail[t] = str(x)
                    break
            rhs = (
                v(m, "total_liabilities")
                + v(m, "stockholders_equity")
                + sum(extra, Decimal(0))
            )
            add(
                _evaluate("balance_sheet", m, v(m, "total_assets"), rhs, extra, detail),
                m,
            )
    if grain == "FY":
        m = get("cfo", "cash_flow_investing", "cash_flow_financing")
        if m:
            change = next(
                (
                    (t, x)
                    for t in CHANGE_TAGS
                    if (x := _printed(printed, t, grain, start, end)) is not None
                ),
                None,
            )
            fx = next(
                (
                    (t, x)
                    for t in FX_TAGS
                    if (x := _printed(printed, t, grain, start, end)) is not None
                ),
                None,
            )
            # the printed change includes the exchange-rate effect: a missing effect line is never assumed zero
            if change is not None and fx is not None:
                extra = [fx[1]]
                detail = {change[0]: str(change[1]), fx[0]: str(fx[1])}
                for t in DISCONTINUED_CF_TAGS:
                    x = _printed(printed, t, grain, start, end)
                    if x is not None:
                        extra.append(x)
                        detail[t] = str(x)
                rhs = sum((p.shown.value for p in m.values()), Decimal(0)) + sum(
                    extra, Decimal(0)
                )
                rec = _evaluate(
                    "cash_change", m, change[1], rhs, [*extra, change[1]], detail
                )
                if rec is not None:
                    # a filer may tag the change BEFORE the exchange-rate effect with the including tag (HD, 3 of 3
                    # breaks): equal to the flows alone is then the same printed line, not a break
                    rhs0 = rhs - fx[1]
                    if (
                        _evaluate("cash_change", m, change[1], rhs0, [*extra, change[1]])
                        is None
                    ):
                        rec = None
                add(rec, m)
        m = get("net_income")
        if m and cf_start is not None:
            tag, start_v = cf_start
            ni = v(m, "net_income")
            extra = []
            detail = {tag: str(start_v)}
            rhs = start_v
            nci_inc: Decimal | None = Decimal(0)
            if tag == "ProfitLoss":
                nci_inc = next(
                    (
                        x
                        for t in NCI_INCOME_TAGS
                        if (x := _printed(printed, t, grain, start, end)) is not None
                    ),
                    None,
                )
                if nci_inc is None and ni == start_v:
                    nci_inc = Decimal(0)
            if nci_inc is not None:  # NCI income not printed: parent vs total cannot be told apart
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
) -> dict[str, int]:
    """Post-pass over a company's proofs (in place). Returns {identity name: failed identities}."""
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
    for (grain, start, end), cells in by_period.items():
        ni = cells.get("net_income")
        cf_start = cf_start_value(structures, ni) if structures and ni else None
        for rec, members in _check_period(cells, grain, start, end, printed, cf_start):
            counts[rec["name"]] += 1
            for p in members.values():
                p.checks.setdefault("identity", rec)
                if p.verdict == PROVEN:
                    p.verdict, p.reason_code = DISAGREE, REASON
                    p.reason_text = (
                        f"identity {rec['name']} breaks: {rec['lhs']} vs {rec['rhs']} "
                        f"(diff {rec['diff']}, tolerance {rec['tolerance']})"
                    )
    return dict(counts)
