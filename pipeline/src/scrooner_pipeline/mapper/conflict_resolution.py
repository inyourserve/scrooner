"""Generic conflict-fill resolver (2026-09-09) -- migration 0059.

Found live investigating a real user report (Etsy's Q1/Q2/Q4 2025 revenue
blank on the company page): `normalizer/dedupe.py`'s Stage 2e conflict
policy is correct and deliberate ("2+ filings disagree on a period's
value -> mark ALL rows non-authoritative -> resolve() returns null",
pipeline/CLAUDE.md's 2026-08-19 total_debt entry already documents this
as intentional, not a bug), but leaves a real, sizeable number of
statement-table cells blank for EVERY concept, not just revenue -- scoped
live: 2,164 companies / 14,031 quarterly periods for revenue alone.

A first attempt at fixing this (per-company, self-pointing
`company_tag_preference` rows activating `tag_investigator._reconcile_by_
mode`) caused a real, measured regression -- 1,364 companies had their
`revenue_sanity_resolved` coverage DROP by ~28,000 periods, because a
company reporting revenue under 2-3 different tags across its history
(taxonomy drift, e.g. Apple: `SalesRevenueNet` pre-2018,
`RevenueFromContractWithCustomerExcludingAssessedTax` after) had its
preference point at only ONE of those tags, silently discarding every
period that legitimately resolved via a different tag. Reverted in full
before this module was written.

This module fixes the actual bug instead: it operates PER (company,
period), never per-company-tag, and is purely ADDITIVE (INSERT ... ON
CONFLICT DO NOTHING, never a DELETE) -- it can only fill an existing
null, never touch or remove a value any other writer (resolve() itself,
or an existing arithmetic-fallback concept like gross_profit_resolved)
already produced. This makes the Apple-shaped regression structurally
impossible: a period that already resolves via ANY tag is never touched.

Safety bar for auto-fill, calibrated against real evidence (Etsy verified
against yfinance -- the later-filed value matched exactly) and this
project's own repeated "small non-material cross-filing revision" finding
(Normalizer Day 5/dedupe.py's own docstring, ~6.6% of duplicate groups):
only fill when the worst-case disagreement across conflicting facts is
<=15%. Anything larger (a real, if rarer, case -- e.g. a genuine
reclassification, or a unit-scale bug) is left null rather than guessed,
same "flag, don't force" discipline as everywhere else in this project.
Tie-break among safely-close candidates is the highest fact_id (most
recently inserted row) -- the same convention `tag_investigator._
reconcile_by_mode` already uses, confirmed live to correlate with
most-recent-filing-date for Etsy's real conflicting facts.
"""

from decimal import Decimal

import psycopg
import structlog

logger = structlog.get_logger()

MAX_SAFE_RATIO = Decimal("1.15")

# (primary_concept_name, resolved_concept_name) -- the 24 statement-table
# rows (statements/classify.py's STATEMENT_LINES). The 5 that already have
# their own arithmetic/coalesce `_resolved` companion still go through this
# same fill pass -- it only ever inserts into currently-null slots, so it
# safely layers on top of whatever gross_profit_resolved/total_debt_resolved/
# etc. already populated, no special-casing needed.
CONFLICT_FILL_TARGETS: list[tuple[str, str]] = [
    ("revenue", "revenue_sanity_resolved"),
    ("cost_of_revenue", "cost_of_revenue_resolved"),
    ("gross_profit", "gross_profit_resolved"),
    ("operating_expenses", "operating_expenses_resolved"),
    ("total_debt", "total_debt_resolved"),
    ("operating_income", "operating_income_resolved"),
    ("interest_expense", "interest_expense_resolved"),
    ("income_before_tax", "income_before_tax_resolved"),
    ("income_tax_expense", "income_tax_expense_resolved"),
    ("net_income", "net_income_resolved"),
    ("diluted_eps", "diluted_eps_resolved"),
    ("cash_and_equivalents", "cash_and_equivalents_resolved"),
    ("current_assets", "current_assets_resolved"),
    ("ppe_net", "ppe_net_resolved"),
    ("total_assets", "total_assets_resolved"),
    ("current_liabilities", "current_liabilities_resolved"),
    ("total_liabilities", "total_liabilities_resolved"),
    ("stockholders_equity", "stockholders_equity_resolved"),
    ("cfo", "cfo_resolved"),
    ("capex", "capex_resolved"),
    ("cash_flow_investing", "cash_flow_investing_resolved"),
    ("cash_flow_financing", "cash_flow_financing_resolved"),
    ("dividends_paid", "dividends_paid_resolved"),
    ("share_buybacks", "share_buybacks_resolved"),
]


def _concept_id(conn: psycopg.Connection, name: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
        row = cur.fetchone()
        return row[0] if row else None


def _load_conflict_groups(conn: psycopg.Connection, primary_id: int) -> list[tuple]:
    """Every (company_id, period_id) where the primary concept's own
    mapped (non-rejected) tags have 2+ disagreeing core.fact values and
    NONE is authoritative -- the exact dedupe.py "flag, don't resolve"
    case. Returns one row per group with every (value, fact_id) pair so
    the safety check and tie-break can happen in Python."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.company_id, f.period_id, array_agg(f.value order by f.id), array_agg(f.id order by f.id)
            from core.fact f
            join core.concept c on c.id = f.concept_id
            join analytics.concept_mapping cm on cm.concept_id = c.id
            join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
            where cc.id = %s and cm.confidence != 'rejected'
            group by f.company_id, f.period_id
            having count(distinct f.value) > 1 and bool_or(f.is_authoritative) = false
            """,
            (primary_id,),
        )
        return cur.fetchall()


def _load_already_resolved(conn: psycopg.Connection, resolved_id: int) -> set[tuple[int, int]]:
    with conn.cursor() as cur:
        cur.execute(
            "select company_id, period_id from analytics.canonical_fact where canonical_concept_id = %s",
            (resolved_id,),
        )
        return {(row[0], row[1]) for row in cur.fetchall()}


def _safe_fill_value(values: list[Decimal], fact_ids: list[int]) -> tuple[Decimal, int] | None:
    """None if the worst-case disagreement exceeds MAX_SAFE_RATIO or any
    value is zero/negative (a ratio check needs a positive denominator to
    mean anything -- a sign flip or a zero is exactly the kind of larger,
    non-immaterial disagreement this function must NOT auto-resolve)."""
    if any(v <= 0 for v in values):
        return None
    worst_ratio = max(values) / min(values)
    if worst_ratio > MAX_SAFE_RATIO:
        return None
    # Highest fact_id among the values tied for "most extreme" isn't quite
    # right when 3+ distinct values exist -- simplest correct rule: the
    # single highest fact_id overall is the most-recently-filed fact,
    # regardless of how many distinct values are in the group.
    best_idx = max(range(len(fact_ids)), key=lambda i: fact_ids[i])
    return values[best_idx], fact_ids[best_idx]


def resolve_baseline_passthrough(conn: psycopg.Connection, primary_name: str, resolved_name: str) -> int:
    """Plain pass-through: copy the primary concept's own canonical_fact
    row into the resolved concept wherever the resolved concept doesn't
    already have one for that (company, period) -- set-based, ON CONFLICT
    DO NOTHING, never a delete. For the 5 statement-table concepts with
    their own arithmetic-fallback/tag-preference populate step
    (concept_fallback.py, tag_investigator.py), THIS FUNCTION MUST RUN
    AFTER those -- they each do a scoped or full delete-then-reinsert of
    their resolved concept, which would silently wipe a passthrough row
    inserted before them. For the 19 concepts with no other populate
    mechanism, this is the only baseline they get; conflict-fill (below)
    then layers on top of it, additive-only, and is always safe to run
    last since nothing downstream deletes from these resolved concepts."""
    primary_id = _concept_id(conn, primary_name)
    resolved_id = _concept_id(conn, resolved_name)
    if primary_id is None or resolved_id is None:
        return 0
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select company_id, %(resolved_id)s, period_id, value, source_fact_ids
            from analytics.canonical_fact
            where canonical_concept_id = %(primary_id)s
            on conflict (company_id, canonical_concept_id, period_id) do nothing
            """,
            {"resolved_id": resolved_id, "primary_id": primary_id},
        )
        inserted = cur.rowcount
    conn.commit()
    logger.info("conflict_resolution.baseline_done", primary=primary_name, resolved=resolved_name, inserted=inserted)
    return inserted


def resolve_conflict_fill(conn: psycopg.Connection, primary_name: str, resolved_name: str) -> dict:
    """Purely additive: INSERT ... ON CONFLICT DO NOTHING into
    `resolved_name` for every (company, period) that's (a) a genuine
    dedupe.py conflict on `primary_name`'s own tags, (b) not already
    covered by whatever the resolved concept already holds (its own
    baseline copy of the primary, or a prior arithmetic-fallback pass),
    and (c) safely close enough to auto-resolve. Idempotent and safe to
    run in any order relative to resolve-facts/concept_fallback -- it
    never deletes, so a rerun of any other stage can't be silently undone
    by this one, and this one can't silently undo any other stage."""
    primary_id = _concept_id(conn, primary_name)
    resolved_id = _concept_id(conn, resolved_name)
    if primary_id is None or resolved_id is None:
        return {"primary": primary_name, "skipped": "concept not found"}

    groups = _load_conflict_groups(conn, primary_id)
    already = _load_already_resolved(conn, resolved_id)

    to_insert = []
    unsafe = 0
    for company_id, period_id, values, fact_ids in groups:
        if (company_id, period_id) in already:
            continue
        filled = _safe_fill_value(list(values), list(fact_ids))
        if filled is None:
            unsafe += 1
            continue
        value, fact_id = filled
        to_insert.append(
            {"company_id": company_id, "resolved_id": resolved_id, "period_id": period_id, "value": value, "fact_id": fact_id}
        )

    if to_insert:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                values (%(company_id)s, %(resolved_id)s, %(period_id)s, %(value)s, array[%(fact_id)s]::bigint[])
                on conflict (company_id, canonical_concept_id, period_id) do nothing
                """,
                to_insert,
            )
        conn.commit()

    stats = {"conflict_groups": len(groups), "already_resolved": len(groups) - len(to_insert) - unsafe, "filled": len(to_insert), "unsafe_skipped": unsafe}
    logger.info("conflict_resolution.done", primary=primary_name, resolved=resolved_name, **stats)
    return stats


# The 5 concepts with their own existing populate step (resolve_company_
# tag_preferences / concept_fallback.py's arithmetic fallback) -- skip the
# baseline passthrough for these, since running it here (this function is
# meant to run standalone/last in the pipeline) could otherwise race an
# out-of-order rerun of their real populate step's own delete-then-
# reinsert. Conflict-fill itself is still safe and still runs for them
# (it never deletes), same as any other target.
_HAS_OWN_POPULATE_STEP = {"revenue_sanity_resolved", "cost_of_revenue_resolved", "gross_profit_resolved", "operating_expenses_resolved", "total_debt_resolved"}


def resolve_all_conflict_fills(conn: psycopg.Connection) -> dict:
    totals = {"baseline_filled": 0, "filled": 0, "unsafe_skipped": 0}
    per_concept = {}
    for primary_name, resolved_name in CONFLICT_FILL_TARGETS:
        baseline_count = 0
        if resolved_name not in _HAS_OWN_POPULATE_STEP:
            baseline_count = resolve_baseline_passthrough(conn, primary_name, resolved_name)
        stats = resolve_conflict_fill(conn, primary_name, resolved_name)
        stats["baseline_filled"] = baseline_count
        per_concept[primary_name] = stats
        totals["baseline_filled"] += baseline_count
        totals["filled"] += stats.get("filled", 0)
        totals["unsafe_skipped"] += stats.get("unsafe_skipped", 0)
    logger.info("conflict_resolution.all_done", **totals)
    return {"totals": totals, "per_concept": per_concept}
