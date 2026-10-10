"""Population-wide fix for the Stage 2e "all-non-authoritative" dedup-hole
bug (found 2026-10-03, generalizing the Flowserve-shaped revenue bug from
2026-09-07 to every concept). Root cause, confirmed on Apple/Microsoft/
Nike/JPMorgan/Bank of America/Abbott Labs: multiple real raw core.fact
rows exist for a period, but ALL are marked is_authoritative=false (Stage
2e correctly-by-design rejecting a near-consensus disagreement with no
tie-break) -- resolve()'s first_match then has nothing to pick, so the
whole period comes back silently null in analytics.canonical_fact.

Scoped ONLY to concepts where a live sample confirmed 88-97% of these
holes have a clean majority among the disagreeing raw rows (balance-
sheet/instant concepts: total_assets, current_assets, current_liabilities,
total_liabilities, stockholders_equity, shares_outstanding, basic_eps,
diluted_eps) -- income-statement/cash-flow concepts (revenue, net_income,
cfo, gross_profit, operating_income, etc.) showed only 68-75% agreement
(confirmed concretely on Abbott Labs FY2012 operating_income: 3 raw rows,
3 genuinely different values, no majority) and are deliberately NOT
included here -- a blind majority vote would silently pick a wrong
number ~25-30% of the time for those. That needs its own, more careful
mechanism (a confidence flag, not blind vote) -- not built here.

Writes into a new `<concept>_resolved` concept (zero concept_mapping
rows, never touched by resolve()) -- same idiom as total_debt_resolved/
gross_profit_resolved/revenue_sanity_resolved. Only acts on a (company,
period) where resolve()'s own concept has ZERO authoritative facts (a
true hole) -- never overrides a value resolve() already found. Requires
an explicit majority (the winning value's row count > 50% of all raw
rows for that period) -- if 2 of 3 rows agree, apply it; if all 3 are
different (Abbott's shape), skip, leave the hole as an honest null
rather than guessing. Tolerance-grouped (relative diff < 0.5%) so trivial
rounding variants count as the same vote, not 3 different "values"."""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback

logger = structlog.get_logger()

# (primary concept name, resolved concept name) -- the 8 concepts a live
# sample confirmed safe for majority-vote. Order doesn't matter; each is
# independent.
SAFE_CONCEPTS: list[tuple[str, str]] = [
    ("total_assets", "total_assets_resolved"),
    ("current_assets", "current_assets_resolved"),
    ("current_liabilities", "current_liabilities_resolved"),
    ("total_liabilities", "total_liabilities_resolved"),
    ("stockholders_equity", "stockholders_equity_resolved"),
    ("shares_outstanding", "shares_outstanding_resolved"),
    ("basic_eps", "basic_eps_resolved"),
    ("diluted_eps", "diluted_eps_resolved"),
    # dividends_per_share added 2026-10-03 -- same per-share-figure shape as
    # EPS (a split shrinks it too), live-sampled before adding: 39 of 300
    # real no-majority holes matched a known split ratio.
    ("dividends_per_share", "dividends_per_share_resolved"),
]

_TOLERANCE = Decimal(
    "0.005"
)  # 0.5% relative -- trivial rounding variants count as one vote

# Concepts where a forward stock split SHRINKS the reported value (a 2-for-1
# split halves EPS) -- confirmed live 2026-10-03 on Nike: two "disagreeing"
# basic_eps raw facts for the same FY2015 Q3 period (2.79 vs 1.39, 0.92 vs
# 0.46) are not real disagreement at all -- both ratios are ~2.0, exactly
# Nike's own real 2015-11-19 split (analytics.company_stock_split). This is
# NOT genuine filing disagreement (Abbott Labs' shape); it's the identical
# fact reported on two different share bases across filing years. Reuses
# corporate_actions/stock_splits.py's own already-detected, SEC-tag-sourced
# split ratios -- never yfinance, never a web lookup, per this project's
# locked "yfinance/external sources validate, SEC data is the only thing
# ever stored" rule.
# concept_name -> "shrinks" (a forward split divides the value -- EPS,
# dividends per share) or "grows" (a forward split multiplies it --
# shares_outstanding). Checked live 2026-10-03 before adding
# shares_outstanding: of 300 real no-majority holes sampled, 12 matched a
# known split ratio -- a smaller share than EPS's 13%, since most
# shares_outstanding disagreement is already caught by the plain
# majority-vote pass above (it runs first in SAFE_CONCEPTS, so by the time
# a shares_outstanding hole reaches the no-majority branch, most of the
# easy cases are already gone).
SPLIT_AWARE_CONCEPTS: dict[str, str] = {
    "basic_eps": "shrinks",
    "diluted_eps": "shrinks",
    "dividends_per_share": "shrinks",
    "shares_outstanding": "grows",
}
_SPLIT_RATIO_TOLERANCE = Decimal(
    "0.02"
)  # 2% -- wider than _TOLERANCE since this compares
# a ratio of two already-independently-rounded filed figures, not the figures themselves


def _concept_id(conn: psycopg.Connection, name: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (name,)
        )
        row = cur.fetchone()
        return row[0] if row else None


def _mapped_concept_ids(
    conn: psycopg.Connection, canonical_concept_id: int
) -> list[int]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select co.id
            from analytics.concept_mapping cm
            join core.concept co on co.id = cm.concept_id
            where cm.canonical_concept_id = %s and cm.confidence != 'rejected'
            """,
            (canonical_concept_id,),
        )
        return [r[0] for r in cur.fetchall()]


def _load_split_ratios(
    conn: psycopg.Connection, company_ids: list[int]
) -> dict[int, list[Decimal]]:
    """company_id -> list of real, SEC-tag-sourced split ratios (one entry
    per detected split event -- a company with 2 splits gets 2 entries, so
    callers can also try their product for a period predating both)."""
    if not company_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            "select company_id, ratio from analytics.company_stock_split where company_id = any(%s)",
            (company_ids,),
        )
        out: dict[int, list[Decimal]] = {}
        for cid, ratio in cur.fetchall():
            out.setdefault(cid, []).append(Decimal(str(ratio)))
        return out


def _candidate_ratios(split_ratios: list[Decimal]) -> list[Decimal]:
    """Every single ratio, plus pairwise products (a period predating two
    splits divides by both) -- matches stock_splits.py's own documented
    multi-split handling. Capped at pairs; a 3-split company is rare
    enough that catching 2 of 3 orderings here is already a big win over
    catching none."""
    candidates = list(split_ratios)
    for i in range(len(split_ratios)):
        for j in range(i + 1, len(split_ratios)):
            candidates.append(split_ratios[i] * split_ratios[j])
    return candidates


def _split_reconcile(
    values: list[Decimal], split_ratios: list[Decimal], direction: str = "shrinks"
) -> Decimal | None:
    """If every value in a disagreeing group reconciles to one real value
    once a real split ratio (or product of two) is applied -- i.e. the
    "disagreement" is just pre-split vs. post-split reporting of the same
    fact -- returns the CURRENT-BASIS value, preserving sign (EPS/DPS can
    be a real, negative loss-per-share). `direction` picks which end of
    the magnitude range is "current": "shrinks" (EPS, dividends per share
    -- a forward split divides the value, so the smaller magnitude is the
    post-split/current one) or "grows" (shares_outstanding -- a forward
    split multiplies it, so the LARGER magnitude is current). Else None
    (genuine disagreement, not a split). A $0 value can never be split-
    explained (0 / any ratio is still 0, so it can't reconcile with a
    nonzero figure, and dividing BY zero below would crash) -- rejected
    outright, not divided by."""
    if not split_ratios or len(values) < 2:
        return None
    if any(v == 0 for v in values):
        return None
    if len({v > 0 for v in values}) > 1:
        return None  # a split never flips sign -- mixed positive/negative is genuine disagreement
    candidates = _candidate_ratios(split_ratios)
    anchor = min(values, key=abs) if direction == "shrinks" else max(values, key=abs)
    for v in values:
        if v == anchor:
            continue
        larger, smaller = (
            (abs(v), abs(anchor)) if abs(v) > abs(anchor) else (abs(anchor), abs(v))
        )
        ratio = larger / smaller
        if not any(abs(ratio - c) / c <= _SPLIT_RATIO_TOLERANCE for c in candidates):
            return None  # at least one pair doesn't reconcile -- genuine disagreement
    return anchor


def _group_by_tolerance(values: list[Decimal]) -> dict[Decimal, int]:
    """Groups near-identical values (within _TOLERANCE relative) under one
    representative key, returns {representative_value: count}."""
    groups: list[list[Decimal]] = []
    for v in values:
        placed = False
        for g in groups:
            rep = g[0]
            denom = max(abs(rep), abs(v), Decimal("1"))
            if abs(v - rep) / denom <= _TOLERANCE:
                g.append(v)
                placed = True
                break
        if not placed:
            groups.append([v])
    return {g[0]: len(g) for g in groups}


def resolve_majority_vote_for_concept(
    conn: psycopg.Connection, concept_name: str, resolved_concept_name: str
) -> dict:
    """Scans the real_operating_company population (not every status='active'
    row -- see mapper/coverage_matrix.py's own corrected-denominator
    reasoning) for (company, period) holes in `concept_name` with a real,
    tolerance-grouped majority among its disagreeing raw facts, and merges
    the resolved value into `resolved_concept_name`. Never touches a
    period resolve() already has a real value for."""
    primary_id = _concept_id(conn, concept_name)
    resolved_id = _concept_id(conn, resolved_concept_name)
    if primary_id is None or resolved_id is None:
        raise ValueError(f"{concept_name!r} or {resolved_concept_name!r} not found")

    tag_concept_ids = _mapped_concept_ids(conn, primary_id)
    if not tag_concept_ids:
        return {"considered": 0, "fixed": 0, "no_majority": 0, "errored": 0}

    with conn.cursor() as cur:
        # (company_id, period_id) pairs: zero authoritative facts for the
        # primary concept's own mapped tags, but >=2 raw facts total under
        # those tags for that period (real_operating_company population,
        # same scoping discipline already used elsewhere in this module
        # family).
        cur.execute(
            """
            with mapped_tags as (
                select co.id as concept_id
                from analytics.concept_mapping cm
                join core.concept co on co.id = cm.concept_id
                where cm.canonical_concept_id = %(primary_id)s and cm.confidence != 'rejected'
            ),
            candidate_periods as (
                select f.company_id, f.period_id,
                       count(*) filter (where f.is_authoritative) as auth_count,
                       count(*) as total_count
                from core.fact f
                join mapped_tags mt on mt.concept_id = f.concept_id
                join core.company c on c.id = f.company_id
                where c.status = 'active'
                group by f.company_id, f.period_id
                having count(*) filter (where f.is_authoritative) = 0
                   and count(*) >= 2
            )
            select company_id, period_id from candidate_periods
            """,
            {"primary_id": primary_id},
        )
        holes = cur.fetchall()

    # Batch-load every raw fact for every hole in ONE round trip (not one
    # query per company) -- found live 2026-10-03: 2,600 per-company round
    # trips to this dev machine's remote Supabase instance blew a 30-minute
    # background-job limit without finishing a single concept.
    period_ids = list({p for _c, p in holes})
    facts_by_key: dict[tuple[int, int], list[tuple[int, object]]] = {}
    if period_ids:
        with conn.cursor() as cur:
            cur.execute(
                """
                select f.company_id, f.period_id, f.id, f.value
                from core.fact f
                where f.period_id = any(%s) and f.concept_id = any(%s)
                """,
                (period_ids, tag_concept_ids),
            )
            for cid, pid, fid, val in cur.fetchall():
                facts_by_key.setdefault((cid, pid), []).append((fid, val))

    split_ratios_by_company = (
        _load_split_ratios(conn, list({c for c, _p in holes}))
        if concept_name in SPLIT_AWARE_CONCEPTS
        else {}
    )

    stats = {
        "considered": len(holes),
        "fixed": 0,
        "fixed_via_split": 0,
        "no_majority": 0,
        "errored": 0,
    }
    CHUNK_SIZE = 1000
    pending: list[dict] = []

    def _flush(pending: list[dict]) -> None:
        if not pending:
            return
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                values (%(company_id)s, %(resolved_id)s, %(period_id)s, %(value)s, %(source_fact_ids)s)
                on conflict (company_id, canonical_concept_id, period_id) do update
                    set value = excluded.value, source_fact_ids = excluded.source_fact_ids
                """,
                pending,
            )
        conn.commit()

    for i, (company_id, period_id) in enumerate(holes, 1):
        try:
            fact_rows = facts_by_key.get((company_id, period_id), [])
            if not fact_rows:
                stats["no_majority"] += 1
                continue
            values = [Decimal(str(v)) for _fid, v in fact_rows]
            groups = _group_by_tolerance(values)
            total = len(values)
            best_value, best_count = max(groups.items(), key=lambda kv: kv[1])
            via_split = False
            if best_count <= total / 2:
                split_value = _split_reconcile(
                    list(groups.keys()),
                    split_ratios_by_company.get(company_id, []),
                    SPLIT_AWARE_CONCEPTS.get(concept_name, "shrinks"),
                )
                if split_value is None:
                    stats["no_majority"] += 1
                    continue
                best_value = split_value
                via_split = True
            source_fact_ids = [
                fid
                for fid, v in fact_rows
                if via_split
                or abs(Decimal(str(v)) - best_value)
                / max(abs(best_value), Decimal("1"))
                <= _TOLERANCE
            ]
            if via_split:
                stats["fixed_via_split"] += 1
            pending.append(
                {
                    "company_id": company_id,
                    "resolved_id": resolved_id,
                    "period_id": period_id,
                    "value": best_value,
                    "source_fact_ids": source_fact_ids,
                }
            )
            stats["fixed"] += 1
        except Exception:
            logger.warning(
                "dedup_majority_resolver.company_period_failed",
                company_id=company_id,
                period_id=period_id,
                exc_info=True,
            )
            stats["errored"] += 1
            conn = safe_rollback(
                conn, stage="dedup_majority_resolver", cik=str(company_id)
            )
        if len(pending) >= CHUNK_SIZE:
            _flush(pending)
            pending = []
            logger.info(
                "dedup_majority_resolver.progress",
                concept=concept_name,
                done=i,
                total=len(holes),
                **stats,
            )
    _flush(pending)
    logger.info("dedup_majority_resolver.concept_done", concept=concept_name, **stats)
    return stats


def resolve_all_safe_concepts(conn: psycopg.Connection) -> dict:
    results = {}
    for concept_name, resolved_name in SAFE_CONCEPTS:
        results[concept_name] = resolve_majority_vote_for_concept(
            conn, concept_name, resolved_name
        )
    return results
