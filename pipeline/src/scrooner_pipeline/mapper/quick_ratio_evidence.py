"""Inventory evidence for quick_ratio (rule ``quick_ratio.inventory_evidence@1``).

Commit f67a927 (2026-10-09) stopped nulling quick_ratio when inventory is absent from our facts: a MISSING inventory
became a ZERO, so quick ratio = current ratio for every inventory holder whose inventory we did not extract (NKE stored
2.075 vs 1.387, BA 1.138 vs 0.331, GAP 1.822 vs 1.109, AZO 0.890 vs 0.137, XOM 1.135 vs 0.847; Data Triage, 2026-10-24).

Rule: a missing inventory is a zero ONLY when ``analytics.company_filing_line_evidence`` (migration 0093) says the
inventory line is NOT presented on the company's balance sheet (line_present = false) AND no inventory-like us-gaap
instant fact that is not mapped to ``inventory`` exists at the same date. Otherwise quick_ratio is NULL with a visible
reason (``incomplete:...``), never a guess:
  inventory_like_tag_unmapped         an inventory-like tag is filed at that date but not mapped (XOM sub-lines, AZO)
  inventory_presented_not_extracted   the statement shows an inventory line, we hold no inventory value
  inventory_presence_unknown          no evidence either way (statement not located / no evidence row)

The evidence is about the company's LATEST statements, so it is applied to every period of the company; it is
evidence, not proof (README of migration 0093).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

RULE_ID = "quick_ratio.inventory_evidence@1"
EVIDENCE_POINT = "inventory"

REASON_UNMAPPED = "incomplete:inventory_like_tag_unmapped"
REASON_PRESENTED = "incomplete:inventory_presented_not_extracted"
REASON_UNKNOWN = "incomplete:inventory_presence_unknown"

# words that make an inventory-named tag NOT a current balance-sheet inventory line (flows, reserves, per-share-like
# and noncurrent figures)
_EXCLUDED = (
    "Increase", "Decrease", "Reserve", "Writedown", "WriteDown", "Cost", "Purchase", "Valuation", "Adjustment",
    "Obsolescence", "Impairment", "Turnover", "Percentage", "Lifo", "LIFO", "Provision", "Expense", "Revenue", "Sale",
    "Change", "Payments", "Proceeds", "Realized", "Shares", "Number", "Days", "Commitment", "Excess", "Noncurrent",
    "LongTerm", "Deferred", "Recovery", "Writeoff", "WriteOff", "Policy", "Method", "Gain", "Loss", "Effect",
    "Contra", "Other", "Reclass", "Transfer", "Acquired", "Capitalized", "Held", "Financing",
)  # fmt: skip


def is_inventory_like(tag: str) -> bool:
    """A balance-sheet inventory line ("...NetOfReserves" lines are lines; reserves on their own are not)."""
    t = tag.replace("NetOfReserves", "").replace("NetOfReserve", "")
    return "nventor" in t and not any(w in t for w in _EXCLUDED)


@dataclass(frozen=True)
class Context:
    line_present: (
        bool | None
    )  # evidence row: True presented, False not presented, None unknown / no row
    unmapped_like_dates: frozenset[date] = field(default_factory=frozenset)


def inventory_missing_reason(ctx: Context, end: date) -> str | None:
    """Why a quick_ratio cell with NO inventory fact at ``end`` must be NULL, or None when a zero is safe."""
    if end in ctx.unmapped_like_dates:
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
            "select id, tag from core.concept where taxonomy = 'us-gaap' and tag ilike %s",
            ("%nventor%",),
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
        dates: set[date] = set()
        if like_ids:
            cur.execute(
                """select distinct p.end_date from core.fact f join core.period p on p.id = f.period_id
                   where f.company_id = %s and f.concept_id = any(%s) and p.period_type = 'instant'""",
                (company_id, like_ids),
            )
            dates = {r[0] for r in cur.fetchall()}
    return Context(None if row is None else row[0], frozenset(dates))


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
