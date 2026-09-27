"""Stock split detection (doc 21 §2, migration 0065, 2026-09-14/15).

Found live investigating a real yfinance mismatch on KLA Corp's diluted
EPS ($8.47 shown vs $0.847 real -- exactly 10x): KLA did a real 10-for-1
split, confirmed two independent ways -- (1) its own FY2025 comparative
EPS exists as both $30.37 (original 10-K) and $3.04 (the same period's
comparative column in the FOLLOWING year's 10-K), and (2) the raw XBRL tag
`StockholdersEquityNoteStockSplitConversionRatio1` for KLA is literally
`10000`, which scale-corrected (see below) is exactly `10`.

doc 21 (2026-08-17) already flagged this tag as "raw data exists,
unmapped" but never built anything -- this closes that gap, verified
before trusting the tag broadly, not assumed from doc 21's own hopeful
framing:

  - Checked the full value distribution across the whole population
    before writing any classification logic: 97.3% of real candidate
    facts (2,945 of 3,028) are already a plausible raw ratio (2, 0.1,
    1.5, 3, 10, 20, 50, ... -- exactly what real split/reverse-split
    ratios look like). A small minority need a scale correction (some
    filers, KLA included, report the ratio x1000 or x10000 instead of
    directly) and a tiny handful (15 of 3,028) get rejected outright --
    negative or absurdly large (up to 109 million) values that are almost
    certainly a DIFFERENT real XBRL use of the same tag name (a
    convertible-security conversion ratio, not a stock split) -- the same
    "same vocabulary, different meaning" trap this project has hit and
    caught before (see doc 40/pipeline/CLAUDE.md's CostsAndExpenses and
    LongTermDebtNoncurrent entries).
  - `0` and `1` are excluded as non-events (no actual ratio change), not
    real splits.

Ratio follows the SEC element's own definition: new shares issued per old
share (2 = 2-for-1 forward split, 0.1 = 1-for-10 reverse split) --
confirmed against KLA's real case (ratio 10, old EPS / 10 = split-adjusted
EPS, matching the value from KLA's own later comparative filing almost
exactly).

This module ONLY detects and records a real, traceable corporate-action
event -- it does not itself adjust, restate, or fabricate any historical
per-share figure. See doc/learnings/ for the follow-up decision on
whether/how detected splits should be used to retroactively adjust
historical EPS/dividends-per-share/shares-outstanding display -- a real
product/trust decision (doc 01's "every number traces to a real filing"
principle), not something this detection module decides on its own.
"""

from decimal import Decimal

import psycopg
import structlog

logger = structlog.get_logger()

SPLIT_RATIO_TAGS = (
    "StockholdersEquityNoteStockSplitConversionRatio",
    "StockholdersEquityNoteStockSplitConversionRatio1",
)

# A genuine split/reverse-split ratio, once correctly scaled, always lands
# in this range -- verified against the real population distribution
# above, not picked arbitrarily. Anything outside it (even after trying
# every scale correction) is rejected rather than guessed.
_PLAUSIBLE_MIN = Decimal("0.001")
_PLAUSIBLE_MAX = Decimal("200")
_SCALE_CANDIDATES = (1, 1000, 10000)
_NON_EVENT_VALUES = {Decimal(0), Decimal(1)}


def _classify(raw_value: Decimal) -> tuple[Decimal, int] | None:
    """Returns (ratio, scale_correction) for a plausible split value, else
    None. Tries the un-scaled value first -- the common case (97.3% of
    real facts) -- before trying wider scale corrections, so a value
    that's already plausible unscaled is never needlessly rescaled."""
    if raw_value in _NON_EVENT_VALUES or raw_value <= 0:
        return None
    for scale in _SCALE_CANDIDATES:
        candidate = raw_value / scale
        if _PLAUSIBLE_MIN <= candidate <= _PLAUSIBLE_MAX:
            return candidate, scale
    return None


# A real split's effective date gets re-disclosed as a footnote in every
# subsequent filing for years -- found live checking Mueller Industries:
# its real 2023-09-26 split appears as an `instant` fact in 7 separate
# filings through 2026, always the same date, plus several `duration`
# facts (whole-fiscal-year footnote mentions, not point-in-time records)
# that would otherwise look like unrelated extra events. Two filters closb
# this: only `instant`-period facts are considered at all (a `duration`
# period here is a footnote restating an already-known split for the
# whole fiscal year, not a new point-in-time event), and any two `instant`
# dates for the same company within this window sharing the same ratio
# are merged into one event (the earliest date -- the first, real
# disclosure -- wins). Chosen from real evidence, not guessed: Mueller's
# own two genuinely-different-but-related dates for its one 2023 split
# (2023-09-26 record date, 2023-10-20 distribution date) are 24 days
# apart; a completely separate second split it did in 2026 is >2.5 years
# from either.
_MERGE_WINDOW_DAYS = 45


def detect_stock_splits(conn: psycopg.Connection) -> dict:
    """Set-based (not a per-company loop) -- scans the whole population's
    already-captured raw facts under SPLIT_RATIO_TAGS in one query. Full
    delete-then-reinsert of analytics.company_stock_split each run: this
    table has no other writer, so re-running after a classifier
    improvement can't step on anything, unlike a canonical_fact `_resolved`
    concept."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.id, f.company_id, f.value, p.end_date, c.tag
            from core.fact f
            join core.concept c on c.id = f.concept_id
            join core.period p on p.id = f.period_id
            where c.tag = any(%s) and f.is_authoritative = true and p.period_type = 'instant'
            """,
            (list(SPLIT_RATIO_TAGS),),
        )
        rows = cur.fetchall()

    stats = {
        "considered": len(rows),
        "detected": 0,
        "non_event": 0,
        "rejected": 0,
        "merged_redisclosures": 0,
    }
    candidates: dict[int, list[dict]] = {}
    for fact_id, company_id, raw_value, effective_date, tag in rows:
        classified = _classify(raw_value)
        if classified is None:
            if raw_value in _NON_EVENT_VALUES:
                stats["non_event"] += 1
            else:
                stats["rejected"] += 1
            continue
        ratio, scale = classified
        candidates.setdefault(company_id, []).append(
            {
                "company_id": company_id,
                "effective_date": effective_date,
                "ratio": ratio,
                "raw_value": raw_value,
                "scale_correction": scale,
                "source_fact_id": fact_id,
                "source_tag": tag,
            }
        )

    best_by_key: dict[tuple[int, object], dict] = {}
    for company_id, company_candidates in candidates.items():
        # Same ratio, close in time -> one real event, re-disclosed. A
        # different ratio, or a date far outside the window, is a
        # genuinely separate split -- companies can and do split more
        # than once over the years.
        company_candidates.sort(key=lambda c: c["effective_date"])
        kept: list[dict] = []
        for candidate in company_candidates:
            merged_into = None
            for existing in kept:
                if (
                    existing["ratio"] == candidate["ratio"]
                    and abs(
                        (candidate["effective_date"] - existing["effective_date"]).days
                    )
                    <= _MERGE_WINDOW_DAYS
                ):
                    merged_into = existing
                    break
            if merged_into is not None:
                stats["merged_redisclosures"] += 1
                if candidate["source_fact_id"] > merged_into["source_fact_id"]:
                    # Keep the earliest EFFECTIVE DATE (the real event
                    # date) but track the most-recently-captured fact_id
                    # as this event's source, for the freshest provenance.
                    merged_into["source_fact_id"] = candidate["source_fact_id"]
                    merged_into["source_tag"] = candidate["source_tag"]
            else:
                kept.append(dict(candidate))
        for event in kept:
            best_by_key[(company_id, event["effective_date"])] = event

    stats["detected"] = len(best_by_key)
    with conn.cursor() as cur:
        cur.execute("delete from analytics.company_stock_split")
        if best_by_key:
            cur.executemany(
                """
                insert into analytics.company_stock_split
                    (company_id, effective_date, ratio, raw_value, scale_correction, source_fact_id, source_tag)
                values
                    (%(company_id)s, %(effective_date)s, %(ratio)s, %(raw_value)s, %(scale_correction)s, %(source_fact_id)s, %(source_tag)s)
                """,
                list(best_by_key.values()),
            )
        conn.commit()

    logger.info("stock_splits.detect_done", **stats)
    return stats


# Per-share concepts a real stock split can leave stranded at a pre-split
# value forever, if the affected historical period was never re-reported
# as a comparative column in ANY later filing (the far more common case
# than the conflict-shaped one conflict_resolution.py's SPLIT_LIKE_CONCEPTS
# already handles -- most companies simply don't bother restating old
# quarters once enough time passes). (primary concept name, resolved
# concept name) -- same _resolved companions SPLIT_LIKE_CONCEPTS uses.
RETROACTIVE_ADJUSTMENT_CONCEPTS: dict[str, str] = {
    "diluted_eps": "diluted_eps_resolved",
    "basic_eps": "basic_eps_resolved",
    "dividends_per_share": "dividends_per_share_resolved",
}


def _concept_id(conn: psycopg.Connection, name: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (name,)
        )
        row = cur.fetchone()
        return row[0] if row else None


def resolve_retroactive_split_adjustments(conn: psycopg.Connection) -> dict:
    """The explicit product/trust decision this module's own docstring
    named as needing confirmation before building: unlike every other
    write in conflict_resolution.py, this SYNTHESIZES a value that was
    never literally filed by the company in any single document -- it
    divides an as-filed pre-split figure by a real, tagged split ratio the
    company DID disclose (in a different filing). Confirmed and directed
    to build, 2026-09-15.

    Kept fully traceable per doc 01's "every number traces to a source"
    principle, just not to ONE filing the way most values are: `source_
    fact_ids` includes both the original per-share fact's own ID(s) AND
    the split-disclosure fact's ID that provided the ratio -- an auditor
    can reconstruct exactly how this number was produced and verify both
    inputs independently, the same transparency any other DERIVED metric
    in this pipeline already has (FCF, margins, ROIC -- none of those are
    a single filed number either).

    Must run BEFORE conflict_resolution.py's own baseline-passthrough for
    these same 3 concepts, not after -- found live 2026-09-15: an earlier
    version of this pipeline ran this step LAST, and baseline-passthrough
    (which copies every primary fact into the resolved concept wherever no
    resolved row exists yet, via ON CONFLICT DO NOTHING) had therefore
    already claimed every never-restated period with its un-adjusted,
    pre-split value before this step ever got to look at it -- its own
    already_resolved check then correctly, but unhelpfully, saw those
    periods as done and skipped them (adjusted=0 across all 3 concepts on
    first real run, despite 1,120 real detected splits). Running this
    FIRST is safe in both directions: baseline-passthrough/conflict-fill/
    split-like-conflicts all skip whatever this step already filled (same
    ON CONFLICT DO NOTHING), and this step's own already_resolved check
    correctly leaves alone anything a PRIOR run of any pass already
    resolved. Handles a company with MULTIPLE splits over time correctly:
    a period predating two later splits gets divided by the PRODUCT of
    both ratios, not just the nearer one."""
    with conn.cursor() as cur:
        cur.execute(
            "select company_id, effective_date, ratio, source_fact_id from analytics.company_stock_split"
        )
        split_rows = cur.fetchall()
    splits_by_company: dict[int, list[tuple]] = {}
    for company_id, effective_date, ratio, source_fact_id in split_rows:
        splits_by_company.setdefault(company_id, []).append(
            (effective_date, ratio, source_fact_id)
        )

    stats: dict = {"concepts": len(RETROACTIVE_ADJUSTMENT_CONCEPTS), "adjusted": 0}
    company_ids_with_splits = list(splits_by_company.keys())
    if not company_ids_with_splits:
        logger.info("stock_splits.retroactive_adjustment_done", **stats)
        return stats

    for primary_name, resolved_name in RETROACTIVE_ADJUSTMENT_CONCEPTS.items():
        primary_id = _concept_id(conn, primary_name)
        resolved_id = _concept_id(conn, resolved_name)
        if primary_id is None or resolved_id is None:
            continue

        with conn.cursor() as cur:
            cur.execute(
                """
                select cf.company_id, cf.period_id, cf.value, cf.source_fact_ids, p.end_date
                from analytics.canonical_fact cf
                join core.period p on p.id = cf.period_id
                where cf.canonical_concept_id = %s and cf.company_id = any(%s)
                """,
                (primary_id, company_ids_with_splits),
            )
            raw_facts = cur.fetchall()
            cur.execute(
                "select company_id, period_id from analytics.canonical_fact where canonical_concept_id = %s",
                (resolved_id,),
            )
            already_resolved = {(cid, pid) for cid, pid in cur.fetchall()}

        to_insert = []
        for company_id, period_id, value, source_fact_ids, end_date in raw_facts:
            if (company_id, period_id) in already_resolved:
                continue
            applicable = [
                (eff, ratio, src)
                for eff, ratio, src in splits_by_company[company_id]
                if eff > end_date
            ]
            if not applicable:
                continue
            cumulative_ratio = Decimal(1)
            split_source_ids: list[int] = []
            for _eff, ratio, src in applicable:
                cumulative_ratio *= ratio
                split_source_ids.append(src)
            if cumulative_ratio in (Decimal(0), Decimal(1)):
                continue
            to_insert.append(
                {
                    "company_id": company_id,
                    "resolved_id": resolved_id,
                    "period_id": period_id,
                    "value": value / cumulative_ratio,
                    "source_fact_ids": list(source_fact_ids or []) + split_source_ids,
                }
            )

        if to_insert:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                    values (%(company_id)s, %(resolved_id)s, %(period_id)s, %(value)s, %(source_fact_ids)s)
                    on conflict (company_id, canonical_concept_id, period_id) do nothing
                    """,
                    to_insert,
                )
            conn.commit()
        stats["adjusted"] += len(to_insert)
        stats[f"{primary_name}_adjusted"] = len(to_insert)

    logger.info("stock_splits.retroactive_adjustment_done", **stats)
    return stats
