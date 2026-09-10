"""Time-series self-consistency check (2026-09-08) -- zero external API
calls, unlike every other checker built this session. Compares a
company's own value for a period against its own value for the SAME
fiscal_period one fiscal year earlier (fiscal-calendar-aware -- matches
on `fiscal_year - 1` with the identical `fiscal_period` label, the same
convention `mapper/ttm.py`'s own YoY growth metrics already use, not a
calendar-date comparison which would be wrong for a non-calendar fiscal
year).

Catches a class of bug nothing else built today can: a value that's
internally wrong (e.g. a unit-scaling error) but happens to look
plausible in isolation sails past yfinance (only sees the LATEST period)
and even the SEC Frames checker (which only proves "we copied the chosen
tag's value correctly" -- if SEC itself served the wrong-looking value,
Frames agrees with us and stays silent). A multi-year-implausible swing
in a company's OWN history is a real, free signal neither of those
produce.

Two distinct severities:
  outlier          -- a YoY ratio outside a plausible bound for this
                      concept, given a materially-sized prior-period base
                      (a tiny company going from $1 to $100 is a 100x
                      ratio but immaterial -- guarded by each concept's
                      own materiality floor, same idiom as
                      yfinance_check.py's REVENUE_ZERO_CHECK_MATERIAL_
                      THRESHOLD).
  sign_violation   -- an absolute check needing no history at all: a
                      concept that structurally can never be negative
                      (revenue, total assets, cash) IS negative. Stronger,
                      more unambiguous evidence of a bug than any
                      ratio-based check."""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.yfinance_financials.line_item_map import CONCEPT_FOR_COMPARISON

logger = structlog.get_logger()

SEVERITY_OK = "ok"
SEVERITY_OUTLIER = "outlier"
SEVERITY_SIGN_VIOLATION = "sign_violation"

# (concept_name, min_ratio, max_ratio, materiality_floor, never_negative)
# Deliberately wide bounds -- a real company CAN legitimately multiply
# net income several-fold in one real turnaround year. This flags "worth
# a second look", not "definitely wrong" -- same discipline as every
# other severity threshold this session calibrated against real data
# before trusting it (see module docstrings across sanity/, yfinance_
# financials/, frames/ for the live-verified precedent this follows).
CONCEPTS_TO_CHECK: list[tuple[str, float, float, int, bool]] = [
    ("revenue", 0.1, 10.0, 1_000_000, True),
    ("net_income", 0.05, 20.0, 1_000_000, False),
    ("cfo", 0.05, 20.0, 1_000_000, False),
    ("operating_income", 0.05, 20.0, 1_000_000, False),
    ("total_assets", 0.2, 5.0, 1_000_000, True),
    ("cash_and_equivalents", 0.05, 20.0, 100_000, True),
    ("stockholders_equity", 0.05, 20.0, 1_000_000, False),
]

# For a sign flip on a concept that CAN legitimately be negative (a real
# turnaround or a new loss), the ordinary ratio bound doesn't apply --
# require a much higher bar (this multiplier on max_ratio) before
# flagging a sign flip specifically, since flips are inherently more
# volatile and common than same-sign growth.
SIGN_FLIP_EXTRA_MULTIPLIER = 5


def check_yoy(
    company_id: int, canonical_concept_id: int, period_id: int, period_end, fiscal_year: int, fiscal_period: str,
    current_value: Decimal, prior_value: Decimal | None,
    min_ratio: float, max_ratio: float, materiality_floor: int, never_negative: bool,
) -> dict:
    """Pure, no DB access -- unit-testable in isolation."""
    base = {
        "company_id": company_id, "concept_id": canonical_concept_id, "period_id": period_id,
        "period_end": period_end, "fiscal_year": fiscal_year, "fiscal_period": fiscal_period,
        "current_value": current_value, "prior_value": prior_value, "prior_period_end": None, "yoy_ratio": None,
    }

    if never_negative and current_value < 0:
        return {**base, "severity": SEVERITY_SIGN_VIOLATION}

    if prior_value is None or abs(prior_value) < Decimal(materiality_floor):
        # No prior period to compare against, or the prior base is too
        # small for a ratio to mean anything -- not flaggable either way.
        return {**base, "severity": SEVERITY_OK}

    is_sign_flip = not never_negative and (prior_value < 0) != (current_value < 0) and prior_value != 0
    if is_sign_flip:
        swing_ratio = abs(current_value) / abs(prior_value)
        severity = SEVERITY_OUTLIER if swing_ratio > Decimal(max_ratio) * SIGN_FLIP_EXTRA_MULTIPLIER else SEVERITY_OK
        return {**base, "yoy_ratio": swing_ratio if current_value >= 0 else -swing_ratio, "severity": severity}

    if prior_value == 0:
        return {**base, "severity": SEVERITY_OK}

    ratio = current_value / prior_value
    severity = SEVERITY_OUTLIER if (ratio < Decimal(min_ratio) or ratio > Decimal(max_ratio)) else SEVERITY_OK
    return {**base, "yoy_ratio": ratio, "severity": severity}


def _canonical_concept_id(conn: psycopg.Connection, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
        return cur.fetchone()[0]


def _load_yoy_pairs(conn: psycopg.Connection, concept_id: int, company_id: int | None = None) -> list[tuple]:
    """One bulk query for the WHOLE population per concept (or, when
    `company_id` is given, just that one company -- added 2026-09-08
    for incidents/verifier.py, which needs to re-check a single
    company cheaply rather than the whole population) -- a self-join
    of canonical_fact/period on (fiscal_year, fiscal_period) shifted by
    one year, entirely in SQL. No per-company loop at all."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select cur.company_id, cur.period_id, p_cur.end_date, p_cur.fiscal_year, p_cur.fiscal_period,
                   cur.value, prior.value, p_prior.end_date
            from analytics.canonical_fact cur
            join core.period p_cur on p_cur.id = cur.period_id
            left join core.period p_prior
                on p_prior.company_id = p_cur.company_id
               and p_prior.fiscal_year = p_cur.fiscal_year - 1
               and p_prior.fiscal_period = p_cur.fiscal_period
            left join analytics.canonical_fact prior
                on prior.period_id = p_prior.id and prior.canonical_concept_id = cur.canonical_concept_id
            where cur.canonical_concept_id = %s and p_cur.fiscal_period is not null
              and (%s::bigint is null or cur.company_id = %s::bigint)
            """,
            (concept_id, company_id, company_id),
        )
        return cur.fetchall()


_UPSERT_SQL = """
    insert into analytics.timeseries_outlier_check
        (company_id, canonical_concept_id, period_id, period_end, fiscal_year, fiscal_period,
         current_value, prior_value, prior_period_end, yoy_ratio, severity, checked_at)
    values (%(company_id)s, %(concept_id)s, %(period_id)s, %(period_end)s, %(fiscal_year)s, %(fiscal_period)s,
            %(current_value)s, %(prior_value)s, %(prior_period_end)s, %(yoy_ratio)s, %(severity)s, now())
    on conflict (company_id, canonical_concept_id, period_id) do update
        set current_value = excluded.current_value, prior_value = excluded.prior_value,
            prior_period_end = excluded.prior_period_end, yoy_ratio = excluded.yoy_ratio,
            severity = excluded.severity, checked_at = now()
"""


def run_concept(
    conn: psycopg.Connection, concept_name: str, min_ratio: float, max_ratio: float, materiality_floor: int,
    never_negative: bool, company_id: int | None = None,
) -> dict:
    """`company_id` optionally scopes both the load AND the delete to
    one company (added 2026-09-08, incidents/verifier.py) -- the delete
    MUST be scoped identically to the load, or a single-company rerun
    would wipe every other company's rows for this concept (the exact
    shared-table-write trap pipeline/CLAUDE.md already documents
    elsewhere in this project).

    Checks the *_resolved concept where one exists (CONCEPT_FOR_
    COMPARISON, same mapping yfinance_financials/compare.py already
    uses) -- found live 2026-09-09 investigating a real sign_violation
    (Mohawk Industries, Plexus Corp: both had a spurious negative value
    under the raw us-gaap:Revenues tag while their real revenue sat
    correctly under a different, already-mapped tag). The FIX (a
    company_tag_preference merged into revenue_sanity_resolved) was
    real and correct, but this checker was still reading the raw,
    never-fixed `revenue` concept -- meaning a real, applied fix could
    never clear its own alert, for any of the 5 concepts with a
    _resolved variant (revenue, gross_profit, cost_of_revenue,
    operating_expenses, total_debt). Checking the resolved concept
    instead means canonical_concept_id in timeseries_outlier_check (and
    therefore analytics.data_incident's metric_or_concept) now reads
    e.g. 'revenue_sanity_resolved' rather than 'revenue' for these 5 --
    more transparent about what was actually checked, not a
    regression."""
    stats = {"considered": 0, SEVERITY_OK: 0, SEVERITY_OUTLIER: 0, SEVERITY_SIGN_VIOLATION: 0}
    concept_id = _canonical_concept_id(conn, CONCEPT_FOR_COMPARISON.get(concept_name, concept_name))
    pairs = _load_yoy_pairs(conn, concept_id, company_id)
    stats["considered"] = len(pairs)

    findings = []
    for row_company_id, period_id, period_end, fiscal_year, fiscal_period, current_value, prior_value, prior_period_end in pairs:
        row = check_yoy(
            row_company_id, concept_id, period_id, period_end, fiscal_year, fiscal_period,
            current_value, prior_value, min_ratio, max_ratio, materiality_floor, never_negative,
        )
        row["prior_period_end"] = prior_period_end
        stats[row["severity"]] += 1
        findings.append(row)

    with conn.cursor() as cur:
        if company_id is None:
            cur.execute("delete from analytics.timeseries_outlier_check where canonical_concept_id = %s", (concept_id,))
        else:
            cur.execute(
                "delete from analytics.timeseries_outlier_check where canonical_concept_id = %s and company_id = %s",
                (concept_id, company_id),
            )
        if findings:
            cur.executemany(_UPSERT_SQL, findings)
    conn.commit()

    logger.info("timeseries_check.done", concept=concept_name, company_id=company_id, **stats)
    return stats


def run_all(conn: psycopg.Connection, company_id: int | None = None) -> dict:
    totals = {"considered": 0, SEVERITY_OK: 0, SEVERITY_OUTLIER: 0, SEVERITY_SIGN_VIOLATION: 0}
    for concept_name, min_ratio, max_ratio, materiality_floor, never_negative in CONCEPTS_TO_CHECK:
        stats = run_concept(conn, concept_name, min_ratio, max_ratio, materiality_floor, never_negative, company_id)
        for key in totals:
            totals[key] += stats.get(key, 0)
    logger.info("timeseries_check.all_done", company_id=company_id, **totals)
    return totals
