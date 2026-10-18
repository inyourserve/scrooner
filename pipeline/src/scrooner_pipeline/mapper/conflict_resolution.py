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

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import psycopg
import structlog

logger = structlog.get_logger()

MAX_SAFE_RATIO = Decimal("1.15")

# Restatement fill (2026-09-29). Beyond MAX_SAFE_RATIO the filings disagree
# materially -- almost always a restatement: a later 10-K/10-Q re-presents
# prior periods with corrected values (Symbotic restated all of FY2025 in
# its FY2026 10-Qs; Q2 2025 net income -3,925K originally, -1,804K
# restated). dedupe.py marks every version non-authoritative, so the whole
# period went blank and, with it, every TTM built across it. The latest
# filing is the company's current official figure (SEC Frames serves the
# same). Checked against yfinance on 93 restated net-income quarters: the
# latest-filed value matched 65, the original 28, neither 3. Guards: one
# unambiguous latest filing date whose facts agree, no zeros, and values
# within 10x of each other (a wider spread looks like a scale error, not a
# restatement: 525 net-income conflicts exceed it and stay blank).
MAX_RESTATEMENT_RATIO = Decimal("10")

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
    # total_debt is deliberately absent (2026-09-29): total_debt_resolved is
    # built from components by concept_fallback.resolve_total_debt_components,
    # which leaves a period blank when the tags can't give a total. A single
    # conflicting tag here (ShortTermBorrowings alone) is a partial debt, not
    # a total -- 254 such rows at 41 companies had slipped in this way.
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
    # Added 2026-09-15 alongside diluted_eps_resolved's split-aware
    # handling below -- basic_eps and dividends_per_share are per-share
    # figures subject to the identical stock-split conflict shape
    # (a company's pre-split historical value legitimately disagrees with
    # its own later, split-adjusted restatement of the same period).
    ("basic_eps", "basic_eps_resolved"),
    ("dividends_per_share", "dividends_per_share_resolved"),
]


def _concept_id(conn: psycopg.Connection, name: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (name,)
        )
        row = cur.fetchone()
        return row[0] if row else None


def _load_conflict_groups(conn: psycopg.Connection, primary_id: int) -> list[tuple]:
    """Every (company_id, period_id) where the primary concept's
    highest-priority mapped tag that the company filed for that period has
    2+ disagreeing core.fact values and NONE is authoritative -- the exact
    dedupe.py "flag, don't resolve" case. Returns one row per group with
    every (value, fact_id, filing_date) so the safety check and tie-break
    can happen in Python.

    Scoped to ONE tag per group (2026-09-29): pooling every mapped tag mixed
    different concepts into one "conflict" -- Symbotic's NetIncomeLoss
    (-3.9M / -1.8M) sat beside its much larger ProfitLoss (-21.4M / -9.9M,
    which includes noncontrolling interests), so no fill was ever safe, and
    a close pair of two different tags could fill from the lower-priority
    one. Taking the top-priority tag mirrors resolve()'s own first_match."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with facts as (
                select f.company_id, f.period_id, f.value, f.id, f.is_authoritative,
                       fl.filing_date, cm.priority,
                       min(cm.priority) over (partition by f.company_id, f.period_id) as top_priority
                from core.fact f
                join core.filing fl on fl.id = f.filing_id
                join analytics.concept_mapping cm on cm.concept_id = f.concept_id
                where cm.canonical_concept_id = %s and cm.confidence != 'rejected'
            )
            select company_id, period_id, array_agg(value order by id), array_agg(id order by id),
                   array_agg(filing_date order by id)
            from facts
            where priority = top_priority
            group by company_id, period_id
            having count(distinct value) > 1 and bool_or(is_authoritative) = false
            """,
            (primary_id,),
        )
        return cur.fetchall()


def _load_already_resolved(
    conn: psycopg.Connection, resolved_id: int
) -> set[tuple[int, int]]:
    with conn.cursor() as cur:
        cur.execute(
            "select company_id, period_id from analytics.canonical_fact where canonical_concept_id = %s",
            (resolved_id,),
        )
        return {(row[0], row[1]) for row in cur.fetchall()}


def _safe_fill_value(
    values: list[Decimal], fact_ids: list[int]
) -> tuple[Decimal, int] | None:
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


def _restatement_fill_value(
    values: list[Decimal], fact_ids: list[int], filing_dates: list
) -> tuple[Decimal, int] | None:
    """The value from the single latest filing, when the disagreement is too
    large for _safe_fill_value but still looks like a restatement. None when
    the latest filing date is shared by disagreeing facts, any value is
    zero, or the magnitudes differ by more than MAX_RESTATEMENT_RATIO."""
    if len(values) < 2 or any(v == 0 for v in values):
        return None
    mags = [abs(v) for v in values]
    if max(mags) / min(mags) > MAX_RESTATEMENT_RATIO:
        return None
    latest = max(filing_dates)
    latest_idx = [i for i, d in enumerate(filing_dates) if d == latest]
    if len(latest_idx) == len(values):
        return None  # every version filed the same day -- not a restatement
    if len({values[i] for i in latest_idx}) != 1:
        return None
    best = max(latest_idx, key=lambda i: fact_ids[i])
    return values[best], fact_ids[best]


def resolve_baseline_passthrough(
    conn: psycopg.Connection, primary_name: str, resolved_name: str
) -> int:
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
    logger.info(
        "conflict_resolution.baseline_done",
        primary=primary_name,
        resolved=resolved_name,
        inserted=inserted,
    )
    return inserted


# Stale-fill refresh (2026-10-18). EXPLICIT, DRY-RUN-FIRST ONLY: never called
# from resolve_all_conflict_fills / the nightly. Every writer of the
# *_resolved concepts is ON CONFLICT DO NOTHING, so a fill written while all
# copies of a period were non-authoritative is never refreshed when a copy
# later becomes authoritative (company 2835 FY2023 revenue, ledger
# 2026-10-18). A first version paired the stored row with the primary row by
# (company, period) only; the Verifier opened 82 of its proposals in the
# filings and the proposed value was wrong in 31
# (data-team/28-VERIFIER-STALE-FILL-PROPOSALS-2026-10-18.md): it swapped in a
# different tag (ASC 606 subset, continuing-ops subtotal, opposite-signed
# alternative tag), a derived FY-minus-9M value, or a DEF 14A / 8-K figure.
# The guards below are that verdict's recommendation, enforced in code.

# Only these forms carry the financial statements a value may be refreshed
# from. 8-K recasts are re-presentations and DEF 14A pay-versus-performance
# figures are rounded (AEMD, ledger 2026-10-18).
STALE_FILL_PERIODIC_FORMS = frozenset(
    {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-KT/A"}
)

# A difference at or below this relative size is skipped as the same figure
# at a different presentation precision, but ONLY if the coarser value really
# is the finer one rounded at the coarser value's precision (TTWO: 3,372,772K
# vs 3,372.8M).
STALE_FILL_ROUNDING_TOLERANCE = Decimal("0.0001")

# Up to this relative difference a same-tag disagreement that is not
# explained by rounding is too close to call from the numbers alone: it may be
# a rounded copy (AEMD's DEF 14A 13,400,000 vs 13,388,089 is 0.09%) or a small
# real re-presentation (JEF 2,187,495K vs 2,186,582K, 0.04%). Routed to review,
# never auto-replaced.
STALE_FILL_NEAR_EQUAL_TOLERANCE = Decimal("0.01")

STALE_FILL_GUARD_CLASS = "same_tag_filed_periodic_later_filing"


@dataclass(frozen=True)
class StaleFillCandidate:
    """One stored *_resolved row (all sources non-authoritative) paired with
    the primary concept's row for the same (company, period). Tags are
    'taxonomy:tag' strings of core.concept behind each side's
    source_fact_ids; a missing source fact simply contributes nothing."""

    concept: str
    row_id: int
    company_id: int
    period_id: int
    stored: Decimal
    primary: Decimal
    stored_tags: frozenset[str]
    primary_tags: frozenset[str]
    primary_any_derived: bool | None
    primary_forms: frozenset[str]
    stored_filing_date: date | None
    primary_filing_date: date | None
    primary_source_fact_ids: tuple[int, ...] = ()
    primary_accessions: tuple[str, ...] = ()
    stored_accessions: tuple[str, ...] = ()
    stored_forms: frozenset[str] = frozenset()


def _rounding_consistent(a: Decimal, b: Decimal) -> bool:
    """True when the coarser-precision value equals the finer one rounded at
    the coarser value's apparent precision (its trailing zeros / decimal
    places). Two values at the same apparent precision can't be a rounding of
    each other."""
    if a == 0 or b == 0:
        return False
    exp_a = a.normalize().as_tuple().exponent
    exp_b = b.normalize().as_tuple().exponent
    if not isinstance(exp_a, int) or not isinstance(exp_b, int) or exp_a == exp_b:
        return False
    coarse, fine, coarse_exp = (a, b, exp_a) if exp_a > exp_b else (b, a, exp_b)
    half_unit = Decimal(1).scaleb(coarse_exp) / 2
    return abs(fine - coarse) <= half_unit


def classify_stale_fill(c: StaleFillCandidate) -> tuple[str, str]:
    """(outcome, reason); outcome is 'propose', 'needs_review' or 'skip'.
    Guards run in this order and the first one that fires decides, so the
    reason is the earliest failing guard:
      skip        equal values
      skip        stored or primary source facts missing
      skip        different_tag: the stored and primary source tags differ
                  (a different tag is a precedence decision, not staleness)
      skip        primary_derived: any primary source fact is_derived
      skip        primary_non_periodic_form: a primary form outside
                  STALE_FILL_PERIODIC_FORMS
      needs_review filing_date_unknown
      skip        authoritative_older_than_stored (a newer restated stored
                  value is never overwritten by an older original)
      needs_review same_filing_date (dates can't order same-day filings)
      needs_review sign_flip / zero_value
      skip        rounding_equivalent (<= 0.01% AND rounding-consistent)
      needs_review near_equal_not_rounding / rounded_copy_beyond_tolerance
      propose     everything else"""
    stored, primary = c.stored, c.primary
    if stored == primary:
        return "skip", "equal"
    if not c.stored_tags:
        return "skip", "stored_source_facts_missing"
    if not c.primary_tags:
        return "skip", "primary_source_facts_missing"
    if c.stored_tags != c.primary_tags:
        return "skip", "different_tag"
    if c.primary_any_derived is not False:
        return "skip", "primary_derived"
    if not c.primary_forms or not c.primary_forms <= STALE_FILL_PERIODIC_FORMS:
        return "skip", "primary_non_periodic_form"
    if c.stored_filing_date is None or c.primary_filing_date is None:
        return "needs_review", "filing_date_unknown"
    if c.primary_filing_date < c.stored_filing_date:
        return "skip", "authoritative_older_than_stored"
    if c.primary_filing_date == c.stored_filing_date:
        return "needs_review", "same_filing_date"
    if stored == 0 or primary == 0:
        return "needs_review", "zero_value"
    if (stored < 0) != (primary < 0):
        return "needs_review", "sign_flip"
    rel = abs(stored - primary) / max(abs(stored), abs(primary))
    rounding = _rounding_consistent(stored, primary)
    if rel <= STALE_FILL_ROUNDING_TOLERANCE and rounding:
        return "skip", "rounding_equivalent"
    if rel <= STALE_FILL_NEAR_EQUAL_TOLERANCE:
        if rounding:
            return "needs_review", "rounded_copy_beyond_tolerance"
        return "needs_review", "near_equal_not_rounding"
    return "propose", STALE_FILL_GUARD_CLASS


_STALE_FILL_CANDIDATE_SQL = """
select r.id, r.company_id, r.period_id, r.value, p.value, p.source_fact_ids,
       s.tags, s.max_date, s.accessions, s.forms,
       q.tags, q.any_derived, q.forms, q.accessions, q.max_date
from analytics.canonical_fact r
join analytics.canonical_fact p
  on p.company_id = r.company_id and p.period_id = r.period_id
 and p.canonical_concept_id = %(primary_id)s
cross join lateral (
    select array_agg(distinct c.taxonomy || ':' || c.tag) as tags,
           max(fl.filing_date) as max_date,
           array_agg(distinct fl.accession_number) as accessions,
           array_agg(distinct fl.form) as forms
    from core.fact f
    join core.concept c on c.id = f.concept_id
    join core.filing fl on fl.id = f.filing_id
    where f.id = any(r.source_fact_ids)
) s
cross join lateral (
    select array_agg(distinct c.taxonomy || ':' || c.tag) as tags,
           bool_or(f.is_derived) as any_derived,
           array_agg(distinct fl.form) as forms,
           array_agg(distinct fl.accession_number) as accessions,
           max(fl.filing_date) as max_date
    from core.fact f
    join core.concept c on c.id = f.concept_id
    join core.filing fl on fl.id = f.filing_id
    where f.id = any(p.source_fact_ids)
) q
where r.canonical_concept_id = %(resolved_id)s
  and r.value is distinct from p.value
  and cardinality(r.source_fact_ids) > 0
  and not exists (select 1 from core.fact f
                  where f.id = any(r.source_fact_ids) and f.is_authoritative)
  and exists (select 1 from core.fact f
              where f.id = any(p.source_fact_ids) and f.is_authoritative)
"""


def _load_stale_fill_candidates(
    conn: psycopg.Connection,
    primary_name: str,
    primary_id: int,
    resolved_id: int,
    company_ids: list[int] | None,
) -> list[StaleFillCandidate]:
    sql = _STALE_FILL_CANDIDATE_SQL
    if company_ids:
        sql += "  and r.company_id = any(%(company_ids)s)\n"
    with conn.cursor() as cur:
        cur.execute(
            sql,
            {
                "primary_id": primary_id,
                "resolved_id": resolved_id,
                "company_ids": company_ids,
            },
        )
        rows = cur.fetchall()
    return [
        StaleFillCandidate(
            concept=primary_name,
            row_id=row_id,
            company_id=co,
            period_id=period,
            stored=stored,
            primary=primary,
            stored_tags=frozenset(s_tags or ()),
            primary_tags=frozenset(p_tags or ()),
            primary_any_derived=p_derived,
            primary_forms=frozenset(p_forms or ()),
            stored_filing_date=s_date,
            primary_filing_date=p_date,
            primary_source_fact_ids=tuple(p_src or ()),
            primary_accessions=tuple(sorted(p_acc or ())),
            stored_accessions=tuple(sorted(s_acc or ())),
            stored_forms=frozenset(s_forms or ()),
        )
        for (
            row_id, co, period, stored, primary, p_src,
            s_tags, s_date, s_acc, s_forms,
            p_tags, p_derived, p_forms, p_acc, p_date,
        ) in rows
    ]


def _stale_fill_record(c: StaleFillCandidate, outcome: str, reason: str) -> dict:
    return {
        "concept": c.concept,
        "id": c.row_id,
        "company_id": c.company_id,
        "period_id": c.period_id,
        "old": c.stored,
        "new": c.primary,
        "stored_tags": sorted(c.stored_tags),
        "primary_tags": sorted(c.primary_tags),
        "stored_forms": sorted(c.stored_forms),
        "primary_forms": sorted(c.primary_forms),
        "stored_accessions": list(c.stored_accessions),
        "primary_accessions": list(c.primary_accessions),
        "stored_filing_date": c.stored_filing_date,
        "primary_filing_date": c.primary_filing_date,
        "src": list(c.primary_source_fact_ids),
        "outcome": outcome,
        "guard": reason,
    }


def refresh_stale_fills(
    conn: psycopg.Connection,
    primary_name: str,
    resolved_name: str,
    company_ids: list[int] | None = None,
    dry_run: bool = True,
) -> dict:
    """Propose (dry_run=True, the default) or apply replacements of resolved
    rows built only from non-authoritative facts with the primary concept's
    authoritative row, using classify_stale_fill's guards. Scoped to rows
    whose every source fact is non-authoritative, so tag-preference and
    arithmetic-fallback rows (authoritative sources) are never candidates.
    Returns 'proposals' (would be written), 'needs_review' (never written by
    this function) and per-reason skip counts. Writing requires an explicit
    dry_run=False after the dry-run's proposals were reviewed; it is not part
    of resolve_all_conflict_fills."""
    primary_id = _concept_id(conn, primary_name)
    resolved_id = _concept_id(conn, resolved_name)
    if primary_id is None or resolved_id is None:
        return {"primary": primary_name, "skipped": "concept not found"}

    candidates = _load_stale_fill_candidates(
        conn, primary_name, primary_id, resolved_id, company_ids
    )
    proposals: list[dict] = []
    needs_review: list[dict] = []
    skipped: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    for c in candidates:
        outcome, reason = classify_stale_fill(c)
        if outcome == "skip":
            skipped[reason] = skipped.get(reason, 0) + 1
        elif outcome == "needs_review":
            review_counts[reason] = review_counts.get(reason, 0) + 1
            needs_review.append(_stale_fill_record(c, outcome, reason))
        else:
            proposals.append(_stale_fill_record(c, outcome, reason))

    if proposals and not dry_run:
        with conn.cursor() as cur:
            for start in range(0, len(proposals), 5000):
                cur.executemany(
                    """
                    update analytics.canonical_fact
                    set value = %(new)s, source_fact_ids = %(src)s, resolved_at = now()
                    where id = %(id)s and value = %(old)s
                    """,
                    proposals[start : start + 5000],
                )
        conn.commit()

    stats = {
        "candidates": len(candidates),
        "refreshed": 0 if dry_run else len(proposals),
        "would_refresh": len(proposals),
        "needs_review_count": len(needs_review),
        "needs_review_by_reason": review_counts,
        "skipped": skipped,
    }
    logger.info(
        "conflict_resolution.stale_refresh",
        primary=primary_name,
        resolved=resolved_name,
        dry_run=dry_run,
        **stats,
    )
    stats["proposals"] = proposals
    stats["needs_review"] = needs_review
    return stats


def resolve_conflict_fill(
    conn: psycopg.Connection, primary_name: str, resolved_name: str
) -> dict:
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
    restated = 0
    allow_restatement = primary_name not in SPLIT_LIKE_CONCEPTS
    for company_id, period_id, values, fact_ids, filing_dates in groups:
        if (company_id, period_id) in already:
            continue
        filled = _safe_fill_value(list(values), list(fact_ids))
        if filled is None and allow_restatement:
            filled = _restatement_fill_value(
                list(values), list(fact_ids), list(filing_dates)
            )
            restated += filled is not None
        if filled is None:
            unsafe += 1
            continue
        value, fact_id = filled
        to_insert.append(
            {
                "company_id": company_id,
                "resolved_id": resolved_id,
                "period_id": period_id,
                "value": value,
                "fact_id": fact_id,
            }
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

    stats = {
        "conflict_groups": len(groups),
        "already_resolved": len(groups) - len(to_insert) - unsafe,
        "filled": len(to_insert),
        "restatement_filled": restated,
        "unsafe_skipped": unsafe,
    }
    logger.info(
        "conflict_resolution.done",
        primary=primary_name,
        resolved=resolved_name,
        **stats,
    )
    return stats


# Per-share concepts ONLY -- a large ratio between disagreeing facts for a
# per-share figure has one dominant real cause (a stock split retroactively
# changing the share count, and every filing before the split keeps
# reporting its own original, un-adjusted EPS forever, since GAAP doesn't
# require re-filing old periods). Deliberately NOT applied to any dollar-
# total concept (assets, debt, revenue, etc.) -- there, a 10x disagreement
# is essentially always a real data problem (a unit-scale bug, a
# reclassification), never a stock split, so the exact same ratio that's
# safe evidence of "just a split" here would be dangerous evidence to
# auto-resolve there.
SPLIT_LIKE_CONCEPTS: tuple[str, ...] = (
    "diluted_eps",
    "basic_eps",
    "dividends_per_share",
)
MIN_SPLIT_RATIO = Decimal("1.5")
MAX_SPLIT_RATIO = Decimal("20")


def _split_safe_fill_value(
    values: list[Decimal], fact_ids: list[int]
) -> tuple[Decimal, int] | None:
    """Found live 2026-09-13 investigating a real yfinance mismatch on KLA
    Corp: our diluted_eps showed $8.47 for a real quarter, yfinance showed
    $0.847 -- exactly 10x. Traced to KLA's OWN data: its FY2025 comparative
    EPS is reported as BOTH $30.37 (the original 10-K) and $3.04 (the
    SAME period's comparative column in the FOLLOWING year's 10-K, filed
    after a real 10-for-1 split) -- a genuine Stage 2e conflict our own
    dedupe.py already correctly flags, just never resolved past `null`
    because MAX_SAFE_RATIO=1.15 (above, for ordinary small cross-filing
    revisions) correctly refuses a 10x gap. This is a DIFFERENT, equally
    real case: not a data error, a real corporate action -- checked
    broadly before trusting the ratio range: 7,982 of 217,224 real
    diluted_eps conflict groups fall in the 1.5x-20x band, none of the
    other 22 statement concepts get this treatment (see SPLIT_LIKE_CONCEPTS
    above for why). Prefers the highest fact_id (most-recently-filed,
    hence split-adjusted, value) -- the same tie-break `_safe_fill_value`
    and tag_investigator.py's `_reconcile_by_mode` already use elsewhere.
    Does NOT fix a quarter that has never yet been re-reported as a prior-
    year comparative (KLA's own real Q1 2025 standalone quarter, only one
    fact exists so there's no conflict to resolve) -- that needs a real,
    not-yet-built corporate-actions system that detects a split from a
    share-count jump and retroactively adjusts every affected historical
    per-share figure, not just the periods that happen to already have a
    second, later-filed value sitting in core.fact. Flagged, not built,
    this session -- see doc/scoping/21's already-deferred corporate-
    actions item."""
    if any(v == 0 for v in values):
        return None
    worst_ratio = max(abs(v) for v in values) / min(abs(v) for v in values)
    if not (MIN_SPLIT_RATIO <= worst_ratio <= MAX_SPLIT_RATIO):
        return None
    best_idx = max(range(len(fact_ids)), key=lambda i: fact_ids[i])
    return values[best_idx], fact_ids[best_idx]


def resolve_split_like_conflicts(
    conn: psycopg.Connection, primary_name: str, resolved_name: str
) -> dict:
    """Same shape as resolve_conflict_fill (reuses its own group-loading
    and already-resolved checks) but with _split_safe_fill_value's wider,
    per-share-specific ratio band instead of MAX_SAFE_RATIO -- run AFTER
    resolve_conflict_fill for the same pair, so it only ever fills what
    that stricter pass correctly declined, never competing with it."""
    primary_id = _concept_id(conn, primary_name)
    resolved_id = _concept_id(conn, resolved_name)
    if primary_id is None or resolved_id is None:
        return {"primary": primary_name, "skipped": "concept not found"}

    groups = _load_conflict_groups(conn, primary_id)
    already = _load_already_resolved(conn, resolved_id)

    to_insert = []
    for company_id, period_id, values, fact_ids, _filing_dates in groups:
        if (company_id, period_id) in already:
            continue
        filled = _split_safe_fill_value(list(values), list(fact_ids))
        if filled is None:
            continue
        value, fact_id = filled
        to_insert.append(
            {
                "company_id": company_id,
                "resolved_id": resolved_id,
                "period_id": period_id,
                "value": value,
                "fact_id": fact_id,
            }
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

    stats = {"conflict_groups": len(groups), "filled": len(to_insert)}
    logger.info(
        "conflict_resolution.split_like_done",
        primary=primary_name,
        resolved=resolved_name,
        **stats,
    )
    return stats


# The 5 concepts with their own existing populate step (resolve_company_
# tag_preferences / concept_fallback.py's arithmetic fallback) -- skip the
# baseline passthrough for these, since running it here (this function is
# meant to run standalone/last in the pipeline) could otherwise race an
# out-of-order rerun of their real populate step's own delete-then-
# reinsert. Conflict-fill itself is still safe and still runs for them
# (it never deletes), same as any other target.
_HAS_OWN_POPULATE_STEP = {
    "revenue_sanity_resolved",
    "cost_of_revenue_resolved",
    "gross_profit_resolved",
    "operating_expenses_resolved",
    "total_debt_resolved",
    "capex_resolved",
}


def resolve_all_conflict_fills(conn: psycopg.Connection) -> dict:
    from scrooner_pipeline.mapper.concept_fallback import (
        resolve_capex_with_software,
        resolve_depreciation_and_amortization_max,
    )

    totals = {"baseline_filled": 0, "filled": 0, "unsafe_skipped": 0}
    per_concept = {}
    # Both run BEFORE the generic loop below: capex_resolved's baseline
    # must exist (software-augmented) before resolve_conflict_fill's own
    # additive pass for it runs later in the loop; D&A has no entry in
    # CONFLICT_FILL_TARGETS at all (a standalone concept, not one of the
    # 24 dedupe-conflict-shaped statement lines), so it's simplest run
    # here rather than invented its own CLI step for one concept.
    per_concept["capex_software"] = {"rows": resolve_capex_with_software(conn)}
    per_concept["depreciation_and_amortization_max"] = {
        "rows": resolve_depreciation_and_amortization_max(conn)
    }

    # Runs BEFORE the main loop, deliberately -- found live 2026-09-15
    # verifying KLA Corp's own real, motivating case (its standalone Q1
    # 2025 quarter, never restated in any later filing): running this
    # AFTER resolve_baseline_passthrough (as an earlier version of this
    # function did) meant baseline-passthrough had ALREADY copied every
    # primary fact -- including the un-adjusted, pre-split original --
    # into diluted_eps_resolved/basic_eps_resolved/dividends_per_share_
    # resolved for every period lacking a resolved row, before this step
    # ever ran. Its own `already_resolved` check then correctly (but
    # unhelpfully) saw those periods as already resolved and skipped them
    # -- a real bug, not a hypothetical: the first live run after building
    # this returned adjusted=0 across all 3 concepts despite 1,120 real
    # detected splits existing. Moving it here is safe in both directions:
    # a period this step already resolved (this run or a prior one) is
    # skipped by its own already_resolved check regardless of order; a
    # period it can't adjust (no applicable split) is left for baseline-
    # passthrough/conflict-fill/split-like-conflicts to handle exactly as
    # before, via their own ON CONFLICT DO NOTHING.
    from scrooner_pipeline.corporate_actions.stock_splits import (
        detect_stock_splits,
        resolve_retroactive_split_adjustments,
    )

    split_detect_stats = detect_stock_splits(conn)
    per_concept["stock_splits_detected"] = split_detect_stats
    retroactive_stats = resolve_retroactive_split_adjustments(conn)
    per_concept["stock_splits_retroactive_adjustment"] = retroactive_stats
    totals["retroactive_split_adjustments"] = retroactive_stats.get("adjusted", 0)

    for primary_name, resolved_name in CONFLICT_FILL_TARGETS:
        # refresh_stale_fills is deliberately NOT called here: it is an
        # explicit, dry-run-first function whose proposals need review
        # before any write (data-team/28, 2026-10-18).
        baseline_count = 0
        if resolved_name not in _HAS_OWN_POPULATE_STEP:
            baseline_count = resolve_baseline_passthrough(
                conn, primary_name, resolved_name
            )
        stats = resolve_conflict_fill(conn, primary_name, resolved_name)
        stats["baseline_filled"] = baseline_count
        if primary_name in SPLIT_LIKE_CONCEPTS:
            split_stats = resolve_split_like_conflicts(
                conn, primary_name, resolved_name
            )
            stats["split_like_filled"] = split_stats["filled"]
            totals["filled"] += split_stats["filled"]
        per_concept[primary_name] = stats
        totals["baseline_filled"] += baseline_count
        totals["filled"] += stats.get("filled", 0)
        totals["unsafe_skipped"] += stats.get("unsafe_skipped", 0)
    oi_arithmetic = resolve_operating_income_arithmetic_fallback(conn)
    per_concept["operating_income_arithmetic"] = oi_arithmetic
    totals["operating_income_arithmetic_filled"] = oi_arithmetic.get("inserted", 0)

    logger.info("conflict_resolution.all_done", **totals)
    return {"totals": totals, "per_concept": per_concept}


# Same three SIC prefixes as yfinance_financials/line_item_map.py's
# BANK_SIC_PREFIXES, for the identical reason: a bank's own "revenue"
# (already a known, separately-flagged imperfect interest-income proxy --
# root CLAUDE.md's bank_interest_income_not_revenue) and its operating-
# expense figure don't compose the way Revenue-minus-Expenses assumes --
# verified live 2026-09-13 before excluding, not assumed: 583 real
# (company, period) pairs across these 3 SIC prefixes would otherwise have
# received a fabricated operating_income_resolved value.
_OPERATING_INCOME_ARITHMETIC_EXCLUDED_SIC_PREFIXES = ("602", "603", "606")


def resolve_operating_income_arithmetic_fallback(conn: psycopg.Connection) -> dict:
    """Derives operating_income_resolved = Revenue - Operating Expenses -
    Cost of Revenue (the last term only when a company separately reports
    one) for every (company, period) where operating_income is missing
    ENTIRELY -- a company that never tags OperatingIncomeLoss at all, not
    a dedupe.py conflict (resolve_conflict_fill above already covers that
    case). Found live 2026-09-13 verifying Robinhood (HOOD, a broker-
    dealer, SIC 6211): yfinance's own "Operating Income" for HOOD matched
    Revenue minus our stored operating_expenses EXACTLY across all 5
    quarters checked -- HOOD reports one combined operating-expense total
    with no separate Cost of Revenue line, so the formula simplifies to
    Revenue - OpEx for that shape of company; a company that DOES
    separately report Cost of Revenue gets the standard Gross Profit -
    OpEx formula instead, via the same expression.

    Verified against real data before shipping, not assumed correct by
    analogy: checked this formula against every (company, period) that
    ALREADY has a real, directly-tagged operating_income_resolved value
    (a control group, not the target population) -- 90.3% land within 2%
    of the real value when cost_of_revenue_resolved also exists (166,417
    real periods), 85.5% within 2% when it doesn't (35,348 real periods).
    Not perfect -- a real income statement can carry additional "other
    operating income/expense" lines this simple subtraction can't see --
    but purely additive (INSERT ... ON CONFLICT DO NOTHING, never
    overrides a real tag) and only ever fills a cell that would otherwise
    render blank, so an imperfect ~10-15% of fills still replace an empty
    cell, not a better one. Banks/savings institutions excluded (see the
    prefix list above)."""
    revenue_id = _concept_id(conn, "revenue_sanity_resolved")
    opex_id = _concept_id(conn, "operating_expenses_resolved")
    cor_id = _concept_id(conn, "cost_of_revenue_resolved")
    oi_id = _concept_id(conn, "operating_income_resolved")
    if None in (revenue_id, opex_id, cor_id, oi_id):
        return {"skipped": "concept not found"}

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
            select
                rev.company_id, %(oi_id)s, rev.period_id,
                rev.value - opex.value - coalesce(cor.value, 0),
                rev.source_fact_ids || opex.source_fact_ids || coalesce(cor.source_fact_ids, array[]::bigint[])
            from analytics.canonical_fact rev
            join analytics.canonical_fact opex
                on opex.company_id = rev.company_id and opex.period_id = rev.period_id and opex.canonical_concept_id = %(opex_id)s
            left join analytics.canonical_fact cor
                on cor.company_id = rev.company_id and cor.period_id = rev.period_id and cor.canonical_concept_id = %(cor_id)s
            join core.company c on c.id = rev.company_id
            where rev.canonical_concept_id = %(revenue_id)s
              and not (c.sic_code is not null and left(c.sic_code, 3) = any(%(excluded_sics)s))
              and not exists (
                  select 1 from analytics.canonical_fact existing
                  where existing.company_id = rev.company_id and existing.period_id = rev.period_id and existing.canonical_concept_id = %(oi_id)s
              )
            on conflict (company_id, canonical_concept_id, period_id) do nothing
            """,
            {
                "oi_id": oi_id,
                "opex_id": opex_id,
                "cor_id": cor_id,
                "revenue_id": revenue_id,
                "excluded_sics": list(
                    _OPERATING_INCOME_ARITHMETIC_EXCLUDED_SIC_PREFIXES
                ),
            },
        )
        inserted = cur.rowcount
    conn.commit()
    logger.info(
        "conflict_resolution.operating_income_arithmetic_done", inserted=inserted
    )
    return {"inserted": inserted}
