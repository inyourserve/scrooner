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

from scrooner_pipeline.common.errors import safe_rollback

logger = structlog.get_logger()

# (primary concept name, fallback concept name, resolved concept name,
# overlap_tag) -- overlap_tag is the one raw XBRL tag whose presence in a
# period signals genuine double-count risk between primary and fallback
# (None if primary and fallback can never legitimately coexist for the
# same real-world figure, in which case every case is summed). Add a new
# tuple here for any future case needing the same pattern.
FALLBACK_PAIRS: list[tuple[str, str, str, str | None]] = [
    # total_debt used to live here -- replaced 2026-09-27 by
    # resolve_total_debt_components() below. See its docstring.
]

# Component-based total debt (2026-09-27). One us-gaap tag per role, in
# preference order. These are ALTERNATIVE spellings of the same component,
# never summed with each other.
DEBT_ALL_IN = ("DebtLongtermAndShorttermCombinedAmount",)  # company's own stated total
DEBT_ALL_IN_LEASE = (
    "DebtAndCapitalLeaseObligations",
)  # total incl. finance leases, last resort
DEBT_LTD_INCL_CURRENT = (
    "LongTermDebt",
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
)
DEBT_LTD_NONCURRENT = (
    "LongTermDebtNoncurrent",
    "LongTermDebtAndCapitalLeaseObligations",
)
DEBT_LTD_CURRENT = (
    "LongTermDebtCurrent",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
)
DEBT_CURRENT_ALL = ("DebtCurrent",)  # short-term borrowings + current LTD
DEBT_SHORT_TERM = ("ShortTermBorrowings", "CommercialPaper")
# Read only as a cross-check (rule 2's tiebreaker), never stored as the value.
DEBT_CARRYING_CHECK = ("DebtInstrumentCarryingAmount",)
TOTAL_DEBT_TAGS = (
    DEBT_ALL_IN
    + DEBT_ALL_IN_LEASE
    + DEBT_LTD_INCL_CURRENT
    + DEBT_LTD_NONCURRENT
    + DEBT_LTD_CURRENT
    + DEBT_CURRENT_ALL
    + DEBT_SHORT_TERM
    + DEBT_CARRYING_CHECK
)

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
    # subtrahend widened to cost_of_revenue_resolved (was raw
    # cost_of_revenue), 2026-09-21: cost_of_revenue_resolved already
    # strictly a superset of raw cost_of_revenue (its own baseline
    # passthrough copies every raw row verbatim, see resolve_arithmetic_
    # fallback's own first INSERT branch), plus it now also carries
    # values `parsers/cost_of_revenue_parser.py` finds via rendered-
    # report dimensional summation for companies with NO raw tag at all
    # (Hyatt Hotels: real Cost of Revenue exists only as 3 separate
    # per-segment XBRL facts the standard Company Facts API strips
    # entirely -- doc 22's already-documented limitation, confirmed here
    # for a new concept family). Reading the resolved concept instead of
    # the raw one only ever WIDENS this derivation's own input coverage,
    # never narrows it.
    ("gross_profit_resolved", "gross_profit", "revenue", "cost_of_revenue_resolved", 0),
    ("cost_of_revenue_resolved", "cost_of_revenue", "revenue", "gross_profit", 0),
    (
        "operating_expenses_resolved",
        "operating_expenses",
        "gross_profit_resolved",
        "operating_income",
        None,
    ),
]


def _concept_id(conn: psycopg.Connection, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (name,)
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"canonical_concept {name!r} does not exist")
        return row[0]


def _load_facts(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> dict[int, tuple]:
    """period_id -> (value, source_fact_ids)."""
    with conn.cursor() as cur:
        cur.execute(
            "select period_id, value, source_fact_ids from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s",
            (company_id, concept_id),
        )
        return {r[0]: (r[1], r[2]) for r in cur.fetchall()}


def resolve_fallback_for_company(
    conn: psycopg.Connection,
    company_id: int,
    primary_id: int,
    fallback_id: int,
    resolved_id: int,
    overlap_tag: str | None = None,
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
            merged[period_id] = (
                value + fallback_value,
                list(source_fact_ids) + list(fallback_sources),
            )
        else:
            merged[period_id] = (
                value,
                source_fact_ids,
            )  # primary wins on genuine overlap, or is the only value present

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
    return len(merged)


def resolve_fallbacks(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "errored": 0, "rows_written": 0}
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where cik = any(%s)", (list(ciks),)
        )
        companies = cur.fetchall()

    for primary_name, fallback_name, resolved_name, overlap_tag in FALLBACK_PAIRS:
        primary_id = _concept_id(conn, primary_name)
        fallback_id = _concept_id(conn, fallback_name)
        resolved_id = _concept_id(conn, resolved_name)

        for company_id, cik in companies:
            stats["considered"] += 1
            try:
                rows = resolve_fallback_for_company(
                    conn, company_id, primary_id, fallback_id, resolved_id, overlap_tag
                )
                conn.commit()
                stats["ok"] += 1
                stats["rows_written"] += rows
            except Exception:
                logger.warning(
                    "concept_fallback.company_failed",
                    cik=cik,
                    pair=resolved_name,
                    exc_info=True,
                )
                stats["errored"] += 1
                # safe_rollback() tolerates a dead connection (a real,
                # recurring Supabase pooler drop) instead of letting
                # conn.rollback() itself raise a second, uncaught
                # OperationalError that would kill the entire remaining
                # batch -- found live 2026-09-15 across 4 parallel
                # full-population workers; see common/errors.py's own
                # docstring for the full history.
                conn = safe_rollback(conn, stage="concept_fallback", cik=cik)

    debt_stats = resolve_total_debt_components(conn, ciks)
    stats["total_debt_components"] = debt_stats
    logger.info("concept_fallback.done", **stats)
    return stats


def compute_total_debt(
    facts: dict[str, tuple[Decimal, int]],
) -> tuple[Decimal, list[int], str] | None:
    """Total debt for ONE balance-sheet date from the company's own tags
    (tag -> (value, fact_id)). Returns (value, source_fact_ids, path) or
    None when the tags can't give a total -- a blank beats a wrong number.

    Replaces the old sum-mode `total_debt` + split-pair fallback, which
    summed whichever mapped tags happened to exist: Chevron 2026-06-30 got
    $0.4B (ShortTermBorrowings alone; its $36.7B long-term debt was under
    an unmapped tag) and 2025-12-31 double-counted ShortTermBorrowings on
    top of DebtCurrent, which already contains it.

    Rules, each from real filings (checked against yfinance's Total Debt
    minus Capital Lease Obligations, 16,064 company-dates, 2026-09-27;
    within 5%: 42.3% -> 50.6%, wrong: 12.6% -> 9.6%):
      1. DebtLongtermAndShorttermCombinedAmount -- the company's own total.
      2. LTD including current maturities + short-term borrowings, unless
         the "including current" tag equals LongTermDebtNoncurrent (the
         company uses LongTermDebt for the noncurrent part only --
         Diamondback, Cheniere) or short-term borrowings equal the current
         LTD portion (same debt tagged twice -- Boxlight).
      3. Noncurrent LTD + DebtCurrent (which already holds short-term
         borrowings and current LTD).
      4. Noncurrent LTD + current LTD + short-term borrowings.
      5. DebtAndCapitalLeaseObligations (all-in incl. finance leases).
    Short-term borrowings alone are NOT a total (69% wrong vs yfinance --
    T-Mobile's long-term debt is under a custom tag Company Facts omits),
    so that case returns None.

    LongTermDebt + DebtCurrent with nothing else is ambiguous (is
    LongTermDebt incl. current?). DebtCurrent is added only when the
    company's own DebtInstrumentCarryingAmount equals the sum within 1%
    (Tesla: 7.721 + 1.340 = 9.061 vs 9.08) -- 7/9 right that way, 0/9 for
    LongTermDebt alone; without that confirmation LongTermDebt alone wins
    (16 vs 10)."""

    def pick(tags: tuple[str, ...]) -> tuple[Decimal, int] | None:
        for t in tags:
            if t in facts:
                return facts[t]
        return None

    def done(parts, path):
        parts = [p for p in parts if p is not None]
        return sum((p[0] for p in parts), Decimal(0)), [p[1] for p in parts], path

    all_in = pick(DEBT_ALL_IN)
    if all_in is not None:
        return done([all_in], "all_in")

    short = pick(DEBT_SHORT_TERM)
    incl = pick(DEBT_LTD_INCL_CURRENT)
    noncurrent = pick(DEBT_LTD_NONCURRENT)
    current_ltd = pick(DEBT_LTD_CURRENT)
    debt_current = pick(DEBT_CURRENT_ALL)

    incl_is_noncurrent = (
        incl is not None
        and noncurrent is not None
        and incl[0] == noncurrent[0]
        and ((current_ltd and current_ltd[0]) or (debt_current and debt_current[0]))
    )
    if incl is not None and not incl_is_noncurrent:
        carrying = pick(DEBT_CARRYING_CHECK)
        only_debt_current = (
            debt_current is not None
            and noncurrent is None
            and current_ltd is None
            and short is None
        )
        if (
            only_debt_current
            and carrying is not None
            and abs(carrying[0] - (incl[0] + debt_current[0]))
            <= abs(carrying[0]) * Decimal("0.01")
        ):
            return done([incl, debt_current], "ltd+debt_current_confirmed")
        if short is not None and current_ltd is not None and short[0] == current_ltd[0]:
            short = None
        return done([incl, short], "ltd_incl_current+short_term")
    if noncurrent is None and incl_is_noncurrent:
        noncurrent = incl
    if debt_current is not None:
        return done([noncurrent, debt_current], "noncurrent+debt_current")
    if noncurrent is not None or current_ltd is not None:
        return done([noncurrent, current_ltd, short], "noncurrent+current+short_term")
    lease_all_in = pick(DEBT_ALL_IN_LEASE)
    if lease_all_in is not None:
        return done([lease_all_in], "all_in_incl_leases")
    return None


def resolve_total_debt_components(
    conn: psycopg.Connection, ciks: set[str], chunk_size: int = 200
) -> dict:
    """Writes total_debt_resolved for every instant period from core.fact
    via compute_total_debt(). Bulk-loads one chunk of companies per query
    (no per-row loop over core.fact). Companies with a total_debt
    company_tag_preference are skipped -- their rows belong to
    sanity/tag_investigator.resolve_company_tag_preferences(), the same
    one-writer-per-company exemption the parser rows already get."""
    stats = {
        "companies": 0,
        "skipped_preference": 0,
        "rows_written": 0,
        "errored": 0,
        "paths": {},
    }
    resolved_id = _concept_id(conn, "total_debt_resolved")
    total_debt_id = _concept_id(conn, "total_debt")
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.id from core.company c
            where c.cik = any(%s)
              and not exists (select 1 from analytics.company_tag_preference p
                              where p.company_id = c.id and p.canonical_concept_id = %s)
            order by c.id
            """,
            (list(ciks), total_debt_id),
        )
        company_ids = [r[0] for r in cur.fetchall()]
        cur.execute(
            "select count(*) from core.company where cik = any(%s)", (list(ciks),)
        )
        stats["skipped_preference"] = cur.fetchone()[0] - len(company_ids)

    for i in range(0, len(company_ids), chunk_size):
        chunk = company_ids[i : i + chunk_size]
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select distinct on (f.company_id, f.period_id, c.tag)
                           f.company_id, f.period_id, c.tag, f.value, f.id
                    from core.fact f
                    join core.concept c on c.id = f.concept_id
                    join core.period p on p.id = f.period_id
                    where f.company_id = any(%s) and f.is_authoritative
                      and c.taxonomy = 'us-gaap' and c.tag = any(%s)
                      and p.period_type = 'instant'
                    order by f.company_id, f.period_id, c.tag, f.id desc
                    """,
                    (chunk, list(TOTAL_DEBT_TAGS)),
                )
                by_period: dict[tuple[int, int], dict] = {}
                for company_id, period_id, tag, value, fact_id in cur.fetchall():
                    by_period.setdefault((company_id, period_id), {})[tag] = (
                        value,
                        fact_id,
                    )

                rows = []
                for (company_id, period_id), facts in by_period.items():
                    result = compute_total_debt(facts)
                    if result is None:
                        continue
                    value, fact_ids, path = result
                    stats["paths"][path] = stats["paths"].get(path, 0) + 1
                    rows.append((company_id, resolved_id, period_id, value, fact_ids))

                cur.execute(
                    "delete from analytics.canonical_fact where canonical_concept_id = %s and company_id = any(%s)",
                    (resolved_id, chunk),
                )
                if rows:
                    cur.executemany(
                        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, %s, %s)",
                        rows,
                    )
            conn.commit()
            stats["companies"] += len(chunk)
            stats["rows_written"] += len(rows)
        except Exception:
            logger.warning(
                "concept_fallback.total_debt_chunk_failed",
                first_company_id=chunk[0],
                exc_info=True,
            )
            stats["errored"] += len(chunk)
            conn = safe_rollback(conn, stage="total_debt_components", cik=str(chunk[0]))
    logger.info(
        "concept_fallback.total_debt_done",
        **{k: v for k, v in stats.items() if k != "paths"},
        paths=stats["paths"],
    )
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
    resolve-facts output changes.

    Excludes companies with a `concept_parser_result` row for the
    PRIMARY concept from both the delete and the insert -- found live
    2026-09-21 (Hyatt Hotels): this function's blanket
    `delete ... where canonical_concept_id = resolved_id` silently wiped
    a value `parsers/cost_of_revenue_parser.py` had just written into
    the SAME resolved concept via `resolve_parser_results()`, because
    neither writer knew about the other -- the identical "shared-table
    write needs scoping on every dimension another writer keys on" bug
    class already hit and fixed for roic/roe (Mapper Day 6),
    expanded_metrics.py's delete scope, and resolve.py's own
    `_load_managed_concept_ids()`. Fixed the same way
    resolve_company_tag_preferences() already protects
    company_tag_preference-owned rows: a parser-owned company's row is
    now permanently exempt from this function's write scope, so a
    parser result persists through any later arithmetic-fallback rerun
    without depending on call order."""
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
        cur.execute(
            """
            delete from analytics.canonical_fact
            where canonical_concept_id = %(resolved_id)s
              and not exists (
                  select 1 from analytics.concept_parser_result cpr
                  where cpr.company_id = analytics.canonical_fact.company_id
                    and cpr.canonical_concept_id = %(primary_id)s
              )
            """,
            params,
        )
        cur.execute(
            f"""
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select company_id, %(resolved_id)s, period_id, value, source_fact_ids
            from analytics.canonical_fact
            where canonical_concept_id = %(primary_id)s
              and not exists (
                  select 1 from analytics.concept_parser_result cpr
                  where cpr.company_id = analytics.canonical_fact.company_id and cpr.canonical_concept_id = %(primary_id)s
              )
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
                and not exists (
                    select 1 from analytics.concept_parser_result cpr
                    where cpr.company_id = m.company_id and cpr.canonical_concept_id = %(primary_id)s
                )
            """,
            params,
        )
        cur.execute(
            "select count(*) from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s",
            params,
        )
        count = cur.fetchone()[0]
    conn.commit()
    return count


def resolve_all_arithmetic_fallbacks(conn: psycopg.Connection) -> dict:
    stats = {"considered": len(ARITHMETIC_FALLBACKS), "rows_written": {}}
    for (
        resolved_name,
        primary_name,
        minuend_name,
        subtrahend_name,
        guard,
    ) in ARITHMETIC_FALLBACKS:
        resolved_id = _concept_id(conn, resolved_name)
        primary_id = _concept_id(conn, primary_name)
        minuend_id = _concept_id(conn, minuend_name)
        subtrahend_id = _concept_id(conn, subtrahend_name)
        count = resolve_arithmetic_fallback(
            conn, resolved_id, primary_id, minuend_id, subtrahend_id, guard
        )
        stats["rows_written"][resolved_name] = count
        logger.info(
            "concept_fallback.arithmetic_done", concept=resolved_name, rows=count
        )
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
        cur.execute(
            "delete from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s",
            {"resolved_id": resolved_id},
        )
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
        cur.execute(
            "select count(*) from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s",
            {"resolved_id": resolved_id},
        )
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
        cur.execute(
            "delete from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s",
            {"resolved_id": resolved_id},
        )
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
        cur.execute(
            "select count(*) from analytics.canonical_fact where canonical_concept_id = %(resolved_id)s",
            {"resolved_id": resolved_id},
        )
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
def _find_or_create_instant_period(
    conn: psycopg.Connection, company_id: int, as_of: date
) -> int:
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
        cur.execute(
            "select id, cik from core.company where cik = any(%s)", (list(ciks),)
        )
        companies = cur.fetchall()

    stats = {
        "considered": 0,
        "from_xbrl": 0,
        "from_prose": 0,
        "from_yfinance": 0,
        "still_null": 0,
        "errored": 0,
    }
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
                    period_id = _find_or_create_instant_period(
                        conn, company_id, report_date
                    )
                    merged[period_id] = (Decimal(headcount), [])
                    stats["from_prose"] += 1

            if not merged:
                with conn.cursor() as cur:
                    cur.execute(
                        "select y_employee_count from core.company where id = %s",
                        (company_id,),
                    )
                    y_row = cur.fetchone()
                if y_row and y_row[0]:
                    period_id = _find_or_create_instant_period(
                        conn, company_id, date.today()
                    )
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
            logger.warning(
                "concept_fallback.employee_count_company_failed", cik=cik, exc_info=True
            )
            stats["errored"] += 1
            conn.rollback()

    logger.info("concept_fallback.employee_count_resolved_done", **stats)
    return stats

# Root-cause-2/3 revenue fixes (collaborative-arrangement revenue,
# net-lease REIT income) moved to mapper/revenue_resolvers/ on 2026-10-02
# -- revenue-specific resolution strategies now live in that package's
# sub-mapper registry, not accreting here alongside the generic
# concept-vs-concept fallback machinery this module owns (total_debt,
# D&A, capex, employee_count). See that package's __init__.py docstring
# for why.

# Balance-sheet identity fallback (2026-10-05, doc 49's "low-risk first
# move" recommendation: add new ARITHMETIC_FALLBACKS-shaped entries
# informed by sanity/accounting_identity.py's already-validated
# `balance_sheet` identity, rather than unifying the two mechanisms
# outright). Assets = Liabilities + StockholdersEquity (+ NCI + temporary
# equity) is a hard accounting identity (verified live: 99.71% exact
# agreement, 215,078/215,713 real coexisting Assets/
# LiabilitiesAndStockholdersEquity periods) -- unlike every other
# candidate this project has rejected, this one is the SAME number by
# definition, not a different concept sharing vocabulary.
#
# Deliberately NOT built on resolve_arithmetic_fallback() (that function's
# 5-tuple shape has no room for the identity's real adjustment terms --
# MinorityInterest/TemporaryEquity*/RedeemableNoncontrollingInterest* --
# and doc 49's own risk #2 names skipping them as the exact false-gap
# trap this project has hit before). Measured before building: of
# total_liabilities_resolved's 9,178 no_mapped_tag gap periods, 7,888
# (86%) have both Assets and StockholdersEquity already resolved: 6,207
# need zero adjustment (bare identity holds), 1,681 have a real nonzero
# NCI/temp-equity fact that must be included, not skipped, to get the
# right number.
#
# Purely additive (INSERT...SELECT ... ON CONFLICT DO NOTHING) -- same
# established-safe idiom as conflict_resolution.py's resolve_conflict_fill
# and dedup_majority_resolver.py's majority-vote fill, both of which
# already write into these same two `_resolved` concepts. This can only
# ever fill a currently-empty cell; it is structurally impossible for it
# to overwrite a value either of those modules (or resolve() itself, for
# the primary Liabilities/StockholdersEquity tag) already produced --
# avoids the "two writers into one shared _resolved concept" bug class
# this project has hit three times (roic/roe, expanded_metrics.py,
# resolve.py's own managed-concept scoping) without needing to coordinate
# delete scope with any of them at all, since there is no delete.
_BALANCE_SHEET_ADJUSTMENT_TAGS = (
    "MinorityInterest",
    "TemporaryEquityCarryingAmountAttributableToParent",
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterest",
    "RedeemableNoncontrollingInterestEquityCarryingAmount",
)


def resolve_balance_sheet_identity_fallback(
    conn: psycopg.Connection,
    resolved_name: str,
    assets_name: str,
    other_name: str,
    other_sign: int,
) -> int:
    """Derives `resolved_name` = Assets - (other_sign * other_name's value)
    - sum(present adjustment tags), only where `resolved_name` doesn't
    already have a value for that (company, period). `other_sign` is -1
    when `other_name` is being SUBTRACTED from Assets to get the target
    (both of this module's two real uses: total_liabilities = Assets -
    StockholdersEquity - adj, and stockholders_equity = Assets -
    total_liabilities - adj -- in both cases the known other term is
    subtracted, so callers always pass -1 today; the parameter exists so
    a future caller solving for Assets itself, if ever needed, could pass
    +1 instead of duplicating this function)."""
    resolved_id = _concept_id(conn, resolved_name)
    assets_id = _concept_id(conn, assets_name)
    other_id = _concept_id(conn, other_name)

    with conn.cursor() as cur:
        # Resolve the adjustment tags to concept_ids up front and pre-
        # aggregate by (company_id, period_id) in a standalone CTE --
        # these 4 tags are rare (NCI/temporary-equity line items), so
        # filtering core.fact by concept_id = any(...) (idx_fact_concept_id)
        # first is a small, fast index scan. The original version instead
        # ran a LATERAL subquery correlated on (company_id, period_id) with
        # no supporting index on that pair alone -- confirmed live it had
        # not finished after 60 minutes against core.fact's 26M+ rows,
        # cancelled via pg_cancel_backend. This version finishes in
        # seconds: aggregate the small adjustment-tag slice ONCE, then join
        # it like any other small table.
        cur.execute(
            "select id from core.concept where tag = any(%s)",
            (list(_BALANCE_SHEET_ADJUSTMENT_TAGS),),
        )
        adj_concept_ids = [row[0] for row in cur.fetchall()]

        cur.execute(
            """
            insert into analytics.canonical_fact
                (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            with adj as (
                select f.company_id, f.period_id,
                       sum(f.value) as total_adj,
                       array_agg(f.id) as adj_fact_ids
                from core.fact f
                where f.concept_id = any(%(adj_concept_ids)s)
                  and f.is_authoritative = true
                group by f.company_id, f.period_id
            )
            select
                a.company_id,
                %(resolved_id)s,
                a.period_id,
                a.value + (%(other_sign)s * o.value) + coalesce(adj.total_adj, 0),
                a.source_fact_ids || o.source_fact_ids || coalesce(adj.adj_fact_ids, array[]::bigint[])
            from analytics.canonical_fact a
            join analytics.canonical_fact o
                on o.company_id = a.company_id
               and o.period_id = a.period_id
               and o.canonical_concept_id = %(other_id)s
            left join adj
                on adj.company_id = a.company_id and adj.period_id = a.period_id
            where a.canonical_concept_id = %(assets_id)s
            on conflict (company_id, canonical_concept_id, period_id) do nothing
            """,
            {
                "resolved_id": resolved_id,
                "assets_id": assets_id,
                "other_id": other_id,
                "other_sign": other_sign,
                "adj_concept_ids": adj_concept_ids,
            },
        )
        count = cur.rowcount
    conn.commit()
    logger.info(
        "concept_fallback.balance_sheet_identity_done",
        concept=resolved_name,
        rows=count,
    )
    return count


def resolve_all_balance_sheet_identity_fallbacks(conn: psycopg.Connection) -> dict:
    """Both directions of the same identity: total_liabilities from
    Assets-Equity, and stockholders_equity from Assets-Liabilities. Each
    only fills its OWN currently-empty cells (ON CONFLICT DO NOTHING), so
    running both in either order is safe -- the second call simply sees
    whatever currently-resolved values the first call's writes, plus
    every pre-existing value, already provide; it does not need to chain
    off the first call's specific output to be correct, only to
    (optionally) benefit from slightly wider coverage if run after."""
    liabilities_count = resolve_balance_sheet_identity_fallback(
        conn,
        "total_liabilities_resolved",
        "total_assets_resolved",
        "stockholders_equity_resolved",
        -1,
    )
    equity_count = resolve_balance_sheet_identity_fallback(
        conn,
        "stockholders_equity_resolved",
        "total_assets_resolved",
        "total_liabilities_resolved",
        -1,
    )
    return {
        "total_liabilities_resolved": liabilities_count,
        "stockholders_equity_resolved": equity_count,
    }
