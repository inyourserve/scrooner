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

from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()

# (primary concept name, fallback concept name, resolved concept name,
# overlap_tag) -- overlap_tag is the one raw XBRL tag whose presence in a
# period signals genuine double-count risk between primary and fallback
# (None if primary and fallback can never legitimately coexist for the
# same real-world figure, in which case every case is summed). Add a new
# tuple here for any future case needing the same pattern.
FALLBACK_PAIRS: list[tuple[str, str, str, str | None]] = [
    ("total_debt", "total_debt_split", "total_debt_resolved", "LongTermDebt"),
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


def resolve_fallback_for_company(
    conn: psycopg.Connection, company_id: int, primary_id: int, fallback_id: int, resolved_id: int, overlap_tag: str | None = None
) -> int:
    """`overlap_tag`, added 2026-09-13: a real, sized bug found investigating
    a user report about a specific company's total_debt looking too low
    (OGE Energy: $492M shown vs a real $5.86B) -- "primary always wins" is
    only correct when the primary concept's own sum-mode tags and the
    fallback concept's tags represent the SAME real-world figure via two
    different reporting conventions (which is true for total_debt's
    LongTermDebt vs LongTermDebtCurrent+LongTermDebtNoncurrent split, the
    ONE genuine double-count risk this module was built to guard against).
    But total_debt's OTHER sum-mode tags (DebtCurrent, SecuredDebtCurrent,
    ShortTermBorrowings) are NEVER part of that overlap -- a company
    reporting short-term debt under those tags AND its long-term debt only
    under the split convention (no combined LongTermDebt tag at all, OGE
    Energy's real shape) needs both ADDED together, not one arbitrarily
    preferred over the other. `overlap_tag` names the one raw XBRL tag
    whose presence signals genuine double-count risk with the fallback
    concept -- when it's not present for a given period, primary and
    fallback are summed instead of one replacing the other. Verified
    live before shipping: reproduces OGE Energy's real $5.862B exactly,
    and checked against the full population's own already-cached yfinance
    comparison data -- 383 net-new matches within 10% of yfinance's own
    reported figure, 6 minor regressions (periods that already matched
    loosely and still do, just via a different exact number)."""
    primary_facts = _load_facts(conn, company_id, primary_id)
    fallback_facts = _load_facts(conn, company_id, fallback_id)

    overlap_periods: set[int] = set()
    if overlap_tag is not None and fallback_facts:
        with conn.cursor() as cur:
            cur.execute(
                """
                select distinct f.period_id from core.fact f
                join core.concept c on c.id = f.concept_id
                where f.company_id = %s and c.tag = %s and f.is_authoritative = true
                """,
                (company_id, overlap_tag),
            )
            overlap_periods = {row[0] for row in cur.fetchall()}

    merged: dict[int, tuple] = dict(fallback_facts)
    for period_id, (value, source_fact_ids) in primary_facts.items():
        if period_id in merged and period_id not in overlap_periods:
            fallback_value, fallback_sources = merged[period_id]
            merged[period_id] = (value + fallback_value, list(source_fact_ids) + list(fallback_sources))
        else:
            merged[period_id] = (value, source_fact_ids)  # primary wins on genuine overlap, or is the only value present

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

    for primary_name, fallback_name, resolved_name, overlap_tag in FALLBACK_PAIRS:
        primary_id = _concept_id(conn, primary_name)
        fallback_id = _concept_id(conn, fallback_name)
        resolved_id = _concept_id(conn, resolved_name)

        for company_id, cik in companies:
            stats["considered"] += 1
            try:
                rows = resolve_fallback_for_company(conn, company_id, primary_id, fallback_id, resolved_id, overlap_tag)
                conn.commit()
                stats["ok"] += 1
                stats["rows_written"] += rows
            except Exception:
                logger.warning("concept_fallback.company_failed", cik=cik, pair=resolved_name, exc_info=True)
                stats["errored"] += 1
                # Found live 2026-09-15, all 4 parallel workers of a
                # full-population rollout crashed identically: when the
                # ORIGINAL exception is a dead connection (a real,
                # documented, recurring Supabase pooler drop), calling
                # conn.rollback() on that same dead connection raises a
                # SECOND, uncaught OperationalError, which propagates out
                # of this function and kills the entire remaining batch --
                # the exact bug class already found and fixed once in
                # common/errors.py's log_error() (2026-09-03): a contract
                # ("one company's failure never aborts the batch") that
                # was never actually tested against its own failure path.
                # Reconnect instead of trusting rollback() to succeed on
                # a connection that may already be gone -- same idiom as
                # yfinance_industry.py's _write_batch().
                try:
                    conn.rollback()
                except psycopg.OperationalError:
                    logger.warning("concept_fallback.connection_dropped_reconnecting", cik=cik)
                    conn = psycopg.connect(settings.database_url)

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


# depreciation_and_amortization_resolved (2026-09-13): found investigating
# a "closing the saga" sanity sweep of every financial-statement row
# against yfinance -- resolve.py's `first_match` (DepreciationAndAmortization
# priority 1, DepreciationDepletionAndAmortization priority 2) assumes
# priority 1, when present, is always the more complete figure. Confirmed
# live this is false for a real, sized minority: Amgen tags
# DepreciationAndAmortization=$220M (PP&E depreciation only) AND
# DepreciationDepletionAndAmortization=$1,116M (the real total, matching
# yfinance exactly) for the SAME period. Verified before shipping against
# every period with a cached yfinance comparison: taking the max of the
# two raw tags (never touching resolve.py's own frozen priority order,
# which still governs the plain `depreciation_and_amortization` concept)
# raised the match rate from 64.1% to 80.1% (1,506->1,884 of 2,351 periods
# within 5% of yfinance), with only 20 regressions -- a company where the
# smaller value was actually the more correct one is possible in principle,
# but not common enough in the real data checked to outweigh the fix.
# Never double-counts: both tags purport to describe the SAME total D&A
# figure via two different reporting conventions, so taking whichever is
# larger (or the only one present) is the correct combination rule here --
# unlike total_debt's two tag groups, which can be genuinely ADDITIVE
# pieces of one total (see resolve_fallback_for_company's overlap_tag).
def resolve_depreciation_and_amortization_max(conn: psycopg.Connection) -> int:
    resolved_id = _concept_id(conn, "depreciation_and_amortization_resolved")
    with conn.cursor() as cur:
        cur.execute("delete from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s", {"resolved_id": resolved_id})
        cur.execute(
            """
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select
                company_id, %(resolved_id)s, period_id,
                case when p2_value is null or p1_value >= p2_value then p1_value else p2_value end,
                case when p2_value is null or p1_value >= p2_value then p1_fact_ids else p2_fact_ids end
            from (
                select
                    f.company_id, f.period_id,
                    max(f.value) filter (where c.tag = 'DepreciationAndAmortization') as p1_value,
                    array_agg(f.id) filter (where c.tag = 'DepreciationAndAmortization') as p1_fact_ids,
                    max(f.value) filter (where c.tag = 'DepreciationDepletionAndAmortization') as p2_value,
                    array_agg(f.id) filter (where c.tag = 'DepreciationDepletionAndAmortization') as p2_fact_ids
                from core.fact f
                join core.concept c on c.id = f.concept_id
                where c.tag in ('DepreciationAndAmortization', 'DepreciationDepletionAndAmortization')
                    and f.is_authoritative = true
                group by f.company_id, f.period_id
            ) both_tags
            where p1_value is not null or p2_value is not null
            """,
            {"resolved_id": resolved_id},
        )
        cur.execute("select count(*) from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s", {"resolved_id": resolved_id})
        count = cur.fetchone()[0]
    conn.commit()
    logger.info("concept_fallback.depreciation_and_amortization_max_done", rows=count)
    return count


# capex_resolved augmentation (2026-09-13): found the same sanity sweep --
# capex's own mapping (resolve.py, first_match) only ever reads
# PaymentsToAcquirePropertyPlantAndEquipment, but a real, growing set of
# companies also capitalize internal-use software development separately
# under PaymentsToAcquireSoftware -- a genuinely DIFFERENT kind of spend,
# never double-counted with PP&E purchases (confirmed: McKesson's real
# $106M PP&E + $90M software = $196M, matching yfinance's Capital
# Expenditure exactly). Verified broadly before shipping: of the 130
# periods with both a cached yfinance comparison AND a real
# PaymentsToAcquireSoftware fact, matches within 5% rose from 24 to 105,
# 5 regressions. Runs BEFORE conflict_resolution.py's generic
# conflict-fill pass for capex (capex_resolved is in
# conflict_resolution._HAS_OWN_POPULATE_STEP) -- that pass is purely
# additive (INSERT ... ON CONFLICT DO NOTHING) and only ever fills a
# period this function left untouched (a genuine dedupe.py conflict on
# the PP&E tag itself, unrelated to software), so running it after this
# one is always safe.
def resolve_capex_with_software(conn: psycopg.Connection) -> int:
    capex_id = _concept_id(conn, "capex")
    resolved_id = _concept_id(conn, "capex_resolved")
    with conn.cursor() as cur:
        cur.execute("delete from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s", {"resolved_id": resolved_id})
        cur.execute(
            """
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select
                cf.company_id, %(resolved_id)s, cf.period_id,
                cf.value + coalesce(sw.sw_value, 0),
                cf.source_fact_ids || coalesce(sw.sw_fact_ids, array[]::bigint[])
            from analytics.canonical_fact cf
            left join (
                select f.company_id, f.period_id, sum(f.value) as sw_value, array_agg(f.id) as sw_fact_ids
                from core.fact f
                join core.concept c on c.id = f.concept_id
                where c.tag = 'PaymentsToAcquireSoftware' and f.is_authoritative = true
                group by f.company_id, f.period_id
            ) sw on sw.company_id = cf.company_id and sw.period_id = cf.period_id
            where cf.canonical_concept_id = %(capex_id)s
            """,
            {"resolved_id": resolved_id, "capex_id": capex_id},
        )
        cur.execute("select count(*) from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s", {"resolved_id": resolved_id})
        count = cur.fetchone()[0]
    conn.commit()
    logger.info("concept_fallback.capex_with_software_done", rows=count)
    return count


# employee_count_resolved (2026-09-12): a third, differently-shaped
# fallback, distinct from both FALLBACK_PAIRS (concept-vs-concept) and
# ARITHMETIC_FALLBACKS (concept-vs-arithmetic-derivation) above -- this
# one falls back to two EXTERNAL tables, neither of which is a
# canonical_concept: core.employee_headcount_disclosure (10-K prose
# extraction, built 2026-08-31/09-01, already covering 2,951 companies
# with zero new fetches -- it just never got wired into the concept the
# registry/coverage system actually tracks) and core.company.y_employee_count
# (yfinance's fullTimeEmployees, same y_-prefixed-column idiom as
# y_sector/y_industry/y_about_text/y_website). Company-level, not
# period-level: prose/yfinance each give one point-in-time count, not a
# real historical series the way XBRL facts do, so they fill a company's
# gap only when XBRL has NOTHING for that company at all -- never
# overriding a real XBRL period, and never invented as a fake series of
# identical values across multiple periods.
def _find_or_create_instant_period(conn: psycopg.Connection, company_id: int, as_of: date) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select id from core.period where company_id = %s and start_date = %s and end_date = %s and period_type = 'instant'",
            (company_id, as_of, as_of),
        )
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            """
            insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
            values (%s, %s, %s, 'instant', %s, 'FY')
            on conflict (company_id, start_date, end_date, period_type) do nothing
            returning id
            """,
            (company_id, as_of, as_of, as_of.year),
        )
        row = cur.fetchone()
        if row:
            return row[0]
        # Lost the on-conflict race (a concurrent insert for the same
        # company/date) -- the row now exists, just re-select it.
        cur.execute(
            "select id from core.period where company_id = %s and start_date = %s and end_date = %s and period_type = 'instant'",
            (company_id, as_of, as_of),
        )
        return cur.fetchone()[0]


def resolve_employee_count_fallback(conn: psycopg.Connection, ciks: set[str]) -> dict:
    primary_id = _concept_id(conn, "employee_count")
    resolved_id = _concept_id(conn, "employee_count_resolved")

    with conn.cursor() as cur:
        cur.execute("select id, cik from core.company where cik = any(%s)", (list(ciks),))
        companies = cur.fetchall()

    stats = {"considered": 0, "from_xbrl": 0, "from_prose": 0, "from_yfinance": 0, "still_null": 0, "errored": 0}
    for company_id, cik in companies:
        stats["considered"] += 1
        try:
            merged: dict[int, tuple] = dict(_load_facts(conn, company_id, primary_id))
            if merged:
                stats["from_xbrl"] += 1

            if not merged:
                with conn.cursor() as cur:
                    cur.execute(
                        "select report_date, headcount from core.employee_headcount_disclosure where company_id = %s order by report_date desc limit 1",
                        (company_id,),
                    )
                    prose_row = cur.fetchone()
                if prose_row:
                    report_date, headcount = prose_row
                    period_id = _find_or_create_instant_period(conn, company_id, report_date)
                    merged[period_id] = (Decimal(headcount), [])
                    stats["from_prose"] += 1

            if not merged:
                with conn.cursor() as cur:
                    cur.execute("select y_employee_count from core.company where id = %s", (company_id,))
                    y_row = cur.fetchone()
                if y_row and y_row[0]:
                    period_id = _find_or_create_instant_period(conn, company_id, date.today())
                    merged[period_id] = (Decimal(y_row[0]), [])
                    stats["from_yfinance"] += 1

            if not merged:
                stats["still_null"] += 1

            with conn.cursor() as cur:
                cur.execute(
                    "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s",
                    (company_id, resolved_id),
                )
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
            conn.commit()
        except Exception:
            logger.warning("concept_fallback.employee_count_company_failed", cik=cik, exc_info=True)
            stats["errored"] += 1
            conn.rollback()

    logger.info("concept_fallback.employee_count_resolved_done", **stats)
    return stats
