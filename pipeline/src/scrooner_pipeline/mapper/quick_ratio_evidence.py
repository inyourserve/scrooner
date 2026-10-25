"""Inventory evidence for quick_ratio (rule ``quick_ratio.inventory_evidence@1``).

Commit f67a927 (2026-10-09) stopped nulling quick_ratio when inventory is absent from our facts: a MISSING inventory
became a ZERO, so quick ratio = current ratio for every inventory holder whose inventory we did not extract (NKE stored
2.075 vs 1.387, BA 1.138 vs 0.331, GAP 1.822 vs 1.109, AZO 0.890 vs 0.137, XOM 1.135 vs 0.847; Data Triage, 2026-10-24).

Verifier round 1 (2026-10-25) found 7 of 20 NULLs false: the evidence row describes the LATEST statements and was applied
to every past period, and inventory-like figures that are not a current face line (note figures, noncurrent line-fill)
blocked the zero. So the decision now rests on the PERIOD'S OWN balance sheet, read from its facts: a self-consistency
test of the current-assets total.

For a cell with no inventory fact at its date, with CA = current assets of that period:
 1. FOOTS WITHOUT INVENTORY: cash (+ short-term investments) + receivables + prepaid/other current assets (+ a few extra
    current lines), taken from the filing's own facts at that date, reproduce CA within 0.3% -> there is no room for an
    inventory line, so a zero is right whatever inventory-like figures exist (INSM, VAL, WES: the figures are notes or
    inside other current assets). No evidence needed.
 2. Otherwise, an inventory-like CURRENT fact at that date no larger than CA -> NULL ``inventory_like_tag_unmapped``
    (NKE: the 7,846 residual is InventoryFinishedGoodsNetOfReserves; BA, XOM, CP's materials and supplies).
 3. Otherwise, nothing explains the residual: the latest-statements evidence decides (line not presented -> zero;
    presented -> NULL ``inventory_presented_not_extracted``; no evidence -> NULL ``inventory_presence_unknown``).
Every NULL carries its reason; the rule never guesses a value.

``MATERIALS_AND_SUPPLIES_ARE_INVENTORY`` is a named switch: whether "materials and supplies" lines count as inventory
is a definition call for the Standardization Lead (CP 2017-03-31, XOM, LNT, WEC); one switch applies it everywhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from itertools import combinations
from typing import Any

RULE_ID = "quick_ratio.inventory_evidence@1"
EVIDENCE_POINT = "inventory"
MATERIALS_AND_SUPPLIES_ARE_INVENTORY = True

REASON_UNMAPPED = "incomplete:inventory_like_tag_unmapped"
REASON_PRESENTED = "incomplete:inventory_presented_not_extracted"
REASON_UNKNOWN = "incomplete:inventory_presence_unknown"

# words that make an inventory-named tag NOT a current balance-sheet inventory line (flows, reserves and noncurrent
# figures). "Other" is deliberately absent: OtherInventorySupplies is a line.
_EXCLUDED = (
    "Increase", "Decrease", "Reserve", "Writedown", "WriteDown", "Cost", "Purchase", "Valuation", "Adjustment",
    "Obsolescence", "Impairment", "Turnover", "Percentage", "Lifo", "LIFO", "Provision", "Expense", "Revenue", "Sale",
    "Change", "Payments", "Proceeds", "Realized", "Shares", "Number", "Days", "Commitment", "Excess", "Noncurrent",
    "LongTerm", "Deferred", "Recovery", "Writeoff", "WriteOff", "Policy", "Method", "Gain", "Loss", "Effect",
    "Contra", "Reclass", "Transfer", "Acquired", "Capitalized", "Held", "Financing", "LineFill",
)  # fmt: skip


def is_inventory_like(tag: str) -> bool:
    """A balance-sheet inventory line ("...NetOfReserves" lines are lines; reserves on their own are not)."""
    t = tag.replace("NetOfReserves", "").replace("NetOfReserve", "")
    named = "nventor" in t or (
        MATERIALS_AND_SUPPLIES_ARE_INVENTORY and "MaterialsSupplies" in t
    )
    return named and not any(w in t for w in _EXCLUDED)


# Current-asset lines used to foot the current-assets total (us-gaap tags, instant facts of the period's own filing).
CASH_TAGS = (
    "CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsAndShortTermInvestments",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash",
)  # fmt: skip
STI_TAGS = (
    "ShortTermInvestments", "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
    "DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent", "AvailableForSaleSecuritiesCurrent",
    "HeldToMaturitySecuritiesCurrent",
)  # fmt: skip
RECEIVABLE_TAGS = (
    "AccountsReceivableNetCurrent", "ReceivablesNetCurrent", "AccountsAndOtherReceivablesNetCurrent",
)  # fmt: skip
OTHER_OPTIONS = (  # alternative ways the prepaid / other line is filed
    ("PrepaidExpenseAndOtherAssetsCurrent",), ("OtherAssetsCurrent",), ("OtherAssetsCurrent", "PrepaidExpenseCurrent"),
    ("PrepaidExpenseCurrent",), ("PrepaidExpenseCurrent", "OtherAssetsCurrent"),
)  # fmt: skip
EXTRA_TAGS = (
    "ContractWithCustomerAssetNetCurrent", "NontradeReceivablesCurrent", "DeferredTaxAssetsNetCurrent",
    "AssetsHeldForSaleCurrent", "IncomeTaxesReceivable", "RestrictedCashAndCashEquivalentsAtCarryingValue",
    "DerivativeAssetsCurrent", "NotesAndLoansReceivableNetCurrent", "DueFromRelatedPartiesCurrent",
    "RestrictedCashCurrent", "ReceivablesFromCustomers", "InterestReceivableCurrent", "OtherReceivablesNetCurrent",
    "ShortTermInvestmentsAndOtherCurrentAssets", "AvailableForSaleSecuritiesEquitySecuritiesCurrent",
    "EquitySecuritiesFvNiCurrent", "TradingSecuritiesCurrent", "OtherAssetsMiscellaneousCurrent",
)  # fmt: skip
CURRENT_ASSETS_TAG = "AssetsCurrent"
FOOTING_TAGS = frozenset(
    (*CASH_TAGS, *STI_TAGS, *RECEIVABLE_TAGS, *EXTRA_TAGS, CURRENT_ASSETS_TAG)
    + tuple(t for o in OTHER_OPTIONS for t in o)
)  # fmt: skip
FOOT_TOLERANCE = Decimal("0.003")


def _unit(x: Decimal) -> Decimal:
    n = abs(x)
    unit = Decimal(1)
    if n == n.to_integral_value() and n != 0:
        while unit < Decimal(10) ** 6 and n % (unit * 10) == 0:
            unit *= 10
    return unit


def foots_without_inventory(current_assets: Decimal, lines: dict[str, Decimal]) -> bool:
    """True when the period's own current-asset lines (no inventory) reproduce the current-assets total."""
    if current_assets <= 0:
        return False
    tol = FOOT_TOLERANCE * current_assets + min(
        2 * _unit(current_assets), current_assets * Decimal("0.002")
    )  # rounding of printed lines, capped
    cash_tag = next((t for t in CASH_TAGS if t in lines), None)
    cash = lines[cash_tag] if cash_tag else Decimal(0)
    # the combined "cash and short-term investments" line already holds the investments
    sti = Decimal(0)
    if cash_tag != "CashCashEquivalentsAndShortTermInvestments":
        sti = sum((lines[t] for t in STI_TAGS if t in lines), Decimal(0))
    recv = next((lines[t] for t in RECEIVABLE_TAGS if t in lines), Decimal(0))
    base = cash + sti + recv
    extras = [lines[t] for t in EXTRA_TAGS if t in lines]
    others = [
        sum((lines[t] for t in opt if t in lines), Decimal(0)) for opt in OTHER_OPTIONS
    ] + [Decimal(0)]
    for other in others:
        for n in range(len(extras) + 1):
            for combo in combinations(extras, n):
                if abs(current_assets - (base + other + sum(combo, Decimal(0)))) <= tol:
                    return True
    return False


@dataclass(frozen=True)
class Context:
    """line_present: the latest-statements evidence (True presented / False not presented / None unknown);
    lines_by_date: per balance-sheet date, the footing lines and the inventory-like current facts of that period
    (tag -> value)."""

    line_present: bool | None
    lines_by_date: dict[date, dict[str, Decimal]] = field(default_factory=dict)
    inventory_like: dict[date, dict[str, Decimal]] = field(default_factory=dict)


def inventory_missing_reason(
    ctx: Context, end: date, current_assets: Decimal | None = None
) -> str | None:
    """Why a quick_ratio cell with NO inventory fact at ``end`` must be NULL, or None when a zero is safe."""
    lines = ctx.lines_by_date.get(end, {})
    ca = current_assets if current_assets is not None else lines.get(CURRENT_ASSETS_TAG)
    if ca is not None and foots_without_inventory(ca, lines):
        return None  # no room for an inventory line in this period's own balance sheet
    like = ctx.inventory_like.get(end, {})
    if any(0 < v <= (ca if ca is not None else v) for v in like.values()):
        return REASON_UNMAPPED
    if ctx.line_present is False:
        return None
    if ctx.line_present is True:
        return REASON_PRESENTED
    return REASON_UNKNOWN


def load_inventory_concept_ids(conn: Any) -> tuple[list[int], set[int]]:
    """(unmapped inventory-like core.concept ids, mapped inventory concept ids)."""
    with conn.cursor() as cur:
        cur.execute(
            """select m.concept_id from analytics.concept_mapping m
               join analytics.canonical_concept cc on cc.id = m.canonical_concept_id where cc.name = %s""",
            (EVIDENCE_POINT,),
        )
        mapped = {r[0] for r in cur.fetchall()}
        cur.execute(
            "select id, tag from core.concept where taxonomy = 'us-gaap' and (tag ilike %s or tag ilike %s)",
            ("%nventor%", "%MaterialsSupplies%"),
        )
        like = [
            i for i, t in cur.fetchall() if is_inventory_like(t) and i not in mapped
        ]
    return like, mapped


def load_context(
    conn: Any, company_id: int, like_ids: list[int] | None = None
) -> Context:
    if like_ids is None:
        like_ids, _ = load_inventory_concept_ids(conn)
    with conn.cursor() as cur:
        cur.execute(
            "select line_present from analytics.company_filing_line_evidence where company_id = %s and data_point = %s",
            (company_id, EVIDENCE_POINT),
        )
        row = cur.fetchone()
        lines: dict[date, dict[str, Decimal]] = {}
        like: dict[date, dict[str, Decimal]] = {}
        cur.execute(
            """select distinct on (p.end_date, k.tag) p.end_date, k.tag, f.value
               from core.fact f join core.period p on p.id = f.period_id join core.concept k on k.id = f.concept_id
               where f.company_id = %s and p.period_type = 'instant' and k.taxonomy = 'us-gaap'
                 and (k.tag = any(%s) or f.concept_id = any(%s))
               order by p.end_date, k.tag, f.is_authoritative desc, f.id desc""",
            (company_id, sorted(FOOTING_TAGS), like_ids or [0]),
        )
        for end, tag, value in cur.fetchall():
            if tag in FOOTING_TAGS:
                lines.setdefault(end, {})[tag] = value
            else:
                like.setdefault(end, {})[tag] = value
    return Context(None if row is None else row[0], lines, like)


@dataclass
class PlannedCell:
    company_id: int
    cik: str
    period_end: str
    period_label: str
    stored: str
    new: str | None  # always None: the value cannot be recomputed without the inventory
    reason: str
    current_ratio: str | None
    equals_current_ratio: bool


def plan_quick_ratio(
    conn: Any, company_ids: list[int], chunk: int = 100
) -> list[PlannedCell]:
    """Read-only dry run: stored quick_ratio cells that have a value although NO inventory fact exists at their date
    (the cells f67a927 turned into current ratio) and that the evidence rule would turn into NULL."""
    from decimal import Decimal

    out: list[PlannedCell] = []
    like_ids, _ = load_inventory_concept_ids(conn)
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.metric_definition where metric_name = 'quick_ratio'"
        )
        qr = cur.fetchone()[0]
        cur.execute(
            "select id from analytics.metric_definition where metric_name = 'current_ratio'"
        )
        cr = cur.fetchone()[0]
        cur.execute(
            "select id from analytics.canonical_concept where name = %s",
            (EVIDENCE_POINT,),
        )
        inv_concept = cur.fetchone()[0]
        cur.execute(
            "select id, cik from core.company where id = any(%s)", (company_ids,)
        )
        cik_of = dict(cur.fetchall())
    for i in range(0, len(company_ids), chunk):
        part = company_ids[i : i + chunk]
        with conn.cursor() as cur:
            cur.execute(
                """select company_id, period_end, period_label, value from analytics.metric_value
                   where company_id = any(%s) and metric_definition_id = %s and value is not null
                     and period_label <> 'TTM'""",
                (part, qr),
            )
            stored = cur.fetchall()
            cur.execute(
                """select company_id, period_end, value from analytics.metric_value
                   where company_id = any(%s) and metric_definition_id = %s and value is not null
                     and period_label <> 'TTM'""",
                (part, cr),
            )
            current = {(c, e): v for c, e, v in cur.fetchall()}
            cur.execute(
                """select cf.company_id, p.end_date from analytics.canonical_fact cf
                   join core.period p on p.id = cf.period_id
                   where cf.company_id = any(%s) and cf.canonical_concept_id = %s and p.period_type = 'instant'""",
                (part, inv_concept),
            )
            have = set(cur.fetchall())
        ctx = {cid: load_context(conn, cid, like_ids) for cid in {s[0] for s in stored}}
        for cid, end, label, value in stored:
            if (cid, end) in have:
                continue
            reason = inventory_missing_reason(ctx[cid], end)
            if reason is None:
                continue
            cur_ratio = current.get((cid, end))
            equal = cur_ratio is not None and abs(
                Decimal(value) - Decimal(cur_ratio)
            ) <= Decimal("0.0005")
            out.append(
                PlannedCell(cid, cik_of[cid], str(end), label, str(value), None, reason,
                            None if cur_ratio is None else str(cur_ratio), equal)
            )  # fmt: skip
    return out
