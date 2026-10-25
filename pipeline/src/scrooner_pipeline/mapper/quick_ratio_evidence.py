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
 3. Otherwise, nothing in our stored lines explains the residual: THIS period's own balance sheet decides, per DATE
    COLUMN (``Context.face_by_date``, read from the FSDS presentation rows and values, ``quick_ratio_face.py``):
    an inventory line with a nonzero value at the cell's own date -> NULL ``inventory_presented_not_extracted``;
    the statement shows the date and no such line -> the zero stands; the statement does not show the date (a later
    filing with newer columns only, no readable pages) -> NULL ``inventory_statement_unavailable`` (never a guess,
    never decided from the latest statements or from a comparative column: BBIO, SWX, TGTX, IOVA, DVN, GOOG, T ...).
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
# Founder ruling 2026-10-25: a current MaterialsSuppliesAndOther (or materials-captioned non-inventory) face line hides
# the quick ratio. The switch turns that rule off in one place; inventory-named supplies elements are inventory either way.
MATERIALS_AND_SUPPLIES_ARE_INVENTORY = True

# ONE mapping table from cause to the reason code shown to the reader: changing a code is a one-line edit here.
# Precedence when several apply (one reason per cell, first wins): materials > not_authoritative > unavailable >
# presented > review (RECORD-INVENTORY2 section 6).
HIDE_REASONS = {
    "materials": "incomplete:materials_supplies_line_present",
    "not_authoritative": "incomplete:inventory_fact_not_authoritative",
    "unavailable": "incomplete:inventory_statement_unavailable",
    "presented": "incomplete:inventory_presented_not_extracted",
    "review": "incomplete:inventory_value_under_review",
}
PRECEDENCE = ("materials", "not_authoritative", "unavailable", "presented", "review")
REASON_MATERIALS = HIDE_REASONS["materials"]
REASON_NOT_AUTHORITATIVE = HIDE_REASONS["not_authoritative"]
REASON_UNAVAILABLE = HIDE_REASONS["unavailable"]
REASON_PRESENTED = HIDE_REASONS["presented"]
REASON_REVIEW = HIDE_REASONS["review"]
# Registrants whose WIP line was read in their own policy note as client billable costs (not inventory, all years):
# {cik: filing and paragraph}. The note-text guard applies only after someone read the note, never on a caption.
CONTRACT_ASSET_NOTE_READ = {
    "0000029989": "OMC 10-K FY2016 0000029989-17-000004 and FY2015 0000029989-16-000015, Note 2 Significant Accounting Policies",
}

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
    """A balance-sheet inventory element ("...NetOfReserves" lines are lines; reserves on their own are not).
    MaterialsSuppliesAndOther is NOT inventory (element text: not included in inventory)."""
    t = tag.replace("NetOfReserves", "").replace("NetOfReserve", "")
    return "nventor" in t and not any(w in t for w in _EXCLUDED)


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
class PeriodFace:
    """What the balance sheet covering one date shows at that date's own column."""

    inventory_line: bool  # a presented inventory line with a nonzero value
    materials_line: bool  # a presented materials-and-supplies line (not inventory-named) with a value


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
    face_by_date: dict[date, PeriodFace] = field(default_factory=dict)
    # dates whose statement was read but does not show the date (a 10-K/A with newer columns only), or whose filing
    # predates machine-readable statements (2009): the cell is hidden as unavailable. A date in neither map has no
    # readable statement here (FSDS does not carry every filing): the stored value is kept and flagged.
    face_hide_dates: frozenset[date] = field(default_factory=frozenset)
    # dates where InventoryNet exists only as non-authoritative copies (no authoritative one): never read, never mapped
    nonauthoritative_dates: frozenset[date] = field(default_factory=frozenset)
    accession_by_date: dict[date, str] = field(
        default_factory=dict
    )  # the filing whose AssetsCurrent fact is the period's


def _materials_cause(ctx: Context, end: date, ca: Decimal | None) -> bool:
    """A current materials-and-supplies line outside inventory: from the period's own statement when it was read,
    else from the fact (a current MaterialsSuppliesAndOther no larger than current assets, not inside a footed total)."""
    if not MATERIALS_AND_SUPPLIES_ARE_INVENTORY:
        return False
    face = ctx.face_by_date.get(end)
    if face is not None:
        return face.materials_line
    value = ctx.materials_supplies.get(end)
    lines = ctx.lines_by_date.get(end, {})
    return bool(
        value
        and value > 0
        and (ca is None or (value <= ca and not foots_without_inventory(ca, lines)))
    )


def hide_cause(
    ctx: Context, end: date, current_assets: Decimal | None, inventory_present: bool
) -> str | None:
    """The cause (key of HIDE_REASONS) that hides the quick ratio of this cell, or None when the value stays.

    ``inventory_present``: our canonical data holds an authoritative inventory value for the date, so the formula
    runs; then only the materials-and-supplies rule can hide it. Otherwise (the f67a927 class: a missing inventory
    would be treated as zero) the period's own statement decides, per date column:
      - the current-assets total foots without an inventory line -> the zero stands;
      - InventoryNet exists only as non-authoritative copies -> not_authoritative;
      - the statement does not show the date / predates machine-readable statements -> unavailable;
      - the statement shows an inventory line at the date (OMC's contract-asset WIP excluded) -> review when the
        approved face-slot rule (authoritative member sub-lines of the period's own filing) yields a value that is not
        yet published, else presented; no inventory line -> the value stays (a note figure: 0001522540 2023-06-30);
      - no readable statement in the data set (after 2009): member facts -> review, else the value stays, flagged."""
    lines = ctx.lines_by_date.get(end, {})
    ca = current_assets if current_assets is not None else lines.get(CURRENT_ASSETS_TAG)
    causes: set[str] = set()
    if _materials_cause(ctx, end, ca):
        causes.add("materials")
    if not inventory_present and not (
        ca is not None and foots_without_inventory(ca, lines)
    ):
        like = ctx.inventory_like.get(end, {})
        has_member = any(0 < v <= (ca if ca is not None else v) for v in like.values())
        face = ctx.face_by_date.get(end)
        if end in ctx.nonauthoritative_dates:
            causes.add("not_authoritative")
        elif face is None and end in ctx.face_hide_dates and not has_member:
            causes.add("unavailable")
        elif face is not None and face.inventory_line:
            causes.add("review" if has_member else "presented")
        elif face is None and has_member:
            causes.add("review")
    return next((c for c in PRECEDENCE if c in causes), None)


def inventory_missing_reason(
    ctx: Context, end: date, current_assets: Decimal | None = None
) -> str | None:
    """Reason text for a cell with NO inventory value (None: the zero stands)."""
    cause = hide_cause(ctx, end, current_assets, inventory_present=False)
    return None if cause is None else HIDE_REASONS[cause]


def materials_supplies_reason(
    ctx: Context, end: date, current_assets: Decimal | None = None
) -> str | None:
    """Reason text for a cell whose inventory value exists (only the materials-and-supplies rule can hide it)."""
    cause = hide_cause(ctx, end, current_assets, inventory_present=True)
    return None if cause is None else HIDE_REASONS[cause]


def face_unavailable(
    ctx: Context, end: date, current_assets: Decimal | None = None
) -> bool:
    return (
        hide_cause(ctx, end, current_assets, inventory_present=False) == "unavailable"
    )


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


def _accession_year(accession: str) -> int:
    """The year in an accession number (0001193125-16-708358 -> 2016)."""
    yy = int(accession.split("-")[1])
    return 2000 + yy if yy < 90 else 1900 + yy


def _column(d: date, dates: frozenset[date]) -> date | None:
    """The data-set column for a balance-sheet date. FSDS rounds 52/53-week year-ends to the month end
    (2020-09-27 appears as 2020-09-30), so a date within 6 days counts."""
    if d in dates:
        return d
    near = [x for x in dates if abs((x - d).days) <= 6]
    return min(near, key=lambda x: abs((x - d).days)) if near else None


def default_face() -> dict[str, Any]:
    """accession -> does its balance sheet show an inventory line, from the interim JSONL named by the environment
    (empty when unset: every face is then unavailable and the affected cells are hidden with a reason)."""
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
    face: dict[str, Any] | None = None,
    mapped_ids: set[int] | None = None,
) -> Context:
    if like_ids is None or mapped_ids is None:
        like_ids, mapped_ids = load_inventory_concept_ids(conn)
    if face is None:
        face = default_face()
    with conn.cursor() as cur:
        cur.execute(
            "select line_present from analytics.company_filing_line_evidence where company_id = %s and data_point = %s",
            (company_id, EVIDENCE_POINT),
        )
        row = cur.fetchone()
        cur.execute("select cik from core.company where id = %s", (company_id,))
        cik_row = cur.fetchone()
        cik = cik_row[0] if cik_row else ""
        cur.execute(
            """select distinct on (period_of_report) period_of_report, accession_number from core.filing
               where company_id = %s and period_of_report is not null
                 and form in ('10-K', '10-Q', '10-K405', '10-KT', '10-KSB', '10-QSB')
               order by period_of_report, is_amendment, filing_date, id""",
            (company_id,),
        )
        accession = dict(cur.fetchall())
        # a cell whose date has no periodic filing of its own (a transition-period or amended filing carries it): the
        # filing of the period's current-assets fact is the statement that shows the date
        cur.execute(
            """select distinct on (p.end_date) p.end_date, fl.accession_number
               from core.fact f join core.period p on p.id = f.period_id
               join core.concept k on k.id = f.concept_id join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and p.period_type = 'instant' and k.taxonomy = 'us-gaap'
                 and k.tag = 'AssetsCurrent'
               order by p.end_date, f.is_authoritative desc, f.id desc""",
            (company_id,),
        )
        for end_date, acc in cur.fetchall():
            accession.setdefault(end_date, acc)
        lines: dict[date, dict[str, Decimal]] = {}
        like: dict[date, dict[str, Decimal]] = {}
        materials: dict[date, Decimal] = {}
        cur.execute(
            """select distinct on (p.end_date, k.tag, fl.accession_number, f.is_authoritative)
                      p.end_date, k.tag, f.value, fl.accession_number, f.is_authoritative
               from core.fact f join core.period p on p.id = f.period_id join core.concept k on k.id = f.concept_id
               join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and p.period_type = 'instant' and k.taxonomy = 'us-gaap'
                 and (k.tag = any(%s) or f.concept_id = any(%s))
               order by p.end_date, k.tag, fl.accession_number, f.is_authoritative desc, f.id desc""",
            (company_id, sorted(FOOTING_TAGS), like_ids or [0]),
        )
        rank: dict[tuple[date, str], tuple[int, int]] = {}
        for r in cur.fetchall():
            end, tag, value = r[0], r[1], r[2]
            acc, auth = (r[3], r[4]) if len(r) > 3 else (accession.get(end), True)
            own = acc == accession.get(end)
            if tag in FOOTING_TAGS:
                score = (int(own), int(bool(auth)))
                if score > rank.get((end, tag), (-1, -1)):
                    rank[(end, tag)] = score
                    lines.setdefault(end, {})[tag] = value
            elif own and auth:
                # a member fact must be authoritative and from the period's own filing (CLAUDE.md hard filter)
                if "MaterialsSupplies" in tag and "nventor" not in tag:
                    materials[end] = materials.get(end, Decimal(0)) + value
                else:
                    like.setdefault(end, {})[tag] = value
        cur.execute(
            """select p.end_date, bool_or(f.is_authoritative) from core.fact f join core.period p on p.id = f.period_id
               where f.company_id = %s and f.concept_id = any(%s) and p.period_type = 'instant'
               group by p.end_date""",
            (company_id, sorted(mapped_ids) or [0]),
        )
        nonauth = {d for d, any_auth in cur.fetchall() if not any_auth}
    face_by_date: dict[date, PeriodFace] = {}
    hide: set[date] = set()
    wip_excluded = cik in CONTRACT_ASSET_NOTE_READ
    for d, acc in accession.items():
        f = face.get(acc)
        if f is None:
            # not in the data set: filings before 2010 have no machine-readable statement (hidden); later ones may
            # simply be missing from it (kept, flagged)
            if _accession_year(acc) < 2010:
                hide.add(d)
            continue
        hit = _column(d, f.statement_dates)
        if hit is None:
            hide.add(d)  # the statement is readable but does not show this date
            continue
        inv_col = _column(d, f.inventory_dates)
        if wip_excluded and inv_col is not None and inv_col in f.wip_only_dates:
            inv_col = None  # the registrant's own note reads this line as client billable costs
        face_by_date[d] = PeriodFace(
            inv_col is not None, _column(d, f.materials_dates) is not None
        )
    return Context(
        None if row is None else row[0],
        lines,
        like,
        materials,
        face_by_date,
        frozenset(hide),
        frozenset(nonauth),
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
    accession: str | None = None
    # hide: the stored value is wrong today (it equals the current ratio, inventory was treated as zero) or a supplies
    # line the locked formula cannot classify is on the face. flag_keep: the stored value differs from the current
    # ratio, so inventory WAS subtracted when it was computed (only our canonical inventory fact is missing now):
    # the value is right, it is flagged, and a recompute without the fact would break it
    outcome: str = "hide"


def plan_quick_ratio(
    conn: Any,
    company_ids: list[int],
    chunk: int = 100,
    face: dict[str, bool] | None = None,
) -> list[PlannedCell]:
    """Read-only dry run: stored quick_ratio cells that have a value although NO inventory fact exists at their date
    (the cells f67a927 turned into current ratio) and that the evidence rule would turn into NULL."""
    from decimal import Decimal

    out: list[PlannedCell] = []
    like_ids, mapped_ids = load_inventory_concept_ids(conn)
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
            cid: load_context(conn, cid, like_ids, face, mapped_ids)
            for cid in {s[0] for s in stored}
        }
        for cid, end, label, value in stored:
            if (cid, end) in have:
                reason = materials_supplies_reason(
                    ctx[cid], end
                )  # inventory present, but a materials line exists
            else:
                reason = inventory_missing_reason(ctx[cid], end)
            if reason is None:
                continue
            cur_ratio = current.get((cid, end))
            equal = cur_ratio is not None and abs(
                Decimal(value) - Decimal(cur_ratio)
            ) <= Decimal("0.0005")
            supplies_path = (cid, end) in have
            out.append(
                PlannedCell(cid, cik_of[cid], str(end), label, str(value), None, reason,
                            None if cur_ratio is None else str(cur_ratio), equal,
                            ctx[cid].accession_by_date.get(end),
                            "hide" if supplies_path or equal else "flag_keep")
            )  # fmt: skip
    return out


def plan_materials_by_face(
    conn: Any, company_ids: list[int], face: dict[str, Any], chunk: int = 200
) -> list[PlannedCell]:
    """Light dry run for the cells that STAY (an inventory value exists): a quick_ratio is hidden with
    ``materials_supplies_line_present`` wherever the period's own balance sheet presents a materials-and-supplies line
    (FDX 'Spare parts, supplies, and fuel', ConEd 'Fuel oil, gas in storage, materials and supplies'). Reads only the
    face and the stored cells; no fact context."""
    out: list[PlannedCell] = []
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.metric_definition where metric_name = 'quick_ratio'"
        )
        qr = cur.fetchone()[0]
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
                """select distinct on (company_id, period_of_report) company_id, period_of_report, accession_number
                   from core.filing where company_id = any(%s) and period_of_report is not null
                     and form in ('10-K', '10-Q', '10-K405', '10-KT', '10-KSB', '10-QSB')
                   order by company_id, period_of_report, is_amendment, filing_date, id""",
                (part,),
            )
            acc = {(c, d): a for c, d, a in cur.fetchall()}
        for cid, end, label, value in stored:
            f = face.get(acc.get((cid, end), ""))
            if (
                f is not None
                and _column(end, f.materials_dates) is not None
                and _column(end, f.statement_dates)
            ):
                out.append(
                    PlannedCell(cid, cik_of[cid], str(end), label, str(value), None, REASON_MATERIALS,
                                None, False, acc[(cid, end)], "hide")
                )  # fmt: skip
    return out
