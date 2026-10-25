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
 3. Otherwise, nothing in our stored lines explains the residual: THIS period's own balance sheet decides
    (``Context.face_by_date``, read per accession from the FSDS presentation rows, ``quick_ratio_face.py``):
    an inventory line shown -> NULL ``inventory_presented_not_extracted``; the statement shows none -> the zero stands;
    the statement is UNAVAILABLE -> the stored value is KEPT and counted as kept-unverified (never NULLed on a guess,
    never decided from the latest statements: BBIO, SWX, TGTX, IOVA, DVN, GOOG, T, MP, RGLD ... had no inventory line).
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
# Founder ruling 2026-10-25: the quick ratio keeps its locked formula; where a current materials-and-supplies face line
# exists the figure is hidden with this reason (the formula cannot say whether the line is inventory).
REASON_MATERIALS = "incomplete:materials_supplies_line_present"

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
    materials_supplies: dict[date, Decimal] = field(
        default_factory=dict
    )  # MaterialsSuppliesAndOther-type facts, per date
    # per balance-sheet date: does that period's OWN balance sheet show an inventory line (True / False)? A date that
    # is absent means the face is UNAVAILABLE
    face_by_date: dict[date, bool] = field(default_factory=dict)
    # InventoryRawMaterialsAndSupplies-type facts (a sub-line of inventory, not a materials-and-supplies line), per date
    supplies_subline: dict[date, Decimal] = field(default_factory=dict)
    accession_by_date: dict[date, str] = field(
        default_factory=dict
    )  # the filing whose AssetsCurrent fact is the period's


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
    if ctx.face_by_date.get(end) is True:
        return REASON_PRESENTED
    # the period's own statement shows no inventory line (False), or is unavailable: the stored value is kept
    return None


def face_unavailable(
    ctx: Context, end: date, current_assets: Decimal | None = None
) -> bool:
    """True when the zero is KEPT only because the period's own statement could not be read (unverified)."""
    lines = ctx.lines_by_date.get(end, {})
    ca = current_assets if current_assets is not None else lines.get(CURRENT_ASSETS_TAG)
    if ca is not None and foots_without_inventory(ca, lines):
        return False
    like = ctx.inventory_like.get(end, {})
    if any(0 < v <= (ca if ca is not None else v) for v in like.values()):
        return False
    return end not in ctx.face_by_date


def materials_supplies_reason(
    ctx: Context, end: date, current_assets: Decimal | None = None
) -> str | None:
    """Hide reason for a cell whose inventory value exists but whose period carries a supplies line the locked formula
    cannot classify: REASON_MATERIALS for a true current materials-and-supplies face line (founder ruling 2026-10-25);
    REASON_PRESENTED for an inventory-named supplies sub-line (Verifier: the label MaterialsSupplies must not be used
    where there is no materials-and-supplies face line). Neither applies when the current-assets total foots without
    the line (it is inside another line or a note) or the figure exceeds current assets."""
    if not MATERIALS_AND_SUPPLIES_ARE_INVENTORY:
        return None
    lines = ctx.lines_by_date.get(end, {})
    ca = current_assets if current_assets is not None else lines.get(CURRENT_ASSETS_TAG)

    def current_line(value: Decimal | None) -> bool:
        if not value or value <= 0:
            return False
        return ca is None or (value <= ca and not foots_without_inventory(ca, lines))

    if current_line(ctx.materials_supplies.get(end)):
        return REASON_MATERIALS
    if current_line(ctx.supplies_subline.get(end)):
        return REASON_PRESENTED
    return None


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


FACE_FILE_ENV = "SCROONER_QR_FACE_FILE"
_face_cache: dict[str, dict[str, bool]] = {}


def default_face() -> dict[str, bool]:
    """accession -> does its balance sheet show an inventory line, from the interim JSONL named by the environment
    (empty when unset: every face is then unavailable and the stored value is kept)."""
    import os
    from pathlib import Path

    from scrooner_pipeline.mapper import quick_ratio_face

    path = os.environ.get(FACE_FILE_ENV, "")
    if path and path not in _face_cache:
        _face_cache[path] = quick_ratio_face.load_jsonl(Path(path))
    return _face_cache.get(path, {})


def load_context(
    conn: Any,
    company_id: int,
    like_ids: list[int] | None = None,
    face: dict[str, bool] | None = None,
) -> Context:
    if like_ids is None:
        like_ids, _ = load_inventory_concept_ids(conn)
    if face is None:
        face = default_face()
    with conn.cursor() as cur:
        cur.execute(
            "select line_present from analytics.company_filing_line_evidence where company_id = %s and data_point = %s",
            (company_id, EVIDENCE_POINT),
        )
        row = cur.fetchone()
        lines: dict[date, dict[str, Decimal]] = {}
        like: dict[date, dict[str, Decimal]] = {}
        materials: dict[date, Decimal] = {}
        subline: dict[date, Decimal] = {}
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
                if "MaterialsSupplies" in tag or "RawMaterialsAndSupplies" in tag:
                    # a true materials-and-supplies line, or (inventory-named) a sub-line of inventory
                    target = subline if "nventor" in tag else materials
                    target[end] = target.get(end, Decimal(0)) + value
        cur.execute(
            """select distinct on (p.end_date) p.end_date, fl.accession_number
               from core.fact f join core.period p on p.id = f.period_id
               join core.concept k on k.id = f.concept_id join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and p.period_type = 'instant' and k.taxonomy = 'us-gaap'
                 and k.tag = 'AssetsCurrent'
               order by p.end_date, f.is_authoritative desc, f.id desc""",
            (company_id,),
        )
        accession = dict(cur.fetchall())
    face_by_date = {d: face[a] for d, a in accession.items() if a in face}
    return Context(
        None if row is None else row[0],
        lines,
        like,
        materials,
        face_by_date,
        subline,
        accession,
    )


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
    outcome: str = "null"  # null | kept_unverified (the period's own statement could not be read: stored value kept)
    accession: str | None = None


def plan_quick_ratio(
    conn: Any,
    company_ids: list[int],
    chunk: int = 100,
    face: dict[str, bool] | None = None,
    include_kept: bool = False,
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
        ctx = {
            cid: load_context(conn, cid, like_ids, face)
            for cid in {s[0] for s in stored}
        }
        for cid, end, label, value in stored:
            if (cid, end) in have:
                reason = materials_supplies_reason(
                    ctx[cid], end
                )  # inventory present, but a materials line exists
            else:
                reason = inventory_missing_reason(ctx[cid], end)
            kept = False
            if reason is None:
                if (
                    include_kept
                    and (cid, end) not in have
                    and face_unavailable(ctx[cid], end)
                ):
                    kept = True
                else:
                    continue
            assert kept or reason is not None
            cur_ratio = current.get((cid, end))
            equal = cur_ratio is not None and abs(
                Decimal(value) - Decimal(cur_ratio)
            ) <= Decimal("0.0005")
            out.append(
                PlannedCell(cid, cik_of[cid], str(end), label, str(value), str(value) if kept else None,
                            "kept_unverified:face_unavailable" if kept or reason is None else reason,
                            None if cur_ratio is None else str(cur_ratio), equal,
                            "kept_unverified" if kept else "null", ctx[cid].accession_by_date.get(end))
            )  # fmt: skip
    return out
