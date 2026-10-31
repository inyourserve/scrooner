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
           WOULD catch (stats held_mixed_vintage / held_sign_conflict /
           held_quarters_vs_ytd)
  on       the cell is not derived, an existing derived Q4 for it is demoted
           (never deleted: derived._retire_derived), and a reason row is written
           to analytics.cell_blank_reason for the concept's canonical name(s)
           and for the statement-fallback concepts derived from them.

Tolerance: core.fact stores no XBRL `decimals`, so the evaluator needs a stated
rounding tolerance. A scale-free tolerance cannot work: NVIDIA's rounding gaps
(a 9M YTD of 327 vs Q1+Q2+Q3 of 326, both in millions; or 630,587,000 in one
10-K vs 631,000,000 in the next after a switch to millions) are 0.3% to 4.8%
of the line, while PM's real recast (3,412 vs 3,429) is 0.5%. Checked on 10
NVDA/AAPL/AMD holds, 2026-10-31: all 10 were rounding, 0 were recasts. So the
slack is ABSOLUTE and per company: 1.5 units of the company's own presentation
scale (the median trailing-zero exponent of its FY duration facts, capped at
millions). A sum of three rounded quarters can differ from the rounded total by
at most 1.5 units; a difference above that is a different number. PM: 17M gap
vs 1.5M slack -> held. NVDA: 1M gap vs 1.5M slack -> derived.
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
    LOAD_SQL,
    YTD9_MAX_DAYS,
    YTD9_MIN_DAYS,
    Fact,
    Q4Candidate,
    Tolerance,
    _fy_groups,
    evaluate_cell,
)

logger = structlog.get_logger()

RULE_ID = RULE_SAME_VINTAGE_DERIVATION
# Relative part only; the absolute part is set per company by rounding_tolerance_for().
HOLD_TOLERANCE = Tolerance(rel=Decimal("0.0005"), abs_tol=Decimal("0"))
ROUNDING_UNITS_SLACK = Decimal("1.5")
MAX_SCALE_EXPONENT = 6  # millions: no filer presents USD coarser than that


def presentation_scale(values: Iterable[Decimal]) -> int:
    """Median exponent of the trailing zeros of the values (0 for 1,234;
    3 for 1,234,000; 6 for 1,234,000,000), clamped to [0, MAX_SCALE_EXPONENT].
    A round number (500,000,000) has more trailing zeros than the filer's
    precision, which is why the median over many values is used, not the max."""
    exps: list[int] = []
    for v in values:
        if v == 0:
            continue
        e = v.normalize().as_tuple().exponent
        if isinstance(e, int):
            exps.append(max(0, min(MAX_SCALE_EXPONENT, e)))
    if not exps:
        return 0
    exps.sort()
    return exps[len(exps) // 2]


def company_presentation_scale(conn: psycopg.Connection, company_id: int) -> int:
    """presentation_scale over the company's authoritative FY duration USD facts."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.value from core.fact f
            join core.period p on p.id = f.period_id
            join core.unit u on u.id = f.unit_id
            where f.company_id = %s and p.period_type = 'duration' and p.fiscal_period = 'FY'
              and f.is_authoritative and not f.is_derived and u.unit_name = 'usd'
            """,
            (company_id,),
        )
        return presentation_scale(Decimal(r[0]) for r in cur.fetchall())


# evaluator verdict -> (stat key in derive_q4, reason_code). "Mixed vintage" is
# reserved for a real recast; the two other groups have their own codes
# (chief of staff, 2026-10-31): the 9M-YTD path and the Q1+Q2+Q3 path giving a
# different Q4 beyond the cell's own rounding is the filer's numbers not adding
# up within one year, not a vintage problem.
QUARTERS_VS_YTD = "ytd9_and_chain_disagree"
HOLD_CODES: dict[str, tuple[str, str]] = {
    BLOCKED_MIXED: ("held_mixed_vintage", "q4_inputs_mixed_vintage"),
    BLOCKED_SIGN: ("held_sign_conflict", "q4_input_sign_conflict"),
    QUARTERS_VS_YTD: ("held_quarters_vs_ytd", "quarters_do_not_sum_to_ytd"),
}
STAT_KEYS = tuple(v[0] for v in HOLD_CODES.values())


def hold_key(candidate: Q4Candidate) -> str:
    """Which HOLD_CODES entry a held candidate falls under."""
    if (
        candidate.category == BLOCKED_MIXED
        and candidate.block_reason == QUARTERS_VS_YTD
    ):
        return QUARTERS_VS_YTD
    return candidate.category


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
    tolerance: dict | None = None

    @property
    def hold_kind(self) -> str:
        if self.category == BLOCKED_MIXED and self.block_reason == QUARTERS_VS_YTD:
            return QUARTERS_VS_YTD
        return self.category

    @property
    def stat_key(self) -> str:
        return HOLD_CODES[self.hold_kind][0]

    @property
    def reason_code(self) -> str:
        return HOLD_CODES[self.hold_kind][1]


def hold_category(candidate: Q4Candidate | None) -> str | None:
    """The evaluator category that makes derive_q4 hold, or None. Only the
    mixed-vintage and sign-conflict categories hold: a cell the evaluator
    cannot derive for other reasons (no FY, no YTD, non-additive) is
    derive_q4's own business."""
    if candidate is None or candidate.category not in (BLOCKED_MIXED, BLOCKED_SIGN):
        return None
    return candidate.category


def cell_scale(values: Iterable[Decimal], company_scale: int) -> int:
    """Presentation scale of ONE cell's copies: the coarsest trailing-zero
    exponent among them, but never above (magnitude exponent - 1) so a lone
    round number cannot widen the slack, and never below the company's own
    scale. AAPL reports interest expense YTDs to the nearest 100M while its
    quarters are in millions: 2,200 vs 695+742+780 = 2,217 is rounding at
    that cell's scale (8), not a different number."""
    vals = [abs(v) for v in values if v != 0]
    if not vals:
        return company_scale
    exps = [v.normalize().as_tuple().exponent for v in vals]
    coarsest = max(e for e in exps if isinstance(e, int))
    magnitude_cap = max(vals).adjusted() - 1
    return max(company_scale, min(coarsest, magnitude_cap, MAX_SCALE_EXPONENT + 3))


def _tol(scale: int) -> Tolerance:
    return Tolerance(
        rel=HOLD_TOLERANCE.rel, abs_tol=ROUNDING_UNITS_SLACK * (Decimal(10) ** scale)
    )


def load_vintage_categories(
    conn: psycopg.Connection,
    company_id: int,
    concept_ids: Collection[int],
    *,
    company_scale: int | None = None,
) -> dict[tuple[int, str, date], Q4Candidate]:
    """(concept_id, unit_name, fiscal_year_start) -> evaluator verdict for one
    company. Read-only; every concept is evaluated as additive because
    derive_q4 applies its own non-additive gate before asking. Each cell is
    evaluated with its own tolerance (cell_scale), floored at the company's
    presentation scale (presentation_scale over its FY facts)."""
    if not concept_ids:
        return {}
    if company_scale is None:
        company_scale = company_presentation_scale(conn, company_id)
    with conn.cursor() as cur:
        cur.execute(
            LOAD_SQL,
            {
                "company_ids": [company_id],
                "concept_ids": sorted(set(concept_ids)),
                "ytd_min": YTD9_MIN_DAYS,
                "ytd_max": YTD9_MAX_DAYS,
            },
        )
        rows = cur.fetchall()
    by_key: dict[tuple[int, str], list[Fact]] = defaultdict(list)
    for fid, _cid, concept, unit, value, acc, fdate, start, end, auth, fp in rows:
        by_key[(concept, unit)].append(
            Fact(fid, Decimal(value), acc, fdate, start, end, bool(auth), fp, unit)
        )
    out: dict[tuple[int, str, date], Q4Candidate] = {}
    for (concept, unit), facts in sorted(by_key.items()):
        for fy_start, group in sorted(_fy_groups(facts).items()):
            cand = evaluate_cell(
                group,
                company_id=company_id,
                concept_id=concept,
                additive=True,
                tol=_tol(cell_scale((f.value for f in group), company_scale)),
                unit=unit,
                context_facts=facts,
            )
            out[(concept, unit, fy_start)] = cand
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
        tolerance=dict(candidate.tolerance or {}),
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
    if hold.hold_kind == QUARTERS_VS_YTD:
        lead = "Q4 not derived: FY minus 9M YTD and FY minus Q1+Q2+Q3 give different Q4 values beyond the cell's rounding"
    elif hold.hold_kind == BLOCKED_SIGN:
        lead = "Q4 not derived: two filed copies of an input differ only by sign"
    else:
        lead = "Q4 not derived: FY and 9M/Q1-Q3 inputs are not from one filing basis (recast)"
    text = (
        f"{lead} ({hold.category}; {hold.block_reason or 'no evidenced same-vintage pairing'}). "
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
        "tolerance": dict(hold.tolerance or {}),
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
