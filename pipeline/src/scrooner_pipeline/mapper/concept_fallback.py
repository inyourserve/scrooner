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

from dataclasses import dataclass, field
from itertools import combinations
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_blank_reason import (
    BlankReason,
    BlankReasonStore,
    PgBlankReasonStore,
)
from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.common.rule_before_image import PlannedChange
from scrooner_pipeline.common.rules_enabled import is_enabled

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
# Found live 2026-10-05 (doc/planning/51 Finding 16): 337 of 2,640
# companies missing total_debt via yfinance's own comparison tool use
# ConvertibleLongTermNotesPayable -- a real, legitimate long-term debt
# instrument not covered by any category above. Verified coexistence
# before adding (4,553 real (company, period) pairs): 66% (3,005) have NO
# other debt tag at all -- a genuine, safe-to-use standalone signal. The
# other 34% (1,548) coexist with another debt tag and show real evidence
# of double-counting risk if simply summed in -- e.g. one company's
# ConvertibleLongTermNotesPayable value exactly equals its own LongTermDebt
# figure (the same debt tagged twice, a more-granular instrument tag
# alongside an aggregate one). Added strictly as a LAST-RESORT fallback in
# compute_total_debt() below -- only reached when every category above
# found nothing at all, so it can never double-count against a value
# already captured by another path.
DEBT_CONVERTIBLE_NOTES_FALLBACK = ("ConvertibleLongTermNotesPayable",)
TOTAL_DEBT_TAGS = (
    DEBT_ALL_IN
    + DEBT_ALL_IN_LEASE
    + DEBT_LTD_INCL_CURRENT
    + DEBT_LTD_NONCURRENT
    + DEBT_LTD_CURRENT
    + DEBT_CURRENT_ALL
    + DEBT_SHORT_TERM
    + DEBT_CARRYING_CHECK
    + DEBT_CONVERTIBLE_NOTES_FALLBACK
)

# --- total_debt guards (2026-10-21, Tag Mapper results file 31 section B) ---
# Instrument-level borrowing tags. They are NEVER summed into a total here
# (that is the proposal-only R3 composition); they are read only by the R5
# guards below, because a published total cannot be smaller than one of its
# own parts and a total of 0 cannot sit beside a nonzero debt tag. Each tag
# is a real us-gaap borrowing element; DebtInstrumentCarryingAmount is
# deliberately absent (gross, per-instrument cross-check only).
DEBT_INSTRUMENT_TAGS = (
    "NotesPayable",
    "NotesPayableCurrent",
    "LongTermNotesPayable",
    "LongTermLineOfCredit",
    "SeniorNotes",
    "SubordinatedDebt",
    "AdvancesFromFederalHomeLoanBanks",
    "LineOfCredit",
    "LinesOfCreditCurrent",
    "ConvertibleNotesPayable",
    "ConvertibleNotesPayableCurrent",
    "ConvertibleDebt",
    "ConvertibleDebtCurrent",
    "ConvertibleDebtNoncurrent",
    "LoansPayable",
    "LoansPayableCurrent",
    "LongTermLoansPayable",
    "SecuredDebt",
    "SecuredDebtCurrent",
    "UnsecuredDebt",
    "UnsecuredDebtCurrent",
    "OtherLongTermDebt",
    "OtherLongTermDebtNoncurrent",
    "OtherLongTermDebtCurrent",
    "OtherShortTermBorrowings",
    "OtherBorrowings",
    "OtherNotesPayable",
    "OtherNotesPayableCurrent",
    "ShortTermBankLoansAndNotesPayable",
    "SecuredLongTermDebt",
    "UnsecuredLongTermDebt",
    "NotesAndLoansPayable",
    "NotesAndLoansPayableCurrent",
    "SeniorLongTermNotes",
    "SeniorNotesCurrent",
    "JuniorSubordinatedNotes",
    "SubordinatedDebtCurrent",
    "SubordinatedLongTermDebt",
    "NotesPayableToBank",
    "NotesPayableToBankCurrent",
    "NotesPayableToBankNoncurrent",
    "LoansPayableToBank",
    "LoansPayableToBankCurrent",
    "CommercialPaperAtCarryingValue",
    "LongTermNotesAndLoans",
    "ConvertibleSubordinatedDebt",
    "ConvertibleSubordinatedDebtCurrent",
    "ConvertibleSubordinatedDebtNoncurrent",
    "NonRecourseDebt",
    "ShortTermNonBankLoansAndNotesPayable",
    "WarehouseAgreementBorrowings",
    "OtherLongTermNotesPayable",
    "OtherLoansPayable",
    "OtherLoansPayableCurrent",
    "OtherLoansPayableLongTerm",
    "SecuredDebtOther",
)
# Role tags that can select a composition path (every tag compute_total_debt
# can sum or pick), minus the gross carrying-amount cross-check.
DEBT_ROLE_TAGS = tuple(t for t in TOTAL_DEBT_TAGS if t not in DEBT_CARRYING_CHECK)
# Tags the floor guard compares against (instrument tags plus the
# convertible last-resort tag, which is itself an instrument).
DEBT_FLOOR_TAGS = DEBT_INSTRUMENT_TAGS + DEBT_CONVERTIBLE_NOTES_FALLBACK
# Everything the resolver must load per balance-sheet date.

# R5 floor tolerance: the published total may sit below a single filed
# instrument tag by at most this fraction of that tag.
DEBT_FLOOR_TOLERANCE = Decimal("0.02")

# R5 floor exemption (data-team lane 3, 2026-10-22). A published total below a single filed
# instrument tag is NOT blanked when the gap equals a filed unamortized discount / issuance cost
# (face value of the instrument vs carrying value of the total): HIG NotesPayable 4,482M vs total
# 4,366M, gap 116M = DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet 116M. No
# other exemption (no 5% tolerance, no "own total" exemption): 18 of 681 floor blanks in the
# top-1000 dry run match; shifting the gap by +-10% or more matches 0 of 681 (coincidence control).
DEBT_DISCOUNT_TAGS = (
    "DebtInstrumentUnamortizedDiscount",
    "DebtInstrumentUnamortizedDiscountCurrent",
    "DebtInstrumentUnamortizedDiscountNoncurrent",
    "DebtInstrumentUnamortizedDiscountPremiumNet",
    "DebtInstrumentUnamortizedPremium",
)
DEBT_ISSUANCE_COST_TAGS = (
    "DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet",
    "DebtIssuanceCostsLineOfCreditArrangementsNet",
    "DeferredFinanceCostsNet",
    "DeferredFinanceCostsCurrentNet",
    "DeferredFinanceCostsNoncurrentNet",
    "UnamortizedDebtIssuanceExpense",
    "DebtIssuanceCosts",
)
DEBT_DISCOUNT_COST_TAGS = DEBT_DISCOUNT_TAGS + DEBT_ISSUANCE_COST_TAGS
DEBT_DISCOUNT_MATCH_TOLERANCE = Decimal("0.005")  # of the gap

# Current-debt parts that DebtCurrent may legitimately be made of (R6 explained check).
DEBT_CURRENT_PART_TAGS = (
    "ShortTermBorrowings",
    "CommercialPaper",
    "OtherShortTermBorrowings",
    "ShortTermBankLoansAndNotesPayable",
    "LinesOfCreditCurrent",
    "NotesPayableCurrent",
    "ConvertibleNotesPayableCurrent",
    "LongTermDebtCurrent",
    "LongTermDebtAndCapitalLeaseObligationsCurrent",
)
# Anchors that make a long-term block present (R7 partial-component check).
DEBT_LONG_TERM_ANCHOR_TAGS = (
    "LongTermDebtNoncurrent",
    "LongTermDebtAndCapitalLeaseObligations",
    "LongTermDebt",
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
)
FALLBACK_PATHS = frozenset(
    {
        "noncurrent+debt_current",
        "noncurrent+current+short_term",
        "ltd+debt_current_confirmed",
    }
)

TOTAL_DEBT_LOAD_TAGS = tuple(
    dict.fromkeys(
        TOTAL_DEBT_TAGS
        + DEBT_INSTRUMENT_TAGS
        + DEBT_DISCOUNT_COST_TAGS
        + DEBT_CURRENT_PART_TAGS
        + ("DebtAndCapitalLeaseObligations",)
    )
)

GUARD_CONTAINMENT = "r1_containment"
GUARD_ZERO = "r5_zero"
GUARD_FLOOR = "r5_floor"
GUARD_FALLBACK = "r6_fallback_overcount"
GUARD_PARTIAL = "r7_partial_component"
GUARD_PREFERENCE = "r4_preference"
ALL_DEBT_GUARDS = frozenset(
    {GUARD_CONTAINMENT, GUARD_ZERO, GUARD_FLOOR, GUARD_FALLBACK, GUARD_PARTIAL}
)
# Rule ID of the family (registry RF-11). The flag lists this ID to enable every sub-rule, or
# "<ID>/<guard>" (e.g. debt.total_debt_consistency@1/r5_floor) to enable one.
RULE_DEBT = "debt.total_debt_consistency@1"


def debt_guards_active(environ: dict[str, str] | None = None) -> frozenset[str]:
    """Guards enabled through SCROONER_RULES_ENABLED; empty (flag OFF) = pre-guard behaviour,
    byte-identical to the compose-only path."""
    if is_enabled(RULE_DEBT, environ):
        return ALL_DEBT_GUARDS
    return frozenset(
        g for g in ALL_DEBT_GUARDS if is_enabled(f"{RULE_DEBT}/{g}", environ)
    )


def debt_preference_guard_active(environ: dict[str, str] | None = None) -> bool:
    return is_enabled(RULE_DEBT, environ) or is_enabled(
        f"{RULE_DEBT}/{GUARD_PREFERENCE}", environ
    )


REASON_UNDECIDABLE_ZERO = (
    "debt composition undecidable: total would be 0 while a debt tag is nonzero"
)
REASON_UNDECIDABLE_FLOOR = (
    "debt composition undecidable: total is below a single filed debt instrument tag"
)
REASON_UNDECIDABLE_FALLBACK = "debt composition undecidable: current debt total is not explained by its filed parts"
REASON_UNDECIDABLE_LEASE = (
    "debt composition undecidable: total is below the filed lease-inclusive debt total"
)
REASON_PARTIAL_COMPONENT = "debt composition undecidable: only current debt portions are filed (no long-term block)"

# R4: a total_debt company_tag_preference is honoured only when the
# preferred tag is itself a TOTAL. Every one of the 41 preference rows
# existing on 2026-10-21 names a single component (LongTermDebt,
# DebtCurrent, ShortTermBorrowings, OtherLongTermDebtNoncurrent,
# SecuredDebtCurrent), e.g. WFC ShortTermBorrowings 18,323M while its
# face debt is 193,035M.
DEBT_TOTAL_PREFERENCE_TAGS = frozenset(DEBT_ALL_IN + DEBT_ALL_IN_LEASE)


def debt_preference_is_applicable(
    taxonomy: str, tag: str, guards: frozenset[str] | None = None
) -> bool:
    """False when a total_debt company_tag_preference names a single
    component rather than a total (R4). The row stays in the database; the
    resolvers just do not apply it. With the R4 guard not active (flag OFF,
    `guards` given or read from SCROONER_RULES_ENABLED) every preference applies,
    exactly as before the guard."""
    if guards is None:
        guards = debt_guards_active() | (
            frozenset({GUARD_PREFERENCE})
            if debt_preference_guard_active()
            else frozenset()
        )
    if GUARD_PREFERENCE not in guards:
        return True
    return taxonomy == "us-gaap" and tag in DEBT_TOTAL_PREFERENCE_TAGS


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
    stats: dict[str, Any] = {"considered": 0, "ok": 0, "errored": 0, "rows_written": 0}
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


def _compose_total_debt(
    facts: dict[str, tuple[Decimal, int]],
) -> tuple[Decimal, list[int], str] | None:
    """Path selection only (the pre-2026-10-21 compute_total_debt body); the
    guards live in evaluate_total_debt(). Total debt for ONE balance-sheet date from the company's own tags
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
            and debt_current is not None
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
    convertible_notes = pick(DEBT_CONVERTIBLE_NOTES_FALLBACK)
    if convertible_notes is not None:
        return done([convertible_notes], "convertible_notes_fallback")
    return None


@dataclass(frozen=True)
class DebtDecision:
    """Outcome of evaluate_total_debt() for one balance-sheet date.
    `value` is None when no total can be published; then `reason` says why
    (None reason = the tags never gave a total, as before the guards)."""

    value: Decimal | None
    source_fact_ids: list[int] = field(default_factory=list)
    path: str | None = None
    reason: str | None = None
    guards_fired: tuple[str, ...] = ()


def _containment_ok(facts: dict[str, tuple[Decimal, int]]) -> bool:
    """R1 guard: bare LongTermDebt may anchor the long-term block only if it
    contains every part filed beside it: >= LongTermDebtNoncurrent,
    >= LongTermDebtCurrent and >= half of LongTermDebtAndCapitalLeaseObligations
    (MAR 23M beside 16,204M noncurrent; TSCO, CSGP, WTRG, DPZ, ALGM)."""
    ltd = facts["LongTermDebt"][0]
    for tag in ("LongTermDebtNoncurrent", "LongTermDebtCurrent"):
        if tag in facts and ltd < facts[tag][0]:
            return False
    lease_nc = facts.get("LongTermDebtAndCapitalLeaseObligations")
    return not (lease_nc is not None and ltd < lease_nc[0] / 2)


def _discount_explains_gap(facts: dict[str, tuple[Decimal, int]], gap: Decimal) -> bool:
    """True when `gap` (instrument tag minus published total) equals a filed unamortized
    discount / issuance cost: one tag, or one discount-or-premium tag plus one issuance-cost
    tag, within DEBT_DISCOUNT_MATCH_TOLERANCE of the gap. Signs are ignored (filers tag the
    same amount positive or negative)."""
    tol = gap * DEBT_DISCOUNT_MATCH_TOLERANCE
    discounts = [abs(facts[t][0]) for t in DEBT_DISCOUNT_TAGS if t in facts]
    costs = [abs(facts[t][0]) for t in DEBT_ISSUANCE_COST_TAGS if t in facts]
    singles = discounts + costs
    if any(abs(v - gap) <= tol for v in singles):
        return True
    return any(abs(d + c - gap) <= tol for d in discounts for c in costs)


def _current_parts_explain(
    facts: dict[str, tuple[Decimal, int]], debt_current: Decimal
) -> bool:
    """DebtCurrent is made of filed current-debt parts: some subset of them sums to it within
    the floor tolerance (PFE 2020: 556 + 145 + 2,002 = 2,703). Zero DebtCurrent is explained,
    and so is a DebtCurrent with no filed part beside it. When parts ARE filed and no subset
    matches, the composition is contradicted (CVX 2016: 19,840 vs 10,840 + 6,253 ...)."""
    if debt_current == 0:
        return True
    parts = [
        facts[t][0] for t in DEBT_CURRENT_PART_TAGS if t in facts and facts[t][0] > 0
    ]
    if not parts:
        return True  # nothing filed beside it that could contradict it (MMM 2024-03-31)
    tol = debt_current * DEBT_FLOOR_TOLERANCE
    for n in range(1, len(parts) + 1):
        for combo in combinations(parts, n):
            if abs(sum(combo) - debt_current) <= tol:
                return True
    return False


def _check_guard_reached_fallback(
    facts: dict[str, tuple[Decimal, int]], result: tuple[Decimal, list[int], str]
) -> tuple[str, tuple[Decimal, list[int], str] | None] | None:
    """R6, applied only when a guard disqualified the primary path so a fallback path was newly
    reached (CVX 2016, DPZ 2024). Returns None (accept), ("hold", None) or
    ("replace", new_result)."""
    value, _ids, path = result
    if (
        path in ("noncurrent+debt_current", "ltd+debt_current_confirmed")
        and "DebtCurrent" in facts
    ):
        if not _current_parts_explain(facts, facts["DebtCurrent"][0]):
            return REASON_UNDECIDABLE_FALLBACK, None
    lease_total = facts.get("DebtAndCapitalLeaseObligations")
    if lease_total is not None and value < lease_total[0] * (1 - DEBT_FLOOR_TOLERANCE):
        nc = facts.get("LongTermDebtAndCapitalLeaseObligations")
        cur = facts.get("LongTermDebtAndCapitalLeaseObligationsCurrent")
        if (
            nc is not None
            and cur is not None
            and abs(nc[0] + cur[0] - lease_total[0]) <= lease_total[0] * Decimal("0.01")
        ):
            # the lease-inclusive noncurrent + current blocks reproduce the company's own
            # lease-inclusive total (DPZ 2024: 3,825,659 + 1,149,679 = 4,975,338)
            return "replace", (nc[0] + cur[0], [nc[1], cur[1]], "lease_family_sum")
        return REASON_UNDECIDABLE_LEASE, None
    return None


def evaluate_total_debt(
    facts: dict[str, tuple[Decimal, int]],
    guards: frozenset[str] = ALL_DEBT_GUARDS,
) -> DebtDecision:
    """compute_total_debt plus the eligible guards from the Tag Mapper's
    results (data-team/31 section B; R2 and the "prefer N + C" reordering are
    proposal-only and deliberately not here). A guard that cannot produce a
    value yields value=None with a reason, never a guess.

      r1_containment  LongTermDebt that fails containment is removed before
                      path selection, so it cannot outrank the face tags.
      r5_zero         A total of 0 while any role or instrument debt tag is
                      nonzero is recomputed with zero-valued tags removed;
                      still 0/none -> blank.
      r5_floor        A total below a single filed instrument tag by more
                      than 2% of that tag is not published, unless the gap
                      equals a filed unamortized discount / issuance cost.
      r6_fallback_overcount
                      When a guard made the composition fall to a fallback
                      path, DebtCurrent must be explained by its filed parts
                      (else blank: CVX 2016) and the total must not sit below
                      the filed lease-inclusive total (replaced by the lease
                      family sum when that reproduces it: DPZ 2024; else blank).
      r7_partial_component
                      The fallback path composed only current portions (no
                      long-term block filed): blank (AAPL 2015-09-26 10,999M
                      against a filed 53,463M long-term debt).

    `facts` maps tag -> (value, fact_id) and may carry instrument tags; they
    never enter a path sum."""
    fired: list[str] = []
    work = facts
    if (
        GUARD_CONTAINMENT in guards
        and "LongTermDebt" in work
        and not _containment_ok(work)
    ):
        work = {t: v for t, v in work.items() if t != "LongTermDebt"}
        fired.append(GUARD_CONTAINMENT)

    result = _compose_total_debt(work)

    if GUARD_ZERO in guards and result is not None and result[0] == 0:
        family = DEBT_ROLE_TAGS + DEBT_INSTRUMENT_TAGS
        if any(t in work and work[t][0] != 0 for t in family):
            fired.append(GUARD_ZERO)
            stripped = {
                t: v for t, v in work.items() if not (t in DEBT_ROLE_TAGS and v[0] == 0)
            }
            result = _compose_total_debt(stripped)
            if result is None or result[0] == 0:
                return DebtDecision(
                    None, reason=REASON_UNDECIDABLE_ZERO, guards_fired=tuple(fired)
                )

    if (
        GUARD_PARTIAL in guards
        and result is not None
        and result[2] == "noncurrent+current+short_term"
        and not any(t in work for t in DEBT_LONG_TERM_ANCHOR_TAGS)
        and any(
            t in work and work[t][0] > 0
            for t in (
                "LongTermDebtCurrent",
                "LongTermDebtAndCapitalLeaseObligationsCurrent",
            )
        )
    ):
        fired.append(GUARD_PARTIAL)
        return DebtDecision(
            None, reason=REASON_PARTIAL_COMPONENT, guards_fired=tuple(fired)
        )

    if (
        GUARD_FALLBACK in guards
        and result is not None
        and fired
        and result[2] in FALLBACK_PATHS
    ):
        verdict = _check_guard_reached_fallback(work, result)
        if verdict is not None:
            what, replacement = verdict
            fired.append(GUARD_FALLBACK)
            if replacement is None:
                return DebtDecision(None, reason=what, guards_fired=tuple(fired))
            result = replacement

    if GUARD_FLOOR in guards and result is not None:
        value = result[0]
        for tag in DEBT_FLOOR_TAGS:
            if tag not in work:
                continue
            part = work[tag][0]
            if (
                part > 0
                and value < part
                and (part - value) > part * DEBT_FLOOR_TOLERANCE
                and not _discount_explains_gap(work, part - value)
            ):
                fired.append(GUARD_FLOOR)
                return DebtDecision(
                    None, reason=REASON_UNDECIDABLE_FLOOR, guards_fired=tuple(fired)
                )

    if result is None:
        return DebtDecision(None, guards_fired=tuple(fired))
    return DebtDecision(result[0], result[1], result[2], guards_fired=tuple(fired))


def compute_total_debt(
    facts: dict[str, tuple[Decimal, int]],
) -> tuple[Decimal, list[int], str] | None:
    """(value, source_fact_ids, path) or None; see evaluate_total_debt() for
    the guards and for the blank reason. Path selection rules: _compose_total_debt."""
    decision = evaluate_total_debt(facts, debt_guards_active())
    if decision.value is None or decision.path is None:
        return None
    return decision.value, decision.source_fact_ids, decision.path


def resolve_total_debt_components(
    conn: psycopg.Connection,
    ciks: set[str],
    chunk_size: int = 200,
    *,
    dry_run: bool = False,
    reason_store: BlankReasonStore | None = None,
    run_id: str | None = None,
    environ: dict[str, str] | None = None,
) -> dict:
    """Writes total_debt_resolved for every instant period from core.fact
    via compute_total_debt(). Bulk-loads one chunk of companies per query
    (no per-row loop over core.fact). Companies with a total_debt
    company_tag_preference that names a TOTAL tag are skipped -- their rows
    belong to sanity/tag_investigator.resolve_company_tag_preferences(), the
    same one-writer-per-company exemption the parser rows already get. A
    preference naming a single component (all 41 existing rows) is not
    applied (R4, debt_preference_is_applicable) and its company is composed
    here like any other.

    All guards are behind the rules_enabled flag (default OFF = the pre-guard
    composition, byte-identical). `dry_run` evaluates every guard as ON and
    writes nothing (rows, reasons, deletes); the cells that would change are
    returned under stats["planned"] (before = the stored value). When any guard
    is active and the run is live, every blocked instant's reason is persisted
    through `reason_store` (default: the Postgres store, which refuses to run
    without analytics.cell_blank_reason) -- a guard may not blank a cell it
    cannot explain. The reason rows' delete scope is exactly this rule's rows
    for the companies processed."""
    guards = ALL_DEBT_GUARDS if dry_run else debt_guards_active(environ)
    pref_guard = dry_run or debt_preference_guard_active(environ)
    live_guards = bool(guards) and not dry_run
    if live_guards and reason_store is None:
        reason_store = PgBlankReasonStore(conn)
    if live_guards and isinstance(reason_store, PgBlankReasonStore):
        reason_store.require_table()
    stats: dict[str, Any] = {
        "companies": 0,
        "skipped_preference": 0,
        "rows_written": 0,
        "errored": 0,
        "paths": {},
        "guards": {},
        "blocked": {},
        "reasons_written": 0,
        "dry_run": dry_run,
        "planned": [],
    }
    resolved_id = _concept_id(conn, "total_debt_resolved")
    total_debt_id = _concept_id(conn, "total_debt")
    with conn.cursor() as cur:
        if pref_guard:
            cur.execute(
                """
                select c.id from core.company c
                where c.cik = any(%s)
                  and not exists (select 1 from analytics.company_tag_preference p
                                  where p.company_id = c.id and p.canonical_concept_id = %s
                                    and p.taxonomy = 'us-gaap' and p.tag = any(%s))
                order by c.id
                """,
                (list(ciks), total_debt_id, sorted(DEBT_TOTAL_PREFERENCE_TAGS)),
            )
        else:
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
                           f.company_id, f.period_id, c.tag, f.value, f.id, p.end_date
                    from core.fact f
                    join core.concept c on c.id = f.concept_id
                    join core.period p on p.id = f.period_id
                    where f.company_id = any(%s) and f.is_authoritative
                      and c.taxonomy = 'us-gaap' and c.tag = any(%s)
                      and p.period_type = 'instant'
                    order by f.company_id, f.period_id, c.tag, f.id desc
                    """,
                    (chunk, list(TOTAL_DEBT_LOAD_TAGS)),
                )
                by_period: dict[tuple[int, int], dict] = {}
                period_end: dict[int, Any] = {}
                for (
                    company_id,
                    period_id,
                    tag,
                    value,
                    fact_id,
                    end_date,
                ) in cur.fetchall():
                    by_period.setdefault((company_id, period_id), {})[tag] = (
                        value,
                        fact_id,
                    )
                    period_end[period_id] = end_date
                stored: dict[tuple[int, int], Decimal] = {}
                if dry_run:
                    cur.execute(
                        "select company_id, period_id, value from analytics.canonical_fact where canonical_concept_id = %s and company_id = any(%s)",
                        (resolved_id, chunk),
                    )
                    stored = {(c, p): v for c, p, v in cur.fetchall()}
                    cur.execute(
                        "select id, cik from core.company where id = any(%s)", (chunk,)
                    )
                    cik_by_id = dict(cur.fetchall())

                rows = []
                reasons: dict[int, list[BlankReason]] = {cid: [] for cid in chunk}
                for (company_id, period_id), facts in by_period.items():
                    decision = evaluate_total_debt(facts, guards)
                    for g in decision.guards_fired:
                        stats["guards"][g] = stats["guards"].get(g, 0) + 1
                    new_value = decision.value if decision.path is not None else None
                    if dry_run:
                        before = stored.get((company_id, period_id))
                        if before != new_value:
                            stats["planned"].append(
                                PlannedChange(
                                    rule_id=RULE_DEBT,
                                    cik=cik_by_id[company_id],
                                    company_id=company_id,
                                    data_point="total_debt_resolved",
                                    period_end=period_end[period_id],
                                    before=before,
                                    after=new_value,
                                    reason=(
                                        "+".join(decision.guards_fired)
                                        or "unchanged_by_guards"
                                    ),
                                )
                            )
                    if decision.value is None or decision.path is None:
                        if decision.reason is not None:
                            stats["blocked"][decision.reason] = (
                                stats["blocked"].get(decision.reason, 0) + 1
                            )
                            reasons[company_id].append(
                                BlankReason(
                                    company_id=company_id,
                                    data_point="total_debt_resolved",
                                    period_grain="instant",
                                    period_start=period_end[period_id],
                                    period_end=period_end[period_id],
                                    basis="resolved",
                                    rule_id=RULE_DEBT,
                                    reason_code="guard_hidden",
                                    detail={
                                        "reason": decision.reason,
                                        "guards_fired": list(decision.guards_fired),
                                    },
                                )
                            )
                        continue
                    value, fact_ids, path = (
                        decision.value,
                        decision.source_fact_ids,
                        decision.path,
                    )
                    stats["paths"][path] = stats["paths"].get(path, 0) + 1
                    rows.append((company_id, resolved_id, period_id, value, fact_ids))

                if dry_run:
                    stats["companies"] += len(chunk)
                    continue
                cur.execute(
                    "delete from analytics.canonical_fact where canonical_concept_id = %s and company_id = any(%s)",
                    (resolved_id, chunk),
                )
                if rows:
                    cur.executemany(
                        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, %s, %s)",
                        rows,
                    )
                if live_guards:
                    assert reason_store is not None
                    for company_id, company_reasons in reasons.items():
                        stats["reasons_written"] += reason_store.replace(
                            company_id, RULE_DEBT, run_id or "adhoc", company_reasons
                        )
            if dry_run:
                continue
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
        **{
            k: v
            for k, v in stats.items()
            if k not in ("paths", "guards", "blocked", "planned")
        },
        paths=stats["paths"],
        guards=stats["guards"],
        blocked=stats["blocked"],
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
    stats: dict[str, Any] = {
        "considered": len(ARITHMETIC_FALLBACKS),
        "rows_written": {},
    }
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
