"""Coverage-score tracking (doc 41, 2026-09-02). Computes and persists one
daily snapshot of data-point coverage -- per canonical_concept (tag-level,
what the Collector/Normalizer/Mapper's resolve() stage produced) and per
active metric_definition (product-facing, what calculate.py/expanded_metrics.py/
ttm.py/quality_score.py/quality_flags.py etc. actually computed) -- plus two
single aggregate scores meant to be watched trending upward over time, the
same "one documented score, hard denominator" discipline doc/status/
SCORECARD.md already established for a different (execution-quality) score.

avg_metric_coverage_score: simple mean of coverage_pct across every ACTIVE
metric_definition row (both the 18 doc-02-locked V1 metrics and every
expanded metric built since) -- this is the product-facing number, what a
user's screener/company-page results actually cover. Not weighted by
metric importance; a metric with real, low structural coverage (e.g.
piotroski_f_score, which correctly excludes financials) pulls the average
down exactly as much as any other -- deliberately simple (KISS BORING, doc
05) rather than a weighted formula reverse-engineered to look better.

avg_concept_coverage_score: same mean, over the 44 canonical_concept rows
-- a diagnostic/leading indicator (concept coverage moves before metric
coverage does, since a metric needs ALL of its input concepts covered for
the same period) but not the number to optimize directly, since concepts
aren't all equally load-bearing (some feed many metrics, some feed one).

avg_core_v1_metric_coverage_score (added 2026-09-03, doc 42 Part 3):
same mean, restricted to the 20 metric_definition rows doc 02 actually
locked for V1 (CORE_V1_METRIC_NAMES below, sourced directly from
mapper/definitions.py's own METRIC_DEFINITIONS -- not a new, invented
"core metrics" list). Answers a real, flagged-but-undecided product
question: avg_metric_coverage_score's full 64-metric average is
correct and complete, but gets diluted by inherently-rare metrics
(Piotroski's 9-simultaneous-input bar, dividend-only metrics) that most
users never look at -- this second score shows progress on the metrics
doc 02 already decided matter most, without replacing or changing the
first one. Purely additive: computing and storing this changes nothing
about how avg_metric_coverage_score is computed or used.

Never fabricates a coverage number -- every row is a real
`count(distinct company_id) / total_active_companies` query against
canonical_fact/metric_value, same as build_tag_coverage_library.py and
every other coverage query this project has run live."""

from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

import psycopg
import structlog

from scrooner_pipeline.mapper.definitions import (
    METRIC_DEFINITIONS as _V1_METRIC_DEFINITIONS,
)

logger = structlog.get_logger()

# The 20 metric_definition rows doc 02 actually locked for V1 (18
# product-facing metrics; revenue/EPS growth each split into YoY and
# 3Y-CAGR rows -- see mapper/definitions.py's own module docstring).
# Sourced directly from that module, never duplicated by hand, so this
# list can never silently drift from what's actually locked.
CORE_V1_METRIC_NAMES = frozenset(name for name, *_rest in _V1_METRIC_DEFINITIONS)


def _pct(covered: int, total: int) -> Decimal:
    if total == 0:
        return Decimal("0.00")
    return (Decimal(covered) / Decimal(total) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def _load_total_active_companies(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("select count(*) from core.company where status = 'active'")
        return cur.fetchone()[0]


def _load_concept_coverage(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, count(distinct cf.company_id)
            from analytics.canonical_concept cc
            left join analytics.canonical_fact cf on cf.canonical_concept_id = cc.id
            group by cc.name
            """
        )
        return dict(cur.fetchall())


def _load_metric_coverage(conn: psycopg.Connection) -> dict[str, int]:
    """`analytics.metric_value` stores an explicit row with `is_null_reason`
    set even when a metric couldn't be computed for a company (the same
    traceability discipline as `excluded_missing_data` elsewhere in this
    project) -- `value is not null` is required here, or every metric
    would silently show 100% coverage regardless of how many of its rows
    are real. Found live 2026-09-02 building this module's first real
    snapshot: market_cap showed 5,216/5,216 companies before this filter,
    3,131/5,216 after -- the true number."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select md.metric_name, count(distinct mv.company_id) filter (where mv.value is not null)
            from analytics.metric_definition md
            left join analytics.metric_value mv on mv.metric_definition_id = md.id
            where md.status = 'active'
            group by md.metric_name
            """
        )
        return dict(cur.fetchall())


def compute_snapshot(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    """Pure-ish computation (no writes) -- returns the rows a snapshot would
    contain, for testing and for the write path below to share."""
    as_of = as_of or date.today()
    total_active = _load_total_active_companies(conn)
    concept_coverage = _load_concept_coverage(conn)
    metric_coverage = _load_metric_coverage(conn)

    rows = []
    for name, covered in sorted(concept_coverage.items()):
        rows.append(
            {
                "snapshot_date": as_of,
                "item_type": "concept",
                "item_name": name,
                "companies_covered": covered,
                "total_active_companies": total_active,
                "coverage_pct": _pct(covered, total_active),
            }
        )
    for name, covered in sorted(metric_coverage.items()):
        rows.append(
            {
                "snapshot_date": as_of,
                "item_type": "metric",
                "item_name": name,
                "companies_covered": covered,
                "total_active_companies": total_active,
                "coverage_pct": _pct(covered, total_active),
            }
        )

    concept_pcts = [r["coverage_pct"] for r in rows if r["item_type"] == "concept"]
    metric_pcts = [r["coverage_pct"] for r in rows if r["item_type"] == "metric"]
    core_v1_pcts = [
        r["coverage_pct"]
        for r in rows
        if r["item_type"] == "metric" and r["item_name"] in CORE_V1_METRIC_NAMES
    ]
    avg_concept = (
        (sum(concept_pcts) / len(concept_pcts)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if concept_pcts
        else Decimal("0.00")
    )
    avg_metric = (
        (sum(metric_pcts) / len(metric_pcts)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if metric_pcts
        else Decimal("0.00")
    )
    avg_core_v1 = (
        (sum(core_v1_pcts) / len(core_v1_pcts)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if core_v1_pcts
        else Decimal("0.00")
    )

    rows.append(
        {
            "snapshot_date": as_of,
            "item_type": "score",
            "item_name": "avg_concept_coverage_score",
            "companies_covered": len(concept_pcts),
            "total_active_companies": len(concept_pcts),
            "coverage_pct": avg_concept,
        }
    )
    rows.append(
        {
            "snapshot_date": as_of,
            "item_type": "score",
            "item_name": "avg_metric_coverage_score",
            "companies_covered": len(metric_pcts),
            "total_active_companies": len(metric_pcts),
            "coverage_pct": avg_metric,
        }
    )
    rows.append(
        {
            "snapshot_date": as_of,
            "item_type": "score",
            "item_name": "avg_core_v1_metric_coverage_score",
            "companies_covered": len(core_v1_pcts),
            "total_active_companies": len(core_v1_pcts),
            "coverage_pct": avg_core_v1,
        }
    )
    return {
        "rows": rows,
        "avg_concept_coverage_score": avg_concept,
        "avg_metric_coverage_score": avg_metric,
        "avg_core_v1_metric_coverage_score": avg_core_v1,
        "total_active_companies": total_active,
    }


def write_snapshot(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    # UTC, not local date.today() -- found live 2026-09-04: the Postgres
    # server runs UTC while a local dev machine can run a different zone
    # (this project's own machine is IST, UTC+5:30), so a snapshot
    # written locally just after UTC midnight lands under tomorrow's
    # date by local-clock reckoning while the DB's own current_date
    # still reads today -- any same-day verification query using SQL's
    # current_date then silently reads yesterday's real row and looks
    # like data corruption. That's the actual root cause of the
    # previously-unexplained "coverage_snapshot insert anomaly"
    # (doc/learnings/2026-09-03-coverage-snapshot-insert-anomaly.md) --
    # not a write bug at all. UTC keeps every environment (a GitHub
    # Actions runner, which is also UTC, and any local machine)
    # agreeing on the same snapshot_date for "today."
    as_of = as_of or datetime.now(timezone.utc).date()
    result = compute_snapshot(conn, as_of)
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.coverage_snapshot where snapshot_date = %s", (as_of,)
        )
        cur.executemany(
            """
            insert into analytics.coverage_snapshot
                (snapshot_date, item_type, item_name, companies_covered, total_active_companies, coverage_pct)
            values (%(snapshot_date)s, %(item_type)s, %(item_name)s, %(companies_covered)s, %(total_active_companies)s, %(coverage_pct)s)
            """,
            result["rows"],
        )
    conn.commit()
    stats = {
        "snapshot_date": as_of.isoformat(),
        "rows_written": len(result["rows"]),
        "avg_concept_coverage_score": str(result["avg_concept_coverage_score"]),
        "avg_metric_coverage_score": str(result["avg_metric_coverage_score"]),
        "avg_core_v1_metric_coverage_score": str(
            result["avg_core_v1_metric_coverage_score"]
        ),
        "total_active_companies": result["total_active_companies"],
    }
    logger.info("coverage_snapshot.written", **stats)
    return stats
