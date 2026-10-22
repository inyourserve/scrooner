"""Operating-income guard (T2, WO-14, RF-14 ``oi.derived_not_face@1``): hide with a reason.

Three mechanisms put a value in ``operating_income_resolved`` (and ``operating_income``) that is
not the filer's operating income. This module hides them (never invents a replacement):

1. **Arithmetic fallback without identity** (``fallback_no_identity``). ``conflict_resolution.
   resolve_operating_income_arithmetic_fallback`` writes revenue - operating expenses - cost of
   revenue wherever no OI exists; its own docstring admits 10-15% misses (85.5-90.3% land within
   2% of a real value). A fallback cell is kept only when the SAME company's overlap periods
   (periods that have a real OI row beside revenue and operating expenses) reproduce the real OI
   within 2% in at least two periods and in all of them. Otherwise it is hidden: the filer's own
   face does not demonstrate that the arithmetic is its operating income.
2. **Pretax income tagged as operating income** (``pretax_equal``): the stored OI equals the
   stored pretax income within 0.1% (AFG, ELS: ledger 2026-10-21, 30 FY2025 10-K filers show this
   label shift) and the arithmetic identity does not vouch for it. Needs the pretax concept
   stored, so it cannot see filers whose pretax is itself tagged OperatingIncomeLoss.
3. **Named company-scoped holds** (``named_hold``) for filers whose OperatingIncomeLoss is a
   segment-note or pretax figure that the face statement does not print: tags cannot show
   statement role, so these are listed with the filing evidence, and generic recall for the
   segment-note mechanism is UNMEASURED until the structure source exists (WO-REVIEW F10).

Flag ``oi.derived_not_face@1`` (SCROONER_RULES_ENABLED), default OFF = no-op. Dry run writes
nothing. Live requires the blank-reason store. Rollback: flag off, rerun the conflict-fill
stage for the manifest ciks.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_blank_reason import BlankReason, BlankReasonStore
from scrooner_pipeline.common.rule_before_image import PlannedChange
from scrooner_pipeline.common.rule_flags import rule_enabled as is_enabled

logger = structlog.get_logger()

RULE_ID = "oi.derived_not_face@1"
TARGET_CONCEPTS = ("operating_income", "operating_income_resolved")
IDENTITY_TOLERANCE = Decimal("0.02")
PRETAX_TOLERANCE = Decimal("0.001")
MIN_OVERLAP_PERIODS = 2

REASON_FALLBACK = "fallback_no_identity"
REASON_PRETAX = "pretax_equal"
REASON_NAMED = "named_hold"


@dataclass(frozen=True)
class NamedHold:
    reason: str
    evidence: str  # accession + locator, label


# Company-scoped (all periods): hide-only, with the filing evidence. Verifier narrows the scope
# per period; until then unavailable-with-reason is the correct side to err on.
NAMED_HOLDS: dict[str, NamedHold] = {
    "0001042046": NamedHold(
        "OperatingIncomeLoss is pretax income (label 'Earnings before income taxes')",
        "FILING-CHECKED AFG 0001042046-26-000010 R5 FY2025 (ledger 2026-10-21)",
    ),
    "0000895417": NamedHold(
        "OperatingIncomeLoss is pretax income (label 'Income before taxes and other items')",
        "FILING-CHECKED ELS 0001628280-26-008722 R5 FY2025 (ledger 2026-10-21)",
    ),
    "0000067887": NamedHold(
        "income statement prints no operating income line; stored OI is a segment-note total",
        "FILING-CHECKED MOG-A 0001628280-25-054103 R3 FY2025 (statement of earnings has no operating profit row; stored 449,606K)",
    ),
    "0001099219": NamedHold(
        "insurer income statement prints no operating income line; stored OI is a segment-note figure",
        "DATA-INFERRED MET FY2025 OI 6,137M vs pretax 4,661M; WO-14 names it (Verifier to confirm at 0001099219-26-000013)",
    ),
    "0002089271": NamedHold(
        "segment-note OI read as consolidated; spin-off with no 10-K yet",
        "ASSUMED from WO-14 / doc 47 (HONA); Verifier to confirm",
    ),
}


def within(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    larger = max(abs(a), abs(b))
    return a == b if larger == 0 else abs(a - b) <= tol * larger


def arithmetic_oi(revenue: Decimal, opex: Decimal, cor: Decimal | None) -> Decimal:
    """Exactly the fallback's formula."""
    return revenue - opex - (cor or Decimal(0))


@dataclass(frozen=True)
class Overlap:
    oi: Decimal
    revenue: Decimal
    opex: Decimal
    cor: Decimal | None


def fallback_identity_ok(overlaps: Iterable[Overlap]) -> bool:
    ov = list(overlaps)
    if len(ov) < MIN_OVERLAP_PERIODS:
        return False
    return all(
        within(arithmetic_oi(o.revenue, o.opex, o.cor), o.oi, IDENTITY_TOLERANCE)
        for o in ov
    )


@dataclass(frozen=True)
class OiCell:
    period_id: int
    value: Decimal
    is_fallback: bool
    pretax: Decimal | None
    revenue: Decimal | None
    opex: Decimal | None
    cor: Decimal | None


def classify_cell(cik: str, cell: OiCell, identity_ok: bool) -> str | None:
    """Reason code to hide the cell, or None to keep."""
    if cik in NAMED_HOLDS:
        return REASON_NAMED
    if cell.is_fallback:
        return None if identity_ok else REASON_FALLBACK
    if cell.pretax is not None and within(cell.value, cell.pretax, PRETAX_TOLERANCE):
        vouched = (
            cell.revenue is not None
            and cell.opex is not None
            and within(
                arithmetic_oi(cell.revenue, cell.opex, cell.cor),
                cell.value,
                IDENTITY_TOLERANCE,
            )
        )
        return None if vouched else REASON_PRETAX
    return None


@dataclass
class GuardResult:
    hidden: list[tuple[int, str]] = field(default_factory=list)  # (period_id, reason)
    stats: dict[str, int] = field(default_factory=dict)


def decide_company(cik: str, cells: list[OiCell]) -> GuardResult:
    res = GuardResult(
        stats={
            REASON_FALLBACK: 0,
            REASON_PRETAX: 0,
            REASON_NAMED: 0,
            "kept_fallback": 0,
        }
    )
    overlaps = [
        Overlap(c.value, c.revenue, c.opex, c.cor)
        for c in cells
        if not c.is_fallback and c.revenue is not None and c.opex is not None
    ]
    identity_ok = fallback_identity_ok(overlaps)
    for c in cells:
        why = classify_cell(cik, c, identity_ok)
        if why is None:
            if c.is_fallback:
                res.stats["kept_fallback"] += 1
            continue
        res.stats[why] += 1
        res.hidden.append((c.period_id, why))
    return res


# ---------------------------------------------------------------- database layer
_CONCEPTS = (
    "operating_income_resolved",
    "revenue_sanity_resolved",
    "operating_expenses_resolved",
    "cost_of_revenue_resolved",
    "income_before_tax_resolved",
)

_LOAD_SQL = """
select cf.company_id, cf.period_id, cc.name, cf.value, cf.source_fact_ids, p.start_date, p.end_date
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id and cc.name = any(%(names)s)
join core.period p on p.id = cf.period_id
where cf.company_id = any(%(ids)s)
"""


def _chunks(seq: list[Any], n: int) -> Iterable[list[Any]]:
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _grain(start: date, end: date) -> str:
    days = (end - start).days + 1
    return "FY" if days >= 300 else ("Q" if days <= 105 else "YTD")


def build_cells(
    rows: Iterable[tuple[Any, ...]],
) -> tuple[list[OiCell], dict[int, tuple[date, date]]]:
    """rows: (period_id, concept, value, source_fact_ids, start, end) of ONE company."""
    by_period: dict[int, dict[str, tuple[Decimal, list[int]]]] = defaultdict(dict)
    info: dict[int, tuple[date, date]] = {}
    for period_id, name, value, src, start, end in rows:
        by_period[period_id][name] = (value, list(src or []))
        info[period_id] = (start, end)
    cells = []
    for period_id, d in by_period.items():
        if "operating_income_resolved" not in d:
            continue
        oi, oi_src = d["operating_income_resolved"]
        rev, opex, cor = (
            d.get("revenue_sanity_resolved"),
            d.get("operating_expenses_resolved"),
            d.get("cost_of_revenue_resolved"),
        )
        is_fallback = bool(
            rev and opex and oi_src == rev[1] + opex[1] + (cor[1] if cor else [])
        )
        pre = d.get("income_before_tax_resolved")
        cells.append(
            OiCell(
                period_id,
                oi,
                is_fallback,
                pre[0] if pre else None,
                rev[0] if rev else None,
                opex[0] if opex else None,
                cor[0] if cor else None,
            )
        )
    return cells, info


def apply_operating_income_guard(
    conn: psycopg.Connection,
    ciks: set[str] | None = None,
    *,
    dry_run: bool = False,
    reason_store: BlankReasonStore | None = None,
    run_id: str | None = None,
    environ: dict[str, str] | None = None,
    chunk: int = 100,
) -> dict[str, Any]:
    live = is_enabled(RULE_ID, environ) and not dry_run
    if not live and not dry_run:
        return {"skipped": "rule_off", "planned": []}
    if live and reason_store is None:
        raise RuntimeError(
            f"{RULE_ID}: a reason store is required to hide cells (migration 0100)"
        )
    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                "select id, cik from core.company where cik = any(%s)", (sorted(ciks),)
            )
        else:
            cur.execute("select id, cik from core.company order by id")
        companies = cur.fetchall()
        cur.execute(
            "select id, name from analytics.canonical_concept where name = any(%s)",
            (list(TARGET_CONCEPTS),),
        )
        concept_ids = {n: i for i, n in cur.fetchall()}
    totals: dict[str, Any] = {
        "companies": 0,
        "companies_with_hides": 0,
        "cells_hidden": 0,
        REASON_FALLBACK: 0,
        REASON_PRETAX: 0,
        REASON_NAMED: 0,
        "kept_fallback": 0,
        "dry_run": dry_run,
    }
    planned: list[PlannedChange] = []
    for batch in _chunks(companies, chunk):
        ids = [c[0] for c in batch]
        ciks_by_id = {c[0]: c[1] for c in batch}
        rows_by_company: dict[int, list[tuple[Any, ...]]] = defaultdict(list)
        with conn.cursor() as cur:
            cur.execute(_LOAD_SQL, {"names": list(_CONCEPTS), "ids": ids})
            for company_id, period_id, name, value, src, start, end in cur.fetchall():
                rows_by_company[company_id].append(
                    (period_id, name, value, src, start, end)
                )
        for company_id in ids:
            totals["companies"] += 1
            cells, info = build_cells(rows_by_company.get(company_id, []))
            res = decide_company(ciks_by_id[company_id], cells)
            for k in (REASON_FALLBACK, REASON_PRETAX, REASON_NAMED, "kept_fallback"):
                totals[k] += res.stats[k]
            if not res.hidden:
                continue
            totals["companies_with_hides"] += 1
            totals["cells_hidden"] += len(res.hidden)
            values = {c.period_id: c.value for c in cells}
            reasons: list[BlankReason] = []
            for period_id, why in res.hidden:
                start, end = info[period_id]
                detail = {"reason": why}
                if why == REASON_NAMED:
                    h = NAMED_HOLDS[ciks_by_id[company_id]]
                    detail.update(evidence=h.evidence, note=h.reason)
                planned.append(
                    PlannedChange(
                        RULE_ID,
                        ciks_by_id[company_id],
                        company_id,
                        "operating_income_resolved",
                        end,
                        values[period_id],
                        None,
                        f"guard_hidden:{why}",
                    )
                )
                reasons.append(
                    BlankReason(
                        company_id,
                        "operating_income_resolved",
                        _grain(start, end),
                        start,
                        end,
                        "resolved",
                        RULE_ID,
                        why,
                        detail,
                    )
                )
            if dry_run:
                continue
            assert reason_store is not None
            reason_store.replace(company_id, RULE_ID, run_id or "adhoc", reasons)
            with conn.cursor() as cur:
                cur.execute(
                    """delete from analytics.canonical_fact
                       where company_id = %s and canonical_concept_id = any(%s) and period_id = any(%s)""",
                    (
                        company_id,
                        [concept_ids[n] for n in TARGET_CONCEPTS if n in concept_ids],
                        sorted({p for p, _ in res.hidden}),
                    ),
                )
            conn.commit()
    totals["planned"] = planned
    logger.info(
        "operating_income_guard.done",
        **{k: v for k, v in totals.items() if k != "planned"},
    )
    return totals
