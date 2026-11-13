"""Independent accounting identities over the SERVED values, a post-pass of the cell proof.

The cell proof judges one cell at a time against the filing the mapper picked. An identity judges the cells
TOGETHER, over what production serves, so a wrong filing choice or a wrong member shows up even when each cell
agrees with its own filing (MSFT FY2017: revenue 89,950 - cost of revenue 34,261 = 55,689, served gross profit
62,310). Identities:

  gross_profit     revenue - cost_of_revenue (- printed excise taxes between revenue and gross profit) =
                   gross_profit
  operating_income gross_profit - operating_expenses = operating_income; revenue - cost_of_revenue -
                   operating_expenses = operating_income when gross profit is not served
  balance_sheet    total_assets = total_liabilities + stockholders_equity (+ the printed non-controlling
                   interest when the served equity excludes it, + EVERY printed temporary-equity operand); where
                   the face prints LiabilitiesAndStockholdersEquity: total_assets = that total, and total_liabilities
                   + every top-level face line between it and that total = that total (the face operand set)
  cash_change      cfo + cfi + cff (+ printed discontinued flows, + the printed exchange-rate effect) = the printed
                   change in cash (annual only: the printed change line exists for years)
  net_income_cf    served net_income = the first line of the filing's cash-flow statement (annual), net of the
                   printed non-controlling income when that line is ProfitLoss

Tolerance is the members' rounding slack, half a unit per member (mapper/dqc_checks.tolerance: trailing zeros).
An identity is SKIPPED, never derived, when a member is not served, the filing does not present it
(NOT_PRESENTED), the company's map calls its line combined, a printed operand (fx, change in cash, NCI) is
absent, a member is itself derived and not printed (gross profit or total liabilities served as derived_not_printed,
mapper/derived_cells.py), or the period is a derived Q4 or a 6M/9M span (not a filed column). A failed identity marks each member cell that would otherwise be PROVEN as DISAGREE, reason
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
# excise taxes printed between revenue and gross profit (MO, PM): deducted in the gross-profit identity
EXCISE_TAGS = ("ExciseAndSalesTaxes", "ExciseTax")
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
            *NCI_EQUITY_TAGS,
            *TEMP_EQUITY_TAGS,
            *EXCISE_TAGS,
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


FilingKey = tuple[
    str, date | None, date
]  # same as PrintedKey; values are per accession


def load_printed_by_filing(
    conn: psycopg.Connection, company_id: int, floor: date
) -> dict[PrintedKey, dict[str, Decimal]]:
    """Discontinued-operations cash flows per FILING (accession -> value): the flows of one identity come from the
    SAME filing as the cfo/cfi/cff cells (a later filing may recast them: B5). Every copy counts here, not only the
    authoritative one; a filing with two distinct values for one key is dropped (never guess)."""
    out: dict[PrintedKey, dict[str, set[Decimal]]] = defaultdict(
        lambda: defaultdict(set)
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.tag, p.period_type, p.start_date, p.end_date, fl.accession_number, f.value
            from core.fact f
            join core.concept c on c.id = f.concept_id
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            where f.company_id = %s and not f.is_derived
              and c.taxonomy = 'us-gaap' and c.tag = any(%s) and p.end_date >= %s
            """,
            (company_id, list(DISCONTINUED_CF_TAGS), floor),
        )
        for tag, ptype, start, end, acc, value in cur.fetchall():
            out[(tag, start if ptype == "duration" else None, end)][acc].add(
                Decimal(value)
            )
    return {
        k: {a: next(iter(v)) for a, v in by.items() if len(v) == 1}
        for k, by in out.items()
    }


def not_printed(p: Proof) -> bool:
    """A cell that is no printed line: derived (a Q4 or a sum from a derived fact), or served with no source fact
    at all (mapper/derived_cells.py: gross profit = revenue - cost of revenue, total liabilities = L&SE - equity,
    family company_tag_map:derived_not_printed). An identity over it would only restate its own derivation."""
    s = p.shown
    return s.is_derived or (not s.source_fact_ids and not s.tags)


def _descendants(st: FilingStructure, tag: str) -> set[str]:
    seen: set[str] = set()
    todo = [tag]
    while todo:
        for child, _neg in st.calc_children.get(todo.pop(), []):
            if child not in seen:
                seen.add(child)
                todo.append(child)
    return seen


def face_between(
    structures: dict[str, FilingStructure] | None,
    members: dict[str, Proof],
    end: date,
) -> tuple[Decimal, list[tuple[str, Decimal]]] | None:
    """The balance sheet's own face operand set (B3): (printed LiabilitiesAndStockholdersEquity, [(tag, value) of
    the top-level face lines between total liabilities and that total]) in the column of `end`, from the filing the
    total_assets cell came from. A line that is a calc descendant of another line in the range (or of total
    liabilities) is a part of it, not an operand. None when the filing's face, the liabilities line or the total is
    not there (the identity falls back to the printed-fact operands)."""
    ta, tl = members["total_assets"], members["total_liabilities"]
    st = (structures or {}).get(ta.shown.accession or "")
    if st is None or len(tl.shown.tags) != 1:
        return None
    ddate = fsn_ddate(end)
    lines = st.lines_on("BS")
    ltag = tl.shown.tags[0]
    li = next((i for i, ln in enumerate(lines) if ln.tag == ltag), None)
    lse_i = next(
        (
            i
            for i, ln in enumerate(lines)
            if ln.tag in LSE_TAGS and li is not None and i > li
        ),
        None,
    )
    if li is None or lse_i is None:
        return None
    lse = st.value(lines[lse_i].tag, ddate, 0)
    if lse is None:
        return None
    tags = [
        t for t in dict.fromkeys(ln.tag for ln in lines[li + 1 : lse_i]) if t != ltag
    ]
    parts = set(_descendants(st, ltag))
    for t in tags:
        parts |= _descendants(st, t)
    equity = members["stockholders_equity"]
    out: list[tuple[str, Decimal]] = []
    for t in tags:
        if t in parts:
            continue
        v = st.value(t, ddate, 0)
        if v is None:
            continue
        # the served equity stands in for its own face line, so a wrong served equity is caught
        out.append((t, equity.shown.value if t in equity.shown.tags else v.value))
    return lse.value, out


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


def _disc_flow(
    printed: dict[PrintedKey, Decimal],
    by_filing: dict[PrintedKey, dict[str, Decimal]] | None,
    tag: str,
    accession: str,
    grain: str,
    start: date,
    end: date,
) -> Decimal | None:
    """A discontinued-operations cash flow from the SAME filing as the cfo/cfi/cff cells (B5): a later filing may
    recast it. A filing that does not print the flow gives none (never the other filing's value). Without per-filing
    data the unique printed value stands."""
    key = (tag, None if grain == "I" else start, end)
    if by_filing is not None and key in by_filing:
        return by_filing[key].get(accession)
    if by_filing:
        return None  # per-filing data loaded and this flow is in no filing
    return printed.get(key)


def _fact_operands(
    printed: dict[PrintedKey, Decimal],
    m: dict[str, Proof],
    grain: str,
    start: date,
    end: date,
) -> tuple[list[Decimal], dict[str, str]]:
    """Printed-fact operands of the balance sheet beyond total liabilities + equity: the non-controlling interest
    (unless the served equity already includes it) and EVERY temporary-equity operand present (B1/B2)."""
    extra: list[Decimal] = []
    detail: dict[str, str] = {}
    if EQUITY_INCL_NCI_TAG not in m["stockholders_equity"].shown.tags:
        for t in NCI_EQUITY_TAGS:
            x = _printed(printed, t, grain, start, end)
            if x is not None:
                extra.append(x)
                detail[t] = str(x)
    temp = [
        (t, x)
        for t in TEMP_EQUITY_TAGS
        if (x := _printed(printed, t, grain, start, end)) is not None
    ]
    if any(t == TEMP_EQUITY_TOTAL_TAG for t, _ in temp):
        temp = [(t, x) for t, x in temp if t not in TEMP_EQUITY_PART_TAGS]
    for t, x in temp:
        extra.append(x)
        detail[t] = str(x)
    return extra, detail


def _balance_sheet(
    m: dict[str, Proof],
    printed: dict[PrintedKey, Decimal],
    structures: dict[str, FilingStructure] | None,
    grain: str,
    start: date,
    end: date,
) -> tuple[dict[str, Any] | None, dict[str, Proof]]:
    """total_assets = L&SE where the face prints it, and L + the face operand set = L&SE (B3); otherwise (or when
    the face operand set does not tie but the printed-fact operands do) A = L + SE + every printed NCI and
    temporary-equity operand."""
    ta, tl, se = (
        m[k].shown.value
        for k in ("total_assets", "total_liabilities", "stockholders_equity")
    )
    extra, detail = _fact_operands(printed, m, grain, start, end)
    fact_rhs = tl + se + sum(extra, Decimal(0))
    face = face_between(structures, m, end)
    if face is None:
        return _evaluate("balance_sheet", m, ta, fact_rhs, extra, detail), m
    lse, lines = face
    rec = _evaluate(
        "balance_sheet",
        m,
        ta,
        lse,
        [lse],
        {"LiabilitiesAndStockholdersEquity": str(lse)},
    )
    if rec is not None:
        return rec, m
    face_detail = {
        "LiabilitiesAndStockholdersEquity": str(lse),
        **{t: str(x) for t, x in lines},
    }
    rec = _evaluate(
        "balance_sheet",
        m,
        tl + sum((x for _t, x in lines), Decimal(0)),
        lse,
        [x for _t, x in lines] + [lse],
        face_detail,
    )
    if (
        rec is not None
        and _evaluate("balance_sheet", m, ta, fact_rhs, extra, detail) is None
    ):
        return (
            None,
            m,
        )  # the printed-fact operands tie (a face without calc arcs may double count a part)
    return rec, m


def _check_period(
    cells: dict[str, Proof],
    grain: str,
    start: date,
    end: date,
    printed: dict[PrintedKey, Decimal],
    cf_start: tuple[str, Decimal] | None,
    printed_by_filing: dict[PrintedKey, dict[str, Decimal]] | None = None,
    structures: dict[str, FilingStructure] | None = None,
) -> list[tuple[dict[str, Any], dict[str, Proof]]]:
    """Every failed identity of one company period: (record, member proofs)."""
    out: list[tuple[dict[str, Any], dict[str, Proof]]] = []
    if grain == "Q" and (end - start).days > 100:
        return out  # a 6M/9M span is no filed column (C3)

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
            out.append((rec, m))

    if grain in ("FY", "Q"):
        m = get("revenue", "cost_of_revenue", "gross_profit")
        # excise taxes printed between revenue and gross profit (B4: MO, PM) are part of the face subtraction
        excise_by_tag = {
            t: x
            for t in EXCISE_TAGS
            if (x := _printed(printed, t, grain, start, end)) is not None
        }
        excise = sum(excise_by_tag.values(), Decimal(0))
        if m:
            add(
                _evaluate(
                    "gross_profit",
                    m,
                    v(m, "revenue") - v(m, "cost_of_revenue") - excise,
                    v(m, "gross_profit"),
                    [excise] if excise else None,
                    {t: str(x) for t, x in excise_by_tag.items()} or None,
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
            add(*_balance_sheet(m, printed, structures, grain, start, end))
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
                acc = (m["cfo"].shown.accession or "") if m else ""
                for t in DISCONTINUED_CF_TAGS:
                    x = _disc_flow(
                        printed, printed_by_filing, t, acc, grain, start, end
                    )
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
                        _evaluate(
                            "cash_change", m, change[1], rhs0, [*extra, change[1]]
                        )
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
    printed_by_filing: dict[PrintedKey, dict[str, Decimal]] | None = None,
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
        for rec, members in _check_period(
            cells, grain, start, end, printed, cf_start, printed_by_filing, structures
        ):
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
