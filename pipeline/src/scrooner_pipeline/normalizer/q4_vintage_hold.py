"""Same-vintage Q4 hold: interim form of rule period.same_vintage_derivation@1 (RF-04).

Found by the Verifier on 2026-10-31 (PM Q4 2025 operating expenses 3,412M; the
10-K basis is 3,429M): derive_q4 pairs an FY value with a 9-month value that
were taken from different restatement vintages (recast 9M under one concept,
original 9M under another), so the Q4 it subtracts out was never reported by
any filing. This module decides, per (company, concept, unit, fiscal year),
whether the FY and 9M/Q1-Q3 inputs share ONE filing basis, using the Period
Engineer's read-only evaluator (q4_vintage_dryrun.evaluate_cell, its vintage
rules unchanged) and tells derive_q4 to HOLD the cell when they do not.

Flag modes (common.rule_flags, env SCROONER_RULES_ENABLED / _DRYRUN):
  off      derive_q4 behaves as before (default)
  dry_run  derive_q4 derives as before but counts and logs every cell the hold
           WOULD catch (stats held_mixed_vintage / held_sign_conflict)
  on       the cell is not derived, an existing derived Q4 for it is demoted
           (never deleted: derived._retire_derived), and a reason row is written
           to analytics.cell_blank_reason for the concept's canonical name(s)
           and for the statement-fallback concepts derived from them.

Tolerance: core.fact stores no XBRL `decimals`, so the evaluator needs a stated
rounding tolerance. HOLD_TOLERANCE treats values within 0.05% as the same
number (thousands vs millions presentations of one figure); anything wider
counts as a different vintage. PM's 3,412 vs 3,429 (0.5%) is caught; this is
an interim choice, recorded here, not a measured one.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection, Iterable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.cell_store import BlankReason, replace_rule_reasons
from scrooner_pipeline.common.rule_flags import RULE_SAME_VINTAGE_DERIVATION
from scrooner_pipeline.normalizer.q4_vintage_dryrun import (
    BLOCKED_MIXED,
    BLOCKED_SIGN,
    Q4Candidate,
    Tolerance,
    load_candidates,
)

logger = structlog.get_logger()

RULE_ID = RULE_SAME_VINTAGE_DERIVATION
HOLD_TOLERANCE = Tolerance(rel=Decimal("0.0005"), abs_tol=Decimal("0"))

# evaluator category -> (stat key in derive_q4, reason_code)
HOLD_CODES: dict[str, tuple[str, str]] = {
    BLOCKED_MIXED: ("held_mixed_vintage", "q4_inputs_mixed_vintage"),
    BLOCKED_SIGN: ("held_sign_conflict", "q4_input_sign_conflict"),
}


@dataclass(frozen=True)
class Hold:
    concept_id: int
    unit_id: int
    q4_start: date
    q4_end: date
    category: str
    block_reason: str | None
    fy_fact_ids: tuple[int, ...] = ()
    ytd_fact_ids: tuple[int, ...] = ()
    fy_accessions: tuple[str, ...] = ()
    ytd_accessions: tuple[str, ...] = ()
    fy_value: Decimal | None = None
    ytd_value: Decimal | None = None
    alternatives: tuple[dict, ...] = field(default_factory=tuple)

    @property
    def stat_key(self) -> str:
        return HOLD_CODES[self.category][0]

    @property
    def reason_code(self) -> str:
        return HOLD_CODES[self.category][1]


def hold_category(candidate: Q4Candidate | None) -> str | None:
    """The evaluator category that makes derive_q4 hold, or None. Only the two
    vintage categories hold: a cell the evaluator cannot derive for other
    reasons (no FY, no YTD, non-additive) is derive_q4's own business."""
    if candidate is None or candidate.category not in HOLD_CODES:
        return None
    return candidate.category


def load_vintage_categories(
    conn: psycopg.Connection,
    company_id: int,
    concept_ids: Collection[int],
    *,
    tol: Tolerance = HOLD_TOLERANCE,
) -> dict[tuple[int, str, date], Q4Candidate]:
    """(concept_id, unit_name, fiscal_year_start) -> evaluator verdict for one
    company. Read-only; every concept is evaluated as additive because
    derive_q4 applies its own non-additive gate before asking."""
    if not concept_ids:
        return {}
    out: dict[tuple[int, str, date], Q4Candidate] = {}
    for cand in load_candidates(
        conn,
        [company_id],
        concept_ids=sorted(set(concept_ids)),
        additive_concept_ids=sorted(set(concept_ids)),
        tol=tol,
    ):
        if cand.fiscal_year_start is None:
            continue
        out[(cand.concept_id, cand.unit, cand.fiscal_year_start)] = cand
    return out


def make_hold(
    candidate: Q4Candidate, unit_id: int, q4_start: date, q4_end: date
) -> Hold:
    return Hold(
        concept_id=candidate.concept_id,
        unit_id=unit_id,
        q4_start=q4_start,
        q4_end=q4_end,
        category=candidate.category,
        block_reason=candidate.block_reason,
        fy_fact_ids=tuple(candidate.fy_fact_ids),
        ytd_fact_ids=tuple(candidate.ytd_fact_ids),
        fy_accessions=tuple(candidate.fy_accessions),
        ytd_accessions=tuple(candidate.ytd_accessions),
        fy_value=candidate.fy_value,
        ytd_value=candidate.ytd_value,
        alternatives=tuple(candidate.alternatives),
    )


# ---- reasons -----------------------------------------------------------------


def canonical_names_by_concept(
    conn: psycopg.Connection, concept_ids: Collection[int]
) -> dict[int, list[str]]:
    """core.concept id -> canonical concept names it is mapped to (not rejected)."""
    if not concept_ids:
        return {}
    out: dict[int, list[str]] = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cm.concept_id, cc.name
            from analytics.concept_mapping cm
            join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
            where cm.concept_id = any(%s) and cm.confidence <> 'rejected'
            order by 1, 2
            """,
            (sorted(set(concept_ids)),),
        )
        for concept_id, name in cur.fetchall():
            out[concept_id].append(name)
    return dict(out)


def dependent_data_points(name: str) -> list[str]:
    """Cells computed from `name` downstream: its *_resolved target (the
    statement-table cell) and every statement-fallback concept that subtracts
    or adds it (gross profit from revenue - cost of revenue, ...). Imported
    lazily: the mapper layer sits above the normalizer."""
    from scrooner_pipeline.mapper.concept_fallback import ARITHMETIC_FALLBACKS
    from scrooner_pipeline.mapper.conflict_resolution import CONFLICT_FILL_TARGETS

    out: list[str] = []
    for primary, resolved in CONFLICT_FILL_TARGETS:
        if primary == name:
            out.append(resolved)
    resolved_of = dict(CONFLICT_FILL_TARGETS)
    for resolved, primary, minuend, subtrahend, _guard in ARITHMETIC_FALLBACKS:
        inputs = {
            minuend,
            subtrahend,
            resolved_of.get(minuend, ""),
            resolved_of.get(subtrahend, ""),
        }
        if name in inputs or resolved_of.get(name) in inputs:
            out.append(resolved)
    return sorted(set(out) - {name})


def blank_reasons(
    company_id: int, hold: Hold, names: Iterable[str]
) -> list[BlankReason]:
    """One reason per displayed data point the hold blanks: the canonical
    name(s) of the held concept plus their dependents. Grain Q, basis latest."""
    text = (
        f"Q4 not derived: FY and 9M/Q1-Q3 inputs are not from one filing basis "
        f"({hold.category}; {hold.block_reason or 'no evidenced same-vintage pairing'}). "
        f"FY {hold.fy_value} from {', '.join(hold.fy_accessions) or '?'}; "
        f"YTD {hold.ytd_value} from {', '.join(hold.ytd_accessions) or '?'}."
    )
    refs = {
        "category": hold.category,
        "block_reason": hold.block_reason,
        "fy_fact_ids": list(hold.fy_fact_ids),
        "ytd_fact_ids": list(hold.ytd_fact_ids),
        "fy_accessions": list(hold.fy_accessions),
        "ytd_accessions": list(hold.ytd_accessions),
        "alternatives": list(hold.alternatives),
        "tolerance": {
            "rel": str(HOLD_TOLERANCE.rel),
            "abs": str(HOLD_TOLERANCE.abs_tol),
        },
    }
    points: list[str] = []
    for n in names:
        points.append(n)
        points.extend(dependent_data_points(n))
    out = []
    for point in sorted(set(points)):
        out.append(
            BlankReason(
                key=CellKey(
                    company_id, point, "Q", hold.q4_start, hold.q4_end, "latest"
                ),
                state="defect",
                rule_id=RULE_ID,
                reason_code=hold.reason_code,
                defect_class="period",
                owner="period_engineer",
                root_cause_class="period",
                reason_text=text
                if point in names
                else f"input {', '.join(names)} held: " + text,
                input_refs=refs,
                source_fact_ids=tuple(hold.fy_fact_ids) + tuple(hold.ytd_fact_ids),
            )
        )
    return out


def write_holds(
    conn: psycopg.Connection, run_id: str, company_id: int, holds: Iterable[Hold]
) -> int:
    """Replace this rule's reason rows for the company in this run. Does not
    commit (the caller owns the transaction)."""
    holds = list(holds)
    names = canonical_names_by_concept(conn, {h.concept_id for h in holds})
    reasons: list[BlankReason] = []
    for h in holds:
        reasons.extend(blank_reasons(company_id, h, names.get(h.concept_id, [])))
    written = replace_rule_reasons(conn, run_id, company_id, RULE_ID, reasons)
    logger.info(
        "q4_vintage_hold.reasons_written",
        company_id=company_id,
        holds=len(holds),
        reasons=written,
    )
    return written
