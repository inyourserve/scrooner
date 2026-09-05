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
