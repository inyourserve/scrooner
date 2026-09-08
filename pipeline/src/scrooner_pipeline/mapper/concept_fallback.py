"""Concept-level fallback resolver (doc 40, 2026-09-02) -- a generalized
version of the "prefer resolved value A, else B" pattern already live in
`expanded_metrics.py`'s/`price_metrics.py`'s shares-outstanding fallback
(`_latest_instant_fact()` then `_load_shares_outstanding_fallback()` if
null), applied here to concept-vs-concept fallback instead of
concept-vs-external-table fallback.

Why this exists, not a change to resolve.py: resolve.py's `sum` mode has
no "prefer group A entirely, else group B entirely" logic -- it sums
every matched tag for a period unconditionally. `total_debt` is the ONE
canonical concept (of 44) using `sum` mode, and a real 360-company gap
exists where filers report split debt tags (LongTermDebtCurrent +
LongTermDebtNoncurrent) instead of the combined LongTermDebt tag
total_debt's mapping relies on -- but naively adding the split tags to
total_debt's own sum-mode mapping would double-count debt for the
~2,168 companies that report BOTH forms (confirmed live 2026-09-02,
and independently already named as a declined-unsafe-fix in
expanded_concepts.py's own docstring).

This module never touches resolve.py's own delete-then-reinsert-per-
company discipline for `total_debt`/`total_debt_split` -- it reads
their already-resolved `canonical_fact` rows (both populated normally
by resolve()) and writes a THIRD concept, `total_debt_resolved`, which
has zero `concept_mapping` rows and is therefore never touched by
resolve() at all. This is what keeps it safe to run resolve-facts again
later without silently wiping this module's own contribution -- a real
risk that would exist if this wrote into the original `total_debt`
concept_id instead.

Deliberately generalized (not hardcoded to total_debt's two concept
names) so a future `sum`-mode concept needing the same fallback reuses
this directly."""

import psycopg
import structlog

logger = structlog.get_logger()

# (primary concept name, fallback concept name, resolved concept name)
# -- add a new tuple here for any future case needing the same pattern.
FALLBACK_PAIRS: list[tuple[str, str, str]] = [
    ("total_debt", "total_debt_split", "total_debt_resolved"),
]

# Arithmetic fallback (migration 0047, 2026-09-07): unlike FALLBACK_PAIRS'
# simple "concept B fills where concept A is null" coalesce, this derives a
# missing value from TWO OTHER concepts (minuend - subtrahend) when the
# primary tag itself is absent. (resolved_name, primary_name, minuend_name,
# subtrahend_name, guard_min_value) -- guard_min_value, when not None,
# requires the minuend's own value to be strictly greater than it before
# trusting the derivation.
#
# The guard exists because of a real bug found live 2026-09-07: resolve.py's
# `first_match` can silently fall through to a lower-priority revenue tag
# reporting an authoritative-but-spurious $0 when the priority-1 tag's real,
# near-consensus value got marked non-authoritative over a trivial (<1%)
# cross-filing rounding difference (Stage 2e's own documented, correct-by-
# design conflict policy -- see pipeline/CLAUDE.md's 2026-08-19 total_debt
# entry for the identical mechanism on a different concept). Flowserve Corp
# (all 7 of its FY revenue rows resolve to exactly $0 despite being a real
# multi-billion-dollar company) is the clearest confirmed instance. Requiring
# `revenue > 0` before deriving gross_profit/cost_of_revenue means this bug
# structurally can't corrupt these derived values -- the affected periods
# just stay an honest blank cell instead of a wrong negative-billions figure.
# NOT fixed here -- that's a frozen resolve.py/dedupe.py boundary issue, see
# doc/learnings/2026-09-07-statement-table-coverage-and-revenue-zero-bug.md.
#
# Order matters: operating_expenses_resolved's minuend is
# gross_profit_resolved itself (for maximum coverage), so it must run AFTER
# gross_profit_resolved is populated -- this list's order is that order.
ARITHMETIC_FALLBACKS: list[tuple[str, str, str, str, int | None]] = [
    ("gross_profit_resolved", "gross_profit", "revenue", "cost_of_revenue", 0),
    ("cost_of_revenue_resolved", "cost_of_revenue", "revenue", "gross_profit", 0),
    ("operating_expenses_resolved", "operating_expenses", "gross_profit_resolved", "operating_income", None),
]


def _concept_id(conn: psycopg.Connection, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"canonical_concept {name!r} does not exist")
        return row[0]


def _load_facts(conn: psycopg.Connection, company_id: int, concept_id: int) -> dict[int, tuple]:
    """period_id -> (value, source_fact_ids)."""
    with conn.cursor() as cur:
        cur.execute(
            "select period_id, value, source_fact_ids from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s",
            (company_id, concept_id),
        )
        return {r[0]: (r[1], r[2]) for r in cur.fetchall()}


def resolve_fallback_for_company(conn: psycopg.Connection, company_id: int, primary_id: int, fallback_id: int, resolved_id: int) -> int:
    primary_facts = _load_facts(conn, company_id, primary_id)
    fallback_facts = _load_facts(conn, company_id, fallback_id)

    merged: dict[int, tuple] = dict(fallback_facts)
    merged.update(primary_facts)  # primary always wins where both exist

    with conn.cursor() as cur:
        cur.execute("delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", (company_id, resolved_id))
        if merged:
            cur.executemany(
                """
                insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                values (%(company_id)s, %(canonical_concept_id)s, %(period_id)s, %(value)s, %(source_fact_ids)s)
                """,
                [
                    {
                        "company_id": company_id,
                        "canonical_concept_id": resolved_id,
                        "period_id": period_id,
                        "value": value,
                        "source_fact_ids": source_fact_ids,
                    }
                    for period_id, (value, source_fact_ids) in merged.items()
                ],
            )
    return len(merged)


def resolve_fallbacks(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "errored": 0, "rows_written": 0}
    with conn.cursor() as cur:
        cur.execute("select id, cik from core.company where cik = any(%s)", (list(ciks),))
        companies = cur.fetchall()

    for primary_name, fallback_name, resolved_name in FALLBACK_PAIRS:
        primary_id = _concept_id(conn, primary_name)
        fallback_id = _concept_id(conn, fallback_name)
        resolved_id = _concept_id(conn, resolved_name)

        for company_id, cik in companies:
            stats["considered"] += 1
            try:
                rows = resolve_fallback_for_company(conn, company_id, primary_id, fallback_id, resolved_id)
                conn.commit()
                stats["ok"] += 1
                stats["rows_written"] += rows
            except Exception:
                logger.warning("concept_fallback.company_failed", cik=cik, pair=resolved_name, exc_info=True)
                stats["errored"] += 1
                conn.rollback()

    logger.info("concept_fallback.done", **stats)
    return stats


def resolve_arithmetic_fallback(
    conn: psycopg.Connection,
    resolved_id: int,
    primary_id: int,
    minuend_id: int,
    subtrahend_id: int,
    guard_min_value: int | None,
) -> int:
    """Set-based (not per-company-loop) by design -- this project's own
    established rule against a query-per-row-in-a-loop batch job (see
    pipeline/CLAUDE.md's restatements.py N+1 entry). One DELETE + one
    INSERT...SELECT covers the whole population regardless of company
    count. Idempotent: safe to rerun any time an upstream concept's own
    resolve-facts output changes."""
    params: dict = {
        "resolved_id": resolved_id,
        "primary_id": primary_id,
        "minuend_id": minuend_id,
        "subtrahend_id": subtrahend_id,
    }
    guard_clause = ""
    if guard_min_value is not None:
        guard_clause = "and m.value > %(guard_value)s"
        params["guard_value"] = guard_min_value

    with conn.cursor() as cur:
        cur.execute("delete from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s", params)
        cur.execute(
            f"""
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select company_id, %(resolved_id)s, period_id, value, source_fact_ids
            from analytics.canonical_fact
            where canonical_concept_id = %(primary_id)s
            union all
            select m.company_id, %(resolved_id)s, m.period_id, (m.value - s.value), m.source_fact_ids || s.source_fact_ids
            from analytics.canonical_fact m
            join analytics.canonical_fact s
                on s.company_id = m.company_id and s.period_id = m.period_id and s.canonical_concept_id = %(subtrahend_id)s
            where m.canonical_concept_id = %(minuend_id)s
                {guard_clause}
                and not exists (
                    select 1 from analytics.canonical_fact p
                    where p.company_id = m.company_id and p.period_id = m.period_id and p.canonical_concept_id = %(primary_id)s
                )
            """,
            params,
        )
        cur.execute("select count(*) from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s", params)
        count = cur.fetchone()[0]
    conn.commit()
    return count


def resolve_all_arithmetic_fallbacks(conn: psycopg.Connection) -> dict:
    stats = {"considered": len(ARITHMETIC_FALLBACKS), "rows_written": {}}
    for resolved_name, primary_name, minuend_name, subtrahend_name, guard in ARITHMETIC_FALLBACKS:
        resolved_id = _concept_id(conn, resolved_name)
        primary_id = _concept_id(conn, primary_name)
        minuend_id = _concept_id(conn, minuend_name)
        subtrahend_id = _concept_id(conn, subtrahend_name)
        count = resolve_arithmetic_fallback(conn, resolved_id, primary_id, minuend_id, subtrahend_id, guard)
        stats["rows_written"][resolved_name] = count
        logger.info("concept_fallback.arithmetic_done", concept=resolved_name, rows=count)
    return stats
